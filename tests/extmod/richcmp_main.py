# tests for the richcmp extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against richcmp.py under CPython, to verify
# the checks themselves.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # richcmp.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import richcmp

if not PURE:
    assert not richcmp.__file__.endswith('.py'), richcmp.__file__


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def test_full():
    # comparisons used to be by identity ('==', '!='), or raise (the others)
    a, b, c = richcmp.Full(1), richcmp.Full(2), richcmp.Full(1)
    assert a == c and not a == b
    assert a != b and not a != c
    assert a < b and not b < a and not a < c
    assert a <= b and a <= c and not b <= a
    assert b > a and not a > b and not a > c
    assert b >= a and a >= c and not a >= b
    assert sorted([b, c, a], key=lambda o: o) == [a, c, b]
    assert max([a, b, c]) is b
    assert a.__eq__(c) is True
    assert a.__lt__(b) is True


def test_other_types():
    # an argument that cannot be converted gives NotImplemented, so '=='
    # falls back to identity and '<' raises TypeError, as in CPython (None
    # used to reach the C++ method as a NULL pointer). under CPython, __eq__
    # just tries 'other.x', so this only applies to the extension module
    if PURE:
        return
    a = richcmp.Full(1)
    for other in [None, 1, 'x', richcmp.EqOnly(1)]:
        assert not a == other and not other == a
        assert a != other and other != a
        assert raises(TypeError, lambda: a < other)
        assert raises(TypeError, lambda: other >= a)
    assert a.__eq__(None) is NotImplemented
    assert a.__eq__(1) is NotImplemented
    assert a in [None, 1, richcmp.Full(1)]
    assert [None, richcmp.Full(1)].index(a) == 1
    assert raises(TypeError, a.__eq__)
    assert raises(TypeError, a.__eq__, a, a)


def test_eq_only():
    a, b, c = richcmp.EqOnly(1), richcmp.EqOnly(2), richcmp.EqOnly(1)
    assert a == c and not a == b
    # '!=' inverts '=='
    assert a != b and not a != c
    assert raises(TypeError, lambda: a < b)
    # __eq__ without __hash__ makes it unhashable
    assert raises(TypeError, hash, a)
    assert raises(TypeError, set, [a])


def test_lt_only():
    a, b = richcmp.LtOnly(1), richcmp.LtOnly(2)
    assert a < b and not b < a
    # 'b > a' falls back to the reflected 'a < b'
    assert b > a and not a > b
    assert raises(TypeError, lambda: a <= b)
    # without __eq__, '==' is identity, and the type stays hashable
    assert a == a and not a == richcmp.LtOnly(1)
    assert hash(a) == hash(a)


def test_eq_hash():
    a, b, c = richcmp.EqHash(1), richcmp.EqHash(11), richcmp.EqHash(2)
    assert a == b and a != c
    assert hash(a) == hash(b) == 1
    assert len({a, b, c}) == 2
    assert {a: 'x'}[b] == 'x'


def test_derived():
    # Derived only defines __lt__: __eq__ and __hash__ come from EqHash
    a, b, c = richcmp.Derived(1), richcmp.Derived(11), richcmp.Derived(2)
    assert a < c and a < b and not c < a
    assert c > a
    assert a == b and a != c
    assert a == richcmp.EqHash(1)
    assert hash(a) == hash(b) == 1
    assert len({a, b, c}) == 2


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
