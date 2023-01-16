


def ident(x):
    return x

def hu(n, s=-1):
    return [1]


def test_list_misc():
    assert [[i] for i in range(5)] == [[0], [1], [2], [3], [4]]
    assert [(2*a, b) for a in range(4) if a > 0 for b in ['1','2']] == [(2, '1'), (2, '2'), (4, '1'), (4, '2'), (6, '1'), (6, '2')]
    assert ['' for i in range(2)] == ['', '']

    ah = []
    ident(ah).append(1)
    ident(ah).append(1.0)
    assert ah ==  [1, 1.0]

def test_list_comp():
    bla = [1,2]
    dinges = [1,2]
    jada = [1,2]
    d = (1, (1.1, "u"))

    assert [x for x in bla] == bla
    assert [[a for a in bla] for c in dinges] == [[1, 2], [1, 2]]
    assert [[[a for a in jada] for c in bla] for d in dinges] == [[[1, 2], [1, 2]], [[1, 2], [1, 2]]]
    assert [0 for s in ["hah"]] == [0]
    assert [bah.upper() for bah in ("hah", "bah")] == ['HAH', 'BAH']
    assert [0 for (str, bah) in [("hah", "bah")]] == [0]
    assert [i for i in hu(10)] == [1]
    assert [((v, u), w) for u, (v, w) in [d]] == [((1.1, 1), 'u')]

def test_list_nested():
    q = [[[1],[2]],[[3],[4]]]

    assert [i+1.2 for i in [1, 1., 2., 3.2]] == [2.2, 2.2, 3.2, 4.4]
    assert list(i+1.2 for i in [1, 1., 2., 3.2]) == [2.2, 2.2, 3.2, 4.4]

    # c = [[1,2],(3,4)]
    # assert c[0] == [1,2]
    # assert c[1] == (3,4)

    assert q[0][0][0] == 1
    assert q[0][1][0] == 2
    assert q[1][0][0] == 3
    assert q[1][1][0] == 4

    # e = [3, [1, 2]]
    # assert e[0] == 3
    # assert e[1] == [1,2]

def test_list_index1():
    a = [1, 2, 3]
    assert a[0] == 1
    assert a[1] == 2
    assert a[-2] == 2 
    assert a[-1] == 3

def test_list_index2():
    xs = [1, 2, 3, 1]
    assert xs.index(1) == 0
    assert xs.index(1, 1) == 3
    assert xs.index(1, -1) == 3
    assert xs.index(1, -4) == 0
    assert xs.index(1, -3, 4) == 3

def test_list_slice():
    a = [1,2,3,4,5]
    assert a[:-1] == [1, 2, 3, 4]
    assert a[1:3] == [2, 3]
    assert a[::]  == [1, 2, 3, 4, 5]
    assert a[:3:] == [1, 2, 3]
    assert a[::-1] == [5, 4, 3, 2, 1]
    assert a[1::3] == [2, 5]

def test_list_del():
    a = list(range(10))
    del a[9]
    assert a == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    del a[1:3]
    assert a == [0, 3, 4, 5, 6, 7, 8]
    del a[::2]
    assert a == [3, 5, 7]

def test_list_append():
    a = []
    a.append(1.0)
    assert a[0] == 1.0

    b = []
    b.append(1)
    assert b[0] == 1

    c = []
    c.append("astring")
    assert c[0] == "astring"

    d = []
    d.append("1")
    assert d[0] == "1"

    e = []
    e.append([1])
    assert e[0] == [1]

def test_tuple_in_list():
    list4 = [(1,2),(3,4)]
    assert (1,2) in list4

def test_list_assign():
    list5 = [(1,2),(3,4)]
    list5[0] = (2,2)
    assert list5 == [(2,2),(3,4)]

def test_list_length():
    puzzlecolumns = [1]
    assert puzzlecolumns.__len__() == 1

# def test_list_copy():
#     a = [(1,2),(3,4)]
#     b = list4.copy() # NotImplemented
#     assert b[0] == [1,2]

def subsets(sequence):
    result = [[]] * (2 ** len(sequence))
    for i, e in enumerate(sequence):
        i2, el = 2**i, [e]
        for j in range(i2):
            result[j + i2] = result[j] + el
    return result

def test_list_subsets():
    assert subsets(range(4)) == [[], [0], [1], [0, 1], [2], [0, 2], [1, 2], [0, 1, 2], [3], [0, 3], [1, 3], [0, 1, 3], [2, 3], [0, 2, 3], [1, 2, 3], [0, 1, 2, 3]]

def test_list_cmp():
    assert [2, 3] > [1, 2, 3]




def test_all():
    test_list_append()
    test_list_assign()
    test_list_cmp()
    test_list_comp()
    test_list_del()
    test_list_index1()
    test_list_index2()
    test_list_length()
    test_list_misc()
    test_list_nested()
    test_list_slice()
    test_list_subsets()
    test_tuple_in_list()


if __name__ == "__main__":
    test_all()



