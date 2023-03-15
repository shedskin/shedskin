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
    # print(map[0])
    map[-1] = ord("Z")
    # print(map[-1])
    # print(map[4 : -PAGESIZE + 7])
    # print("%r" % map[:15])
    map[4:7] = b"foo"
    map[PAGESIZE - 3 :] = b"xyz"
    # print(map[PAGESIZE - 3 :])

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


def test_ctx_mgr():
    with open(TESTFILE_IN, "rb") as f:
        with mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ) as mm:
            assert f.read(8) == mm.read(8)




def test_all():
    if sys.platform != 'win32':
        test_anonymous()
        test_basic()
        test_readonly()
        test_rfind()
        test_tougher_find()
        test_ctx_mgr()

if __name__ == '__main__':
    test_all()


