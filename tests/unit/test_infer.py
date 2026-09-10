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


class TestBackupRestore:
    """Tests for backup_network / restore_network round-tripping.

    backup_network stores empty sets as a single shared immutable marker
    instead of copying one empty set per node, so restore_network has to
    hand back real, independent, mutable sets.
    """

    def _network(self, gx):
        """Three nodes, one edge a -> b, and a mix of empty and non-empty
        type sets."""
        a = infer.CNode(gx, None, ast.Name(id="a", ctx=ast.Load()))
        b = infer.CNode(gx, None, ast.Name(id="b", ctx=ast.Load()))
        c = infer.CNode(gx, None, ast.Name(id="c", ctx=ast.Load()))
        gx.types[a] = {("cls", 0)}
        gx.types[b] = set()
        gx.types[c] = set()
        infer.in_out(a, b)
        return a, b, c

    def test_restore_undoes_type_and_edge_changes(self, gx):
        """restore_network should put types and in_/out back as they were."""
        a, b, c = self._network(gx)
        backup = infer.backup_network(gx)

        gx.types[a].add(("late", 0))
        gx.types[b].add(("late", 0))
        infer.in_out(b, c)

        infer.restore_network(gx, backup)

        assert gx.types[a] == {("cls", 0)}
        assert gx.types[b] == set()
        assert a.out == {b}
        assert b.in_ == {a}
        assert b.out == set()
        assert c.in_ == set()

    def test_restore_drops_nodes_created_afterwards(self, gx):
        """Nodes added after the backup should be gone again."""
        a, _b, _c = self._network(gx)
        backup = infer.backup_network(gx)

        d = infer.CNode(gx, None, ast.Name(id="d", ctx=ast.Load()))
        gx.types[d] = {("late", 0)}

        infer.restore_network(gx, backup)

        assert d not in gx.types
        assert a in gx.types

    def test_restored_sets_are_mutable_and_independent(self, gx):
        """Restored sets must be real sets, not the shared empty marker."""
        a, b, c = self._network(gx)
        backup = infer.backup_network(gx)

        gx.types[b].add(("late", 0))
        infer.in_out(b, c)

        infer.restore_network(gx, backup)

        for node in (a, b, c):
            assert isinstance(gx.types[node], set)
            assert isinstance(node.in_, set)
            assert isinstance(node.out, set)
            # mutating one restored set must not affect any other
            gx.types[node].add(("mutable", 0))
            node.in_.add(a)
            node.out.add(a)

        assert infer.EMPTY_SET == set()

    def test_backup_is_not_aliased(self, gx):
        """Mutating the live network must not disturb the snapshot."""
        a, b, _c = self._network(gx)
        backup = infer.backup_network(gx)

        gx.types[a].add(("late", 0))
        gx.types[b].add(("late", 0))
        a.out.clear()

        beforetypes, _constr, beforeinout, _cnode = backup
        assert beforetypes[a] == {("cls", 0)}
        assert beforetypes[b] == set()
        assert beforeinout[a][1] == {b}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
