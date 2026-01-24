# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.cpp module."""

import argparse

import pytest

from shedskin.config import GlobalInfo


class TestCppKeywords:
    """Tests for C++ keyword handling."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_cpp_keywords_loaded(self, gx):
        """C++ keywords should be loaded from illegal.txt."""
        assert len(gx.cpp_keywords) > 0
        # Check for C++ keywords and system constants in illegal.txt
        assert "int" in gx.cpp_keywords
        assert "auto" in gx.cpp_keywords
        assert "const" in gx.cpp_keywords
        assert "virtual" in gx.cpp_keywords
        assert "template" in gx.cpp_keywords

    def test_ss_prefix(self, gx):
        """shedskin prefix should be defined."""
        assert gx.ss_prefix == "__ss_"


class TestBuiltinTypes:
    """Tests for builtin type definitions."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_builtins_list(self, gx):
        """Builtins list should contain expected types."""
        expected = [
            "none",
            "str_",
            "bytes_",
            "float_",
            "int_",
            "class_",
            "list",
            "tuple",
            "tuple2",
            "dict",
            "set",
            "frozenset",
            "bool_",
        ]
        assert gx.builtins == expected

    def test_builtins_count(self, gx):
        """Builtins list should have expected count."""
        assert len(gx.builtins) == 13


class TestMergedInheritance:
    """Tests for merged inheritance type information."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_merged_inh_initially_empty(self, gx):
        """merged_inh should be empty initially."""
        assert len(gx.merged_inh) == 0

    def test_merged_inh_modifiable(self, gx):
        """merged_inh should be modifiable."""
        gx.merged_inh["test_key"] = {("type1", 0), ("type2", 1)}
        assert "test_key" in gx.merged_inh
        assert len(gx.merged_inh["test_key"]) == 2


class TestBuildConfiguration:
    """Tests for build configuration options used by cpp.py."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_wrap_around_check_default(self, gx):
        """wrap_around_check should default to True."""
        assert gx.wrap_around_check is True

    def test_bounds_checking_default(self, gx):
        """bounds_checking should default to True."""
        assert gx.bounds_checking is True

    def test_assertions_default(self, gx):
        """assertions should default to True."""
        assert gx.assertions is True

    def test_nogc_default(self, gx):
        """nogc should default to False."""
        assert gx.nogc is False

    def test_backtrace_default(self, gx):
        """backtrace should default to False."""
        assert gx.backtrace is False


class TestIntegerTypes:
    """Tests for integer type configuration."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_int32_default(self, gx):
        """int32 should default to False."""
        assert gx.int32 is False

    def test_int64_default(self, gx):
        """int64 should default to False."""
        assert gx.int64 is False

    def test_int128_default(self, gx):
        """int128 should default to False."""
        assert gx.int128 is False

    def test_int32_settable(self, gx):
        """int32 should be settable."""
        gx.int32 = True
        assert gx.int32 is True

    def test_int64_settable(self, gx):
        """int64 should be settable."""
        gx.int64 = True
        assert gx.int64 is True


class TestFloatTypes:
    """Tests for float type configuration."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_float32_default(self, gx):
        """float32 should default to False."""
        assert gx.float32 is False

    def test_float64_default(self, gx):
        """float64 should default to False."""
        assert gx.float64 is False


class TestTemplates:
    """Tests for template tracking."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_templates_counter_initial(self, gx):
        """templates counter should start at 0."""
        assert gx.templates == 0

    def test_templates_counter_modifiable(self, gx):
        """templates counter should be modifiable."""
        gx.templates = 5
        assert gx.templates == 5


class TestEntityTracking:
    """Tests for entity tracking used during code generation."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_allfuncs_empty_initially(self, gx):
        """allfuncs should be empty initially."""
        assert len(gx.allfuncs) == 0

    def test_allclasses_empty_initially(self, gx):
        """allclasses should be empty initially."""
        assert len(gx.allclasses) == 0

    def test_allvars_empty_initially(self, gx):
        """allvars should be empty initially."""
        assert len(gx.allvars) == 0

    def test_modules_empty_initially(self, gx):
        """modules should be empty initially."""
        assert len(gx.modules) == 0


def test_all():
    """Run all tests in this module."""
    pytest.main([__file__, "-v"])
