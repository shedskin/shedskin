# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.virtual module."""

import argparse
import ast
from unittest.mock import MagicMock, patch

import pytest

from shedskin.config import GlobalInfo
from shedskin import graph, python, virtual


@pytest.fixture
def gx_with_builtin():
    """Create a GlobalInfo instance with builtin module loaded."""
    options = argparse.Namespace()
    gx = GlobalInfo(options)
    graph.parse_module("builtin", gx)
    return gx


class TestUpgradeCl:
    """Tests for upgrade_cl function."""

    def test_skip_getattr_setattr(self, gx_with_builtin):
        """upgrade_cl should not register __getattr__/__setattr__ as virtual methods."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        # Create a simple class hierarchy
        node = ast.ClassDef(
            name="Animal",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        abstract_cl = python.Class(gx, node, mv, mv.module)
        abstract_cl.module = mv.module

        child_node = ast.ClassDef(
            name="Cow",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        child_cl = python.Class(gx, child_node, mv, mv.module)
        child_cl.bases = [abstract_cl]
        abstract_cl.children = [child_cl]

        mock_call = MagicMock()
        classes = {child_cl}

        # __getattr__ should not add to virtuals
        virtual.upgrade_cl(gx, abstract_cl, mock_call, "__getattr__", classes)
        assert "__getattr__" not in abstract_cl.virtuals

    def test_skip_builtin_module(self, gx_with_builtin):
        """upgrade_cl should not register virtuals for builtin module classes."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        # Get a builtin class
        int_cl = python.def_class(gx, "int_")

        mock_call = MagicMock()
        classes = set()

        # Should not crash on builtin classes
        virtual.upgrade_cl(gx, int_cl, mock_call, "some_method", classes)
        assert "some_method" not in int_cl.virtuals

    def test_registers_virtual_method(self, gx_with_builtin):
        """upgrade_cl should register virtual methods when redefined in subclass."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        # Create parent class with a method
        parent_node = ast.ClassDef(
            name="Base",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        parent_cl = python.Class(gx, parent_node, mv, mv.module)
        parent_cl.module = MagicMock()
        parent_cl.module.builtin = False

        func_node = ast.FunctionDef(
            name="sound",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        parent_func = python.Function(gx, mv, func_node, parent_cl)
        parent_func.inherited = None
        parent_cl.funcs["sound"] = parent_func

        # Create child class that redefines the method
        child_node = ast.ClassDef(
            name="Child",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        child_cl = python.Class(gx, child_node, mv, mv.module)
        child_cl.bases = [parent_cl]
        parent_cl.children = [child_cl]

        child_func_node = ast.FunctionDef(
            name="sound",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        child_func = python.Function(gx, mv, child_func_node, child_cl)
        child_func.inherited = None
        child_cl.funcs["sound"] = child_func

        mock_call = MagicMock()
        classes = {child_cl}

        virtual.upgrade_cl(gx, parent_cl, mock_call, "sound", classes)
        assert "sound" in parent_cl.virtuals
        assert child_cl in parent_cl.virtuals["sound"]

    def test_no_registration_without_redefinition(self, gx_with_builtin):
        """upgrade_cl should not register virtual if method not redefined."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        parent_node = ast.ClassDef(
            name="Base",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        parent_cl = python.Class(gx, parent_node, mv, mv.module)
        parent_cl.module = MagicMock()
        parent_cl.module.builtin = False

        # Child class with NO redefined method
        child_node = ast.ClassDef(
            name="Child",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        child_cl = python.Class(gx, child_node, mv, mv.module)
        child_cl.bases = [parent_cl]

        mock_call = MagicMock()
        classes = {child_cl}

        virtual.upgrade_cl(gx, parent_cl, mock_call, "sound", classes)
        assert "sound" not in parent_cl.virtuals


class TestVirtuals:
    """Tests for virtuals function (code generation)."""

    def test_empty_virtuals(self, gx_with_builtin):
        """virtuals should not invoke start when class has no virtual methods."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        node = ast.ClassDef(
            name="Test",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        mock_gv = MagicMock()
        mock_gv.gx = gx
        mock_gv.mv = mv

        virtual.virtuals(mock_gv, cl, declare=True)
        assert mock_gv.start.call_count == 0

    def test_skips_empty_subclasses(self, gx_with_builtin):
        """virtuals should not invoke start when subclass sets are empty."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        node = ast.ClassDef(
            name="Test",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)
        cl.virtuals["sound"] = set()

        mock_gv = MagicMock()
        mock_gv.gx = gx
        mock_gv.mv = mv

        virtual.virtuals(mock_gv, cl, declare=True)
        assert mock_gv.start.call_count == 0


class TestAnalyzeVirtuals:
    """Tests for analyze_virtuals function."""

    def test_empty_merged_inh(self, gx_with_builtin):
        """analyze_virtuals should leave virtuals unchanged on empty merged_inh."""
        gx = gx_with_builtin
        gx.merged_inh = {}

        virtual.analyze_virtuals(gx)
        assert gx.merged_inh == {}

    def test_skips_non_call_nodes(self, gx_with_builtin):
        """analyze_virtuals should not modify merged_inh for non-Call nodes."""
        gx = gx_with_builtin
        name_node = ast.Name(id="x", ctx=ast.Load())
        gx.merged_inh = {name_node: set()}

        virtual.analyze_virtuals(gx)
        assert name_node in gx.merged_inh


class TestSubclass:
    """Tests for python.subclass function (used by virtual.py)."""

    def test_direct_subclass(self, gx_with_builtin):
        """subclass should return True for direct child."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        parent_node = ast.ClassDef(
            name="Parent", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        child_node = ast.ClassDef(
            name="Child", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        parent_cl = python.Class(gx, parent_node, mv, mv.module)
        child_cl = python.Class(gx, child_node, mv, mv.module)
        child_cl.bases = [parent_cl]

        assert python.subclass(child_cl, parent_cl) is True

    def test_not_subclass(self, gx_with_builtin):
        """subclass should return False for unrelated classes."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        cl_a_node = ast.ClassDef(
            name="A", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl_b_node = ast.ClassDef(
            name="B", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl_a = python.Class(gx, cl_a_node, mv, mv.module)
        cl_b = python.Class(gx, cl_b_node, mv, mv.module)

        assert python.subclass(cl_a, cl_b) is False

    def test_transitive_subclass(self, gx_with_builtin):
        """subclass should return True for transitive inheritance."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        grandparent_node = ast.ClassDef(
            name="GP", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        parent_node = ast.ClassDef(
            name="P", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        child_node = ast.ClassDef(
            name="C", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        gp_cl = python.Class(gx, grandparent_node, mv, mv.module)
        p_cl = python.Class(gx, parent_node, mv, mv.module)
        c_cl = python.Class(gx, child_node, mv, mv.module)
        p_cl.bases = [gp_cl]
        c_cl.bases = [p_cl]

        assert python.subclass(c_cl, gp_cl) is True


def test_all():
    """Verify module is importable for standalone execution."""
    assert virtual is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
