# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.strbuild module."""

import argparse
import ast

import pytest

from shedskin import graph, python, strbuild
from shedskin.config import GlobalInfo


@pytest.fixture
def gx():
    """GlobalInfo with the builtin module loaded, so def_class('str_') works."""
    options = argparse.Namespace()
    info = GlobalInfo(options)
    graph.parse_module("builtin", info)
    return info


def analyze(gx, source, str_vars=("out", "a", "b", "total"), is_generator=False):
    """Run loop_accumulators over the single function in `source`.

    The real pipeline supplies types via inference; here the variables named in
    `str_vars` are simply declared to be strings, which is what the analysis
    actually consults.
    """
    tree = ast.parse(source)
    fnode = tree.body[0]
    assert isinstance(fnode, ast.FunctionDef)

    func = python.Function(gx, node=fnode, mv=gx.modules["builtin"].mv)
    func.isGenerator = is_generator
    # graph.ModuleVisitor.visit_Global does this during the real pipeline
    for node in ast.walk(fnode):
        if isinstance(node, ast.Global):
            func.globals += node.names

    str_class = python.def_class(gx, "str_")
    mergeinh = {}
    for name in str_vars:
        var = python.Variable(name, func)
        func.vars[name] = var
        mergeinh[var] = {(str_class, 0)}
    # every '+=' right-hand side in these fixtures is a string
    for node in ast.walk(fnode):
        if isinstance(node, ast.AugAssign):
            mergeinh[node.value] = {(str_class, 0)}

    return strbuild.loop_accumulators(func, gx, mergeinh)


def accumulated_names(result):
    """Flatten the analysis result to the set of accumulated variable names."""
    return {acc.name for accs in result.values() for acc in accs}


class TestQualifying:
    """Loops the rewrite applies to"""

    def test_simple_for(self, gx):
        result = analyze(gx, "def f():\n out = ''\n for i in r:\n  out += 'x'\n")
        assert accumulated_names(result) == {"out"}

    def test_simple_while(self, gx):
        result = analyze(gx, "def f():\n out = ''\n while c:\n  out += 'x'\n")
        assert accumulated_names(result) == {"out"}

    def test_two_accumulators(self, gx):
        result = analyze(
            gx, "def f():\n for i in r:\n  a += 'x'\n  b += 'y'\n"
        )
        assert accumulated_names(result) == {"a", "b"}

    def test_conditional_append(self, gx):
        result = analyze(
            gx, "def f():\n for i in r:\n  if i:\n   out += 'x'\n"
        )
        assert accumulated_names(result) == {"out"}

    def test_break_and_continue_allowed(self, gx):
        result = analyze(
            gx,
            "def f():\n for i in r:\n  if i:\n   continue\n  if j:\n   break\n  out += 'x'\n",
        )
        assert accumulated_names(result) == {"out"}

    def test_reads_after_loop_allowed(self, gx):
        result = analyze(
            gx, "def f():\n for i in r:\n  out += 'x'\n return out\n"
        )
        assert accumulated_names(result) == {"out"}

    def test_try_inside_loop_allowed(self, gx):
        # only the loop being *inside* a try is a problem
        result = analyze(
            gx,
            "def f():\n for i in r:\n  try:\n   g()\n  except E:\n   pass\n  out += 'x'\n",
        )
        assert accumulated_names(result) == {"out"}


class TestDisqualifying:
    """Loops the rewrite must stay away from"""

    def test_read_inside_loop(self, gx):
        result = analyze(
            gx, "def f():\n for i in r:\n  out += 'x'\n  print(out)\n"
        )
        assert result == {}

    def test_self_append(self, gx):
        result = analyze(gx, "def f():\n for i in r:\n  out += out\n")
        assert result == {}

    def test_reassigned_inside_loop(self, gx):
        result = analyze(
            gx, "def f():\n for i in r:\n  out += 'x'\n  out = 'r'\n"
        )
        assert result == {}

    def test_while_test_reads_accumulator(self, gx):
        result = analyze(gx, "def f():\n while len(out) < 3:\n  out += 'x'\n")
        assert result == {}

    def test_read_in_for_iter(self, gx):
        result = analyze(gx, "def f():\n for c in out:\n  out += 'x'\n")
        assert result == {}

    def test_loop_inside_try(self, gx):
        result = analyze(
            gx,
            "def f():\n try:\n  for i in r:\n   out += 'x'\n except E:\n  pass\n",
        )
        assert result == {}

    def test_for_else(self, gx):
        result = analyze(
            gx, "def f():\n for i in r:\n  out += 'x'\n else:\n  pass\n"
        )
        assert result == {}

    def test_generator(self, gx):
        result = analyze(
            gx, "def f():\n for i in r:\n  out += 'x'\n  yield 1\n", is_generator=True
        )
        assert result == {}

    def test_global_accumulator(self, gx):
        result = analyze(
            gx, "def f():\n global out\n for i in r:\n  out += 'x'\n"
        )
        assert result == {}

    def test_attribute_target(self, gx):
        result = analyze(gx, "def f():\n for i in r:\n  self.s += 'x'\n")
        assert result == {}

    def test_non_str_accumulator(self, gx):
        # 'n' is not declared a string, so it is not a candidate
        result = analyze(gx, "def f():\n for i in r:\n  n += 1\n")
        assert result == {}


class TestNesting:
    """Only the outermost qualifying loop is claimed"""

    def test_outermost_wins(self, gx):
        source = "def f():\n for i in r:\n  for j in s:\n   out += 'x'\n"
        result = analyze(gx, source)
        assert len(result) == 1
        loop = next(iter(result))
        assert isinstance(loop, ast.For)
        assert loop.target.id == "i"  # the outer loop

    def test_sibling_loops_both_claimed(self, gx):
        source = (
            "def f():\n for i in r:\n  a += 'x'\n for j in s:\n  b += 'y'\n"
        )
        result = analyze(gx, source)
        assert len(result) == 2
        assert accumulated_names(result) == {"a", "b"}

    def test_inner_loop_claimed_when_outer_disqualified(self, gx):
        # the outer loop reads 'out', the inner one only appends
        source = "def f():\n for i in r:\n  for j in s:\n   out += 'x'\n  print(out)\n"
        result = analyze(gx, source)
        assert len(result) == 1
        loop = next(iter(result))
        assert loop.target.id == "j"  # the inner loop
