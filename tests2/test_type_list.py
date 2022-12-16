

# def test_list_copy():
#     a = [(1,2),(3,4)]
#     b = list4.copy() # NotImplemented
#     assert b[0] == [1,2]


def test_list_slice():
    a = [1,2,3,4,5]
    assert a[:-1] == [1, 2, 3, 4]
    assert a[1:3] == [2, 3]
    assert a[::]  == [1, 2, 3, 4, 5]
    assert a[:3:] == [1, 2, 3]
    assert a[::-1] == [5, 4, 3, 2, 1]

def test_list_append():
    list1 = []
    list1.append(1.0)
    assert list1[0] == 1.0

    list2 = []
    list2.append(1)
    assert list2[0] == 1

    list3 = []
    list3.append("astring")
    assert list3[0] == "astring"


def test_tuple_in_list():
    list4 = [(1,2),(3,4)]
    assert (1,2) in list4


def test_list_assign():
    list5 = [(1,2),(3,4)]
    list5[0] = (2,2)
    assert list5 == [(2,2),(3,4)]




if __name__ == '__main__':
    test_list_assign()
    test_list_append()
    test_tuple_in_list()
    test_list_slice()
