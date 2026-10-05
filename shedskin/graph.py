# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
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
import _string  # type: ignore[import-not-found]
from typing import TYPE_CHECKING, Any, NoReturn, Optional, TypeAlias, Union

from . import ast_utils, error, infer, python

if TYPE_CHECKING:
    from . import config

Parent: TypeAlias = Union["python.Class", "python.Function"]
AllParent: TypeAlias = Union["python.Class", "python.Function", "python.StaticClass"]


def _as_expr(node: ast.AST) -> ast.expr:
    """Narrow AST nodes to expression nodes."""
    assert isinstance(node, ast.expr)
    return node


def _const_str(node: ast.AST) -> str:
    """Return string value from a constant node."""
    assert isinstance(node, ast.Constant)
    assert isinstance(node.value, str)
    return node.value


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



# --- rewrite literal str.format(..) calls into f-strings
class StrFormatRewriter(ast.NodeTransformer):
    """Replace each '<literal>.format(..)' call with a StrFormat node

    The format string is parsed at compile-time into an equivalent f-string
    (ast.JoinedStr), which refers to the call arguments via StrFormatArg
    nodes. Anything that CPython would reject for the given arguments
    (bad index, missing keyword, bad conversion..) becomes a compile-time
    error. Format specs are passed on as f-string format specs (including
    nested replacement fields), so they are handled in the same way.
    """

    def __init__(self, gx: "config.GlobalInfo", mv: "ModuleVisitor"):
        self.gx = gx
        self.mv = mv

    def fail(self, node: ast.AST, msg: str) -> NoReturn:
        error.error("str.format: " + msg, self.gx, node, mv=self.mv)
        assert False

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        # (literal str.format calls don't get here, see visit_Call)
        if node.attr == "format" and ast_utils.is_str(node.value):
            self.fail(node, "only direct calls are supported")
        self.generic_visit(node)
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # '<literal>.format(..)' or 'str.format(<literal>, ..)'
        fmt: Optional[str] = None
        if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
            if ast_utils.is_str(node.func.value):
                fmt = _const_str(node.func.value)
            elif (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "str"
            ):
                if not node.args or not ast_utils.is_str(node.args[0]):
                    self.fail(node, "only supported for literal format strings")
                fmt = _const_str(node.args[0])
                node.args = node.args[1:]

        if fmt is None:
            self.generic_visit(node)
            return node

        # nested rewrites (keyword values are replaced in-place)
        node.args = [self.visit(arg) for arg in node.args]
        for kw in node.keywords:
            self.visit(kw)

        def fail(msg: str) -> NoReturn:
            self.fail(node, msg)

        for arg in node.args:
            if isinstance(arg, ast.Starred):
                fail("'*' arguments are not supported")
        kwpos: dict[str, int] = {}
        for i, kw in enumerate(node.keywords):
            if kw.arg is None:
                fail("'**' arguments are not supported")
            kwpos[kw.arg] = len(node.args) + i
        npos = len(node.args)
        args = list(node.args) + [kw.value for kw in node.keywords]

        auto_index = 0
        numbering: Optional[str] = None  # 'automatic' or 'manual'

        def build(fmt: str, depth: int) -> list[ast.expr]:
            nonlocal auto_index, numbering
            try:
                parsed = list(string.Formatter().parse(fmt))
            except ValueError as e:
                fail(str(e))

            values: list[ast.expr] = []
            for literal, field_name, format_spec, conversion in parsed:
                if literal:
                    if values and ast_utils.is_str(values[-1]):
                        values[-1] = ast.Constant(_const_str(values[-1]) + literal)
                    else:
                        values.append(ast.Constant(literal))
                if field_name is None:
                    continue
                if depth > 1:
                    fail("Max string recursion exceeded")

                try:
                    first, rest_iter = _string.formatter_field_name_split(
                        field_name
                    )
                    rest = list(rest_iter)
                except ValueError as e:
                    fail(str(e))

                # positional (automatic or manual numbering) or keyword argument
                if isinstance(first, int) or first == "":
                    if first == "":
                        if numbering == "manual":
                            fail(
                                "cannot switch from manual field specification "
                                "to automatic field numbering"
                            )
                        numbering = "automatic"
                        first = auto_index
                        auto_index += 1
                    else:
                        if numbering == "automatic":
                            fail(
                                "cannot switch from automatic field numbering "
                                "to manual field specification"
                            )
                        numbering = "manual"
                    assert isinstance(first, int)
                    if first >= npos:
                        fail(
                            "Replacement index %d out of range for positional "
                            "args tuple" % first
                        )
                    index = first
                else:
                    if first not in kwpos:
                        fail("no keyword argument '%s'" % first)
                    index = kwpos[first]
                expr: ast.expr = ast_utils.StrFormatArg(index)

                # attribute access/indexing, e.g. '{0.x[1]}'
                for is_attr, key in rest:
                    if is_attr:
                        expr = ast.Attribute(expr, key, ast.Load())
                    else:
                        expr = ast.Subscript(expr, ast.Constant(key), ast.Load())

                # conversion
                if conversion is None:
                    conv = -1
                elif conversion in ("s", "r", "a"):
                    conv = ord(conversion)
                else:
                    fail("Unknown conversion specifier %s" % conversion)

                # format spec, possibly containing nested replacement fields
                spec: Optional[ast.expr] = None
                if format_spec:
                    spec = ast.JoinedStr(build(format_spec, depth + 1))

                values.append(ast.FormattedValue(expr, conv, spec))
            return values

        joined = ast.JoinedStr(build(fmt, 0))
        newnode = ast_utils.StrFormat(args, joined)
        ast.copy_location(newnode, node)
        # synthesized nodes get the location of the call
        for child in ast.walk(joined):
            if "lineno" in child._attributes:
                ast.copy_location(child, node)
        return newnode


def register_node(node: ast.AST, func: Optional[AllParent]) -> None:
    """Register a node with a function"""
    if isinstance(func, python.Function):
        func.registered.append(node)


def slice_nums(nodes: list[Optional[ast.AST]]) -> list[ast.AST]:
    """Slice numbers from a list of nodes"""
    nodes2: list[ast.AST] = []
    x = 0
    for i, n in enumerate(nodes):
        if not n or ast_utils.is_none(n):
            nodes2.append(ast.Constant(0))
        else:
            nodes2.append(n)
            x |= 1 << i
    nodes2.insert(0, ast.Constant(x))
    return nodes2


def get_arg_nodes(node: ast.Call) -> list[ast.expr]:
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


def make_arg_list(argnames: list[str]) -> ast.arguments:
    """Make a simple argument list from a list of argument names"""
    args = [ast.arg(a) for a in argnames]
    return ast.arguments([], args, None, [], [], None, [])


def is_property_setter(dec: ast.AST, parent: Optional["python.Class"] = None) -> bool:
    """Check if a decorator is a property setter.

    Structurally, any '@X.setter'-shaped decorator matches this shape.
    When 'parent' (the enclosing class) is given, we additionally verify
    that 'X' was actually registered as a real '@property' earlier in
    that same class -- otherwise an unrelated '@obj.setter' decorator
    (where 'obj' just happens to have its own, unrelated 'setter' method)
    gets misidentified as a property setter, leading to a KeyError later
    when the (non-existent) property entry is looked up.

    'parent' is omitted at the point (forward_references) where methods
    get provisionally renamed to avoid setter/getter name clashes, since
    properties haven't been registered yet at that stage; it is required
    at the point (visit_FunctionDef) where the setter is actually wired
    up to its property.
    """
    if not (
        isinstance(dec, ast.Attribute)
        and isinstance(dec.value, ast.Name)
        and dec.attr == "setter"
    ):
        return False
    if parent is not None:
        return dec.value.id in parent.properties
    return True


