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


def test_list_clear():
    some_list = [ 1, 2, 3, 4 ]
    some_list.clear()
    assert len(some_list) == 0


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
    assert [i+1.2 for i in [1, 1., 2., 3.2]] == [2.2, 2.2, 3.2, 4.4]
    assert list(i+1.2 for i in [1, 1., 2., 3.2]) == [2.2, 2.2, 3.2, 4.4]

    c = [[1],[3,4], None]
    assert c[0] == [1]
    assert c[1] == [3,4]
    assert c[2] is None

    q = [[[1],[2]],[[3],[4]]]
    assert q[0][0][0] == 1
    assert q[0][1][0] == 2
    assert q[1][0][0] == 3
    assert q[1][1][0] == 4


def test_list_index1():
    a = [1, 2, 3]
    assert a[0] == 1
    assert a[1] == 2
    assert a[-2] == 2
    assert a[-1] == 3

    lst = [1,0,2,3]
    missing = False
    try:
        lst.index(3,0,2)
    except ValueError as e:
        missing = True
    assert missing


def test_list_index2():
    xs = [1, 2, 3, 1]
    assert xs.index(1) == 0
    assert xs.index(1, 1) == 3
    assert xs.index(1, -1) == 3
    assert xs.index(1, -4) == 0
    assert xs.index(1, -3, 4) == 3


def test_list_index_str_identity():
    # 'foo' built via concatenation is value-equal to the literal in xs,
    # but is a separate allocation (distinct pointer identity). index()
    # must dispatch through __eq__, not compare object identity.
    needle = "f" + "oo"
    xs = ["foo", "bar", "foo"]
    assert xs.index(needle) == 0
    assert xs.index(needle, 1) == 2


def test_list_slice_assign():
    a = [1,2,3,4,5]
    assert a[:-1] == [1, 2, 3, 4]
    assert a[1:3] == [2, 3]
    assert a[::]  == [1, 2, 3, 4, 5]
    assert a[:3:] == [1, 2, 3]
    assert a[::-1] == [5, 4, 3, 2, 1]
    assert a[1::3] == [2, 5]
    assert a[4:1:-1] == [5, 4, 3]

    # iterator
    data = [1, 2, 3, 4]
    data[::2] = iter([10, 20])
    assert data == [10, 2, 20, 4]

    # set
    data = [1, 2, 3, 4]
    s = set([17, 18, 18])
    data[2:] = s
    assert sorted(data) == [1, 2, 17, 18]

    # literal set (see issue #829; now verified fixed)
    data = [1, 2, 3, 4]
    data[2:] = set([17, 18, 18])
    assert sorted(data) == [1, 2, 17, 18]

    # empty list
    data = [1, 2, 3, 4]
    data[:] = []
    assert data == []

    # tuple (non-list rvalue into list lvalue)
    data = [1, 2, 3, 4]
    data[1:3] = (10, 20)
    assert data == [1, 10, 20, 4]


def _extend_iterable_gen():
    yield 100
    yield 200


def test_list_extend_iterable():
    # list.extend() with various non-list iterables (see issue #828)
    data = [1, 2, 3, 4]
    data.extend(set([9, 10]))
    assert sorted(data) == [1, 2, 3, 4, 9, 10]

    data = [1, 2, 3, 4]
    data.extend(iter([5, 6]))
    assert data == [1, 2, 3, 4, 5, 6]

    data = [1, 2, 3, 4]
    data.extend((7, 8))
    assert data == [1, 2, 3, 4, 7, 8]

    data = [1, 2]
    data.extend(_extend_iterable_gen())
    assert data == [1, 2, 100, 200]

def test_list_extended_slice_size_mismatch_message():
    # regression test: list's extended-slice-assignment size check moved
    # into a shared helper (also used by bytearray); make sure list itself
    # kept its own "sequence of size" wording (bytearray uses "bytes of
    # size" instead -- see test_bytearray_extended_slice_size_mismatch_message).
    a = [1, 2, 3, 4, 5, 6]
    error = ''
    try:
        a[::2] = [1, 2]
    except ValueError as e:
        error = str(e)
    assert error == 'attempt to assign sequence of size 2 to extended slice of size 3'
    assert a == [1, 2, 3, 4, 5, 6]  # left untouched on error


