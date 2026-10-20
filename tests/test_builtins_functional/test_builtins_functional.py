
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

    # the same iterator passed twice
    it4 = iter([0, 1, 2, 3, 4])
    assert list(zip(it4, it4)) == [(0, 1), (2, 3)]
    assert list(it4) == []
    gen = (x * 10 for x in range(4))
    assert list(zip(gen, gen)) == [(0, 10), (20, 30)]
    it5 = iter('abcdef')
    assert [a + b for a, b in zip(it5, it5)] == ['ab', 'cd', 'ef']


def zip_strict_error(z):
    try:
        for t in z:
            pass
    except ValueError as e:
        return str(e)
    return ''


def test_zip_strict_messages():
    # which argument is shorter or longer than the ones before it
    assert zip_strict_error(zip([1, 2], [3], strict=True)) == 'zip() argument 2 is shorter than argument 1'
    assert zip_strict_error(zip([1], [3, 4], strict=True)) == 'zip() argument 2 is longer than argument 1'
    assert zip_strict_error(zip(iter([1, 2]), iter([3]), strict=True)) == 'zip() argument 2 is shorter than argument 1'
    assert zip_strict_error(zip((x for x in [1]), [3, 4], strict=True)) == 'zip() argument 2 is longer than argument 1'
    assert zip_strict_error(zip([1, 2], [3, 4], [5], strict=True)) == 'zip() argument 3 is shorter than arguments 1-2'
    assert zip_strict_error(zip([1, 2], [3], [5, 6], strict=True)) == 'zip() argument 2 is shorter than argument 1'
    assert zip_strict_error(zip([1], [3], [5, 6], strict=True)) == 'zip() argument 3 is longer than arguments 1-2'
    assert zip_strict_error(zip([1], [3], [5], [7, 8], strict=True)) == 'zip() argument 4 is longer than arguments 1-3'
    assert zip_strict_error(zip([1], [3], [5, 6], [7, 8], strict=True)) == 'zip() argument 3 is longer than arguments 1-2'
    assert zip_strict_error(zip([1, 2], [3, 4], [5, 6], [7], strict=True)) == 'zip() argument 4 is shorter than arguments 1-3'
    assert zip_strict_error(zip([1, 2], [3, 4], [5, 6], strict=True)) == ''

    error = ''
    try:
        list(zip('ab', [1], strict=True))
    except ValueError as e:
        error = str(e)
    assert error == 'zip() argument 2 is shorter than argument 1'

    # arguments after a shorter one are not advanced
    a, b, c = iter([1, 9]), iter([2]), iter([3, 4, 5])
    assert zip_strict_error(zip(a, b, c, strict=True)) == 'zip() argument 2 is shorter than argument 1'
    assert list(a) == []
    assert list(c) == [4, 5]


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


def map_strict_error(m):
    try:
        for x in m:
            pass
    except ValueError as e:
        return str(e)
    return ''


def test_map_strict_messages():
    f2 = lambda a, b: a + b
    f3 = lambda a, b, c: a + b + c
    assert map_strict_error(map(f2, [1, 2], [3], strict=True)) == 'map() argument 2 is shorter than argument 1'
    assert map_strict_error(map(f2, [1], [3, 4], strict=True)) == 'map() argument 2 is longer than argument 1'
    assert map_strict_error(map(f3, [1, 2], [3, 4], [5], strict=True)) == 'map() argument 3 is shorter than arguments 1-2'
    assert map_strict_error(map(f3, [1, 2], [3], [5, 6], strict=True)) == 'map() argument 2 is shorter than argument 1'
    assert map_strict_error(map(f3, [1], [3], [5, 6], strict=True)) == 'map() argument 3 is longer than arguments 1-2'
    assert map_strict_error(map(f3, [1], [3, 4], [5], strict=True)) == 'map() argument 2 is longer than argument 1'
    assert map_strict_error(map(f3, [1], [3], [5], strict=True)) == ''


def test_map_exhaustion():
    f2 = lambda a, b: a
    f3 = lambda a, b, c: a

    # arguments after the first exhausted one are not advanced
    it1 = iter([1])
    it2 = iter(['a', 'b'])
    assert list(map(f2, it1, it2)) == [1]
    assert list(it2) == ['b']

    a = iter([1])
    b = iter(['a', 'b'])
    c = iter([1.0, 2.0])
    assert list(map(f3, a, b, c)) == [1]
    assert list(b) == ['b']
    assert list(c) == [2.0]

    a = iter([1, 2, 3])
    b = iter(['a'])
    c = iter([1.0, 2.0, 3.0])
    assert list(map(f3, a, b, c)) == [1]
    assert list(a) == [3]
    assert list(c) == [2.0, 3.0]

    a = iter([1, 2, 3])
    b = iter(['a', 'b', 'c'])
    c = iter([1.0])
    assert list(map(f3, a, b, c)) == [1]
    assert list(a) == [3]
    assert list(b) == ['c']

    # .. but strict=True checks the later ones if the first is exhausted
    a = iter([1])
    b = iter(['a'])
    c = iter([1.0, 2.0])
    assert map_strict_error(map(f3, a, b, c, strict=True)) == 'map() argument 3 is longer than arguments 1-2'
    assert list(c) == []

    # .. and not if a later one is
    a = iter([1, 2])
    b = iter(['a'])
    c = iter([1.0, 2.0])
    assert map_strict_error(map(f3, a, b, c, strict=True)) == 'map() argument 2 is shorter than argument 1'
    assert list(c) == [2.0]

    # an exhausted map object stays exhausted
    m = map(f2, iter([1]), iter(['a']))
    assert list(m) == [1]
    assert list(m) == []


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
    test_zip_strict_messages()
    test_zip_sequences()
    test_map()
    test_map_strict_messages()
    test_map_exhaustion()
    test_map_nested()

if __name__ == '__main__':
    test_all()

