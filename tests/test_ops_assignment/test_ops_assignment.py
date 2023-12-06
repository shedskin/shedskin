

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

def test_unpack1():
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

def test_unpack2():

    foo = (2, [4, 6])
    [a, (b, c)] = foo
    assert (a, b, c) == (2, 4, 6)

def test_unpack3():

    (a, b), (c, d) = (6, 9), (8, 7)
    assert (a, b, c, d) == (6, 9, 8, 7)

def test_unpack4():

    [(a, b), (c, d)] = (9, 8), (7, 6)
    assert (a, b, c, d) == (9, 8, 7, 6)

def test_unpack5():

    [(a, b), (c, d)] = [(1, 8), (7, 2)]
    assert (a, b, c, d) == (1, 8, 7, 2)

def test_unpack6():

    [[a, b], c] = (5, 6), 3
    assert (a, b, c) == (5, 6, 3)

def test_unpack7():

    [[a, b], c] = [[4, 5], 6]
    assert (a, b, c) ==  (4, 5, 6)

def test_unpack8():

    a, [b, c] = [1, (2, 3)]
    assert (a, b, c) == (1, 2, 3)

def test_unpack9():

    a, (b, c, d) = 1, (1, 2, 3)
    assert (a, b, c, d) == (1, 1, 2, 3)

def test_unpack10():

    [(a, b), [c, d]] = [[1, 2], (3, 4)]
    assert (a, b, c, d) ==  (1, 2, 3, 4)

def test_unpack11():

    njeh = [[8, 7, 6], [5, 4, 3], [2, 1, 0]]
    [[a, b, c], [d, e, f], [g, h, i]] = njeh
    assert (a, b, c, d, e, f, g, h, i) == (8, 7, 6, 5, 4, 3, 2, 1, 0)

    [dx, [a, b, c], ex] = njeh
    assert (dx, a, b, c, ex) == ([8, 7, 6], 5, 4, 3, [2, 1, 0])

def test_unpack12():

    blah = (1, 2, 3, 4, 5, 6)
    a, b, c, d, e, f = blah
    assert (a, b, c, d, e, f) == (1, 2, 3, 4, 5, 6)


def test_unpack13():
    t = (1, 'aap')
    tx, ty = t
    assert tx == 1
    assert ty == 'aap'


def test_unpack14():
    s1, s2 = set([7, 8])
    assert sorted([s1, s2]) == [7, 8]

    m1, m2, m3 = map(lambda x: 2*x, [9,10,11])
    assert (m1, m2, m3) == (18, 20, 22)


def test_unpack15():
    val_error = False
    try:
        c1, c2 = b'hoi'
    except ValueError:
        val_error = True
    assert val_error

    val_error = False
    try:
        m1, m2, m3, m4 = map(lambda x: 2*x, [9,10,11])
    except ValueError:
        val_error = True
    assert val_error


def test_walrus():
    walrus = False
    assert str(walrus := True) == 'True'
    assert str(walrus) == 'True'


def test_walrus2():
    users = [
        {'name': 'John Doe', 'occupation': 'gardener'},
        {'name': None, 'occupation': 'teacher'}, 
    ]

    result = None
    for user in users:
        if ((name := user.get('name')) is not None):
            result = f'{name} is a {user.get("occupation")}'

    assert result == 'John Doe is a gardener'


import re

def test_walrus3():
    data = 'There is a book on the table.'

    pattern = re.compile(r'book')

    if match := pattern.search(data):
        print(f'The word {pattern.pattern} is at {match.start(), match.end()}') 
    else:
        print(f'No {pattern.pattern} found')


def cube(num):
    return num ** 3


def test_walrus4():
    l = [y for x in range(10) if (y := cube(x)) < 20]

    assert l == [0, 1, 8]


def test_walrus5():
    total = 0
    partial_sums = [total := total + v for v in range(5)]
    assert total == 10



def test_all():
    test_assign_int()
    test_assign_list()
    test_reference()
    test_slice_assign()
    test_unpack1()
    test_unpack2()
    test_unpack3()
    test_unpack4()
    test_unpack5()
    test_unpack6()
    test_unpack7()
    test_unpack8()
    test_unpack9()
    test_unpack10()
    # test_unpack11()
    test_unpack12()
    test_unpack13()
    test_unpack14()
    test_unpack15()
    test_walrus()
    test_walrus2()
    test_walrus3()
    test_walrus4()
    test_walrus5()


if __name__ == '__main__':
    test_all()
