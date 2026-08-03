# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.strbuild: recognize loops that only append to a local string

A loop of the shape

    out = ''
    for x in xs:
        out += f(x)

is quadratic in shed skin. Strings are immutable, so each '+=' allocates a
fresh str and copies both operands; over n iterations that copies O(n**2)
bytes. CPython does not have this problem because it resizes the left operand
in place whenever it holds the only reference to it. Shed skin has no reference
counts to consult at run time, so the equivalent question is answered at
compile time instead: if the accumulator is a local that the loop touches
*only* as the target of '+=', then nothing can observe it while the loop runs,
and codegen is free to append into a single buffer and publish the result once,
after the loop.

`loop_accumulators` reports the loops in a function for which that holds. The
codegen side lives in `cpp.GenerateVisitor.sb_begin`/`sb_end`.

The conditions are deliberately conservative; each one exists because dropping
it makes an observable difference:

- Every occurrence of the name in the loop, header included, must be an
  augmented-assignment target. A read would see the accumulator's pre-loop
  value, which is stale. This also rules out `out += out`, and rules out the
  `while` test re-reading it on each iteration.
- The loop may not sit inside a `try` in the same function. If an exception
  escapes the loop, python leaves the accumulator holding everything appended
  so far, whereas a builder would not have published anything yet.
- The loop may not have an `else` clause, which would run before the value is
  published.
- The function may not be a generator, whose locals survive across yields.

Loops nested inside a qualifying loop are left alone: the outermost one already
covers them, and transforming both would publish (and copy) once per outer
iteration.
"""

import ast
from typing import TYPE_CHECKING, Any, NamedTuple

from . import python

if TYPE_CHECKING:
    from . import config


class Accumulator(NamedTuple):
    """A local string a loop only ever appends to"""

    name: str
    """name of the accumulated variable"""

    augassigns: list[ast.AugAssign]
    """the '+=' statements to rewrite into appends"""


Types = Any
Accumulators = dict[ast.stmt, list[Accumulator]]


def loop_accumulators(
    func: "python.Function", gx: "config.GlobalInfo", mergeinh: dict[Any, Types]
) -> Accumulators:
    """Map each qualifying loop in func to the string it accumulates"""
    result: Accumulators = {}
    fnode = func.node
    if fnode is None or func.isGenerator or func.listcomp:
        return result
    if not isinstance(fnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return result
    _scan(list(fnode.body), func, gx, mergeinh, _loops_under_try(fnode), result)
    return result


def _scan(
    stmts: list[ast.stmt],
    func: "python.Function",
    gx: "config.GlobalInfo",
    mergeinh: dict[Any, Types],
    disqualified: set[ast.stmt],
    result: Accumulators,
) -> None:
    """Claim the outermost qualifying loop along each path"""
    for stmt in stmts:
        if isinstance(stmt, (ast.For, ast.While)) and stmt not in disqualified:
            accs = _accumulators(stmt, func, gx, mergeinh)
            if accs:
                result[stmt] = accs
                continue  # nested loops are already covered by this one
        for child in ast.iter_child_nodes(stmt):
            if isinstance(child, ast.stmt):
                _scan([child], func, gx, mergeinh, disqualified, result)
            elif isinstance(child, ast.ExceptHandler):
                _scan(list(child.body), func, gx, mergeinh, disqualified, result)


def _loops_under_try(fnode: ast.AST) -> set[ast.stmt]:
    """Loops sitting inside a 'try' in this function"""
    inside: set[ast.stmt] = set()
    for node in ast.walk(fnode):
        if isinstance(node, ast.Try):
            for child in ast.walk(node):
                if isinstance(child, (ast.For, ast.While)):
                    inside.add(child)
    return inside


def _accumulators(
    loop: ast.stmt,
    func: "python.Function",
    gx: "config.GlobalInfo",
    mergeinh: dict[Any, Types],
) -> list[Accumulator]:
    """The strings this loop only ever appends to"""
    found: list[Accumulator] = []
    if getattr(loop, "orelse", None):
        return found

    candidates: dict[str, list[ast.AugAssign]] = {}
    for node in ast.walk(loop):
        if (
            isinstance(node, ast.AugAssign)
            and isinstance(node.op, ast.Add)
            and isinstance(node.target, ast.Name)
            and _is_str(gx, mergeinh, node.value)
        ):
            candidates.setdefault(node.target.id, []).append(node)

    for name, augassigns in candidates.items():
        if name in func.globals or name not in func.vars:
            continue
        # the target is in Store context and so carries no type of its own;
        # the accumulator's type lives on the variable
        if not _is_str(gx, mergeinh, func.vars[name]):
            continue
        targets = {id(aug.target) for aug in augassigns}
        if all(
            id(node) in targets
            for node in ast.walk(loop)
            if isinstance(node, ast.Name) and node.id == name
        ):
            found.append(Accumulator(name, augassigns))
    return found


def _is_str(gx: "config.GlobalInfo", mergeinh: dict[Any, Types], thing: Any) -> bool:
    """Whether an ast node's or variable's inferred type is exactly str"""
    return mergeinh.get(thing) == {(python.def_class(gx, "str_"), 0)}
