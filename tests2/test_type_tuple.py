



def gettuple():
    return (5,6)


def test_tuple():
    a = gettuple()
    assert [(1,2),(3,4), a, gettuple()] == [(1,2), (3,4), (5,6), (5,6)]


def test_equivalence():
    assert [1,2] == [1,2]
    assert [(1,2),(2,3)] == [(1,2),(2,3)]
    assert [(1,4),(2,3)] != [(1,2),(2,3)]


def test_membership():
    assert 1 in (1,2,3)
    assert 1 in (1,2)
    assert 3 not in (1,2)

    assert (1,2) in [(1,2),(2,3)]
    assert (1,4) not in [(1,2),(2,3)]

    assert ((1,)) in [((2,)),((1,))]
    assert ((3,)) not in [((2,)),((1,))]

    assert [1] in ([2],[1])


if __name__ == '__main__':
    test_tuple()
    test_equivalence()
    test_membership()

