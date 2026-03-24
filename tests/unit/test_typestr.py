# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.typestr module."""

import argparse
import ast
from unittest.mock import MagicMock

import pytest

from shedskin.config import GlobalInfo
from shedskin import graph, python, typestr


@pytest.fixture
def gx_with_builtin():
    """Create a GlobalInfo instance with builtin module loaded."""
    options = argparse.Namespace()
    gx = GlobalInfo(options)
    graph.parse_module("builtin", gx)
    return gx


class TestExtmodError:
    """Tests for ExtmodError exception."""

    def test_extmod_error_is_exception(self):
        """ExtmodError should be a subclass of Exception."""
        assert issubclass(typestr.ExtmodError, Exception)

    def test_extmod_error_can_be_raised(self):
        """ExtmodError should be raisable with a message."""
        with pytest.raises(typestr.ExtmodError, match="test"):
            raise typestr.ExtmodError("test")

    def test_extmod_error_no_message(self):
        """ExtmodError should be raisable without a message."""
        with pytest.raises(typestr.ExtmodError):
            raise typestr.ExtmodError()


class TestMaxTypeDepth:
    """Tests for MAX_TYPE_DEPTH constant."""

    def test_max_type_depth_is_positive(self):
        """MAX_TYPE_DEPTH should be a positive integer."""
        assert typestr.MAX_TYPE_DEPTH > 0

    def test_max_type_depth_value(self):
        """MAX_TYPE_DEPTH should be 10."""
        assert typestr.MAX_TYPE_DEPTH == 10


class TestTypesClasses:
    """Tests for types_classes function."""

    def test_empty_types(self):
        """types_classes should return empty set for empty input."""
        result = typestr.types_classes(set())
        assert result == set()

    def test_with_class_types(self, gx_with_builtin):
        """types_classes should extract Class instances from type tuples."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        str_cl = python.def_class(gx, "str_")
        types = {(int_cl, 0), (str_cl, 0)}

        result = typestr.types_classes(types)

        assert int_cl in result
        assert str_cl in result
        assert len(result) == 2

    def test_with_function_types(self, gx_with_builtin):
        """types_classes should filter out non-Class instances."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}

        result = typestr.types_classes(types)
        assert int_cl in result


class TestUnboxable:
    """Tests for unboxable function."""

    def test_empty_types(self, gx_with_builtin):
        """unboxable should return None for empty types."""
        gx = gx_with_builtin
        result = typestr.unboxable(gx, set())
        assert result is None

    def test_int_type_unboxable(self, gx_with_builtin):
        """int type should be unboxable."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}

        result = typestr.unboxable(gx, types)
        assert result == "int_"

    def test_float_type_unboxable(self, gx_with_builtin):
        """float type should be unboxable."""
        gx = gx_with_builtin
        float_cl = python.def_class(gx, "float_")
        types = {(float_cl, 0)}

        result = typestr.unboxable(gx, types)
        assert result == "float_"

    def test_bool_type_unboxable(self, gx_with_builtin):
        """bool type should be unboxable."""
        gx = gx_with_builtin
        bool_cl = python.def_class(gx, "bool_")
        types = {(bool_cl, 0)}

        result = typestr.unboxable(gx, types)
        assert result == "bool_"

    def test_complex_type_unboxable(self, gx_with_builtin):
        """complex type should be unboxable."""
        gx = gx_with_builtin
        complex_cl = python.def_class(gx, "complex")
        types = {(complex_cl, 0)}

        result = typestr.unboxable(gx, types)
        assert result == "complex"

    def test_str_type_not_unboxable(self, gx_with_builtin):
        """str type should not be unboxable."""
        gx = gx_with_builtin
        str_cl = python.def_class(gx, "str_")
        types = {(str_cl, 0)}

        result = typestr.unboxable(gx, types)
        assert result is None

    def test_list_type_not_unboxable(self, gx_with_builtin):
        """list type should not be unboxable."""
        gx = gx_with_builtin
        list_cl = python.def_class(gx, "list")
        types = {(list_cl, 0)}

        result = typestr.unboxable(gx, types)
        assert result is None

    def test_mixed_numeric_types(self, gx_with_builtin):
        """mixed numeric types (int + float) should be unboxable."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        float_cl = python.def_class(gx, "float_")
        types = {(int_cl, 0), (float_cl, 0)}

        result = typestr.unboxable(gx, types)
        # returns one of the numeric idents (set.pop is non-deterministic)
        assert result in ("int_", "float_")


