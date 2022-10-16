'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour; License GNU GPL version 3 (See LICENSE)

compat.py: python2/3 related compatibility

'''

try:
    from compiler import parse
    from compiler.ast import Stmt, Assign, AssName, Discard, Const, Return, \
        Function as FunctionDef, Class as ClassDef, Keyword, UnarySub, UnaryAdd

    OLD = True

except ModuleNotFoundError:
    import ast
    from ast import parse, Assign, Name, Expr, Constant, Starred, UnaryOp

    OLD = False

NODE_MAP = {
    'From': 'ImportFrom',
    'Function': 'FunctionDef',
    'Class': 'ClassDef',
    'CallFunc': 'Call',
    'Getattr': 'Attribute',
    'Const': 'Constant',
}

# sub-class NodeVisitor to pass *args

class NodeVisitor:
    def visit(self, node, *args):
        class_name = node.__class__.__name__
        if class_name in NODE_MAP:
            class_name = NODE_MAP[class_name]

        adapter = getattr(self, 'adapt_' + class_name, None)
        if adapter:
            adapter(node)

        visitor = getattr(self, 'visit_' + class_name, self.generic_visit)
        return visitor(node, *args)

    def generic_visit(self, node, *args):
        for child in getChildNodes(node):
            self.visit(child, *args)

    if OLD:
        def adapt_ImportFrom(self, node):
            node.module = node.modname

        def adapt_Name(self, node):
            node.id = node.name

def filter_rec(node, cl):
    result = []

    if isinstance(node, cl):
        result.append(node)

    elif isinstance(node, list):
        for child in node:
             result.extend(filter_rec(child, cl))

    else:
        for child in getChildNodes(node):
             result.extend(filter_rec(child, cl))

    return result

if OLD:
    def parse_expr(s):
        return parse(s).node.nodes[0]

    def getChildNodes(node):
        return node.getChildNodes()

    def filter_statements(node, cl):
        result = []
        for child in node.getChildNodes():
            if isinstance(child, Stmt):
                result.extend([n for n in child.nodes if isinstance(n, cl)])
        return result

    def get_docstring(node):
        return node.doc

    def get_formals(node):
        return node.argnames

    def get_defaults(node):
        return node.defaults

    def get_assnames(node):
        return [n.name for n in filter_rec(node.nodes, AssName)]

    def get_body(node):
        if isinstance(node, (FunctionDef, ClassDef)):
            return node.code
        else:
            return node.node

    def get_statements(node):
        if isinstance(node, Stmt):
            return [n.expr if isinstance(n, Discard) else n for n in node.nodes]
        else:
            return [node]

    def is_const(node):
        return isinstance(node, Const)

    def const_value(node):
        return node.value

    def get_id(node):
        return node.name

    def get_func(node):
        return node.node

    def attr_value(node):
        return node.expr

    def attr_attr(node):
        return node.attrname

    def get_args(node):
        args = []
        for arg in node.args:
            if isinstance(arg, Keyword):
                arg = arg.expr
            args.append(arg)

        if node.star_args:
            args.append(node.star_args)

        if node.dstar_args:
            args.append(node.dstar_args)

        return args

    def get_elts(node):
        return node.nodes

    def is_unary(node):
        return isinstance(node, (UnarySub, UnaryAdd))

    def get_targets(node):
        return node.nodes

    def get_value(node):
        return node.expr

    long_ = long
    unicode_ = unicode

else:
    def parse_expr(s):
        return parse(s).body[0]

    def getChildNodes(node):
        return tuple(ast.iter_child_nodes(node))

    def filter_statements(node, cl):
        return [n for n in ast.iter_child_nodes(node) if isinstance(n, cl)]

    def get_docstring(node):
        return ast.get_docstring(node)

    def get_formals(node):
        return [arg.arg for arg in node.args.args]

    def get_defaults(node):
        return node.args.defaults

    def get_assnames(node):
        return [n.id for n in filter_rec(node.targets, Name)]

    def get_body(node):
        return node.body

    def get_statements(node):
        return node

    def is_const(node):
        return isinstance(node, Expr) and isinstance(node.value, Constant)

    def const_value(node):
        return node.value.value

    def get_id(node):
        return node.id

    def get_func(node):
        return node.func

    def attr_value(node):
        return node.value

    def attr_attr(node):
        return node.attr

    def get_args(node):
        args = []
        for arg in node.args:
            if isinstance(arg, Starred):
                args.append(arg.value)

        if hasattr(node, 'keywords'):
            for arg in node.keywords:
                args.append(arg.expr)

        return args

    def get_elts(node):
        return node.elts

    def is_unary(node):
        return isinstance(node, UnaryOp)

    def get_targets(node):
        return node.targets

    def get_value(node):
        return node.value

    long_ = int
    unicode_ = str
