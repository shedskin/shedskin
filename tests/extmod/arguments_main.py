# tests for the arguments extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against arguments.py under CPython, to verify
# the checks themselves: the error messages are the same as CPython's.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # arguments.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import arguments

if not PURE:
    assert not arguments.__file__.endswith('.py'), arguments.__file__


def error(func, *args, **kwargs):
    """the message of the TypeError raised by func(*args, **kwargs)"""
    try:
        func(*args, **kwargs)
    except TypeError as e:
        return str(e)
    return None


def test_valid_calls():
    assert arguments.nothing() == 0
    assert arguments.one(5) == 5
    assert arguments.one(a=5) == 5
    assert arguments.two(1, 2) == 3
    assert arguments.two(1, b=2) == 3
    assert arguments.two(b=2, a=1) == 3
    assert arguments.three(1, c=3, b=2) == 6
    assert arguments.opt(1) == 12
    assert arguments.opt(1, 3) == 13
    assert arguments.opt(1, b=3) == 13
    assert arguments.opt(b=3, a=1) == 13
    assert arguments.opts() == 12
    assert arguments.opts(b=5) == 15
    assert arguments.opts(b=5, a=2) == 25
    assert arguments.flag(1) == 1
    assert arguments.flag(1, True) == -1
    assert arguments.flag(1, b=True) == -1
    assert arguments.unicode_name(1) == 2
    assert arguments.unicode_name(größe=5) == 6
    assert arguments.one(*[5], **{}) == 5


def test_too_many_positional():
    assert error(arguments.nothing, 1) == 'nothing() takes 0 positional arguments but 1 was given'
    assert error(arguments.nothing, 1, 2) == 'nothing() takes 0 positional arguments but 2 were given'
    assert error(arguments.one, 1, 2) == 'one() takes 1 positional argument but 2 were given'
    assert error(arguments.two, 1, 2, 3) == 'two() takes 2 positional arguments but 3 were given'
    assert error(arguments.opt, 1, 2, 3, 4) == 'opt() takes from 1 to 2 positional arguments but 4 were given'
    assert error(arguments.opts, 1, 2, 3) == 'opts() takes from 0 to 2 positional arguments but 3 were given'


def test_unexpected_keyword():
    assert error(arguments.nothing, x=1) == "nothing() got an unexpected keyword argument 'x'"
    assert error(arguments.opt, 1, zz=5) == "opt() got an unexpected keyword argument 'zz'"
    assert error(arguments.opt, a=1, zz=5) == "opt() got an unexpected keyword argument 'zz'"
    # keywords are checked first, as in CPython
    assert error(arguments.opt, 1, 2, 3, zz=1) == "opt() got an unexpected keyword argument 'zz'"
    assert error(arguments.two, zz=1) == "two() got an unexpected keyword argument 'zz'"
    # non-ascii (and almost matching) names
    assert error(arguments.unicode_name, 1, gröse=1) == "unicode_name() got an unexpected keyword argument 'gröse'"
    assert error(arguments.one, **{'\U0001f600': 1}) == "one() got an unexpected keyword argument '\U0001f600'"
    # non-string keys are rejected by CPython itself
    assert error(lambda: arguments.one(**{1: 2})) == 'keywords must be strings'


def test_multiple_values():
    assert error(arguments.opt, 1, 2, b=9) == "opt() got multiple values for argument 'b'"
    assert error(arguments.opt, 1, a=2) == "opt() got multiple values for argument 'a'"
    assert error(arguments.unicode_name, 1, größe=2) == "unicode_name() got multiple values for argument 'größe'"


def test_missing():
    assert error(arguments.one) == "one() missing 1 required positional argument: 'a'"
    assert error(arguments.opt) == "opt() missing 1 required positional argument: 'a'"
    assert error(arguments.opt, b=1) == "opt() missing 1 required positional argument: 'a'"
    assert error(arguments.two) == "two() missing 2 required positional arguments: 'a' and 'b'"
    assert error(arguments.three) == "three() missing 3 required positional arguments: 'a', 'b', and 'c'"
    assert error(arguments.three, 1) == "three() missing 2 required positional arguments: 'b' and 'c'"
    assert error(arguments.three, 1, c=3) == "three() missing 1 required positional argument: 'b'"
    assert error(arguments.unicode_name) == "unicode_name() missing 1 required positional argument: 'größe'"


def test_methods():
    p = arguments.Point(1, 2)
    assert p.move(1) == 202
    assert p.move(dx=1, dy=1) == 303
    assert p.norm1() == 6
    # 'self' counts, as in CPython
    assert error(p.move, 1, 2, 3) == 'Point.move() takes from 2 to 3 positional arguments but 4 were given'
    assert error(p.norm1, 1) == 'Point.norm1() takes 1 positional argument but 2 were given'
    assert error(p.move) == "Point.move() missing 1 required positional argument: 'dx'"
    assert error(p.move, 1, zz=1) == "Point.move() got an unexpected keyword argument 'zz'"
    assert error(p.move, 1, dx=1) == "Point.move() got multiple values for argument 'dx'"
    assert p.x == 3 and p.y == 3  # failed calls changed nothing
    # inherited method
    q = arguments.Point3(1, 2)
    assert q.move(1) == 202
    assert error(q.move, 1, 2, 3) == 'Point.move() takes from 2 to 3 positional arguments but 4 were given'
    assert error(q.depth, 1) == 'Point3.depth() takes 1 positional argument but 2 were given'


def test_constructors():
    assert repr(arguments.Point(1)) == 'Point(1, 0)'
    assert repr(arguments.Point(x=1, y=2)) == 'Point(1, 2)'
    assert error(arguments.Point) == "Point.__init__() missing 1 required positional argument: 'x'"
    assert error(arguments.Point, 1, 2, 3) == 'Point.__init__() takes from 2 to 3 positional arguments but 4 were given'
    assert error(arguments.Point, 1, z=2) == "Point.__init__() got an unexpected keyword argument 'z'"
    # inherited __init__
    assert repr(arguments.Point3(1, 2)) == 'Point(1, 2)'
    assert error(arguments.Point3, 1, 2, 3) == 'Point.__init__() takes from 2 to 3 positional arguments but 4 were given'
    # no __init__
    assert arguments.Empty().value() == 7
    assert error(arguments.Empty, 1) == 'Empty() takes no arguments'
    assert error(arguments.Empty, x=1) == 'Empty() takes no arguments'


def test_slots():
    # slots call the methods without arguments (or with the regular ones)
    p = arguments.Point(3, -4)
    assert repr(p) == 'Point(3, -4)'
    assert str(p) == '(3, -4)'
    assert repr(-p) == 'Point(-3, 4)'
    assert repr(abs(p)) == 'Point(3, 4)'
    assert p(2) == 6
    assert p(n=2) == 6
    assert list(arguments.Steps(3)) == [1, 2, 3]
    # tp_call gets the regular arguments, so these are checked as for methods
    assert error(p, 1, 2) == 'Point.__call__() takes 2 positional arguments but 3 were given'
    assert error(p) == "Point.__call__() missing 1 required positional argument: 'n'"
    # calling a slot method directly goes through CPython's own slot wrapper
    # for the extension type, so only the exception type is the same
    assert error(p.__repr__, 1) is not None
    assert error(p.__str__, x=1) is not None
    steps = arguments.Steps(1)
    assert error(steps.__next__, 1) is not None
    assert next(steps) == 1


if __name__ == '__main__':
    tests = [f for name, f in sorted(globals().items()) if name.startswith('test_')]
    for test in tests:
        test()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
