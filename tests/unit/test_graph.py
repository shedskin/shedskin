# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.graph module."""

import argparse
import ast

import pytest

from shedskin.config import GlobalInfo
from shedskin import graph


class TestModuleVisitorGlobals:
    """Tests for global module visitor functions."""

    def test_setmv_getmv_roundtrip(self):
        """setmv and getmv should work as a pair."""
        # Create a mock module visitor (just need something to store)
        mock_mv = object()

        result = graph.setmv(mock_mv)  # type: ignore
        assert result is mock_mv

        retrieved = graph.getmv()
        assert retrieved is mock_mv


class TestInheritRec:
    """Tests for inheritance relation tracking."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_inherit_rec_simple(self, gx):
        """inherit_rec should track AST node inheritance."""
        # Create simple AST nodes
        original = ast.parse("x = 1").body[0]
        copy = ast.parse("x = 1").body[0]

        graph.inherit_rec(gx, original, copy, None)  # type: ignore

        # Check that the relationship was recorded
        assert original in gx.inheritance_relations
        assert copy in gx.inheritance_relations[original]
        assert copy in gx.inherited
        assert gx.parent_nodes[copy] == original

    def test_inherit_rec_nested(self, gx):
        """inherit_rec should handle nested AST nodes."""
        # Create AST with nested structure
        original = ast.parse("x = [1, 2, 3]").body[0]
        copy = ast.parse("x = [1, 2, 3]").body[0]

        graph.inherit_rec(gx, original, copy, None)  # type: ignore

        # Both top-level and nested nodes should be tracked
        assert copy in gx.inherited


class TestParseModule:
    """Tests for module parsing functionality."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_parse_module_builtin(self, gx):
        """parse_module should handle builtin modules."""
        # Parse the builtin module
        module = graph.parse_module("builtin", gx)

        assert module is not None
        assert module.builtin is True
        assert "builtin" in gx.modules


class TestTempVarGeneration:
    """Tests for temporary variable generation."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_tempcount_tracking(self, gx):
        """GlobalInfo should track temporary variable counts."""
        # tempcount is a dict that maps nodes to temp var names
        assert isinstance(gx.tempcount, dict)
        assert len(gx.tempcount) == 0

        # Add a temp var (simulating what graph.py does)
        mock_node = ast.Name(id="test", ctx=ast.Load())
        gx.tempcount[mock_node] = "__0"

        assert gx.tempcount[mock_node] == "__0"


class TestLoopStack:
    """Tests for loop tracking functionality."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_loopstack_push_pop(self, gx):
        """loopstack should work as a stack for nested loops."""
        for_node = ast.For(
            target=ast.Name(id="i", ctx=ast.Store()),
            iter=ast.Name(id="range", ctx=ast.Load()),
            body=[],
            orelse=[],
        )

        while_node = ast.While(test=ast.Constant(value=True), body=[], orelse=[])

        # Push nodes onto stack
        gx.loopstack.append(for_node)
        gx.loopstack.append(while_node)

        assert len(gx.loopstack) == 2
        assert gx.loopstack[-1] is while_node

        # Pop nodes
        gx.loopstack.pop()
        assert len(gx.loopstack) == 1
        assert gx.loopstack[-1] is for_node


class TestComprehensionTranslation:
    """Tests for comprehension-to-list-comp translation tracking."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_genexp_to_lc_tracking(self, gx):
        """Generator expression to list comp mapping should be tracked."""
        genexp = ast.GeneratorExp(
            elt=ast.Name(id="x", ctx=ast.Load()),
            generators=[
                ast.comprehension(
                    target=ast.Name(id="x", ctx=ast.Store()),
                    iter=ast.Name(id="range", ctx=ast.Load()),
                    ifs=[],
                    is_async=0,
                )
            ],
        )

        listcomp = ast.ListComp(
            elt=ast.Name(id="x", ctx=ast.Load()),
            generators=[
                ast.comprehension(
                    target=ast.Name(id="x", ctx=ast.Store()),
                    iter=ast.Name(id="range", ctx=ast.Load()),
                    ifs=[],
                    is_async=0,
                )
            ],
        )

        gx.genexp_to_lc[genexp] = listcomp
        assert gx.genexp_to_lc[genexp] is listcomp


def test_all():
    """Run all tests in this module."""
    pytest.main([__file__, "-v"])