class TestSingletype2:
    """Tests for singletype2 function."""

    def test_single_class_match(self, gx_with_builtin):
        """singletype2 should return class when single type matches."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}

        result = typestr.singletype2(types, python.Class)
        assert result is int_cl

    def test_single_type_no_match(self, gx_with_builtin):
        """singletype2 should return None when type doesn't match."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}

        result = typestr.singletype2(types, python.Function)
        assert result is None

    def test_multiple_types(self, gx_with_builtin):
        """singletype2 should return None for multiple types."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        str_cl = python.def_class(gx, "str_")
        types = {(int_cl, 0), (str_cl, 0)}

        result = typestr.singletype2(types, python.Class)
        assert result is None

    def test_empty_types(self):
        """singletype2 should return None for empty types."""
        result = typestr.singletype2(set(), python.Class)
        assert result is None


class TestPolymorphicCl:
    """Tests for polymorphic_cl function."""

    def test_empty_classes(self, gx_with_builtin):
        """polymorphic_cl should return empty set for empty input."""
        gx = gx_with_builtin
        result = typestr.polymorphic_cl(gx, [])
        assert result == set()

    def test_single_class(self, gx_with_builtin):
        """polymorphic_cl should return set with single class."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        result = typestr.polymorphic_cl(gx, [int_cl])
        assert result == {int_cl}

    def test_none_removed_with_non_numeric(self, gx_with_builtin):
        """polymorphic_cl should remove none when mixed with non-numeric types."""
        gx = gx_with_builtin
        str_cl = python.def_class(gx, "str_")
        none_cl = python.def_class(gx, "none")

        result = typestr.polymorphic_cl(gx, [str_cl, none_cl])
        assert none_cl not in result
        assert str_cl in result

    def test_none_kept_with_int(self, gx_with_builtin):
        """polymorphic_cl should keep none when mixed with int."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        none_cl = python.def_class(gx, "none")

        result = typestr.polymorphic_cl(gx, [int_cl, none_cl])
        assert none_cl in result
        assert int_cl in result

    def test_none_kept_with_float(self, gx_with_builtin):
        """polymorphic_cl should keep none when mixed with float."""
        gx = gx_with_builtin
        float_cl = python.def_class(gx, "float_")
        none_cl = python.def_class(gx, "none")

        result = typestr.polymorphic_cl(gx, [float_cl, none_cl])
        assert none_cl in result
        assert float_cl in result

    def test_none_kept_with_bool(self, gx_with_builtin):
        """polymorphic_cl should keep none when mixed with bool."""
        gx = gx_with_builtin
        bool_cl = python.def_class(gx, "bool_")
        none_cl = python.def_class(gx, "none")

        result = typestr.polymorphic_cl(gx, [bool_cl, none_cl])
        assert none_cl in result
        assert bool_cl in result

    def test_tuple2_removed_when_tuple_present(self, gx_with_builtin):
        """polymorphic_cl should remove tuple2 when tuple is present."""
        gx = gx_with_builtin
        tuple_cl = python.def_class(gx, "tuple")
        tuple2_cl = python.def_class(gx, "tuple2")

        result = typestr.polymorphic_cl(gx, [tuple_cl, tuple2_cl])
        assert tuple2_cl not in result
        assert tuple_cl in result

    def test_none_alone_kept(self, gx_with_builtin):
        """polymorphic_cl should keep none when it's the only type."""
        gx = gx_with_builtin
        none_cl = python.def_class(gx, "none")

        result = typestr.polymorphic_cl(gx, [none_cl])
        assert none_cl in result


class TestPolymorphicT:
    """Tests for polymorphic_t function."""

    def test_extracts_classes_from_type_tuples(self, gx_with_builtin):
        """polymorphic_t should extract and filter classes from type tuples."""
        gx = gx_with_builtin
        str_cl = python.def_class(gx, "str_")
        none_cl = python.def_class(gx, "none")
        types = {(str_cl, 0), (none_cl, 0)}

        result = typestr.polymorphic_t(gx, types)
        # none removed when mixed with non-numeric
        assert str_cl in result
        assert none_cl not in result


