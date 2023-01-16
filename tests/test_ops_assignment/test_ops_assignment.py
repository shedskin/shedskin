

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

def test_slice_assign():
    d = list(range(10))
    d[::2] = [1, 2, 3, 4, 5]
    assert d == [1, 1, 2, 3, 3, 5, 4, 7, 5, 9]
    d[1:2] = [1,2,2,3,3]
    assert d == [1, 1, 2, 2, 3, 3, 2, 3, 3, 5, 4, 7, 5, 9]

def test_destructure1():
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

def test_destructure2():

    foo = (2, [4, 6])
    [a, (b, c)] = foo
    assert (a, b, c) == (2, 4, 6)

def test_destructure3():

    (a, b), (c, d) = (6, 9), (8, 7)
    assert (a, b, c, d) == (6, 9, 8, 7)

def test_destructure4():

    [(a, b), (c, d)] = (9, 8), (7, 6)
    assert (a, b, c, d) == (9, 8, 7, 6)

def test_destructure5():

    [(a, b), (c, d)] = [(1, 8), (7, 2)]
    assert (a, b, c, d) == (1, 8, 7, 2)

def test_destructure6():

    [[a, b], c] = (5, 6), 3
    assert (a, b, c) == (5, 6, 3)

def test_destructure7():

    [[a, b], c] = [[4, 5], 6]
    assert (a, b, c) ==  (4, 5, 6)

def test_destructure8():

    a, [b, c] = [1, (2, 3)]
    assert (a, b, c) == (1, 2, 3)

def test_destructure9():

    a, (b, c, d) = 1, (1, 2, 3)
    assert (a, b, c, d) == (1, 1, 2, 3)

def test_destructure10():

    [(a, b), [c, d]] = [[1, 2], (3, 4)]
    assert (a, b, c, d) ==  (1, 2, 3, 4)

def test_destructure11():

    njeh = [[8, 7, 6], [5, 4, 3], [2, 1, 0]]
    [[a, b, c], [d, e, f], [g, h, i]] = njeh
    assert (a, b, c, d, e, f, g, h, i) == (8, 7, 6, 5, 4, 3, 2, 1, 0)

    [dx, [a, b, c], ex] = njeh
    assert (dx, a, b, c, ex) == ([8, 7, 6], 5, 4, 3, [2, 1, 0])

def test_destructure12():

    blah = (1, 2, 3, 4, 5, 6)
    a, b, c, d, e, f = blah
    assert (a, b, c, d, e, f) == (1, 2, 3, 4, 5, 6)



def test_all():
    test_assign_int()
    test_assign_list()
    test_reference()
    test_slice_assign()
    test_destructure1()
    test_destructure2()
    test_destructure3()
    test_destructure4()
    test_destructure5()
    test_destructure6()
    test_destructure7()
    test_destructure8()
    test_destructure9()
    test_destructure10()
    # test_destructure11()
    test_destructure12()



if __name__ == '__main__':
    test_all()
