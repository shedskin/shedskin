# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state.type_inference: Type inference state."""

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Set, Tuple

if TYPE_CHECKING:
    from shedskin import infer, python
    from shedskin.config import CartesianProduct


@dataclass
class TypeInferenceState:
    """Mutable state for type inference.

    This contains the core data structures used during constraint-based
    type inference.

    Attributes:
        constraints: Set of constraint pairs between CNodes.
        cnode: Dictionary mapping (node, context) tuples to CNodes.
        types: Dictionary mapping CNodes to their inferred type sets.
        orig_types: Original types before widening.
        alloc_info: Allocation site type information across iterations.
        new_alloc_info: New allocation info for current iteration.
        iterations: Current iteration count.
        total_iterations: Total iterations across all phases.
        templates: Template instantiation counter.
        added_allocs: Count of added allocations in current iteration.
        added_allocs_set: Set of added allocations.
        added_funcs: Count of added functions in current iteration.
        added_funcs_set: Set of added functions.
        cpa_clean: Whether CPA is in clean state.
        cpa_limit: Limit for Cartesian Product Algorithm.
        cpa_limited: Whether CPA limit was reached.
        merged_inh: Merged inheritance type information.
        maxhits: Maximum hits counter (for termination).
    """

    constraints: Set[Tuple["infer.CNode", "infer.CNode"]] = field(default_factory=set)
    cnode: Dict[Tuple[Any, int, int], "infer.CNode"] = field(default_factory=dict)
    types: Dict["infer.CNode", Set[Tuple[Any, int]]] = field(default_factory=dict)
    orig_types: Dict["infer.CNode", Set[Tuple[Any, int]]] = field(default_factory=dict)
    alloc_info: Dict[
        Tuple[str, "CartesianProduct", ast.AST], Tuple["python.Class", int]
    ] = field(default_factory=dict)
    new_alloc_info: Dict[
        Tuple[str, "CartesianProduct", ast.AST], Tuple["python.Class", int]
    ] = field(default_factory=dict)
    iterations: int = 0
    total_iterations: int = 0
    templates: int = 0
    added_allocs: int = 0
    added_allocs_set: Set[Any] = field(default_factory=set)
    added_funcs: int = 0
    added_funcs_set: Set["python.Function"] = field(default_factory=set)
    cpa_clean: bool = False
    cpa_limit: int = 0
    cpa_limited: bool = False
    merged_inh: Dict[Any, Set[Tuple[Any, int]]] = field(default_factory=dict)
    maxhits: int = 0
