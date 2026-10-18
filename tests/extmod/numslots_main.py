# tests for the numslots extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against numslots.py under CPython, to verify
# the checks themselves.

import operator
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PURE = '--py' in sys.argv

if not PURE:
    # numslots.py sits next to this script, so make sure the compiled module
    # comes first on the path (and check that we actually got it below)
    sys.path.insert(0, os.path.join(HERE, 'build'))

import numslots

if not PURE:
    assert not numslots.__file__.endswith('.py'), numslots.__file__


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def test_pow_modulo_required():
    # the modulo is passed on as the third argument (it used to be ignored,
    # with the exponent passed for both: pow(3, 4, 4))
    assert pow(numslots.Mod(3), 4, 100).x == 81
    assert pow(numslots.Mod(3), 4, 5).x == 1
    assert pow(numslots.Mod(7), 2, 10).x == 9
    # no modulo given
    assert raises(TypeError, lambda: numslots.Mod(3) ** 4)
    assert raises(TypeError, pow, numslots.Mod(3), 4)


def test_pow_no_modulo():
    assert (numslots.Pow(3) ** 4).x == 81
    assert pow(numslots.Pow(3), 4).x == 81
    # a modulo is not silently ignored
    assert raises(TypeError, pow, numslots.Pow(3), 4, 5)


def test_pow_modulo_default():
    assert (numslots.ModDefault(7) ** 4).x == 401  # 2401 % 1000
    assert pow(numslots.ModDefault(7), 4).x == 401
    assert pow(numslots.ModDefault(7), 4, 10).x == 1


def test_pow_wrong_types():
    assert raises(TypeError, pow, numslots.Mod(3), 4, 'x')
    assert raises(TypeError, pow, numslots.Mod(3), 'x', 5)
    # reflected: the int's slot declines, and so does ours
    assert raises(TypeError, lambda: 2 ** numslots.Pow(3))
    assert raises(TypeError, pow, 2, numslots.Mod(3), 5)


def test_binary():
    a, b = numslots.Num(7), numslots.Num(3)
    assert (a + b).x == 10
    assert (a - b).x == 4
    assert (a * b).x == 21
    assert (a % b).x == 1
    q, r = divmod(a, b)
    assert (q.x, r.x) == (2, 1)
    assert (a << 2).x == 28
    assert (a >> 1).x == 3
    assert (a & b).x == 3
    assert (a ^ b).x == 4
    assert (a | b).x == 7
    assert (a // b).x == 2
    assert a / b == 7 / 3
    assert a @ b == 22
    # through the slot wrappers
    assert a.__floordiv__(b).x == 2
    assert a.__and__(b).x == 3
    # wrong types (an AttributeError for numslots.py)
    assert raises((TypeError, AttributeError), lambda: a // 'x')
    assert raises((TypeError, AttributeError), lambda: a & 1.5)
    # reflected: the int's slot declines, and so does ours
    assert raises(TypeError, lambda: 1 // a)
    assert raises(TypeError, lambda: 1 | a)
    assert raises(TypeError, lambda: 1 @ a)


def test_unary():
    a = numslots.Num(7)
    assert (-a).x == -7
    assert (+a).x == 8
    assert abs(numslots.Num(-7)).x == 7
    assert (~a).x == -8
    assert a.__invert__().x == -8
    assert bool(a) is True
    assert bool(numslots.Num(0)) is False


def test_int_float_index():
    a = numslots.Num(7)
    # __int__ and __float__ take precedence over __index__
    assert int(a) == 70
    assert float(a) == 7.5
    assert a.__int__() == 70
    assert a.__float__() == 7.5
    assert operator.index(a) == 7
    assert a.__index__() == 7
    assert hex(a) == '0x7'
    assert bin(a) == '0b111'
    assert oct(a) == '0o7'
    assert [10, 11, 12, 13, 14, 15, 16, 17][a] == 17
    assert list(range(10))[numslots.Num(2):a] == [2, 3, 4, 5, 6]
    assert list(range(a)) == [0, 1, 2, 3, 4, 5, 6]
    assert 'ab' * numslots.Num(3) == 'ababab'
    assert complex(a) == 7.5


def test_index_fallback():
    i = numslots.Index(5)
    assert int(i) == 5
    assert float(i) == 5.0
    assert operator.index(i) == 5
    assert hex(i) == '0x5'
    assert [0, 1, 2, 3, 4, 5, 6][i] == 5
    assert complex(i) == 5


def test_no_index():
    f = numslots.IntFloat(4)
    assert int(f) == 4
    assert float(f) == 6.0
    assert raises(TypeError, operator.index, f)
    assert raises(TypeError, hex, f)
    assert raises(TypeError, lambda: [1, 2, 3][f])


def test_no_conversion():
    # a class without these methods is still not convertible
    p = numslots.Pow(3)
    assert raises(TypeError, int, p)
    assert raises(TypeError, float, p)
    assert raises(TypeError, operator.index, p)
    assert raises(TypeError, lambda: ~p)
    assert raises(TypeError, lambda: p // p)


def test_generated_inplace():
    # 'n += m' falls back on __add__
    n = numslots.Num(1)
    m = n
    n += numslots.Num(2)
    assert n.x == 3
    assert m.x == 1


def test_inplace():
    acc = numslots.Acc(5)
    orig = acc
    acc += 3
    assert acc.x == 8
    acc -= 1
    assert acc.x == 7
    acc *= 4
    assert acc.x == 28
    acc %= 10
    assert acc.x == 8
    acc **= 3
    assert acc.x == 512
    acc <<= 2
    assert acc.x == 2048
    acc >>= 1
    assert acc.x == 1024
    acc &= 0xfff
    assert acc.x == 1024
    acc ^= 5
    assert acc.x == 1029
    acc |= 16
    assert acc.x == 1045
    acc //= 3
    assert acc.x == 348
    acc /= 7
    assert acc.x == 4971
    acc @= 2
    assert acc.x == 9943
    # the same object is returned and updated
    assert acc is orig
    # wrong type
    assert raises(TypeError, operator.iadd, acc, 'x')
    # no binary operator to fall back on
    assert raises(TypeError, lambda: acc + 1)


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
