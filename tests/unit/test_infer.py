# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.infer module."""

import argparse
import ast

import pytest

from shedskin.config import GlobalInfo
from shedskin import infer


class TestConstants:
    """Tests for inference constants."""

    def test_incremental_flags(self):
        """Incremental analysis flags should have expected values."""
        assert infer.INCREMENTAL is True
        assert infer.INCREMENTAL_FUNCS == 5
        assert infer.INCREMENTAL_DATA is True
        assert infer.INCREMENTAL_ALLOCS == 1

    def test_limits(self):
        """Analysis limits should have expected values."""
        assert infer.MAXITERS == 30
        assert infer.CPA_LIMIT == 10


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


class TestConstraintGraph:
    """Tests for constraint graph operations."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_cnode_dict_empty_initially(self, gx):
        """cnode dictionary should be empty initially."""
        assert len(gx.cnode) == 0

    def test_constraints_empty_initially(self, gx):
        """constraints set should be empty initially."""
        assert len(gx.constraints) == 0

    def test_types_dict_empty_initially(self, gx):
        """types dictionary should be empty initially."""
        assert len(gx.types) == 0


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


class TestTypeInferenceState:
    """Tests for type inference state tracking."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_iterations_tracking(self, gx):
        """iterations counter should be modifiable."""
        assert gx.iterations == 0
        gx.iterations = 5
        assert gx.iterations == 5

    def test_cpa_limit_tracking(self, gx):
        """cpa_limit should be modifiable."""
        gx.cpa_limit = 15
        assert gx.cpa_limit == 15

    def test_cpa_clean_flag(self, gx):
        """cpa_clean flag should be modifiable."""
        assert gx.cpa_clean is False
        gx.cpa_clean = True
        assert gx.cpa_clean is True

    def test_cpa_limited_flag(self, gx):
        """cpa_limited flag should be modifiable."""
        assert gx.cpa_limited is False
        gx.cpa_limited = True
        assert gx.cpa_limited is True

    def test_added_funcs_counter(self, gx):
        """added_funcs counter should be modifiable."""
        gx.added_funcs = 10
        assert gx.added_funcs == 10

    def test_added_allocs_counter(self, gx):
        """added_allocs counter should be modifiable."""
        gx.added_allocs = 3
        assert gx.added_allocs == 3

    def test_alloc_info_dict(self, gx):
        """alloc_info should be a modifiable dictionary."""
        assert isinstance(gx.alloc_info, dict)
        gx.alloc_info = {"test": "value"}  # type: ignore
        assert gx.alloc_info == {"test": "value"}

    def test_merged_inh_dict(self, gx):
        """merged_inh should be a modifiable dictionary."""
        assert isinstance(gx.merged_inh, dict)
        gx.merged_inh = {"key": {("value", 0)}}
        assert "key" in gx.merged_inh


class TestMaxHits:
    """Tests for maxhits termination counter."""

    @pytest.fixture
    def gx(self):
        """Create a GlobalInfo instance for testing."""
        options = argparse.Namespace()
        return GlobalInfo(options)

    def test_maxhits_initial_value(self, gx):
        """maxhits should start at 0."""
        assert gx.maxhits == 0

    def test_maxhits_increment(self, gx):
        """maxhits should be incrementable."""
        gx.maxhits += 1
        assert gx.maxhits == 1

        gx.maxhits += 1
        assert gx.maxhits == 2


def test_all():
    """Run all tests in this module."""
    pytest.main([__file__, "-v"])
