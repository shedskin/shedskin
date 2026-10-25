"""
not implemented:

    aiter
    anext
    ascii
    breakpoint
    callable
    classmethod
    compile
    copyright
    credits
    delattr
    dir
    display
    eval
    exec
    format
    getattr
    globals
    hasattr
    help
    id
    input
    locals
    memoryview
    setattr
    super
    type
    vars

 """

import io

class Klass:
    def __init__(self, name):
        self.name = name

class SubKlass(Klass): pass

def test_abs():
    assert abs(-10) == 10
    assert str(abs(-0.0)) == '0.0'
    assert abs(-2.5) == 2.5

class Bert:
    def __index__(self):
        return 77

# def test_ascii():
#     assert ascii(1) == '1'


def test_bin():
    assert bin(3) == '0b11'


def test_bool():
    assert bool(2 > 1) == True


class MyString:
    def __init__(self, s):
        self.s = s
    def __bytes__(self):
        return self.s.encode('utf8')


def test_bytes():
    # s = MyString('sam')
    # assert bytes(s) == b'sam'
    assert bytes('a', encoding='utf8') == b'a'
    assert bytes('\xf1', 'utf-8') == b'\xc3\xb1'
    assert bytes('\xf1', 'ascii', 'replace') == b'?'
    assert bytes('\xf1', 'ascii', errors='ignore') == b''
    b = bytearray('\xf1', 'latin-1')
    b.append(65)
    assert b == bytearray(b'\xf1A')
    try:
        bytes('\xf1', 'ascii')
        assert False
    except UnicodeEncodeError:
        pass
    s = 'x'
    try:
        bytes(s)
        assert False
    except TypeError:
        pass
    assert bytes() == b''
    assert bytes([1, 2, 3]) == b'\x01\x02\x03'
    assert bytes(set([1])) == b'\x01'
    assert bytes(0) == b''
    assert bytes(4) == b'\x00\x00\x00\x00'
    assert bytes(7) == b'\x00\x00\x00\x00\x00\x00\x00'
    assert bytes(b"hop") ==  b'hop'
    assert bytes(bytes(7)) == b'\x00\x00\x00\x00\x00\x00\x00'


def test_callable():
    assert callable(abs)


def test_chr():
    assert chr(97) == 'a'
    assert chr(True) == '\x01'
    assert chr(Bert()) == 'M'


def test_complex():
    a = complex(1, 2)
    assert a.imag == 2.0
    assert a.real == 1.0

# def test_delattr():
#     obj = Klass('sam')
#     assert hasattr(obj, 'name')
#     delattr(obj, 'name')
#     assert not hasattr(obj, 'name')


def test_divmod():
    assert divmod(10, 2) == (5, 0)
    assert divmod(-496, 3) == (-166, 2)
    assert divmod(-496.0, 3) == (-166.0, 2.0)
    assert divmod(-496, 3.0) == (-166.0, 2.0)
    assert divmod(-496, -3) == (165, -1)
    assert divmod(-496.0, -3.0) == (165.0, -1.0)
    error = ''
    try:
        divmod(1.0, 0.0)
    except ZeroDivisionError as e:
        error = str(e)
    assert error == 'float divmod()'


def test_pow():
    assert pow(2, 10) == 1024
    assert pow(2.0, 3) == 8.0

    # three-argument form: modular exponentiation
    assert pow(2, 10, 1000) == 24
    assert pow(3, 0, 7) == 1
    assert pow(5, 0, 1) == 0
    assert pow(0, 0, 7) == 1
    assert pow(7, 1, 7) == 0
    assert pow(True, 2, 3) == 1
    assert pow(False, 2, 3) == 0

    # the result takes the sign of the modulus
    assert pow(-2, 3, 5) == 2
    assert pow(2, 3, -5) == -2
    assert pow(-3, 5, -7) == -5
    assert pow(-4, 2, 8) == 0
    assert pow(4, 2, -8) == 0

    # negative exponent: modular inverse
    assert pow(3, -1, 7) == 5
    assert pow(-5, -1, 7) == 4
    assert pow(3, -2, -7) == -3
    assert pow(38, -1, 97) == 23
    assert pow(9, -1, 1) == 0

    # no intermediate overflow with a large modulus
    assert pow(123456789, 987654321, 10**12 + 39) == 971610774191
    assert pow(2, 100, 2**61 - 1) == 2**39  # 2**61 = 1 (mod 2**61 - 1)
    assert pow(2**62 - 1, 2, 2**62) == 1
    assert pow(2**32 - 1, 2, 2**32) == 1
    assert pow(2**32 - 2, 2**32 - 3, 2**32 - 1) == 2**32 - 2
    assert pow(2**63 - 2, 3, 2**63 - 1) == 2**63 - 2
    assert pow(3**39, 5, 2**63 - 25) == 3583665142610473966

    # keyword arguments
    assert pow(base=3, exp=4, mod=5) == 1
    assert pow(3, 4, mod=5) == 1
    assert pow(3, exp=4) == 81

    try:
        pow(2, 3, 0)
        assert False
    except ValueError as e:
        assert str(e) == 'pow() 3rd argument cannot be 0'

    try:
        pow(2, -1, 4)
        assert False
    except ValueError as e:
        assert str(e) == 'base is not invertible for the given modulus'


