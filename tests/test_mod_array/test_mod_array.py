import array
import os.path


def test_typecodes():
    assert array.typecodes == 'bBuwhHiIlLqQfd'

    arr = array.array('i')
    assert arr.typecode == 'i'
    assert arr.itemsize == 4


def test_file():
    testdir = os.curdir
    while not os.path.exists(os.path.join(testdir, "testdata")) and os.path.exists(os.pardir):
        testdir = os.path.join(testdir, os.pardir)
    testdata = os.path.join(testdir, "testdata")
    assert os.path.exists(testdata)

    arr = array.array('i', range(10))
    with open(testdata + "/blabla", "wb") as f:
        arr.tofile(f)

    arr2 = array.array("i")
    with open(testdata + "/blabla", "rb") as f:
        arr2.fromfile(f, 10)

    assert arr == arr2


def test_bytes():
    arr = array.array('i', range(10))
    bs = arr.tobytes()

    arr2 = array.array("i")
    arr2.frombytes(bs)

    assert arr == arr2

    arr2.frombytes(bs)
    assert arr2 == arr + arr


def test_list():
    arr = array.array('i', [1, 2])
    arr.fromlist([3, 4, 5])
    assert arr.tolist() == [1, 2, 3, 4, 5]


def test_sequence_immutable():
    arr = array.array('i', range(5, 15))
    assert arr[3] == 8
    assert arr.index(8) == 3
    assert arr.index(8, 0) == 3
    assert arr.index(8, 0, -1) == 3
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
    arr = array.array('i', range(5, 11))

    arr[1] = 17
    assert arr.tolist() == [5, 17, 7, 8, 9, 10]

    del arr[2]
    assert arr.tolist() == [5, 17, 8, 9, 10]

    arr.append(11)
    arr.extend([12, 13])
    assert arr.tolist() == [5, 17, 8, 9, 10, 11, 12, 13]

    assert arr.pop() == 13
    assert arr.pop(-2) == 11
    assert arr.pop(0) == 5
    assert arr.tolist() == [17, 8, 9, 10, 12]

    arr.append(9)
    arr.remove(9)
    assert arr.tolist() == [17, 8, 10, 12, 9]

    arr.insert(0, 12)
    assert arr.tolist() == [12, 17, 8, 10, 12, 9]
    arr.insert(-2, 21)
    assert arr.tolist() == [12, 17, 8, 10, 21, 12, 9]

    arr.reverse()
    assert arr.tolist() == [9, 12, 21, 10, 8, 17, 12]

    arr.byteswap()
    assert arr[0] == 0x9000000
    assert arr[-1] == 0xc000000
    arr.byteswap()
    assert arr.tolist() == [9, 12, 21, 10, 8, 17, 12]

    del arr[1::2]
    assert arr.tolist() == [9, 21, 8, 12]

    arr[::2] = array.array('i', [17, 18])
    assert arr.tolist() == [17, 21, 18, 12]

    arr.clear()
    assert len(arr) == 0


def test_all():
    test_typecodes()
    test_list()
    test_bytes()
    test_file()
    test_sequence_immutable()
    test_sequence_mutable()


if __name__ == '__main__':
    test_all()
