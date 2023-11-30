
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

    assert [v for v in [(1,),(2,),(3,)] if v != (1,)] == [(2,), (3,)]

def test_iteration():
    res = 0
    for c in [(2,3),(3,4)]:
        if c == (3,4):
            res = 1
    assert res == 1

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

    assert 12 in (10, 12, 14)
    assert 12 not in (7, 8, 9)
    assert 12 in (10, 12, 14)
    assert 12 not in (7, 8, 9)


def test_variable():
    a = (1,2)
    assert (1,2) == a
    assert a == [(1,2),(3,4)][0]
    assert a != (2,3)
    assert a in [(1,2),(3,4)]
    assert a in [(1,x) for x in range(3)]

def return_tuple(x):
    return (x, x+1)


def test_return_tuple():
    assert return_tuple(5) == (5, 6)

def test_add():
    a = (1, 2)
    b = (1, 2, 3)
    c = a
    c = b
    d = a + b
    assert d == (1, 2, 1, 2, 3)


def test_mul():
    a = (0,)
    b = a * 4
    assert b == (0, 0, 0, 0)

    c = (1, 2)
    d = 2 * c
    assert d == (1, 2, 1, 2)


def test_all():
    test_tuple()
    test_equivalence()
    test_membership()
    test_return_tuple()
    test_variable()
    test_iteration()
    test_add()
    test_mul()




if __name__ == "__main__":
    test_all()


