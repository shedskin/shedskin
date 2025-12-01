# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2025 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)

import ast

from typing import (IO, TYPE_CHECKING, Any, Dict, Iterator, List, Optional,
                    Tuple, TypeAlias, Union)

from . import ast_utils
from . import python
from . import infer

Parent: TypeAlias = Union["python.Class", "python.Function"]
Types: TypeAlias = set[Tuple["python.Class", int]]


# TODO nodes without assignment don't escape
# TODO methods
# TODO setattr
# TODO walrus

# TODO raise
# TODO connect return
# TODO generic builtin container visiting


class ConnectionGraphVisitor(ast_utils.BaseNodeVisitor):
    """Visitor for generating connection graph from Python ASTs"""

    def __init__(
        self, gx: "config.GlobalInfo", module: "python.Module", connections, start_values, constructors
    ):
        self.gx = gx
        self.module = module
        self.mergeinh = self.gx.merged_inh
        self.mv = module.mv

        self.connections = connections # var assignment dataflow
        self.start_values = start_values  # 'esc'/'ret'/'cap'
        self.constructors = constructors

    def visit_Return(
        self, node: ast.Return, func: Optional["python.Function"] = None
    ) -> None:
        if func:
            if isinstance(node.value, ast.Name):
                v = python.lookup_var(node.value.id, func, self.mv)
                self.start_values[v] = 'ret'
            else:
                self.start_values[node.value] = 'ret'

        for child in ast.iter_child_nodes(node):
            self.visit(child, func)

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

    def visit_Assign(
        self, node: ast.Assign, func: Optional["python.Function"] = None
    ) -> None:
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            a = python.lookup_var(node.targets[0].id, func, self.mv)
            if isinstance(node.value, ast.Name):
                b = python.lookup_var(node.value.id, func, self.mv)
                self.connections.append((a, b))
#                print('assign var', a, '<-', b)
            elif not isinstance(node.value, ast.Constant):
                self.connections.append((a, node.value))
#                print('assign node', a, '<-', node.value)

        for child in ast.iter_child_nodes(node):
            self.visit(child, func)

    def visit_Tuple(
        self,
        node: ast.Tuple,
        func: Optional["python.Function"] = None,
        argtypes: Optional[Types] = None,
    ) -> None:
        self.constructors.add(node)

    def visit_List(
        self,
        node: ast.List,
        func: Optional["python.Function"] = None,
        argtypes: Optional[Types] = None,
    ) -> None:
        self.constructors.add(node)

    def visit_ListComp(
        self, node: ast.ListComp, func: Optional["python.Function"] = None
    ) -> None:
        self.constructors.add(node)

    def visit_Call(
        self,
        node: ast.Call,
        func: Optional["python.Function"] = None,
        argtypes: Optional[Types] = None,
    ) -> None:
        """Visit a call node"""
        (
            objexpr,
            ident,
            direct_call,
            method_call,
            constructor,
            parent_constr,
            anon_func,
        ) = infer.analyze_callfunc(self.gx, node, merge=self.gx.merged_inh)

        if constructor:
            self.constructors.add(node)

        funcs = infer.callfunc_targets(self.gx, node, self.gx.merged_inh)
        if not funcs:
            return

        target = funcs[0]

        pairs, rest, err = infer.connect_actual_formal(
            self.gx, node, target, parent_constr, merge=self.mergeinh
        )

        for actual, formal in pairs:
            if isinstance(actual, ast.Name):
                b = python.lookup_var(actual.id, func, self.mv)
                self.connections.append((formal, b))
#                print('hum', formal, '<-', b)

        for child in ast.iter_child_nodes(node):
            self.visit(child, func)


def report(gx: "config.GlobalInfo") -> None:
    connections = []
    start_values = {}
    constructors = set()

    for module in gx.modules.values():
        if not module.builtin:
            cv = ConnectionGraphVisitor(gx, module, connections, start_values, constructors)
            cv.visit(module.ast)

    for a, b in connections:
#        print('conn', a, '<-', b)

        for v in (a, b):
            if isinstance(v, python.Variable) and not v.parent:
                start_values[v] = 'esc'

#    for k, v in start_values.items():
#        print('init', k, v)

    values = {}
    for a, b in connections:
        values[a] = 'cap'
        values[b] = 'cap'

    for k, v in start_values.items():
        values[k] = v

    while True:
        changed = False

        for a, b in connections:
            if values[a] == 'esc':
                if values[b] != 'esc':
                    values[b] = 'esc'
                    changed = True
            elif values[a] == 'ret':
                if values[b] != 'esc':
                    values[b] = 'ret'
                    changed = True

        if not changed:
            break

    for k, v in values.items():
        if k in constructors:
            print(f'{k.lineno}:', v, ast.unparse(k))
