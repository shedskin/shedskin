


def test_none():
    x = "0,0"
    b = str(x)
    a = [[1]]
    c = [None, [2]]
    assert a != c 

    d = [3]
    d = None
    e = [4]
    e = None

    d == e
    e == None
    d == None
    a == None
    c[0] == None
    c[1] == None


def test_all():
    test_none()

if __name__ == '__main__':
    test_all() 

