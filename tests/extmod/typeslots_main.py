# tests for the typeslots extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against typeslots.py under CPython, to verify
# the checks themselves.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # typeslots.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import typeslots

if not PURE:
    assert not typeslots.__file__.endswith('.py'), typeslots.__file__


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def test_unexported_call():
    # the class used to fail to compile (a tp_call slot pointing to the
    # unexported __call__ glue). now it compiles, without tp_call
    a = typeslots.Applier(3)
    assert a.value() == 3
    assert repr(a) == 'Applier(3)'
    assert str(a) == 'applier 3'
    if PURE:
        assert a(typeslots.square) == 9
    else:
        assert raises(TypeError, a, typeslots.square)


def test_exported_call():
    assert typeslots.Scaler(2)(5) == 10
    assert typeslots.Scaler(3)(-1) == -3


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
