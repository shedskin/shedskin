

def test_list():
    assert [(b, a) for a, b in enumerate([1, 2, 3])] == [(1, 0), (2, 1), (3, 2)]
    assert [(a, "%.1f" % b) for a, b in enumerate([1.1, 2.2, 3.3])] == [(0, '1.1'), (1, '2.2'), (2, '3.3')]


def test_iter():
    it = iter([9, 8, 7])
    assert list(enumerate(it)) == [(0, 9), (1, 8), (2, 7)]


def test_all():
    test_list()
    test_iter()


if __name__ == '__main__':
    test_all()