def test_enumerate():
    assert [(i, obj) for i, obj in enumerate(['a', 'b', 'c'])] == [(0, 'a'), (1, 'b'), (2, 'c')]


def test_filter():
    is_gt_10 = lambda x: x > 10
    xs = range(12)
    assert list(filter(is_gt_10, xs)) == [11]


def test_float():
    assert float(100) == 100.0
    assert float('1.5') == 1.5
    assert float(' 2.5 ') == 2.5
    assert float('\t3.5\n') == 3.5
    assert float('-1.5') == -1.5
    assert float('+1.5') == 1.5
    assert float('.5') == 0.5
    assert float('5.') == 5.0
    assert float('1e2') == 100.0
    assert float('1E2') == 100.0
    assert float('1e+2') == 100.0
    assert float('1e-2') == 0.01
    assert float('1_000.5') == 1000.5
    assert float('1.5e1_0') == 15000000000.0
    assert float('inf') > 0
    assert float('-inf') < 0
    assert float('Infinity') > 0
    assert float('nan') != float('nan')


def test_float_invalid():
    # regression test: strtod is far more permissive than CPython's float(),
    # stopping at the first character it cannot use and accepting hex
    # literals, so trailing garbage and empty strings used to convert
    # silently ('1.5x' gave 1.5, '' gave 0.0, '0x10' gave 16.0)
    error = ''
    try:
        float('1.5x')
    except ValueError as e:
        error = str(e)
    assert error == "could not convert string to float: '1.5x'"

    for bad in ['', '  ', 'abc', '0x10', '1_', '_1', '1__0', '1_.5', '1._5',
                '1.5e', 'e5', '+', '-', '1 2', '1.5 x', '1e5.5', 'infin',
                'nano', '9.5.']:
        caught = False
        try:
            float(bad)
        except ValueError:
            caught = True
        assert caught


class HashMinusOne:
    def __init__(self, value):
        self.value = value
    def __hash__(self):
        return self.value

def test_hash():
    assert hash('abc') == hash('abc')
    assert hash('abc') != hash('cba')
    # like CPython, hash() never returns -1
    assert hash(-1) == -2
    assert hash(-2) == -2
    assert hash(0) == 0
    assert hash(7) == 7
    assert hash(True) == 1
    assert hash(False) == 0
    minus_one = -1
    assert hash(minus_one) == -2
    assert hash(HashMinusOne(-1)) == -2
    assert hash(HashMinusOne(-2)) == -2
    assert hash(HashMinusOne(7)) == 7
    assert HashMinusOne(-1).__hash__() == -1

# def test_hasattr():
#     c = complex(4,2)
#     assert hasattr(c, 'real')


def test_int():
    assert int(100.2) == 100

    assert (12345).bit_count() == 6


def test_int_base():
    assert int('ff', 16) == 255
    assert int('ff', base=16) == 255
    assert int('101', base=2) == 5
    assert int('0x1A', base=0) == 26
    assert int('  42  ') == 42
    assert (0b11111111111111111111111111111111).bit_count() == 32
#    assert int.bit_count(-12345) == 6

# def test_getattr():
#     c = complex(4,2)
#     assert getattr(c, 'real') == 4.0


def test_hex():
    assert hex(1) == '0x1'


