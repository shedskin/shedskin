# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state.entity_registry: Registry of compiled entities."""

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Set, Union

if TYPE_CHECKING:
    from shedskin import python


@dataclass
class EntityRegistry:
    """Mutable registry tracking all compiled entities.

    This registry maintains collections of functions, classes, variables,
    and modules discovered during compilation.

    Attributes:
        allfuncs: Set of all discovered functions.
        allclasses: Set of all discovered classes.
        allvars: Set of all discovered variables.
        modules: Dictionary mapping module names to Module objects.
        inheritance_relations: Maps functions/AST nodes to their inherited versions.
        inheritance_temp_vars: Maps variables to their inherited versions.
        inherited: Set of AST nodes that are inherited.
        lambdawrapper: Dictionary mapping lambda expressions to wrapper names.
        class_def_order: Counter for class definition ordering.
        import_order: Counter for module import ordering.
    """

    allfuncs: Set["python.Function"] = field(default_factory=set)
    allclasses: Set["python.Class"] = field(default_factory=set)
    allvars: Set["python.Variable"] = field(default_factory=set)
    modules: Dict[str, "python.Module"] = field(default_factory=dict)
    inheritance_relations: Dict[
        Union["python.Function", ast.AST],
        List[Union["python.Function", ast.AST]],
    ] = field(default_factory=dict)
    inheritance_temp_vars: Dict[
        "python.Variable", List["python.Variable"]
    ] = field(default_factory=dict)
    inherited: Set[ast.AST] = field(default_factory=set)
    lambdawrapper: Dict[Any, str] = field(default_factory=dict)
    class_def_order: int = 0
    import_order: int = 0
