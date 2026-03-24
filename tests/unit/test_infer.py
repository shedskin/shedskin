# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.infer module."""

import ast

import pytest

from shedskin import infer


class TestGetStarargs:
    """Tests for get_starargs function."""

    def test_no_starargs(self):
        """get_starargs should return None for calls without starred args."""
        # func(a, b, c)
        call_node = ast.Call(
            func=ast.Name(id="func", ctx=ast.Load()),
            args=[
                ast.Name(id="a", ctx=ast.Load()),
                ast.Name(id="b", ctx=ast.Load()),
                ast.Name(id="c", ctx=ast.Load()),
            ],
            keywords=[],
        )

        result = infer.get_starargs(call_node)
        assert result is None

    def test_with_starargs(self):
        """get_starargs should return the starred argument value."""
        # func(a, *args, c)
        args_name = ast.Name(id="args", ctx=ast.Load())
        call_node = ast.Call(
            func=ast.Name(id="func", ctx=ast.Load()),
            args=[
                ast.Name(id="a", ctx=ast.Load()),
                ast.Starred(value=args_name, ctx=ast.Load()),
                ast.Name(id="c", ctx=ast.Load()),
            ],
            keywords=[],
        )

        result = infer.get_starargs(call_node)
        assert result is args_name


class TestWorklist:
    """Tests for worklist operations."""

    def test_add_to_worklist_new_node(self):
        """add_to_worklist should add new nodes."""
        worklist = []
        # Create a mock CNode-like object
        node = type("MockCNode", (), {"in_list": 0})()

        infer.add_to_worklist(worklist, node)

        assert node in worklist
        assert node.in_list == 1

    def test_add_to_worklist_existing_node(self):
        """add_to_worklist should not re-add existing nodes."""
        worklist = []
        node = type("MockCNode", (), {"in_list": 0})()

        infer.add_to_worklist(worklist, node)
        infer.add_to_worklist(worklist, node)

        assert worklist.count(node) == 1


class TestInOut:
    """Tests for in_out constraint creation."""

    def test_in_out_creates_constraints(self):
        """in_out should create bidirectional constraint references."""
        a = type("MockCNode", (), {"out": set(), "in_": set()})()
        b = type("MockCNode", (), {"out": set(), "in_": set()})()

        infer.in_out(a, b)

        assert b in a.out
        assert a in b.in_


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
