# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.infer: type inference

Shed Skin infers a static type for every expression by propagating types
through a constraint graph: a node per expression and variable (`CNode`), and
an edge wherever types flow from one to the other (`add_constraint`). The
graph is built from the AST by `shedskin.graph`; this module solves it.

Seeds start the process, e.g. the int in `x = 0`, and `propagate()` moves
types along the edges until nothing changes. Precision comes from copying
parts of the graph, so that different uses of the same code do not mix their
types. Each node is therefore identified by (thing, dcpa, cpa), and there are
two kinds of copies:

- function polymorphism: `cpa()` (Agesen's cartesian product algorithm)
  copies a function into one *template* per combination of argument types it
  is called with, so that e.g. an identity function returns an int where it
  is called with an int (`cpa` numbers the template).
- container polymorphism: builtin container classes are copied into
  *contours* (`dcpa` numbers them), so that a list of ints and a list of strs
  are different types. Which contours exist, and which allocations share one,
  is decided by `shedskin.contours`, which drives the propagation here in
  rounds.

The sections below, in order:

- the driver, `analyze()`, and the solver, `propagate()`
- the constraint graph: nodes, edges, the worklist
- call analysis: what a call expression can call, and how its actual
  arguments map onto formal parameters; also used by code generation
- CPA: the cartesian product of a call, and creating templates
- copying parts of the graph for a template or contour, and seeding the
  allocation sites in a new template
- backing up and restoring the graph, between sweeps of `shedskin.contours`
- after analysis: merging the copies again, for code generation

For more details, see Ole Agesen's PhD thesis on CPA, Mark Dufour's MSc
thesis on Shed Skin, and the docstring of `shedskin.contours`.
"""

import ast
import itertools
import logging
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    TypeAlias,
    Union,
)
from collections.abc import Iterable, Set as AbstractSet

from . import ast_utils, error, python

if TYPE_CHECKING:
    from . import config, graph

Types: TypeAlias = set[
    tuple["python.Class", int]
]  # TODO merge with other modules, reuse common types
CartesianProduct: TypeAlias = tuple[
    tuple["python.Class", int], ...
]  # TODO wrong name!!
AllParent: TypeAlias = Union["python.Class", "python.Function", "python.StaticClass"]
Merged: TypeAlias = dict[Any, set[tuple[Any, int]]]
Analysis: TypeAlias = tuple[
    Optional[ast.AST],
    Optional[str],
    Optional["python.Function"],
    bool,
    Optional["python.Class"],
    bool,
    bool,
]
Backup: TypeAlias = tuple[
    # gx.types (empty sets are stored as the shared EMPTY_SET marker)
    dict["CNode", AbstractSet[tuple[Any, int]]],
    set[tuple["CNode", "CNode"]],  # gx.constraints
    # cnode -> (cnode.in_, cnode.out), same marker for empty sets
    dict["CNode", tuple[AbstractSet["CNode"], AbstractSet["CNode"]]],
    dict[tuple[Any, int, int], "CNode"],  # gx.cnode
]
PossibleFuncs: TypeAlias = list[
    tuple["python.Function", int, Optional[tuple["python.Class", int]]]
]

logger = logging.getLogger("infer")


class MaxIterationsException(Exception):
    pass


# SPLIT_CLASS_IDENTS: builtin classes that carry contours, i.e. the classes
# that are duplicated per allocation site so that (say) a list of ints and a
# list of strings can be told apart. These are the only classes that split.
SPLIT_CLASS_IDENTS = (
    "list",
    "tuple",
    "tuple2",
    "tuple3",
    "dict",
    "frozendict",
    "defaultdict",
    "Counter",
    "set",
    "frozenset",
    "deque",
    "__iter",
    "array",
)


# SCALAR_CLASS_IDENTS: builtin classes that are never duplicated per allocation
# site. Allocation sites of these classes always live at dcpa 0 and so can
# never gain contours.
SCALAR_CLASS_IDENTS = frozenset(
    ["int_", "float_", "str_", "bytes_", "none", "class_", "bool_"]
)


# ---------------------------------------------------------------------------
# the driver and the solver
# ---------------------------------------------------------------------------


def analyze(gx: "config.GlobalInfo", module_name: str) -> None:
    """Analyze a module"""
    from . import graph  # TODO improve separation to avoid circular imports..
    from .typestr import nodetypestr
    from .virtual import analyze_virtuals

    # --- build dataflow graph from source code
    gx.main_module = graph.parse_module(module_name, gx)

    # --- seed class_.__name__ attributes..
    for cl in gx.allclasses:
        if cl.ident == "class_":
            var = default_var(gx, "__name__", cl)
            gx.types[inode(gx, var)] = {(python.def_class(gx, "str_"), 0)}

    # --- copy classes for each allocation site
    for cl in gx.allclasses:
        if cl.ident in SCALAR_CLASS_IDENTS:
            continue
        if cl.ident == "list":
            cl.dcpa = len(gx.list_types) + 2
        elif cl.ident != "__iter":  # XXX huh
            cl.dcpa = 2

        for dcpa in range(1, cl.dcpa):
            class_copy(gx, cl, dcpa)

    # --- seed str/bytes unit
    cl = python.def_class(gx, "str_")
    var = default_var(gx, "unit", cl)
    gx.types[inode(gx, var)] = {(cl, 0)}

    cl = python.def_class(gx, "bytes_")
    var = default_var(gx, "unit", cl)
    gx.types[inode(gx, var)] = {(python.def_class(gx, "int_"), 0)}

    # --- cartesian product algorithm & frozen-core sweep
    from . import contours

    contours.analyze(gx)

    logger.info("[generating c++ code..]")

    for cl in gx.allclasses:
        for name in cl.vars:
            if name in cl.parent.vars and not name.startswith("__"):
                error.error(
                    "instance variable '%s' of class '%s' shadows class variable"
                    % (name, cl.ident),
                    gx,
                    warning=True,
                )

    gx.merged_inh = merged(gx, gx.types, inheritance=True)
    analyze_virtuals(gx)
    determine_classes(gx)

    # --- add inheritance relationships for non-original Nodes (and temp_vars?); XXX register more, right solution?
    for func in gx.allfuncs:
        if func in gx.inheritance_relations:
            for inhfunc in gx.inheritance_relations[func]:
                assert isinstance(inhfunc, python.Function)
                for c, d in zip(func.registered, inhfunc.registered):
                    graph.inherit_rec(gx, c, d, func.mv)

                for a, b in zip(
                    func.registered_temp_vars, inhfunc.registered_temp_vars
                ):  # XXX more general
                    gx.inheritance_temp_vars.setdefault(a, []).append(b)

    gx.merged_inh = merged(gx, gx.types, inheritance=True)

    # error for dynamic expression without explicit type declaration
    for node in gx.merged_inh:
        if (
            isinstance(node, ast.AST)
            and not ast_utils.is_assign_attribute(node)
            and not inode(gx, node).mv.module.builtin
        ):
            nodetypestr(gx, node, inode(gx, node).parent, mv=inode(gx, node).mv)


def propagate(gx: "config.GlobalInfo") -> None:
    """Propagate constraints through the graph"""
    logger.debug("propagate")

    # --- initialize working sets
    worklist: list[CNode] = []
    changed = set()
    for node in gx.types:
        if gx.types[node]:
            add_to_worklist(worklist, node)
        expr = node.thing
        if (
            isinstance(expr, ast.Call) and not expr.args
        ) or expr in gx.lambdawrapper:  # XXX
            changed.add(node)

    for node in changed:
        cpa(gx, node, worklist)

    builtins = set(gx.builtins)
    types = gx.types

    # --- the freeze (see shedskin.contours): container contours outside
    # --- gx.open_contours still pass on what they hold, but receive nothing
    open_contours = gx.open_contours
    split_idents = SPLIT_CLASS_IDENTS

    # --- iterative dataflow analysis
    while worklist:
        callnodes = set()
        while worklist:
            a = worklist.pop(0)
            a.in_list = 0

            for callfunc in a.callfuncs:
                t = (callfunc, a.dcpa, a.cpa)
                if t in gx.cnode:
                    callnodes.add(gx.cnode[t])

            for b in a.out.copy():  # XXX can change...?
                # for builtin types, the set of instance variables is known, so do not flow into non-existent ones # XXX ifa
                if isinstance(b.thing, python.Variable) and isinstance(
                    b.thing.parent, python.Class
                ):
                    parent_ident = b.thing.parent.ident

                    if (
                        open_contours is not None
                        and parent_ident in split_idents
                        and b.thing.parent.mv.module.builtin
                        and (b.thing.parent, b.dcpa) not in open_contours
                    ):
                        continue

                    if parent_ident in builtins:
                        if parent_ident in [
                            "int_",
                            "float_",
                            "str_",
                            "none",
                            "bool_",
                            "bytes_",
                        ]:
                            continue
                        elif (
                            parent_ident
                            in [
                                "list",
                                "tuple",
                                "frozenset",
                                "set",
                                "file",
                                "__iter",
                                "deque",
                                "array",
                            ]
                            and b.thing.name != "unit"
                        ):
                            continue
                        elif parent_ident in (
                            "dict",
                            "frozendict",
                            "defaultdict",
                            "Counter",
                        ) and b.thing.name not in ["unit", "value"]:
                            continue
                        elif parent_ident == "tuple2" and b.thing.name not in [
                            "unit",
                            "first",
                            "second",
                        ]:
                            continue
                        elif parent_ident == "tuple3" and b.thing.name not in [
                            "unit",
                            "first",
                            "second",
                            "third",
                        ]:
                            continue

                typesa = types[a]
                typesb = types[b]
                oldsize = len(typesb)

                typesb.update(typesa)
                if len(typesb) > oldsize:
                    add_to_worklist(worklist, b)

        for callnode in callnodes:
            cpa(gx, callnode, worklist)


# ---------------------------------------------------------------------------
# the constraint graph
# ---------------------------------------------------------------------------


class CNode:
    """A node in the constraint graph"""

    __slots__ = [
        "gx",
        "thing",
        "dcpa",
        "cpa",
        "fakefunc",
        "parent",
        "defnodes",
        "mv",
        "constructor",
        "copymetoo",
        "lambdawrapper",
        "in_",
        "out",
        "in_list",
        "callfuncs",
        "nodecp",
        "assignhop",
        "temp1",
        "temp2",
        "subs",
    ]

    def __init__(
        self,
        gx: "config.GlobalInfo",
        mv: "graph.ModuleVisitor",
        thing: Any,
        dcpa: int = 0,
        cpa: int = 0,
        parent: Optional[AllParent] = None,
    ):
        self.gx = gx
        self.thing = thing
        self.dcpa = dcpa
        self.cpa = cpa
        self.fakefunc: Optional[ast.Call] = None
        if isinstance(
            parent, python.Class
        ):  # TODO leave class in? add type, see 'parent' usage below
            parent = None
        self.parent = parent
        self.defnodes = (
            False  # if callnode, notification nodes were made for default arguments
        )
        self.mv = mv
        self.constructor = False  # allocation site
        self.copymetoo = False
        self.lambdawrapper: Optional["python.Function"] = None

        self.gx.cnode[self.thing, self.dcpa, self.cpa] = self

        # --- in, outgoing constraints

        self.in_: set[CNode] = set()  # incoming nodes
        self.out: set[CNode] = set()  # outgoing nodes

        # --- iterative dataflow analysis

        self.in_list = 0  # node in work-list
        self.callfuncs: list[Any] = []  # callfuncs to which node is object/argument

        self.nodecp: set[
            tuple["python.Function", CartesianProduct, CartesianProduct]
        ] = set()  # already analyzed cp's # XXX kill!?

        self.temp1: str
        self.temp2: str
        self.subs: ast.AST
        self.assignhop: ast.Assign

        # --- add node to surrounding non-listcomp function
        parent = python.outer_func(parent)
        if parent and self not in parent.nodes:
            parent.nodes.add(self)
            parent.nodes_ordered.append(self)

    def copy(
        self, dcpa: int, cpa: int, worklist: Optional[list["CNode"]] = None
    ) -> "CNode":  # XXX to infer.py
        """Copy a node"""
        # if not self.mv.module.builtin: print 'copy', self

        if (self.thing, dcpa, cpa) in self.gx.cnode:
            return self.gx.cnode[self.thing, dcpa, cpa]

        newnode = CNode(self.gx, self.mv, self.thing, dcpa, cpa)

        newnode.callfuncs = self.callfuncs[:]  # XXX no copy?
        newnode.constructor = self.constructor
        newnode.copymetoo = self.copymetoo
        newnode.parent = self.parent

        add_to_worklist(worklist, newnode)

        if (
            self.constructor
            or self.copymetoo
            or isinstance(self.thing, (ast.Not, ast.Compare))
        ):  # XXX XXX
            self.gx.types[newnode] = self.gx.types[self].copy()
        else:
            self.gx.types[newnode] = set()
        return newnode

    def types(self) -> Types:
        """Get the types of a node"""
        if self in self.gx.types:
            return self.gx.types[self]
        else:
            return set()  # XXX

    def __repr__(self) -> str:
        return repr((self.thing, self.dcpa, self.cpa))


def inode(gx: "config.GlobalInfo", node: Any) -> CNode:
    """Get the constraint node for a given object"""
    return gx.cnode[node, 0, 0]


def add_constraint(
    gx: "config.GlobalInfo", a: CNode, b: CNode, worklist: Optional[list[CNode]] = None
) -> None:
    """Add a constraint to the graph"""
    gx.constraints.add((a, b))
    in_out(a, b)
    add_to_worklist(worklist, a)


def in_out(a: CNode, b: CNode) -> None:
    """Add an outgoing edge to a node"""
    a.out.add(b)
    b.in_.add(a)


def add_to_worklist(
    worklist: Optional[list[CNode]], node: CNode
) -> None:  # XXX to infer.py
    """Add a node to the worklist"""
    if worklist is not None and not node.in_list:
        worklist.append(node)
        node.in_list = 1


def default_var(
    gx: "config.GlobalInfo",
    name: str,
    parent: Optional[AllParent],
    worklist: Optional[list[CNode]] = None,
    mv: Optional["graph.ModuleVisitor"] = None,
    exc_name: bool = False,
) -> "python.Variable":
    """Create a default variable"""
    if parent:
        mv = parent.mv
    assert mv
    var = python.lookup_var(name, parent, mv, local=True)
    if not var:
        var = python.Variable(name, parent)
        if parent:  # XXX move to python.Variable?
            parent.vars[name] = var
        elif exc_name:
            mv.exc_names[name] = var
        else:
            mv.globals[name] = var
        gx.allvars.add(var)

    if (var, 0, 0) not in gx.cnode:
        newnode = CNode(gx, mv, var, parent=parent)
        if parent:
            newnode.mv = parent.mv
        else:
            newnode.mv = mv
        add_to_worklist(worklist, newnode)
        gx.types[newnode] = set()

    if isinstance(parent, python.Function) and parent.listcomp and not var.registered:
        register_temp_var(var, python.outer_func(parent))

    return var


def register_temp_var(var: "python.Variable", parent: Optional[AllParent]) -> None:
    """Register a temporary variable"""
    if isinstance(parent, python.Function):
        parent.registered_temp_vars.append(var)


# ---------------------------------------------------------------------------
# call analysis
# ---------------------------------------------------------------------------


def analyze_callfunc(
    gx: "config.GlobalInfo",
    node: ast.Call,
    node2: Optional[CNode] = None,
    merge: Optional[Merged] = None,
) -> Analysis:
    """Analyze a call expression"""

    # XXX generate target list XXX uniform python.Variable system! XXX node2, merge?
    # print 'analyze callnode', ast.dump(node), inode(gx, node).parent
    cnode = inode(gx, node)
    mv = cnode.mv
    assert mv  # TODO make cnode.mv non-optional instead?
    namespace, objexpr, method_call, parent_constr = mv.module, None, False, False
    constructor, direct_call, ident = None, None, None

    # anon func call XXX refactor as __call__ method call below
    anon_func, is_callable = is_anon_callable(gx, node, node2, merge)
    if is_callable:
        method_call, objexpr, ident = True, node.func, "__call__"
        return (
            objexpr,
            ident,
            direct_call,
            method_call,
            constructor,
            parent_constr,
            anon_func,
        )

    # method call
    if isinstance(node.func, ast.Attribute):
        objexpr, ident = node.func.value, node.func.attr
        cl, module = python.lookup_class_module(objexpr, mv, cnode.parent)

        if cl:
            # staticmethod call
            if ident in cl.staticmethods or ident in cl.classmethods:
                direct_call = cl.funcs[ident]
                return (
                    objexpr,
                    ident,
                    direct_call,
                    method_call,
                    constructor,
                    parent_constr,
                    anon_func,
                )

            # ancestor call
            elif ident not in ["__setattr__", "__getattr__"] and cnode.parent:
                thiscl = cnode.parent.parent
                if isinstance(thiscl, python.Class) and cl.ident in (
                    x.ident for x in thiscl.ancestors_upto(None)
                ):  # XXX
                    implementor = python.lookup_implementor(cl, ident)
                    if implementor:
                        parent_constr = True
                        ident = ident + implementor + "__"  # XXX change data structure
                        return (
                            objexpr,
                            ident,
                            direct_call,
                            method_call,
                            constructor,
                            parent_constr,
                            anon_func,
                        )

        if module:  # XXX elif?
            namespace, objexpr = module, None
        else:
            method_call = True

    elif isinstance(node.func, ast.Name):
        ident = node.func.id

    # direct [constructor] call
    if isinstance(node.func, ast.Name) or namespace != mv.module:
        assert isinstance(ident, str)

        if isinstance(node.func, ast.Name):
            if python.lookup_var(ident, cnode.parent, mv):
                return (
                    objexpr,
                    ident,
                    direct_call,
                    method_call,
                    constructor,
                    parent_constr,
                    anon_func,
                )
        if ident in namespace.mv.classes:
            constructor = namespace.mv.classes[ident]
        elif ident in namespace.mv.funcs:
            direct_call = namespace.mv.funcs[ident]
        elif ident in namespace.mv.ext_classes:
            constructor = namespace.mv.ext_classes[ident]
        elif ident in namespace.mv.ext_funcs:
            direct_call = namespace.mv.ext_funcs[ident]
        else:
            if namespace != mv.module:
                return objexpr, ident, None, False, None, False, False
        if direct_call and direct_call.ident in ('min', 'max'):  # TODO remove ident check
            direct_call = redirect_func(direct_call, node)

    return (
        objexpr,
        ident,
        direct_call,
        method_call,
        constructor,
        parent_constr,
        anon_func,
    )


def is_anon_callable(
    gx: "config.GlobalInfo",
    expr: ast.Call,
    node: Optional[CNode],
    merge: Optional[Merged] = None,
) -> tuple[bool, bool]:
    """Check if an anonymous function is callable"""
    types = get_types(gx, expr, node, merge)
    anon = bool([t for t in types if isinstance(t[0], python.Function)])
    call = bool(
        [
            t
            for t in types
            if isinstance(t[0], python.Class) and "__call__" in t[0].funcs
        ]
    )
    return anon, call


def get_types(
    gx: "config.GlobalInfo",
    expr: ast.Call,
    node: Optional[CNode],
    merge: Optional[Merged],
) -> Types:
    """Get the types of a call node"""
    types = set()
    if merge:
        if expr.func in merge:
            types = merge[expr.func]
    elif node:
        node2 = (expr.func, node.dcpa, node.cpa)
        if node2 in gx.cnode:
            types = gx.cnode[node2].types()
    return types


def redirect_func(
    func: "python.Function",
    callfunc: ast.Call,
) -> "python.Function":
    """ redirect based on number of arguments (__%s%d syntax in builtins) """

    if func.mv.module.builtin:
        if isinstance(func.parent, python.Class):
            funcs = func.parent.funcs
        else:
            funcs = func.mv.funcs
        nargs = len(
            [kwarg for kwarg in callfunc.args if not isinstance(kwarg, ast.keyword)]
        )
        if func.ident == 'groupby':  # TODO avoid special case..
            nargs += len([a for a in callfunc.keywords if a.arg == 'key'])
        redir = "__%s%d" % (func.ident, nargs)
        func = funcs.get(redir, func)
    return func


def callfunc_targets(
    gx: "config.GlobalInfo", node: ast.Call, merge: Merged
) -> list["python.Function"]:
    """Get the potential call targets of a call node"""

    (
        objexpr,
        ident,
        direct_call,
        method_call,
        constructor,
        parent_constr,
        anon_func,
    ) = analyze_callfunc(gx, node, merge=merge)
    funcs = []

    if node.func in merge and [
        t for t in merge[node.func] if isinstance(t[0], python.Function)
    ]:  # anonymous function call
        funcs = [t[0] for t in merge[node.func] if isinstance(t[0], python.Function)]

    elif constructor:
        if (
            constructor.mv.module.builtin
            and ident in ("list", "tuple", "set", "frozenset")
            and nrargs(gx, node) == 1
        ):
            funcs = [constructor.funcs["__inititer__"]]
        elif (
            constructor.mv.module.builtin
            and (ident, nrargs(gx, node)) in (
                ("dict", 1),
                ("frozendict", 1),
                ("defaultdict", 2),
                ("Counter", 1),
            )
        ):  # XXX merge infer.redirect
            funcs = [constructor.funcs["__initdict__"]]  # XXX __inititer__?
        elif sys.platform == "win32" and "__win32__init__" in constructor.funcs:
            funcs = [constructor.funcs["__win32__init__"]]
        elif "__init__" in constructor.funcs:
            funcs = [constructor.funcs["__init__"]]

    elif parent_constr:
        if ident != "__init__":
            func = inode(gx, node).parent
            assert isinstance(func, python.Function)
            cl = func.parent
            assert isinstance(cl, python.Class)
            assert isinstance(ident, str)
            funcs = [cl.funcs[ident]]

    elif direct_call:
        funcs = [direct_call]

    elif method_call:
        classes = {t[0] for t in merge[objexpr] if isinstance(t[0], python.Class)}
        funcs = [cl.funcs[ident] for cl in classes if ident in cl.funcs]

    return funcs


def nrargs(gx: "config.GlobalInfo", node: ast.Call) -> Optional[int]:
    """Get the number of arguments of a call node"""
    cnode = inode(gx, node)
    if cnode.lambdawrapper:
        return cnode.lambdawrapper.largs
    return len(node.args)


def analyze_args(
    gx: "config.GlobalInfo",
    expr: ast.Call,
    func: "python.Function",
    node: Optional[CNode] = None,
    skip_defaults: bool = False,
    merge: Optional[Merged] = None,
) -> tuple[
    list[Optional[ast.AST]], list[str], list[ast.AST], list[Optional[ast.AST]], bool
]:
    """Analyze the arguments of a call node"""
    (
        objexpr,
        ident,
        direct_call,
        method_call,
        constructor,
        parent_constr,
        anon_func,
    ) = analyze_callfunc(gx, expr, node, merge)

    args: list[Optional[ast.AST]] = []
    kwdict = {}
    for a in expr.args:
        args.append(a)
    for b in expr.keywords:
        kwdict[b.arg] = b.value
    formal_args = func.formals[:]
    assert func.node
    if func.node.args.vararg:
        formal_args = formal_args[:-1]
    default_start = len(formal_args) - len(func.defaults)

    if ident in ["__getattr__", "__setattr__"]:  # property?
        args = args[1:]

    if (method_call or constructor) and not (parent_constr or anon_func):  # XXX
        args.insert(0, None)

    kwextra = []
    for kw in kwdict:
        if kw not in formal_args and f"__kw_{kw}" not in formal_args:
            kwextra.append(kw)

    argnr = 0
    actuals: list[Optional[ast.AST]] = []
    formals = []
    defaults: list[ast.AST] = []
    missing = False
    for i, formal in enumerate(formal_args):
        if formal in kwdict:
            actuals.append(kwdict[formal])
            formals.append(formal)
        elif formal.startswith("__kw_") and formal[5:] in kwdict:
            actuals.insert(0, kwdict[formal[5:]])
            formals.insert(0, formal)
        elif argnr < len(args) and not formal.startswith("__kw_"):
            actuals.append(args[argnr])
            argnr += 1
            formals.append(formal)
        elif i >= default_start:
            default = func.defaults[i - default_start]
            if not skip_defaults:
                if formal.startswith("__kw_"):
                    actuals.insert(0, default)
                    formals.insert(0, formal)
                else:
                    actuals.append(default)
                    formals.append(formal)
                defaults.append(default)
            elif func.mv.module.ident == "bisect":  # TODO generalize
                if formal.startswith("__kw_"):
                    actuals.insert(0, default)
                    formals.insert(0, formal)
        else:
            missing = True

    extra = args[argnr:]

    _error = bool(
        (missing or extra or kwextra)
        and not func.node.args.vararg
        and not func.node.args.kwarg
        and not get_starargs(expr)
        and func.lambdanr is None
        and expr not in gx.lambdawrapper
    )  # XXX

    if func.node.args.vararg:
        for arg in extra:
            actuals.append(arg)
            formals.append(func.formals[-1])

    return actuals, formals, defaults, extra, _error


def get_starargs(node: ast.Call) -> Optional[ast.AST]:
    """Get the starred argument of a call node"""
    for arg in node.args:
        if isinstance(arg, ast.Starred):
            return arg.value
    return None


def connect_actual_formal(
    gx: "config.GlobalInfo",
    expr: ast.Call,
    func: "python.Function",
    parent_constr: bool = False,
    merge: Optional[Merged] = None,
) -> tuple[list[tuple[ast.AST, "python.Variable"]], int, bool]:
    """Connect actual and formal arguments"""

    pairs = []

    actuals: list[Optional[ast.AST]] = [
        a for a in expr.args if not isinstance(a, ast.keyword)
    ]
    if isinstance(func.parent, python.Class):
        formals = [f for f in func.formals if f != "self"]
    else:
        formals = [f for f in func.formals]

    if parent_constr:
        actuals = actuals[1:]

    # TODO replace all this with __ss_void approach?
    skip_defaults = (
        False  # XXX investigate and further narrow down cases where we want to skip
    )
    if (
        (
            func.mv.module.ident
            in [
                "time",
                "string",
                "collections",
                "bisect",
                "array",
                "math",
                "integer",
                "cStringIO",
                "getopt",
            ]
        )
        or (func.mv.module.ident == "random" and func.ident == "randrange")
        or (
            func.mv.module.ident == "builtin"
            and func.ident
            not in (
                "sort",
                "sorted",
                "min",
                "__min1",
                "max",
                "__max1",
                "__print",
                "zip",
                "split",
                "rsplit",
                "map",
                "to_bytes",
                "from_bytes",
                # emit all (None) defaults, so that e.g. decode(errors=..)
                # does not pass 'errors' as the encoding
                "encode",
                "decode",
                "open",  # open(f, encoding=..) must not pass it as the mode
                "open_binary",
            )
        )
    ):
        if (
            not (
                func.mv.module.ident == "math"
                and func.ident == "isclose"
            )
            and not (
                func.mv.module.ident == "collections"
                and func.ident == "__init__"
                and isinstance(func.parent, python.Class)
                and func.parent.ident == 'deque'
            )
        ):
            skip_defaults = True

    actuals, formals, _, extra, _error = analyze_args(
        gx, expr, func, skip_defaults=skip_defaults, merge=merge
    )

    for actual, formal in zip(actuals, formals):
        if not (isinstance(func.parent, python.Class) and formal == "self"):
            assert actual
            pairs.append((actual, func.vars[formal]))

    return pairs, len(extra), _error


def actuals_formals(
    gx: "config.GlobalInfo",
    expr: ast.Call,
    func: "python.Function",
    node: CNode,
    dcpa: int,
    cpa: int,
    types: CartesianProduct,
    analysis: Analysis,
    worklist: list[CNode],
) -> None:
    """Connect actual and formal arguments"""
    (
        objexpr,
        ident,
        direct_call,
        method_call,
        constructor,
        parent_constr,
        anon_func,
    ) = analysis

    starargs = get_starargs(expr)
    if starargs:  # XXX only in lib/
        formals = func.formals
        actuals: list[Optional[ast.AST]] = []
        for _ in range(len(formals)):
            actuals.append(starargs)
        types = len(formals) * types
    else:
        actuals, formals, _, _, _error = analyze_args(gx, expr, func, node)
        if _error:
            return

    for actual, formal, formaltype in zip(actuals, formals, types):
        formalnode = gx.cnode[func.formal_nodes[formal], dcpa, cpa]

        if (
            formaltype[1] != 0
        ):  # ifa: remember dataflow information for non-simple types
            if actual is None:
                if constructor:
                    objexpr = node.thing

                if method_call or constructor:
                    formalnode.in_.add(gx.cnode[objexpr, node.dcpa, node.cpa])
            else:
                if actual in func.defaults:
                    formalnode.in_.add(gx.cnode[actual, 0, 0])
                else:
                    formalnode.in_.add(gx.cnode[actual, node.dcpa, node.cpa])

        gx.types[formalnode].add(formaltype)
        add_to_worklist(worklist, formalnode)


def connect_getsetattr(
    gx: "config.GlobalInfo",
    func: "python.Function",
    callnode: CNode,
    callfunc: ast.Call,
    dcpa: int,
    worklist: list[CNode],
) -> bool:
    """Connect a get/setattr call to the target attribute"""

    if (
        isinstance(callfunc.func, ast.Attribute)
        and callfunc.func.attr in ["__setattr__", "__getattr__"]
        and not (
            isinstance(func.parent, python.Class)
            and callfunc.args
            and ast_utils.is_str(callfunc.args[0])
            and _const_str(callfunc.args[0]) in func.parent.properties
        )
    ):
        assert ast_utils.is_str(callfunc.args[0])
        varname = _const_str(callfunc.args[0])
        parent = func.parent
        assert isinstance(parent, (python.Class, python.StaticClass))

        var = default_var(
            gx, varname, parent, worklist, mv=parent.module.mv
        )  # XXX always make new var??
        inode(gx, var).copy(dcpa, 0, worklist)

        if gx.cnode[var, dcpa, 0] not in gx.types:
            gx.types[gx.cnode[var, dcpa, 0]] = set()

        gx.cnode[var, dcpa, 0].mv = parent.module.mv  # XXX move into default_var

        if callfunc.func.attr == "__setattr__":
            add_constraint(
                gx,
                gx.cnode[callfunc.args[1], callnode.dcpa, callnode.cpa],
                gx.cnode[var, dcpa, 0],
                worklist,
            )
        else:
            add_constraint(gx, gx.cnode[var, dcpa, 0], callnode, worklist)
        return True
    return False


def redirect(
    gx: "config.GlobalInfo",
    c: CartesianProduct,
    dcpa: int,
    func: "python.Function",
    callfunc: ast.Call,
    ident: Optional[str],
    callnode: CNode,
    direct_call: Optional["python.Function"],
    constructor: Optional["python.Class"],
) -> tuple[CartesianProduct, int, "python.Function"]:
    """Redirect a call node"""
    func = redirect_func(func, callfunc)

    # staticmethod
    if isinstance(func.parent, python.Class) and (
        func.ident in func.parent.staticmethods
        or func.ident in func.parent.classmethods
    ):
        dcpa = 1

    # dict.__init__
    if (
        constructor
        and constructor.mv.module.builtin
        and (ident, nrargs(gx, callfunc)) in (
            ("dict", 1),
            ("frozendict", 1),
            ("defaultdict", 2),
            ("Counter", 1),
        )
    ):
        clnames = [x[0].ident for x in c if isinstance(x[0], python.Class)]
        if "dict" in clnames or "defaultdict" in clnames or "frozendict" in clnames or "Counter" in clnames:
            func = list(callnode.types())[0][0].funcs["__initdict__"]
        else:
            func = list(callnode.types())[0][0].funcs["__inititer__"]

    # dict.{update, __ior__}, Counter.{update, subtract}
    if (
        func.ident in ("update", "__ior__", "subtract")
        and isinstance(func.parent, python.Class)
        and func.parent.mv.module.builtin
        and func.parent.ident in ("dict", "frozendict", "defaultdict", "Counter")
    ):
        clnames = [x[0].ident for x in c if isinstance(x[0], python.Class)]
        if not ("dict" in clnames or "defaultdict" in clnames or "frozendict" in clnames or "Counter" in clnames):
            func = func.parent.funcs[func.ident + "iter"]

    # list, tuple
    if (
        constructor
        and ident in ("list", "tuple", "set", "frozenset")
        and nrargs(gx, callfunc) == 1
    ):
        func = list(callnode.types())[0][0].funcs["__inititer__"]  # XXX use __init__?

    # array
    if constructor and ident == "array" and ast_utils.is_str(callfunc.args[0]):
        typecode = _const_str(callfunc.args[0])
        array_type = None
        if typecode in "bBhHiIlLqQ":
            array_type = "int"
        elif typecode in "fd":
            array_type = "float"
        elif typecode in "uw":
            # unicode typecodes: elements are single-character strings
            # ('u' is deprecated in CPython since 3.3 and removed in 3.16,
            # 'w' is its replacement, added in 3.13)
            array_type = "str"
        if array_type is not None:
            func = list(callnode.types())[0][0].funcs["__init_%s__" % array_type]

    # tuple2.__getitem__(0/1) -> __getfirst__/__getsecond__
    # tuple3.__getitem__(0/1/2) -> __getfirst__/__getsecond__/__getthird__
    if (
        isinstance(callfunc.func, ast.Attribute)
        and callfunc.func.attr in ("__getitem__", "__getunit__")
        and ast_utils.is_num(callfunc.args[0])
        and func.parent
        and func.parent.mv.module.builtin
        and (
            (func.parent.ident == "tuple2" and _const_num(callfunc.args[0]) in (0, 1))
            or (
                func.parent.ident == "tuple3"
                and _const_num(callfunc.args[0]) in (0, 1, 2)
            )
        )
    ):
        assert isinstance(func.parent, python.Class)
        getter = ["__getfirst__", "__getsecond__", "__getthird__"][
            _const_num(callfunc.args[0])
        ]
        func = func.parent.funcs[getter]

    # property
    if isinstance(callfunc.func, ast.Attribute) and callfunc.func.attr in [
        "__setattr__",
        "__getattr__",
    ]:
        if (
            isinstance(func.parent, python.Class)
            and callfunc.args
            and ast_utils.is_str(callfunc.args[0])
            and _const_str(callfunc.args[0]) in func.parent.properties
        ):
            arg = _const_str(callfunc.args[0])
            if callfunc.func.attr == "__setattr__":
                assert isinstance(func.parent, python.Class)
                func = func.parent.funcs[func.parent.properties[arg][1]]
            else:
                assert isinstance(func.parent, python.Class)
                func = func.parent.funcs[func.parent.properties[arg][0]]
            c = c[1:]

    # win32
    if (
        sys.platform == "win32"
        and func.mv.module.builtin
        and isinstance(func.parent, python.Class)
        and "__win32" + func.ident in func.parent.funcs
    ):
        func = func.parent.funcs["__win32" + func.ident]

    return c, dcpa, func


def _const_str(node: ast.AST) -> str:
    """Return string value from a constant node."""
    assert isinstance(node, ast.Constant)
    assert isinstance(node.value, str)
    return node.value


def _const_num(node: ast.AST) -> Union[int, float]:
    """Return numeric value from a constant node."""
    assert isinstance(node, ast.Constant)
    assert isinstance(node.value, (int, float))
    return node.value


# ---------------------------------------------------------------------------
# CPA: one template per cartesian product of argument types
# ---------------------------------------------------------------------------


def cpa(gx: "config.GlobalInfo", callnode: CNode, worklist: list[CNode]) -> None:
    """Perform the cartesian product algorithm"""

    analysis = analyze_callfunc(gx, callnode.thing, callnode)

    # loop over cartesian product of possible funcs, arg types
    functypes = possible_functions(gx, callnode, analysis)
    if not functypes:
        return
    argtypes = possible_argtypes(gx, callnode, functypes, analysis, worklist)
    cp = list(itertools.product(*argtypes))
    if not cp:
        return

    if (len(functypes) * len(cp)) > gx.cpa_limit:
        gx.cpa_limited = True
        return

    (
        objexpr,
        ident,
        direct_call,
        method_call,
        constructor,
        parent_constr,
        anon_func,
    ) = analysis

    # --- iterate over function/argument type combinations
    for functype in functypes:
        for c in cp:
            (func, dcpa, objtype) = functype

            objtype2: CartesianProduct  # TODO wrong name for type!
            if objtype:
                objtype2 = (objtype,)
            else:
                objtype2 = ()

            # redirect in special cases
            callfunc = callnode.thing
            c, dcpa, func = redirect(
                gx, c, dcpa, func, callfunc, ident, callnode, direct_call, constructor
            )

            # already connected to template
            if (func, objtype2, c) in callnode.nodecp:
                continue
            callnode.nodecp.add((func, objtype2, c))

            # create new template
            if dcpa not in func.cp or c not in func.cp[dcpa]:
                create_template(gx, func, dcpa, c, worklist)
            cpa = func.cp[dcpa][c]
            func.xargs[dcpa, cpa] = len(c)

            # __getattr__, __setattr__
            if connect_getsetattr(gx, func, callnode, callfunc, dcpa, worklist):
                continue

            # connect actuals and formals
            actuals_formals(
                gx,
                callfunc,
                func,
                callnode,
                dcpa,
                cpa,
                objtype2 + c,
                analysis,
                worklist,
            )

            # connect call and return expressions
            if func.retnode and not constructor:
                retnode = gx.cnode[func.retnode.thing, dcpa, cpa]
                add_constraint(gx, retnode, callnode, worklist)


def possible_functions(
    gx: "config.GlobalInfo", node: CNode, analysis: Analysis
) -> PossibleFuncs:
    """Determine the cartesian product of possible function and argument types"""
    expr = node.thing

    # --- determine possible target functions
    (
        objexpr,
        ident,
        direct_call,
        method_call,
        constructor,
        parent_constr,
        anon_func,
    ) = analysis

    funcs: PossibleFuncs = []

    if anon_func:
        # anonymous call
        types2 = gx.cnode[expr.func, node.dcpa, node.cpa].types()
        types: list[tuple["python.Function", int]] = []
        for t in types2:
            if isinstance(t[0], python.Function):
                types.append(t)

        # XXX XXX analyse per t, sometimes class, sometimes function..

        if list(types)[0][0].parent:  # method reference XXX merge below?
            for f in types:
                cl = f[0].parent
                assert isinstance(cl, python.Class)
                funcs.append(
                    (f[0], f[1], (cl, f[1]))
                )  # node.dcpa: connect to right dcpa duplicate version
        else:  # function reference
            funcs = [
                (f[0], f[1], None) for f in types
            ]  # function call: only one version; no objtype

    elif constructor:
        funcs = [
            (t[0].funcs["__init__"], t[1], t)
            for t in node.types()
            if "__init__" in t[0].funcs
        ]

    elif parent_constr:
        assert node.mv
        objtypes = gx.cnode[
            python.lookup_var("self", node.parent, node.mv), node.dcpa, node.cpa
        ].types()
        funcs = [
            (t[0].funcs[ident], t[1], None) for t in objtypes if ident in t[0].funcs
        ]

    elif direct_call:
        funcs = [(direct_call, 0, None)]

    elif method_call:
        objtypes = gx.cnode[objexpr, node.dcpa, node.cpa].types()
        objtypes = {t for t in objtypes if not isinstance(t[0], python.Function)}  # XXX

        funcs = [
            (t[0].funcs[ident], t[1], t)
            for t in objtypes
            if ident in t[0].funcs
            and not (
                isinstance(t[0], python.Class)
                and (ident in t[0].staticmethods or ident in t[0].classmethods)
            )
        ]

    return funcs


def possible_argtypes(
    gx: "config.GlobalInfo",
    node: CNode,
    funcs: PossibleFuncs,
    analysis: Analysis,
    worklist: list[CNode],
) -> list[Types]:
    """Determine the possible argument types for a call node"""
    expr = node.thing
    (
        objexpr,
        ident,
        direct_call,
        method_call,
        constructor,
        parent_constr,
        anon_func,
    ) = analysis
    if funcs:
        func = funcs[0][0]  # XXX

    args = []
    starargs = get_starargs(expr)
    if starargs:  # XXX
        args = [starargs]
    elif funcs and not func.node:  # XXX getattr, setattr
        args = expr.args
    elif funcs:
        actuals, formals, used_defaults, _, _ = analyze_args(gx, expr, func, node)

        if not node.defnodes:
            for i, default in enumerate(used_defaults):
                defnode = CNode(
                    gx,
                    node.mv,
                    (inode(gx, node.thing), i),
                    node.dcpa,
                    node.cpa,
                    parent=func,
                )
                gx.types[defnode] = set()
                defnode.callfuncs.append(node.thing)
                add_constraint(
                    gx, gx.cnode[default, 0, 0], defnode, worklist
                )  # XXX bad place
        node.defnodes = True

        for act, form in zip(actuals, formals):
            if parent_constr or not (
                isinstance(func.parent, python.Class) and form == "self"
            ):  # XXX merge
                assert act
                args.append(act)

    argtypes = []
    for arg in args:
        if (arg, node.dcpa, node.cpa) in gx.cnode:
            argtypes.append(gx.cnode[arg, node.dcpa, node.cpa].types())
        else:
            argtypes.append(inode(gx, arg).types())  # XXX def arg?

    # store arg count for wrappers to builtin refs
    if funcs and (func.lambdawrapper or node.thing in gx.lambdawrapper):
        while argtypes and not argtypes[-1]:
            argtypes = argtypes[:-1]
        if func.lambdawrapper:
            assert isinstance(node.parent, python.Function)
            if (
                starargs
                and node.parent
                and node.parent.node
                and node.parent.node.args.vararg
            ):
                func.largs = (
                    node.parent.xargs[node.dcpa, node.cpa]
                    - len(node.parent.formals)
                    + 1
                )
            else:
                func.largs = len(argtypes)

    return argtypes


def create_template(
    gx: "config.GlobalInfo",
    func: "python.Function",
    dcpa: int,
    c: CartesianProduct,
    worklist: list[CNode],
) -> None:
    """Create a new template for a function"""
    # --- unseen cartesian product: create new template
    if dcpa not in func.cp:
        func.cp[dcpa] = {}
    func.cp[dcpa][c] = cpa = len(func.cp[dcpa])  # XXX +1

    if not func.mv.module.builtin and func.ident not in ["__getattr__", "__setattr__"]:
        logger.debug("template (%s, %s) %s", func, dcpa, c)

    gx.templates += 1
    func_copy(gx, func, dcpa, cpa, worklist, c)


def called(func: "python.Function") -> bool:
    """Check if a function has been called"""
    return bool([cpas for cpas in func.cp.values() if cpas])


# ---------------------------------------------------------------------------
# copying parts of the graph
# ---------------------------------------------------------------------------


def func_copy(
    gx: "config.GlobalInfo",
    func: "python.Function",
    dcpa: int,
    cpa: int,
    worklist: Optional[list[CNode]] = None,
    cart: Optional[CartesianProduct] = None,
) -> None:
    """Copy a function"""
    # print 'funccopy', func, cart, dcpa, cpa

    # --- copy other nodes
    cnode_redirect = {}
    for node in func.nodes:
        cnode_copy = node.copy(dcpa, cpa, worklist)
        if not isinstance(node.thing, python.Variable):
            cnode_redirect[node] = cnode_copy

    # --- copy local end points of each constraint
    for a, b in func.constraints:
        a = cnode_redirect.get(a, a)
        b = cnode_redirect.get(b, b)
        if (
            not (
                isinstance(a.thing, python.Variable)
                and parent_func(gx, a.thing) != func
            )
            and a.dcpa == 0
        ):
            a = a.copy(dcpa, cpa, worklist)
        if (
            not (
                isinstance(b.thing, python.Variable)
                and parent_func(gx, b.thing) != func
            )
            and b.dcpa == 0
        ):
            b = b.copy(dcpa, cpa, worklist)

        add_constraint(gx, a, b, worklist)

    # --- iterative flow analysis: seed allocation sites in new template
    seed_template(gx, func, cart, dcpa, cpa, worklist)


def parent_func(gx: "config.GlobalInfo", thing: Any) -> Optional["python.Function"]:
    """Get the parent function of a node"""
    return python.outer_func(inode(gx, thing).parent)


def class_copy(gx: "config.GlobalInfo", cl: "python.Class", dcpa: int) -> None:
    """Copy a class"""
    for var in cl.vars.values():  # XXX
        if (var, 0, 0) not in gx.cnode or inode(gx, var) not in gx.types:
            continue  # XXX research later, triggered for doom example

        inode(gx, var).copy(dcpa, 0)
        gx.types[gx.cnode[var, dcpa, 0]] = inode(gx, var).types().copy()

        for n in inode(gx, var).in_:  # XXX
            if isinstance(n.thing, ast.Constant):
                add_constraint(gx, n, gx.cnode[var, dcpa, 0])

    for func in cl.funcs.values():
        func_copy(gx, func, dcpa, 0)

        # --- a method copied here is not a template yet, so its allocation
        # --- sites are not seeded (cart is None), and CNode.copy has given
        # --- each constructor node the types of the base copy: the shared
        # --- bucket contour. Propagation reads that before the template is
        # --- created for real and seeded from the core, and a bucket
        # --- iterator is already flowing out of list.__iter__(7) by the time
        # --- the site gets its own contour. The old analysis special-cased
        # --- __iter__ for the same reason; the sweep owns every site, so
        # --- nothing is known here and the node holds nothing.
        for node in func.nodes:
            if node.constructor and isinstance(
                node.thing,
                (ast.List, ast.Dict, ast.Set, ast.Tuple, ast.ListComp, ast.Call),
            ):
                copied = gx.cnode.get((node.thing, dcpa, 0))
                if copied is not None and copied is not node:
                    gx.types[copied] = set()


def seed_template(
    gx: "config.GlobalInfo",
    func: "python.Function",
    cart: Optional[CartesianProduct],
    dcpa: int,
    cpa: int,
    worklist: Optional[list[CNode]],
) -> None:
    """Seed allocation sites in newly created templates

    A mold in a newly created template becomes a real allocation site here,
    so this is where it is given its contour: the one the contours core
    already has for this (function, cart, node), or its class's shared bucket
    if the core has none yet.
    """
    if cart is None:  # not in the process of propagation
        return
    core = gx.contour_core
    assert core is not None, "templates are only created during contour analysis"
    if isinstance(func.parent, python.Class):  # self
        cart = ((func.parent, dcpa),) + cart

    for node in func.nodes_ordered:
        if node.constructor and isinstance(
            node.thing, (ast.List, ast.Dict, ast.Set, ast.Tuple, ast.ListComp, ast.Call)
        ):
            assert isinstance(node.parent, python.Function)
            parent = node.parent
            while isinstance(parent.parent, python.Function):
                parent = parent.parent

            alloc_id: tuple[str, CartesianProduct, ast.AST] = (
                parent.ident,
                cart,
                node.thing,
            )  # XXX ident?
            alloc_node = gx.cnode[node.thing, dcpa, cpa]

            binding = core.note_mold(gx, alloc_id, node)
            if binding is None and gx.orig_types[node]:
                binding = list(gx.orig_types[node])[0]
            if binding is not None:
                gx.types[alloc_node] = {binding}
                add_to_worklist(worklist, alloc_node)


# ---------------------------------------------------------------------------
# backing up and restoring the graph
# ---------------------------------------------------------------------------


# --- shared, immutable stand-in for an empty set, so that snapshots of the
# --- constraint network do not allocate one empty set per node. It must never
# --- be stored where a mutable set is expected.
EMPTY_SET: frozenset = frozenset()


def backup_network(gx: "config.GlobalInfo") -> Backup:
    """Backup the constraint network

    Most nodes carry no types and have no incoming or outgoing edges, so the
    bulk of the work here used to be allocating empty set copies. Empty sets
    are stored as the shared immutable EMPTY_SET marker instead;
    `restore_network` turns them back into fresh mutable sets where needed.
    The two passes over `gx.types` are also fused into one.
    """
    beforetypes: dict[CNode, AbstractSet[tuple[Any, int]]] = {}
    beforeinout: dict[CNode, tuple[AbstractSet[CNode], AbstractSet[CNode]]] = {}

    for node, typeset in gx.types.items():
        beforetypes[node] = typeset.copy() if typeset else EMPTY_SET
        in_ = node.in_
        out = node.out
        beforeinout[node] = (
            in_.copy() if in_ else EMPTY_SET,
            out.copy() if out else EMPTY_SET,
        )

    beforeconstr = gx.constraints.copy()
    beforecnode = gx.cnode.copy()

    return (beforetypes, beforeconstr, beforeinout, beforecnode)


def restore_network(gx: "config.GlobalInfo", backup: Backup) -> None:
    """Restore the constraint network"""
    beforetypes, beforeconstr, beforeinout, beforecnode = backup

    cur = gx.types
    for node in list(cur):
        before = beforetypes.get(node)
        if before is None:
            del cur[node]
        elif cur[node] != before:
            cur[node] = set(before)
    if len(cur) != len(beforetypes):
        for node, typeset in beforetypes.items():
            if node not in cur:
                cur[node] = set(typeset)

    gx.constraints = beforeconstr.copy()
    gx.cnode = beforecnode.copy()

    for node in gx.types:
        # only reallocate what is not already empty on both sides
        if node.nodecp:
            node.nodecp = set()
        node.defnodes = False
        before_in, before_out = beforeinout[node]
        if node.in_ or before_in:
            node.in_ = set(before_in)
        if node.out or before_out:
            node.out = set(before_out)

    for func in gx.allfuncs:
        func.cp = {}
        # drop nodes created during the iteration that this restore just
        # dropped from gx.cnode (default-argument notification nodes are
        # remade every iteration, see possible_argtypes)
        stale = {n for n in func.nodes if gx.cnode.get((n.thing, n.dcpa, n.cpa)) is not n}
        if stale:
            func.nodes -= stale
            func.nodes_ordered = [n for n in func.nodes_ordered if n not in stale]


# ---------------------------------------------------------------------------
# after analysis
# ---------------------------------------------------------------------------


# --- merge constraint network along combination of given dimensions (dcpa, cpa, inheritance)
# e.g. for annotation we merge everything; for code generation, we might want to create specialized code
def merged(
    gx: "config.GlobalInfo", nodes: Iterable[CNode], inheritance: bool = False
) -> Merged:
    """Merge constraint networks along given dimensions"""

    merge: Merged = {}

    if inheritance:  # XXX do we really need this crap
        mergeinh = merged(gx, [n for n in nodes if n.thing in gx.inherited])
        mergenoinh = merged(gx, [n for n in nodes if n.thing not in gx.inherited])

    for node in nodes:
        # --- merge node types
        sortdefault = merge.setdefault(node.thing, set())
        sortdefault.update(gx.types[node])

        # --- merge inheritance nodes
        if inheritance:
            inh = gx.inheritance_relations.get(node.thing, [])

            # merge function variables with their inherited versions (we don't customize!)
            if isinstance(node.thing, python.Variable) and isinstance(
                node.thing.parent, python.Function
            ):
                var = node.thing
                for inhfunc in gx.inheritance_relations.get(node.thing.parent, []):
                    assert isinstance(inhfunc, python.Function)
                    if var.name in inhfunc.vars:
                        if inhfunc.vars[var.name] in mergenoinh:
                            sortdefault.update(mergenoinh[inhfunc.vars[var.name]])
                for inhvar in gx.inheritance_temp_vars.get(var, []):  # XXX more general
                    if inhvar in mergenoinh:
                        sortdefault.update(mergenoinh[inhvar])

            # node is not a function variable
            else:
                for n in inh:
                    if n in mergeinh:  # XXX ook mergenoinh?
                        sortdefault.update(mergeinh[n])
    return merge


def get_classes(gx: "config.GlobalInfo", var: "python.Variable") -> set["python.Class"]:
    """Get the classes of a variable"""
    return {
        t[0]
        for t in gx.merged_inh[var]
        if isinstance(t[0], python.Class) and not t[0].mv.module.builtin
    }


def nested_classes(
    gx: "config.GlobalInfo", var: "python.Variable"
) -> set["python.Class"]:
    """Get the classes of a variable, descending into builtin containers

    A user-defined class may only be reachable through a builtin container, as in
    'self.items = [Item()]'. Such classes are not returned by get_classes, so we
    walk the type variables of builtin classes (list.unit, dict.value, ..) as well.
    """
    from .typestr import types_var_types

    result = set()
    todo = list(gx.merged_inh[var])
    seen = set()

    while todo:
        t = todo.pop()
        if t in seen:
            continue
        seen.add(t)
        cl = t[0]
        if not isinstance(cl, python.Class):
            continue
        if not cl.mv.module.builtin:
            result.add(cl)
            continue
        for tvar in cl.tvar_names():
            todo.extend(types_var_types(gx, {t}, tvar))

    return result


def deepcopy_classes(
    gx: "config.GlobalInfo", classes: set["python.Class"]
) -> set["python.Class"]:
    """Deepcopy classes"""
    changed = True
    while changed:
        changed = False
        for cl in classes.copy():
            for var in cl.vars.values():
                if var not in gx.merged_inh:
                    continue
                newcl = nested_classes(gx, var)
                if newcl - classes:
                    changed = True
                    classes.update(newcl)
    return classes


def determine_classes(gx: "config.GlobalInfo") -> None:  # XXX modeling..?
    """Determine the classes of a module"""
    if "copy" not in gx.modules:
        return
    func = gx.modules["copy"].mv.funcs["copy"]
    var = func.vars[func.formals[0]]
    for cl in get_classes(gx, var):
        cl.has_copy = True
    func = gx.modules["copy"].mv.funcs["deepcopy"]
    var = func.vars[func.formals[0]]
    for cl in deepcopy_classes(gx, nested_classes(gx, var)):
        cl.has_deepcopy = True


def var_types(gx: "config.GlobalInfo", var: "python.Variable") -> Types:
    """Get the types of a variable"""
    return inode(gx, var).types()
