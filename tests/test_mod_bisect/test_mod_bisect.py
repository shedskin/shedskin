import array
import bisect
import collections


def test_bisect():
    xs = [1, 2, 3, 4, 5, 6, 6, 7]
    n = 4
    assert bisect.bisect_left(xs, n) == 3
    assert bisect.bisect_left(xs, n, 0) == 3
    assert bisect.bisect_left(xs, n, 0, len(xs)) == 3
    assert bisect.bisect_right(xs, n) == 4
    assert bisect.bisect(xs, n) == 4

    bisect.insort_left(xs, n)
    assert xs == [1, 2, 3, 4, 4, 5, 6, 6, 7]

    bisect.insort_right(xs, n)
    assert xs == [1, 2, 3, 4, 4, 4, 5, 6, 6, 7]

    bisect.insort(xs, n)
    assert xs == [1, 2, 3, 4, 4, 4, 4, 5, 6, 6, 7]


class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def val(self):
        return (self.x, self.y)

    def __repr__(self):
        return "Pair(%s, %s)" % (self.x, self.y)

    def __lt__(self, other):
        return self.x + self.y < other.x + other.y

    def __eq__(self, other):
        return self.x + self.y == other.x + other.y


def test_bisect_insort():
    pairs = [[18, 6], [28, 5], [35, 26], [31, 28], [3, 3], [32, 37], [11, 17], [28, 29]]
    items = []
    for pair in pairs:
        bisect.insort(items, Pair(pair[0], pair[1]))

    assert items[0].val == (3,3)
    assert items[-1].val == (32, 37)
    assert [i.val for i in items] == [(3, 3), (18, 6), (11, 17), (28, 5), (28, 29), (31, 28), (35, 26), (32, 37)]


idx = {
    1: 'z',
    2: 'y',
    3: 'x',
    4: 'w',
    5: 'v',
}

def test_key():
    l = [1,2,3,4,5]
    l.sort(key=lambda a: -a)
    assert l == [5,4,3,2,1]

    assert bisect.bisect(l, -4, key=lambda a: -a) == 2
    assert bisect.bisect_right(l, -4, key=lambda a: -a) == 2
    assert bisect.bisect_left(l, -4, key=lambda a: -a) == 1

    bisect.insort_right(l, 2, key=lambda a: -a)
    assert l == [5,4,3,2,2,1]

    l = [1,2,3,4,5]
    l.sort(key=lambda a: idx[a])
    assert l == [5,4,3,2,1]

    assert bisect.bisect(l, 'w', key=lambda a: idx[a]) == 2

    # regression test: key's return type (str) differs from the list's
    # element type (int); bisect_left previously mis-typed its 'x'
    # parameter as the element type instead of the key's return type,
    # which failed to compile for exactly this case
    assert bisect.bisect_left(l, 'w', key=lambda a: idx[a]) == 1
    assert bisect.bisect_right(l, 'w', key=lambda a: idx[a]) == 2


def negate(a):
    return -a


def test_bounds():
    xs = [1, 2, 3, 4, 5]

    # negative 'lo' is always rejected
    ok = False
    try:
        bisect.bisect_right(xs, 3, -1, 5)
    except ValueError:
        ok = True
    assert ok

    ok = False
    try:
        bisect.insort_right(xs, 3, -1, 5)
    except ValueError:
        ok = True
    assert ok

    # negative 'hi' is NOT an error: it's just used as a bound, so
    # 'lo < hi' is immediately false and the search range is empty
    assert bisect.bisect_right(xs, 3, 0, -100) == 0
    assert bisect.bisect_left(xs, 3, 0, -100) == 0
    assert bisect.bisect_right(xs, 3, 0, -2) == 0

    # ..except for -1, which is the in-band 'hi is None' sentinel in
    # CPython's _bisect, so it means len(a) there. (the pure python
    # bisect.py fallback disagrees, but _bisect is what users get)
    assert bisect.bisect_right(xs, 3, 0, -1) == 3
    assert bisect.bisect_left(xs, 3, 0, -1) == 2
    assert bisect.bisect(xs, 3, 0, -1) == 3

    ks = [5, 4, 3, 2, 1]
    assert bisect.bisect_right(ks, -3, 0, -1, key=negate) == 3
    assert bisect.bisect_left(ks, -3, 0, -1, key=negate) == 2

    ys = [1, 2, 3, 4, 5]
    bisect.insort_right(ys, 3, 0, -1)
    assert ys == [1, 2, 3, 3, 4, 5]


