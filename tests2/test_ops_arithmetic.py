

def test_addition():
    # int
    a = 2
    assert 0 + 2 == 2
    assert 1 + 2 == 3
    a += 3
    assert a == 5

    # float
    b = 2.0
    assert 0.0 + 2.0 == 2.0
    assert 1.0 + 2.0 == 3.0
    b += 3.0
    assert b == 5.0

    # hex
    c = 0x32
    assert 0x00 + 0x32 == 0x32
    assert 0x16 + 0x32 == 0x48
    c += 0x32
    assert c == 0x64

    # octal
    d = 0o2
    assert 0o0 + 0o20 == 0o20
    assert 0o16 + 0o32 == 0o50
    d += 0o32
    assert d == 0o34

    e = [2]
    assert [] + [1,2] == [1, 2]
    assert [3,4] + [1,2] == [3, 4, 1, 2]
    e += [1, 0]
    assert e == [2,1,0]

def test_subtraction():
    x = 4
    assert 2 - 0 == 2
    assert 0 - 2 == -2
    assert 2 - 1 == 1
    x -= 2
    assert x == 2


def test_misc():
    f = -112
    f //= -3
    assert f == 37
    assert f // -3 == -13

    f %= -3
    assert f == -2

    f //= -1
    assert f == 2

    d = {}

    val = 9.0
    i = 4
    j = 5

    d[i, j] = 3.0

    d[i, j] += val
    assert d[i, j] == 12.0

    d[i, j] *= val
    assert d[i, j] == 108.0

    d[i, j] /= val
    assert d[i, j] == 12.0

    assert d ==  {(4, 5): 12.0}

    e = {}
    e[i, j] = -7

    e[i, j] //= -2
    e[i, j] == 3

    e[i, j] *= -2
    e[i, j] == -6

    e[i, j] %= -2
    e[i, j] == 0

    e[i, j] //= -2
    e[i, j] == 0

    assert e == {(4, 5): 0}

def test_all():
    test_addition()
    test_subtraction()
    # test_multiplication()
    # test_division()
    test_misc()

if __name__ == '__main__':
    test_all() 


