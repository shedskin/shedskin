def escapement():
    a = vars1()
    return a

def vars1():
    return [1, 2]

def escapement2():
    bla(vars3())

def bla(x):
    global bye
    bye = x

def vars3():
    return [1]

def joink():
    x = vars3()

def transitive():
    a = vars2()
    hoi()
    return a

def vars2():
    return [1, 2]

def hoi():
    a = vars2()
    a.append(3)


def test_order():
    x = escapement()
    assert x == [1,2]

    y = escapement()
    assert y == [1,2]

    y.append(3)
    assert y == [1,2,3]

    escapement2()

    bye.append(2)
    assert bye == [1,2]

    joink()
    assert transitive() == [1,2]


def test_all():
    test_order()

if __name__ == "__main__":
    test_all()



