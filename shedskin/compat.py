'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour; License GNU GPL version 3 (See LICENSE)

compat.py: python2/3 related compatibility

'''

import ast


# sub-class to pass *args, as was possible with python2 compiler.ast..

class NodeVisitor(ast.NodeVisitor):

    def visit(self, node, *args):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, *args)

    def generic_visit(self, node, *args):  # TODO update to newer ast
        for child in node.getChildNodes():
            self.visit(child, *args)
