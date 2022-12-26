import bisect


def test_bisect():
    xs = [1, 2, 3, 4, 5, 6, 6, 7]
    n = 4
    assert bisect.bisect_left(xs, n) == 3
    assert bisect.bisect_left(xs, n, 0) == 3
    assert bisect.bisect_left(xs, n, 0, len(xs)) == 3
    assert bisect.bisect_right(xs, n) == 4
    assert bisect.bisect(xs, n) == 4

    bisect.insort_left(xs, n)
    assert xs == [1, 2, 3, 4, 4, 5, 6, 6, 7]

    bisect.insort_right(xs, n)
    assert xs == [1, 2, 3, 4, 4, 4, 5, 6, 6, 7]

    bisect.insort(xs, n)
    assert xs == [1, 2, 3, 4, 4, 4, 4, 5, 6, 6, 7]


def test_all():
    test_bisect()
    

if __name__ == '__main__':
    test_all() 