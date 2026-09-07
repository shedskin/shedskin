# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state.type_inference: Type inference state."""

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple

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
        retry_maxiters: Whether to raise on hitting the iteration limit.
        infer_v2: Use the experimental v2 type analysis.
        infer_v2_open_contours: While v2 probes, the set of (class, contour)
            pairs allowed to receive inflow. Every other contour is frozen:
            readable, but not writable. None disables the mechanism.
        infer_v2_core: While v2 sweeps, the FrozenCore that owns allocation
            site contours. ifa_seed_template asks it for the contour of a
            mold in a newly created template, instead of falling back to the
            "mother contour" search. None disables the mechanism.
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
    retry_maxiters: bool = False
    infer_v2: bool = False
    infer_v2_open_contours: Optional[Set[Tuple[Any, int]]] = None
    infer_v2_core: Optional[Any] = None
