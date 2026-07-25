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


def test_codes():  # TODO check these type codes: bBuwhHiIlLfd
    arr = array.array('q', [1,2,3])
    assert list(arr) == [1,2,3]

    arr = array.array('Q', [3,2,1])
    assert list(arr) == [3,2,1]


def test_mul_nonpositive():
    # negative or zero multiplier must yield an empty array, not crash
    arr = array.array('i', [1, 2, 3])
    assert arr * -1 == array.array('i')
    assert arr * -100 == array.array('i')
    assert arr * 0 == array.array('i')
    assert -1 * arr == array.array('i')

    # original array must be untouched by __mul__
    assert arr.tolist() == [1, 2, 3]

    arr2 = array.array('i', [1, 2, 3])
    arr2 *= -1
    assert arr2 == array.array('i')

    arr3 = array.array('i', [1, 2, 3])
    arr3 *= 0
    assert arr3 == array.array('i')

    # sanity check positive multiplier still works
    arr4 = array.array('i', [1, 2])
    assert arr4 * 2 == array.array('i', [1, 2, 1, 2])


def test_insert_out_of_range():
    # insert() must clamp like list.insert(), not raise IndexError
    arr = array.array('i', [1, 2, 3])
    arr.insert(100, 9)
    assert arr.tolist() == [1, 2, 3, 9]

    arr2 = array.array('i', [1, 2, 3])
    arr2.insert(-100, 9)
    assert arr2.tolist() == [9, 1, 2, 3]

    # in-range and negative-in-range inserts still behave normally
    arr3 = array.array('i', [1, 2, 3])
    arr3.insert(1, 9)
    assert arr3.tolist() == [1, 9, 2, 3]

    arr4 = array.array('i', [1, 2, 3])
    arr4.insert(-1, 9)
    assert arr4.tolist() == [1, 2, 9, 3]


def test_repr_empty():
    assert repr(array.array('i')) == "array('i')"
    assert repr(array.array('i', [1, 2])) == "array('i', [1, 2])"


def test_double_typecode_roundtrip():
    # 'd' arrays must store/retrieve full-width doubles regardless of the
    # --float32 build flag (which only affects the *runtime* float type,
    # not the on-disk/in-memory width of a typecode 'd' array element).
    arr = array.array('d', [1.0, 2.0, 3.5, -7.25])
    assert arr.itemsize == 8
    lst = arr.tolist()
    for got, expected in zip(lst, [1.0, 2.0, 3.5, -7.25]):
        assert abs(got - expected) < 1e-6
    assert arr[0] == 1.0
    assert arr[1] == 2.0


def test_bytes_initializer_itemsize_gt_1():
    # a bytes/bytearray initializer (or argument to frombytes-equivalent
    # construction) must be interpreted as packed binary data via
    # frombytes(), not iterated byte-by-byte as a generic sequence of
    # ints -- the latter only happens to give the right answer when
    # itemsize == 1 ('b'/'B').
    arr = array.array('h', bytes([1, 0, 2, 0]))
    assert arr.tolist() == [1, 2]

    arr2 = array.array('i', bytes([1, 0, 0, 0, 2, 0, 0, 0]))
    assert arr2.tolist() == [1, 2]

    # itemsize == 1 should still work as before
    arr3 = array.array('B', b'hi')
    assert arr3.tolist() == [104, 105]


def test_index_not_found_message():
    arr = array.array('i', [1, 2, 3])
    try:
        arr.index(99)
        assert False, "expected ValueError"
    except ValueError as e:
        assert str(e) == "array.index(x): x not in array"


def test_frombytes_validates_against_itemsize():
    # frombytes() must validate the byte length against the array's real
    # itemsize (4 for 'f'), not sizeof(the C++ template parameter behind
    # it, which is 8 for a double-backed float implementation) -- a
    # single 'f' element is 4 bytes and must be accepted.
    arr = array.array('f')
    arr.frombytes(bytes([0, 0, 128, 63]))  # 1.0f, little-endian
    assert len(arr) == 1
    assert abs(arr[0] - 1.0) < 1e-6


def test_pop_empty_message():
    # pop() on an empty array must report "array", not "list" (it was
    # copy-pasted from list's error message).
    arr = array.array('i')
    try:
        arr.pop()
        assert False, "expected IndexError"
    except IndexError as e:
        assert str(e) == "pop from empty array"


def test_remove_not_found_message():
    # remove() delegated to index() to find the element, which meant a
    # failed remove() incorrectly raised index()'s error message instead
    # of its own distinct one.
    arr = array.array('i', [1, 2, 3])
    try:
        arr.remove(99)
        assert False, "expected ValueError"
    except ValueError as e:
        assert str(e) == "array.remove(x): x not in array"


def test_extend_bytes_is_elementwise():
    # unlike the array(typecode, bytes-like) *constructor*, which reinterprets
    # a bytes/bytearray argument as a raw packed buffer, extend() must treat
    # bytes/bytearray as an ordinary iterable of small ints (0-255 each),
    # matching CPython.
    arr = array.array('i')
    arr.extend(bytes([1, 0, 0, 0, 2, 0, 0, 0]))
    assert arr.tolist() == [1, 0, 0, 0, 2, 0, 0, 0]

    arr2 = array.array('i')
    arr2.extend(bytearray([1, 0, 0, 0, 2, 0, 0, 0]))
    assert arr2.tolist() == [1, 0, 0, 0, 2, 0, 0, 0]


