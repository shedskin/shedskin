# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.extmod module."""

import argparse
import ast
import io
from unittest.mock import MagicMock, PropertyMock

import pytest

from shedskin.config import GlobalInfo
from shedskin import extmod, graph, infer, python


@pytest.fixture
def gx_with_builtin():
    """Create a GlobalInfo instance with builtin module loaded."""
    options = argparse.Namespace()
    gx = GlobalInfo(options)
    graph.parse_module("builtin", gx)
    return gx


class TestOverloadConstants:
    """Tests for overload operator constants."""

    def test_overload_single_contents(self):
        """OVERLOAD_SINGLE should contain unary operator names."""
        assert "__neg__" in extmod.OVERLOAD_SINGLE
        assert "__pos__" in extmod.OVERLOAD_SINGLE
        assert "__abs__" in extmod.OVERLOAD_SINGLE
        assert "__bool__" in extmod.OVERLOAD_SINGLE
        assert len(extmod.OVERLOAD_SINGLE) == 4

    def test_overload_contains_binary_ops(self):
        """OVERLOAD should contain binary operator names."""
        assert "__add__" in extmod.OVERLOAD
        assert "__sub__" in extmod.OVERLOAD
        assert "__mul__" in extmod.OVERLOAD
        assert "__div__" in extmod.OVERLOAD
        assert "__mod__" in extmod.OVERLOAD
        assert "__divmod__" in extmod.OVERLOAD
        assert "__pow__" in extmod.OVERLOAD

    def test_overload_includes_single(self):
        """OVERLOAD should include all OVERLOAD_SINGLE entries."""
        for op in extmod.OVERLOAD_SINGLE:
            assert op in extmod.OVERLOAD

    def test_overload_total_count(self):
        """OVERLOAD should have 7 binary + 4 unary = 11 entries."""
        assert len(extmod.OVERLOAD) == 11


class TestClname:
    """Tests for clname function."""

    def test_simple_module(self, gx_with_builtin):
        """clname should generate proper prefixed name for single module."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        node = ast.ClassDef(
            name="MyClass",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        result = extmod.clname(cl)
        assert result == "__ss_builtin_MyClass"

    def test_nested_module(self, gx_with_builtin):
        """clname should join nested module names with underscores."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv

        node = ast.ClassDef(
            name="Widget",
            bases=[],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)
        # Simulate nested module
        cl.mv.module.name_list = ["pkg", "sub", "mod"]

        result = extmod.clname(cl)
        assert result == "__ss_pkg_sub_mod_Widget"


class TestExtensionModuleInit:
    """Tests for ExtensionModule initialization."""

    def test_init_stores_gx_and_gv(self, gx_with_builtin):
        """ExtensionModule should store gx and gv references."""
        gx = gx_with_builtin
        mock_gv = MagicMock()

        em = extmod.ExtensionModule(gx, mock_gv)
        assert em.gx is gx
        assert em.gv is mock_gv

    def test_write_outputs_to_gv_out(self, gx_with_builtin):
        """ExtensionModule.write should print to gv.out."""
        gx = gx_with_builtin
        output = io.StringIO()
        mock_gv = MagicMock()
        mock_gv.out = output

        em = extmod.ExtensionModule(gx, mock_gv)
        em.write("test output")

        assert "test output" in output.getvalue()