def test_isinstance():
    obj = Klass('foo')
    assert isinstance(obj, Klass)

# def test_issubclass():
#     assert issubclass(SubKlass, Klass)


def test_len():
    assert len([1,2,3]) == 3


def test_max():
    assert max([4, 5, 9, 12]) == 12
    assert max([1.2, 3.14, 5.56, 9.31]) == 9.31
    assert max(['a', 'b', 'c']) == 'c'
    assert max({1: 2, 3: 4}) == 3

    assert max([1]) == 1
    assert max(1, 2) == 2
    assert max(7.7, 7) == 7.7
    assert max(7, 7.7) == 7.7
    assert max(1, 2, 3) == 3
    assert max(1, 2, 3, 4, 5) == 5

    xs = [1, 2, 3]
    neg = lambda x: -x
    assert max(1, 2) == 2
    assert max(1, 2, 3) == 3
    assert max(1, 2, 3, key=neg) == 1
    assert max(1, 2, 3, key=str) == 3
    assert max(1, 2, key=neg) == 1
    assert max(xs) == 3
    assert max(xs, key=neg) == 1

    assert max(xs, key=lambda y: -y) == 1

    xs = []
    assert max(xs, default=7) == 7
    assert max(xs, default=7, key=lambda y: -y) == 7

    try:
        max(xs)
    except ValueError:
        pass
    else:
        assert False


def test_min():
    assert min([1]) == 1
    assert min(1, 2) == 1
    assert min(6.7, 7) == 6.7
    assert min(7, 6.7) == 6.7
    assert min(1, 2, 3) == 1
    assert min(1, 2, 3, 4, 5) == 1

    assert min([4, 5, 9, 12]) == 4
    assert min([1.2, 3.14, 5.56, 9.31]) == 1.2
    assert min(['a', 'b', 'c']) == 'a'

    xs = [1, 2, 3]
    neg = lambda x: -x
    assert min(1, 2) == 1
    assert min(1, 2, 3) == 1
    assert min(1, 2, 3, key=int) == 1
    assert min(1, 2, 3, key=neg) == 3
    assert min(1, 2, key=neg) == 2
    assert min(xs) == 1
    assert min(xs, key=neg) == 3

    assert min(xs, key=lambda u: -u) == 3

    xs = []
    assert min(xs, default=7) == 7
    assert min(xs, default=7, key=lambda y: -y) == 7

    try:
        min(xs)
    except ValueError:
        pass
    else:
        assert False


class MinMaxTie:
    def __init__(self, k, n):
        self.k = k
        self.n = n
    def __lt__(self, o):
        return self.k < o.k

def test_min_max_ties():
    # on ties, min/max return the first argument
    p, q = MinMaxTie(1, 'a'), MinMaxTie(1, 'b')
    assert min(p, q).n == 'a'
    assert max(p, q).n == 'a'
    assert min(p, q, MinMaxTie(1, 'c')).n == 'a'
    assert max(p, q, MinMaxTie(1, 'c')).n == 'a'
    assert min([p, q]).n == 'a'
    assert max([p, q]).n == 'a'
    assert min(x for x in [p, q]).n == 'a'
    assert max(x for x in [p, q]).n == 'a'
    assert min('aa', 'bb', key=len) == 'aa'
    assert max('aa', 'bb', key=len) == 'aa'
    assert min('aa', 'bb', 'cc', key=len) == 'aa'
    assert max('aa', 'bb', 'cc', key=len) == 'aa'
    assert str(min(-0.0, 0.0)) == '-0.0'
    assert str(max(0.0, -0.0)) == '0.0'
    assert str(min(0.0, -0.0)) == '0.0'
    assert str(max(-0.0, 0.0)) == '-0.0'

def test_oct():
    assert oct(10) == '0o12'


def test_ord():
    assert ord('a') == 97
    assert ord('z') == 122
    assert ord('1') == 49
    assert ord('9') == 57
    # constant arguments are folded at compile time
    assert ord(' ') + ord(b'*') == 74
    assert ord('\xe9') == 233
    assert ord('\u20ac') == 0x20ac
    assert ord(b'\xff') == 255
    c = 'q'
    assert ord(c) == ord('q')


class Account:
    def __init__(self):
        self._cash = 0

    @property
    def cash(self):
        return self._cash

    @cash.setter
    def cash(self, amount):
        self._cash = amount


