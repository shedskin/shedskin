from __future__ import annotations

# relative imports from a plain module (not an __init__.py)
from . import insubsub
from .insubsub import inhoho
from .. import daar
from ..daar import indaar
from ... import hier
from ...hier import inhier
from ...sub import insub


def deepest() -> list[int]:
    return [insubsub.inhoho(), inhoho(), daar.indaar(), indaar(), hier.inhier(), inhier(), insub()]