def test_list_del():
    a = list(range(10))
    del a[9]
    assert a == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    del a[1:3]
    assert a == [0, 3, 4, 5, 6, 7, 8]
    del a[::2]
    assert a == [3, 5, 7]

    lst = list(range(10))
    del lst[8:2:-2]
    assert lst == [0, 1, 2, 3, 5, 7, 9]


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


class NeverEqual:
    def __eq__(self, other):
        return False

    def __hash__(self):
        return 1


def test_list_contains_identity():
    # like CPython, containment checks identity before calling __eq__
    a, b = NeverEqual(), NeverEqual()
    assert a in [b, a]
    assert b not in [a]
    assert not (a == a)
    assert a in (b, a)
    t = (1, 2)
    assert t in [(3, 4), t]


def test_list_assign():
    list5 = [(1,2),(3,4)]
    list5[0] = (2,2)
    assert list5 == [(2,2),(3,4)]


def test_list_length():
    puzzlecolumns = [1]
    assert puzzlecolumns.__len__() == 1


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


def test_list_copy():
    l = [1,2,3]
    a = l.copy()
    a.append(4)
    assert a == [1,2,3,4]
    assert l == [1,2,3]

    aa = [(1,2),(3,4)]
    bb = aa.copy()
    assert bb == aa


def test_list_imul():
    l = [1,2,3]
    l *= 4
    assert l == [1,2,3,1,2,3,1,2,3,1,2,3]

    l = [1,2,3]
    l *= -1
    assert l == []


def test_list_iadd():
    # 'list += iterable' extends in place: aliases DO see the change
    l = [1, 2]
    t = l
    l += [3]
    assert l == [1, 2, 3]
    assert t == [1, 2, 3]
    assert l is t

    l += (4, 5)
    assert t == [1, 2, 3, 4, 5]


def test_list_index_error_message():
    error = ''
    try:
        [1, 2].index(3)
    except ValueError as e:
        error = str(e)
    assert error == '3 is not in list'

    error = ''
    try:
        ['a', 'b'].index('c', 1)
    except ValueError as e:
        error = str(e)
    assert error == "'c' is not in list"

    error = ''
    try:
        [1.5].index(2.5, 0, 1)
    except ValueError as e:
        error = str(e)
    assert error == '2.5 is not in list'


def test_list_slice_assign_same_size():
    a = list(range(10))
    a[2:5] = [20, 30, 40]
    assert a == [0, 1, 20, 30, 40, 5, 6, 7, 8, 9]
    a[-3:] = [70, 80, 90]
    assert a == [0, 1, 20, 30, 40, 5, 6, 70, 80, 90]
    a[0:0] = []
    assert len(a) == 10
    a[4:2] = [-1]  # empty slice: insert
    assert a == [0, 1, 20, 30, -1, 40, 5, 6, 70, 80, 90]
    b = [1, 2, 3]
    b[0:3] = b
    assert b == [1, 2, 3]
    b[:] = b
    assert b == [1, 2, 3]
    d = [1, 2, 3]
    d[1:2] = d
    assert d == [1, 1, 2, 3, 3]
    d = [1, 2, 3]
    d[3:] = d
    assert d == [1, 2, 3, 1, 2, 3]
    c = [1, 2, 3]
    c[1:2] = [7, 8]
    assert c == [1, 7, 8, 3]
    c[1:3] = [9]
    assert c == [1, 9, 3]
    rows = [0] * 12
    for y in range(3):
        rows[y*4:y*4+4] = [y] * 4
    assert rows == [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]


