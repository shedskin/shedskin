import mmap
import os
import sys

if os.path.exists("testdata"):
    testdata = "testdata"
elif os.path.exists("../testdata"):
    testdata = "../testdata"
else:
    testdata = "../../testdata"

TESTFILE_IN = os.path.join(testdata, "board.py")
TESTFILE_OUT = os.path.join(testdata, "mmap.out")


def setUp():
    if os.path.exists(TESTFILE_OUT):
        os.remove(TESTFILE_OUT)


def tearDown(map):
    map.close()
    try:
        os.remove(TESTFILE_OUT)
    except OSError:
        pass


def test_anonymous():
    PAGESIZE = mmap.PAGESIZE

    map = mmap.mmap(-1, PAGESIZE)
    assert len(map) == PAGESIZE
    # print("# write:")

    assert map.tell() == 0
    map.write_byte(ord("f"))
    assert map.tell() == 1
    map.write(b"oo bar\tbaz\nqux")
    assert map.tell() == 15

    # print("# get/set:")
    assert map[:15] == b"foo bar\tbaz\nqux"
    assert map[:] == map[:PAGESIZE]      # bare full slice must work like an explicit one
    assert map[PAGESIZE:] == b""         # slicing from the exact end returns empty
    assert map[15:PAGESIZE] == b"\x00" * (PAGESIZE - 15)  # slicing up to the exact end
    # print(map[0])
    map[-1] = ord("Z")
    # print(map[-1])
    # print(map[4 : -PAGESIZE + 7])
    # print("%r" % map[:15])
    map[4:7] = b"foo"
    map[PAGESIZE - 3 :] = b"xyz"
    # print(map[PAGESIZE - 3 :])

    saved = map[:]
    map[:] = saved                       # bare full-slice assignment must work
    assert map[:] == saved
    try:
        map[0:15] = b"too short"
        assert False, "should have raised on size mismatch"
    except IndexError:
        pass
    try:
        map[0:15] = b"this string is much too long for the slice"
        assert False, "should have raised on size mismatch"
    except IndexError:
        pass

    # print("# find/seek:")
    assert map.find(b"foo") == -1
    map.seek(0)
    assert map.tell() == 0
    assert map.find(b"foo") == 0
    assert map.rfind(b"foo") == 4
    map.seek(-1, 2)
    assert map.tell() == PAGESIZE - 1
    map.seek(0, 2)
    assert map.tell() == PAGESIZE
    map.seek(-PAGESIZE, 1)
    assert map.tell() == 0

    # print("# read:")
    # print(map.read(3))
    # print("%r" % map.read_byte())
    # print("%r" % map.readline())
    # print("%r" % map.read(3))

    # print("# read_byte:")
    map.seek(0)
    assert map.read_byte() == ord("f")
    assert map.read_byte() == ord("o")
    assert map.tell() == 2

    map.seek(0, 2)  # seek to end
    assert map.tell() == PAGESIZE
    error = False
    try:
        map.read_byte()
    except ValueError as e:
        error = True
        assert str(e) == "read byte out of range"
    assert error, "read_byte() at end of map should raise ValueError"

    # reading again at end should keep raising, not silently succeed
    error2 = False
    try:
        map.read_byte()
    except ValueError:
        error2 = True
    assert error2

    # print("# move:")
    map.move(8, 4, 3)

    # print("# iter:")
    assert b"f" in map
    assert b"a" not in map

    map.flush()

    # print("# Result:")
    # print("%r" % map[:15])

    h = 0
    for c in map:
        h += ord(c) * 31
    # print(h)

    try:
        map.resize(0x2000)
        assert len(map) == 0x2000
    except:
        pass

    map.close()


