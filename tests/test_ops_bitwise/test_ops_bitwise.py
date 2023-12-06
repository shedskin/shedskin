
def test_bitwise_operators():
    #from: https://www.tutorialspoint.com/python/bitwise_operators_example.htm

    a = 60            # 60 = 0011 1100 
    b = 13            # 13 = 0000 1101 
    c = 0

    c = a & b        # 12 = 0000 1100
    assert c == 12

    c = a | b        # 61 = 0011 1101
    assert c == 61

    c = a ^ b        # 49 = 0011 0001
    assert c == 49

    c = ~a           # -61 = 1100 0011
    assert c == -61

    c = a << 2       # 240 = 1111 0000
    assert c == 240

    c = a >> 2       # 15 = 0000 1111
    assert c == 15


def test_bitwise_bases():
    assert 0xFF << 24       == 0xFF000000
    assert 0xFF << 24       == int(0xFF000000)
    assert 255 << 24        == 4278190080
    assert 0b11111111 << 24 == 4278190080




def test_all():
    test_bitwise_operators()
    test_bitwise_bases()

if __name__ == '__main__':
    test_all() 