def test_list_copy_paths():
    a = [1, 2, 3]
    a.extend(a)
    assert a == [1, 2, 3, 1, 2, 3]
    assert a + a == [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
    assert [] + a[:2] == [1, 2]
    assert a[:0] + [] == []
    assert a[1:4] == [2, 3, 1]
    assert a[4:1] == []
    b = ['x']
    b.extend(['y', 'z'])
    b += b[:1]
    assert b == ['x', 'y', 'z', 'x']


class Elt:
    pass


class SubElt(Elt):
    pass


_mul_x = 1


def _mul_count():
    global _mul_x
    _mul_x = 2
    return 3


def test_list_mul_elt():
    total = 5
    counts = [0] * total
    assert counts == [0, 0, 0, 0, 0]
    counts[2] += 1
    assert counts == [0, 0, 1, 0, 0]
    assert [7] * 0 == []
    assert [7] * -2 == []
    assert [-1] * 2 == [-1, -1]
    assert ['ab'] * 3 == ['ab', 'ab', 'ab']
    assert [None] * 2 == [None, None]
    floats = [0] * 3  # int literal converted to float elements
    floats[1] = 1.5
    assert floats == [0.0, 1.5, 0.0]
    x = 4
    assert [x] * total == [4, 4, 4, 4, 4]
    rows = [[]] * 3  # the same inner list, three times
    rows[0].append(1)
    assert rows == [[1], [1], [1]]
    grid = [[0] * 3] * 2
    assert grid == [[0, 0, 0], [0, 0, 0]]
    e = Elt()
    elts = [e] * 2
    elts.append(SubElt())
    assert elts[0] is e and elts[1] is e and len(elts) == 3
    # the element is evaluated before the count
    assert [_mul_x] * _mul_count() == [1, 1, 1]
    assert _mul_x == 2


class Deck:
    def __init__(self):
        self.cards = list(range(1, 11))

    def cut(self, n):
        self.cards[:-1] = self.cards[n:-1] + self.cards[:n]


class Counted:
    def __init__(self):
        self.calls = 0
        self._items = [1, 2, 3]

    @property
    def items(self):
        self.calls += 1
        self._items.append(self.calls)
        return self._items


def bump(l):
    l.append(99)
    return 1


def test_list_concat_parts():
    # concatenation of 2 or more (slices of) lists
    a = [1, 2, 3, 4, 5]
    b = [6, 7]
    c = [8, 9, 10]
    assert a[:2] + b == [1, 2, 6, 7]
    assert a + b + c == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert a[3:] + b[:1] + c[1:] + a[:1] == [4, 5, 6, 9, 10, 1]
    assert a[-2:] + a[:-3] + a[1:-1] == [4, 5, 1, 2, 2, 3, 4]
    assert a[10:] + a[-10:2] + a[4:2] + b == [1, 2, 6, 7]
    i, j = 1, 3
    assert a[i:j+1] + a[j*1:] + a[-i:] + a[:-j] == [2, 3, 4, 4, 5, 5, 1, 2]
    x = a[i:] + a[:i]
    x.append(0)
    assert x == [2, 3, 4, 5, 1, 0]
    assert a == [1, 2, 3, 4, 5]

    # slice assignment, also from the target itself
    d = list(range(10))
    d[:] = d[7:] + d[3:7] + d[:3]  # same size
    assert d == [7, 8, 9, 3, 4, 5, 6, 0, 1, 2]
    d[1:] = d[-1:] + d[1:-1]
    assert d == [7, 2, 8, 9, 3, 4, 5, 6, 0, 1]
    d[:-1] = d[4:-1] + d[:4]
    assert d == [3, 4, 5, 6, 0, 7, 2, 8, 9, 1]
    d[2:4] = d + a[:1]  # grow
    assert d == [3, 4, 3, 4, 5, 6, 0, 7, 2, 8, 9, 1, 1, 0, 7, 2, 8, 9, 1]
    d[1:-1] = d[:2] + d[-2:]  # shrink
    assert d == [3, 3, 4, 9, 1, 1]
    d[3:3] = d[:1] + b  # insert
    assert d == [3, 3, 4, 3, 6, 7, 9, 1, 1]
    d[5:2] = b[1:] + b[:1]  # empty target slice: insert
    assert d == [3, 3, 4, 3, 6, 7, 6, 7, 9, 1, 1]
    d[-100:100] = c[1:] + c[:1]
    assert d == [9, 10, 8]
    d[:] = a[2:4]  # single slice
    assert d == [3, 4]
    d[1:] = d[:0] + d[5:]  # delete
    assert d == [3]

    # pointers, floats
    s = ['a', 'b', 'c', 'd']
    s[:] = s[2:] + s[:2]
    assert s == ['c', 'd', 'a', 'b']
    assert s[:1] + s[3:] + s[1:3] == ['c', 'b', 'd', 'a']
    f = [1.5, 2.5, 3.5]
    f[1:] = f[2:] + f[:1] + f[1:2]
    assert f == [1.5, 3.5, 1.5, 2.5]

    # larger than the stack buffer
    big = list(range(2000))
    big[:] = big[1000:] + big[:1000]
    assert big[0] == 1000 and big[999] == 1999 and big[1000] == 0 and len(big) == 2000
    big[1:] = big[1500:] + big[:1]
    assert len(big) == 502 and big[:3] == [1000, 500, 501] and big[-1] == 1000

    # attributes
    deck = Deck()
    deck.cut(3)
    assert deck.cards == [4, 5, 6, 7, 8, 9, 1, 2, 3, 10]
    deck.cards[:] = deck.cards[5:] + deck.cards[:5]
    assert deck.cards == [9, 1, 2, 3, 10, 4, 5, 6, 7, 8]

    # side-effects: evaluated in order
    cnt = Counted()
    assert cnt.items[:2] + cnt.items[3:] == [1, 2, 1, 2]
    assert cnt.calls == 2
    e = [1, 2, 3]
    assert e[:] + e[bump(e):] == [1, 2, 3, 2, 3, 99]
    e = [1, 2, 3]
    e[bump(e):] = b[1:] + c[:1]  # (C++ argument order is unspecified)
    assert e == [1, 7, 8]

    # multiple targets
    g = [1, 2, 3]
    h = [0, 0]
    g[:1] = h[:] = g[1:] + g[:1]
    assert g == [2, 3, 1, 2, 3] and h == [2, 3, 1]


class Rows:
    def __init__(self):
        self.rows = []

    def fill(self, n):
        for i in range(n):
            self.rows.append(i)


def test_listcomp_append_reserve():
    # single-loop list comprehensions reserve for the remaining iterations
    n = 10
    assert [i * i for i in range(n)] == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    assert [i for i in range(20, 3, -3)] == [20, 17, 14, 11, 8, 5]
    assert [i for i in range(n, n)] == []
    assert [[j for j in range(i)] for i in range(1, 4)] == [[0], [0, 1], [0, 1, 2]]
    s = 'abcdefgh'
    assert [c * i for i, c in enumerate(s)] == ['', 'b', 'cc', 'ddd', 'eeee', 'fffff', 'gggggg', 'hhhhhhh']
    d = {}
    for i in range(9):
        d[i] = str(i)
    assert sorted([(v, k) for k, v in d.items()]) == [(str(i), i) for i in range(9)]
    assert sorted([k for k, v in d.items() if k % 2]) == [1, 3, 5, 7]
    assert [k for k, v in {}.items()] == []


def test_list_append_reserve():
    # 'for i in range(..): l.append(..)': reserve for remaining iterations
    a = [1, 2]
    for i in range(10):
        a.append(i)
    assert a == [1, 2, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    b = []
    c = []
    for i in range(20, 3, -3):
        b.append(i)
        c.append(-i)
        b.append(i // 2)
    assert b == [20, 10, 17, 8, 14, 7, 11, 5, 8, 4, 5, 2]
    assert c == [-20, -17, -14, -11, -8, -5]
    for i in range(5, 5):
        b.append(i)
    assert len(b) == 12
    d = [[0]]
    for i in range(1, 4):
        d.append([])
        for j in range(i):
            d[i].append(j)
    assert d == [[0], [0], [0, 1], [0, 1, 2]]
    e = []
    for i in range(0, 100, 7):
        i = i * 2  # does not change the iteration count
        e.append(i)
    assert e == [0, 14, 28, 42, 56, 70, 84, 98, 112, 126, 140, 154, 168, 182, 196]
    f = []
    for i in range(3):
        f.append(i)
        f = f + [9]
    assert f == [0, 9, 1, 9, 2, 9]
    g = []
    try:
        for i in range(10**15):
            g.append(i)
            if i == 3:
                raise ValueError
    except ValueError:
        pass
    assert g == [0, 1, 2, 3]
    h = []
    for i in range(10**15, 0, -10**14):
        h.append(i // 10**14)
    assert h == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    r = Rows()
    r.fill(3)
    r.fill(2)
    assert r.rows == [0, 1, 2, 0, 1]
    big = []
    for i in range(100000):
        big.append(i)
    assert len(big) == 100000 and big[-1] == 99999
    # inner loop appending to a list shared by the outer loop: must still
    # grow geometrically (minpng regression)
    img = []
    for y in range(300):
        for x in range(200):
            img.append(x + y)
    assert len(img) == 60000 and img[0] == 0 and img[-1] == 498
    assert sum(img) == 60000 * 249
    s = []
    for i in range(3):
        s.append(str(i))
    else:
        s.append('x')
    assert s == ['0', '1', '2', 'x']

    # other sized iterables
    src = [3, 1, 2]
    t = [0]
    for x in src:
        t.append(x * 2)
        t.append(x)
    assert t == [0, 6, 3, 2, 1, 4, 2]
    u = []
    for ch in 'abc':
        u.append(ch)
    for num in (1, 2):
        u.append(str(num))
    for key in {'z': 1}:
        u.append(key)
    for elem in {5}:
        u.append(str(elem))
    for i, ch2 in enumerate('pq'):
        u.append(ch2 * (i + 1))
    assert u == ['a', 'b', 'c', '1', '2', 'z', '5', 'p', 'qq']
    v = [1, 2, 3]
    w = []
    for x in v:
        w.append(x)
        if x < 3:
            v.append(x + 3)  # iterated list grows
    assert w == [1, 2, 3, 4, 5] and v == [1, 2, 3, 4, 5]
    v = [1, 2, 3, 4]
    w = []
    for x in v:
        w.append(x)
        del v[-1]  # iterated list shrinks
    assert w == [1, 2]


def test_list_fresh_copy():
    # list(..) of a fresh list need not copy it
    a = [1, 2, 3]
    b = list(a[1:])
    b.append(4)
    c = list(a + b)
    c[0] = 9
    d = list([x * 2 for x in a])
    e = list(a * 2)
    f = list([7, 8])
    g = list(a[:])
    assert a == [1, 2, 3] and b == [2, 3, 4] and c == [9, 2, 3, 2, 3, 4]
    assert d == [2, 4, 6] and e == [1, 2, 3, 1, 2, 3] and f == [7, 8]
    assert g == a and g is not a


def test_list_literal_long():
    # more elements than the inline storage of the backing small_vector
    l = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 2), (3, 3)]
    assert len(l) == 8
    assert l[7] == (3, 3)
    assert sum([a + b for a, b in l]) == 18


def test_all():
    test_list_literal_long()
    test_list_copy_paths()
    test_list_append()
    test_list_assign()
    test_list_cmp()
    test_list_clear()
    test_list_comp()
    test_list_del()
    test_list_index1()
    test_list_index2()
    test_list_index_str_identity()
    test_list_length()
    test_list_misc()
    test_list_nested()
    test_list_slice_assign()
    test_list_extend_iterable()
    test_list_extended_slice_size_mismatch_message()
    test_list_subsets()
    test_list_copy()
    test_tuple_in_list()
    test_list_contains_identity()
    test_list_imul()
    test_list_iadd()
    test_list_index_error_message()
    test_list_slice_assign_same_size()
    test_list_mul_elt()
    test_list_concat_parts()
    test_list_append_reserve()
    test_listcomp_append_reserve()
    test_list_fresh_copy()


if __name__ == "__main__":
    test_all()