def test_property():
    a = Account()
    assert a.cash == 0
    a.cash = 10
    assert a.cash == 10


def test_print():  # TODO print to StringIO and check?
    print('')
    print('\n')
    print(None)
    print({1, 2})
    print([])
    print(1, 2.2, end='hoep', sep='--')
    print()
    assert True


def test_print_stringio():
    f = io.StringIO()
    print('', file=f)
    print('\n', file=f)
    print({1}, file=f)
    print([], file=f)
    print(1, 2.2, end='hoep', sep='--', file=f)
    print(file=f)
    print(1, None, 'x', file=f, sep=None, end=None)
    assert f.getvalue() == '\n\n\n{1}\n[]\n1--2.2hoep\n1 None x\n'

    # literal None (a bare C++ NULL) printed as '0'
    f = io.StringIO()
    print(None, file=f)
    print('a', None, file=f)
    print(None, None, sep='-', file=f)
    print(None, 1, flush=True, file=f)
    assert f.getvalue() == 'None\na None\nNone-None\nNone 1\n'

    f = io.StringIO()
    print(None, sep=None, end='', file=f)
    assert f.getvalue() == 'None'


def test_range():
    a = 1

    assert list(range(1, 10, 1)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(10, 1, -1)) == [10, 9, 8, 7, 6, 5, 4, 3, 2]
    assert list(range(1, 10, +1)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, a)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(10, 1, -a)) == [10, 9, 8, 7, 6, 5, 4, 3, 2]
    assert list(range(1, 10, +a)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, a * 1)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, -(-1))) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, +(+a))) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    assert list(range(1, 10, 1)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, +1)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, a)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, +a)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, -(-1))) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, +(+1))) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(1, 10, +(+a))) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(range(10, 1, -1)) == [10, 9, 8, 7, 6, 5, 4, 3, 2]
    assert list(range(10, 1, -a)) == [10, 9, 8, 7, 6, 5, 4, 3, 2]

    assert len(range(5)) == 5
    assert max(range(10)) == 9
    assert min(range(10)) == 0
    assert list(range(3)) == [0, 1, 2]
    assert sum(range(20)) == 190
    assert list(range(1, 10, 2)) == [1, 3, 5, 7, 9]
    assert list(range(-17, -120, -17)) == [-17, -34, -51, -68, -85, -102, -119]

    # list(range(a, b, c)) with a runtime step: direction/step mismatches
    # must yield an empty list rather than looping forever or crashing
    # (regression test for a bug in the __ss_list_range() fast path,
    # which under -O2 could invoke undefined behavior via unbounded
    # signed-integer increment and crash instead of terminating)
    assert list(range(5, 0, a)) == []
    assert list(range(0, 5, -a)) == []

    # step=0 (only detectable at runtime here) must raise ValueError,
    # matching plain for-loop iteration over range(), not hang/crash
    zero = a - 1
    try:
        list(range(0, 5, zero))
        assert False, "expected ValueError for step=0"
    except ValueError:
        pass

    r = range(4, 10, 2)
    assert r.start == 4
    assert r.stop == 10
    assert r.step == 2
    assert 8 in r
    assert 9 not in r

    r = range(1, 10)
    assert r.count(7) == 1
    assert r.count(77) == 0
    assert r.index(7) == 6

    assert r[7] == 8
    assert bool(r)
    assert not bool(range(0))

    # negative step: count()/index() must use the same sign-aware bounds
    # check as __contains__ (they previously always returned "not found")
    r = range(10, 0, -1)
    assert r.count(10) == 1
    assert r.count(5) == 1
    assert r.count(1) == 1
    assert r.count(0) == 0
    assert r.count(11) == 0
    assert r.index(10) == 0
    assert r.index(5) == 5
    assert r.index(1) == 9

    try:
        r.index(0)
        assert False
    except ValueError:
        pass

    r = range(-5, -20, -3)
    assert list(r) == [-5, -8, -11, -14, -17]
    assert r.count(-11) == 1
    assert r.index(-11) == 2
    assert r.count(-12) == 0

    # step size > 1 skips values even when within bounds
    r = range(1, 10, 2)
    assert r.count(2) == 0
    assert r.count(3) == 1
    assert r.index(3) == 1


