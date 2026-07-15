

def test_list():
    assert [(b, a) for a, b in enumerate([1, 2, 3])] == [(1, 0), (2, 1), (3, 2)]
    assert [(a, "%.1f" % b) for a, b in enumerate([1.1, 2.2, 3.3])] == [(0, '1.1'), (1, '2.2'), (2, '3.3')]


def test_iter():
    it = iter([9, 8, 7])
    assert list(enumerate(it)) == [(0, 9), (1, 8), (2, 7)]


def test_start_positional():
    assert list(enumerate(['a', 'b', 'c'], 5)) == [(5, 'a'), (6, 'b'), (7, 'c')]


def test_start_keyword():
    assert list(enumerate(['a', 'b', 'c'], start=5)) == [(5, 'a'), (6, 'b'), (7, 'c')]


def test_start_negative():
    assert list(enumerate('xyz', start=-2)) == [(-2, 'x'), (-1, 'y'), (0, 'z')]


def test_start_with_iterator():
    it = iter([9, 8, 7])
    assert list(enumerate(it, start=10)) == [(10, 9), (11, 8), (12, 7)]


def test_start_keyword_forloop():
    # don't use FOR_IN_ENUMERATE with 'start' argument for now
    result = []
    for i, v in enumerate(['a', 'b', 'c'], start=1):
        result.append((i, v))
    assert result == [(1, 'a'), (2, 'b'), (3, 'c')]


def test_all():
    test_list()
    test_iter()
    test_start_positional()
    test_start_keyword()
    test_start_negative()
    test_start_with_iterator()
    test_start_keyword_forloop()


if __name__ == '__main__':
    test_all()

