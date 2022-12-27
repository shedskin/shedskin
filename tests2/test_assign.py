

def test_assign_int():
    a = 1
    assert a == 1

def test_assign_list():
    a = [1]
    assert a == [1]

def test_reference():
    a = []
    a.append(1)

    b = a

    a = []
    a.append(2)

    assert b == [1]

def test_destructure():
    a, b = "ab"
    assert a == "a"
    assert b == "b"

    a, b, c, d, e = "abcde"
    assert a == "a"
    assert b == "b"
    assert c == "c"
    assert d == "d"
    assert e == "e"

    a, b = tuple("ab")
    assert a == "a"
    assert b == "b"

    a, b, c, d, e = tuple("abcde")
    assert a == "a"
    assert b == "b"
    assert c == "c"
    assert d == "d"
    assert e == "e"


def test_all():
    test_assign_int()
    test_assign_list()
    test_reference()
    test_destructure()




if __name__ == '__main__':
    test_all()
