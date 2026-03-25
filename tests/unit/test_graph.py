# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.graph module."""

import argparse
import ast

import pytest

from shedskin.config import GlobalInfo
from shedskin import graph, python


class TestModuleVisitorGlobals:
    """Tests for global module visitor functions."""

    def test_setmv_getmv_roundtrip(self):
        """setmv and getmv should work as a pair."""
        mock_mv = object()

        result = graph.setmv(mock_mv)  # type: ignore
        assert result is mock_mv

        retrieved = graph.getmv()
        assert retrieved is mock_mv


class TestConstStr:
    """Tests for _const_str helper."""

    def test_returns_string_value(self):
        """_const_str should return the string value of a Constant node."""
        node = ast.Constant(value="hello")
        assert graph._const_str(node) == "hello"

    def test_empty_string(self):
        """_const_str should handle empty strings."""
        node = ast.Constant(value="")
        assert graph._const_str(node) == ""

    def test_rejects_non_constant(self):
        """_const_str should assert on non-Constant nodes."""
        node = ast.Name(id="x", ctx=ast.Load())
        with pytest.raises(AssertionError):
            graph._const_str(node)

    def test_rejects_non_string_constant(self):
        """_const_str should assert on non-string Constant nodes."""
        node = ast.Constant(value=42)
        with pytest.raises(AssertionError):
            graph._const_str(node)


class TestRegisterNode:
    """Tests for register_node function."""

    def test_registers_with_function(self):
        """register_node should append node to function's registered list."""
        func = type("MockFunc", (), {"registered": []})()
        node = ast.Name(id="x", ctx=ast.Load())

        graph.register_node(node, func)

        assert node in func.registered

    def test_skips_none_function(self):
        """register_node should do nothing when func is None."""
        node = ast.Name(id="x", ctx=ast.Load())
        graph.register_node(node, None)
        # Should not raise


class TestSliceNums:
    """Tests for slice_nums function."""

    def test_all_present(self):
        """slice_nums should set bitmask bits for present nodes."""
        a = ast.Constant(value=1)
        b = ast.Constant(value=2)
        c = ast.Constant(value=3)

        result = graph.slice_nums([a, b, c])

        # Header should be 0b111 = 7 (all three present)
        assert result[0].value == 7
        assert result[1] is a
        assert result[2] is b
        assert result[3] is c

    def test_none_entries(self):
        """slice_nums should replace None with Constant(0) and clear bitmask."""
        a = ast.Constant(value=10)

        result = graph.slice_nums([a, None, None])

        # Header should be 0b001 = 1 (only first present)
        assert result[0].value == 1
        assert result[1] is a
        assert result[2].value == 0  # replaced None
        assert result[3].value == 0  # replaced None

    def test_none_constant_entries(self):
        """slice_nums should treat Constant(None) as absent."""
        a = ast.Constant(value=5)
        none_node = ast.Constant(value=None)

        result = graph.slice_nums([none_node, a])

        # Header should be 0b10 = 2 (only second present)
        assert result[0].value == 2

    def test_empty_list(self):
        """slice_nums should return just the header for empty input."""
        result = graph.slice_nums([])
        assert len(result) == 1
        assert result[0].value == 0


class TestGetArgNodes:
    """Tests for get_arg_nodes function."""

    def test_simple_args(self):
        """get_arg_nodes should return positional args."""
        call = ast.Call(
            func=ast.Name(id="f", ctx=ast.Load()),
            args=[
                ast.Name(id="a", ctx=ast.Load()),
                ast.Name(id="b", ctx=ast.Load()),
            ],
            keywords=[],
        )

        result = graph.get_arg_nodes(call)
        assert len(result) == 2
        assert result[0].id == "a"
        assert result[1].id == "b"

    def test_starred_arg_unwrapped(self):
        """get_arg_nodes should unwrap Starred args to their inner value."""
        inner = ast.Name(id="args", ctx=ast.Load())
        call = ast.Call(
            func=ast.Name(id="f", ctx=ast.Load()),
            args=[ast.Starred(value=inner, ctx=ast.Load())],
            keywords=[],
        )

        result = graph.get_arg_nodes(call)
        assert len(result) == 1
        assert result[0] is inner

    def test_keyword_args_included(self):
        """get_arg_nodes should include keyword argument values."""
        call = ast.Call(
            func=ast.Name(id="f", ctx=ast.Load()),
            args=[ast.Name(id="a", ctx=ast.Load())],
            keywords=[
                ast.keyword(arg="x", value=ast.Constant(value=1)),
                ast.keyword(arg="y", value=ast.Constant(value=2)),
            ],
        )

        result = graph.get_arg_nodes(call)
        assert len(result) == 3
        assert result[1].value == 1
        assert result[2].value == 2

    def test_no_args(self):
        """get_arg_nodes should return empty list for no-arg call."""
        call = ast.Call(
            func=ast.Name(id="f", ctx=ast.Load()),
            args=[],
            keywords=[],
        )

        result = graph.get_arg_nodes(call)
        assert result == []


