# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.graph: Builds and manages the constraint graph for type inference

This module implements a constraint-based type inference system using a graph structure
where types "flow" during analysis. The constraint graph is used to determine possible
types for variables and expressions through dataflow analysis.

Key concepts:
- Constraint Graph: A directed graph where nodes represent program elements and edges
  represent type constraints between them. For example, in `a = b`, types flow from
  `b` to `a` since `a` must be able to hold any type that `b` could be.

- Constraint Graph Structure:
  - Nodes are stored in `gx.cnode`
  - Type sets for each node are stored in `gx.types` 
  - Each node is identified by (AST Node, int, int), where the integers are used
    by `infer.py` to duplicate graph sections (class duplicate, function duplicate).
    Initially both are 0.

Key components:
- `ModuleVisitor`: Inherits from `ast_utils.BaseNodeVisitor` and traverses Python AST
  to recursively generate type constraints for each syntactical Python language
  construct, calling specialized methods (such as `visitFor` for for-loops) as needed
  and introducing temporary variables as needed for C++ translation.

- `parse_module()`: Entry point that locates and processes Python modules, using
  `ModuleVisitor` for uncached modules.
"""


import ast
import copy
import os
import pathlib
import re
import string
import sys
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, TypeAlias, Union

from . import ast_utils, error, infer, python

if TYPE_CHECKING:
    from . import config

Parent: TypeAlias = Union["python.Class", "python.Function"]
AllParent: TypeAlias = Union["python.Class", "python.Function", "python.StaticClass"]

# --- global variable mv
_mv: "ModuleVisitor"


def setmv(mv: "ModuleVisitor") -> "ModuleVisitor":
    """Set and return the global module visitor"""
    global _mv
    _mv = mv
    return _mv


def getmv() -> "ModuleVisitor":
    """Get the global module visitor"""
    return _mv


def check_redef(
    gx: "config.GlobalInfo",
    node: Union[ast.ClassDef, ast.FunctionDef],
    s: Optional[str] = None,
    onlybuiltins: bool = False,
) -> None:
    """Check for redefinition of a function or class"""
    # XXX to modvisitor, rewrite
    mv = getmv()
    if mv and mv.module and not mv.module.builtin:
        existing_names = list(mv.ext_classes) + list(mv.ext_funcs)
        if not onlybuiltins:
            existing_names.extend(mv.classes)
            existing_names.extend(mv.funcs)
        if s is not None:
            name = s
        else:
            name = node.name
        if name in existing_names:
            error.error("function/class redefinition is not supported", gx, node, mv=mv)


# --- maintain inheritance relations between copied AST nodes
def inherit_rec(
    gx: "config.GlobalInfo", original: ast.AST, copy: ast.AST, mv: "ModuleVisitor"
) -> None:
    """Inherit recursively from an original AST node to a copy"""
    gx.inheritance_relations.setdefault(original, []).append(copy)
    gx.inherited.add(copy)
    gx.parent_nodes[copy] = original

    for a, b in zip(ast.iter_child_nodes(original), ast.iter_child_nodes(copy)):
        inherit_rec(gx, a, b, mv)


def register_node(node: ast.AST, func: Optional["python.Function"]) -> None:
    """Register a node with a function"""
    if func:
        func.registered.append(node)


def slice_nums(nodes: List[Optional[ast.AST]]) -> List[ast.AST]:
    """Slice numbers from a list of nodes"""
    nodes2: List[ast.AST] = []
    x = 0
    for i, n in enumerate(nodes):
        if not n or ast_utils.is_none(n):
            nodes2.append(ast.Num(0))
        else:
            nodes2.append(n)
            x |= 1 << i
    nodes2.insert(0, ast.Num(x))
    return nodes2


def get_arg_nodes(node: ast.Call) -> List[ast.expr]:
    """Get argument nodes from a call node"""
    args = []

    for arg in node.args:
        if isinstance(arg, ast.Starred):
            arg = arg.value
        args.append(arg)

    if node.keywords:
        args.extend([kw.value for kw in node.keywords])

    return args


def has_star_kwarg(node: ast.Call) -> bool:
    """Check if a call node has a starred keyword argument"""
    for arg in node.args:
        if isinstance(arg, ast.Starred):
            return True

    for kw in node.keywords:
        if kw.arg is None:
            return True

    return False


def make_arg_list(argnames: List[str]) -> ast.arguments:
    """Make a simple argument list from a list of argument names"""
    args = [ast.arg(a) for a in argnames]
    return ast.arguments([], args, None, [], [], None, [])


def is_property_setter(dec: ast.AST) -> bool:
    """Check if a decorator is a property setter"""
    return (
        isinstance(dec, ast.Attribute)
        and isinstance(dec.value, ast.Name)
        and dec.attr == "setter"
    )


# --- module visitor; analyze program, build constraint graph
class ModuleVisitor(ast_utils.BaseNodeVisitor):
    """Module visitor for analyzing program and building constraint graph"""

    def __init__(self, module: python.Module, gx: "config.GlobalInfo"):
        ast_utils.BaseNodeVisitor.__init__(self)
        self.module = module
        self.gx = gx
        self.classes: dict[str, "python.Class"] = {}
        self.funcs: dict[str, "python.Function"] = {}
        self.globals: dict[str, "python.Variable"] = {}
        self.exc_names: dict[str, "python.Variable"] = {}
        self.current_with_vars: List[List[str]] = []

        self.lambdas: dict[str, "python.Function"] = {}
        self.imports: dict[str, "python.Module"] = {}
        self.fake_imports: dict[str, "python.Module"] = {}
        self.ext_classes: dict[str, "python.Class"] = {}
        self.ext_funcs: dict[str, "python.Function"] = {}
        self.lambdaname: dict[ast.AST, str] = {}
        self.lwrapper: dict[ast.AST, str] = {}
        self.tempcount = self.gx.tempcount
        self.listcomps: List[
            Tuple[ast.ListComp, "python.Function", Optional["python.Function"]]
        ] = []
        self.defaults: dict[ast.AST, Tuple[int, "python.Function", int]] = {}

        self.importnodes: List[ast.AST] = []
        self.funcnodes: List[ast.FunctionDef]
        self.classnodes: List[ast.ClassDef]

    def visit(self, node: ast.AST, *args: Any) -> None:
        """Visit a node"""
        if (node, 0, 0) not in self.gx.cnode:
            ast_utils.BaseNodeVisitor.visit(self, node, *args)

    def fake_func(
        self,
        node: Any,
        objexpr: ast.AST,
        attrname: str,
        args: List[ast.AST],
        func: Optional[python.Function] = None,
    ) -> ast.Call:
        """Generate a fake function"""
        if (node, 0, 0) in self.gx.cnode:  # XXX
            newnode = self.gx.cnode[node, 0, 0]
        else:
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)
            self.gx.types[newnode] = set()

        fakefunc = ast.Call(ast.Attribute(objexpr, attrname, ast.Load()), args, [])
        fakefunc.lineno = objexpr.lineno
        self.visit(fakefunc, func)
        self.add_constraint((infer.inode(self.gx, fakefunc), newnode), func)

        infer.inode(self.gx, objexpr).fakefunc = fakefunc
        return fakefunc

    # simple heuristic for initial list split: count nesting depth, first constant child type
    def list_type(self, node: ast.AST) -> Optional[int]:
        """Determine the type of a list"""
        assert isinstance(node, (ast.List, ast.ListComp, ast.Call))
        count = 0
        child: Any = node
        while isinstance(child, (ast.List, ast.ListComp)):
            if isinstance(child, ast.List):
                if not child.elts:
                    return None
                child = child.elts[0]
                count += 1
            else:
                if not child.elt:
                    return None
                child = child.elt
                count += 1

        if isinstance(child, ast.UnaryOp) and isinstance(
            child.op, (ast.USub, ast.UAdd)
        ):
            child = child.operand

        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            map = {"int": int, "str": str, "float": float}
            func_id = child.func.id
            if func_id in ("range"):  # ,'xrange'):
                count, child = count + 1, int
            elif func_id in map:
                child = map[func_id]
            elif (
                func_id in (cl.ident for cl in self.gx.allclasses)
                or func_id in getmv().classes
            ):  # XXX getmv().classes
                child = func_id
            else:
                if count == 1:
                    return None
                child = None
        elif isinstance(child, ast.Num):
            child = type(child.n)
        elif isinstance(child, ast.Str):
            child = type(child.s)
        elif isinstance(child, ast.Name) and child.id in ("True", "False"):
            child = bool
        elif isinstance(child, ast.Tuple):
            child = tuple
        elif isinstance(child, ast.Dict):
            child = dict
        else:
            if count == 1:
                return None
            child = None

        self.gx.list_types.setdefault((count, child), len(self.gx.list_types) + 2)
        return self.gx.list_types[count, child]

    def instance(
        self,
        node: ast.AST,
        cl: "python.Class",
        func: Optional["python.Function"] = None,
    ) -> None:
        """Generate an instance of a class"""
        if (node, 0, 0) in self.gx.cnode:  # XXX to create_node() func
            newnode = self.gx.cnode[node, 0, 0]
        else:
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)

        newnode.constructor = True

        if cl.ident in ["int_", "float_", "str_", "bytes_", "none", "class_", "bool_"]:
            self.gx.types[newnode] = set([(cl, cl.dcpa - 1)])
        else:
            if cl.ident == "list" and (dcpa := self.list_type(node)):
                self.gx.types[newnode] = set([(cl, dcpa)])
            else:
                self.gx.types[newnode] = set([(cl, cl.dcpa)])

    def constructor(
        self,
        node: Union[ast.Tuple, ast.List, ast.Dict, ast.Set],
        classname: str,
        func: Optional["python.Function"],
    ) -> None:
        """Generate a constructor"""
        cl = python.def_class(self.gx, classname)
        assert cl

        self.instance(node, cl, func)
        infer.default_var(self.gx, "unit", cl)

        # --- internally flow binary tuples
        if isinstance(node, ast.Tuple) and cl.ident == "tuple2":
            infer.default_var(self.gx, "first", cl)
            infer.default_var(self.gx, "second", cl)
            elem0, elem1 = node.elts

            self.visit(elem0, func)
            self.visit(elem1, func)

            self.add_dynamic_constraint(node, elem0, "unit", func)
            self.add_dynamic_constraint(node, elem1, "unit", func)

            self.add_dynamic_constraint(node, elem0, "first", func)
            self.add_dynamic_constraint(node, elem1, "second", func)

            return

        # --- add dynamic children constraints for other types
        if isinstance(node, ast.Dict):  # XXX filter children
            infer.default_var(self.gx, "unit", cl)
            infer.default_var(self.gx, "value", cl)

            for child in ast.iter_child_nodes(node):
                self.visit(child, func)

            for key, value in zip(node.keys, node.values):  # XXX filter
                assert key  # TODO when None?
                self.add_dynamic_constraint(node, key, "unit", func)
                self.add_dynamic_constraint(node, value, "value", func)
        else:
            for child in node.elts:
                self.visit(child, func)

            for child in self.filter_redundant_children(node):
                self.add_dynamic_constraint(node, child, "unit", func)

    # --- for compound list/tuple/dict constructors, we only consider a single child node for each subtype
    def filter_redundant_children(
        self, node: Union[ast.Tuple, ast.List, ast.Set]
    ) -> List[ast.AST]:
        """Filter redundant children from a compound list/tuple/dict constructor"""
        done = set()
        nonred: List[ast.AST] = []
        for child in node.elts:
            type = self.child_type_rec(child)
            if not type or type not in done:
                done.add(type)
                nonred.append(child)
        return nonred

    # --- determine single constructor child node type, used by the above
    def child_type_rec(self, node: ast.AST) -> Tuple["python.Class", ...]:
        """Determine the type of a single constructor child node"""
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            node = node.operand

        if isinstance(node, (ast.List, ast.Tuple)):
            if isinstance(node, ast.List):
                cl = python.def_class(self.gx, "list")
            elif len(node.elts) == 2:
                cl = python.def_class(self.gx, "tuple2")
            else:
                cl = python.def_class(self.gx, "tuple")

            merged = set()
            assert isinstance(
                node, (ast.List, ast.Tuple)
            )  # why needed after isinstance check above
            for child in node.elts:
                merged.add(self.child_type_rec(child))

            if len(merged) == 1:
                return (cl,) + merged.pop()

        elif isinstance(node, (ast.Num, ast.Str)):
            return (list(infer.inode(self.gx, node).types())[0][0],)

        return ()

    # --- add dynamic constraint for constructor argument, e.g. '[expr]' becomes [].__setattr__('unit', expr)
    def add_dynamic_constraint(
        self,
        parent: ast.AST,
        child: ast.AST,
        varname: str,
        func: Optional["python.Function"],
    ) -> None:
        """Add a dynamic constraint for a constructor argument"""
        self.gx.assign_target[child] = parent
        cu = ast.Str(varname)
        self.visit(cu, func)
        fakefunc = ast.Call(
            ast.Attribute(parent, "__setattr__", ast.Load()), [cu, child], []
        )
        self.visit_Call(fakefunc, func, fake_attr=True)

        fakechildnode = infer.CNode(
            self.gx, getmv(), (child, varname), parent=func
        )  # create separate 'fake' infer.CNode per child, so we can have multiple 'callfuncs'
        self.gx.types[fakechildnode] = set()

        self.add_constraint(
            (infer.inode(self.gx, parent), fakechildnode), func
        )  # add constraint from parent to fake child node. if parent changes, all fake child nodes change, and the callfunc for each child node is triggered
        fakechildnode.callfuncs.append(fakefunc)

    # --- add regular constraint to function
    def add_constraint(
        self,
        constraint: Tuple[infer.CNode, infer.CNode],
        func: Optional["python.Function"],
    ) -> None:
        """Add a regular constraint to a function"""
        infer.in_out(constraint[0], constraint[1])
        self.gx.constraints.add(constraint)
        parent: Optional[AllParent] = func
        while (
            isinstance(parent, python.Function) and parent.listcomp
        ):  # TODO occurs frequently, ugly typing.. add Function method(s)
            parent = parent.parent
        if isinstance(parent, python.Function):
            parent.constraints.add(constraint)

    def struct_unpack(self, rvalue: ast.AST, func: Optional["python.Function"]) -> bool:
        """Check if a call node is a struct unpack"""
        if isinstance(rvalue, ast.Call):
            struct_var = python.lookup_var("struct", func, self)
            if (
                isinstance(rvalue.func, ast.Attribute)
                and isinstance(rvalue.func.value, ast.Name)
                and rvalue.func.value.id == "struct"
                and rvalue.func.attr in ("unpack", "unpack_from")
                and struct_var
                and struct_var.imported
            ):  # XXX imported from where?
                return True
            elif (
                isinstance(rvalue.func, ast.Name)
                and rvalue.func.id in ("unpack", "unpack_from")
                and rvalue.func.id in self.ext_funcs
                and not python.lookup_var(rvalue.func.id, func, self)
            ):  # XXX imported from where?
                return True
        return False

    def struct_info(
        self, node: ast.AST, func: Optional["python.Function"]
    ) -> List[Tuple[str, str, str, int]]:
        """Get struct information"""
        if isinstance(node, ast.Name):
            var = python.lookup_var(node.id, func, self)  # XXX fwd ref?
            if not var or len(var.const_assign) != 1:
                error.error("non-constant format string", self.gx, node, mv=self)
            error.error(
                "assuming constant format string", self.gx, node, mv=self, warning=True
            )
            assert var
            fmt = var.const_assign[0].s
        elif isinstance(node, ast.Num):
            fmt = node.n
        elif isinstance(node, ast.Str):
            fmt = node.s
        else:
            error.error("non-constant format string", self.gx, node, mv=self)
        char_type = {
            "x": "x",
            "c": "s",
            "b": "i",
            "B": "i",
            "?": "b",
            "h": "i",
            "H": "i",
            "i": "i",
            "I": "i",
            "l": "i",
            "L": "i",
            "q": "i",
            "Q": "i",
            "f": "f",
            "d": "f",
            "s": "s",
            "p": "s",
        }
        ordering = "@"
        if fmt and fmt[0] in "@<>!=":
            ordering, fmt = fmt[0], fmt[1:]
        result = []
        digits = ""
        for i, c in enumerate(fmt):
            if c.isdigit():
                digits += c
            elif c in char_type:
                rtype = {
                    "i": "int",
                    "s": "bytes",
                    "b": "bool",
                    "f": "float",
                    "x": "pad",
                }[char_type[c]]
                if rtype == "bytes" and c != "c":
                    result.append((ordering, c, "bytes", int(digits or "1")))
                elif digits == "0":
                    result.append((ordering, c, rtype, 0))
                else:
                    result.extend(int(digits or "1") * [(ordering, c, rtype, 1)])
                digits = ""
            elif c in string.whitespace:
                pass
            else:
                error.error(
                    "bad or unsupported char in struct format: " + repr(c),
                    self.gx,
                    node,
                    mv=self,
                )
                digits = ""
        return result

    def struct_faketuple(self, info: List[Tuple[str, str, str, int]]) -> ast.Tuple:
        """Generate a fake tuple for struct unpack"""
        result: List[ast.AST] = []
        for o, c, t, d in info:
            if d != 0 or c == "s":
                if t == "int":
                    result.append(ast.Num(1))
                elif t == "bytes":
                    result.append(ast.Str(b""))
                elif t == "float":
                    result.append(ast.Num(1.0))
                elif t == "bool":
                    result.append(ast.Name("True", ast.Load()))
        return ast.Tuple(result, ast.Load())

    def visit_GeneratorExp(
        self, node: ast.GeneratorExp, func: Optional["python.Function"] = None
    ) -> None:
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        lc = ast.ListComp(
            node.elt,
            [
                ast.comprehension(qual.target, qual.iter, qual.ifs)
                for qual in node.generators
            ],
            lineno=node.lineno,
        )
        register_node(lc, func)
        self.gx.genexp_to_lc[node] = lc
        self.visit(lc, func)
        self.add_constraint((infer.inode(self.gx, lc), newnode), func)

    def visit_JoinedStr(
        self, node: ast.JoinedStr, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a joined string"""
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                if value.format_spec:
                    error.error(
                        "f-string format spec is not supported",
                        self.gx,
                        node,
                        warning=True,
                        mv=getmv(),
                    )
                value = value.value
            self.visit(value, func)
            self.fake_func(infer.inode(self.gx, value), value, "__str__", [], func)
        self.instance(node, python.def_class(self.gx, "str_"), func)

    def visit_Expr(
        self, node: ast.Expr, func: Optional["python.Function"] = None
    ) -> None:
        """Visit an expression"""
        self.bool_test_add(node.value)
        self.visit(node.value, func)

    def visit_NamedExpr(
        self, node: ast.NamedExpr, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a named expression"""
        self.visit(node.value, func)

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        self.add_constraint((infer.inode(self.gx, node.value), newnode), func)

        assert isinstance(node.target, ast.Name)

        parent: Optional[AllParent] = func
        while parent and isinstance(parent, python.Function) and parent.listcomp:
            parent.misses_by_ref.add(node.target.id)
            parent = parent.parent

        assert isinstance(parent, (python.Function, type(None)))

        lvar = self.default_var(
            node.target.id, parent
        )  # TODO shouldn't this be in orig func
        self.add_constraint((newnode, infer.inode(self.gx, lvar)), parent)

    def visit_Module(self, node: ast.Module) -> None:
        """Visit a module"""
        # --- bootstrap built-in classes
        if self.module.ident == "builtin":
            for dummy in self.gx.builtins:
                self.visit(ast.ClassDef(dummy, [], [], [ast.Pass()]))

        if self.module.ident != "builtin":
            n = ast.ImportFrom("builtin", [ast.alias("*", None)], None)  # Python2.5+
            getmv().importnodes.append(n)
            self.visit(n)

        # --- __name__
        if self.module.ident != "builtin":
            namevar = infer.default_var(self.gx, "__name__", None, mv=getmv())
            self.gx.types[infer.inode(self.gx, namevar)] = set(
                [(python.def_class(self.gx, "str_"), 0)]
            )

        self.forward_references(node)

        # --- visit children
        getmv().importnodes.extend(
            n for n in node.body if isinstance(n, (ast.Import, ast.ImportFrom))
        )
        for child in node.body:
            self.visit(child, None)

        # --- register classes
        for cl in getmv().classes.values():
            self.gx.allclasses.add(cl)

        # --- inheritance expansion

        # determine base classes
        for cl in self.classes.values():
            for base in cl.node.bases:
                if not (isinstance(base, ast.Name) and base.id == "object"):
                    ancestor = python.lookup_class(base, getmv())
                    assert ancestor
                    cl.bases.append(ancestor)
                    ancestor.children.append(cl)

        # for each base class, duplicate methods
        for cl in self.classes.values():
            for ancestor in cl.ancestors_upto(None)[1:]:
                cl.staticmethods.extend(ancestor.staticmethods)
                cl.properties.update(ancestor.properties)

                for func in ancestor.funcs.values():
                    if not func.node or func.inherited:
                        continue

                    ident = func.ident
                    if ident in cl.funcs:
                        ident += ancestor.ident + "__"

                    # deep-copy AST function nodes
                    func_copy = copy.deepcopy(func.node)
                    inherit_rec(self.gx, func.node, func_copy, func.mv)
                    tempmv, mv = getmv(), func.mv
                    setmv(mv)
                    self.visit_FunctionDef(func_copy, cl, inherited_from=ancestor)
                    mv = tempmv
                    setmv(mv)

                    # maintain relation with original
                    self.gx.inheritance_relations.setdefault(func, []).append(
                        cl.funcs[ident]
                    )
                    cl.funcs[ident].inherited = func.node
                    cl.funcs[ident].inherited_from = func
                    func_copy.name = ident

                    if ident == func.ident:
                        cl.funcs[ident + ancestor.ident + "__"] = cl.funcs[ident]

    def forward_references(self, node: ast.Module) -> None:
        """Forward references"""
        getmv().classnodes = []

        # classes
        for n in node.body:
            if isinstance(n, ast.ClassDef):
                check_redef(self.gx, n)
                getmv().classnodes.append(n)
                newclass = python.Class(self.gx, n, getmv(), self.module)
                self.classes[n.name] = newclass
                getmv().classes[n.name] = newclass

                # methods
                for m in n.body:
                    if isinstance(m, ast.FunctionDef):
                        if m.decorator_list and [
                            dec for dec in m.decorator_list if is_property_setter(dec)
                        ]:
                            m.name = m.name + "__setter__"
                        if (
                            m.name in newclass.funcs
                        ):  # and func.ident not in ['__getattr__', '__setattr__']: # XXX
                            error.error(
                                "function/class redefinition is not allowed",
                                self.gx,
                                m,
                                mv=getmv(),
                            )
                        self.remove_poskw_only_args(m)
                        func = python.Function(self.gx, getmv(), m, newclass)
                        newclass.funcs[func.ident] = func
                        self.set_default_vars(m, func)

        # functions
        getmv().funcnodes = []
        for n in node.body:
            if isinstance(n, ast.FunctionDef):
                check_redef(self.gx, n)
                getmv().funcnodes.append(n)
                self.remove_poskw_only_args(n)
                func = getmv().funcs[n.name] = python.Function(self.gx, getmv(), n)
                self.set_default_vars(n, func)

        # global variables XXX visit_Global
        for assname in self.local_assignments(node, global_=True):
            infer.default_var(self.gx, assname.id, None, mv=getmv())

    def set_default_vars(self, node: ast.AST, func: "python.Function") -> None:
        """Set default variables"""
        globals = set(self.get_globals(node))
        for assname in self.local_assignments(node):
            if assname.id not in globals:
                infer.default_var(self.gx, assname.id, func)

    def remove_poskw_only_args(self, node: ast.FunctionDef) -> None:
        """Ignore /, * (pos-only, keyword-only) arguments"""
        if node.args.posonlyargs or node.args.kwonlyargs:
            node.args.args = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            node.args.posonlyargs = []
            node.args.kwonlyargs = []

    def get_globals(self, node: ast.AST) -> List[str]:
        """Get global variables"""
        if isinstance(node, ast.Global):
            result = node.names
        else:
            result = []
            for child in ast.iter_child_nodes(node):
                result.extend(self.get_globals(child))
        return result

    def local_assignments(self, node: ast.AST, global_: bool = False) -> List[ast.Name]:
        """Get local assignments"""
        if global_ and isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            return []
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp)):
            return []
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            result = [node]
        else:
            # Try-Excepts introduce a new small scope with the exception name,
            # so we skip it here.
            children: List[ast.AST]

            if isinstance(node, ast.Try):
                children = list(node.body)
                for handler in node.handlers:
                    children.extend(handler.body)
                if node.orelse:
                    children.extend(node.orelse)
            elif isinstance(node, ast.With):
                children = list(node.body)
            else:
                children = list(ast.iter_child_nodes(node))

            result = []
            for child in children:
                result.extend(self.local_assignments(child, global_))
        return result

    def visit_Import(
        self, node: ast.Import, func: Optional["python.Function"] = None
    ) -> None:
        """Visit an import"""
        if node not in getmv().importnodes:
            error.error(
                "please place all imports (no 'try:' etc) at the top of the file",
                self.gx,
                node,
                mv=getmv(),
            )

        for name_alias in node.names:
            if name_alias.name == "typing":
                continue

            (name, pseudonym) = (name_alias.name, name_alias.asname)
            if pseudonym:
                # --- import a.b as c: don't import a
                self.import_module(name, pseudonym, node, False)
            else:
                self.import_modules(name, node, False)

    def import_modules(
        self, name: Optional[str], node: ast.AST, fake: bool
    ) -> "python.Module":
        """Return last imported module"""
        # in case of relative import, make name absolute
        level = getattr(node, "level", None) or 0
        if level > 0:
            newname = ".".join(getmv().module.name.split(".")[: -level + 1])
            if name:
                if newname:
                    name = newname + "." + name
            else:
                name = newname

        # --- import a.b.c: import a, then a.b, then a.b.c
        assert name
        split = name.split(".")
        module = getmv().module
        for i in range(len(split)):
            subname = ".".join(split[: i + 1])
            parent = module
            module = self.import_module(subname, subname, node, fake)
            if module.ident not in parent.mv.imports:  # XXX
                if not fake:
                    parent.mv.imports[module.ident] = module
        return module

    def import_module(
        self, name: str, pseudonym: Optional[str], node: ast.AST, fake: bool
    ) -> "python.Module":
        """Return an already imported module"""
        module = self.analyze_module(name, pseudonym or name, node, fake)
        if not fake:
            var = infer.default_var(self.gx, pseudonym or name, None, mv=getmv())
            var.imported = True
            self.gx.types[infer.inode(self.gx, var)] = set([(module, 0)])
        return module

    def visit_ImportFrom(
        self, node: ast.ImportFrom, parent: Optional["python.Function"] = None
    ) -> None:
        """Visit an import from"""
        if node.module == "typing":
            return

        if node not in getmv().importnodes:  # XXX use (func, node) as parent..
            error.error(
                "please place all imports (no 'try:' etc) at the top of the file",
                self.gx,
                node,
                mv=getmv(),
            )

        # from __future__ import
        if node.module == "__future__":
            for node_name in node.names:
                name = node_name.name
                if name not in ["with_statement", "print_function"]:
                    error.error(
                        "future '%s' is not yet supported" % name,
                        self.gx,
                        node,
                        mv=getmv(),
                    )
            return

        # from . import (needed for 'illegal' import eg 'cd examples/c64; shedskin c64' as no root module)
        if node.module is None and hasattr(node, "level") and node.level == 1:
            for alias in node.names:
                submod = self.import_module(alias.name, alias.asname, node, False)
                parent2 = getmv().module
                parent2.mv.imports[submod.ident] = submod
                self.gx.from_module[node] = submod
                return

        # from [..]a.b.c import
        module = self.import_modules(node.module, node, True)
        self.gx.from_module[node] = module

        for name_alias in node.names:
            (name, pseudonym) = (name_alias.name, name_alias.asname)
            if name == "*":
                self.ext_funcs.update(module.mv.funcs)
                self.ext_classes.update(module.mv.classes)
                for import_name, import_module in module.mv.imports.items():
                    var = infer.default_var(
                        self.gx, import_name, None, mv=getmv()
                    )  # XXX merge
                    var.imported = True
                    self.gx.types[infer.inode(self.gx, var)] = set([(import_module, 0)])
                    self.imports[import_name] = import_module
                for name, extvar in module.mv.globals.items():
                    if not extvar.imported and name not in ["__name__"]:
                        var = infer.default_var(
                            self.gx, name, None, mv=getmv()
                        )  # XXX merge
                        var.imported = True
                        self.add_constraint(
                            (infer.inode(self.gx, extvar), infer.inode(self.gx, var)),
                            None,
                        )
                continue

            path = module.path
            pseudonym = pseudonym or name
            if name in module.mv.funcs:
                self.ext_funcs[pseudonym] = module.mv.funcs[name]
            elif name in module.mv.classes:
                self.ext_classes[pseudonym] = module.mv.classes[name]
            elif (
                name in module.mv.globals and not module.mv.globals[name].imported
            ):  # XXX
                extvar = module.mv.globals[name]
                var = infer.default_var(self.gx, pseudonym, None, mv=getmv())
                var.imported = True
                self.add_constraint(
                    (infer.inode(self.gx, extvar), infer.inode(self.gx, var)), None
                )
            elif os.path.isfile(os.path.join(path, name + ".py")) or os.path.isfile(
                os.path.join(path, name, "__init__.py")
            ):
                modname = ".".join(module.name_list + [name])
                self.import_module(modname, name, node, False)
            else:
                error.error(
                    "no identifier '%s' in module '%s'" % (name, node.module),
                    self.gx,
                    node,
                    mv=getmv(),
                )

    def analyze_module(
        self, name: str, pseud: str, node: ast.AST, fake: bool
    ) -> "python.Module":
        """Analyze a module"""
        module = parse_module(name, self.gx, getmv().module, node)
        if not fake:
            self.imports[pseud] = module
        else:
            self.fake_imports[pseud] = module
        return module

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
        parent: Optional["python.Class"] = None,
        is_lambda: bool = False,
        inherited_from: Optional["python.Class"] = None,
    ) -> None:
        """Visit a function definition"""

        if not getmv().module.builtin and (node.args.vararg or node.args.kwarg):
            error.error(
                "argument (un)packing is not supported", self.gx, node, mv=getmv()
            )

        if not parent and not is_lambda and node.name in getmv().funcs:
            func = getmv().funcs[node.name]
        elif (
            isinstance(parent, python.Class)
            and not inherited_from
            and node.name in parent.funcs
        ):
            func = parent.funcs[node.name]
        else:
            func = python.Function(self.gx, getmv(), node, parent, inherited_from)
            if inherited_from:
                self.set_default_vars(node, func)

        if not (
            isinstance(func, python.Function) and isinstance(func.parent, python.Class)
        ):
            if (
                not getmv().module.builtin
                and node not in getmv().funcnodes
                and not is_lambda
            ):
                error.error(
                    "non-global function '%s'" % node.name, self.gx, node, mv=getmv()
                )

        if node.decorator_list:
            for dec in node.decorator_list:
                if parent and isinstance(dec, ast.Name) and dec.id == "staticmethod":
                    parent.staticmethods.append(node.name)
                elif parent and isinstance(dec, ast.Name) and dec.id == "property":
                    parent.properties[node.name] = [node.name, ""]
                elif parent and is_property_setter(dec):
                    assert isinstance(dec, ast.Attribute)
                    assert isinstance(dec.value, ast.Name)
                    parent.properties[dec.value.id][1] = node.name
                else:
                    error.error(
                        "unsupported type of decorator", self.gx, dec, mv=getmv()
                    )

        if parent:
            if (
                not inherited_from
                and func.ident not in parent.staticmethods
                and (not func.formals or func.formals[0] != "self")
            ):
                error.error(
                    "formal arguments of method must start with 'self'",
                    self.gx,
                    node,
                    mv=getmv(),
                )
            if not func.mv.module.builtin and func.ident in [
                "__new__",
                "__getattr__",
                "__setattr__",
                "__radd__",
                "__rsub__",
                "__rmul__",
                "__rdiv__",
                "__rtruediv__",
                "__rfloordiv__",
                "__rmod__",
                "__rdivmod__",
                "__rpow__",
                "__rlshift__",
                "__rrshift__",
                "__rand__",
                "__rxor__",
                "__ror__",
                "__iter__",
                "__call__",
                "__enter__",
                "__exit__",
                "__del__",
                "__copy__",
                "__deepcopy__",
            ]:
                error.error(
                    "'%s' is not supported" % func.ident,
                    self.gx,
                    node,
                    warning=True,
                    mv=getmv(),
                )

        if is_lambda:
            self.lambdas[node.name] = func

        func.defaults = node.args.defaults

        for formal in func.formals:
            var = infer.default_var(self.gx, formal, func)
            var.formal_arg = True

        # --- flow return expressions together into single node
        func.retnode = retnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[retnode] = set()
        func.yieldnode = yieldnode = infer.CNode(
            self.gx, getmv(), (node, "yield"), parent=func
        )
        self.gx.types[yieldnode] = set()

        for body_node in node.body:
            self.visit(body_node, func)

        for i, default in enumerate(func.defaults):
            if (
                not ast_utils.is_literal(default) and not
                (isinstance(default, ast.Constant) and isinstance(default.value, bool))  # TODO fix is_literal
            ):
                self.defaults[default] = (len(self.defaults), func, i)
            self.visit(default, None)  # defaults are global

        # --- add implicit 'return None' if no return expressions
        if not func.returnexpr:
            func.fakeret = ast.Return(ast.Name("None", ast.Load()))
            self.visit(func.fakeret, func)

        # --- register function
        if isinstance(parent, python.Class):
            if func.ident not in parent.staticmethods:  # XXX use flag
                infer.default_var(self.gx, "self", func)
            parent.funcs[func.ident] = func

    def visit_Lambda(
        self, node: ast.Lambda, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a lambda function"""
        lambdanr = len(self.lambdas)
        name = "__lambda%d__" % lambdanr
        fakenode = ast.FunctionDef(name, node.args, [ast.Return(node.body)], [])
        self.visit(fakenode, None, True)
        f = self.lambdas[name]
        f.lambdanr = lambdanr
        self.lambdaname[node] = name
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set([(f, 0)])
        newnode.copymetoo = True

    def visit_BoolOp(
        self, node: ast.BoolOp, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a boolean operation"""
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        for child in node.values:
            if node in self.gx.bool_test_only:
                self.bool_test_add(child)
            self.visit(child, func)
            self.add_constraint((infer.inode(self.gx, child), newnode), func)
            self.temp_var2(child, newnode, func)

    def visit_If(
        self,
        node: ast.If,
        func: Optional["python.Function"] = None,
        root_if: Optional[ast.If] = None,
    ) -> None:
        """Visit an if statement"""
        # add temp var for to split up long if-elif-elif.. chains (MSVC error C1061, c64/hq2x examples)
        if not root_if:
            root_if = node
            chain_len = 0
            x = root_if
            while len(x.orelse) == 1 and isinstance(x.orelse[0], ast.If):
                x = x.orelse[0]
                chain_len += 1
            if chain_len > 100:
                self.temp_var_int(root_if, func)

        self.bool_test_add(node.test)
        faker = ast.Call(ast.Name("bool", ast.Load()), [node.test], [])
        self.visit(faker, func)
        for child in node.body:
            self.visit(child, func)
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            self.visit_If(node.orelse[0], func, root_if)
        else:
            for child in node.orelse:
                self.visit(child, func)

    def visit_IfExp(
        self, node: ast.IfExp, func: Optional["python.Function"] = None
    ) -> None:
        """Visit an if expression"""
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()

        for child in ast.iter_child_nodes(node):
            self.visit(child, func)

        self.add_constraint((infer.inode(self.gx, node.body), newnode), func)
        self.add_constraint((infer.inode(self.gx, node.orelse), newnode), func)

    def visit_Match(
        self, node: ast.Match, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a match statement"""
        error.error("match case statement not supported", self.gx, node, mv=getmv())

    def visit_Global(self, node: ast.Global, func: "python.Function") -> None:
        """Visit a global statement"""
        func.globals += node.names

    def visit_List(
        self, node: ast.List, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a list"""
        self.constructor(node, "list", func)

    def visit_Dict(
        self, node: ast.Dict, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a dictionary"""
        self.constructor(node, "dict", func)

    def visit_Set(
        self, node: ast.Set, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a set"""
        self.constructor(node, "set", func)

    def visit_Tuple(
        self, node: ast.Tuple, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a tuple"""
        if isinstance(node.ctx, ast.Load):
            if len(node.elts) == 2:
                self.constructor(node, "tuple2", func)
            else:
                self.constructor(node, "tuple", func)
        else:
            error.error("unsupported tuple ctx", self.gx, node, mv=getmv())

    def visit_Subscript(
        self, node: ast.Subscript, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a subscript"""
        # XXX merge __setitem__, __getitem__
        if isinstance(node.slice, ast.Slice):
            nslice = node.slice
            self.slice(
                node, node.value, [nslice.lower, nslice.upper, nslice.step], func
            )

        elif isinstance(node.slice, ast.Del):
            assert False
        #            if any(
        #                isinstance(dim, ast.Ellipsis) for dim in node.slice.dims
        #            ):  # XXX also check at setitem
        #                error.error("ellipsis is not supported", self.gx, node, mv=getmv())
        #            error.error("unsupported subscript method", self.gx, node, mv=getmv())

        else:
            if isinstance(node.slice, ast.Index):
                assert False
            #                subscript = node.slice.value
            else:
                subscript = node.slice

            if isinstance(node.ctx, ast.Del):
                self.fake_func(node, node.value, "__delitem__", [subscript], func)
            elif isinstance(subscript, (ast.List, ast.Tuple)):
                self.fake_func(node, node.value, "__getitem__", [subscript], func)
            else:
                ident = "__getitem__"
                self.fake_func(node, node.value, ident, [subscript], func)

    def visit_Slice(
        self, node: ast.Slice, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a slice"""
        assert False

    def slice(
        self,
        node: Union[ast.Slice, ast.Subscript],
        expr: ast.AST,
        nodes: List[Optional[ast.AST]],
        func: Optional["python.Function"],
        replace: Optional[ast.AST] = None,
    ) -> None:
        """Slice a node"""
        nodes2 = slice_nums(nodes)
        if replace:
            self.fake_func(node, expr, "__setslice__", nodes2 + [replace], func)
        elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Del):
            self.fake_func(node, expr, "__delete__", nodes2, func)
        else:
            self.fake_func(node, expr, "__slice__", nodes2, func)

    def visit_UnaryOp(
        self, node: ast.UnaryOp, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a unary operation"""
        op_type = type(node.op)
        if op_type == ast.Not:
            self.bool_test_add(node.operand)
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)
            newnode.copymetoo = True
            self.gx.types[newnode] = set(
                [(python.def_class(self.gx, "bool_"), 0)]
            )  # XXX new type?
            self.visit(node.operand, func)
        else:
            op_map = {
                ast.USub: "__neg__",
                ast.UAdd: "__pos__",
                ast.Invert: "__invert__",
            }
            self.fake_func(node, node.operand, op_map[op_type], [], func)

    def visit_Compare(
        self, node: ast.Compare, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a comparison"""
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        newnode.copymetoo = True
        self.gx.types[newnode] = set(
            [(python.def_class(self.gx, "bool_"), 0)]
        )  # XXX new type?
        self.visit(node.left, func)
        msgs = {
            ast.Eq: "eq",
            ast.NotEq: "ne",
            ast.Lt: "lt",
            ast.LtE: "le",
            ast.Gt: "gt",
            ast.GtE: "ge",
            ast.In: "contains",
            ast.NotIn: "contains",
        }  # 'Is' and IsNot only in cpp
        left = node.left
        for op, right in zip(node.ops, node.comparators):
            self.visit(right, func)
            msg = msgs.get(type(op))

            if msg == "contains":
                self.fake_func(node, right, "__" + msg + "__", [left], func)

                if (
                    isinstance(right, (ast.List, ast.Tuple)) and right.elts
                ):  # expr in [..]/(..) opt
                    self.temp_var2(
                        (right, "cmp"), infer.inode(self.gx, right.elts[0]), func
                    )

            elif msg in ("lt", "gt", "le", "ge"):
                fakefunc = ast.Call(
                    ast.Name("__%s" % msg, ast.Load()), [left, right], []
                )
                fakefunc.lineno = left.lineno
                self.visit(fakefunc, func)
            elif msg:
                self.fake_func(node, left, "__" + msg + "__", [right], func)
            left = right

        # tempvars, e.g. (t1=fun())
        for term in node.comparators[:-1]:
            if not (isinstance(term, ast.Name) or ast_utils.is_constant(term)):
                self.temp_var2(term, infer.inode(self.gx, term), func)

    def visit_BinOp(
        self, node: ast.BinOp, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a binary operation"""
        if isinstance(node.op, ast.Add):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "add"),
                [node.right],
                func,
            )
        elif isinstance(node.op, ast.Sub):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "sub"),
                [node.right],
                func,
            )
        elif isinstance(node.op, ast.Mult):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "mul"),
                [node.right],
                func,
            )
        elif isinstance(node.op, ast.Div):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "truediv"),
                [node.right],
                func,
            )
        elif isinstance(node.op, ast.FloorDiv):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "floordiv"),
                [node.right],
                func,
            )
        elif isinstance(node.op, ast.Pow):
            self.fake_func(node, node.left, "__pow__", [node.right], func)
        elif isinstance(node.op, ast.Mod):
            if isinstance(node.right, ast.Tuple):
                self.fake_func(node, node.left, "__mod__", [], func)
                for child in node.right.elts:
                    self.visit(child, func)
                    self.fake_func(
                        infer.inode(self.gx, child), child, "__str__", [], func
                    )
            else:
                self.fake_func(node, node.left, "__mod__", [node.right], func)
        elif isinstance(node.op, ast.LShift):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "lshift"),
                [node.right],
                func,
            )
        elif isinstance(node.op, ast.RShift):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "rshift"),
                [node.right],
                func,
            )
        elif isinstance(node.op, ast.BitOr):
            self.visit_impl_bitpair(node, ast_utils.aug_msg(self.gx, node, "or"), func)
        elif isinstance(node.op, ast.BitXor):
            self.visit_impl_bitpair(node, ast_utils.aug_msg(self.gx, node, "xor"), func)
        elif isinstance(node.op, ast.BitAnd):
            self.visit_impl_bitpair(node, ast_utils.aug_msg(self.gx, node, "and"), func)
        # PY3: elif isinstance(node.op, MatMult):
        else:
            error.error(
                "Unknown op type for ast.BinOp: %s" % type(node.op),
                self.gx,
                node,
                mv=getmv(),
            )

    def visit_impl_bitpair(
        self, node: ast.BinOp, msg: str, func: Optional["python.Function"] = None
    ) -> None:
        """Visit an implementation of a bitwise pair operation"""
        infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[infer.inode(self.gx, node)] = set()
        faker = self.fake_func((node.left, 0), node.left, msg, [node.right], func)
        self.add_constraint(
            (infer.inode(self.gx, faker), infer.inode(self.gx, node)), func
        )

    def visit_AugAssign(
        self, node: ast.AugAssign, func: Optional["python.Function"] = None
    ) -> None:
        """Visit an augmented assignment"""
        # a[b] += c -> a[b] = a[b]+c, using tempvars to handle sidefx
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()

        clone = copy.deepcopy(node)
        assert isinstance(clone, ast.AugAssign)
        lnode: ast.AST

        if isinstance(clone.target, ast.Name):
            blah = node.target
            lnode = ast.Name(clone.target.id, ast.Load(), lineno=node.target.lineno)
        elif isinstance(clone.target, ast.Attribute):
            blah = node.target
            lnode = ast.Attribute(
                clone.target.value,
                clone.target.attr,
                ast.Load(),
                lineno=node.target.lineno,
            )
        elif isinstance(node.target, ast.Subscript):
            t1 = self.temp_var(node.target.value, func)
            a1 = ast.Assign([ast.Name(t1.name, ast.Store())], node.target.value)
            self.visit(a1, func)
            self.add_constraint(
                (infer.inode(self.gx, node.target.value), infer.inode(self.gx, t1)),
                func,
            )

            if isinstance(node.target.slice, ast.Index):
                assert False
            #                subs = node.target.slice.value
            else:
                subs = node.target.slice
            t2 = self.temp_var(subs, func)
            a2 = ast.Assign([ast.Name(t2.name, ast.Store())], subs)

            self.visit(a1, func)
            self.visit(a2, func)
            self.add_constraint(
                (infer.inode(self.gx, subs), infer.inode(self.gx, t2)), func
            )

            infer.inode(self.gx, node).temp1 = t1.name
            infer.inode(self.gx, node).temp2 = t2.name
            infer.inode(self.gx, node).subs = subs

            blah = ast.Subscript(
                ast.Name(t1.name, ast.Load(), lineno=node.lineno),
                ast.Index(ast.Name(t2.name, ast.Load())),
                ast.Store(),
                lineno=node.lineno,
            )
            lnode = ast.Subscript(
                ast.Name(t1.name, ast.Load(), lineno=node.lineno),
                ast.Index(ast.Name(t2.name, ast.Load())),
                ast.Load(),
                lineno=node.lineno,
            )
        else:
            error.error("unsupported type of assignment", self.gx, node, mv=getmv())

        blah2 = ast.BinOp(lnode, node.op, node.value)
        self.gx.augment.add(blah2)

        assign = ast.Assign([blah], blah2)
        register_node(assign, func)
        infer.inode(self.gx, node).assignhop = assign
        self.visit(assign, func)

    def temp_var(
        self,
        node: Any,
        func: Optional["python.Function"] = None,
        looper: Optional[ast.AST] = None,
        wopper: Optional[ast.AST] = None,
        exc_name: bool = False,
    ) -> "python.Variable":
        """Create a temporary variable"""
        if node in self.gx.parent_nodes:
            varname = self.tempcount[self.gx.parent_nodes[node]]
        elif node in self.tempcount:  # XXX investigate why this happens
            varname = self.tempcount[node]
        else:
            varname = "__" + str(len(self.tempcount))

        var = infer.default_var(self.gx, varname, func, mv=getmv(), exc_name=exc_name)
        var.looper = looper
        var.wopper = wopper
        self.tempcount[node] = varname

        infer.register_temp_var(var, func)
        return var

    def temp_var2(
        self, node: Any, source: Any, func: Optional["python.Function"]
    ) -> "python.Variable":
        """Create a temporary variable from a source"""
        tvar = self.temp_var(node, func)
        self.add_constraint((source, infer.inode(self.gx, tvar)), func)
        return tvar

    def temp_var_int(
        self, node: Any, func: Optional["python.Function"]
    ) -> "python.Variable":
        """Create a temporary integer variable"""
        var = self.temp_var(node, func)
        self.gx.types[infer.inode(self.gx, var)] = set(
            [(python.def_class(self.gx, "int_"), 0)]
        )
        infer.inode(self.gx, var).copymetoo = True
        return var

    def visit_Raise(
        self, node: ast.Raise, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a raise statement"""
        if node.exc is None or node.cause is not None:
            error.error("unsupported raise syntax", self.gx, node, mv=getmv())
        for child in ast.iter_child_nodes(node):
            self.visit(child, func)

    def visit_Assert(
        self, node: ast.Assert, func: Optional["python.Function"] = None
    ) -> None:
        """Visit an assert statement"""
        self.visit(node.test, func)
        if node.msg:
            self.visit(node.msg, func)

    def visit_Try(
        self, node: ast.Try, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a try statement"""
        for child in node.body:
            self.visit(child, func)

        for handler in node.handlers:
            if not handler.type:
                continue

            if isinstance(handler.type, ast.Tuple):
                pairs = [(n, handler.name) for n in handler.type.elts]
            else:
                pairs = [(handler.type, handler.name)]

            for h0, h1 in pairs:
                if isinstance(h0, ast.Name) and h0.id in [
                    "int",
                    "float",
                    "str",
                    "class",
                ]:
                    continue  # handle in python.lookup_class
                cl = python.lookup_class(h0, getmv())
                if not cl:
                    if isinstance(h0, ast.Name):
                        name = "('" + h0.id + "')"
                    else:
                        name = ""
                    error.error(
                        "unknown/unsupported exception type %s" % name,
                        self.gx,
                        h0,
                        mv=getmv(),
                    )

                if isinstance(h1, str):
                    var = self.default_var(h1, func, exc_name=True)
                elif isinstance(h1, ast.Name):  # py2
                    var = self.default_var(h1.id, func, exc_name=True)
                else:
                    var = self.temp_var(h0, func, exc_name=True)

                var.invisible = True
                infer.inode(self.gx, var).copymetoo = True
                self.gx.types[infer.inode(self.gx, var)] = set([(cl, 1)])

        if node.finalbody:
            error.error("'try..finally' is not supported", self.gx, node, mv=getmv())

        for handler in node.handlers:
            for child in handler.body:
                self.visit(child, func)

        # else
        if node.orelse:
            for child in node.orelse:
                self.visit(child, func)
            self.temp_var_int(node.orelse[0], func)

    def visit_Yield(self, node: ast.Yield, func: "python.Function") -> None:
        """Visit a yield statement"""
        func.isGenerator = True
        func.yieldNodes.append(node)
        if not node.value:
            node.value = ast.Name("None", ast.Load())
        self.visit(
            ast.Return(ast.Call(ast.Name("__iter", ast.Load()), [node.value], [])),
            func,
        )
        self.add_constraint((infer.inode(self.gx, node.value), func.yieldnode), func)

    def visit_For(
        self, node: ast.For, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a for statement"""
        # --- iterable contents -> assign node
        assnode = infer.CNode(self.gx, getmv(), node.target, parent=func)
        self.gx.types[assnode] = set()

        get_iter = ast.Call(ast.Attribute(node.iter, "__iter__", ast.Load()), [], [])
        fakefunc = ast.Call(ast.Attribute(get_iter, "__next__", ast.Load()), [], [])

        self.visit(fakefunc, func)
        self.add_constraint((infer.inode(self.gx, fakefunc), assnode), func)

        # --- assign node -> variables  XXX merge into assign_pair
        if isinstance(node.target, ast.Name):
            # for x in..
            lvar = self.default_var(node.target.id, func)
            self.add_constraint((assnode, infer.inode(self.gx, lvar)), func)

        elif ast_utils.is_assign_attribute(node.target):  # XXX experimental :)
            assert isinstance(node.target, ast.Attribute)

            # for expr.x in..
            infer.CNode(self.gx, getmv(), node.target, parent=func)

            self.gx.assign_target[node.target.value] = (
                node.target.value
            )  # XXX multiple targets possible please
            fakefunc2 = ast.Call(
                ast.Attribute(node.target.value, "__setattr__", ast.Load()),
                [ast.Str(node.target.attr), fakefunc],
                [],
            )
            self.visit(fakefunc2, func)

        elif ast_utils.is_assign_list_or_tuple(node.target):
            # for (a,b, ..) in..
            self.tuple_flow(node.target, node.target, func)
        else:
            error.error("unsupported type of assignment", self.gx, node, mv=getmv())

        self.do_for(node, assnode, get_iter, func)

        # --- for-else
        if node.orelse:
            self.temp_var_int(node.orelse[0], func)
            for child in node.orelse:
                self.visit(child, func)

        # --- loop body
        self.gx.loopstack.append(node)
        for child in node.body:
            self.visit(child, func)
        self.gx.loopstack.pop()

    def do_for(
        self,
        node: Union[ast.For, ast.comprehension],
        assnode: "infer.CNode",
        get_iter: ast.Call,
        func: Optional["python.Function"],
    ) -> None:
        """Process a for statement"""
        # --- for i in range(..) XXX i should not be modified.. use tempcounter; two bounds
        if ast_utils.is_fastfor(node):
            assert isinstance(node.iter, ast.Call)

            self.temp_var2(node.target, assnode, func)
            self.temp_var2(node.iter, infer.inode(self.gx, node.iter.args[0]), func)

            if (
                len(node.iter.args) == 3
                and not isinstance(node.iter.args[2], ast.Name)
                and not ast_utils.is_literal(node.iter.args[2])
            ):  # XXX merge with ast.ListComp
                for arg in node.iter.args:
                    if not isinstance(arg, ast.Name) and not ast_utils.is_literal(
                        arg
                    ):  # XXX create func for better check
                        self.temp_var2(arg, infer.inode(self.gx, arg), func)

        # --- temp vars for list, iter etc.
        else:
            self.temp_var2(node, infer.inode(self.gx, node.iter), func)
            self.temp_var2((node, 1), infer.inode(self.gx, get_iter), func)
            self.temp_var_int(node.iter, func)

            if ast_utils.is_enumerate(node) or ast_utils.is_zip2(node):
                assert isinstance(node.iter, ast.Call)
                self.temp_var2((node, 2), infer.inode(self.gx, node.iter.args[0]), func)
                if ast_utils.is_zip2(node):
                    self.temp_var2(
                        (node, 3), infer.inode(self.gx, node.iter.args[1]), func
                    )
                    self.temp_var_int((node, 4), func)

            self.temp_var((node, 5), func, looper=node.iter)
            if isinstance(node.iter, ast.Call) and isinstance(
                node.iter.func, ast.Attribute
            ):
                self.temp_var((node, 6), func, wopper=node.iter.func.value)
                self.temp_var2(
                    (node, 7), infer.inode(self.gx, node.iter.func.value), func
                )

    def bool_test_add(self, node: ast.AST) -> None:
        """Add a boolean test to the graph"""
        if (
            isinstance(node, ast.BoolOp)
            or isinstance(node, ast.UnaryOp)
            and isinstance(node.op, ast.FloorDiv)
        ):
            self.gx.bool_test_only.add(node)

    def visit_While(
        self, node: ast.While, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a while statement"""
        self.gx.loopstack.append(node)
        self.bool_test_add(node.test)
        for child in ast.iter_child_nodes(node):
            self.visit(child, func)
        self.gx.loopstack.pop()

        if node.orelse:
            self.temp_var_int(node.orelse[0], func)
            for child in node.orelse:
                self.visit(child, func)

    def visit_Continue(
        self, node: ast.Continue, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a continue statement"""
        pass

    def visit_Break(
        self, node: ast.Break, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a break statement"""
        pass

    def visit_With(
        self, node: ast.With, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a with statement"""
        if len(node.items) > 1:
            error.error(
                "with-construct with multiple 'as' terms", self.gx, node, mv=getmv()
            )
        item = node.items[0]

        self.visit(item.context_expr, func)

        if item.optional_vars:
            if isinstance(item.optional_vars, ast.Name):
                varnode = infer.CNode(self.gx, getmv(), item.optional_vars, parent=func)
                self.gx.types[varnode] = set()
                self.add_constraint(
                    (infer.inode(self.gx, item.context_expr), varnode), func
                )
                lvar = self.default_var(item.optional_vars.id, func)
                self.add_constraint((varnode, infer.inode(self.gx, lvar)), func)
            else:
                error.error("unsupported with syntax", self.gx, item, mv=getmv())

        for child in node.body:
            self.visit(child, func)

    def visit_ListComp(
        self, node: ast.ListComp, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a list/set/dict/generator comprehension"""
        # --- [expr for iter in list for .. if cond ..]
        # --- {..}
        # --- {a: b for .. }
        # --- (expr for .. }
        lcfunc = python.Function(self.gx, getmv())
        lcfunc.listcomp = True
        lcfunc.ident = "l.c."  # XXX
        lcfunc.parent = func

        for qual in node.generators:
            # iter
            assnode = infer.CNode(self.gx, getmv(), qual.target, parent=func)
            self.gx.types[assnode] = set()

            # list.unit->iter
            get_iter = ast.Call(
                ast.Attribute(qual.iter, "__iter__", ast.Load()), [], []
            )
            fakefunc = ast.Call(ast.Attribute(get_iter, "__next__", ast.Load()), [], [])
            self.visit(fakefunc, lcfunc)
            self.add_constraint(
                (infer.inode(self.gx, fakefunc), infer.inode(self.gx, qual.target)),
                lcfunc,
            )

            if isinstance(qual.target, ast.Name):  # XXX merge with visit_For
                lvar = infer.default_var(
                    self.gx, qual.target.id, lcfunc
                )  # XXX str or ast.Name?
                self.add_constraint(
                    (infer.inode(self.gx, qual.target), infer.inode(self.gx, lvar)),
                    lcfunc,
                )
            else:  # AssTuple, AssList
                self.tuple_flow(qual.target, qual.target, lcfunc)

            self.do_for(qual, assnode, get_iter, lcfunc)

            # cond
            for child in qual.ifs:
                self.bool_test_add(child)
                self.visit(child, lcfunc)

        # node type
        if node in self.gx.genexp_to_lc.values():  # converted generator expression
            self.instance(node, python.def_class(self.gx, "__iter"), func)
        elif node in self.gx.setcomp_to_lc.values():
            self.instance(node, python.def_class(self.gx, "set"), func)
        elif node in self.gx.dictcomp_to_lc.values():
            self.instance(node, python.def_class(self.gx, "dict"), func)
        else:
            self.instance(node, python.def_class(self.gx, "list"), func)

        # expr->instance.unit
        if isinstance(node.elt, tuple):
            self.visit(node.elt[0], lcfunc)
            self.add_dynamic_constraint(node, node.elt[0], "unit", lcfunc)
            self.visit(node.elt[1], lcfunc)
            self.add_dynamic_constraint(node, node.elt[1], "value", lcfunc)
        else:
            self.visit(node.elt, lcfunc)
            self.add_dynamic_constraint(node, node.elt, "unit", lcfunc)

        lcfunc.ident = "list_comp_" + str(len(self.listcomps))
        self.listcomps.append((node, lcfunc, func))

    def visit_DictComp(
        self, node: ast.DictComp, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a dictionary comprehension"""
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        lc = ast.ListComp(
            (node.key, node.value),
            [
                ast.comprehension(qual.target, qual.iter, qual.ifs)
                for qual in node.generators
            ],
            lineno=node.lineno,
        )
        register_node(lc, func)
        self.gx.dictcomp_to_lc[node] = lc
        self.visit(lc, func)
        self.add_constraint((infer.inode(self.gx, lc), newnode), func)

    def visit_SetComp(
        self, node: ast.SetComp, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a set comprehension"""
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        lc = ast.ListComp(
            node.elt,
            [
                ast.comprehension(qual.target, qual.iter, qual.ifs)
                for qual in node.generators
            ],
            lineno=node.lineno,
        )
        register_node(lc, func)
        self.gx.setcomp_to_lc[node] = lc
        self.visit(lc, func)
        self.add_constraint((infer.inode(self.gx, lc), newnode), func)

    def visit_Return(self, node: ast.Return, func: "python.Function") -> None:
        """Visit a return statement"""
        if node.value is None:
            node.value = ast.Name("None", ast.Load())
        self.visit(node.value, func)
        func.returnexpr.append(node.value)
        if node.value is not None:  # Not naked return
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)
            self.gx.types[newnode] = set()
        if func.retnode:
            self.add_constraint((infer.inode(self.gx, node.value), func.retnode), func)

    def visit_Delete(
        self, node: ast.Delete, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a delete statement"""
        for child in node.targets:
            #            assert isinstance(child.ctx, ast.Del)
            self.visit(child, func)

    def visit_AnnAssign(
        self, node: ast.AnnAssign, func: Optional["python.Function"] = None
    ) -> None:
        """Visit an annotated assignment"""
        assign = ast.Assign([node.target], node.value)
        self.visit(assign, func)

    def visit_Assign(
        self, node: ast.Assign, func: Optional["python.Function"] = None
    ) -> None:
        """Visit an assignment"""
        # skip type annotations
        if node.value is None:
            return

        # --- rewrite for struct.unpack XXX rewrite callfunc as tuple
        if len(node.targets) == 1:
            lvalue2, rvalue2 = node.targets[0], node.value
            if (
                self.struct_unpack(rvalue2, func)
                and isinstance(rvalue2, ast.Call)  # TODO double check
                and ast_utils.is_assign_list_or_tuple(lvalue2)
                and isinstance(lvalue2, (ast.List, ast.Tuple))  # TODO double check
                and not [
                    n for n in lvalue2.elts if ast_utils.is_assign_list_or_tuple(n)
                ]
            ):
                self.visit(node.value, func)
                sinfo = self.struct_info(rvalue2.args[0], func)
                faketuple = self.struct_faketuple(sinfo)
                self.visit(ast.Assign(node.targets, faketuple), func)
                tvar = self.temp_var2(
                    rvalue2.args[1], infer.inode(self.gx, rvalue2.args[1]), func
                )
                tvar_pos = self.temp_var_int(rvalue2.args[0], func)
                self.gx.struct_unpack[node] = (sinfo, tvar.name, tvar_pos.name)
                return

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()

        # --- a,b,.. = c,(d,e),.. = .. = expr
        for target_expr in node.targets:
            pairs = ast_utils.assign_rec(target_expr, node.value)
            for lvalue, rvalue in pairs:
                # expr[expr] = expr
                if isinstance(lvalue, ast.Subscript) and not isinstance(
                    lvalue.slice, (ast.Slice, ast.Del)
                ):
                    self.assign_pair(
                        lvalue, rvalue, func
                    )  # XXX use here generally, and in tuple_flow

                # expr.attr = expr
                elif ast_utils.is_assign_attribute(lvalue):
                    self.assign_pair(lvalue, rvalue, func)

                # name = expr
                elif isinstance(lvalue, ast.Name):
                    if (rvalue, 0, 0) not in self.gx.cnode:  # XXX generalize
                        self.visit(rvalue, func)
                    self.visit(lvalue, func)
                    lvar = self.default_var(lvalue.id, func)
                    if ast_utils.is_constant(rvalue):
                        assert isinstance(rvalue, ast.Constant)
                        lvar.const_assign.append(rvalue)
                    self.add_constraint(
                        (infer.inode(self.gx, rvalue), infer.inode(self.gx, lvar)), func
                    )

                # (a,(b,c), ..) = expr
                elif ast_utils.is_assign_list_or_tuple(lvalue):
                    self.visit(rvalue, func)
                    self.tuple_flow(lvalue, rvalue, func)

                # expr[a:b] = expr # XXX bla()[1:3] = [1]
                elif isinstance(lvalue, ast.Slice):
                    assert (
                        False
                    ), "ast.Slice shouldn't appear outside ast.Subscript node"
                    self.slice(
                        lvalue,
                        lvalue.expr,
                        [lvalue.lower, lvalue.upper, None],
                        func,
                        rvalue,
                    )

                # expr[a:b:c] = expr
                elif isinstance(lvalue, ast.Subscript) and isinstance(
                    lvalue.slice, ast.Slice
                ):
                    lslice = lvalue.slice
                    self.slice(
                        lvalue,
                        lvalue.value,
                        [lslice.lower, lslice.upper, lslice.step],
                        func,
                        rvalue,
                    )

        # temp vars
        if len(node.targets) > 1 or isinstance(node.value, ast.Tuple):
            if isinstance(node.value, ast.Tuple):
                if [n for n in node.targets if ast_utils.is_assign_tuple(n)]:
                    for child in node.value.elts:
                        if (
                            child,
                            0,
                            0,
                        ) not in self.gx.cnode:  # (a,b) = (1,2): (1,2) never visited
                            continue
                        if not ast_utils.is_constant(child) and not ast_utils.is_none(
                            child
                        ):
                            self.temp_var2(child, infer.inode(self.gx, child), func)
            elif not ast_utils.is_constant(node.value) and not ast_utils.is_none(
                node.value
            ):
                self.temp_var2(node.value, infer.inode(self.gx, node.value), func)

    def assign_pair(
        self, lvalue: ast.AST, rvalue: ast.AST, func: Optional["python.Function"]
    ) -> None:
        """Assign a pair of values"""
        # expr[expr] = expr
        if isinstance(lvalue, ast.Subscript) and not isinstance(
            lvalue.slice, (ast.Slice, ast.Del)
        ):
            if isinstance(lvalue.slice, ast.Index):
                assert False
            #                subscript = lvalue.slice.value
            else:
                subscript = lvalue.slice

            fakefunc = ast.Call(
                ast.Attribute(lvalue.value, "__setitem__", ast.Load()),
                [subscript, rvalue],
                [],
            )
            self.visit(fakefunc, func)
            infer.inode(self.gx, lvalue.value).fakefunc = fakefunc

            if not isinstance(lvalue.value, ast.Name):
                self.temp_var2(lvalue.value, infer.inode(self.gx, lvalue.value), func)

        # expr.attr = expr
        elif ast_utils.is_assign_attribute(lvalue):
            assert isinstance(lvalue, ast.Attribute)
            infer.CNode(self.gx, getmv(), lvalue, parent=func)
            self.gx.assign_target[rvalue] = lvalue.value
            fakefunc = ast.Call(
                ast.Attribute(lvalue.value, "__setattr__", ast.Load()),
                [ast.Str(lvalue.attr), rvalue],
                [],
            )
            self.visit(fakefunc, func)

    def default_var(
        self, name: str, func: Optional["python.Function"], exc_name: bool = False
    ) -> "python.Variable":
        """Get the default variable for a name"""
        if isinstance(func, python.Function) and name in func.globals:
            return infer.default_var(self.gx, name, None, mv=getmv(), exc_name=exc_name)
        else:
            return infer.default_var(self.gx, name, func, mv=getmv(), exc_name=exc_name)

    def tuple_flow(
        self, lvalue: ast.AST, rvalue: ast.AST, func: Optional["python.Function"] = None
    ) -> None:
        """Handle tuple flow"""
        self.temp_var2(lvalue, infer.inode(self.gx, rvalue), func)

        lvalues: List[ast.expr]
        if isinstance(lvalue, tuple):
            assert False
        elif ast_utils.is_assign_list_or_tuple(lvalue):
            assert isinstance(lvalue, (ast.Tuple, ast.List))
            lvalues = lvalue.elts

        for i, item in enumerate(lvalues):
            fakenode = infer.CNode(
                self.gx, getmv(), (item,), parent=func
            )  # fake node per item, for multiple callfunc triggers
            self.gx.types[fakenode] = set()
            self.add_constraint((infer.inode(self.gx, rvalue), fakenode), func)

            fakefunc = ast.Call(
                ast.Attribute(rvalue, "__getunit__", ast.Load()), [ast.Num(i)], []
            )

            fakenode.callfuncs.append(fakefunc)
            self.visit_Call(fakefunc, func, fake_attr=True)

            self.gx.item_rvalue[item] = rvalue
            if isinstance(item, ast.Name):
                lvar = self.default_var(item.id, func)
                self.add_constraint(
                    (infer.inode(self.gx, fakefunc), infer.inode(self.gx, lvar)), func
                )
            elif isinstance(item, ast.Subscript) or ast_utils.is_assign_attribute(item):
                self.assign_pair(item, fakefunc, func)
            elif ast_utils.is_assign_list_or_tuple(item):  # recursion
                self.tuple_flow(item, fakefunc, func)
            else:
                error.error("unsupported type of assignment", self.gx, item, mv=getmv())

    def super_call(self, orig: ast.Call) -> Optional[ast.AST]:
        """Handle a super call"""
        node = orig.func
        assert isinstance(node, ast.Attribute)
        if (
            isinstance(node.value, ast.Call)
            and node.attr not in ("__getattr__", "__setattr__")
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "super"
        ):
            if (
                len(node.value.args) >= 2
                and isinstance(node.value.args[1], ast.Name)
                and node.value.args[1].id == "self"
            ):
                cl = python.lookup_class(node.value.args[0], getmv())
                assert cl
                if cl.node.bases:
                    return cl.node.bases[0]
            error.error("unsupported usage of 'super'", self.gx, orig, mv=getmv())

        return None

    def visit_Pass(
        self, node: ast.Pass, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a pass statement"""
        pass

    def visit_Call(
        self,
        node: ast.Call,
        func: Optional["python.Function"] = None,
        fake_attr: bool = False,
    ) -> None:
        """Visit a call statement"""
        # XXX clean up!!
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()

        # XXX import math; math.e
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.ctx, ast.Load):
            # rewrite super(..) call
            base = self.super_call(node)
            if base:
                node.func = ast.Attribute(
                    copy.deepcopy(base), node.func.attr, ast.Load()
                )
                node.args.insert(0, ast.Name("self", ast.Load()))

            # method call
            if not fake_attr:
                self.visit_Attribute(node.func, func, callfunc=True)
                infer.inode(self.gx, node.func).callfuncs.append(
                    node
                )  # XXX iterative dataflow analysis: move there?

            ident = node.func.attr
            infer.inode(self.gx, node.func.value).callfuncs.append(
                node
            )  # XXX iterative dataflow analysis: move there?

            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id in getmv().imports
                and node.func.attr == "__getattr__"
            ):  # XXX analyze_callfunc
                assert isinstance(node.args[0], ast.Str)
                if (
                    node.args[0].s in getmv().imports[node.func.value.id].mv.globals
                ):  # XXX bleh
                    self.add_constraint(
                        (
                            infer.inode(
                                self.gx,
                                getmv()
                                .imports[node.func.value.id]
                                .mv.globals[node.args[0].s],
                            ),
                            newnode,
                        ),
                        func,
                    )

        elif isinstance(node.func, ast.Name):
            # direct call
            ident = node.func.id
            if ident == "print":
                ident = node.func.id = "__print"  # XXX

            if ident == "open" and len(node.args) > 1:
                if isinstance(node.args[1], ast.Str):
                    if "b" in node.args[1].s:
                        ident = node.func.id = "open_binary"

                else:
                    error.error(
                        "non-constant mode passed to 'open'",
                        self.gx,
                        node.func,
                        mv=getmv(),
                    )

            if ident in ["hasattr", "getattr", "setattr", "slice", "type", "Ellipsis"]:
                error.error(
                    "'%s' function is not supported" % ident,
                    self.gx,
                    node.func,
                    mv=getmv(),
                )
            if ident == "dict" and node.keywords:
                error.error(
                    "unsupported method of initializing dictionaries",
                    self.gx,
                    node,
                    mv=getmv(),
                )
            if ident == "isinstance":
                error.error(
                    "'isinstance' is not supported; always returns True",
                    self.gx,
                    node,
                    mv=getmv(),
                    warning=True,
                )

            if python.lookup_var(ident, func, getmv()):
                self.visit(node.func, func)
                infer.inode(self.gx, node.func).callfuncs.append(
                    node
                )  # XXX iterative dataflow analysis: move there
        else:
            self.visit(node.func, func)
            infer.inode(self.gx, node.func).callfuncs.append(
                node
            )  # XXX iterative dataflow analysis: move there

        # --- arguments
        if not getmv().module.builtin and has_star_kwarg(node):
            error.error(
                "argument (un)packing is not supported", self.gx, node, mv=getmv()
            )

        for arg in get_arg_nodes(node):
            self.visit(arg, func)
            infer.inode(self.gx, arg).callfuncs.append(node)  # this one too

        # --- handle instantiation or call
        constructor = python.lookup_class(node.func, getmv())
        if constructor and (
            not isinstance(node.func, ast.Name)
            or not python.lookup_var(node.func.id, func, getmv())
        ):
            self.instance(node, constructor, func)
            infer.inode(self.gx, node).callfuncs.append(
                node
            )  # XXX see above, investigate

    def visit_ClassDef(
        self, node: ast.ClassDef, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a class definition"""
        if not getmv().module.builtin and node not in getmv().classnodes:
            error.error("non-global class '%s'" % node.name, self.gx, node, mv=getmv())
        if len(node.bases) > 1:
            error.error(
                "multiple inheritance is not supported", self.gx, node, mv=getmv()
            )

        if not getmv().module.builtin:
            for base in node.bases:
                if isinstance(base, ast.Name):
                    name = base.id
                elif isinstance(base, ast.Attribute):
                    name = base.attr
                else:
                    error.error(
                        "invalid expression for base class", self.gx, node, mv=getmv()
                    )

                cl = python.lookup_class(base, getmv())
                if not cl:
                    error.error("no such class: '%s'" % name, self.gx, node, mv=getmv())

                elif cl.mv.module.builtin and name not in [
                    "object",
                    "Exception",
                    "tzinfo",
                ]:
                    if python.def_class(self.gx, "Exception") not in cl.ancestors():
                        error.error(
                            "inheritance from builtin class '%s' is not supported"
                            % name,
                            self.gx,
                            node,
                            mv=getmv(),
                        )

        if node.name in getmv().classes:
            newclass = getmv().classes[
                node.name
            ]  # set in visit_Module, for forward references
        else:
            check_redef(self.gx, node)  # XXX merge with visit_Module
            newclass = python.Class(self.gx, node, getmv(), self.module)
            self.classes[node.name] = newclass
            getmv().classes[node.name] = newclass
            return

        # --- built-in functions
        for ident in ["__setattr__", "__getattr__"]:
            func = python.Function(self.gx, getmv())
            func.ident = ident
            func.parent = newclass

            if ident == "__setattr__":
                func.formals = ["name", "whatsit"]
                retexpr = ast.Return(value=None)
                self.visit(retexpr, func)
            elif ident == "__getattr__":
                func.formals = ["name"]

            assert newclass
            newclass.funcs[ident] = func

        newstaticclass = newclass.parent  # TODO copy-paste of above for mypy --strict
        for ident in ["__setattr__", "__getattr__"]:
            func = python.Function(self.gx, getmv())
            func.ident = ident
            func.parent = newstaticclass

            if ident == "__setattr__":
                func.formals = ["name", "whatsit"]
                retexpr = ast.Return(value=None)
                self.visit(retexpr, func)
            elif ident == "__getattr__":
                func.formals = ["name"]

            assert newstaticclass
            newstaticclass.funcs[ident] = func

        # --- built-in attributes
        if "class_" in getmv().classes or "class_" in getmv().ext_classes:
            var = infer.default_var(self.gx, "__class__", newclass)
            var.invisible = True
            self.gx.types[infer.inode(self.gx, var)] = set(
                [
                    (
                        python.def_class(self.gx, "class_"),
                        python.def_class(self.gx, "class_").dcpa,
                    )
                ]
            )
            python.def_class(self.gx, "class_").dcpa += 1

        # --- staticmethod, property
        skip = []
        for child in node.body:
            if isinstance(child, ast.Assign) and len(child.targets) == 1:
                lvalue, rvalue = child.targets[0], child.value
                if (
                    isinstance(lvalue, ast.Name)
                    and isinstance(rvalue, ast.Call)
                    and isinstance(rvalue.func, ast.Name)
                    and rvalue.func.id in ["staticmethod", "property"]
                ):
                    if rvalue.func.id == "property":
                        if len(rvalue.args) == 1 and isinstance(
                            rvalue.args[0], ast.Name
                        ):
                            newclass.properties[lvalue.id] = [rvalue.args[0].id, ""]
                        elif (
                            len(rvalue.args) == 2
                            and isinstance(rvalue.args[0], ast.Name)
                            and isinstance(rvalue.args[1], ast.Name)
                        ):
                            newclass.properties[lvalue.id] = [
                                rvalue.args[0].id,
                                rvalue.args[1].id,
                            ]
                        else:
                            error.error(
                                "complex properties are not supported",
                                self.gx,
                                rvalue,
                                mv=getmv(),
                            )
                    else:
                        newclass.staticmethods.append(lvalue.id)
                    skip.append(child)

        # --- children
        for child in node.body:
            if child not in skip:
                cl = self.classes[node.name]
                if isinstance(child, ast.FunctionDef):
                    self.visit(child, cl)
                else:
                    cl.parent.static_nodes.append(child)
                    self.visit(child, cl.parent)

        # --- __iadd__ etc.
        if not newclass.mv.module.builtin or newclass.ident in [
            "int_",
            "float_",
            "str_",
            "tuple",
            "complex",
        ]:
            msgs = ["add", "mul"]  # XXX mod, pow
            if newclass.ident in ["int_", "float_"]:
                msgs += ["sub", "truediv", "floordiv"]
            if newclass.ident in ["int_"]:
                msgs += ["lshift", "rshift", "and", "xor", "or"]
            for msg in msgs:
                if "__i" + msg + "__" not in newclass.funcs:
                    self.visit(
                        ast.parse(
                            "def __i%s__(self, other): return self.__%s__(other)"
                            % (msg, msg)
                        ).body[0],
                        newclass,
                    )

        # --- __str__, __hash__ # XXX model in lib/builtin.py, other defaults?
        if not newclass.mv.module.builtin and "__str__" not in newclass.funcs:
            self.visit(
                ast.FunctionDef(
                    "__str__",
                    make_arg_list(["self"]),
                    [
                        ast.Return(
                            ast.Call(
                                ast.Attribute(
                                    ast.Name("self", ast.Load()), "__repr__", ast.Load()
                                ),
                                [],
                                [],
                            )
                        )
                    ],
                    [],
                ),
                newclass,
            )
            newclass.funcs["__str__"].invisible = True
        if not newclass.mv.module.builtin and "__hash__" not in newclass.funcs:
            self.visit(
                ast.FunctionDef(
                    "__hash__",
                    make_arg_list(["self"]),
                    [ast.Return(ast.Num(0))],
                    [],
                ),
                newclass,
            )
            newclass.funcs["__hash__"].invisible = True

    def visit_Attribute(
        self,
        node: ast.Attribute,
        func: Optional["python.Function"] = None,
        callfunc: bool = False,
    ) -> None:
        """Visit an attribute"""
        if isinstance(node.ctx, ast.Load):
            if node.attr in ["__doc__"]:
                error.error(
                    "%s attribute is not supported" % node.attr,
                    self.gx,
                    node,
                    mv=getmv(),
                )

            newnode = infer.CNode(self.gx, getmv(), node, parent=func)
            self.gx.types[newnode] = set()

            fakefunc = ast.Call(
                ast.Attribute(node.value, "__getattr__", ast.Load()),
                [ast.Str(node.attr)],
                [],
            )
            self.visit(node.value, func)
            self.visit_Call(fakefunc, func, fake_attr=True)
            self.add_constraint((self.gx.cnode[fakefunc, 0, 0], newnode), func)

            if not callfunc:
                self.fncl_passing(node, newnode, func)
        elif isinstance(node.ctx, ast.Del):
            error.error(
                "unsupported attribute delete",
                self.gx,
                node,
                mv=getmv(),
                warning=True,
            )
        else:
            error.error(
                "unsupported attribute ctx",
                self.gx,
                node,
                mv=getmv(),
            )

    def visit_Constant(
        self, node: ast.Constant, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a constant"""
        if node.value.__class__.__name__ == "ellipsis":
            error.error("ellipsis is not supported", self.gx, node, mv=getmv())
        else:
            map = {
                int: "int_",
                float: "float_",
                complex: "complex",
                str: "str_",
                bool: "bool_",
                type(None): "none",
                bytes: "bytes_",
            }
            self.instance(node, python.def_class(self.gx, map[type(node.value)]), func)

    def fncl_passing(
        self, node: ast.AST, newnode: infer.CNode, func: Optional["python.Function"]
    ) -> bool:
        """Handle function or class lookup for assignment"""
        lfunc = python.lookup_func(node, getmv())
        lclass = python.lookup_class(node, getmv())
        if lfunc:
            if lfunc.mv.module.builtin:
                lfunc = self.builtin_wrapper(node, func)
            elif lfunc.ident not in lfunc.mv.lambdas:
                lfunc.lambdanr = len(lfunc.mv.lambdas)
                lfunc.mv.lambdas[lfunc.ident] = lfunc
            self.gx.types[newnode] = set([(lfunc, 0)])
        elif lclass:
            lclass2: Union["python.Function", "python.StaticClass"]
            if lclass.mv.module.builtin:
                lclass2 = self.builtin_wrapper(node, func)
            else:
                lclass2 = lclass.parent
            self.gx.types[newnode] = set([(lclass2, 0)])
        else:
            return False
        newnode.copymetoo = True  # XXX merge into some kind of 'seeding' function
        return True

    def visit_Name(
        self, node: ast.Name, func: Optional["python.Function"] = None
    ) -> None:
        """Visit a name"""
        if isinstance(node.ctx, ast.Load):
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)
            self.gx.types[newnode] = set()

            if node.id == "__doc__":
                error.error(
                    "'%s' attribute is not supported" % node.id,
                    self.gx,
                    node,
                    mv=getmv(),
                )

            if node.id in ["None", "True", "False"]:
                if node.id == "None":  # XXX also bools, remove def seed_nodes()
                    self.instance(node, python.def_class(self.gx, "none"), func)
                else:
                    self.instance(node, python.def_class(self.gx, "bool_"), func)
                return

            var: Optional["python.Variable"]

            if isinstance(func, python.Function) and node.id in func.globals:
                var = infer.default_var(self.gx, node.id, None, mv=getmv())
            else:
                var = python.lookup_var(node.id, func, getmv())
                if not var:
                    if self.fncl_passing(node, newnode, func):
                        pass
                    elif node.id in ["int", "float", "str"]:  # XXX
                        cl = self.ext_classes[node.id + "_"]
                        self.gx.types[newnode] = set([(cl.parent, 0)])
                        newnode.copymetoo = True
                    else:
                        var = infer.default_var(self.gx, node.id, None, mv=getmv())
            if var:
                self.add_constraint((infer.inode(self.gx, var), newnode), func)

        elif isinstance(node.ctx, ast.Store):
            # Adding vars for ast.Name store are handled elsewhere
            pass
        elif isinstance(node.ctx, ast.Del):
            # Do nothing
            pass
        else:
            error.error(
                "unknown ctx type for ast.Name, %s" % node.ctx,
                self.gx,
                node,
                mv=getmv(),
            )

    def builtin_wrapper(
        self, node: ast.AST, func: Optional["python.Function"]
    ) -> "python.Function":
        """Create a wrapper for a builtin function"""
        node2 = ast.Call(
            copy.deepcopy(node), [ast.Name(x, ast.Load()) for x in "abcde"], []
        )
        lam = ast.Lambda(make_arg_list(list("abcde")), node2)
        self.visit(lam, func)
        self.lwrapper[node] = self.lambdaname[lam]
        self.gx.lambdawrapper[node2] = self.lambdaname[lam]
        f = self.lambdas[self.lambdaname[lam]]
        f.lambdawrapper = True
        infer.inode(self.gx, node2).lambdawrapper = f
        return f


def parse_module(
    name: str,
    gx: "config.GlobalInfo",
    parent: Optional["python.Module"] = None,
    node: Optional[ast.AST] = None,
) -> "python.Module":
    """Parse a module"""
    # --- valid name?
    if not re.match("^[a-zA-Z0-9_.]+$", name):
        print(
            "*ERROR*:%s.py: module names should consist of letters, digits and underscores"
            % name
        )
        sys.exit(1)

    # --- create module
    try:
        cwd = pathlib.Path(os.getcwd())
        if parent and parent.path != cwd:
            basepaths = [parent.path, cwd]
        else:
            basepaths = [cwd]
        module_paths = [str(p) for p in basepaths] + gx.libdirs
        absolute_name, filename, relative_filename, builtin = python.find_module(
            gx, name, module_paths
        )
    except ImportError:
        error.error("cannot locate module: " + name, gx, node, mv=getmv())

    # --- check cache
    if absolute_name in gx.modules:
        return gx.modules[absolute_name]

    # --- not cached, so parse
    ast = python.parse_file(pathlib.Path(filename))

    module = python.Module(
        absolute_name, filename, relative_filename, builtin, node, ast
    )

    gx.modules[absolute_name] = module

    # --- visit ast
    try:
        old_mv = getmv()
    except NameError:
        pass
    module.mv = mv = ModuleVisitor(module, gx)
    setmv(mv)

    mv.visit(module.ast)
    module.import_order = gx.import_order
    gx.import_order += 1

    try:
        mv = old_mv
        setmv(mv)
    except NameError:
        pass

    return module
