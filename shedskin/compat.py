'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour; License GNU GPL version 3 (See LICENSE)

compat.py: python2/3 related compatibility

'''

try:
    from compiler.ast import Stmt

except ModuleNotFoundError:
    pass

import ast

try:
    from compiler import parse

    def parse_expr(s):
        return parse(s).node.nodes[0]

    OLD = True

except ModuleNotFoundError:
    from ast import parse

    def parse_expr(s):
        return parse(s).body[0]

    OLD = False

NODE_MAP = {
    'From': 'ImportFrom',
}

# sub-class NodeVisitor to pass *args

class NodeVisitor(ast.NodeVisitor):

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


if OLD:
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

else:
    def getChildNodes(node):
        return tuple(ast.iter_child_nodes(node))

    def filter_statements(node, cl):
        return [n for n in ast.iter_child_nodes(node) if isinstance(n, cl)]

    def get_docstring(node):
        return ast.get_docstring(node)

    def get_formals(node):
        return [arg.arg for arg in node.args.args]
