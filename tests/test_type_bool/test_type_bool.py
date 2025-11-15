

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


def test_all():
    test_bool()
    test_empty()
    test_custom()


if __name__ == "__main__":
    test_all()
