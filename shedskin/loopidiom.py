# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2025 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)
"""shedskin.loopidiom: loop idiom recognition

Finds common patterns ('idioms') in loops, that code generation can then
implement more efficiently (compare LLVM's LoopIdiomRecognize pass). This
module only looks at the syntax, and decides which loops qualify; type checks
and the actual code generation are done by cpp.py.

Idioms:

- append: 'for i in range(..): .. l.append(x) ..', where the append is done
  exactly once per iteration. Once the list has to grow, room can be made
  for the remaining iterations at once (__append_reserve).
"""

import ast
from typing import Union


def _exits(node: ast.AST, in_loop: bool) -> bool:
    """Whether 'node' may leave the current loop iteration early, apart from
    exceptions. 'in_loop': inside a nested loop, where break/continue apply"""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
        return False
    if isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom, ast.Await)):
        return True
    if isinstance(node, (ast.Break, ast.Continue)):
        return not in_loop
    if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
        # break/continue in a nested loop apply to that loop, except in its else clause
        return any(_exits(child, True) for child in node.body) or any(
            _exits(child, in_loop)
            for child in ast.iter_child_nodes(node)
            if not any(child is stmt for stmt in node.body)
        )
    return any(_exits(child, in_loop) for child in ast.iter_child_nodes(node))


def completes_iterations(loop: Union[ast.For, ast.While]) -> bool:
    """Whether each iteration of a loop always runs its whole body (unless
    an exception is raised): no break, continue, return or yield"""
    return not any(_exits(stmt, False) for stmt in loop.body)


def append_idioms(loop: ast.For) -> list[tuple[ast.Expr, ast.expr, int]]:
    """Find 'l.append(x)' statements done once per iteration of a loop, as
    (statement, list expression, number of such appends to the same list)"""
    if not completes_iterations(loop):
        return []

    appends: list[tuple[ast.Expr, ast.expr]] = []
    for stmt in loop.body:
        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute)
            and stmt.value.func.attr == "append"
            and len(stmt.value.args) == 1
            and not stmt.value.keywords
            and not isinstance(stmt.value.args[0], ast.Starred)
        ):
            appends.append((stmt, stmt.value.func.value))

    counts: dict[str, int] = {}
    for _, lst in appends:
        key = ast.dump(lst)
        counts[key] = counts.get(key, 0) + 1

    # reserve once per list, at its first append
    result = []
    seen: set[str] = set()
    for stmt, lst in appends:
        key = ast.dump(lst)
        if key not in seen:
            seen.add(key)
            result.append((stmt, lst, counts[key]))
    return result
