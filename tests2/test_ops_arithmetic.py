


def test_operators():
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
    test_operators()

if __name__ == '__main__':
    test_all() 


