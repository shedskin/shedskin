# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state.type_inference: Type inference state."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple

if TYPE_CHECKING:
    from shedskin import infer


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
        templates: Template instantiation counter.
        cpa_limit: Limit for Cartesian Product Algorithm.
        cpa_limited: Whether CPA limit was reached.
        merged_inh: Merged inheritance type information.
        retry_maxiters: Set by --retry; no longer has any effect, but still
            passed on to the generated build files.
        infer_v2_open_contours: While v2 probes, the set of (class, contour)
            pairs allowed to receive inflow. Every other contour is frozen:
            readable, but not writable. None disables the mechanism.
        infer_v2_core: While v2 sweeps, the FrozenCore that owns allocation
            site contours. ifa_seed_template asks it for the contour of a
            mold in a newly created template. Set whenever propagation runs.
    """

    constraints: Set[Tuple["infer.CNode", "infer.CNode"]] = field(default_factory=set)
    cnode: Dict[Tuple[Any, int, int], "infer.CNode"] = field(default_factory=dict)
    types: Dict["infer.CNode", Set[Tuple[Any, int]]] = field(default_factory=dict)
    orig_types: Dict["infer.CNode", Set[Tuple[Any, int]]] = field(default_factory=dict)
    templates: int = 0
    cpa_limit: int = 0
    cpa_limited: bool = False
    merged_inh: Dict[Any, Set[Tuple[Any, int]]] = field(default_factory=dict)
    retry_maxiters: bool = False
    infer_v2_open_contours: Optional[Set[Tuple[Any, int]]] = None
    infer_v2_core: Optional[Any] = None
