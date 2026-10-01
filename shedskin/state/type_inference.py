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
        open_contours: During propagation, the (class, contour) pairs of
            container contours that may receive types; all other container
            contours are frozen (see shedskin.contours).
        contour_core: During propagation, the contours.FrozenCore that
            seed_template asks for the contour of each new allocation site.
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
    open_contours: Optional[Set[Tuple[Any, int]]] = None
    contour_core: Optional[Any] = None