class TestSupportedVars:
    """Tests for supported_vars filtering."""

    def test_empty_vars(self, gx_with_builtin):
        """supported_vars should return empty list for no variables."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        result = em.supported_vars([])
        assert result == []

    def test_filters_invisible_vars(self, gx_with_builtin):
        """supported_vars should filter out invisible variables."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable("_hidden", None)
        var.invisible = True

        # Variable not in merged_inh, so filtered first
        result = em.supported_vars([var])
        assert var not in result

    def test_filters_vars_not_in_merged_inh(self, gx_with_builtin):
        """supported_vars should filter out variables not in merged_inh."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable("myvar", None)

        result = em.supported_vars([var])
        assert var not in result

    def test_filters_dunder_vars(self, gx_with_builtin):
        """supported_vars should filter out __dunder__ variables."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable("__internal", None)
        int_cl = python.def_class(gx, "int_")
        gx.merged_inh[var] = {(int_cl, 0)}

        result = em.supported_vars([var])
        assert var not in result

    def test_filters_none_name_vars(self, gx_with_builtin):
        """supported_vars should filter out variables with None name."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable(None, None)  # type: ignore
        int_cl = python.def_class(gx, "int_")
        gx.merged_inh[var] = {(int_cl, 0)}

        result = em.supported_vars([var])
        assert var not in result

    def test_filters_empty_merged_inh(self, gx_with_builtin):
        """supported_vars should filter out variables with empty merged_inh."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        mock_gv.mv = gx.modules["builtin"].mv
        em = extmod.ExtensionModule(gx, mock_gv)

        var = python.Variable("myvar", None)
        gx.merged_inh[var] = set()  # empty type set

        result = em.supported_vars([var])
        assert var not in result


class TestSupportedFuncs:
    """Tests for supported_funcs filtering."""

    def test_empty_funcs(self, gx_with_builtin):
        """supported_funcs should return empty list for no functions."""
        gx = gx_with_builtin
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        result = em.supported_funcs([])
        assert result == []

    def test_filters_generators(self, gx_with_builtin):
        """supported_funcs should filter out generators."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        mock_gv.inhcpa.return_value = True
        mock_gv.mv = mv
        em = extmod.ExtensionModule(gx, mock_gv)

        func_node = ast.FunctionDef(
            name="gen",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node)
        func.isGenerator = True

        result = em.supported_funcs([func])
        assert func not in result

    def test_filters_uncalled_funcs(self, gx_with_builtin):
        """supported_funcs should filter out uncalled functions."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        mock_gv.inhcpa.return_value = False
        mock_gv.mv = mv
        em = extmod.ExtensionModule(gx, mock_gv)

        func_node = ast.FunctionDef(
            name="uncalled",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node)

        result = em.supported_funcs([func])
        assert func not in result

    def test_filters_setattr_getattr(self, gx_with_builtin):
        """supported_funcs should filter __setattr__ and __getattr__."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        mock_gv.inhcpa.return_value = True
        mock_gv.mv = mv
        em = extmod.ExtensionModule(gx, mock_gv)

        for method_name in ["__setattr__", "__getattr__"]:
            func_node = ast.FunctionDef(
                name=method_name,
                args=ast.arguments(
                    posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                    kw_defaults=[], kwarg=None, defaults=[],
                ),
                body=[ast.Pass()],
                decorator_list=[],
                returns=None,
            )
            func = python.Function(gx, mv, func_node)

            result = em.supported_funcs([func])
            assert func not in result


class TestHasMethod:
    """Tests for has_method function."""

    def test_no_method(self, gx_with_builtin):
        """has_method should return False when method doesn't exist."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        node = ast.ClassDef(
            name="Test", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        result = em.has_method(cl, "__init__")
        assert result is False

    def test_invisible_method(self, gx_with_builtin):
        """has_method should return False for invisible methods."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        node = ast.ClassDef(
            name="Test", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        func_node = ast.FunctionDef(
            name="hidden",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node, cl)
        func.invisible = True
        cl.funcs["hidden"] = func

        result = em.has_method(cl, "hidden")
        assert result is False

    def test_inherited_method(self, gx_with_builtin):
        """has_method should return False for inherited methods."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        mock_gv = MagicMock()
        em = extmod.ExtensionModule(gx, mock_gv)

        node = ast.ClassDef(
            name="Test", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl = python.Class(gx, node, mv, mv.module)

        func_node = ast.FunctionDef(
            name="inherited_func",
            args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[],
                kw_defaults=[], kwarg=None, defaults=[],
            ),
            body=[ast.Pass()],
            decorator_list=[],
            returns=None,
        )
        func = python.Function(gx, mv, func_node, cl)
        func.inherited = func_node  # mark as inherited
        cl.funcs["inherited_func"] = func

        result = em.has_method(cl, "inherited_func")
        assert result is False