class VisitContext:
    def __init__(
        self,
        namespace: Union[AllParent, "python.Module"],
        parent: Optional["VisitContext"] = None,
    ):
        self.namespace = namespace
        self.parent = parent
        self.live_local_writes: dict[str, set["infer.CNode"]] = {}
        self.contained_local_writes: Optional[dict[str, "infer.CNode"]] = None
        self.all_local_writes: dict[str, set["infer.CNode"]] = {}
        self.incoming_definition: dict[str, "infer.CNode"] = {}
        self.conditional_writes: set[str] = set()

    def child(self) -> "VisitContext":
        return VisitContext(self.namespace, self)

    def child_with_class(
        self, class_: Union["python.Class", "python.StaticClass"]
    ) -> "VisitContext":
        return VisitContext(class_, self)

    def as_except_context(self) -> "VisitContext":
        context = VisitContext(self.namespace, self.parent)
        context.live_local_writes = {
            name: values.copy() for name, values in self.all_local_writes.items()
        }
        context.incoming_definition = self.incoming_definition.copy()
        context.conditional_writes = set(context.live_local_writes)
        return context

    def class_object(self) -> Optional["python.Class"]:
        namespace = self.namespace
        if isinstance(namespace, python.Class):
            return namespace
        return None

    def function(self) -> Optional["python.Function"]:
        namespace = self.namespace
        if isinstance(namespace, python.Function):
            return namespace
        return None

    def parent_object(self) -> Optional[AllParent]:
        namespace = self.namespace
        if isinstance(namespace, (python.Function, python.Class, python.StaticClass)):
            return namespace
        return None

    def contained_write(self, node: ast.Name, cnode: "infer.CNode") -> None:
        assert node.id not in self.all_local_writes
        assert node.id not in self.live_local_writes
        if self.contained_local_writes is None:
            self.contained_local_writes = {}
        else:
            # assert node.id not in self.contained_local_writes
            # this is apparently ok for comprehensions [i for i in range(2) for i in range(5,7)] => [5, 6, 5, 6]
            pass
        self.contained_local_writes[node.id] = cnode

    def write(self, node: ast.Name, cnode: "infer.CNode") -> None:
        all_writes = self.all_local_writes.setdefault(node.id, set())
        all_writes.add(cnode)
        defs = self.live_local_writes.setdefault(node.id, set())
        defs.clear()
        defs.add(cnode)
        if node.id in self.conditional_writes:
            self.conditional_writes.remove(node.id)

    def read(self, mv: "ModuleVisitor", node: ast.Name) -> "infer.CNode":
        name: str = node.id
        assert isinstance(node.ctx, ast.Load)
        func: AllParent | None = self.parent_object()
        cnode = mv.gx.cnode.get((node, 0, 0))
        if cnode is None:
            cnode = infer.CNode(
                mv.gx, mv, node, parent=func
            )  # XXX: Should parent be self.parent_object()
            mv.gx.types[cnode] = set()
        self.namespace.variable_reads.setdefault(name, set()).add(cnode)
        defs = self.live_local_writes.get(name)
        if defs:
            for c in defs:
                mv.add_constraint((c, cnode), func)
            return cnode
        if self.contained_local_writes:
            contained_def = self.contained_local_writes.get(name)
            if contained_def:
                mv.add_constraint((contained_def, cnode), func)
                return cnode
        incoming_def = self.incoming_definition.get(name)
        if incoming_def is not None:
            mv.add_constraint((incoming_def, cnode), func)
            return cnode
        if self.parent:
            parent_cnode = self.parent.read(mv, node)
            if parent_cnode != cnode:
                mv.add_constraint((parent_cnode, cnode), func)
            self.incoming_definition[name] = cnode
        elif isinstance(func, python.Function):
            func_parent = (
                func.parent
                if isinstance(func.parent, python.Function)
                else None
            )
            var = python.lookup_var(node.id, func_parent, mv) or infer.default_var(
                mv.gx, name, None, mv=mv
            )
            mv.add_constraint((infer.inode(mv.gx, var), cnode), func)
            self.incoming_definition[name] = cnode
        else:
            var = python.lookup_var(node.id, func, mv) or infer.default_var(
                mv.gx, name, None, mv=mv
            )
            mv.add_constraint((infer.inode(mv.gx, var), cnode), func)
            self.incoming_definition[name] = cnode
        return cnode

    def feedback_loop_writes(
        self, mv: "ModuleVisitor", loop_context: "VisitContext"
    ) -> None:
        for name, outgoing_cnodes in loop_context.live_local_writes.items():
            incoming_cnode = self.incoming_definition.get(name)
            if incoming_cnode is None:  # variable is not read before write
                continue
            for outgoing_cnode in outgoing_cnodes:
                mv.add_constraint((outgoing_cnode, incoming_cnode), self.parent_object())

    def merge_loop(self, mv: "ModuleVisitor", loop_context: "VisitContext") -> None:
        self.feedback_loop_writes(mv, loop_context)
        self.merge([loop_context], True)

    def merge_loop_orelse(
        self,
        mv: "ModuleVisitor",
        loop_context: "VisitContext",
        orelse_context: "VisitContext",
    ) -> None:
        self.feedback_loop_writes(mv, loop_context)
        self.merge([loop_context, orelse_context], False)

    def merge(
        self, children: list["VisitContext"], all_conditional: bool = True
    ) -> None:
        conditional: set[str] = set()
        all_outgoing_cnodes: dict[str, set["infer.CNode"]] = {}
        for c in children:
            assert c.parent == self
            conditional.update(c.conditional_writes)
            for name, outgoing_cnodes in c.all_local_writes.items():
                assert outgoing_cnodes
                self.all_local_writes.setdefault(name, set()).update(outgoing_cnodes)
            for name, outgoing_cnodes in c.live_local_writes.items():
                assert outgoing_cnodes
                all_outgoing_cnodes.setdefault(name, set()).update(outgoing_cnodes)
        if all_conditional:
            conditional.update(set(all_outgoing_cnodes))
        else:
            conditional.update(
                {
                    n
                    for n in all_outgoing_cnodes
                    if n not in conditional
                    and not all(n in c.live_local_writes for c in children)
                }
            )
        self.conditional_writes.update(conditional - set(self.live_local_writes))
        if not all_conditional and len(all_outgoing_cnodes) > len(conditional):
            self.conditional_writes.difference_update(
                set(all_outgoing_cnodes) - conditional
            )
        for name, outgoing_cnodes in all_outgoing_cnodes.items():
            local_writes = self.live_local_writes.setdefault(name, set())
            if name not in conditional:
                local_writes.clear()
            local_writes.update(outgoing_cnodes)


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
        self.current_with_vars: list[list[str]] = []

        self.lambdas: dict[str, "python.Function"] = {}
        self.imports: dict[str, "python.Module"] = {}
        self.fake_imports: dict[str, "python.Module"] = {}
        self.ext_classes: dict[str, "python.Class"] = {}
        self.ext_funcs: dict[str, "python.Function"] = {}
        self.lambdaname: dict[ast.AST, str] = {}
        self.lwrapper: dict[ast.AST, str] = {}
        self.tempcount = self.gx.tempcount
        self.str_format_node: Optional[ast_utils.StrFormat] = None
        self.listcomps: list[
            tuple[ast.ListComp, "python.Function", Optional[AllParent]]
        ] = []
        self.defaults: dict[ast.AST, tuple[int, "python.Function", int]] = {}

        self.importnodes: list[ast.AST] = []
        self.funcnodes: list[ast.FunctionDef]
        self.classnodes: list[ast.ClassDef]

    def visit(self, node: ast.AST, context: VisitContext, *args: Any) -> None:
        """Visit a node"""
        if (node, 0, 0) not in self.gx.cnode:
            ast_utils.BaseNodeVisitor.visit(self, node, context, *args)

    def fake_func(
        self,
        node: Any,
        objexpr: ast.AST,
        attrname: str,
        args: list[ast.AST],
        context: VisitContext,
    ) -> ast.Call:
        """Generate a fake function"""
        func: Optional[AllParent] = context.parent_object()

        if (node, 0, 0) in self.gx.cnode:  # XXX
            newnode = self.gx.cnode[node, 0, 0]
        else:
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)
            self.gx.types[newnode] = set()

        objexpr = _as_expr(objexpr)
        args_expr = [_as_expr(arg) for arg in args]
        fakefunc = ast.Call(ast.Attribute(objexpr, attrname, ast.Load()), args_expr, [])
        if hasattr(objexpr, "lineno"):
            fakefunc.lineno = objexpr.lineno
        self.visit_Call(fakefunc, context)
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
            if func_id == "range":
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
        elif isinstance(child, ast.Constant):
            child = type(child.value)
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
        func: Optional[AllParent] = None,
    ) -> None:
        """Generate an instance of a class"""
        if (node, 0, 0) in self.gx.cnode:  # XXX to create_node() func
            newnode = self.gx.cnode[node, 0, 0]
        else:
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)

        newnode.constructor = True

        if cl.ident in ["int_", "float_", "str_", "bytes_", "none", "class_", "bool_"]:
            self.gx.types[newnode] = {(cl, cl.dcpa - 1)}
        else:
            if cl.ident == "list" and (dcpa := self.list_type(node)):
                self.gx.types[newnode] = {(cl, dcpa)}
            else:
                self.gx.types[newnode] = {(cl, cl.dcpa)}

    def constructor(
        self,
        node: Union[ast.Tuple, ast.List, ast.Dict, ast.Set],
        classname: str,
        context: VisitContext,
    ) -> None:
        """Generate a constructor"""
        func: Optional[AllParent] = context.parent_object()

        cl = python.def_class(self.gx, classname)
        assert cl

        self.instance(node, cl, func)
        infer.default_var(self.gx, "unit", cl)

        # --- internally flow binary/ternary tuples
        if isinstance(node, ast.Tuple) and cl.ident in ("tuple2", "tuple3"):
            elemnames = cl.tvar_names()
            assert elemnames and len(elemnames) == len(node.elts)
            for elemname in elemnames:
                infer.default_var(self.gx, elemname, cl)

            for elem in node.elts:
                self.visit(elem, context)

            for elem in node.elts:
                self.add_dynamic_constraint(node, elem, "unit", context)

            for elem, elemname in zip(node.elts, elemnames):
                self.add_dynamic_constraint(node, elem, elemname, context)

            return

        # --- add dynamic children constraints for other types
        if isinstance(node, ast.Dict):  # XXX filter children
            infer.default_var(self.gx, "unit", cl)
            infer.default_var(self.gx, "value", cl)

            for child in ast.iter_child_nodes(node):
                self.visit(child, context)

            for key, value in zip(node.keys, node.values):  # XXX filter
                if key is None:  # dict unpacking, e.g. {**d1, 'c': 3}
                    error.error(
                        "dict unpacking ('**') in a dict display is not supported",
                        self.gx,
                        node,
                        mv=getmv(),
                    )
                else:
                    self.add_dynamic_constraint(node, key, "unit", context)
                    self.add_dynamic_constraint(node, value, "value", context)
        else:
            for child in node.elts:
                self.visit(child, context)

            for child in self.filter_redundant_children(node):
                self.add_dynamic_constraint(node, child, "unit", context)

    # --- for compound list/tuple/dict constructors, we only consider a single child node for each subtype
    def filter_redundant_children(
        self, node: Union[ast.Tuple, ast.List, ast.Set]
    ) -> list[ast.expr]:
        """Filter redundant children from a compound list/tuple/dict constructor"""
        done = set()
        nonred: list[ast.expr] = []
        for child in node.elts:
            type = self.child_type_rec(child)
            if not type or type not in done:
                done.add(type)
                nonred.append(child)
        return nonred

    # --- determine single constructor child node type, used by the above
    def child_type_rec(self, node: ast.AST) -> tuple["python.Class", ...]:
        """Determine the type of a single constructor child node"""
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            node = node.operand

        if isinstance(node, (ast.List, ast.Tuple)):
            if isinstance(node, ast.List):
                cl = python.def_class(self.gx, "list")
            elif len(node.elts) == 2:
                cl = python.def_class(self.gx, "tuple2")
            elif len(node.elts) == 3:
                cl = python.def_class(self.gx, "tuple3")
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

        elif isinstance(node, ast.Constant):
            return (list(infer.inode(self.gx, node).types())[0][0],)

        return ()

    # --- add dynamic constraint for constructor argument, e.g. '[expr]' becomes [].__setattr__('unit', expr)
    def add_dynamic_constraint(
        self, parent: ast.expr, child: ast.expr, varname: str, context: VisitContext
    ) -> None:
        """Add a dynamic constraint for a constructor argument"""
        func: Optional[AllParent] = context.parent_object()

        self.gx.assign_target[child] = parent
        cu = ast.Constant(varname)
        self.visit_Constant(cu, context)
        fakefunc = ast.Call(
            ast.Attribute(_as_expr(parent), "__setattr__", ast.Load()),
            [cu, _as_expr(child)],
            [],
        )
        self.visit_Call(fakefunc, context, fake_attr=True)

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
        constraint: tuple[infer.CNode, infer.CNode],
        func: Optional[AllParent],
    ) -> None:
        """Add a regular constraint to a function"""
        in_cnode = constraint[0]
        if (
            isinstance(in_cnode.thing, python.Variable)
            and func
            and in_cnode.thing.parent == func
        ):
            assert False

        infer.in_out(constraint[0], constraint[1])
        self.gx.constraints.add(constraint)
        parent = python.outer_func(func)
        if parent:
            parent.constraints.add(constraint)

    def struct_unpack(self, rvalue: ast.AST, func: Optional[AllParent]) -> bool:
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
        self, node: ast.AST, func: Optional[AllParent]
    ) -> list[tuple[str, str, str, int]]:
        """Get struct information"""
        if isinstance(node, ast.Name):
            var = python.lookup_var(node.id, func, self)  # XXX fwd ref?
            if not var or len(var.const_assign) != 1:
                error.error("non-constant format string", self.gx, node, mv=self)
            error.error(
                "assuming constant format string", self.gx, node, mv=self, warning=True
            )
            assert var
            fmt = var.const_assign[0].value
        elif isinstance(node, ast.Constant):
            fmt = node.value
        else:
            error.error("non-constant format string", self.gx, node, mv=self)
            return []
        if isinstance(fmt, bytes):
            fmt = fmt.decode()
        if not isinstance(fmt, str):
            error.error("non-string format string", self.gx, node, mv=self)
            return []
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
            "N": "i",
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
            if c in string.digits:  # not str.isdigit(), which accepts e.g. '²'
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

    def struct_faketuple(self, info: list[tuple[str, str, str, int]]) -> ast.Tuple:
        """Generate a fake tuple for struct unpack"""
        result: list[ast.expr] = []
        for o, c, t, d in info:
            if d != 0 or c in "sp":
                if t == "int":
                    result.append(ast.Constant(1))
                elif t == "bytes":
                    result.append(ast.Constant(b""))
                elif t == "float":
                    result.append(ast.Constant(1.0))
                elif t == "bool":
                    result.append(ast.Constant(True))
        return ast.Tuple(result, ast.Load())

    def visit_GeneratorExp(self, node: ast.GeneratorExp, context: VisitContext) -> None:
        func: Optional[AllParent] = context.parent_object()

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        lc = ast.ListComp(
            node.elt,
            [
                ast.comprehension(qual.target, qual.iter, qual.ifs, qual.is_async)
                for qual in node.generators
            ],
            lineno=node.lineno,
        )
        register_node(lc, func)
        self.gx.genexp_to_lc[node] = lc
        self.visit(lc, context)
        self.add_constraint((infer.inode(self.gx, lc), newnode), func)

    def visit_JoinedStr(self, node: ast.JoinedStr, context: VisitContext) -> None:
        """Visit a joined string"""
        for value in node.values:
            method = "__str__"
            if isinstance(value, ast.FormattedValue):
                if value.format_spec:
                    error.error(
                        "f-string format spec is not supported",
                        self.gx,
                        node,
                        warning=True,
                        mv=getmv(),
                    )
                # '!s' is just the default str conversion; '!r' and '!a' map
                # onto __repr__ (note '{x=}' desugars to a '!r' conversion as
                # well; '!a' is ascii(), i.e. an escaped repr).
                if value.conversion in (ord("r"), ord("a")):
                    method = "__repr__"
                elif value.conversion not in (None, -1, ord("s")):
                    error.error(
                        "f-string conversion '!%s' is not supported"
                        % chr(value.conversion),
                        self.gx,
                        node,
                        warning=True,
                        mv=getmv(),
                    )
                value = value.value
            self.visit(value, context)
            self.fake_func(infer.inode(self.gx, value), value, method, [], context)
        self.instance(node, python.def_class(self.gx, "str_"), context.parent_object())

    def visit_StrFormat(
        self, node: ast_utils.StrFormat, context: VisitContext
    ) -> None:
        """Visit a literal str.format(..) call (see StrFormatRewriter)

        Each argument is evaluated exactly once and in order, into a temp var,
        unless all arguments are plain names or constants (so there can be no
        side-effects or evaluation order issues). Constant arguments are
        always used directly.
        """
        func: Optional[AllParent] = context.parent_object()

        direct = all(
            isinstance(arg, ast.Name) or ast_utils.is_constant(arg)
            for arg in node.args
        )
        temps: list[Optional[str]] = []
        for i, arg in enumerate(node.args):
            self.visit(arg, context)
            if direct or ast_utils.is_constant(arg):
                temps.append(None)
            else:
                tvar = self.temp_var2(
                    (node, "format", i), infer.inode(self.gx, arg), func
                )
                temps.append(tvar.name)
        self.gx.str_format[node] = temps

        outer, self.str_format_node = self.str_format_node, node
        self.visit(node.joined, context)
        self.str_format_node = outer

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        self.add_constraint((infer.inode(self.gx, node.joined), newnode), func)

    def visit_StrFormatArg(
        self, node: ast_utils.StrFormatArg, context: VisitContext
    ) -> None:
        """Visit a reference to a str.format(..) argument"""
        func: Optional[AllParent] = context.parent_object()

        assert self.str_format_node
        arg = self.str_format_node.args[node.index]
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        self.add_constraint((infer.inode(self.gx, arg), newnode), func)

    def visit_Expr(
        self, node: ast.Expr, context: VisitContext
    ) -> None:
        """Visit an expression"""
        self.bool_test_add(node.value)
        self.visit(node.value, context)

    def visit_NamedExpr(self, node: ast.NamedExpr, context: VisitContext) -> None:
        """Visit a named expression"""
        func: Optional[AllParent] = context.parent_object()
        self.visit(node.value, context)

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
        context.write(node.target, newnode)
        self.add_constraint((newnode, infer.inode(self.gx, lvar)), parent)

    def visit_Module(self, node: ast.Module, context: VisitContext) -> None:
        """Visit a module"""
        # --- literal str.format(..) calls become f-strings
        StrFormatRewriter(self.gx, getmv()).visit(node)

        # --- bootstrap built-in classes
        if self.module.ident == "builtin":
            for dummy in self.gx.builtins:
                self.visit_ClassDef(
                    ast.ClassDef(dummy, [], [], [ast.Pass()], [], []), context
                )

        if self.module.ident != "builtin":
            n = ast.ImportFrom("builtin", [ast.alias("*", None)], 0)  # Python2.5+
            getmv().importnodes.append(n)
            self.visit_ImportFrom(n, context)

        # --- __name__
        if self.module.ident != "builtin":
            namevar = infer.default_var(self.gx, "__name__", None, mv=getmv())
            self.gx.types[infer.inode(self.gx, namevar)] = {
                (python.def_class(self.gx, "str_"), 0)
            }

        self.forward_references(node)

        # --- visit children
        getmv().importnodes.extend(
            n for n in node.body if isinstance(n, (ast.Import, ast.ImportFrom))
        )
        for child in node.body:
            self.visit(child, context)

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
            class_context = context.child_with_class(cl)
            for ancestor in cl.ancestors_upto(None)[1:]:
                cl.staticmethods.extend(ancestor.staticmethods)
                cl.classmethods.extend(ancestor.classmethods)
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
                    self.visit_FunctionDef(
                        func_copy, class_context, inherited_from=func
                    )
                    mv = tempmv
                    setmv(mv)

                    # maintain relation with original
                    self.gx.inheritance_relations.setdefault(func, []).append(
                        cl.funcs[ident]
                    )
                    cl.funcs[ident].inherited = func.node
                    cl.funcs[ident].inherited_from = func
                    cl.funcs[ident].invisible = func.invisible
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
            node.args.args = (
                node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            )
            node.args.posonlyargs = []
            node.args.kwonlyargs = []

    def get_globals(self, node: ast.AST) -> list[str]:
        """Get global variables"""
        if isinstance(node, ast.Global):
            result = node.names
        else:
            result = []
            for child in ast.iter_child_nodes(node):
                result.extend(self.get_globals(child))
        return result

    def local_assignments(self, node: ast.AST, global_: bool = False) -> list[ast.Name]:
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
            children: list[ast.AST]

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

    def visit_Import(self, node: ast.Import, context: VisitContext) -> None:
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
            self.gx.types[infer.inode(self.gx, var)] = {(module, 0)}
        return module

    def visit_ImportFrom(self, node: ast.ImportFrom, context: VisitContext) -> None:
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
                    self.gx.types[infer.inode(self.gx, var)] = {(import_module, 0)}
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
                self.import_module(modname, pseudonym, node, False)
            else:
                error.error(
                    "no identifier '{}' in module '{}'".format(name, node.module),
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
        context: VisitContext,
        is_lambda: bool = False,
        inherited_from: Optional["python.Function"] = None,
    ) -> None:
        """Visit a function definition"""
        parent: Optional["python.Class"] = context.class_object()

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
                elif (
                    parent
                    and isinstance(dec, ast.Name)
                    and dec.id == "classmethod"
                    and getmv().module.builtin
                ):
                    parent.classmethods.append(node.name)
                elif parent and isinstance(dec, ast.Name) and dec.id == "property":
                    parent.properties[node.name] = [node.name, ""]
                elif parent and is_property_setter(dec, parent):
                    assert isinstance(dec, ast.Attribute)
                    assert isinstance(dec.value, ast.Name)
                    parent.properties[dec.value.id][1] = node.name
                else:
                    error.error(
                        "unsupported type of decorator", self.gx, dec, mv=getmv()
                    )

        if parent and not is_lambda:
            if (
                not inherited_from
                and func.ident not in parent.staticmethods
                and func.ident not in parent.classmethods
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
                "__enter__",
                "__exit__",
                "__del__",
                "__copy__",
                "__deepcopy__",
                "__round__",
                "__index__",
                "__reversed__",
                "__divmod__",
                "__floor__",
                "__ceil__",
                "__trunc__",
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

        func_context = VisitContext(func)
        for formal in func.formals:
            formal_node = ast.Name(formal, ast.Store())
            func.formal_nodes[formal] = formal_node
            formal_cnode = infer.CNode(self.gx, getmv(), formal_node, parent=func)
            self.gx.types[formal_cnode] = set()
            func_context.write(formal_node, formal_cnode)
            var = infer.default_var(self.gx, formal, func)
            var.formal_arg = True
            self.add_constraint((formal_cnode, infer.inode(self.gx, var)), func)

        # --- flow return expressions together into single node
        func.retnode = retnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[retnode] = set()
        func.yieldnode = yieldnode = infer.CNode(
            self.gx, getmv(), (node, "yield"), parent=func
        )
        self.gx.types[yieldnode] = set()

        for body_node in node.body:
            self.visit(body_node, func_context)

        defaults_context = VisitContext(func.parent or getmv().module)
        for i, default in enumerate(func.defaults):
            if (
                not ast_utils.is_literal(default)
                and not (
                    isinstance(default, ast.Constant)
                    and isinstance(default.value, bool)
                )  # TODO fix is_literal
            ):
                self.defaults[default] = (len(self.defaults), func, i)
            self.visit(default, defaults_context)  # defaults are global

        # --- add implicit 'return None' if no return expressions
        if not func.returnexpr:
            fakeret = ast.Return(ast.Name("None", ast.Load()))
            func.fakeret = fakeret
            self.visit_Return(fakeret, func_context)

        # --- register function
        if isinstance(parent, python.Class):
            if (
                func.ident not in parent.staticmethods
                and func.ident not in parent.classmethods
            ):  # XXX use flag
                infer.default_var(self.gx, "self", func)
            parent.funcs[func.ident] = func
        # XXX: Should add context.write for ast.Name(node.name,...)

    def visit_Lambda(self, node: ast.Lambda, context: VisitContext) -> None:
        """Visit a lambda function"""
        lambdanr = len(self.lambdas)
        name = "__lambda%d__" % lambdanr
        fakenode = ast.FunctionDef(name, node.args, [ast.Return(node.body)], [])
        lambda_context = VisitContext(context.namespace)  # XXX: What should this be?
        self.visit_FunctionDef(fakenode, lambda_context, True)
        f = self.lambdas[name]
        f.lambdanr = lambdanr
        self.lambdaname[node] = name
        newnode = infer.CNode(self.gx, getmv(), node, parent=context.parent_object())
        self.gx.types[newnode] = {(f, 0)}
        newnode.copymetoo = True

    def visit_BoolOp(self, node: ast.BoolOp, context: VisitContext) -> None:
        """Visit a boolean operation"""
        func: Optional[AllParent] = context.parent_object()

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        for child in node.values:
            if node in self.gx.bool_test_only:
                self.bool_test_add(child)
            self.visit(child, context)
            self.add_constraint((infer.inode(self.gx, child), newnode), func)
            self.temp_var2(child, newnode, func)

    def visit_If(
        self,
        node: ast.If,
        context: VisitContext,
        root_if: Optional[ast.If] = None,
    ) -> None:
        """Visit an if statement"""
        func: Optional[AllParent] = context.parent_object()

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

        if_context = context.child()
        self.bool_test_add(node.test)
        faker = ast.Call(ast.Name("bool", ast.Load()), [node.test], [])
        self.visit(faker, if_context)
        body_context = if_context.child()
        for child in node.body:
            self.visit(child, body_context)
        if node.orelse:
            orelse_context = if_context.child()
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self.visit_If(node.orelse[0], orelse_context, root_if)
            else:
                for child in node.orelse:
                    self.visit(child, orelse_context)
            if_context.merge([body_context, orelse_context], False)
        else:
            if_context.merge([body_context], True)
        context.merge([if_context], False)

    def visit_IfExp(self, node: ast.IfExp, context: VisitContext) -> None:
        """Visit an if expression"""
        func: Optional[AllParent] = context.parent_object()

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()

        for child in ast.iter_child_nodes(node):
            self.visit(child, context)  # XXX: Should use new context?

        self.add_constraint((infer.inode(self.gx, node.body), newnode), func)
        self.add_constraint((infer.inode(self.gx, node.orelse), newnode), func)

    def visit_Match(self, node: ast.Match, context: VisitContext) -> None:
        """Visit a match statement"""
        error.error("match case statement not supported", self.gx, node, mv=getmv())

    def visit_Global(self, node: ast.Global, context: VisitContext) -> None:
        """Visit a global statement"""
        func = context.parent_object()
        assert func is not None
        func.globals.update(node.names)

    def visit_List(self, node: ast.List, context: VisitContext) -> None:
        """Visit a list"""
        self.constructor(node, "list", context)

    def visit_Dict(self, node: ast.Dict, context: VisitContext) -> None:
        """Visit a dictionary"""
        self.constructor(node, "dict", context)

    def visit_Set(self, node: ast.Set, context: VisitContext) -> None:
        """Visit a set"""
        self.constructor(node, "set", context)

    def visit_Tuple(self, node: ast.Tuple, context: VisitContext) -> None:
        """Visit a tuple"""
        if isinstance(node.ctx, ast.Load):
            if len(node.elts) == 2:
                self.constructor(node, "tuple2", context)
            elif len(node.elts) == 3:
                self.constructor(node, "tuple3", context)
            else:
                self.constructor(node, "tuple", context)
        else:
            error.error("unsupported tuple ctx", self.gx, node, mv=getmv())

    def visit_Subscript(self, node: ast.Subscript, context: VisitContext) -> None:
        """Visit a subscript"""
        # XXX merge __setitem__, __getitem__
        if isinstance(node.slice, ast.Slice):
            nslice = node.slice
            self.slice(
                node, node.value, [nslice.lower, nslice.upper, nslice.step], context
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
                self.fake_func(node, node.value, "__delitem__", [subscript], context)
            elif isinstance(subscript, (ast.List, ast.Tuple)):
                self.fake_func(node, node.value, "__getitem__", [subscript], context)
            else:
                ident = "__getitem__"
                self.fake_func(node, node.value, ident, [subscript], context)

    def visit_Slice(self, node: ast.Slice, context: VisitContext) -> None:
        """Visit a slice"""
        assert False

    def slice(
        self,
        node: Union[ast.Slice, ast.Subscript],
        expr: ast.AST,
        nodes: list[Optional[ast.AST]],
        context: VisitContext,
        replace: Optional[ast.AST] = None,
    ) -> None:
        """Slice a node"""
        nodes2 = slice_nums(nodes)
        if replace:
            self.fake_func(node, expr, "__setslice__", nodes2 + [replace], context)
        elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Del):
            self.fake_func(node, expr, "__delete__", nodes2, context)
        else:
            self.fake_func(node, expr, "__slice__", nodes2, context)

    def visit_UnaryOp(self, node: ast.UnaryOp, context: VisitContext) -> None:
        """Visit a unary operation"""
        func: Optional[AllParent] = context.parent_object()

        op_type = type(node.op)
        if op_type == ast.Not:
            self.bool_test_add(node.operand)
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)
            newnode.copymetoo = True
            self.gx.types[newnode] = {
                (python.def_class(self.gx, "bool_"), 0)
            }  # XXX new type?
            self.visit(node.operand, context)
        else:
            op_map = {
                ast.USub: "__neg__",
                ast.UAdd: "__pos__",
                ast.Invert: "__invert__",
            }
            self.fake_func(node, node.operand, op_map[op_type], [], context)

    def visit_Compare(self, node: ast.Compare, context: VisitContext) -> None:
        """Visit a comparison"""
        func: Optional[AllParent] = context.parent_object()

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        newnode.copymetoo = True
        self.gx.types[newnode] = {
            (python.def_class(self.gx, "bool_"), 0)
        }  # XXX new type?
        self.visit(node.left, context)
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
            self.visit(right, context)
            msg = msgs.get(type(op))

            if msg == "contains":
                self.fake_func(node, right, "__" + msg + "__", [left], context)

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
                self.visit(fakefunc, context)
            elif msg:
                self.fake_func(node, left, "__" + msg + "__", [right], context)
            left = right

        # tempvars, e.g. (t1=fun())
        for term in node.comparators[:-1]:
            if not (isinstance(term, ast.Name) or ast_utils.is_constant(term)):
                self.temp_var2(term, infer.inode(self.gx, term), func)

    def visit_BinOp(self, node: ast.BinOp, context: VisitContext) -> None:
        """Visit a binary operation"""
        if isinstance(node.op, ast.Add):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "add"),
                [node.right],
                context,
            )
        elif isinstance(node.op, ast.Sub):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "sub"),
                [node.right],
                context,
            )
        elif isinstance(node.op, ast.Mult):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "mul"),
                [node.right],
                context,
            )
        elif isinstance(node.op, ast.Div):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "truediv"),
                [node.right],
                context,
            )
        elif isinstance(node.op, ast.FloorDiv):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "floordiv"),
                [node.right],
                context,
            )
        elif isinstance(node.op, ast.Pow):
            if not getmv().module.builtin:
                node.right = ast_utils.float_negative_exponent(node.right)
            self.fake_func(node, node.left, "__pow__", [node.right], context)
        elif isinstance(node.op, ast.Mod):
            if isinstance(node.right, ast.Tuple):
                self.fake_func(node, node.left, "__mod__", [], context)
                for child in node.right.elts:
                    self.visit(child, context)
                    self.fake_func(
                        infer.inode(self.gx, child), child, "__str__", [], context
                    )
            else:
                self.fake_func(node, node.left, "__mod__", [node.right], context)
        elif isinstance(node.op, ast.LShift):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "lshift"),
                [node.right],
                context,
            )
        elif isinstance(node.op, ast.RShift):
            self.fake_func(
                node,
                node.left,
                ast_utils.aug_msg(self.gx, node, "rshift"),
                [node.right],
                context,
            )
        elif isinstance(node.op, ast.BitOr):
            self.visit_impl_bitpair(
                node, ast_utils.aug_msg(self.gx, node, "or"), context
            )
        elif isinstance(node.op, ast.BitXor):
            self.visit_impl_bitpair(
                node, ast_utils.aug_msg(self.gx, node, "xor"), context
            )
        elif isinstance(node.op, ast.BitAnd):
            self.visit_impl_bitpair(
                node, ast_utils.aug_msg(self.gx, node, "and"), context
            )
        # PY3: elif isinstance(node.op, MatMult):
        else:
            error.error(
                "Unknown op type for ast.BinOp: %s" % type(node.op),
                self.gx,
                node,
                mv=getmv(),
            )

    def visit_impl_bitpair(
        self, node: ast.BinOp, msg: str, context: VisitContext
    ) -> None:
        """Visit an implementation of a bitwise pair operation"""
        infer.CNode(self.gx, getmv(), node, parent=context.parent_object())
        self.gx.types[infer.inode(self.gx, node)] = set()
        faker = self.fake_func((node.left, 0), node.left, msg, [node.right], context)
        self.add_constraint(
            (infer.inode(self.gx, faker), infer.inode(self.gx, node)),
            context.parent_object(),
        )

    def visit_AugAssign(self, node: ast.AugAssign, context: VisitContext) -> None:
        """Visit an augmented assignment"""
        func: Optional[AllParent] = context.parent_object()

        # a[b] += c -> a[b] = a[b]+c, using tempvars to handle sidefx
        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()

        clone = copy.deepcopy(node)
        assert isinstance(clone, ast.AugAssign)
        lnode: ast.expr

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
            self.visit_Assign(a1, context)
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
            self.visit_Assign(a2, context)
            self.add_constraint(
                (infer.inode(self.gx, subs), infer.inode(self.gx, t2)), func
            )

            infer.inode(self.gx, node).temp1 = t1.name
            infer.inode(self.gx, node).temp2 = t2.name
            infer.inode(self.gx, node).subs = subs

            blah = ast.Subscript(
                ast.Name(t1.name, ast.Load(), lineno=node.lineno),
                ast.Name(t2.name, ast.Load()),
                ast.Store(),
                lineno=node.lineno,
            )
            lnode = ast.Subscript(
                ast.Name(t1.name, ast.Load(), lineno=node.lineno),
                ast.Name(t2.name, ast.Load()),
                ast.Load(),
                lineno=node.lineno,
            )
        else:
            error.error("unsupported type of assignment", self.gx, node, mv=getmv())
            return

        blah2 = ast.BinOp(lnode, node.op, node.value)
        self.gx.augment.add(blah2)

        assign = ast.Assign([blah], blah2)
        register_node(assign, func)
        infer.inode(self.gx, node).assignhop = assign
        self.visit_Assign(assign, context)

    def temp_var(
        self,
        node: Any,
        func: Optional[AllParent] = None,
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
        self, node: Any, source: Any, func: Optional[AllParent]
    ) -> "python.Variable":
        """Create a temporary variable from a source"""
        tvar = self.temp_var(node, func)
        self.add_constraint((source, infer.inode(self.gx, tvar)), func)
        return tvar

    def temp_var_int(
        self, node: Any, func: Optional[AllParent]
    ) -> "python.Variable":
        """Create a temporary integer variable"""
        var = self.temp_var(node, func)
        self.gx.types[infer.inode(self.gx, var)] = {
            (python.def_class(self.gx, "int_"), 0)
        }
        infer.inode(self.gx, var).copymetoo = True
        return var

    def visit_Raise(self, node: ast.Raise, context: VisitContext) -> None:
        """Visit a raise statement"""
        if node.exc is None or node.cause is not None:
            error.error("unsupported raise syntax", self.gx, node, mv=getmv())
        for child in ast.iter_child_nodes(node):
            self.visit(child, context)

    def visit_Assert(self, node: ast.Assert, context: VisitContext) -> None:
        """Visit an assert statement"""
        self.visit(node.test, context)
        if node.msg:
            self.visit(node.msg, context)

    def visit_Try(self, node: ast.Try, context: VisitContext) -> None:
        """Visit a try statement"""
        func: Optional[AllParent] = context.parent_object()

        try_context = context.child()
        body_context = try_context.child()
        for child in node.body:
            self.visit(child, body_context)

        child_contexts: list[VisitContext] = [body_context]
        for handler in node.handlers:
            handler_context = (
                body_context.as_except_context()
            )  # XXX: which context to use as parent
            child_contexts.append(handler_context)
            if handler.type is not None:
                if isinstance(handler.type, ast.Tuple):
                    pairs = [(n, handler.name) for n in handler.type.elts]
                    if len(pairs) > 1:
                        for h0, h1 in pairs:
                            self.gx.handler_body[h0] = copy.deepcopy(handler.body)
                else:
                    pairs = [(handler.type, handler.name)]

                for h0, h1 in pairs:
                    if isinstance(h0, ast.Name) and h0.id in [
                        "int",
                        "float",
                        "str",
                        "class",
                    ]:
                        # XXX: Wouldn't this imply catching basic type as exception?
                        continue  # handle in python.lookup_class

                    handler_body = self.gx.handler_body.get(h0, handler.body)

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

                    varname: Optional["ast.Name"] = None
                    if isinstance(h1, str):
                        varname = ast.Name(h1, ast.Store())
                        var = self.default_var(h1, func, exc_name=True)
                    elif isinstance(h1, ast.Name):  # py2
                        varname = h1
                        var = self.default_var(h1.id, func, exc_name=True)
                    else:
                        var = self.temp_var(h0, func, exc_name=True)

                    cnode = self.gx.cnode.get((h0, 0, 0)) or infer.CNode(
                        self.gx, getmv(), h0, parent=func
                    )
                    self.gx.types[cnode] = {(cl, 1)}

                    var.invisible = True
                    var_cnode = infer.inode(self.gx, var)
                    var_cnode.copymetoo = True
                    self.add_constraint((cnode, var_cnode), func)

                    if varname:
                        handler_context.contained_write(varname, cnode)
                    for child in handler_body:
                        self.visit(child, handler_context)
            else:
                for child in handler.body:
                    self.visit(child, handler_context)

        if node.finalbody:
            error.error("'try..finally' is not supported", self.gx, node, mv=getmv())

        # else
        if node.orelse:
            # XXX: which context to use as parent
            for child in node.orelse:
                self.visit(child, body_context)  # Should a child be created and merged?
            self.temp_var_int((node, "orelse"), func)

        try_context.merge(child_contexts, False)
        context.merge([try_context], False)

    def visit_Yield(self, node: ast.Yield, context: VisitContext) -> None:
        """Visit a yield statement"""
        func: Optional["python.Function"] = context.function()
        assert func is not None

        func.isGenerator = True
        func.yieldNodes.append(node)
        node_value = node.value
        if not node_value:
            node_value = ast.Name("None", ast.Load())
            node.value = node_value
        self.visit_Return(
            ast.Return(ast.Call(ast.Name("__iter", ast.Load()), [node_value], [])),
            context,
        )
        self.add_constraint((infer.inode(self.gx, node.value), func.yieldnode), func)

    def visit_YieldFrom(self, node: ast.YieldFrom, context: VisitContext) -> None:
        """Visit a 'yield from' expression"""
        error.error("'yield from' is not supported", self.gx, node, mv=getmv())

    def visit_For(self, node: ast.For, context: VisitContext) -> None:
        """Visit a for statement"""
        func: Optional[AllParent] = context.parent_object()

        # --- iterable contents -> assign node
        assnode = infer.CNode(self.gx, getmv(), node.target, parent=func)
        self.gx.types[assnode] = set()

        get_iter = ast.Call(ast.Attribute(node.iter, "__iter__", ast.Load()), [], [])
        fakefunc = ast.Call(ast.Attribute(get_iter, "__next__", ast.Load()), [], [])

        for_context = context.child()
        self.visit_Call(fakefunc, for_context)
        self.add_constraint((infer.inode(self.gx, fakefunc), assnode), func)

        # --- assign node -> variables  XXX merge into assign_pair
        if isinstance(node.target, ast.Name):
            # for x in..
            lvar = self.default_var(node.target.id, func)
            context.write(node.target, assnode)
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
                [ast.Constant(node.target.attr), fakefunc],
                [],
            )
            self.visit_Call(fakefunc2, context)

        elif ast_utils.is_assign_list_or_tuple(node.target):
            # for (a,b, ..) in..
            self.tuple_flow(node.target, node.target, context)
        else:
            error.error("unsupported type of assignment", self.gx, node, mv=getmv())

        self.do_for(node, assnode, get_iter, func)

        # --- loop body
        self.gx.loopstack.append(node)
        body_context = for_context.child()
        for child in node.body:
            self.visit(child, body_context)
        self.gx.loopstack.pop()

        # --- for-else
        if node.orelse:
            self.temp_var_int((node, "orelse"), func)
            orelse_context = for_context.child()
            for child in node.orelse:
                self.visit(child, orelse_context)
            for_context.merge_loop_orelse(getmv(), body_context, orelse_context)
        else:
            for_context.merge_loop(getmv(), body_context)
        context.merge([for_context], False)

    def do_for(
        self,
        node: Union[ast.For, ast.comprehension],
        assnode: "infer.CNode",
        get_iter: ast.Call,
        func: Optional[AllParent],
    ) -> None:
        """Process a for statement"""
        # --- for i in range(..) XXX i should not be modified.. use tempcounter; two bounds
        if ast_utils.is_fastfor(node, func, self):
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

            if ast_utils.is_enumerate(node, func, self) or ast_utils.is_zip2(
                node, func, self
            ):
                assert isinstance(node.iter, ast.Call)
                self.temp_var2((node, 2), infer.inode(self.gx, node.iter.args[0]), func)
                if ast_utils.is_zip2(node, func, self):
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

    def visit_While(self, node: ast.While, context: VisitContext) -> None:
        """Visit a while statement"""
        func: Optional[AllParent] = context.parent_object()

        while_context = context.child()
        self.gx.loopstack.append(node)
        self.bool_test_add(node.test)
        self.visit(node.test, context)
        body_context = while_context.child()
        for child in node.body:
            self.visit(child, body_context)
        self.gx.loopstack.pop()

        if node.orelse:
            self.temp_var_int((node, "orelse"), func)
            orelse_context = while_context.child()
            for child in node.orelse:
                self.visit(child, orelse_context)
            while_context.merge_loop_orelse(getmv(), body_context, orelse_context)
        else:
            while_context.merge_loop(getmv(), body_context)
        context.merge([while_context], False)

    def visit_Continue(self, node: ast.Continue, context: VisitContext) -> None:
        """Visit a continue statement"""
        pass

    def visit_Break(self, node: ast.Break, context: VisitContext) -> None:
        """Visit a break statement"""
        pass

    def visit_With(self, node: ast.With, context: VisitContext) -> None:
        """Visit a with statement"""
        func: Optional[AllParent] = context.parent_object()

        if len(node.items) > 1:
            error.error(
                "with-construct with multiple 'as' terms", self.gx, node, mv=getmv()
            )
        item = node.items[0]

        self.visit(item.context_expr, context)

        if item.optional_vars:
            if isinstance(item.optional_vars, ast.Name):
                varnode = infer.CNode(self.gx, getmv(), item.optional_vars, parent=func)
                self.gx.types[varnode] = set()
                assnode = infer.inode(self.gx, item.context_expr)
                context.write(item.optional_vars, assnode)
                self.add_constraint((assnode, varnode), func)
                lvar = self.default_var(item.optional_vars.id, func)
                self.add_constraint((varnode, infer.inode(self.gx, lvar)), func)
            else:
                error.error("unsupported with syntax", self.gx, item, mv=getmv())

        body_context = context.child()
        for child in node.body:
            self.visit(child, body_context)
        context.merge([body_context], False)

    def visit_ListComp(self, node: ast.ListComp, context: VisitContext) -> None:
        """Visit a list/set/dict/generator comprehension"""
        # --- [expr for iter in list for .. if cond ..]
        # --- {..}
        # --- {a: b for .. }
        # --- (expr for .. }
        func: Optional[AllParent] = context.parent_object()

        lcfunc = python.Function(self.gx, getmv(), parent=func)
        lcfunc.listcomp = True
        lcfunc.ident = "l.c."  # XXX
        lc_context = VisitContext(lcfunc)

        for qual in node.generators:
            # iter
            assnode = infer.CNode(
                self.gx, getmv(), qual.target, parent=lc_context.parent_object()
            )
            self.gx.types[assnode] = set()

            # list.unit->iter
            get_iter = ast.Call(
                ast.Attribute(qual.iter, "__iter__", ast.Load()), [], []
            )
            fakefunc = ast.Call(ast.Attribute(get_iter, "__next__", ast.Load()), [], [])
            self.visit_Call(fakefunc, lc_context)
            fakefunc_cnode = infer.inode(self.gx, fakefunc)
            self.add_constraint(
                (fakefunc_cnode, infer.inode(self.gx, qual.target)),
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
                lc_context.contained_write(qual.target, fakefunc_cnode)
            else:  # AssTuple, AssList
                self.tuple_flow(qual.target, qual.target, lc_context, True)

            self.do_for(qual, assnode, get_iter, lcfunc)

            # cond
            for child in qual.ifs:
                self.bool_test_add(child)
                self.visit(child, lc_context)

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
        if node in self.gx.dictcomp_to_lc.values():
            assert isinstance(node.elt, ast.Tuple)
            assert len(node.elt.elts) == 2
            self.visit(node.elt.elts[0], lc_context)
            self.add_dynamic_constraint(node, node.elt.elts[0], "unit", lc_context)
            self.visit(node.elt.elts[1], lc_context)
            self.add_dynamic_constraint(node, node.elt.elts[1], "value", lc_context)
        else:
            self.visit(node.elt, lc_context)
            self.add_dynamic_constraint(node, node.elt, "unit", lc_context)

        lcfunc.ident = "list_comp_" + str(len(self.listcomps))
        self.listcomps.append((node, lcfunc, func))

    def visit_DictComp(self, node: ast.DictComp, context: VisitContext) -> None:
        """Visit a dictionary comprehension"""
        func: Optional[AllParent] = context.parent_object()

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        lc = ast.ListComp(
            ast.Tuple([node.key, node.value], ast.Load()),
            [
                ast.comprehension(qual.target, qual.iter, qual.ifs, qual.is_async)
                for qual in node.generators
            ],
            lineno=node.lineno,
        )
        register_node(lc, func)
        self.gx.dictcomp_to_lc[node] = lc
        self.visit_ListComp(lc, context)
        self.add_constraint((infer.inode(self.gx, lc), newnode), func)

    def visit_SetComp(self, node: ast.SetComp, context: VisitContext) -> None:
        """Visit a set comprehension"""
        func: Optional[AllParent] = context.parent_object()

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()
        lc = ast.ListComp(
            node.elt,
            [
                ast.comprehension(qual.target, qual.iter, qual.ifs, qual.is_async)
                for qual in node.generators
            ],
            lineno=node.lineno,
        )
        register_node(lc, func)
        self.gx.setcomp_to_lc[node] = lc
        self.visit_ListComp(lc, context)
        self.add_constraint((infer.inode(self.gx, lc), newnode), func)

    def visit_Return(self, node: ast.Return, context: VisitContext) -> None:
        """Visit a return statement"""
        func: Optional["python.Function"] = context.function()
        assert func is not None

        node_value = node.value
        if node_value is None:
            node_value = ast.Name("None", ast.Load())
            node.value = node_value
        self.visit(node_value, context)
        func.returnexpr.append(node_value)
        if node.value is not None:  # Not naked return
            newnode = infer.CNode(self.gx, getmv(), node, parent=func)
            self.gx.types[newnode] = set()
        if func.retnode:
            self.add_constraint((infer.inode(self.gx, node.value), func.retnode), func)

    def visit_Delete(self, node: ast.Delete, context: VisitContext) -> None:
        """Visit a delete statement"""
        for child in node.targets:
            #            assert isinstance(child.ctx, ast.Del)
            self.visit(child, context)

    def visit_AnnAssign(self, node: ast.AnnAssign, context: VisitContext) -> None:
        """Visit an annotated assignment"""
        if node.value is None:
            return
        assign = ast.Assign([node.target], node.value)
        self.visit(assign, context)

    def visit_Assign(self, node: ast.Assign, context: VisitContext) -> None:
        """Visit an assignment"""
        # skip type annotations
        if node.value is None:
            return

        func: Optional[AllParent] = context.parent_object()

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
                self.visit(node.value, context)
                sinfo = self.struct_info(rvalue2.args[0], func)
                faketuple = self.struct_faketuple(sinfo)
                self.visit_Assign(ast.Assign(node.targets, faketuple), context)
                tvar = self.temp_var2(
                    rvalue2.args[1], infer.inode(self.gx, rvalue2.args[1]), func
                )
                tvar_pos = self.temp_var_int(rvalue2.args[0], func)
                base_name = None  # start position, for native alignment
                if (isinstance(rvalue2.func, ast.Attribute) and rvalue2.func.attr == "unpack_from") or \
                   (isinstance(rvalue2.func, ast.Name) and rvalue2.func.id == "unpack_from"):
                    base_name = self.temp_var_int(rvalue2.func, func).name
                self.gx.struct_unpack[node] = (sinfo, tvar.name, tvar_pos.name, base_name)
                return

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()

        # --- a,b,.. = c,(d,e),.. = .. = expr
        for target_expr in node.targets:
            mismatch = ast_utils.check_assign_arity(target_expr, node.value)
            if mismatch:
                expected, got = mismatch
                if got > expected:
                    error.error(
                        "too many values to unpack (expected %d)" % expected,
                        self.gx,
                        node,
                        mv=getmv(),
                    )
                else:
                    error.error(
                        "not enough values to unpack (expected %d, got %d)"
                        % (expected, got),
                        self.gx,
                        node,
                        mv=getmv(),
                    )
            pairs = ast_utils.assign_rec(target_expr, node.value)
            for lvalue, rvalue in pairs:
                # expr[expr] = expr
                if isinstance(lvalue, ast.Subscript) and not isinstance(
                    lvalue.slice, (ast.Slice, ast.Del)
                ):
                    self.assign_pair(
                        lvalue, rvalue, context
                    )  # XXX use here generally, and in tuple_flow

                # expr.attr = expr
                elif ast_utils.is_assign_attribute(lvalue):
                    self.assign_pair(lvalue, rvalue, context)

                # name = expr
                elif isinstance(lvalue, ast.Name):
                    if (rvalue, 0, 0) not in self.gx.cnode:  # XXX generalize
                        self.visit(rvalue, context)
                    self.visit_Name(lvalue, context)
                    lvar = self.default_var(lvalue.id, func)
                    if ast_utils.is_constant(rvalue):
                        assert isinstance(rvalue, ast.Constant)
                        lvar.const_assign.append(rvalue)
                    context.write(lvalue, infer.inode(self.gx, rvalue))
                    self.add_constraint(
                        (infer.inode(self.gx, rvalue), infer.inode(self.gx, lvar)),
                        func,
                    )

                # (a,(b,c), ..) = expr
                elif ast_utils.is_assign_list_or_tuple(lvalue):
                    self.visit(rvalue, context)
                    self.tuple_flow(lvalue, rvalue, context)

                # expr[a:b] = expr # XXX bla()[1:3] = [1]
                elif isinstance(lvalue, ast.Slice):
                    assert False, (
                        "ast.Slice shouldn't appear outside ast.Subscript node"
                    )
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
                        context,
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
        self, lvalue: ast.AST, rvalue: ast.AST, context: VisitContext
    ) -> None:
        """Assign a pair of values"""
        # expr[expr] = expr
        func: Optional[AllParent] = context.parent_object()

        if isinstance(lvalue, ast.Subscript) and not isinstance(
            lvalue.slice, (ast.Slice, ast.Del)
        ):
            if isinstance(lvalue.slice, ast.Index):
                assert False
            #                subscript = lvalue.slice.value
            else:
                subscript = lvalue.slice
            assert isinstance(subscript, ast.expr)
            assert isinstance(rvalue, ast.expr)
            assert isinstance(lvalue.value, ast.expr)

            fakefunc = ast.Call(
                ast.Attribute(lvalue.value, "__setitem__", ast.Load()),
                [subscript, rvalue],
                [],
            )
            self.visit_Call(fakefunc, context)
            infer.inode(self.gx, lvalue.value).fakefunc = fakefunc

            if not isinstance(lvalue.value, ast.Name):
                self.temp_var2(lvalue.value, infer.inode(self.gx, lvalue.value), func)

        # expr.attr = expr
        elif ast_utils.is_assign_attribute(lvalue):
            assert isinstance(lvalue, ast.Attribute)
            assert isinstance(lvalue.value, ast.expr)
            assert isinstance(rvalue, ast.expr)
            infer.CNode(self.gx, getmv(), lvalue, parent=func)
            self.gx.assign_target[rvalue] = lvalue.value
            fakefunc = ast.Call(
                ast.Attribute(lvalue.value, "__setattr__", ast.Load()),
                [ast.Constant(lvalue.attr), rvalue],
                [],
            )
            self.visit_Call(fakefunc, context)

    def default_var(
        self, name: str, func: Optional[AllParent], exc_name: bool = False
    ) -> "python.Variable":
        """Get the default variable for a name"""
        if isinstance(func, (python.Function, python.Class, python.StaticClass)) and name in func.globals:
            return infer.default_var(self.gx, name, None, mv=getmv(), exc_name=exc_name)
        else:
            return infer.default_var(self.gx, name, func, mv=getmv(), exc_name=exc_name)

    def tuple_flow(
        self,
        lvalue: ast.AST,
        rvalue: ast.AST,
        context: VisitContext,
        is_contained: bool = False,
    ) -> None:
        """Handle tuple flow"""
        func: Optional[AllParent] = context.parent_object()

        self.temp_var2(lvalue, infer.inode(self.gx, rvalue), func)

        lvalues: list[ast.expr]
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
                ast.Attribute(_as_expr(rvalue), "__getunit__", ast.Load()),
                [ast.Constant(i)],
                [],
            )

            fakenode.callfuncs.append(fakefunc)
            self.visit_Call(fakefunc, context, fake_attr=True)

            self.gx.item_rvalue[item] = rvalue
            if isinstance(item, ast.Name):
                lvar = self.default_var(item.id, func)
                fakefunc_cnode = infer.inode(self.gx, fakefunc)
                self.add_constraint(
                    (fakefunc_cnode, infer.inode(self.gx, lvar)), func,
                )
                if is_contained:
                    context.contained_write(item, fakefunc_cnode)
                else:
                    context.write(item, fakefunc_cnode)
            elif isinstance(item, ast.Subscript) or ast_utils.is_assign_attribute(item):
                self.assign_pair(item, fakefunc, context)
            elif ast_utils.is_assign_list_or_tuple(item):  # recursion
                self.tuple_flow(item, fakefunc, context)
            else:
                error.error("unsupported type of assignment", self.gx, item, mv=getmv())

    def super_call(
        self, orig: ast.Call, func: Optional["python.Function"]
    ) -> Optional[ast.expr]:
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
                func
                and isinstance(func.parent, python.Class)
                and len(node.value.args) == 0
            ):
                if func.parent.node.bases:
                    base = func.parent.node.bases[0]
                    assert isinstance(base, ast.expr)
                    return base
            elif (
                len(node.value.args) >= 2
                and isinstance(node.value.args[1], ast.Name)
                and node.value.args[1].id == "self"
            ):
                cl = python.lookup_class(node.value.args[0], getmv())
                assert cl
                if cl.node.bases:
                    base = cl.node.bases[0]
                    assert isinstance(base, ast.expr)
                    return base
            error.error("unsupported usage of 'super'", self.gx, orig, mv=getmv())
        return None

    def visit_Pass(
        self, node: ast.Pass, context: VisitContext
    ) -> None:
        """Visit a pass statement"""
        pass

    def visit_Call(
        self,
        node: ast.Call,
        context: VisitContext,
        fake_attr: bool = False,
    ) -> None:
        """Visit a call statement"""
        # XXX clean up!!
        func: Optional[AllParent] = context.parent_object()

        newnode = infer.CNode(self.gx, getmv(), node, parent=func)
        self.gx.types[newnode] = set()

        # XXX import math; math.e
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.ctx, ast.Load):
            # os.fdopen(fd, 'rb') returns a binary file, as open(.., 'rb')
            if node.func.attr == "fdopen" and ast_utils.is_binary_mode(node, 1):
                module = python.lookup_module(node.func.value, getmv())
                if module and module.ident == "os":
                    node.func.attr = "fdopen_binary"

            # classmethod: insert 'cls' arg (None for now)
            if not fake_attr and isinstance(node.func.value, ast.Name):
                if node.func.value.id in (
                    "dict",
                    "frozendict",
                    "float",
                    "bytes",
                    "complex",
                    "bytearray",
                ):
                    node.args.insert(0, ast.Name("None", ast.Load()))

            # rewrite super(..) call
            if isinstance(func, python.Function):
                base = self.super_call(node, func)
                if base:
                    node.func = ast.Attribute(
                        copy.deepcopy(base), node.func.attr, ast.Load()
                    )
                    node.args.insert(0, ast.Name("self", ast.Load()))

            # method call
            if not fake_attr:
                self.visit_Attribute(node.func, context, callfunc=True)
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
                assert ast_utils.is_str(node.args[0])
                if (
                    _const_str(node.args[0])
                    in getmv().imports[node.func.value.id].mv.globals
                ):  # XXX bleh
                    self.add_constraint(
                        (
                            infer.inode(
                                self.gx,
                                getmv()
                                .imports[node.func.value.id]
                                .mv.globals[_const_str(node.args[0])],
                            ),
                            newnode,
                        ),
                        func,
                    )

        elif isinstance(node.func, ast.Name):
            # direct call
            ident = node.func.id
            # if 'ident' is shadowed by a local variable or parameter, none
            # of the builtin-specific special-casing below applies: this is
            # just a regular call through that variable, not a call to the
            # builtin of the same name.
            shadowed = python.lookup_var(ident, func, getmv()) is not None

            if ident == "print" and not shadowed:
                ident = node.func.id = "__print"  # XXX

            if ident == "open" and not shadowed:
                mode_arg = ast_utils.mode_arg(node, 1)
            else:
                mode_arg = None
            if mode_arg is not None:
                if ast_utils.is_str(mode_arg):
                    if "b" in _const_str(mode_arg):
                        ident = node.func.id = "open_binary"

                else:
                    error.error(
                        "non-constant mode passed to 'open'",
                        self.gx,
                        node.func,
                        mv=getmv(),
                    )

            # from os import fdopen; fdopen(fd, 'rb'): as os.fdopen above
            ext_func = getmv().ext_funcs.get(ident)
            if (
                not shadowed
                and ext_func
                and ext_func.ident == "fdopen"
                and ext_func.mv.module.ident == "os"
                and ast_utils.is_binary_mode(node, 1)
            ):
                ident = node.func.id = "fdopen_binary"
                getmv().ext_funcs[ident] = ext_func.mv.funcs[ident]

            if (
                not shadowed
                and ident in ["hasattr", "getattr", "setattr", "slice", "type", "Ellipsis"]
            ):
                error.error(
                    "'%s' function is not supported" % ident,
                    self.gx,
                    node.func,
                    mv=getmv(),
                )
            if not shadowed and ident == "dict" and node.keywords:
                error.error(
                    "unsupported method of initializing dictionaries",
                    self.gx,
                    node,
                    mv=getmv(),
                )
            if not shadowed and ident == "isinstance":
                error.error(
                    "'isinstance' is not supported; always returns True",
                    self.gx,
                    node,
                    mv=getmv(),
                    warning=True,
                )

            # pow(10, -1) should agree with 10 ** -1, see visit_BinOp. Only the
            # two-argument form: three-argument pow is modular exponentiation.
            if not shadowed and ident == "pow" and not getmv().module.builtin:
                if len(node.args) == 2 and not node.keywords:
                    node.args[1] = ast_utils.float_negative_exponent(node.args[1])

            # optimize sum/max/min(listcomp-or-genexpr)
            if not shadowed and ident in ("sum", "min", "max") and not getmv().module.builtin:
                if (
                    len(node.args) == 1
                    and isinstance(node.args[0], (ast.ListComp, ast.GeneratorExp))
                    and not node.keywords
                ):
                    self.gx.fuse_reduce.add(node)
                    self.gx.fuse_reduce_arg.add(node.args[0])
                    self.gx.fuse_reduce_op[node.args[0]] = ident

            if shadowed or python.lookup_var(ident, func, getmv()):
                self.visit(node.func, context)
                infer.inode(self.gx, node.func).callfuncs.append(
                    node
                )  # XXX iterative dataflow analysis: move there
        else:
            self.visit(node.func, context)
            infer.inode(self.gx, node.func).callfuncs.append(
                node
            )  # XXX iterative dataflow analysis: move there

        # --- arguments
        if not getmv().module.builtin and has_star_kwarg(node):
            error.error(
                "argument (un)packing is not supported", self.gx, node, mv=getmv()
            )

        for arg in get_arg_nodes(node):
            self.visit(arg, context)
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

    def visit_ClassDef(self, node: ast.ClassDef, context: VisitContext) -> None:
        """Visit a class definition"""
        if not getmv().module.builtin and node not in getmv().classnodes:
            error.error("non-global class '%s'" % node.name, self.gx, node, mv=getmv())
        real_bases = [
            base
            for base in node.bases
            if not (isinstance(base, ast.Name) and base.id == "object")
        ]
        if len(real_bases) > 1:
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

        newclass_context = context.child_with_class(newclass)

        # --- built-in functions
        for ident in ["__setattr__", "__getattr__"]:
            func = python.Function(self.gx, getmv())
            func.ident = ident
            func.parent = newclass

            if ident == "__setattr__":
                func.formals = ["name", "whatsit"]
                function_context = VisitContext(func)
                retexpr = ast.Return(value=None)
                self.visit_Return(retexpr, function_context)
            elif ident == "__getattr__":
                func.formals = ["name"]

            assert newclass
            newclass.funcs[ident] = func
            # XXX: Add newclass_context.write for ast.Name(ident,...)

        newstaticclass = newclass.parent  # TODO copy-paste of above for mypy --strict
        for ident in ["__setattr__", "__getattr__"]:
            func = python.Function(self.gx, getmv())
            func.ident = ident
            func.parent = newstaticclass

            if ident == "__setattr__":
                func.formals = ["name", "whatsit"]
                retexpr = ast.Return(value=None)
                function_context = VisitContext(func)
                self.visit(retexpr, function_context)
            elif ident == "__getattr__":
                func.formals = ["name"]

            assert newstaticclass
            newstaticclass.funcs[ident] = func

        # --- built-in attributes
        if "class_" in getmv().classes or "class_" in getmv().ext_classes:
            var = infer.default_var(self.gx, "__class__", newclass)
            var.invisible = True
            self.gx.types[infer.inode(self.gx, var)] = {
                    (
                        python.def_class(self.gx, "class_"),
                        python.def_class(self.gx, "class_").dcpa,
                    )
            }
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
                    and rvalue.func.id in ["staticmethod", "classmethod", "property"]
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
                    elif rvalue.func.id == "staticmethod":
                        newclass.staticmethods.append(lvalue.id)
                    else:
                        newclass.classmethods.append(lvalue.id)
                    skip.append(child)

        # --- children
        cl = self.classes[node.name]
        class_context = context.child_with_class(cl)
        staticclass_context = context.child_with_class(cl.parent)
        for child in node.body:
            if child not in skip:
                if isinstance(child, ast.FunctionDef):
                    self.visit(child, class_context)
                else:
                    cl.parent.static_nodes.append(child)
                    self.visit(child, staticclass_context)

        # --- __iadd__ etc.
        datetime_class = newclass.mv.module.builtin and newclass.ident in [
            "date",
            "datetime",
            "timedelta",
        ]
        if datetime_class or not newclass.mv.module.builtin or newclass.ident in [
            "int_",
            "float_",
            "str_",
            "tuple",
            "complex",
        ]:
            msgs = ["add", "sub", "mul", "floordiv", "truediv"]
            if newclass.ident == "int_":
                msgs += ["lshift", "rshift", "and", "xor", "or"]
            if datetime_class:  # only the operators these classes have
                msgs = [msg for msg in msgs if "__%s__" % msg in newclass.funcs]
            for msg in msgs:
                method_name = "__i" + msg + "__"
                if method_name not in newclass.funcs:
                    self.visit(
                        ast.parse(
                            "def %s(self, other): return self.__%s__(other)"
                            % (method_name, msg)
                        ).body[0],
                        newclass_context,
                    )
                    newclass.funcs[method_name].invisible = True

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
                newclass_context,
            )
            newclass.funcs["__str__"].invisible = True
        if not newclass.mv.module.builtin and "__hash__" not in newclass.funcs:
            self.visit(
                ast.FunctionDef(
                    "__hash__",
                    make_arg_list(["self"]),
                    [ast.Return(ast.Constant(0))],
                    [],
                ),
                newclass_context,
            )
            newclass.funcs["__hash__"].invisible = True
        # XXX: Should add context.write for ast.Name(node.name,...)

    def visit_Attribute(
        self,
        node: ast.Attribute,
        context: VisitContext,
        callfunc: bool = False,
    ) -> None:
        """Visit an attribute"""
        func: Optional[AllParent] = context.parent_object()

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
                [ast.Constant(node.attr)],
                [],
            )
            self.visit(node.value, context)
            self.visit_Call(fakefunc, context, fake_attr=True)
            self.add_constraint((self.gx.cnode[fakefunc, 0, 0], newnode), func)

            if not callfunc:
                self.fncl_passing(node, newnode, context)
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

    def visit_Constant(self, node: ast.Constant, context: VisitContext) -> None:
        """Visit a constant"""
        func: Optional[AllParent] = context.parent_object()

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
        self, node: ast.AST, newnode: "infer.CNode", context: VisitContext
    ) -> bool:
        """Handle function or class lookup for assignment"""
        lfunc = python.lookup_func(node, getmv())
        lclass = python.lookup_class(node, getmv())
        if lfunc:
            if lfunc.mv.module.builtin:
                lfunc = self.builtin_wrapper(node, context)
            elif lfunc.ident not in lfunc.mv.lambdas:
                lfunc.lambdanr = len(lfunc.mv.lambdas)
                lfunc.mv.lambdas[lfunc.ident] = lfunc
            self.gx.types[newnode] = {(lfunc, 0)}
        elif lclass:
            lclass2: Union["python.Function", "python.StaticClass"]
            if lclass.mv.module.builtin:
                lclass2 = self.builtin_wrapper(node, context)
            else:
                lclass2 = lclass.parent
            self.gx.types[newnode] = {(lclass2, 0)}
        else:
            return False
        newnode.copymetoo = True  # XXX merge into some kind of 'seeding' function
        return True

    def visit_Name(self, node: ast.Name, context: VisitContext) -> None:
        """Visit a name"""
        func: Optional[AllParent] = context.parent_object()

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

            if (
                isinstance(func, (python.Function, python.Class))
                and node.id in func.globals
            ):
                var = infer.default_var(self.gx, node.id, None, mv=getmv())
                self.add_constraint((infer.inode(self.gx, var), newnode), func)
            else:
                var = python.lookup_var(node.id, func, getmv())
                if not var:
                    if self.fncl_passing(node, newnode, context):
                        pass
                    elif node.id in ["int", "float", "str"]:  # XXX
                        cl = self.ext_classes[node.id + "_"]
                        self.gx.types[newnode] = {(cl.parent, 0)}
                        newnode.copymetoo = True
                    else:
                        var = infer.default_var(self.gx, node.id, None, mv=getmv())
                if var:
                    context.read(getmv(), node)

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
        self, node: ast.AST, context: VisitContext
    ) -> "python.Function":
        """Create a wrapper for a builtin function"""
        assert isinstance(node, ast.expr)
        node2 = ast.Call(
            copy.deepcopy(node), [ast.Name(x, ast.Load()) for x in "abcde"], []
        )
        lam = ast.Lambda(make_arg_list(list("abcde")), node2)
        self.visit_Lambda(lam, context)
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
        source_root = gx.source_root or pathlib.Path.cwd()
        if parent and parent.path != source_root:
            basepaths = [parent.path, source_root]
        else:
            basepaths = [source_root]
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

    module_context = VisitContext(module)
    mv.visit(module.ast, module_context)
    module.import_order = gx.import_order
    gx.import_order += 1

    try:
        mv = old_mv
        setmv(mv)
    except NameError:
        pass

    return module
