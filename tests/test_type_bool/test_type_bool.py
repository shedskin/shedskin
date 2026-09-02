

def test_bool():
    assert bool(0) == False
    assert bool(1) == True
    assert int(True) == 1
    assert int(False) == 0

    assert not (True & True & False)
    assert (True & True & True)

    assert True & 1
    assert not 1 & False
    assert True * 5 == 5
    assert False * 5 == 0

    assert True *  [1, 2] == [1, 2]
    assert False * [1, 2] == []


def test_empty():
    assert bool([]) == bool(None)
    assert bool(set()) == bool(())
    assert bool({}) == bool("")
    assert bool(0.0) == bool(0)


class Bert:
    pass


class Bert2:
    def __bool__(self):
        return False

class Bert3:
    def __len__(self):
        return 0


def test_custom():
    b = Bert()
    assert bool(b)

    b2 = Bert2()
    assert not bool(b2)

    b3 = Bert3()
    assert not bool(b3)


def test_containers():
    # dict with bool values (dict<K, __ss_bool> instantiates __ne/__none)
    d = {0: True, 1: False}
    e = {0: True, 1: False}
    f = {0: True, 1: True}

    assert d == e
    assert not (d != e)
    assert d != f
    assert not (d == f)

    assert d[0] == True
    assert d.get(1, True) == False
    assert d.get(7, True) == True
    assert sorted(d.values()) == [False, True]
    assert sorted(d.items()) == [(0, True), (1, False)]

    g = d.copy()
    assert g == d
    assert g.pop(0) == True
    assert sorted(g.items()) == [(1, False)]

    # bool as dict key
    dd = {True: 0, False: 1}
    assert dd[True] == 0
    assert dd[False] == 1
    assert sorted(dd.keys()) == [False, True]

    # set/list/tuple of bools
    s = {True, False}
    assert sorted(s) == [False, True]
    assert True in s

    l = [True, False]
    assert l == [True, False]
    assert not (l != [True, False])
    assert l != [False, True]
    assert sorted(l) == [False, True]
    assert l.count(True) == 1
    assert l.index(False) == 1

    t = (True, False)
    assert t == (True, False)
    assert t != (True, True)
    assert t < (True, True)


def test_all():
    test_bool()
    test_empty()
    test_custom()
    test_containers()


if __name__ == "__main__":
    test_all()
