
builtins = [
    # 'aiter',
    # 'anext',
    ## 'ascii',
    # 'breakpoint',
    ## 'callable',
    # 'classmethod',
    # 'compile',
    # 'copyright',
    # 'credits',
    ##'delattr',
    ##'dir',
    #'display',
    #'eval',
    #'exec',
    'format',
    'frozenset',
    ##'getattr',
    #'globals',
    ##'hasattr',
    # 'help',
    #'id',
    'input',
    'isinstance',
    'issubclass',
    'iter',
    'len',
    'license',
    'list',
    'locals',
    'map',
    'max',
    'memoryview',
    'min',
    'next',
    'object',
    'oct',
    'open',
    'ord',
    'pow',
    'print',
    'property',
    'range',
    'repr',
    'reversed',
    'round',
    'set',
    'setattr',
    'slice',
    'sorted',
    'staticmethod',
    'str',
    'sum',
    'super',
    'tuple',
    'type',
    'vars',
    'zip'
 ]

class Klass:
    def __init__(self, name):
        self.name = name

def test_abs():
    assert abs(-10) == 10

# def test_ascii():
#     assert ascii(1) == '1'

def test_bin():
    assert bin(3) == '0b11'

def test_bool():
    assert bool(2 > 1) == True

def test_bytes():
    assert bytes('a', encoding='utf8') == b'a'

def test_callable():
    assert callable(abs)

def test_chr():
    assert chr(97) == 'a'

def test_complex():
    c = complex(1,2)
    assert c.imag == 2.0

# def test_delattr():
#     obj = Klass('sam')
#     assert hasattr(obj, 'name')
#     delattr(obj, 'name')
#     assert not hasattr(obj, 'name')

def test_divmod():
    assert divmod(10, 2) == (5, 0)

def test_enumerate():
    assert [(i, obj) for i, obj in enumerate(['a', 'b', 'c'])] == [(0, 'a'), (1, 'b'), (2, 'c')]

def test_filter():
    is_gt_10 = lambda x: x > 10
    xs = range(12)
    assert list(filter(is_gt_10, xs)) == [11]

def test_hash():
    assert hash('abc') == hash('abc')
    assert hash('abc') != hash('cba')

# def test_hasattr():
#     c = complex(4,2)
#     assert hasattr(c, 'real')

# def test_getattr():
#     c = complex(4,2)
#     assert getattr(c, 'real') == 4.0

def test_hex():
    assert hex(1) == '0x1'

def test_isinstance():
    obj = Klass('foo')
    assert isinstance(obj, Klass)





    





def test_all():
    test_abs()
    # test_ascii()
    test_bin()
    test_bool()
    # test_bytes()
    # test_callable()
    test_chr()
    test_complex()
    # test_delattr()
    test_divmod()
    test_enumerate()
    test_filter()
    # test_getattr()
    # test_hasattr()
    test_hash()
    test_hex()
    test_isinstance()

if __name__ == '__main__':
    test_all()





