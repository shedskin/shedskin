# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.escape: escape analysis for local container literals

This is a *diagnostic-only* first pass towards stack-allocating container
literals (see issue #363). It does not change code generation in any way; it
only reports, per module/function, which list literals provably do not
escape the frame they are created in, and why the ones that might escape are
considered unsafe.

Approach
--------
For each function (and the module top-level), we build a small directed
graph while walking the AST:

- every `list` literal (`ast.List` in `Load` context) becomes a node ("literal")
- every local variable that a literal (or another tracked variable) is
  assigned to becomes a node ("var")
- assignments, returns, stores to attributes/subscripts/globals, calls, and
  so on add edges or directly mark a node as "escaping"

Once the graph for a scope is built, escaping is flood-filled backwards: if
a node has an edge to something that escapes, the node escapes too. A
literal survives (is a stack-allocation candidate) only if nothing it can
reach ever escapes.

This is deliberately conservative in every direction that matters for
correctness: anything not explicitly recognized as safe is treated as
escaping. Getting this wrong in the "doesn't escape" direction would be a
correctness bug once this feeds into code generation; getting it wrong in
the "escapes" direction just means a missed optimization. So:

- only direct `ast.Name` aliasing is tracked (`x = [1, 2, 3]`); anything
  else flowing into a variable (a call result, a binop, a subscript, ...)
  is simply not tracked, so that variable's literal-ness is unknown and any
  literal already reachable through it is left alone (not spuriously
  cleared)
- only a small allowlist of builtins that are known to read their argument
  without stashing a reference anywhere (`SAFE_CONSUMING_BUILTINS`) are
  treated as non-escaping call sites; every other call is an escape
- tuple/list-unpacking targets, closures (nonlocal/global), attribute and
  subscript stores, returns, and yields are all treated as escaping
- list comprehensions (`[... for ... in ...]`) are tracked the same way as
  list literals: the comprehension itself is a "literal" node, its
  generator sources are consumed locally (iterating over something does
  not make it escape, the same as `SAFE_CONSUMING_BUILTINS`), and a
  literal/comprehension directly in the element position is treated as
  escaping, the same as a list literal nested inside another list literal

Later iterations can relax these one at a time (e.g. track `sorted()`,
`reversed()`, set/dict comprehensions, or trace values through more
expression kinds) without changing the overall shape of the graph.

Usage
-----
Enabled with `--stack` on `translate`/`build`/`run`/`analyze`. Runs
after parsing, prints a report, and does not otherwise affect compilation.
"""

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from . import ast_utils

if TYPE_CHECKING:
    from . import config

# --- builtins that consume an iterable argument locally (read elements
# during the call) and are known to never retain a reference to the
# argument object itself. Conservative allowlist: extend only after
# verifying the implementation doesn't stash the object anywhere.
SAFE_CONSUMING_BUILTINS = {
    "sum",
    "len",
    "min",
    "max",
    "any",
    "all",
}


def _callee_name(func: ast.expr) -> str:
    """Best-effort human-readable name of a call target, for messages."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return "<call>"


@dataclass
class EscapeNode:
    """A single node in a scope's escape graph.

    `key` identifies the node: `id(ast.List-node)` for literals, or
    `(scope_name, varname)` for local variables.
    """

    key: Any
    kind: str  # "literal" or "var"
    lineno: Optional[int] = None
    escapes: bool = False
    escape_reason: Optional[str] = None
    edges: set = field(default_factory=set)  # -> other node keys


class EscapeGraph:
    """Escape graph for a single function (or module top-level) scope."""

    def __init__(self, name: str):
        self.name = name
        self.nodes: dict[Any, EscapeNode] = {}
        self.literals: list[ast.List] = []

    def node(self, key: Any, kind: str, lineno: Optional[int] = None) -> EscapeNode:
        n = self.nodes.get(key)
        if n is None:
            n = EscapeNode(key=key, kind=kind, lineno=lineno)
            self.nodes[key] = n
        return n

    def add_edge(self, src_key: Any, dst_key: Any) -> None:
        if src_key in self.nodes and dst_key in self.nodes:
            self.nodes[src_key].edges.add(dst_key)

    def mark_escape(self, key: Any, reason: str) -> None:
        n = self.nodes.get(key)
        if n is not None and not n.escapes:
            n.escapes = True
            n.escape_reason = reason

    def propagate(self) -> None:
        """Flood-fill escaping backwards across edges until fixpoint."""
        changed = True
        while changed:
            changed = False
            for n in self.nodes.values():
                if n.escapes:
                    continue
                for dst_key in n.edges:
                    dst = self.nodes.get(dst_key)
                    if dst is not None and dst.escapes:
                        self.mark_escape(n.key, f"flows to escaping {dst.kind}")
                        changed = True
                        break


@dataclass
class EscapeReport:
    """One reported list literal and its escape verdict."""

    module: str
    scope: str
    lineno: Optional[int]
    escapes: bool
    reason: Optional[str]


class EscapeVisitor(ast_utils.BaseNodeVisitor):
    """Builds one EscapeGraph per function (and the module top-level)."""

    def __init__(self, gx: "config.GlobalInfo"):
        self.gx = gx
        self.graphs: list[EscapeGraph] = []
        self.graph: Optional[EscapeGraph] = None
        self.nonlocal_names: set[str] = set()

    # --- scopes -----------------------------------------------------------

    def _enter_scope(self, name: str, node: ast.AST) -> None:
        outer_graph, outer_nonlocal = self.graph, self.nonlocal_names
        self.graph = EscapeGraph(name)
        self.nonlocal_names = set()
        self.generic_visit(node)
        self.graph.propagate()
        self.graphs.append(self.graph)
        self.graph, self.nonlocal_names = outer_graph, outer_nonlocal

    def visit_Module(self, node: ast.Module) -> None:
        self._enter_scope("<module>", node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._enter_scope(node.name, node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        # lambdas can only return a single expression; not yet analyzed
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        self.nonlocal_names.update(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.nonlocal_names.update(node.names)

    # --- literals -----------------------------------------------------------

    def visit_List(self, node: ast.List) -> None:
        if not isinstance(node.ctx, ast.Load):
            self.generic_visit(node)
            return
        assert self.graph is not None
        self.graph.node(id(node), "literal", lineno=getattr(node, "lineno", None))
        self.graph.literals.append(node)
        for elt in node.elts:
            self.visit(elt)
            if isinstance(elt, (ast.List, ast.ListComp)):
                self.graph.mark_escape(id(elt), "nested inside another list literal")

    def visit_ListComp(self, node: ast.ListComp) -> None:
        assert self.graph is not None
        self.graph.node(id(node), "literal", lineno=getattr(node, "lineno", None))
        self.graph.literals.append(node)
        # comprehensions introduce their own scope in real Python, but for
        # this rudimentary analysis we don't yet model that separately; we
        # only need to know whether the *result* list escapes, and whether
        # its sources/element expression do
        for gen in node.generators:
            self.visit(gen.iter)
            # iterating over something in a comprehension just reads its
            # elements locally, it is never stashed anywhere -- the same
            # non-escaping treatment as SAFE_CONSUMING_BUILTINS, so we
            # deliberately do *not* call _mark_value_escape here
            for if_ in gen.ifs:
                self.visit(if_)
        self.visit(node.elt)
        if isinstance(node.elt, (ast.List, ast.ListComp)):
            self.graph.mark_escape(
                id(node.elt), "nested inside comprehension result"
            )

    # --- assignment / aliasing -----------------------------------------------

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        for target in node.targets:
            self._handle_target(target, node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self.visit(node.value)
            self._handle_target(node.target, node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        assert self.graph is not None
        self.visit(node.value)
        # combines with the *previous* value of the target: conservatively
        # treat both sides as escaping rather than tracing in-place update
        self._mark_value_escape(node.value, "augmented assignment")
        if isinstance(node.target, ast.Name):
            self.graph.mark_escape(
                (self.graph.name, node.target.id), "augmented assignment"
            )

    def _handle_target(self, target: ast.AST, value: ast.expr) -> None:
        assert self.graph is not None
        if isinstance(target, ast.Name):
            if self.graph.name == "<module>":
                # a name bound at module top level is an implicit global:
                # every function in the module can read it for the whole
                # program lifetime, whether or not it says `global`
                self._mark_value_escape(value, "assigned to module-level global")
                return
            if target.id in self.nonlocal_names:
                self._mark_value_escape(
                    value, f"assigned to global/nonlocal '{target.id}'"
                )
                return
            var_key = (self.graph.name, target.id)
            self.graph.node(var_key, "var")
            self._connect_value(value, var_key)
        elif isinstance(target, (ast.Tuple, ast.List)):
            # unpacking assignment: not yet traced element-wise
            self._mark_value_escape(value, "tuple/list unpacking (not yet analyzed)")
        else:
            # ast.Attribute / ast.Subscript / ast.Starred store
            self._mark_value_escape(
                value, f"stored to {type(target).__name__.lower()}"
            )

    def _connect_value(self, value: ast.expr, dst_key: Any) -> None:
        """If `value` is a tracked literal or variable, add an edge to dst_key."""
        assert self.graph is not None
        if isinstance(value, (ast.List, ast.ListComp)):
            self.graph.add_edge(id(value), dst_key)
        elif isinstance(value, ast.Name):
            src_key = (self.graph.name, value.id)
            self.graph.add_edge(src_key, dst_key)
        # any other expression kind (call, binop, subscript, ...): not
        # traced in v1, so dst_key just starts out as an ordinary,
        # non-escaping var node until/unless something else marks it

    def _mark_value_escape(self, value: ast.expr, reason: str) -> None:
        assert self.graph is not None
        if isinstance(value, (ast.List, ast.ListComp)):
            self.graph.mark_escape(id(value), reason)
        elif isinstance(value, ast.Name):
            self.graph.mark_escape((self.graph.name, value.id), reason)

    # --- exits from the scope -----------------------------------------------

    def visit_Return(self, node: ast.Return) -> None:
        if node.value is not None:
            self.visit(node.value)
            self._mark_value_escape(node.value, "returned from function")

    def visit_Yield(self, node: ast.Yield) -> None:
        if node.value is not None:
            self.visit(node.value)
            self._mark_value_escape(node.value, "yielded")

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        self.visit(node.value)
        self._mark_value_escape(node.value, "yielded")

    # --- calls: the one place we currently allow a "safe" non-escaping use --

    def visit_Call(self, node: ast.Call) -> None:
        self.visit(node.func)
        func = node.func
        is_safe_sink = (
            isinstance(func, ast.Name)
            and func.id in SAFE_CONSUMING_BUILTINS
            and len(node.args) == 1
            and not node.keywords
            and not isinstance(node.args[0], ast.Starred)
        )
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                self.visit(arg.value)
                self._mark_value_escape(arg.value, "starred call argument")
                continue
            self.visit(arg)
            if not is_safe_sink:
                self._mark_value_escape(
                    arg, f"passed to '{_callee_name(func)}(...)'"
                )
            # else: e.g. sum([1, 2, 3]) -- read locally, does not escape
        for kw in node.keywords:
            self.visit(kw.value)
            self._mark_value_escape(kw.value, "passed as keyword argument")


# --- entry point -------------------------------------------------------------


def analyze(gx: "config.GlobalInfo") -> list[EscapeReport]:
    """Run escape analysis over all non-builtin modules and print a report."""
    reports: list[EscapeReport] = []
    for module in gx.modules.values():
        if module.builtin or module.ast is None:
            continue
        visitor = EscapeVisitor(gx)
        visitor.visit(module.ast)
        for scope_graph in visitor.graphs:
            for literal in scope_graph.literals:
                node = scope_graph.nodes[id(literal)]
                reports.append(
                    EscapeReport(
                        module=module.ident,
                        scope=scope_graph.name,
                        lineno=getattr(literal, "lineno", None),
                        escapes=node.escapes,
                        reason=node.escape_reason,
                    )
                )
    print_report(reports)
    return reports


def print_report(reports: list[EscapeReport]) -> None:
    """Print a human-readable escape-analysis report."""
    if not reports:
        print("\n[escape analysis: no list literals found]")
        return

    print("\n[escape analysis]")
    n_stack, n_heap = 0, 0
    for r in sorted(reports, key=lambda r: (r.module, r.lineno or 0)):
        loc = f"{r.module}:{r.lineno}" if r.lineno is not None else r.module
        if r.escapes:
            n_heap += 1
            print(f"  {loc:<30} in {r.scope:<20} HEAP  ({r.reason})")
        else:
            n_stack += 1
            print(f"  {loc:<30} in {r.scope:<20} STACK")
    print(f"\n  {n_stack} of {n_stack + n_heap} list literal(s) do not escape their frame\n")