class TestHasStarKwarg:
    """Tests for has_star_kwarg function."""

    def test_no_stars(self):
        """has_star_kwarg should return False for plain calls."""
        call = ast.Call(
            func=ast.Name(id="f", ctx=ast.Load()),
            args=[ast.Name(id="a", ctx=ast.Load())],
            keywords=[ast.keyword(arg="x", value=ast.Constant(value=1))],
        )
        assert graph.has_star_kwarg(call) is False

    def test_starred_positional(self):
        """has_star_kwarg should return True for *args."""
        call = ast.Call(
            func=ast.Name(id="f", ctx=ast.Load()),
            args=[ast.Starred(value=ast.Name(id="a", ctx=ast.Load()), ctx=ast.Load())],
            keywords=[],
        )
        assert graph.has_star_kwarg(call) is True

    def test_double_star_keyword(self):
        """has_star_kwarg should return True for **kwargs (arg=None)."""
        call = ast.Call(
            func=ast.Name(id="f", ctx=ast.Load()),
            args=[],
            keywords=[ast.keyword(arg=None, value=ast.Name(id="kw", ctx=ast.Load()))],
        )
        assert graph.has_star_kwarg(call) is True

    def test_empty_call(self):
        """has_star_kwarg should return False for empty call."""
        call = ast.Call(
            func=ast.Name(id="f", ctx=ast.Load()),
            args=[],
            keywords=[],
        )
        assert graph.has_star_kwarg(call) is False


class TestMakeArgList:
    """Tests for make_arg_list function."""

    def test_creates_arguments(self):
        """make_arg_list should create ast.arguments from name list."""
        result = graph.make_arg_list(["self", "x", "y"])

        assert isinstance(result, ast.arguments)
        assert len(result.args) == 3
        assert result.args[0].arg == "self"
        assert result.args[1].arg == "x"
        assert result.args[2].arg == "y"

    def test_empty_list(self):
        """make_arg_list should handle empty arg list."""
        result = graph.make_arg_list([])
        assert isinstance(result, ast.arguments)
        assert len(result.args) == 0

    def test_single_arg(self):
        """make_arg_list should handle single arg."""
        result = graph.make_arg_list(["x"])
        assert len(result.args) == 1
        assert result.args[0].arg == "x"


class TestStructFaketuple:
    """Tests for ModuleVisitor.struct_faketuple method."""

    @pytest.fixture
    def mv(self):
        """Create a ModuleVisitor with builtin module loaded."""
        options = argparse.Namespace()
        gx = GlobalInfo(options)
        graph.parse_module("builtin", gx)
        return gx.modules["builtin"].mv

    def test_int_type(self, mv):
        """struct_faketuple should produce Constant(1) for int types."""
        info = [("@", "i", "int", 1)]
        result = mv.struct_faketuple(info)
        assert isinstance(result, ast.Tuple)
        assert len(result.elts) == 1
        assert result.elts[0].value == 1

    def test_float_type(self, mv):
        """struct_faketuple should produce Constant(1.0) for float types."""
        info = [("@", "f", "float", 1)]
        result = mv.struct_faketuple(info)
        assert result.elts[0].value == 1.0

    def test_bytes_type(self, mv):
        """struct_faketuple should produce Constant(b'') for bytes types."""
        info = [("@", "s", "bytes", 1)]
        result = mv.struct_faketuple(info)
        assert result.elts[0].value == b""

    def test_bool_type(self, mv):
        """struct_faketuple should produce Constant(True) for bool types."""
        info = [("@", "?", "bool", 1)]
        result = mv.struct_faketuple(info)
        assert result.elts[0].value is True

    def test_skips_padding_with_zero_count(self, mv):
        """struct_faketuple should skip pad entries with d=0 (except 's')."""
        info = [("@", "x", "pad", 0)]
        result = mv.struct_faketuple(info)
        assert len(result.elts) == 0

    def test_keeps_s_with_zero_count(self, mv):
        """struct_faketuple should keep 's' entries even with d=0."""
        info = [("@", "s", "bytes", 0)]
        result = mv.struct_faketuple(info)
        assert len(result.elts) == 1
        assert result.elts[0].value == b""

    def test_mixed_types(self, mv):
        """struct_faketuple should handle multiple types."""
        info = [
            ("@", "i", "int", 1),
            ("@", "f", "float", 1),
            ("@", "s", "bytes", 5),
        ]
        result = mv.struct_faketuple(info)
        assert len(result.elts) == 3
        assert result.elts[0].value == 1
        assert result.elts[1].value == 1.0
        assert result.elts[2].value == b""


class TestInheritRec:
    """Tests for inheritance relation tracking."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_inherit_rec_simple(self, gx):
        """inherit_rec should track AST node inheritance."""
        original = ast.parse("x = 1").body[0]
        copy = ast.parse("x = 1").body[0]

        graph.inherit_rec(gx, original, copy, None)  # type: ignore

        assert original in gx.inheritance_relations
        assert copy in gx.inheritance_relations[original]
        assert copy in gx.inherited
        assert gx.parent_nodes[copy] == original

    def test_inherit_rec_nested(self, gx):
        """inherit_rec should handle nested AST nodes."""
        original = ast.parse("x = [1, 2, 3]").body[0]
        copy = ast.parse("x = [1, 2, 3]").body[0]

        graph.inherit_rec(gx, original, copy, None)  # type: ignore

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
        module = graph.parse_module("builtin", gx)

        assert module is not None
        assert module.builtin is True
        assert "builtin" in gx.modules


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