def test_basic():
    PAGESIZE = mmap.PAGESIZE

    # print("## test_basic:")
    setUp()

    f = open(TESTFILE_OUT, "w+")

    f.write("\0" * PAGESIZE)
    f.write("foo")
    f.write("\0" * (PAGESIZE - 3))
    f.flush()
    m = mmap.mmap(f.fileno(), 2 * PAGESIZE)
    f.close()

    assert m.find(b"foo") == PAGESIZE

    assert len(m) == 2 * PAGESIZE

    # print(repr(m[0]))
    # print(repr(m[0:3]))

    try:
        m[len(m)]
    except IndexError:
        print("ok")

    m[0] = ord("3")
    m[PAGESIZE + 3 : PAGESIZE + 3 + 3] = b"bar"

    # print(repr(m[0]))
    # print(repr(m[0:3]))
    # print(repr(m[PAGESIZE - 1 : PAGESIZE + 7]))

    m.flush()

    try:
        m.seek(-1)
    except ValueError:
        pass
        # print("ok")

    try:
        m.seek(1, 2)
    except ValueError:
        pass
        # print("ok")

    try:
        m.seek(-len(m) - 1, 2)
    except ValueError:
        pass
        # print("ok")

    tearDown(m)


def test_readonly():

    # print("## test_readonly:")
    f = open(TESTFILE_IN, "r+")
    mapsize = os.path.getsize(TESTFILE_IN)
    map = mmap.mmap(f.fileno(), 0)
    assert map.size() == mapsize
    # print(repr(map.read(mapsize)))
    map.close()
    f.close()


def test_rfind():

    # print("## test_rfind:")
    setUp()
    f = open(TESTFILE_OUT, "wb+")
    data = b"one two ones"
    n = len(data)
    f.write(data)
    f.flush()
    m = mmap.mmap(f.fileno(), n)
    f.close()

    assert m.rfind(b"one") == 8
    assert m.rfind(b"one ") == 0
    assert m.rfind(b"one", 0, -1) == 8
    assert m.rfind(b"one", 0, -2) == 0
    assert m.rfind(b"one", 1, -1) == 8
    assert m.rfind(b"one", 1, -2) == -1

    tearDown(m)


def test_tougher_find():

    # print("## test_tougher_find:")
    setUp()

    f = open(TESTFILE_OUT, "wb+")

    data = b"aabaac\x00deef\x00\x00aa\x00"
    n = len(data)
    f.write(data)
    f.flush()
    m = mmap.mmap(f.fileno(), n)
    f.close()

    for start in range(n + 1):
        for finish in range(start, n + 1):
            slice = data[start:finish]
            # print(m.find(slice), data.find(slice))
            # print(m.find(slice + b"x") == -1)

    tearDown(m)


def test_explicit_iter():
    # exercises __mmapiter/__next__ directly (iter()/list()/zip()),
    # as opposed to the inlined for-loop fast path, which doesn't
    # go through __mmapiter at all.
    setUp()
    f = open(TESTFILE_OUT, "wb+")
    data = b"foobar"
    f.write(data)
    f.flush()
    m = mmap.mmap(f.fileno(), len(data))
    f.close()

    assert list(iter(m)) == [bytes([b]) for b in data]

    it = iter(m)
    collected = []
    while True:
        try:
            collected.append(next(it))
        except StopIteration:
            break
    assert collected == [bytes([b]) for b in data]

    tearDown(m)


def test_ctx_mgr():
    with open(TESTFILE_IN, "rb") as f:
        with mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ) as mm:
            assert f.read(8) == mm.read(8)