class TestLowestCommonParents:
    """Tests for lowest_common_parents function."""

    def test_empty_input(self):
        """lowest_common_parents should return empty list for empty input."""
        result = typestr.lowest_common_parents([])
        assert result == []

    def test_single_class(self, gx_with_builtin):
        """lowest_common_parents should return the class itself."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")

        result = typestr.lowest_common_parents([int_cl])
        assert int_cl in result

    def test_non_class_filtered(self):
        """lowest_common_parents should filter non-Class items."""
        result = typestr.lowest_common_parents(["not_a_class"])  # type: ignore
        assert result == []


class TestTypesVarTypes:
    """Tests for types_var_types function."""

    def test_empty_types(self, gx_with_builtin):
        """types_var_types should return empty set for empty types."""
        gx = gx_with_builtin
        result = typestr.types_var_types(gx, set(), "unit")
        assert result == set()

    def test_no_matching_varname(self, gx_with_builtin):
        """types_var_types should return empty set when varname not in class."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}
        result = typestr.types_var_types(gx, types, "nonexistent_var")
        assert result == set()


class TestIncompatibleAssignmentRec:
    """Tests for incompatible_assignment_rec function."""

    def test_empty_types_compatible(self, gx_with_builtin):
        """Empty type sets should be compatible."""
        gx = gx_with_builtin
        result = typestr.incompatible_assignment_rec(gx, set(), set())
        assert result is False

    def test_max_depth_returns_false(self, gx_with_builtin):
        """At max depth, should return False (stop recursing)."""
        gx = gx_with_builtin
        result = typestr.incompatible_assignment_rec(
            gx, set(), set(), depth=typestr.MAX_TYPE_DEPTH
        )
        assert result is False

    def test_void_to_numeric_incompatible(self, gx_with_builtin):
        """Assigning void to numeric type should be incompatible."""
        gx = gx_with_builtin
        int_type = (python.def_class(gx, "int_"), 0)

        result = typestr.incompatible_assignment_rec(
            gx, set(), {int_type}
        )
        assert result is True

    def test_void_to_float_incompatible(self, gx_with_builtin):
        """Assigning void to float type should be incompatible."""
        gx = gx_with_builtin
        float_type = (python.def_class(gx, "float_"), 0)

        result = typestr.incompatible_assignment_rec(
            gx, set(), {float_type}
        )
        assert result is True

    def test_none_to_anything_compatible(self, gx_with_builtin):
        """Assigning None to anything should be compatible."""
        gx = gx_with_builtin
        none_type = (python.def_class(gx, "none"), 0)
        int_type = (python.def_class(gx, "int_"), 0)

        result = typestr.incompatible_assignment_rec(
            gx, {none_type}, {int_type}
        )
        assert result is False

    def test_int_to_float_at_depth(self, gx_with_builtin):
        """Assigning int to float at depth > 0 should be incompatible."""
        gx = gx_with_builtin
        int_type = (python.def_class(gx, "int_"), 0)
        float_type = (python.def_class(gx, "float_"), 0)

        result = typestr.incompatible_assignment_rec(
            gx, {int_type}, {float_type}, depth=1
        )
        assert result is True

    def test_int_to_float_at_depth_zero(self, gx_with_builtin):
        """Assigning int to float at depth 0 should be compatible."""
        gx = gx_with_builtin
        int_type = (python.def_class(gx, "int_"), 0)
        float_type = (python.def_class(gx, "float_"), 0)

        result = typestr.incompatible_assignment_rec(
            gx, {int_type}, {float_type}, depth=0
        )
        assert result is False

    def test_bool_to_int_at_depth(self, gx_with_builtin):
        """Assigning bool to int at depth > 0 should be incompatible."""
        gx = gx_with_builtin
        bool_type = (python.def_class(gx, "bool_"), 0)
        int_type = (python.def_class(gx, "int_"), 0)

        result = typestr.incompatible_assignment_rec(
            gx, {bool_type}, {int_type}, depth=1
        )
        assert result is True


