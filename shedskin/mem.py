# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2025 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)

import ast

from typing import (IO, TYPE_CHECKING, Any, Dict, Iterator, List, Optional,
                    Tuple, TypeAlias, Union)

from . import ast_utils
from . import python

Parent: TypeAlias = Union["python.Class", "python.Function"]


class ConnectionGraphVisitor(ast_utils.BaseNodeVisitor):
    """Visitor for generating connection graph from Python ASTs"""

    def __init__(
        self, gx: "config.GlobalInfo", module: "python.Module"
    ):
        self.gx = gx
        self.module = module
        self.mv = module.mv

    def visit_Return(
        self, node: ast.Return, func: Optional["python.Function"] = None
    ) -> None:
        if isinstance(node.value, ast.Name):
            print('return', func, python.lookup_var(node.value.id, func, self.mv))

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
        parent: Optional[Parent] = None,
        declare: bool = False,
    ) -> None:
        if node.name in self.mv.funcs:
            func = self.mv.funcs[node.name]
            for child in node.body:
                self.visit(child, func)


def report(gx: "config.GlobalInfo") -> None:
    for module in gx.modules.values():
        if not module.builtin:
            cv = ConnectionGraphVisitor(gx, module)
            cv.visit(module.ast)
    print('mem report!')