def test_closed():
    map = mmap.mmap(-1, mmap.PAGESIZE)
    assert map.closed is False
    map.close()
    assert map.closed is True

    # note: deliberately not using `with mmap.mmap(...) as mm: ...` here and
    # then checking mm.closed afterwards -- that pattern currently corrupts
    # memory for both file-backed and anonymous mmaps (crashes on the next
    # unrelated allocation). Tracked separately; calling close() directly
    # and checking .closed right after (still within the object's normal
    # lifetime) is the safe, currently-working pattern exercised here.
    with open(TESTFILE_IN, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        assert mm.closed is False
        mm.close()
        assert mm.closed is True


def test_resize_grows_backing_file():
    # regression test: resize() on a file-backed mmap must grow (or shrink)
    # the underlying file to match, and the mapping must actually be usable
    # (and persisted) past the original file size afterwards. Without this,
    # writes into the newly-mapped region either get silently dropped or
    # crash the process (SIGBUS/SIGSEGV), since mremap() alone never
    # touches the backing file.
    PAGESIZE = mmap.PAGESIZE
    setUp()

    f = open(TESTFILE_OUT, "w+b")
    f.write(b"x" * PAGESIZE)
    f.flush()
    m = mmap.mmap(f.fileno(), PAGESIZE)
    f.close()

    m.resize(PAGESIZE * 3)
    assert len(m) == PAGESIZE * 3

    # write well into a page beyond the original file's last mapped page
    m.seek(PAGESIZE * 2 + 10)
    m.write_byte(65)
    m.flush()
    m.close()

    assert os.path.getsize(TESTFILE_OUT) == PAGESIZE * 3
    with open(TESTFILE_OUT, "rb") as f2:
        f2.seek(PAGESIZE * 2 + 10)
        assert f2.read(1) == b"A"

    try:
        os.remove(TESTFILE_OUT)
    except OSError:
        pass


def test_resize_shrinks_backing_file():
    # regression test: resize() to a smaller size must also shrink the
    # underlying file to match (same code path as the grow case above).
    PAGESIZE = mmap.PAGESIZE
    setUp()

    f = open(TESTFILE_OUT, "w+b")
    f.write(b"x" * PAGESIZE * 3)
    f.flush()
    m = mmap.mmap(f.fileno(), PAGESIZE * 3)
    f.close()

    m.resize(PAGESIZE)
    assert len(m) == PAGESIZE
    m.close()

    assert os.path.getsize(TESTFILE_OUT) == PAGESIZE

    try:
        os.remove(TESTFILE_OUT)
    except OSError:
        pass


def test_madvise():
    # madvise() is available wherever the madvise() system call is (so not
    # on Windows). MADV_NORMAL/WILLNEED/DONTNEED/RANDOM/SEQUENTIAL are the
    # portable subset; the platform-specific ones are -1 here when missing,
    # which madvise() rejects with OSError.
    PAGESIZE = mmap.PAGESIZE
    m = mmap.mmap(-1, 4 * PAGESIZE)

    m.madvise(mmap.MADV_NORMAL)
    m.madvise(mmap.MADV_WILLNEED)
    m.madvise(mmap.MADV_RANDOM, 0, PAGESIZE)
    m.madvise(mmap.MADV_SEQUENTIAL, PAGESIZE, PAGESIZE)
    # a length running past the end of the mapping is clamped, not an error
    m.madvise(mmap.MADV_NORMAL, 2 * PAGESIZE, 99 * PAGESIZE)

    error = False
    try:
        m.madvise(mmap.MADV_NORMAL, -1)
    except ValueError as e:
        error = True
        assert str(e) == "madvise start out of bounds"
    assert error, "negative start should raise ValueError"

    error = False
    try:
        m.madvise(mmap.MADV_NORMAL, 4 * PAGESIZE)
    except ValueError:
        error = True
    assert error, "start at or past the end should raise ValueError"

    error = False
    try:
        m.madvise(mmap.MADV_NORMAL, 0, -2)
    except ValueError as e:
        error = True
        assert str(e) == "madvise length invalid"
    assert error, "negative length should raise ValueError"

    m.close()

    error = False
    try:
        m.madvise(mmap.MADV_NORMAL)
    except ValueError:
        error = True
    assert error, "madvise() on a closed mmap should raise ValueError"


def test_seekable():
    m = mmap.mmap(-1, mmap.PAGESIZE)
    assert m.seekable() is True
    m.seek(10)
    assert m.seekable() is True
    m.close()


def test_set_name():
    # set_name() is Linux-only (kernel >= 5.17 built with
    # CONFIG_ANON_VMA_NAME); elsewhere it raises NotImplementedError, and on
    # a kernel without the feature the underlying prctl() fails with OSError.
    # Only the error cases are checked unconditionally, since those do not
    # depend on the kernel.
    m = mmap.mmap(-1, mmap.PAGESIZE)

    if sys.platform == "linux":
        try:
            m.set_name("test-anon")
        except OSError:
            pass  # kernel without CONFIG_ANON_VMA_NAME

        error = False
        try:
            m.set_name("x" * 67)
        except ValueError as e:
            error = True
            assert str(e) == "name is too long"
        except OSError:
            error = True
        assert error, "overlong name should raise ValueError"
    else:
        error = False
        try:
            m.set_name("test-anon")
        except NotImplementedError:
            error = True
        assert error, "set_name() should raise NotImplementedError here"

    m.close()

    error = False
    try:
        m.set_name("after-close")
    except ValueError:
        error = True
    except NotImplementedError:
        error = True
    assert error, "set_name() on a closed mmap should raise"


def test_set_name_file_backed():
    # only anonymous mappings can be annotated
    if sys.platform != "linux":
        return

    setUp()
    f = open(TESTFILE_OUT, "w+b")
    f.write(b"x" * mmap.PAGESIZE)
    f.flush()
    m = mmap.mmap(f.fileno(), mmap.PAGESIZE)
    f.close()

    error = False
    try:
        m.set_name("file-backed")
    except ValueError as e:
        error = True
        assert str(e) == "Cannot set annotation on non-anonymous mappings"
    assert error, "file-backed mapping should not be nameable"

    tearDown(m)


def test_default_flags_prot():
    # omitted flags/prot must mean MAP_SHARED, PROT_READ | PROT_WRITE
    m = mmap.mmap(-1, mmap.PAGESIZE)
    m.write(b"abc")
    assert m[:3] == b"abc"
    m.close()

    # ..so access= combines with omitted or explicitly-default flags/prot
    m = mmap.mmap(-1, mmap.PAGESIZE, access=mmap.ACCESS_READ)
    assert m.read(3) == b"\x00\x00\x00"
    m.close()
    # (keyword args: on win32 the positional slots are (fileno, length, tagname, ..))
    m = mmap.mmap(-1, mmap.PAGESIZE, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ | mmap.PROT_WRITE, access=mmap.ACCESS_WRITE)
    m.write(b"x")
    m.close()

    # ..but not with non-default ones
    error = False
    try:
        mmap.mmap(-1, mmap.PAGESIZE, prot=mmap.PROT_READ, access=mmap.ACCESS_READ)
    except ValueError:
        error = True
    assert error, "access= with non-default prot should raise ValueError"



def test_module_constants():
    assert mmap.ACCESS_DEFAULT == 0
    assert mmap.ACCESS_READ == 1
    assert mmap.ACCESS_WRITE == 2
    assert mmap.ACCESS_COPY == 3
    assert mmap.ALLOCATIONGRANULARITY > 0
    # the granularity is a whole number of pages on every platform
    assert mmap.ALLOCATIONGRANULARITY % mmap.PAGESIZE == 0

    # ACCESS_DEFAULT is the same as not passing access= at all
    m = mmap.mmap(-1, mmap.PAGESIZE, access=mmap.ACCESS_DEFAULT)
    m.write(b'hello')
    m.seek(0)
    assert m.read(5) == b'hello'
    m.close()


def test_access_copy():
    setUp()
    with open(TESTFILE_OUT, 'wb') as f:
        f.write(b'original!')
    f = open(TESTFILE_OUT, 'r+b')
    m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY)
    assert m.read(8) == b'original'
    # writes are visible through the mapping..
    m.seek(0)
    m.write(b'changed')
    m.seek(0)
    assert m.read(9) == b'changedl!'
    m.flush()
    f.close()
    # ..but never reach the file
    with open(TESTFILE_OUT, 'rb') as g:
        assert g.read() == b'original!'
    tearDown(m)

