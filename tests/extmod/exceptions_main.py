# tests for the exceptions extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against exceptions.py under CPython, to verify
# the checks themselves.

import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # exceptions.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import exceptions

if not PURE:
    assert not exceptions.__file__.endswith('.py'), exceptions.__file__


def caught(n):
    try:
        exceptions.boom(n)
    except Exception as e:
        return e
    return None


def test_exported():
    # the classes are module attributes, with the same bases as in Python
    assert issubclass(exceptions.MyError, Exception)
    assert issubclass(exceptions.SubError, exceptions.MyError)
    assert issubclass(exceptions.MyValueError, ValueError)
    assert issubclass(exceptions.MyKeyError, KeyError)
    assert issubclass(exceptions.MyOSError, OSError)
    assert exceptions.MyError.__name__ == 'MyError'
    assert exceptions.MyError.__module__ == 'exceptions'


def test_raised_types():
    # raised exceptions are of the subclass, not flattened to its base
    for n, cls, args in [
        (1, exceptions.MyError, ('boom',)),
        (2, exceptions.SubError, ('sub',)),
        (3, exceptions.MyValueError, ('value',)),
        (4, exceptions.MyKeyError, ('key',)),
        (5, exceptions.MyOSError, ('os',)),
        (6, ValueError, ('plain',)),
        (7, exceptions.CodeError, ('code',)),
        (8, exceptions.SubCodeError, ('subcode',)),
    ]:
        e = caught(n)
        assert type(e) is cls, (n, type(e))
        assert e.args == args, (n, e.args)
    assert caught(0) is None

    # so they can be caught by type, including through a base class
    try:
        exceptions.boom(2)
    except exceptions.MyError as e:
        assert str(e) == 'sub'
    else:
        assert False
    try:
        exceptions.boom(3)
    except ValueError as e:
        assert isinstance(e, exceptions.MyValueError)
    else:
        assert False


def test_attributes():
    # attributes are copied to the raised exception, including inherited ones
    e = caught(7)
    assert isinstance(e, exceptions.MyError)
    assert e.code == 42 and e.where == ['here']
    assert not hasattr(e, 'extra')
    e = caught(8)
    assert isinstance(e, exceptions.CodeError)
    assert e.code == 43 and e.where == ['here'] and e.extra == 1.5
    assert str(e) == 'subcode'


def test_str_repr():
    # __str__ and __repr__ defined in the module are used from Python
    e = caught(9)
    assert type(e) is exceptions.StrError and e.args == ('base msg',)
    assert str(e) == 'StrError code=7' and repr(e) == "StrError('base msg')"
    e = caught(10)  # inherited
    assert type(e) is exceptions.SubStrError and str(e) == 'StrError code=8'
    e = caught(11)  # overridden
    assert type(e) is exceptions.OtherStrError and str(e) == 'other 9'
    e = caught(12)
    assert str(e) == 'repr' and repr(e) == 'ReprError!'
    # a __str__ that raises (in python only when str is called)
    e = caught(13)
    assert type(e) is exceptions.BadStrError and e.args == ('bad',)
    try:
        str(e)
    except ValueError:
        assert PURE
    else:
        assert not PURE and str(e) == "'bad'"  # falls back to KeyError
    # pickled along with the other attributes
    e = pickle.loads(pickle.dumps(caught(9)))
    assert type(e) is exceptions.StrError and str(e) == 'StrError code=7'
    # unaffected exceptions
    assert str(caught(7)) == 'code' and repr(caught(7)) == "CodeError('code')"


def test_inside():
    # catching inside the module is unaffected
    assert exceptions.catch_inside(0) == 'none'
    assert exceptions.catch_inside(1) == 'MyError boom'
    assert exceptions.catch_inside(2) == 'MyError sub'
    assert exceptions.catch_inside(3) == 'ValueError value'
    assert exceptions.catch_inside(4) == 'LookupError'
    assert exceptions.catch_inside(5) == 'OSError os'
    assert exceptions.catch_inside(6) == 'ValueError plain'
    assert exceptions.catch_inside(7) == 'MyError code'
    assert exceptions.catch_inside(8) == 'MyError subcode'


def test_python_side():
    # the types can be raised from Python and pickled like any exception
    try:
        raise exceptions.SubError('py')
    except exceptions.MyError as e:
        assert e.args == ('py',)
    e = pickle.loads(pickle.dumps(caught(1)))
    assert type(e) is exceptions.MyError and e.args == ('boom',)


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
