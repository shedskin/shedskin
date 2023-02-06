from . import insubsub
from .. import daar
from .. import insub
from ... import hier

from .insubsub import inhoho
from ..daar import indaar
from ...sub import insub
from ...hier import inhier


def diepst():
    return [
        insubsub.inhoho(),
        daar.indaar(),
        insub(),
        hier.inhier(),

        inhoho(),
        indaar(),
        insub(),
        inhier(),
    ]