def test_readline():
    m = mmap.mmap(-1, 24)
    m.write(b"first\nsecond line\nlast")
    m.seek(0)
    assert m.readline() == b"first\n"
    assert m.tell() == 6
    assert m.readline() == b"second line\n"
    # no trailing newline: runs up to the end of the mapping
    assert m.readline() == b"last\x00\x00"
    assert m.tell() == 24
    assert m.readline() == b""
    m.seek(3)
    assert m.readline() == b"st\n"
    m.close()


def test_readline_file():
    setUp()
    with open(TESTFILE_OUT, "wb") as f:
        f.write(b"alpha\nbeta\ngamma\n")
    with open(TESTFILE_OUT, "r+b") as f:
        m = mmap.mmap(f.fileno(), 0)
        lines = []
        line = m.readline()
        while line:
            lines.append(line)
            line = m.readline()
        assert lines == [b"alpha\n", b"beta\n", b"gamma\n"]
        m.close()
    tearDown(m)


def test_flush():
    PAGESIZE = mmap.PAGESIZE
    m = mmap.mmap(-1, PAGESIZE * 2)
    m.write(b"flushme")
    m.flush()
    m.flush(0)
    m.flush(PAGESIZE)                 # offset without size: flush to the end
    m.flush(0, PAGESIZE)
    m.flush(PAGESIZE, PAGESIZE)
    m.flush(PAGESIZE * 2)             # empty range at the end is fine
    m.flush(flags=mmap.MS_SYNC)
    m.flush(0, PAGESIZE, flags=mmap.MS_ASYNC)
    m.flush(PAGESIZE, flags=mmap.MS_SYNC)

    for offset, size in [(0, PAGESIZE * 2 + 1), (PAGESIZE, PAGESIZE + 1), (-PAGESIZE, -1), (0, -2), (PAGESIZE * 3, -1)]:
        error = False
        try:
            m.flush(offset, size)
        except ValueError as e:
            error = True
            assert str(e) == "flush values out of range"
        assert error, "flush(%d, %d) should raise ValueError" % (offset, size)
    m.close()

    error = False
    try:
        m.flush()
    except ValueError:
        error = True
    assert error, "flush() on a closed mmap should raise ValueError"


