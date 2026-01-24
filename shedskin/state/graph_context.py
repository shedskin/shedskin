# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state.graph_context: Graph building context."""

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Set, Tuple, Union

if TYPE_CHECKING:
    from shedskin import python


@dataclass
class GraphBuildingContext:
    """Mutable context for building the constraint graph.

    This context tracks temporary state during AST traversal and
    constraint graph construction.

    Attributes:
        tempcount: Dictionary mapping expressions to temporary variable names.
        loopstack: Stack of nested loop AST nodes.
        genexp_to_lc: Maps generator expressions to equivalent list comprehensions.
        setcomp_to_lc: Maps set comprehensions to equivalent list comprehensions.
        dictcomp_to_lc: Maps dict comprehensions to equivalent list comprehensions.
        bool_test_only: AST nodes used only in boolean test context.
        called: Set of attribute nodes that are called.
        item_rvalue: Maps AST nodes to their item rvalue.
        assign_target: Maps assignment nodes to their targets.
        struct_unpack: Maps struct unpack assignments to their format info.
        augment: Set of augmented assignment AST nodes.
        parent_nodes: Maps AST nodes to their parent nodes.
        from_module: Maps AST nodes to their source modules.
        list_types: Maps (lineno, node) tuples to list type identifiers.
    """

    tempcount: Dict[Any, str] = field(default_factory=dict)
    loopstack: List[Union[ast.While, ast.For]] = field(default_factory=list)
    genexp_to_lc: Dict[ast.GeneratorExp, ast.ListComp] = field(default_factory=dict)
    setcomp_to_lc: Dict[ast.SetComp, ast.ListComp] = field(default_factory=dict)
    dictcomp_to_lc: Dict[ast.DictComp, ast.ListComp] = field(default_factory=dict)
    bool_test_only: Set[ast.AST] = field(default_factory=set)
    called: Set[ast.Attribute] = field(default_factory=set)
    item_rvalue: Dict[ast.AST, ast.AST] = field(default_factory=dict)
    assign_target: Dict[ast.AST, ast.AST] = field(default_factory=dict)
    struct_unpack: Dict[
        ast.Assign, Tuple[List[Tuple[str, str, str, int]], str, str]
    ] = field(default_factory=dict)
    augment: Set[ast.AST] = field(default_factory=set)
    parent_nodes: Dict[ast.AST, ast.AST] = field(default_factory=dict)
    from_module: Dict[ast.AST, "python.Module"] = field(default_factory=dict)
    list_types: Dict[Tuple[int, ast.AST], int] = field(default_factory=dict)
