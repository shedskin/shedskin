


def test_none():
    x = "0,0"
    b = str(x)
    a = [[1]]
    c = [None, [2]]

    assert a != c
    assert not a == c
    assert not a is c

    d = [3]
    d = None
    e = [4]
    e = None

    assert d == e
    assert d is e
    assert not d != e

    assert e == None
    assert e is None

    assert d == None
    assert d is None

    assert not a == None
    assert not a is None

    assert c[0] == None
    assert c[0] is None
    assert not c[0] != None

    assert c[1] != None
    assert not c[1] == None
    assert not c[1] is None


def test_all():
    test_none()

if __name__ == '__main__':
    test_all() 