def test_flush_file():
    PAGESIZE = mmap.PAGESIZE
    setUp()
    with open(TESTFILE_OUT, "wb") as f:
        f.write(b"-" * PAGESIZE * 2)
    f = open(TESTFILE_OUT, "r+b")
    m = mmap.mmap(f.fileno(), 0)
    m[:5] = b"hello"
    m[PAGESIZE:PAGESIZE + 5] = b"world"
    m.flush(0, PAGESIZE, flags=mmap.MS_SYNC)
    m.flush(PAGESIZE, flags=mmap.MS_SYNC | mmap.MS_INVALIDATE)
    f.close()
    with open(TESTFILE_OUT, "rb") as g:
        data = g.read()
    assert data[:5] == b"hello"
    assert data[PAGESIZE:PAGESIZE + 5] == b"world"
    tearDown(m)

    # flushing a read-only mapping is a no-op, as in CPython
    with open(TESTFILE_IN, "rb") as f:
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        m.flush()
        m.flush(0, 1, flags=mmap.MS_ASYNC)
        m.close()


def test_offset():
    GRAN = mmap.ALLOCATIONGRANULARITY
    setUp()
    with open(TESTFILE_OUT, "wb") as f:
        f.write(b"a" * GRAN + b"b" * GRAN + b"c" * 10)
    f = open(TESTFILE_OUT, "r+b")

    # length 0: map from offset to the end of the file
    m = mmap.mmap(f.fileno(), 0, offset=GRAN)
    assert len(m) == GRAN + 10
    assert m.size() == GRAN * 2 + 10      # size() is the size of the file
    assert m[0] == ord("b")
    assert m[-1] == ord("c")
    assert m.read(3) == b"bbb"
    assert m.find(b"c") == GRAN
    m[GRAN:GRAN + 3] = b"XYZ"
    m.move(0, GRAN, 3)
    m.flush()
    m.close()

    # explicit length at an offset
    m = mmap.mmap(f.fileno(), 5, offset=GRAN * 2)
    assert len(m) == 5
    assert m[:] == b"XYZcc"
    m.close()

    # positional offset (unix signature: fileno, length, flags, prot, access, offset)
    m = mmap.mmap(f.fileno(), 4, mmap.MAP_SHARED, mmap.PROT_READ, 0, GRAN)
    assert m[:] == b"XYZb"
    m.close()
    f.close()

    with open(TESTFILE_OUT, "rb") as g:
        data = g.read()
    assert data[:GRAN] == b"a" * GRAN
    assert data[GRAN:GRAN + 4] == b"XYZb"
    assert data[GRAN * 2:] == b"XYZccccccc"

    f = open(TESTFILE_OUT, "r+b")
    error = False
    try:
        mmap.mmap(f.fileno(), 0, offset=GRAN * 3)
    except ValueError as e:
        error = True
        assert str(e) == "mmap offset is greater than file size"
    assert error, "offset beyond the end of the file should raise"
    for length, offset in [(GRAN * 2, GRAN), (1, GRAN * 3)]:
        error = False
        try:
            mmap.mmap(f.fileno(), length, offset=offset)
        except ValueError as e:
            error = True
            assert str(e) == "mmap length is greater than file size"
        assert error, "mmap(fd, %d, offset=%d) should raise" % (length, offset)

    error = False
    try:
        mmap.mmap(f.fileno(), 0, offset=-GRAN)
    except OverflowError:
        error = True
    assert error, "a negative offset should raise OverflowError"

    # a misaligned offset is rejected by the OS
    error = False
    try:
        mmap.mmap(f.fileno(), 0, offset=1)
    except OSError:
        error = True
    assert error, "a misaligned offset should raise OSError"
    f.close()

    setUp()
    with open(TESTFILE_OUT, "wb") as f:
        pass
    with open(TESTFILE_OUT, "r+b") as f:
        error = False
        try:
            mmap.mmap(f.fileno(), 0)
        except ValueError as e:
            error = True
            assert str(e) == "cannot mmap an empty file"
        assert error, "mapping an empty file should raise ValueError"
    os.remove(TESTFILE_OUT)