class TestTypestrnew:
    """Tests for typestrnew function (internal type string generation)."""

    def test_max_depth_raises_runtime_error(self, gx_with_builtin):
        """typestrnew should raise RuntimeError at max depth."""
        gx = gx_with_builtin
        with pytest.raises(RuntimeError):
            typestr.typestrnew(gx, set(), depth=typestr.MAX_TYPE_DEPTH)

    def test_empty_types_returns_void_ptr(self, gx_with_builtin):
        """typestrnew should return 'void *' for empty types in C++ mode."""
        gx = gx_with_builtin
        result = typestr.typestrnew(gx, set(), cplusplus=True)
        assert result == "void *"

    def test_empty_types_returns_empty_in_annotation_mode(self, gx_with_builtin):
        """typestrnew should return '' for empty types in annotation mode."""
        gx = gx_with_builtin
        result = typestr.typestrnew(gx, set(), cplusplus=False)
        assert result == ""

    def test_int_type_cpp(self, gx_with_builtin):
        """typestrnew should return '__ss_int' for int in C++ mode."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "__ss_int"

    def test_int_type_annotation(self, gx_with_builtin):
        """typestrnew should return 'int' for int in annotation mode."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=False, mv=gx.modules["builtin"].mv)
        assert result == "int"

    def test_float_type_cpp(self, gx_with_builtin):
        """typestrnew should return '__ss_float' for float in C++ mode."""
        gx = gx_with_builtin
        float_cl = python.def_class(gx, "float_")
        types = {(float_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "__ss_float"

    def test_bool_type_cpp(self, gx_with_builtin):
        """typestrnew should return '__ss_bool' for bool in C++ mode."""
        gx = gx_with_builtin
        bool_cl = python.def_class(gx, "bool_")
        types = {(bool_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "__ss_bool"

    def test_complex_type_cpp(self, gx_with_builtin):
        """typestrnew should return 'complex' for complex in C++ mode."""
        gx = gx_with_builtin
        complex_cl = python.def_class(gx, "complex")
        types = {(complex_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "complex"

    def test_str_type_cpp(self, gx_with_builtin):
        """typestrnew should return 'str *' for str in C++ mode."""
        gx = gx_with_builtin
        str_cl = python.def_class(gx, "str_")
        types = {(str_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "str *"

    def test_bytes_type_cpp(self, gx_with_builtin):
        """typestrnew should return 'bytes *' for bytes in C++ mode."""
        gx = gx_with_builtin
        bytes_cl = python.def_class(gx, "bytes_")
        types = {(bytes_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "bytes *"

    def test_none_type_cpp(self, gx_with_builtin):
        """typestrnew should return 'void *' for none in C++ mode."""
        gx = gx_with_builtin
        none_cl = python.def_class(gx, "none")
        types = {(none_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "void *"

    def test_none_type_annotation(self, gx_with_builtin):
        """typestrnew should return 'None' for none in annotation mode."""
        gx = gx_with_builtin
        none_cl = python.def_class(gx, "none")
        types = {(none_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=False, mv=gx.modules["builtin"].mv)
        assert result == "None"

    def test_int_float_merge_to_float_cpp(self, gx_with_builtin):
        """Mixed int + float should resolve to float in C++ mode."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        float_cl = python.def_class(gx, "float_")
        types = {(int_cl, 0), (float_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "__ss_float"

    def test_int_float_merge_to_float_annotation(self, gx_with_builtin):
        """Mixed int + float should resolve to float in annotation mode."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        float_cl = python.def_class(gx, "float_")
        types = {(int_cl, 0), (float_cl, 0)}

        result = typestr.typestrnew(gx, types, cplusplus=False, mv=gx.modules["builtin"].mv)
        assert result == "float"

    def test_extmod_error_on_anon_func(self, gx_with_builtin):
        """typestrnew should raise ExtmodError for anonymous functions when check_extmod."""
        gx = gx_with_builtin
        mv = gx.modules["builtin"].mv
        func = python.Function(gx, mv)
        func.ident = "testfunc"
        func.lambdanr = 0
        func.mv = mv
        types = {(func, 0)}

        with pytest.raises(typestr.ExtmodError):
            typestr.typestrnew(gx, types, check_extmod=True, mv=mv)


class TestTypestr:
    """Tests for typestr function (top-level type string with error handling)."""

    def test_cpp_mode_adds_space(self, gx_with_builtin):
        """typestr should add trailing space for non-pointer C++ types."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}

        result = typestr.typestr(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "__ss_int "

    def test_cpp_mode_no_extra_space_for_pointers(self, gx_with_builtin):
        """typestr should not add trailing space for pointer C++ types."""
        gx = gx_with_builtin
        str_cl = python.def_class(gx, "str_")
        types = {(str_cl, 0)}

        result = typestr.typestr(gx, types, cplusplus=True, mv=gx.modules["builtin"].mv)
        assert result == "str *"
        assert not result.endswith("* ")

    def test_annotation_mode_brackets(self, gx_with_builtin):
        """typestr should wrap in brackets for annotation mode."""
        gx = gx_with_builtin
        int_cl = python.def_class(gx, "int_")
        types = {(int_cl, 0)}

        result = typestr.typestr(gx, types, cplusplus=False, mv=gx.modules["builtin"].mv)
        assert result.startswith("[")
        assert result.endswith("]")
        assert "int" in result


def test_all():
    """Verify module is importable for standalone execution."""
    assert typestr is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
