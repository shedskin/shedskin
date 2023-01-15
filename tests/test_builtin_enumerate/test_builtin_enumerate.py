

def test_e1():
    assert [(b, a) for a, b in enumerate([1, 2, 3])] == [(1, 0), (2, 1), (3, 2)]
    assert [(a, "%.1f" % b)for a, b in enumerate([1.1, 2.2, 3.3])] == [(0, '1.1'), (1, '2.2'), (2, '3.3')]



def test_all():
    test_e1()

if __name__ == '__main__':
    test_all()

