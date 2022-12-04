'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)

'''
import ast


def is_assign_list_or_tuple(node):
    return isinstance(node, (ast.Tuple, ast.List)) and isinstance(node.ctx, ast.Store)


def is_assign_tuple(node):
    return isinstance(node, ast.Tuple) and isinstance(node.ctx, ast.Store)


def is_assign_attribute(node):
    return isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store)


def is_constant(node):
    return isinstance(node, (ast.Str, ast.Num)) or node.__class__.__name__ == 'Constant'

def is_none(node):
    return (isinstance(node, ast.Name) and node.id == 'None' or
            node.__class__.__name__ == 'Constant' and node.value is None)


def handle_with_vars(var):
    if isinstance(var, ast.Name):
        return [var.id]
    elif isinstance(var, (ast.List, ast.Tuple)):
        result = []
        for elt in var.elts:
            result.extend(handle_with_vars(elt))


def orelse_to_node(node):
    if isinstance(node.orelse, ast.AST):
        return ast.AST
    elif isinstance(node.orelse, list) and len(node.orelse) > 0:
        return node.orelse[0]
    else:
        assert False


def get_arg_name(node, is_tuple_expansion=False):
    if hasattr(node, 'arg'):
        assert isinstance(node.arg, str), 'non-arg string %s' % type(node.arg)
        return node.arg

    if isinstance(node, ast.Tuple):
        return tuple(get_arg_name(child, is_tuple_expansion=True) for child in node.elts)
    elif isinstance(node, ast.Name):
        assert is_tuple_expansion and type(node.ctx) == ast.Store or type(node.ctx) == ast.Param
        return node.id
    elif isinstance(node, str):
        return node
    else:
        assert False, "Unexpected argument type got %s" % type(node)


def extract_argnames(arg_struct):
    argnames = [get_arg_name(arg) for arg in arg_struct.args]
    if arg_struct.vararg:
        argnames.append(get_arg_name(arg_struct.vararg))
    # PY3: kwonlyargs
    if arg_struct.kwarg:
        argnames.append(arg_struct.kwarg)
    return argnames


def make_arg_list(argnames, vararg=None, kwonlyargs=[], kwarg=None, defaults=[], kw_defaults=[]):
    try:
        ast.arg

        args = [ast.arg(a) for a in argnames]
        vararg = ast.arg(vararg) if vararg else None
        kwarg = ast.arg(kwarg) if kwarg else None

        # PY3: what about kwonlyargs, kw_defaults, posonlyargs?
        return ast.arguments([], args, vararg, [], [], kwarg, defaults)

    except AttributeError:
        args = [ast.Name(argname, ast.Param()) for argname in argnames]
        return ast.arguments(args, vararg, kwarg, defaults)


def make_call(func, args=[], keywords=[], starargs=None, kwargs=None):
    try:
        return ast.Call(func, args, keywords, starargs, kwargs)
    except TypeError:
        # PY3: Incorporate starargs and kwargs into args and keywords respectively
        return ast.Call(func, args, keywords)

def has_star_kwarg(node):
    if hasattr(node, 'starargs'):
       return bool(node.starargs or node.kwargs)

    for arg in node.args:
        if arg.__class__.__name__ == 'Starred':
            return True

    for kw in node.keywords:
        if kw.arg is None:
            return True

    return False

def get_starargs(node):
    if hasattr(node, 'starargs'):
       return node.starargs

    for arg in node.args:
        if arg.__class__.__name__ == 'Starred':
            return arg.value

def get_arg_nodes(node):
    args = []

    for arg in node.args:
        if arg.__class__.__name__ == 'Starred':
            arg = arg.value
        args.append(arg)

    if node.keywords:
        args.extend([kw.value for kw in node.keywords])

    if hasattr(node, 'starargs') and node.starargs:
        if node.starargs:
            args.append(node.starargs)  # partially allowed in builtins

    if hasattr(node, 'kwargs') and node.kwargs:
        args.append(node.kwargs)

    return args


def parse_expr(s):
    return ast.parse(s).body[0]


class BaseNodeVisitor(object):
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
        assert isinstance(node, ast.AST), "Expected node of type ast.AST, got node of type %s" % type(node)
        method = 'visit_' + node.__class__.__name__
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
