
def test_abs():
    assert abs(-10) == 10


def test_all_logic():
    assert all([1, 1, 0 , 1, 0]) == False
    assert all([True, True]) == True


def test_any_logic():
    assert any([True, False, False]) == True

def test_and():
    assert 1 and 1
    assert 1 and 1 and 1 and 1

# def test_or():
#     assert 0 or 1
#     assert not 0 or 0

# def test_and_or():
#     assert (0 or 0 or 1) and 1

# def test_ascii():
#     assert ascii(1) == '1'

def test_bin():
    assert bin(3) == '0b11'

# def test_callable():
#     assert callable(abs)

def test_chr():
    assert chr(97) == 'a'

def test_complex():
    c = complex(1,2)
    assert c.imag == 2.0

def test_filter():
    is_gt_10 = lambda x: x > 10
    xs = range(12)
    assert list(filter(is_gt_10, xs)) == [11]

# def test_hasattr():
#     c = complex(4,2)
#     assert hasattr(c, 'real')

# def test_getattr():
#     c = complex(4,2)
#     assert getattr(c, 'real') == 4.0


def test_misc(): pass
    # assert bytes('a') == b'a'
    





def test_all():
    test_abs()
    test_all_logic()
    test_any_logic()
    # test_or()
    # test_and_or()
    # test_ascii()
    test_bin()
    test_chr()
    test_complex()
    test_misc()
    test_filter()
    # test_hasattr()
    # test_getattr()

if __name__ == '__main__':
    test_all()





