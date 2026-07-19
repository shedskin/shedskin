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
- every function parameter is *also* pre-registered as a "var" node in its
  own function's graph (whether or not it is ever assigned), so that we can
  later ask "did this specific parameter escape through this function
  body?" and reuse the answer at every call site that passes an argument
  into it
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
- a small allowlist of builtins that are known to read their argument
  without stashing a reference anywhere (`SAFE_CONSUMING_BUILTINS`) are
  treated as non-escaping call sites unconditionally
- calls to *ordinary user-defined functions* (module-level `def`s with only
  plain positional parameters -- no `*args`/`**kwargs`/keyword-only/
  positional-only params, and called without keyword arguments) are also
  potentially safe, per argument position: interprocedurally, we compute
  whether each function's own parameters ever escape *through that
  function's body*, and reuse that per-position verdict at every call site.
  This is a whole-module fixpoint (see `analyze`): start by assuming no
  user function is safe in any position (matching the old, fully
  conservative behavior), analyze every function, derive a new safety
  verdict per (function, parameter position) from what was actually proven
  in that pass, and repeat with the refined assumptions until nothing
  changes. Recursive and mutually-recursive functions fall out naturally:
  if a parameter's only interesting use is being forwarded unchanged to
  other calls whose safety is still unknown, it stays conservatively
  "escaping" for that round and gets a chance to be re-examined (with
  better information) on the next one; a genuinely-recursive parameter
  that is never actually the thing forwarded (e.g. a *derived copy* is
  passed to the recursive call instead of the parameter itself) can still
  be proven safe once the calls it depends on are.
- every other call is an escape for arguments not covered by either of the
  above
- tuple/list-unpacking *assignment targets*, closures (nonlocal/global),
  attribute and subscript stores, and yields are all treated as escaping;
  `return`/`yield` of a bare `ast.Tuple` recurses element-wise (so
  `return x, some_list` still marks `some_list`, without needing to track
  tuples as containers in their own right)
- list comprehensions (`[... for ... in ...]`) are tracked the same way as
  list literals: the comprehension itself is a "literal" node, its
  generator sources are consumed locally (iterating over something does
  not make it escape, the same as `SAFE_CONSUMING_BUILTINS`), and a
  literal/comprehension directly in the element position gets an edge to
  its enclosing literal/comprehension (nested containers only escape if
  the container holding them does -- being nested is not, by itself, an
  escape)

Later iterations can relax these one at a time (e.g. track `sorted()`,
`reversed()`, set/dict comprehensions, attribute/subscript-store targets,
or trace values through more expression kinds) without changing the
overall shape of the graph.

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

# safety cap on the interprocedural fixpoint below; real programs converge
# in far fewer rounds than this (each round can only ever *add* safe
# positions, over a finite number of (function, parameter) pairs, so this
# is just a defensive bound against a bug turning it into an infinite loop)
MAX_INTERPROCEDURAL_ROUNDS = 50

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


def _simple_function_params(node: "ast.FunctionDef | ast.AsyncFunctionDef") -> Optional[list[str]]:
    """Positional parameter names for `node`, or None if it has any
    parameter kind we don't reason about interprocedurally (*args,
    **kwargs, keyword-only, or positional-only params). Defaults are fine
    -- we only match call sites by position, not by how a parameter ends
    up bound."""
    a = node.args
    if a.vararg or a.kwarg or a.kwonlyargs or a.posonlyargs:
        return None
    return [arg.arg for arg in a.args]


