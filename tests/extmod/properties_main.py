# tests for the properties extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against properties.py under CPython, to verify
# the checks themselves.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # properties.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import properties

if not PURE:
    assert not properties.__file__.endswith('.py'), properties.__file__


def raises(exc, func, *args):
    try:
        func(*args)
    except exc as e:
        return str(e)
    return None


def test_getter_setter():
    k = properties.K(1)
    assert k.a == 1
    k.a = 2
    assert k.a == 20
    assert k.ro == 'ro20'


def test_read_only():
    k = properties.K(1)
    msg = raises(AttributeError, setattr, k, 'ro', 'x')
    assert msg and 'has no setter' in msg, msg
    msg = raises(AttributeError, delattr, k, 'a')
    assert msg and 'has no deleter' in msg, msg


def test_property_call():
    k = properties.K(1)
    assert k.b == 1.5
    k.b = 2.5
    assert k.b == 2.5 and k.get_b() == 2.5
    k.set_b(3.5)
    assert k.b == 3.5


def test_accessors_not_methods():
    names = dir(properties.K)
    assert 'a' in names and 'ro' in names
    assert not [n for n in names if n.endswith('__setter__')]
    assert not callable(properties.K(1).a)


def test_inherited():
    l = properties.L(3)
    assert isinstance(l, properties.K)
    assert l.a == 3
    l.a = 4
    assert l.a == 40
    assert l.ro == 'L40'
    assert l.b == 1.5
    assert raises(AttributeError, setattr, l, 'ro', 'x')


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
