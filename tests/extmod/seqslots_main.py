# tests for the seqslots extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against seqslots.py under CPython, to verify
# the checks themselves.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # seqslots.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import seqslots

if not PURE:
    assert not seqslots.__file__.endswith('.py'), seqslots.__file__


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def test_sequence():
    b = seqslots.Bag(3)
    assert len(b) == 3
    assert b[0] == 0 and b[2] == 2 and b[-1] == 2
    b[0] = 7
    assert b[0] == 7
    assert 7 in b and 1 in b and 0 not in b
    assert list(b) == [7, 1, 2]
    assert list(reversed(b)) == [2, 1, 7]
    assert raises(IndexError, lambda: b[3])
    assert raises(TypeError, lambda: b['x'])
    assert b.__len__() == 3


def test_bool():
    assert bool(seqslots.Bag(1))
    assert not seqslots.Bag(0)
    assert not seqslots.Table()


def test_inherited():
    s = seqslots.SubBag(2)
    assert len(s) == 2 and s[1] == 1 and 1 in s
    s[1] = 5
    assert s.total() == 5


def test_mapping():
    t = seqslots.Table()
    t['a'] = 1
    t['b'] = 2
    assert len(t) == 2
    assert t['b'] == 2
    assert 'a' in t and 'c' not in t
    del t['a']
    assert 'a' not in t and len(t) == 1
    assert raises(KeyError, lambda: t['a'])

    def delete():
        del t['zz']

    assert raises(KeyError, delete)


def test_getitem_only():
    q = seqslots.Squares()
    assert q[3] == 9
    assert list(q) == [0, 1, 4, 9]
    assert 4 in q and 5 not in q
    assert raises(TypeError, len, q)

    def assign():
        q[0] = 1

    def delete():
        del q[0]

    assert raises(TypeError, assign)
    assert raises(TypeError, delete)


def test_negative_len():
    assert raises(ValueError, len, seqslots.BadLen())


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
