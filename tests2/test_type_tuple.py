
def get_tuple():
    return (5, 6)

def recv_tuple(t):
    return t


def test_tuple():
    a = get_tuple()
    assert [(1, 2), (3, 4), a, get_tuple()] == [(1, 2), (3, 4), (5, 6), (5, 6)]
    assert recv_tuple((1,2,3)) == (1,2,3)

def test_equivalence():
    assert [1, 2] == [1, 2]
    assert [(1, 2), (2, 3)] == [(1, 2), (2, 3)]
    assert [(1, 4), (2, 3)] != [(1, 2), (2, 3)]


def test_membership():
    assert 1 in (1,)
    assert 1 in (1, 2, 3)
    assert 1 in (1, 2)
    assert 3 not in (1, 2)

    assert (1, 2) in [(1, 2), (2, 3)]
    assert (1, 4) not in [(1, 2), (2, 3)]

    assert ((1,)) in [((2,)), ((1,))]
    assert ((3,)) not in [((2,)), ((1,))]

    assert [1] in ([2], [1])

    assert 1.0 in (1.0,2.0,3.0)


def return_tuple(x):
    return (x, x+1)


def test_return_tuple():
    assert return_tuple(5) == (5, 6)


def test_all():
    test_tuple()
    test_equivalence()
    test_membership()
    test_return_tuple()


if __name__ == "__main__":
    test_all()