def _collect_simple_functions(module_ast: ast.Module) -> dict[str, "ast.FunctionDef | ast.AsyncFunctionDef"]:
    """Map name -> def node, for module-level functions simple enough for
    the interprocedural per-parameter safety check below."""
    funcs: dict[str, "ast.FunctionDef | ast.AsyncFunctionDef"] = {}
    for node in module_ast.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _simple_function_params(node) is not None:
                funcs[node.name] = node
    return funcs


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

    def __init__(
        self,
        gx: "config.GlobalInfo",
        known_funcs: Optional[dict[str, "ast.FunctionDef | ast.AsyncFunctionDef"]] = None,
        safe_positions: Optional[dict[str, set]] = None,
    ):
        self.gx = gx
        self.graphs: list[EscapeGraph] = []
        self.graph: Optional[EscapeGraph] = None
        self.nonlocal_names: set[str] = set()
        # interprocedural context for this round (see `analyze`): which
        # user functions we're allowed to reason about at all, and which
        # (function, positional-arg-index) pairs are currently *known* not
        # to escape through that function's body, as of the previous round
        self.known_funcs = known_funcs or {}
        self.safe_positions: dict[str, set] = safe_positions or {}

    # --- scopes -----------------------------------------------------------

    def _enter_scope(self, name: str, node: ast.AST, params: Optional[list[str]] = None) -> None:
        outer_graph, outer_nonlocal = self.graph, self.nonlocal_names
        self.graph = EscapeGraph(name)
        self.nonlocal_names = set()
        # pre-register parameters as var nodes *before* walking the body,
        # whether or not the body ever assigns to them, so that a
        # parameter which is simply never touched in an escaping way ends
        # up with a real (non-escaping) node rather than no node at all
        for p in params or ():
            self.graph.node((name, p), "var")
        self.generic_visit(node)
        self.graph.propagate()
        self.graphs.append(self.graph)
        self.graph, self.nonlocal_names = outer_graph, outer_nonlocal

    def visit_Module(self, node: ast.Module) -> None:
        self._enter_scope("<module>", node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._enter_scope(node.name, node, params=_simple_function_params(node))

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
                # a nested literal is *stored as an element* of the outer
                # one: it escapes exactly when the outer container does,
                # no more and no less, so this is an edge (propagated by
                # EscapeGraph.propagate), not an unconditional escape
                self.graph.add_edge(id(elt), id(node))

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
            # same reasoning as visit_List above: nested, not escaping
            self.graph.add_edge(id(node.elt), id(node))

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
        elif isinstance(value, ast.Tuple):
            # a bare tuple isn't itself tracked as a container, but each of
            # its elements is exposed exactly as much as the tuple is (e.g.
            # `return x, some_list` still exposes `some_list`), so recurse
            # instead of silently doing nothing for the Tuple case
            for elt in value.elts:
                self._mark_value_escape(elt, reason)

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

    # --- calls: builtins and (once proven safe) ordinary user functions ----

    def visit_Call(self, node: ast.Call) -> None:
        self.visit(node.func)
        func = node.func
        callee_name = func.id if isinstance(func, ast.Name) else None

        is_safe_builtin_call = (
            callee_name in SAFE_CONSUMING_BUILTINS
            and len(node.args) == 1
            and not node.keywords
            and not isinstance(node.args[0], ast.Starred)
        )

        # per-argument-position safety for calls to ordinary user
        # functions, from the previous round's interprocedural fixpoint
        # (see `analyze`). Keyword arguments make position-matching
        # unreliable, so those calls stay fully conservative.
        user_safe_positions: set = set()
        if callee_name is not None and callee_name in self.known_funcs and not node.keywords:
            user_safe_positions = self.safe_positions.get(callee_name, set())

        for i, arg in enumerate(node.args):
            if isinstance(arg, ast.Starred):
                self.visit(arg.value)
                self._mark_value_escape(arg.value, "starred call argument")
                continue
            self.visit(arg)
            safe_here = is_safe_builtin_call or i in user_safe_positions
            if not safe_here:
                self._mark_value_escape(
                    arg, f"passed to '{_callee_name(func)}(...)'"
                )
            # else: e.g. sum([1, 2, 3]) or a call into a parameter position
            # already proven not to escape -- read locally, does not escape
        for kw in node.keywords:
            self.visit(kw.value)
            self._mark_value_escape(kw.value, "passed as keyword argument")


# --- entry point -------------------------------------------------------------


def _param_safety_from_round(
    graphs: list[EscapeGraph],
    func_param_names: dict[str, list[str]],
) -> dict[str, set]:
    """From one round's per-function graphs, extract which (function,
    positional-index) parameters were actually proven not to escape in
    that round -- i.e. this round's *output* facts, which become next
    round's input assumptions."""
    by_name = {g.name: g for g in graphs}
    result: dict[str, set] = {}
    for name, params in func_param_names.items():
        safe_here: set = set()
        g = by_name.get(name)
        if g is not None:
            for i, p in enumerate(params):
                node = g.nodes.get((name, p))
                # every parameter is pre-registered in _enter_scope, so
                # `node` should always exist; a parameter that nothing in
                # the body ever marked escaping is non-escaping
                if node is None or not node.escapes:
                    safe_here.add(i)
        result[name] = safe_here
    return result


def _analyze_module(gx: "config.GlobalInfo", module: Any) -> list[EscapeGraph]:
    """Run the whole-module interprocedural fixpoint for one module and
    return the final round's per-function graphs.

    Round 0 assumes no user function is safe in any parameter position
    (identical to the original, fully call-conservative behavior). Each
    round derives, from what was *actually* proven that round, a new set
    of (function, position) facts; since assuming more safety can only
    ever let a later round prove at least as much (never less), the set
    of known-safe positions only grows round over round, so this
    converges to a fixpoint (bounded by the finite number of
    (function, position) pairs in the module).
    """
    funcs = _collect_simple_functions(module.ast)
    func_param_names = {name: _simple_function_params(f) or [] for name, f in funcs.items()}

    safe_positions: dict[str, set] = {name: set() for name in funcs}
    graphs: list[EscapeGraph] = []

    for _ in range(MAX_INTERPROCEDURAL_ROUNDS):
        visitor = EscapeVisitor(gx, known_funcs=funcs, safe_positions=safe_positions)
        visitor.visit(module.ast)
        graphs = visitor.graphs

        new_safe_positions = _param_safety_from_round(graphs, func_param_names)
        if new_safe_positions == safe_positions:
            break
        safe_positions = new_safe_positions

    return graphs


def analyze(gx: "config.GlobalInfo") -> list[EscapeReport]:
    """Run escape analysis over all non-builtin modules and print a report."""
    reports: list[EscapeReport] = []
    for module in gx.modules.values():
        if module.builtin or module.ast is None:
            continue
        for scope_graph in _analyze_module(gx, module):
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
