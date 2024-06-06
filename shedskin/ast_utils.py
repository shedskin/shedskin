"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2023 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)

"""
import ast


def is_assign_list_or_tuple(node) -> bool:
    return isinstance(node, (ast.Tuple, ast.List)) and isinstance(node.ctx, ast.Store)


def is_assign_tuple(node) -> bool:
    return isinstance(node, ast.Tuple) and isinstance(node.ctx, ast.Store)


def is_assign_attribute(node) -> bool:
    return isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store)


def is_constant(node) -> bool:  # TODO simplify?
    return isinstance(node, (ast.Str, ast.Num)) or node.__class__.__name__ == "Constant"


def is_none(node) -> bool:
    return (
        isinstance(node, ast.Name)
        and node.id == "None"
        or node.__class__.__name__ == "Constant"
        and node.value is None
    )


def is_literal(node) -> bool:
    # RESOLVE: Can all UnaryOps be literals, Not?, Invert?
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        node = node.operand
    # RESOLVE: Isn't Str node also literal
    return isinstance(node, ast.Num) and isinstance(node.n, (int, float))


def is_fastfor(node) -> bool:
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id in ["range", "xrange"]
    )


def is_enumerate(node) -> bool:
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "enumerate"
        and len(node.iter.args) == 1
        and is_assign_list_or_tuple(node.target)
    )


def is_zip2(node) -> bool:
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "zip"
        and len(node.iter.args) == 2
        and is_assign_list_or_tuple(node.target)
    )

# --- recursively determine (lvalue, rvalue) pairs in assignment expressions
def assign_rec(left, right):
    if is_assign_list_or_tuple(left) and isinstance(
        right, (ast.Tuple, ast.List)
    ):
        pairs = []
        for lvalue, rvalue in zip(left.elts, right.elts):
            pairs += assign_rec(lvalue, rvalue)
        return pairs
    else:
        return [(left, right)]


def aug_msg(node, msg):
    if hasattr(node, "augment"):
        return "__i" + msg + "__"
    return "__" + msg + "__"


class BaseNodeVisitor:
    """
    Copy of ast.NodeVisitor with added *args argument to visit functions

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

    def visit(self, node, *args):
        """Visit a node."""
        assert isinstance(
            node, ast.AST
        ), "Expected node of type ast.AST, got node of type %s" % type(node)
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, None)
        if visitor:
            visitor(node, *args)
        else:
            self.generic_visit(node, *args)

    def generic_visit(self, node, *args):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item, *args)
            elif isinstance(value, ast.AST):
                self.visit(value, *args)