def test_hi_out_of_range():
    xs = [1, 2, 3, 4, 5]

    # 'hi' beyond len(a) is not clamped: CPython raises IndexError as
    # soon as the search probes an index that is out of range
    ok = False
    try:
        bisect.bisect_right(xs, 3, 0, 100)
    except IndexError:
        ok = True
    assert ok

    ok = False
    try:
        bisect.bisect_left(xs, 3, 0, 100)
    except IndexError:
        ok = True
    assert ok

    ok = False
    try:
        bisect.bisect_right([5, 4, 3, 2, 1], -3, 0, 100, key=negate)
    except IndexError:
        ok = True
    assert ok

    ok = False
    try:
        bisect.insort_right(xs, 3, 0, 100)
    except IndexError:
        ok = True
    assert ok
    assert xs == [1, 2, 3, 4, 5]

    ok = False
    try:
        bisect.insort_left(xs, 3, 0, 100)
    except IndexError:
        ok = True
    assert ok

    # ..but only if it actually probes out of range: here the very first
    # probe moves 'hi' back into the list, so no error is raised
    assert bisect.bisect_right(xs, 1, 0, 6) == 1
    assert bisect.bisect_left(xs, 1, 0, 6) == 0


def test_insort_left_key():
    # insort_left with a key that inverts the order
    l = [5, 4, 3, 2, 1]
    bisect.insort_left(l, 3, key=lambda a: -a)
    assert l == [5, 4, 3, 3, 2, 1]

    # left vs right placement among equal keys: the key only looks at
    # 'x', so the inserted pair must land before (left) or after (right)
    # the existing pairs with the same 'x'
    ps = [Pair(1, 10), Pair(2, 20), Pair(3, 30)]
    bisect.insort_left(ps, Pair(2, 99), key=lambda p: p.x)
    assert [p.val for p in ps] == [(1, 10), (2, 99), (2, 20), (3, 30)]
    bisect.insort_right(ps, Pair(2, 77), key=lambda p: p.x)
    assert [p.val for p in ps] == [(1, 10), (2, 99), (2, 20), (2, 77), (3, 30)]
    bisect.insort_left(ps, Pair(0, 0), key=lambda p: p.x)
    bisect.insort_left(ps, Pair(4, 0), key=lambda p: p.x)
    assert [p.x for p in ps] == [0, 1, 2, 2, 2, 3, 4]

    # key returns a different type (str) than the list's element type (int)
    l = [5, 4, 3, 2, 1]
    bisect.insort_left(l, 3, key=lambda a: idx[a])
    assert l == [5, 4, 3, 3, 2, 1]
    bisect.insort_left(l, 1, key=lambda a: idx[a])
    assert l == [5, 4, 3, 3, 2, 1, 1]

    # named key function, with lo/hi
    ks = [5, 4, 3, 2, 1]
    bisect.insort_left(ks, 3, 0, -1, key=negate)
    assert ks == [5, 4, 3, 3, 2, 1]
    ks = [5, 4, 3, 2, 1]
    bisect.insort_left(ks, 3, 3, 5, key=negate)
    assert ks == [5, 4, 3, 3, 2, 1]
    ks = [5, 4, 3, 2, 1]
    bisect.insort_left(ks, 9, 0, 2, key=negate)
    assert ks == [9, 5, 4, 3, 2, 1]
    ks = [5, 4, 3, 2, 1]
    bisect.insort_left(ks, 0, lo=2, key=negate)
    assert ks == [5, 4, 3, 2, 1, 0]


