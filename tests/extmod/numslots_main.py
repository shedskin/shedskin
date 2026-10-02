# tests for the numslots extension module; see README.md
#
# by default, this requires the compiled extension module (in build/). use
# '--py' to run the same checks against numslots.py under CPython, to verify
# the checks themselves.

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


if __name__ == '__main__':
    tests = [(name, f) for (name, f) in sorted(globals().items()) if name.startswith('test_')]
    for name, f in tests:
        f()
    print('%s: %d tests passed (%s)' % (os.path.basename(__file__), len(tests), 'python' if PURE else 'extmod'))
