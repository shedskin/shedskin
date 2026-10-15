# tests for the alloc extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against alloc.py under CPython, to verify
# the checks themselves.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    sys.path.insert(0, os.path.join(HERE, 'build'))

import alloc

if not PURE:
    assert not alloc.__file__.endswith('.py'), alloc.__file__

N = 200000


def test_chain():
    assert alloc.chain(N) == N * (N - 1) // 2


def test_survive():
    # results that survive many collections on the C++ side
    ps = [alloc.pairs(1000) for _ in range(50)]
    ws = [alloc.words(1000) for _ in range(50)]
    alloc.chain(N)
    for p in ps:
        assert p == [(i, i * i) for i in range(1000)]
    for w in ws:
        assert w == ['w' + str(i) for i in range(1000)]


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
