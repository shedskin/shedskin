def f1():
    a = g1()
    return a

def g1():
    return [1, 2]

def f2():
    f3(v3())

def f3(x):
    global bye
    bye = x

def v3():
    return [1]

def j1():
    x = v3()

def t1():
    a = v2()
    h1()
    return a

def v2():
    return [1, 2]

def h1():
    a = v2()
    a.append(3)


def test_order():
    x = f1()
    assert x == [1,2]

    y = f1()
    assert y == [1,2]

    y.append(3)
    assert y == [1,2,3]

    f2()

    bye.append(2)
    assert bye == [1,2]

    j1()
    assert t1() == [1,2]


def test_all():
    test_order()

if __name__ == "__main__":
    test_all()



