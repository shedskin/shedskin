# tests for the basics extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against basics.py under CPython, to verify
# the checks themselves.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # basics.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import basics

if not PURE:
    assert not basics.__file__.endswith('.py'), basics.__file__


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def test_globals():
    assert basics.answer == 42
    assert basics.greeting == 'hello'


def test_functions():
    assert basics.add(1, 2) == 3
    assert basics.scale(1.5) == 3.0
    assert basics.scale(1.5, 3.0) == 4.5
    assert basics.scale(1.5, factor=4.0) == 6.0
    assert basics.join(['a', 'b', 'c'], '-') == 'a-b-c'
    assert basics.count(['a', 'b', 'a']) == {'a': 2, 'b': 1}
    assert basics.nothing() is None


def test_exceptions():
    assert basics.fail(1) == 1
    assert raises(ValueError, basics.fail, -1)


def test_class():
    v = basics.Vector(3, 4)
    assert v.x == 3 and v.y == 4
    assert v.length2() == 25
    v.x = 5
    assert v.x == 5
    assert repr(basics.Vector(1, 2)) == 'Vector(1, 2)'
    assert str(basics.Vector(1, 2)) == '(1, 2)'
    assert isinstance(v, basics.Vector)


def test_number_slots():
    a, b = basics.Vector(1, 2), basics.Vector(3, 5)
    assert repr(a + b) == 'Vector(4, 7)'
    assert repr(a - b) == 'Vector(-2, -3)'
    assert repr(a * b) == 'Vector(3, 10)'
    assert repr(-a) == 'Vector(-1, -2)'
    assert repr(abs(basics.Vector(-1, -2))) == 'Vector(1, 2)'
    assert bool(a) is True
    assert bool(basics.Vector(0, 0)) is False


def test_reflected_number_slots():
    # the int's slot declines, then the Vector's slot is called with the
    # int as 'self': this used to crash the interpreter
    a = basics.Vector(1, 2)
    assert raises(TypeError, lambda: 1 + a)
    assert raises(TypeError, lambda: 1 - a)
    assert raises(TypeError, lambda: 2 * a)
    assert raises(TypeError, lambda: None + a)


def test_hash():
    assert hash(basics.Vector(1, 2)) == 1002
    assert hash(basics.Vector(-1, 999)) == -2  # -1 is reserved
    d = {basics.Vector(1, 2): 'a'}
    assert len(d) == 1


def test_call():
    assert basics.Vector(2, 0)(5) == 10


def test_iter():
    assert list(basics.Countdown(3)) == [2, 1, 0]


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