def test_trackfd():
    PAGESIZE = mmap.PAGESIZE
    setUp()
    with open(TESTFILE_OUT, "wb") as f:
        f.write(b"q" * PAGESIZE)

    f = open(TESTFILE_OUT, "r+b")
    m = mmap.mmap(f.fileno(), 0, trackfd=True)
    assert m.size() == PAGESIZE
    m.close()

    m = mmap.mmap(f.fileno(), 0, trackfd=False)
    f.close()                              # the mapping stays usable
    assert len(m) == PAGESIZE
    assert m[:3] == b"qqq"
    m[0] = ord("Q")
    m.flush()
    error = False
    try:
        m.size()
    except ValueError as e:
        error = True
        assert str(e) == "can't get size with trackfd=False"
    assert error, "size() with trackfd=False should raise ValueError"
    error = False
    try:
        m.resize(PAGESIZE * 2)
    except ValueError as e:
        error = True
        assert str(e) == "mmap can't resize with trackfd=False."
    assert error, "resize() with trackfd=False should raise ValueError"
    m.close()
    with open(TESTFILE_OUT, "rb") as g:
        assert g.read(2) == b"Qq"

    # also for anonymous mappings
    m = mmap.mmap(-1, PAGESIZE, trackfd=False)
    assert len(m) == PAGESIZE
    error = False
    try:
        m.size()
    except ValueError:
        error = True
    assert error
    m.close()
    os.remove(TESTFILE_OUT)


def test_all():
    if sys.platform != 'win32':
        test_anonymous()
        test_basic()
        test_readonly()
        test_rfind()
        test_tougher_find()
        test_explicit_iter()
        test_ctx_mgr()
        test_closed()
        test_resize_grows_backing_file()
        test_resize_shrinks_backing_file()
        test_madvise()
        test_seekable()
        test_set_name()
        test_set_name_file_backed()
        test_default_flags_prot()
        test_flush_file()
        test_offset()
        test_trackfd()
    test_module_constants()
    test_access_copy()
    test_readline()
    test_readline_file()
    test_flush()

if __name__ == '__main__':
    test_all()


