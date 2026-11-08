# tests for the classvars extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against classvars.py under CPython, to verify
# the checks themselves.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # classvars.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import classvars

if not PURE:
    assert not classvars.__file__.endswith('.py'), classvars.__file__


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def test_read_write():
    # 1016-D9: K.count used to be missing (AttributeError)
    K = classvars.K
    assert K.count == 3
    assert K().x == 3
    K.count = 7
    assert K.count == 7
    assert K().x == 7  # compiled code sees the new value
    assert K().count == 7  # readable through an instance
    K.count = 3


def test_inherited():
    Base, Sub = classvars.Base, classvars.Sub
    Base.label = 'changed'
    b = Base()
    assert b.get() == (Base.count, 'changed')
    s = Sub()
    assert Sub.count == Base.count and Sub.label == 'changed'
    assert s.count == Base.count
    assert s.scaled() == 3.0
    Sub.scale = 3  # int converts to float, as for instance attributes
    assert Sub.scale == 3.0 and s.scaled() == 6.0
    Sub.scale = 1.5
    Base.label = 'base'


def test_errors():
    K = classvars.K
    if not PURE:
        # a class variable has a fixed C++ type
        assert raises(TypeError, setattr, K, 'count', 'str')
        assert K.count == 3
        # a class variable of a compiled class cannot be deleted, a new class
        # attribute cannot be added, an inherited one can only be set through
        # the class that defines it, and none can be set through an instance
        # (as it has no __dict__)
        assert raises(AttributeError, delattr, K, 'count')
        assert raises(TypeError, setattr, K, 'other', 1)
        assert raises(TypeError, setattr, classvars.Sub, 'count', 1)
        assert raises(AttributeError, setattr, K(), 'count', 1)


def test_types():
    assert issubclass(type(classvars.K), type)
    assert issubclass(type(classvars.Sub), type(classvars.Base))
    assert isinstance(classvars.Sub(), classvars.Base)
    assert type(classvars.Plain) is type  # no class variables, no metatype


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
