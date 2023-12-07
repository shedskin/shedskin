
def test_filter():
    assert list(filter(lambda c: c > "a", "abaaac")) == ['b', 'c']


def test_reversed():
    assert list(reversed(range(10, 20, 2))) == [18, 16, 14, 12, 10]


def test_enumerate():
    assert list(enumerate("bun")) == [(0, 'b'), (1, 'u'), (2, 'n')]


def test_range():
    assert list(range(11, 4, -2)) == [11, 9, 7, 5]
    assert len(range(8, 20)) == 12
    assert range(8, 20)[5] == 13
    assert range(8, 20)[-2] == 18


def test_zip():
    assert list(zip()) == []
    assert list(zip([1,2])) == [(1,), (2,)]
    assert list(zip([1, 2], [3, 4])) == [(1, 3), (2, 4)]
    assert list(list(zip([1, 2], [3, 4], [5, 6]))) == [(1, 3, 5), (2, 4, 6)]


def test_zip_strict():
    # different types
    a = iter([1, 2])
    b = iter(['a', 'b', 'c'])
    assert list(zip(a, b)) == [(1, 'a'), (2, 'b')]

    a = iter([1,2])
    b = iter(['a', 'b', 'c'])
    error = False
    try:
        list(zip(a, b, strict=True))
    except ValueError as e:
        error = True
    assert error

    # homogeneous
    a = iter([1,2])
    b2 = iter([3,4,5])
    assert list(zip(a, b2)) == [(1, 3), (2, 4)]

    a = iter([1,2])
    b2 = iter([3,4,5])
    error = False
    try:
        list(zip(a, b2, strict=True))
    except ValueError as e:
        error = True
    assert error


def test_map():
    assert list(map(lambda a: 2 * a, [1, 2, 3])) == [2, 4, 6]
    assert list(map(lambda a, b: a * b, [1, 2, 3], [4, 5])) == [4, 10]
    assert list(map(lambda a, b, c: a + b + c, [1, 2, 3], [3, 4, 5], [5, 4, 3])) == [9, 10, 11]


def test_map_nested():
    foo3 = lambda a, b, c: "%d %.2f %s" % (a, b, c)
    flats = (chr(ord("A") + x) for x in range(3))
    assert list(map(foo3, range(3), map(float, list(range(1, 4))), flats)) == ['0 1.00 A', '1 2.00 B', '2 3.00 C']


def test_all():
    test_filter()
    test_reversed()
    test_enumerate()
    test_range()
    test_zip()
    test_zip_strict()
    test_map()
    test_map_nested()

if __name__ == '__main__':
    test_all()