def test_range_beyond_32_bits():
    # range lengths used to be computed in 32-bit arithmetic, so anything past
    # 2 ** 31 wrapped: len() returned 705032704 here and indexing raised
    big = 5000000000

    assert len(range(0, big)) == big
    assert len(range(big, 0, -1)) == big
    assert range(0, big)[3000000000] == 3000000000
    assert range(0, big)[-1] == big - 1
    assert len(range(0, big, 3)) == 1666666667

    assert list(range(4000000000, 4000000003)) == [4000000000, 4000000001, 4000000002]
    assert list(reversed(range(4000000000, 4000000003))) == [4000000002, 4000000001, 4000000000]

    assert 4000000000 in range(0, big)
    assert list(range(0, big)[3000000000:3000000003]) == [3000000000, 3000000001, 3000000002]


def test_range_near_int_limits():
    # stepping past the last value used to overflow: iteration then never
    # ended, and lengths, indices and slices near the limits came out wrong
    M = 9223372036854775807
    m = -M - 1

    r = range(M - 3, M, 2)
    assert len(r) == 2
    assert list(r) == [M - 3, M - 1]
    assert [i for i in r] == [M - 3, M - 1]
    assert list(reversed(r)) == [M - 1, M - 3]
    assert r[-1] == M - 1
    assert list(range(m + 3, m, -2)) == [m + 3, m + 1]
    assert list(reversed(range(m, m + 7, 3))) == [m + 6, m + 3, m]
    assert list(range(0, M, M - 1)) == [0, M - 1]

    # the length does not fit (as in CPython), but the rest works
    big = range(m, M)
    assert big[0] == m and big[-1] == M - 1 and big[5] == m + 5
    assert M - 1 in big and big.count(M - 1) == 1
    assert range(m, M, 2).index(M - 1) == M
    it = iter(reversed(big))
    assert next(it) == M - 1 and next(it) == M - 2
    try:
        len(big)
        assert False
    except OverflowError:
        pass

    # slices whose CPython stop does not fit stop just past the last value
    assert list(range(0, M, 2)[-2:]) == [M - 3, M - 1]
    assert list(range(M - 5, M, 2)[::-1]) == [M - 1, M - 3, M - 5]
    assert list(range(M - 9, M)[1::3]) == [M - 8, M - 5, M - 2]
    assert list(range(m + 9, m, -1)[1::3]) == [m + 8, m + 5, m + 2]


def test_range_slicing():
    r = range(2,20,2)
    assert list(r[2:4:3]) == [6]
    assert list(r[::2]) == [2, 6, 10, 14, 18]
    assert list(r[1:5:]) == [4, 6, 8, 10]
    assert list(r[-5:-2:]) == [10, 12, 14]
    assert list(r[4:1:]) == []
    assert list(r[4:1:-2]) == [10, 6]

    r = range(-5,-5,-5)
    assert list(r[-5:-4:1]) == []

def test_range_equality():
    # ranges compare (and hash) by the sequence they produce, not by identity
    assert range(5) == range(5)
    assert range(0, 10, 3) == range(0, 11, 3)
    assert range(0) == range(5, 2, 3)
    assert range(3, 4) == range(3, 9, 100)
    assert range(0, 3) != range(0, 3, 2)
    assert range(1, 3) != range(2, 4)
    assert range(10, 0, -2) != range(0, 10, 2)
    assert not (range(5) != range(0, 5, 1))
    assert range(2, 20, 2)[::2] == range(2, 20, 4)

    M = 9223372036854775807
    m = -M - 1
    assert range(m, M) == range(m, M, 1)
    assert range(m, M) != range(m + 1, M)

    assert hash(range(0, 10, 3)) == hash(range(0, 11, 3))
    assert hash(range(0)) == hash(range(7, 2))
    assert hash(range(3, 4)) == hash(range(3, 5, 9))
    assert len({range(0), range(4, 1), range(1), range(0, 1, 5), range(2)}) == 3
    d = {range(3): 'a'}
    assert d[range(0, 3, 1)] == 'a'
    assert range(0, 3) in [range(4), range(3)]

def test_repr():
    assert repr(1) == '1'
    assert repr(1.1) == '1.1'


class Asciied:
    def __repr__(self):
        return 'Asciied(\u00e9)'


