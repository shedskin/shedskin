# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""Unit tests for shedskin.ast_utils, focused on the builtin-name checks
used to select fast-path for loop code generation (range/enumerate/zip).

These functions used to check only the *identifier string* of the called
name (e.g. `node.iter.func.id == "enumerate"`), so a local variable,
parameter, or nested function that happened to share a builtin's name was
incorrectly treated as the builtin itself. That silently miscompiled
programs which shadow 'range', 'enumerate' or 'zip'.
"""

import ast

from shedskin import ast_utils


class FakeVar:
    """Stand-in for python.Variable; identity is all lookup_var cares
    about here."""


class FakeScope:
    """Stand-in for python.Function/Class: only 'vars' and 'parent' are
    read by python.smart_lookup_var for a scope with no enclosing
    parent."""

    def __init__(self, vars=None):
        self.vars = vars or {}
        self.parent = None


class FakeMv:
    """Stand-in for graph.ModuleVisitor: only the attributes
    python.smart_lookup_var falls back to once the scope chain is
    exhausted without finding the name."""

    def __init__(self):
        self.exc_names = {}
        self.current_with_vars = []
        self.globals = {}


def _for_node(call_name, target=("a", "b"), n_args=1):
    """Build a minimal `for <target> in <call_name>(...)` ast.For node."""
    args = [ast.Name(id=f"arg{i}", ctx=ast.Load()) for i in range(n_args)]
    return ast.For(
        target=ast.Tuple(
            elts=[ast.Name(id=t, ctx=ast.Store()) for t in target],
            ctx=ast.Store(),
        ),
        iter=ast.Call(
            func=ast.Name(id=call_name, ctx=ast.Load()), args=args, keywords=[]
        ),
        body=[ast.Pass()],
        orelse=[],
    )


class TestIsEnumerate:
    def test_true_for_genuine_builtin(self):
        node = _for_node("enumerate")
        scope = FakeScope()
        assert ast_utils.is_enumerate(node, scope, mv=FakeMv()) is True

    def test_false_when_shadowed_by_local(self):
        """A local named 'enumerate' (e.g. a parameter) must not be
        mistaken for the builtin."""
        node = _for_node("enumerate")
        scope = FakeScope(vars={"enumerate": FakeVar()})
        assert ast_utils.is_enumerate(node, scope, mv=FakeMv()) is False

    def test_false_for_different_name(self):
        node = _for_node("not_enumerate")
        scope = FakeScope()
        assert ast_utils.is_enumerate(node, scope, mv=FakeMv()) is False

    def test_no_context_falls_back_to_permissive(self):
        """Without parent/mv context, shadowing can't be checked, so the
        (pre-fix) name-only behavior is preserved for unmigrated callers."""
        node = _for_node("enumerate")
        assert ast_utils.is_enumerate(node) is True


class TestIsZip2:
    def test_true_for_genuine_builtin(self):
        node = _for_node("zip", n_args=2)
        scope = FakeScope()
        assert ast_utils.is_zip2(node, scope, mv=FakeMv()) is True

    def test_false_when_shadowed_by_local(self):
        node = _for_node("zip", n_args=2)
        scope = FakeScope(vars={"zip": FakeVar()})
        assert ast_utils.is_zip2(node, scope, mv=FakeMv()) is False


class TestZipArity:
    def test_two_and_three_args(self):
        scope = FakeScope()
        node = _for_node("zip", n_args=2)
        assert ast_utils.zip_arity(node, scope, mv=FakeMv()) == 2
        node = _for_node("zip", target=("a", "b", "c"), n_args=3)
        assert ast_utils.zip_arity(node, scope, mv=FakeMv()) == 3
        assert ast_utils.is_zip3(node, scope, mv=FakeMv()) is True
        assert ast_utils.is_zip2(node, scope, mv=FakeMv()) is False

    def test_other_arg_counts(self):
        scope = FakeScope()
        node = _for_node("zip", target=("a",), n_args=1)
        assert ast_utils.zip_arity(node, scope, mv=FakeMv()) == 0
        node = _for_node("zip", target=("a", "b", "c", "d"), n_args=4)
        assert ast_utils.zip_arity(node, scope, mv=FakeMv()) == 0

    def test_target_count_mismatch(self):
        # 'for a, b, c in zip(x, y)' takes the general path (unpack check)
        scope = FakeScope()
        node = _for_node("zip", target=("a", "b", "c"), n_args=2)
        assert ast_utils.zip_arity(node, scope, mv=FakeMv()) == 0
        node = _for_node("zip", target=("a", "b"), n_args=3)
        assert ast_utils.zip_arity(node, scope, mv=FakeMv()) == 0

    def test_keywords(self):
        # zip(x, y, strict=True) takes the general path (length check)
        scope = FakeScope()
        node = _for_node("zip", n_args=2)
        node.iter.keywords = [ast.keyword(arg="strict", value=ast.Constant(True))]
        assert ast_utils.zip_arity(node, scope, mv=FakeMv()) == 0

    def test_shadowed(self):
        node = _for_node("zip", target=("a", "b", "c"), n_args=3)
        scope = FakeScope(vars={"zip": FakeVar()})
        assert ast_utils.zip_arity(node, scope, mv=FakeMv()) == 0


class TestIsFastfor:
    def test_true_for_genuine_range(self):
        node = _for_node("range", target=("i",))
        scope = FakeScope()
        assert ast_utils.is_fastfor(node, scope, mv=FakeMv()) is True

    def test_false_when_shadowed_by_local(self):
        node = _for_node("range", target=("i",))
        scope = FakeScope(vars={"range": FakeVar()})
        assert ast_utils.is_fastfor(node, scope, mv=FakeMv()) is False

    def test_true_for_xrange(self):
        node = _for_node("xrange", target=("i",))
        scope = FakeScope()
        assert ast_utils.is_fastfor(node, scope, mv=FakeMv()) is True