def test_hi_keyword():
    # hi by keyword, without lo, must not be passed as lo
    a = [1, 2, 3, 4, 5, 6]
    assert bisect.bisect(a, 4, hi=2) == 2
    assert bisect.bisect_left(a, 4, hi=2) == 2
    assert bisect.bisect_right(a, 4, hi=2) == 2
    assert bisect.bisect_left(a, 4, hi=5, lo=1) == 3
    d = [6, 5, 4, 3, 2, 1]
    assert bisect.bisect(d, -2, key=negate) == 5
    assert bisect.bisect(d, -2, hi=3, key=negate) == 3
    l = [1, 2, 3, 4]
    bisect.insort(l, 4, hi=2)
    assert l == [1, 2, 4, 3, 4]
    l = [1, 2, 3, 4]
    bisect.insort_left(l, 4, hi=2)
    assert l == [1, 2, 4, 3, 4]
    l = [1, 2, 3, 4]
    bisect.insort_right(l, 4, hi=2, key=lambda x: x)
    assert l == [1, 2, 4, 3, 4]


class Seq:
    # only __getitem__ and __len__, like a minimal CPython sequence
    def __init__(self, n):
        self.n = n
        self.inserted = []

    def __getitem__(self, i):
        assert 0 <= i < self.n
        return i * 10

    def __len__(self):
        return self.n

    def insert(self, i, x):
        self.inserted.append((i, x))


class NoLen:
    # without __len__, CPython only needs it when hi is omitted
    def __getitem__(self, i):
        return i * 10


def test_sequences():
    # tuple
    t = (1, 2, 2, 3)
    assert bisect.bisect_left(t, 2) == 1
    assert bisect.bisect_right(t, 2) == 3
    assert bisect.bisect(t, 2) == 3
    assert bisect.bisect_left(t, 2, 2) == 2
    assert bisect.bisect_right(t, 2, 0, 2) == 2
    assert bisect.bisect(t, 0, hi=2) == 0
    assert bisect.bisect_left(t, 4, key=lambda v: v * 2) == 1
    ts = ('a', 'bb', 'ccc')
    assert bisect.bisect_left(ts, 2, key=len) == 1
    assert bisect.bisect_right(ts, 2, key=len) == 2
    try:
        bisect.bisect(t, 2, 0, 10)
        assert False
    except IndexError as e:
        assert str(e) == 'tuple index out of range'
    try:
        bisect.bisect(t, 2, -1)
        assert False
    except ValueError as e:
        assert str(e) == 'lo must be non-negative'

    # str, bytes
    assert bisect.bisect_left('abcd', 'c') == 2
    assert bisect.bisect_right('aabb', 'a') == 2
    assert bisect.bisect_left(b'abcd', ord('c')) == 2
    assert bisect.bisect_right(bytearray(b'aabb'), ord('a')) == 2

    # deque and array have insert(), so insort works too
    d = collections.deque([1, 3, 5])
    assert bisect.bisect_left(d, 3) == 1
    bisect.insort(d, 4)
    bisect.insort_left(d, 0)
    bisect.insort_right(d, 6, key=lambda v: v)
    assert list(d) == [0, 1, 3, 4, 5, 6]
    ar = array.array('i', [1, 3, 5])
    assert bisect.bisect_right(ar, 3) == 2
    bisect.insort(ar, 2)
    assert list(ar) == [1, 2, 3, 5]

    # user classes
    s = Seq(8)
    assert bisect.bisect_left(s, 35) == 4
    assert bisect.bisect_right(s, 30) == 4
    assert bisect.bisect(s, 30, 0, 3) == 3
    assert bisect.bisect_left(s, 3, key=lambda v: v // 10) == 3
    bisect.insort(s, 15)
    bisect.insort_left(s, 20)
    bisect.insort_right(s, 20, 0, 2)
    assert s.inserted == [(2, 15), (2, 20), (2, 20)]

    n = NoLen()
    assert bisect.bisect_right(n, 35, 0, 100) == 4
    assert bisect.bisect_left(n, 35, hi=1000) == 4
    try:
        bisect.bisect(n, 35)
        assert False
    except TypeError as e:
        assert str(e) == "object of type 'NoLen' has no len()"


def test_all():
    test_bisect()
    test_bisect_insort()
    test_key()
    test_bounds()
    test_hi_out_of_range()
    test_insort_left_key()
    test_hi_keyword()
    test_sequences()


if __name__ == '__main__':
    test_all()
