# tests for the intrange extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against intrange.py under CPython, to verify
# the checks themselves (python ints have no range, so the overflow checks
# are skipped then). build the module both with and without --int32:
#
#   shedskin build -e intrange && python3 intrange_main.py
#   shedskin build -e --int32 intrange && python3 intrange_main.py

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # intrange.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import intrange

if not PURE:
    assert not intrange.__file__.endswith('.py'), intrange.__file__

HI = intrange.maxint()  # 2**31-1 with --int32, else 2**63-1
LO = -HI - 1

# just out of range, an unsigned value of the same width (not accepted:
# it would come back negative), and far out of range
OUT = [HI + 1, LO - 1, 2 * HI + 1, 2**64, -2**64, 2**100, -2**1000]


def raises(exc, func, *args):
    try:
        func(*args)
    except exc as e:
        assert 'too large' in str(e) or exc is not OverflowError, str(e)
        return True
    return False


def setattr_n(h, v):
    h.n = v


def test_in_range():
    assert HI in (2**31 - 1, 2**63 - 1)
    for v in [0, 1, -1, LO, LO + 1, HI, HI - 1, 2**31 - 1, -2**31]:
        assert intrange.ident(v) == v and type(intrange.ident(v)) is int
        assert intrange.first([v]) == v
        assert intrange.lookup({v: 1}, v) == 1
        assert intrange.lookup({1: v}, 1) == v
        assert intrange.pair_sum((v, 0)) == v
        assert intrange.set_sum({v}) == v
        assert intrange.Holder(v).get() == v
    assert intrange.add(HI, 0) == HI and intrange.add(LO, 0) == LO
    # bools are ints
    assert intrange.ident(True) == 1 and intrange.ident(False) == 0


def test_out_of_range():
    if PURE:
        return
    for v in OUT:
        assert raises(OverflowError, intrange.ident, v), v
        assert raises(OverflowError, intrange.add, v, 0), v
        assert raises(OverflowError, intrange.add, 0, v), v
        assert raises(OverflowError, intrange.first, [1, v]), v
        assert raises(OverflowError, intrange.lookup, {v: 1}, 1), v
        assert raises(OverflowError, intrange.lookup, {1: v}, 1), v
        assert raises(OverflowError, intrange.lookup, {1: 2}, v), v
        assert raises(OverflowError, intrange.pair_sum, (1, v)), v
        assert raises(OverflowError, intrange.set_sum, {1, v}), v
        assert raises(OverflowError, intrange.Holder, v), v
        h = intrange.Holder(5)
        assert raises(OverflowError, setattr_n, h, v), v
        assert h.get() == 5


def test_recovers():
    # no python exception is left behind after a failed conversion
    for i in range(100):
        if not PURE:
            assert raises(OverflowError, intrange.ident, 2**100)
        assert intrange.ident(i) == i


def test_float():
    assert intrange.ident_float(1.5) == 1.5
    assert intrange.ident_float(2**60) == float(2**60)
    assert float(intrange.ident_float(HI)) == float(HI)
    assert intrange.ident_float(2**1023) == float(2**1023)
    assert intrange.ident_float(-2**1023) == -float(2**1023)
    assert intrange.ident_float(-1) == -1.0  # -1.0 is also the C API error value
    if not PURE:
        assert type(intrange.ident_float(1)) is float
        # float(2**1024) overflows (it used to return -1.0 and leave the
        # python error set)
        assert raises(OverflowError, intrange.ident_float, 2**1024)
        assert raises(OverflowError, intrange.ident_float, -2**1024)
        assert raises(TypeError, intrange.ident_float, 'x')
        assert intrange.ident_float(2.5) == 2.5


def test_complex():
    assert intrange.ident_complex(1 + 2j) == 1 + 2j
    assert intrange.ident_complex(-1 - 1j) == -1 - 1j  # -1.0 parts: error value
    assert intrange.ident_complex(3) == 3
    assert intrange.ident_complex(2.5) == 2.5
    if not PURE:
        assert type(intrange.ident_complex(3)) is complex
        assert raises(OverflowError, intrange.ident_complex, 2**1024)
        assert raises(TypeError, intrange.ident_complex, 'x')
        assert intrange.ident_complex(1j) == 1j


if __name__ == '__main__':
    tests = [f for name, f in sorted(globals().items()) if name.startswith('test_')]
    for test in tests:
        test()
    print('%s: %d tests passed (%s, %d-bit)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod', HI.bit_length() + 1))
