# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
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
from typing import Any, List, Tuple, Union

from . import config


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


def is_none(node: ast.AST) -> bool:
    """Check if a node is the None constant"""
    if isinstance(node, ast.Name) and node.id == "None":
        return True
    else:
        if isinstance(node, ast.Constant) and node.value is None:
            return True
    return False


def is_literal(node: ast.AST) -> bool:
    """Check if a node is a literal"""
    # RESOLVE: Can all UnaryOps be literals, Not?, Invert?
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        node = node.operand
    # RESOLVE: Isn't Str node also literal
    return isinstance(node, ast.Num) and isinstance(node.n, (int, float))


def is_fastfor(node: Union[ast.For, ast.comprehension]) -> bool:
    """Check if a node is a fast for loop"""
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id in ["range", "xrange"]
    )


def is_enumerate(node: Union[ast.For, ast.comprehension]) -> bool:
    """Check if a node is an enumerate loop"""
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "enumerate"
        and len(node.iter.args) == 1
        and is_assign_list_or_tuple(node.target)
    )


def is_zip2(node: Union[ast.For, ast.comprehension]) -> bool:
    """Check if a node is a zip loop with two arguments"""
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "zip"
        and len(node.iter.args) == 2
        and is_assign_list_or_tuple(node.target)
    )


# --- recursively determine (lvalue, rvalue) pairs in assignment expressions
def assign_rec(left: ast.AST, right: ast.AST) -> List[Tuple[ast.AST, ast.AST]]:
    """Recursively determine (lvalue, rvalue) pairs in assignment expressions"""
    if is_assign_list_or_tuple(left) and isinstance(right, (ast.Tuple, ast.List)):
        assert isinstance(left, (ast.Tuple, ast.List))
        pairs = []
        for lvalue, rvalue in zip(left.elts, right.elts):
            pairs += assign_rec(lvalue, rvalue)
        return pairs
    else:
        return [(left, right)]


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
