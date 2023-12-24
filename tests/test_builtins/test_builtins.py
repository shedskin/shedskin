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

class Klass:
    def __init__(self, name):
        self.name = name

class SubKlass(Klass): pass

def test_abs():
    assert abs(-10) == 10

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
    # assert bytes('a', encoding='utf8') == b'a'
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

def test_enumerate():
    assert [(i, obj) for i, obj in enumerate(['a', 'b', 'c'])] == [(0, 'a'), (1, 'b'), (2, 'c')]

def test_filter():
    is_gt_10 = lambda x: x > 10
    xs = range(12)
    assert list(filter(is_gt_10, xs)) == [11]

def test_float():
    assert float(100) == 100.0

def test_hash():
    assert hash('abc') == hash('abc')
    assert hash('abc') != hash('cba')

# def test_hasattr():
#     c = complex(4,2)
#     assert hasattr(c, 'real')

def test_int():
    assert int(100.2) == 100

    assert int.bit_count(12345) == 6
    assert int.bit_count(0b11111111111111111111111111111111) == 32
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

def test_oct():
    assert oct(10) == '0o12'

def test_ord():
    assert ord('a') == 97
    assert ord('z') == 122
    assert ord('1') == 49
    assert ord('9') == 57


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
    assert True

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

def test_repr():
    assert repr(1) == '1'
    assert repr(1.1) == '1.1'

def test_reversed():
    assert list(reversed([1,2,3])) == [3,2,1]
    assert list(reversed(['a','b','c'])) == ['c','b','a']

def test_round():
    assert round(1.5) == 2
    assert round(1.15, 0) == 1.0

def test_set():
    assert list(set([1,2,3,4]).difference(set([3]))) == [1, 2, 4]

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
    # test_getattr()
    # test_hasattr()
    test_hash()
    test_hex()
    test_int()
    test_isinstance() # always returns True
    # test_issubclass()
    test_len()
    test_max()
    test_min()
    test_oct()
    test_ord()
    test_property()
    test_print()
    test_range()
    test_repr()
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





