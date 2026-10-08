# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2025 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.loopidiom: which loops qualify for the append
idiom (one 'l.append(x)' per iteration, see __append_reserve)."""

import ast
import textwrap

from shedskin import loopidiom


def appends(src: str) -> list[tuple[str, int]]:
    loop = ast.parse(textwrap.dedent(src)).body[0]
    assert isinstance(loop, ast.For)
    return [(ast.unparse(lst), count) for _, lst, count in loopidiom.append_idioms(loop)]


def test_single_append():
    assert appends("""
        for i in range(10):
            x = i * 2
            l.append(x)
    """) == [("l", 1)]


def test_several_lists():
    assert appends("""
        for i in range(10):
            a.append(i)
            self.b.append(i)
            a.append(-i)
    """) == [("a", 2), ("self.b", 1)]


def test_conditional_append():
    assert appends("""
        for i in range(10):
            if i % 2:
                l.append(i)
    """) == []


def test_early_exits():
    for stmt in ["break", "continue", "return", "yield i"]:
        assert appends(f"""
            for i in range(10):
                l.append(i)
                if i == 5:
                    {stmt}
        """) == [], stmt


def test_nested_loop_exits():
    # break/continue in a nested loop apply to that loop
    assert appends("""
        for i in range(10):
            l.append(i)
            for j in range(i):
                if j:
                    break
                continue
            while True:
                break
    """) == [("l", 1)]
    # .. but not in its else clause
    assert appends("""
        for i in range(10):
            l.append(i)
            for j in range(i):
                pass
            else:
                continue
    """) == []
    # return always leaves the loop
    assert appends("""
        for i in range(10):
            l.append(i)
            for j in range(i):
                return
    """) == []


def test_nested_scopes():
    assert appends("""
        for i in range(10):
            l.append(i)
            def f():
                return 1
            g = lambda: 2
    """) == [("l", 1)]


def test_raise_and_else():
    # exceptions are not considered, and else runs after the loop
    assert appends("""
        for i in range(10):
            l.append(i)
            if i > 10:
                raise ValueError
        else:
            pass
    """) == [("l", 1)]


def test_not_an_append():
    assert appends("""
        for i in range(10):
            l.append(*x)
            l.append(i, j)
            l.extend([i])
            y = l.append(i)
    """) == []