def test_fromfile_ragged_short_read():
    # if the file is shorter than requested AND the amount actually read
    # is not a whole number of items, CPython raises ValueError and
    # leaves the array untouched -- it must not raise EOFError, and it
    # must not append the partial/misaligned data first.
    testdir = os.curdir
    while not os.path.exists(os.path.join(testdir, "testdata")) and os.path.exists(os.pardir):
        testdir = os.path.join(testdir, os.pardir)
    testdata = os.path.join(testdir, "testdata")

    path = os.path.join(testdata, "ragged_short_read")
    with open(path, "wb") as f:
        f.write(bytes(range(25)))  # 25 bytes: not a multiple of 4

    arr = array.array('i')
    with open(path, "rb") as f:
        try:
            arr.fromfile(f, 7)  # asks for 28 bytes, gets 25
            assert False, "expected ValueError"
        except ValueError:
            pass
    assert len(arr) == 0

    # sanity check: a short read that IS a whole number of items still
    # raises EOFError and keeps the complete items that were read
    path2 = os.path.join(testdata, "aligned_short_read")
    with open(path2, "wb") as f:
        f.write(bytes(range(24)))  # 24 bytes: exactly 6 items

    arr2 = array.array('i')
    with open(path2, "rb") as f:
        try:
            arr2.fromfile(f, 7)
            assert False, "expected EOFError"
        except EOFError:
            pass
    assert len(arr2) == 6


def test_setslice_typecode_mismatch():
    # slice assignment across mismatched typecodes must raise TypeError,
    # just like __add__/__iadd__ already do, instead of silently
    # converting through lists and corrupting the values.
    a = array.array('i', [1, 2, 3, 4])
    b = array.array('d', [9.0, 8.0])
    try:
        a[0:2] = b
        assert False, "expected TypeError"
    except TypeError:
        pass
    assert a.tolist() == [1, 2, 3, 4]

    # sanity check: matching typecodes still work
    c = array.array('i', [1, 2, 3, 4])
    d = array.array('i', [9, 8])
    c[0:2] = d
    assert c.tolist() == [9, 8, 3, 4]


def test_extend_typecode_mismatch():
    # extending an array with another array of a *different* typecode must
    # raise TypeError, just like __add__/__iadd__/__setslice__ already do.
    # 'i' and 'h' both map to the same underlying element type internally,
    # so this exercises the fast memcpy-based array-to-array path in
    # extend() specifically (not just the generic iterable path).
    a = array.array('i', [100, 200, 300])
    b = array.array('h', [1, 2, 3])
    try:
        a.extend(b)
        assert False, "expected TypeError"
    except TypeError:
        pass
    assert a.tolist() == [100, 200, 300]

    # sanity check: matching typecodes still work and go through the fast path
    c = array.array('i', [1, 2, 3])
    d = array.array('i', [4, 5, 6])
    c.extend(d)
    assert c.tolist() == [1, 2, 3, 4, 5, 6]

    # sanity check: fromlist() delegates to extend() and must behave the same
    e = array.array('d', [1.0, 2.0])
    f = array.array('f', [3.0, 4.0])
    try:
        e.fromlist(f)
        assert False, "expected TypeError"
    except TypeError:
        pass
    assert e.tolist() == [1.0, 2.0]


def test_extend_overflow_no_corruption():
    # if a later element in the list is out of range for the typecode,
    # extend() must leave exactly the elements that were successfully
    # converted before the failure -- not a corrupted trailing element from
    # the underlying buffer having already been grown to its final size
    # before validation reached that far. (Note: real CPython's fromlist()
    # is stricter still -- it validates the whole list up front and leaves
    # the array completely untouched on any failure. Shedskin's fromlist()
    # is implemented directly in terms of extend(), so it shares extend()'s
    # partial-commit behavior rather than that atomic one; this test covers
    # the corruption bug, not that CPython/shedskin discrepancy.)
    arr2 = array.array('B')
    try:
        arr2.extend([1, 2, 300])
        assert False, "expected OverflowError"
    except OverflowError:
        pass
    assert arr2.tolist() == [1, 2]

    # a failure on the very first element must leave the array untouched
    arr3 = array.array('B')
    try:
        arr3.extend([300])
        assert False, "expected OverflowError"
    except OverflowError:
        pass
    assert arr3.tolist() == []

    # extending onto a non-empty array: existing elements must survive,
    # and no corrupted tail should appear after the failure point
    arr4 = array.array('B', [9, 8])
    try:
        arr4.extend([1, 2, 300])
        assert False, "expected OverflowError"
    except OverflowError:
        pass
    assert arr4.tolist() == [9, 8, 1, 2]


def test_all():
    test_typecodes()
    test_list()
    test_bytes()
    test_file()
    test_sequence_immutable()
    test_sequence_mutable()
    test_codes()
    test_mul_nonpositive()
    test_insert_out_of_range()
    test_repr_empty()
    test_double_typecode_roundtrip()
    test_bytes_initializer_itemsize_gt_1()
    test_index_not_found_message()
    test_frombytes_validates_against_itemsize()
    test_pop_empty_message()
    test_remove_not_found_message()
    test_extend_bytes_is_elementwise()
    test_fromfile_ragged_short_read()
    test_setslice_typecode_mismatch()
    test_extend_typecode_mismatch()
    test_extend_overflow_no_corruption()


if __name__ == '__main__':
    test_all()
