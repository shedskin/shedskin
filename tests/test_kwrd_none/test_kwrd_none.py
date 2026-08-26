


def test_none():
    x = "0,0"
    b = str(x)
    a = [[1]]
    c = [None, [2]]

    assert a != c
    assert not a == c
    assert a is not c

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
    assert a is not None

    assert c[0] == None
    assert c[0] is None
    assert not c[0] != None

    assert c[1] != None
    assert not c[1] == None
    assert c[1] is not None


def test_str_repr_none():
    # str(None)/repr(None) used to collide with the int-formatting
    # overloads of __str()/repr() at the C++ level (None compiles to a
    # bare NULL, which is also a valid "integer 0"), silently returning
    # "0" instead of "None".
    n = None
    assert str(None) == "None"
    assert str(n) == "None"
    assert repr(None) == "None"
    assert repr(n) == "None"
    assert "value: " + str(None) == "value: None"


def test_all():
    test_none()
    test_str_repr_none()

if __name__ == '__main__':
    test_all() 