class TestExportedClasses:
    """Tests for exported_classes method."""

    @pytest.fixture
    def fake_module_mv(self, gx_with_builtin):
        """Create a fake non-builtin module with its own mv for testing."""
        gx = gx_with_builtin
        builtin_mv = gx.modules["builtin"].mv

        fake_module = python.Module(
            "test_mod", "/fake/test_mod.py", "test_mod.py",
            False, None, ast.parse(""),
        )
        # Create a minimal mock mv for the fake module
        fake_mv = MagicMock()
        fake_mv.module = fake_module
        fake_mv.classes = {}
        fake_module.mv = fake_mv

        return gx, fake_mv, fake_module

    def test_excludes_exception_subclasses(self, fake_module_mv):
        """exported_classes should exclude classes inheriting from Exception."""
        gx, fake_mv, fake_module = fake_module_mv
        builtin_mv = gx.modules["builtin"].mv

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.module.mv = fake_mv
        em = extmod.ExtensionModule(gx, mock_gv)

        exception_cl = python.def_class(gx, "Exception")

        node = ast.ClassDef(
            name="MyError", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        error_cl = python.Class(gx, node, builtin_mv, fake_module)
        error_cl.bases = [exception_cl]
        error_cl.def_order = 0

        fake_mv.classes = {"MyError": error_cl}

        result = em.exported_classes()
        assert error_cl not in result

    def test_includes_regular_classes(self, fake_module_mv):
        """exported_classes should include regular classes."""
        gx, fake_mv, fake_module = fake_module_mv
        builtin_mv = gx.modules["builtin"].mv

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.module.mv = fake_mv
        em = extmod.ExtensionModule(gx, mock_gv)

        node = ast.ClassDef(
            name="MyClass", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        regular_cl = python.Class(gx, node, builtin_mv, fake_module)
        regular_cl.def_order = 0

        fake_mv.classes = {"MyClass": regular_cl}

        result = em.exported_classes()
        assert regular_cl in result

    def test_sorted_by_def_order(self, fake_module_mv):
        """exported_classes should be sorted by def_order."""
        gx, fake_mv, fake_module = fake_module_mv
        builtin_mv = gx.modules["builtin"].mv

        mock_gv = MagicMock()
        mock_gv.module = fake_module
        mock_gv.module.mv = fake_mv
        em = extmod.ExtensionModule(gx, mock_gv)

        node_a = ast.ClassDef(
            name="A", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        node_b = ast.ClassDef(
            name="B", bases=[], keywords=[],
            body=[ast.Pass()], decorator_list=[],
        )
        cl_a = python.Class(gx, node_a, builtin_mv, fake_module)
        cl_b = python.Class(gx, node_b, builtin_mv, fake_module)
        cl_a.def_order = 5
        cl_b.def_order = 2

        fake_mv.classes = {"A": cl_a, "B": cl_b}

        result = em.exported_classes()
        assert result == [cl_b, cl_a]  # B (order=2) before A (order=5)


class TestDoInitMods:
    """Tests for do_init_mods method."""

    def test_skips_builtin_and_current(self, gx_with_builtin):
        """do_init_mods should skip builtin and current module."""
        gx = gx_with_builtin
        output = io.StringIO()
        mock_gv = MagicMock()
        mock_gv.out = output
        mock_gv.module = gx.modules["builtin"]
        em = extmod.ExtensionModule(gx, mock_gv)

        # Only builtin module loaded, which should be skipped
        em.do_init_mods("__init")

        # Should not output anything (builtin is skipped)
        assert output.getvalue() == ""


def test_all():
    """Verify module is importable for standalone execution."""
    assert extmod is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
