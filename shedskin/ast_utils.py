# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2026 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.ast_utils: Functions and classes which operate on ast nodes.

This module provides utility functions and classes for working with abstract syntax
trees (ASTs) in Python. It includes functions to:

- Check node types and contexts:
  - `is_assign_list_or_tuple()`: Check if node is list/tuple assignment
  - `is_assign_tuple()`: Check if node is tuple assignment
  - `is_assign_attribute()`: Check if node is attribute assignment
  -` is_constant()`: Check if node is a constant value
  - `is_none()`: Check if node represents None
  - `is_literal()`: Check if node is a numeric literal

The functions help analyze and validate Python AST nodes during the compilation
process. They abstract away the details of AST node type checking to make the
compiler code more readable and maintainable.

Key use cases:
- Validating assignment targets and contexts
- Identifying constant values and literals
- Supporting type inference and code generation

The module is used by other parts of the compiler to analyze Python source code
and generate equivalent C++ code.

Note that ast.unparse can be very useful during debugging.
"""

import ast
from typing import TYPE_CHECKING, Any, Optional, Union

from . import config, python

if TYPE_CHECKING:
    from . import graph


def is_assign_list_or_tuple(node: ast.AST) -> bool:
    """Check if a node is an assignment to a list or tuple"""
    return isinstance(node, (ast.Tuple, ast.List)) and isinstance(node.ctx, ast.Store)


def is_assign_tuple(node: ast.AST) -> bool:
    """Check if a node is an assignment to a tuple"""
    return isinstance(node, ast.Tuple) and isinstance(node.ctx, ast.Store)


def is_assign_attribute(node: ast.AST) -> bool:
    """Check if a node is an assignment to an attribute"""
    return isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store)


def is_constant(node: ast.AST) -> bool:
    """Check if a node is a constant"""
    return isinstance(node, ast.Constant)


def is_str(node: ast.AST) -> bool:
    """Check if a node is a str constant"""
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def is_num(node: ast.AST) -> bool:
    """Check if a node is a numeric constant"""
    return isinstance(node, ast.Constant) and isinstance(node.value, (int, float))


def is_bytes(node: ast.AST) -> bool:
    """Check if a node is a bytes constant"""
    return isinstance(node, ast.Constant) and isinstance(node.value, bytes)


def is_none(node: ast.AST) -> bool:
    """Check if a node is the None constant"""
    if isinstance(node, ast.Name) and node.id == "None":
        return True
    else:
        if isinstance(node, ast.Constant) and node.value is None:
            return True
    return False


def negative_num_value(node: ast.AST) -> Optional[Union[int, float]]:
    """Value of a syntactically negative numeric literal, else None.

    '-1' parses as UnaryOp(USub, Constant(1)) rather than Constant(-1), so both
    spellings have to be recognized.
    """
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value < 0:
                return value
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        operand = node.operand
        if isinstance(operand, ast.Constant):
            negated = operand.value
            if isinstance(negated, (int, float)) and not isinstance(negated, bool):
                if negated > 0:
                    return -negated
    return None


def float_negative_exponent(node: ast.expr) -> ast.expr:
    """Retype a negative int literal exponent as the equivalent float.

    'int ** int' is typed as int, but python returns a float when the exponent
    is negative: 10 ** -1 is 0.1. That depends on the exponent's *value*, which
    inference cannot see -- except for a literal, where the sign is right
    there. Handing back a float literal gives exactly python's result via
    'int_ ** float_', and matches how cpython itself defers to float pow here.
    Anything else is returned unchanged, including an already-float literal, so
    this is safe to apply more than once.
    """
    value = negative_num_value(node)
    if isinstance(value, int):
        return ast.copy_location(ast.Constant(value=float(value)), node)
    return node


def is_literal(node: ast.AST) -> bool:
    """Check if a node is a literal"""
    # RESOLVE: Can all UnaryOps be literals, Not?, Invert?
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        node = node.operand
    # RESOLVE: Isn't Str node also literal
    return is_num(node)


def _is_shadowed(
    name: str,
    parent: Optional["python.AllParent"],
    mv: Optional["graph.ModuleVisitor"],
) -> bool:
    """Check whether 'name' is bound to something other than the builtin of
    that name in the current scope.

    A parameter, local variable, or nested function/class named e.g.
    'range', 'enumerate' or 'zip' shadows the builtin: calls to it must not
    be special-cased as if they were calls to the builtin. Without 'parent'
    (the enclosing function/class) and 'mv' (the module visitor) to look the
    name up in, no shadowing information is available, so nothing is
    reported as shadowed -- callers that can supply this context should
    always do so.
    """
    if mv is None:
        return False
    return python.lookup_var(name, parent, mv) is not None


def is_fastfor(
    node: Union[ast.For, ast.comprehension],
    parent: Optional["python.AllParent"] = None,
    mv: Optional["graph.ModuleVisitor"] = None,
) -> bool:
    """Check if a node is a fast for loop"""
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id in ["range", "xrange"]
        and not _is_shadowed(node.iter.func.id, parent, mv)
    )


def is_enumerate(
    node: Union[ast.For, ast.comprehension],
    parent: Optional["python.AllParent"] = None,
    mv: Optional["graph.ModuleVisitor"] = None,
) -> bool:
    """Check if a node is an enumerate loop"""
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "enumerate"
        and not _is_shadowed("enumerate", parent, mv)
        and len(node.iter.args) == 1
        and not node.iter.keywords  # TODO start arg not supported
        and is_assign_list_or_tuple(node.target)
    )


def is_zip2(
    node: Union[ast.For, ast.comprehension],
    parent: Optional["python.AllParent"] = None,
    mv: Optional["graph.ModuleVisitor"] = None,
) -> bool:
    """Check if a node is a zip loop with two arguments"""
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "zip"
        and not _is_shadowed("zip", parent, mv)
        and len(node.iter.args) == 2
        and is_assign_list_or_tuple(node.target)
    )


# --- recursively determine (lvalue, rvalue) pairs in assignment expressions
def assign_rec(left: ast.AST, right: ast.AST) -> list[tuple[ast.AST, ast.AST]]:
    """Recursively determine (lvalue, rvalue) pairs in assignment expressions"""
    if is_assign_list_or_tuple(left) and isinstance(right, (ast.Tuple, ast.List)):
        assert isinstance(left, (ast.Tuple, ast.List))
        pairs = []
        for lvalue, rvalue in zip(left.elts, right.elts):
            pairs += assign_rec(lvalue, rvalue)
        return pairs
    else:
        return [(left, right)]


def check_assign_arity(left: ast.AST, right: ast.AST) -> Optional[tuple[int, int]]:
    """Recursively check that a literal (list/tuple) unpacking target and a
    literal (list/tuple) right-hand side have matching arity.

    `assign_rec` pairs up (lvalue, rvalue) elements with `zip()`, which
    silently truncates to the shorter side, so e.g. `a, b = [1, 2, 3]` or
    `a, b, c = [1, 2]` would otherwise be accepted without any check
    (unlike CPython, which raises ValueError at runtime).

    Returns (expected, got) for the first arity mismatch found, or None if
    every literal-vs-literal pair matches. Only literal-vs-literal
    unpacking is checked here (both sides need a known length); unpacking
    from a non-literal iterable is still checked at runtime via
    __SS_UNPACK_CHECK.
    """
    if is_assign_list_or_tuple(left) and isinstance(right, (ast.Tuple, ast.List)):
        assert isinstance(left, (ast.Tuple, ast.List))
        if len(left.elts) != len(right.elts):
            return (len(left.elts), len(right.elts))
        for lvalue, rvalue in zip(left.elts, right.elts):
            mismatch = check_assign_arity(lvalue, rvalue)
            if mismatch:
                return mismatch
    return None


def aug_msg(gx: "config.GlobalInfo", node: ast.BinOp, msg: str) -> str:
    """Generate an augmented assignment message"""
    if node in gx.augment:
        return "__i" + msg + "__"
    return "__" + msg + "__"


class BaseNodeVisitor:
    """Copy of ast.NodeVisitor with added *args argument to visit functions

    A node visitor base class that walks the abstract syntax tree and calls a
    visitor function for every node found.  This function may return a value
    which is forwarded by the `visit` method.

    This class is meant to be subclassed, with the subclass adding visitor
    methods.

    Per default the visitor functions for the nodes are ``'visit_'`` +
    class name of the node.  So a `TryFinally` node visit function would
    be `visit_TryFinally`.  This behavior can be changed by overriding
    the `visit` method.  If no visitor function exists for a node
    (return value `None`) the `generic_visit` visitor is used instead.
    """

    def visit(self, node: ast.AST, *args: Any) -> None:
        """Visit a node."""
        assert isinstance(node, ast.AST), (
            "Expected node of type ast.AST, got node of type %s" % type(node)
        )
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, None)
        if visitor:
            visitor(node, *args)
        else:
            self.generic_visit(node, *args)

    def generic_visit(self, node: ast.AST, *args: Any) -> None:
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, *args)
            elif isinstance(value, ast.AST):
                self.visit(value, *args)
