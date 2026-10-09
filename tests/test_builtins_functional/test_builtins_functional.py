
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
    except ValueError:
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
    except ValueError:
        error = True
    assert error


def test_zip_exhaustion():
    # arguments of different lengths, repeatedly
    for n in range(4):
        assert list(zip(list(range(n)), list(range(n + 1)))) == [(i, i) for i in range(n)]
    assert list(zip('abc', [1, 2])) == [('a', 1), ('b', 2)]
    assert list(zip([1, 2, 3], [4, 5], [6, 7, 8])) == [(1, 4, 6), (2, 5, 7)]
    assert [a + b for a, b in zip([1, 2, 3], (10, 20))] == [11, 22]
    assert list(zip((x * x for x in range(4)), [1, 2])) == [(0, 1), (1, 2)]
    assert dict(zip(['a', 'b'], [1, 2, 3])) == {'a': 1, 'b': 2}

    # next() on an exhausted zip object keeps raising StopIteration
    z = zip([1], [2])
    assert next(z) == (1, 2)
    stops = 0
    for i in range(2):
        try:
            next(z)
        except StopIteration:
            stops += 1
    assert stops == 2

    # arguments after the first exhausted one are not advanced
    it = iter([1, 2, 3])
    assert list(zip('ab', it)) == [('a', 1), ('b', 2)]
    assert list(it) == [3]
    it2 = iter([1, 2, 3])
    assert list(zip([5], [6], it2)) == [(5, 6, 1)]
    assert list(it2) == [2, 3]

    # .. but strict=True checks all of them
    it3 = iter([1, 2, 3])
    error = False
    try:
        list(zip([5], [6], it3, strict=True))
    except ValueError:
        error = True
    assert error
    assert list(zip([5, 6], [7, 8], [9, 10], strict=True)) == [(5, 7, 9), (6, 8, 10)]


def test_zip_sequences():
    # list arguments are indexed directly: like a list iterator, zip sees
    # items appended to or removed from a list during iteration
    l = [1, 2]
    z = zip(l, (5, 6, 7, 8))
    assert next(z) == (1, 5)
    l.append(3)
    assert list(z) == [(2, 6), (3, 7)]
    l2 = [1, 2, 3]
    z2 = zip(('a', 'b', 'c'), l2)
    assert next(z2) == ('a', 1)
    l2.pop()
    assert list(z2) == [('b', 2)]

    # mixed with iterators: those after an exhausted argument are not advanced
    it = iter([1, 2, 3])
    assert list(zip([7], it)) == [(7, 1)]
    assert list(it) == [2, 3]
    it2 = iter('xyz')
    assert list(zip(it2, (1, 2))) == [('x', 1), ('y', 2)]
    assert list(it2) == []  # 'z' was consumed before the tuple ran out

    error = False
    try:
        list(zip((1, 2), [3], strict=True))
    except ValueError:
        error = True
    assert error
    assert list(zip((1, 2), [3, 4], strict=True)) == [(1, 3), (2, 4)]

    # other argument types
    d = {'a': 1, 'b': 2, 'c': 3}
    assert sorted(zip(d, 'xxx')) == [('a', 'x'), ('b', 'x'), ('c', 'x')]  # dict order is unspecified
    assert dict(zip('ab', [1.5, 2.5])) == {'a': 1.5, 'b': 2.5}
    assert list(zip(range(3), (4, 5, 6))) == [(0, 4), (1, 5), (2, 6)]
    assert sorted(zip({7, 8}, [1, 1])) == [(7, 1), (8, 1)]

    # consumers that iterate a zip object directly: list(), sorted(), dict(),
    # comprehensions and for-loops, also after it was partly consumed
    z3 = zip([1, 2, 3], (4, 5, 6))
    assert next(z3) == (1, 4)
    assert [a + b for a, b in z3] == [7, 9]
    assert list(z3) == []
    z4 = zip('abc', [3, 1, 2])
    total = 0
    for k, v in z4:
        total += v
    assert total == 6 and list(z4) == []
    assert sorted(zip([3, 1], ['x', 'y'])) == [(1, 'y'), (3, 'x')]
    assert dict(zip([1, 2], [1.5, 2.5])) == {1: 1.5, 2: 2.5}


def test_map():
    assert list(map(lambda a: 2 * a, [1, 2, 3])) == [2, 4, 6]
    assert list(map(lambda a, b: a * b, [1, 2, 3], [4, 5])) == [4, 10]
    assert list(map(lambda a, b, c: a + b + c, [1, 2, 3], [3, 4, 5], [5, 4, 3])) == [9, 10, 11]

    a = iter([1,2,3])
    b = iter([1,2])
    error = False
    try:
        list(map(lambda a,b:a+b, a, b, strict=True))
    except ValueError:
        error = True
    assert error

    a = iter([1,2])
    b = iter([1,2,3])
    c = iter([1,2,3])
    error = False
    try:
        list(map(lambda a,b,c:a+b-c, a, b, c, strict=True))
    except ValueError:
        error = True
    assert error


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
    test_zip_exhaustion()
    test_zip_sequences()
    test_map()
    test_map_nested()

if __name__ == '__main__':
    test_all()