def test_ascii():
    assert ascii(1) == '1'
    assert ascii(1.5) == '1.5'
    assert ascii(True) == 'True'
    assert ascii(None) == 'None'
    assert ascii('hoi') == "'hoi'"
    assert ascii('') == "''"
    assert ascii('caf\u00e9') == "'caf\\xe9'"
    assert ascii('\u20ac5') == "'\\u20ac5'"
    assert ascii('\U0001f600') == "'\\U0001f600'"
    assert ascii('a\nb\\') == "'a\\nb\\\\'"
    assert ascii(b'\xe9') == "b'\\xe9'"
    assert ascii(['\u00ff', 'x']) == "['\\xff', 'x']"
    assert ascii({'\u0100': 1}) == "{'\\u0100': 1}"
    assert ascii(('\u00e9', 2)) == "('\\xe9', 2)"
    assert ascii(Asciied()) == 'Asciied(\\xe9)'
    s = 'na\u00efve'
    assert ascii(s) == repr(s).replace('\u00ef', '\\xef')
    assert '%a' % 'caf\u00e9' == "'caf\\xe9'"
    assert '%a|%a' % ('\u20ac', 3) == "'\\u20ac'|3"
    assert '%(x)a' % {'x': '\u00e9'} == "'\\xe9'"
    assert '%8a' % '\u00e9' == "  '\\xe9'"


def test_reversed():
    assert list(reversed([1,2,3])) == [3,2,1]
    assert list(reversed(['a','b','c'])) == ['c','b','a']


def test_round():
    assert round(0.5) == 0
    assert round(1.5) == 2
    assert round(2.5) == 2
    assert round(3.5) == 4
    assert round(4.5) == 4

    assert round(-1.5) == -2
    assert round(-2.5) == -2
    assert round(-3.5) == -4
    assert round(-4.5) == -4

    assert round(1.15, 0) == 1.0

    # round(x, n) must round the exact binary value of x, not a value
    # that has already picked up its own floating point error from
    # multiplying/dividing by 10**n, and ties must round to even.
    assert round(2.675, 2) == 2.67
    assert round(-2.675, 2) == -2.67
    assert round(0.125, 2) == 0.12
    assert round(2.5, 0) == 2.0
    assert round(0.5, 0) == 0.0
    assert round(1.25, 1) == 1.2
    assert round(1234.5, -2) == 1200.0

    # round(int, -n): ties to even, and exact beyond 2**53
    assert round(5, -1) == 0
    assert round(15, -1) == 20
    assert round(25, -1) == 20
    assert round(-15, -1) == -20
    assert round(-25, -1) == -20
    assert round(1249, -2) == 1200
    assert round(1251, -2) == 1300
    assert round(12345, 2) == 12345
    assert round(2**60 + 7, -1) == 2**60 + 4
    assert round(2**60 + 7, -30) == 0
    assert round(25.0, -1) == 20.0
    assert round(15.0, -1) == 20.0
    assert round(-0.0, 2) == 0.0

    # round(x) always returns int; round(x, ndigits) preserves the input's type
    assert str(round(2.5)) == '2'
    assert str(round(2.5, 1)) == '2.5'
    assert str(round(5, 2)) == '5'
    assert str(round(1234, -2)) == '1200'

    # round(inf/nan) raises (it used to return INT64_MIN), round(x, n) doesn't
    inf, nan = float('inf'), float('nan')
    for x in [inf, -inf, nan]:
        error = ''
        try:
            round(x)
        except OverflowError as e:
            error = 'OverflowError: ' + str(e)
        except ValueError as e:
            error = 'ValueError: ' + str(e)
        if x != x:
            assert error == 'ValueError: cannot convert float NaN to integer'
        else:
            assert error == 'OverflowError: cannot convert float infinity to integer'
    assert round(inf, 2) == inf
    assert round(-inf, -1) == -inf
    assert str(round(nan, 2)) == 'nan'

    # a finite value that rounds beyond the float range raises
    big = 1.7976931348623157e308
    for x, n in [(big, -308), (-big, -308), (big, -304)]:
        error = ''
        try:
            round(x, n)
        except OverflowError as e:
            error = str(e)
        assert error == 'rounded value too large to represent'
    assert round(big, -303) == 1.79769e308
    assert round(-9.5e307, -308) == -1e308


