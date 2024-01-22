import array


def test_typecodes():
    assert array.typecodes == 'bBuhHiIlLqQfd'

    arr = array.array('i')
    assert arr.typecode == 'i'
    assert arr.itemsize == 4


def test_file():
    pass
    # tofile
    # fromfile

    # f = open("testdata/blabla", "wb")
    # arr4.tofile(f)
    # f.close()
    # arr5 = array.array("i")
    # f = open("testdata/blabla", "rb")
    # arr5.fromfile(f, 2)
    # try:
    #     arr5.fromfile(f, 2)
    # except EOFError as e:
    #     print(e)
    # f.close()


def test_list():
    arr = array.array('i', [1, 2])
    arr.fromlist([3, 4, 5])
    assert arr.tolist() == [1, 2, 3, 4, 5]


def test_bytes():
    pass
    # tobytes
    # frombytes


def test_sequence_immutable():
    arr = array.array('i', range(5, 15))
    assert arr[3] == 8
    assert arr.index(8) == 3
    assert arr.count(6) == 1
    assert 14 in arr
    assert 15 not in arr
    assert len(arr) == 10
    assert arr + arr == array.array('i', 2 * list(range(5, 15)))
    assert arr * 2 == 2 * arr
    assert list(3 * arr) == 3 * list(range(5, 15))

    # slicing
    arr = array.array("B")
    arr.extend(list(range(20)))
    assert arr == array.array('B', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    assert arr[:] == array.array('B', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    assert arr[-7:] == array.array('B', [13, 14, 15, 16, 17, 18, 19])
    assert arr[-7::2] == array.array('B', [13, 15, 17, 19])
    assert arr[:8:3] == array.array('B', [0, 3, 6])
    assert arr[15:1:-2] == array.array('B', [15, 13, 11, 9, 7, 5, 3])


def test_sequence_mutable():
    pass
    # __setitem__
    # __delitem__
    # extend
    # pop
    # remove
    # insert
    # append
    # reverse
    # byteswap?
    # __delslice__
    # __setslice__
    # __delete__


def test_all():
    test_typecodes()
    test_list()
    test_bytes()
    test_file()
    test_sequence_immutable()
    test_sequence_mutable()


if __name__ == '__main__':
    test_all()
