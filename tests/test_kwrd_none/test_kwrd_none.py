


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


def in_str_none(c):
    return c in ("x", None)


def not_in_str_none(c):
    return c not in [None, "x"]


def in_int_none(n):
    return n in (None, 1)


def in_ints(x):
    return x in (1, 2)


def in_floats(n):
    return n in (1.5, 2)


def test_in_const_tuple_none():
    # 'x in (const, ..)' is inlined as a chain of __eq calls. None used to
    # be emitted as a bare NULL (no matching __eq for str*), and the temp
    # var was typed after the first element (so 1.5 in (1, 2) was True).
    assert in_str_none("x")
    assert not in_str_none("y")
    assert in_str_none(None)
    assert not not_in_str_none("x")
    assert not_in_str_none("y")
    assert not not_in_str_none(None)
    assert in_int_none(1)
    assert not in_int_none(0)
    assert not in_ints(1.5)
    assert in_ints(2.0)
    assert in_ints(1)
    assert in_floats(1.5)
    assert in_floats(2)
    assert not in_floats(1)
    t = True
    assert t in (1, 2)
    assert t not in (0, None)


def test_all():
    test_none()
    test_str_repr_none()
    test_in_const_tuple_none()

if __name__ == '__main__':
    test_all() 

