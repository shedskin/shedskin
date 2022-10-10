'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour; License GNU GPL version 3 (See LICENSE)

compat.py: python2/3 related compatibility

'''

import ast

try:
    from compiler import parse

    def parse_expr(s):
        return parse(s).node.nodes[0]

except ModuleNotFoundError:
    from ast import parse

    def parse_expr(s):
        return parse(s).body[0]

NODE_MAP = {
    'From': 'ImportFrom',
}

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

    def generic_visit(self, node, *args):  # TODO update to newer ast
        for child in node.getChildNodes():
            self.visit(child, *args)

    def adapt_ImportFrom(self, node):
#        node.names = [(alias.name, alias.asname) for alias in node.names]
        node.module = node.modname