def test_set():
    assert sorted(set([1,2,3,4]).difference(set([3]))) == [1, 2, 4]


def test_str():
    assert str(1) == '1'
    assert str(1.5) == '1.5'


def test_sum():
    assert sum([1.0, 5.0]) == 6.0
    assert sum(range(100)) == 4950
    assert sum([1, 2, 3]) == 6
    assert sum([1, 2, 3], 4) == 10
    assert sum([[1], [2], [3, 4]], [0]) == [0, 1, 2, 3, 4]
    assert sum([[1], [2], [3, 4]], []) == [1, 2, 3, 4]
    a = [1,2,3]
    a = []
    assert sum(a, start=7) == 7

    xs = [1, 2, 3]
    d = sum(xs)
    assert d == 6

    e = sum(xs, 100)
    assert e == 106

    f = sum(xs, start=100)
    assert f == 106

    # bool elements sum to int
    g = sum([True, False, True])
    assert g == 2
    assert g + 1 == 3
    h = sum([True, True], 0)
    assert h + 1 == 3
    assert sum(x == 1 for x in [1, 2, 1]) == 2
    assert True + True == 2

    # start type takes part in result type
    assert sum([1, 2], 0.5) == 3.5
    assert sum([1.5, 2.5], 1) == 5.0
    assert sum([(1,), (2,)], ()) == (1, 2)

    # user-defined __add__
    v = sum([SumVec(1), SumVec(2)], SumVec(10))
    assert v.x == 13

    try:
        sum(['a', 'b'], '')
        assert False
    except TypeError as err:
        assert str(err) == "sum() can't sum strings [use ''.join(seq) instead]"
    try:
        sum([b'a', b'b'], b'')
        assert False
    except TypeError as err:
        assert str(err) == "sum() can't sum bytes [use b''.join(seq) instead]"
    try:
        sum(['a', 'b'])
        assert False
    except TypeError as err:
        assert str(err) == "unsupported operand type(s) for +: 'int' and 'str'"
    try:
        sum([b'a', b'b'])
        assert False
    except TypeError as err:
        assert str(err) == "unsupported operand type(s) for +: 'int' and 'bytes'"
    try:
        sum([s for s in ['a', 'b']])  # fused listcomp
        assert False
    except TypeError as err:
        assert str(err) == "unsupported operand type(s) for +: 'int' and 'str'"


class SumVec:
    def __init__(self, x):
        self.x = x

    def __add__(self, other):
        return SumVec(self.x + other.x)


def test_tuple():
    assert tuple([1,2]) == (1,2)

# def test_type():
#     assert type(1) == type(2)
#     assert type(1.0) == type(2.0)
#     assert type("2") == type("3")


def test_zip():
    assert list(zip([1,2])) == [(1,), (2,)]
    assert list(zip([1,2], [3, 4])) == [(1, 3), (2, 4)]
    assert list(zip([1,2], ['a','b'])) == [(1, 'a'), (2, 'b')]
    assert list(zip([1,2,3], [4,5,6], [7,8,9])) == [(1,4,7), (2,5,8), (3,6,9)]
    assert list(zip([1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15])) == [(1,4,7,10,13), (2,5,8,11,14), (3,6,9,12,15)]


def test_all():
    test_abs()
    # test_ascii()
    test_bin()
    test_bool()
    test_bytes()
    # test_callable()
    test_chr()
    test_complex()
    # test_delattr()
    test_divmod()
    test_enumerate()
    test_filter()
    test_float()
    test_float_invalid()
    # test_getattr()
    # test_hasattr()
    test_hash()
    test_hex()
    test_int()
    test_int_base()
    test_isinstance() # always returns True
    # test_issubclass()
    test_len()
    test_max()
    test_min()
    test_min_max_ties()
    test_oct()
    test_ord()
    test_pow()
    test_property()
    test_print()
    test_print_stringio()
    test_range()
    test_range_beyond_32_bits()
    test_range_near_int_limits()
    test_range_slicing()
    test_range_equality()
    test_repr()
    test_ascii()
    test_reversed()
    test_round()
    test_set()
    test_str()
    test_sum()
    test_tuple()
    # test_type()
    test_zip()


if __name__ == '__main__':
    test_all()
