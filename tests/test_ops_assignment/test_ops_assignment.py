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
    assert (a, b, c) == (5, 4, 3)
    assert (dx, ex) == ([8, 7, 6], [2, 1, 0])


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
from collections import Counter, defaultdict

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


def test_walrus6():
    # target not otherwise used inside the comprehension (0925-C12)
    r = [1, 2, 3]
    assert [y for y in r if (z := y * 2) > 3] == [2, 3]
    assert z == 6
    assert [(w := y * 3) for y in r] == [3, 6, 9]
    assert w == 9
    assert [y for y in r for u in r if (v := y + u) > 5] == [3]
    assert v == 6
    assert {y for y in r if (a := y * 2) > 3} == {2, 3}
    assert a == 6
    assert {y: 1 for y in r if (b := y * 2) > 3} == {2: 1, 3: 1}
    assert b == 6
    assert sum(y for y in r if (c := y * 2) > 3) == 5
    assert c == 6
    assert list(y for y in r if (d := y * 2) > 3) == [2, 3]
    assert d == 6


class Acc:
    def __init__(self, n):
        self.n = n

    def __iadd__(self, other):
        self.n += other.n
        return self


def test_augassign_dict_inplace():
    # 'd[k] += v' updates a mutable value in place, like 'l[i] += v' (1023-B3)
    d = {'k': [1]}
    alias = d['k']
    d['k'] += [2]
    d['k'] += (3,)
    assert alias == [1, 2, 3]
    assert alias is d['k']

    dd = defaultdict(list)
    for i in range(4):
        dd[i % 2] += [i]
    first = dd[0]
    dd[0] += [4]
    assert first == [0, 2, 4]
    assert first is dd[0]
    assert dd[1] == [1, 3]

    ba = {'b': bytearray(b'a')}
    bal = ba['b']
    ba['b'] += b'b'
    assert bal == bytearray(b'ab')
    assert bal is ba['b']

    # class with only __iadd__ (1023-C5)
    da = {'a': Acc(1)}
    a0 = da['a']
    da['a'] += Acc(5)
    assert da['a'].n == 6
    assert a0 is da['a']

    # immutable values
    di = {'i': 1}
    di['i'] += 2
    assert di == {'i': 3}
    ds = {'s': 'a'}
    ds['s'] += 'b'
    assert ds == {'s': 'ab'}
    dt = {'t': (1,)}
    dt['t'] += (2,)
    assert dt == {'t': (1, 2)}
    dc = {'c': 1j}
    dc['c'] += 2
    assert dc == {'c': 2+1j}
    c = Counter('aab')
    c['a'] += 3
    c['z'] += 1
    assert sorted(c.items()) == [('a', 5), ('b', 1), ('z', 1)]
    try:
        dk = {'x': 1}
        dk['y'] += 1
        assert False
    except KeyError:
        pass


def unpack_gen(n):
    for i in range(n):
        yield i + 1


def unpack_gen2():
    a, b = unpack_gen(2)
    yield a + b


def test_unpack16():
    # iterables other than list/tuple/str/bytes (no intermediate list)
    a, b = {7: 'x', 8: 'y'}
    assert sorted([a, b]) == [7, 8]

    a, b, c = unpack_gen(3)
    assert (a, b, c) == (1, 2, 3)

    x, = {4}
    assert x == 4

    a, b = iter([5, 6])
    assert (a, b) == (5, 6)

    assert list(unpack_gen2()) == [3]

    for n in (2, 4):
        try:
            a, b, c = unpack_gen(n)
            assert False
        except ValueError:
            pass


class UnpackPoint:
    def __init__(self):
        self.x = 0
        self.y = 0


def test_unpack17():
    # attribute/subscript/nested targets (#1580)
    p = UnpackPoint()
    p.x, p.y = [1, 2]
    assert (p.x, p.y) == (1, 2)
    for rhs in ([1, 2, 3], [1]):
        try:
            p.x, p.y = rhs
            assert False
        except ValueError:
            pass
    for p.x, p.y in [[3, 4]]:
        pass
    assert (p.x, p.y) == (3, 4)
    try:
        for p.x, p.y in [[1, 2], [3, 4, 5]]:
            pass
        assert False
    except ValueError:
        pass

    l = [0, 0]
    l[0], l[1] = {1: 10, 0: 20}  # keys, not d[0], d[1]
    assert sorted(l) == [0, 1]
    l[0], l[1] = (x for x in range(2))
    assert l == [0, 1]
    l[0], l[1] = {9, 10}
    assert sorted(l) == [9, 10]
    l[0], p.y = unpack_gen(2)
    assert (l[0], p.y) == (1, 2)
    ls = ['', '']
    ls[0], ls[1] = {'a': 'b', 'c': 'd'}
    assert sorted(ls) == ['a', 'c']

    try:
        (a, b), c = [(i, i) for i in range(3)]
        assert False
    except ValueError:
        pass
    (a, b), c = [(1, 2), (3, 4)]
    assert (a, b, c) == (1, 2, (3, 4))
    (e, f), (g, h) = unpack_gen(2), unpack_gen(2)
    assert (e, f, g, h) == (1, 2, 1, 2)


class UnpackStar:
    def __init__(self):
        self.x = [0]


def test_unpack18():
    # extended iterable unpacking (#1484)
    a, *rest, b = [1, 2, 3, 4]
    assert (a, rest, b) == (1, [2, 3], 4)
    *rest, b = (1, 2, 3)
    assert (rest, b) == ([1, 2], 3)
    a, *rest = 1, 2
    assert (a, rest) == (1, [2])
    a, *rest = range(3)
    assert (a, rest) == (0, [1, 2])
    a, *rest, b = iter([1, 2])
    assert (a, rest, b) == (1, [], 2)
    *rest, = {5}
    assert rest == [5]
    a, *rest = b'xyz'
    assert (a, rest) == (120, [121, 122])
    a, *rest = unpack_gen(3)
    assert (a, rest) == (1, [2, 3])
    [c, *s] = 'hoi'
    assert (c, s) == ('h', ['o', 'i'])

    # starred attribute, subscript and nested targets
    q = UnpackStar()
    a, *q.x = [1, 2, 3]
    assert (a, q.x) == (1, [2, 3])
    l = [[0], [0]]
    a, *l[1], b = [1, 2, 3, 4]
    assert (a, l, b) == (1, [[0], [2, 3]], 4)
    a, *(e, f) = [1, 2, 3]
    assert (a, e, f) == (1, 2, 3)
    (a, *rest), b = [1, 2, 3], 4
    assert (a, rest, b) == (1, [2, 3], 4)

    # loops and comprehensions
    for a, *rest in [(1, 2, 3)]:
        assert (a, rest) == (1, [2, 3])
    for a, *rest in {1: 2}.items():
        assert (a, rest) == (1, [2])
    for a, *rest in enumerate([7]):
        assert (a, rest) == (0, [7])
    for a, *rest in zip([1], [2]):
        assert (a, rest) == (1, [2])
    assert [s for c, *s in ['abc', 'de']] == [['b', 'c'], ['e']]
    assert [(a, b, q.x) for a, *(b, *q.x) in [[1, 2, 3, 4], [5, 6]]] == \
        [(1, 2, [3, 4]), (5, 6, [])]

    try:
        a, *rest, b = [1]
        assert False
    except ValueError:
        pass
    try:
        a, b, *rest = iter([1])
        assert False
    except ValueError:
        pass


class AugAttr:
    def __init__(self):
        self.n = 0
        self.s = 'a'
        self.l = [1]
        self.other = None


augattr_objs = [AugAttr(), AugAttr()]
augattr_pos = [0]
augattr_k = [0]


def augattr_nxt():
    augattr_pos[0] += 1
    return augattr_objs[augattr_pos[0] - 1]


def augattr_idx():
    augattr_k[0] += 1
    return augattr_k[0] - 1


def test_augassign_attr_sidefx():
    # 'f().x += c' evaluates f() only once (1025-B3)
    objs, pos = augattr_objs, augattr_pos

    augattr_nxt().n += 10
    assert (objs[0].n, objs[1].n, pos[0]) == (10, 0, 1)
    augattr_nxt().s += 'b'
    assert (objs[0].s, objs[1].s, pos[0]) == ('a', 'ab', 2)
    pos[0] = 0
    augattr_nxt().l += [2]
    assert (objs[0].l, objs[1].l, pos[0]) == ([1, 2], [1], 1)

    objs[augattr_idx()].n -= 3
    assert (objs[0].n, augattr_k[0]) == (7, 1)

    objs[0].other = objs[1]
    objs[1].n = 1
    pos[0] = 0
    augattr_nxt().other.n <<= 2
    assert (objs[0].n, objs[1].n, pos[0]) == (7, 4, 1)


def unpack_msg(n, kind):
    try:
        if kind == 0:
            a, b, c = list(range(n))
        elif kind == 1:
            d, e, f = (i for i in range(n))
        elif kind == 2:
            g, *h, i, j = list(range(n))
        else:
            k, l, *m = iter(range(n))
    except ValueError as exc:
        return str(exc)
    return ''


def test_unpack_msgs():
    for kind in range(2):
        assert unpack_msg(2, kind) == 'not enough values to unpack (expected 3, got 2)'
        # python 3.14+ adds 'got N' for sized sequences
        assert unpack_msg(4, kind).startswith('too many values to unpack (expected 3')
    assert unpack_msg(2, 2) == 'not enough values to unpack (expected at least 3, got 2)'
    assert unpack_msg(1, 3) == 'not enough values to unpack (expected at least 2, got 1)'
    assert unpack_msg(3, 3) == ''
    a, b = 'ab'
    try:
        a, b = 'abc'
        assert False
    except ValueError as e:
        assert str(e).startswith('too many values to unpack (expected 2')


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
    test_unpack11()
    test_unpack12()
    test_unpack13()
    test_unpack14()
    test_unpack15()
    test_unpack16()
    test_unpack17()
    test_unpack18()
    test_walrus()
    test_walrus2()
    test_walrus3()
    test_walrus4()
    test_walrus5()
    test_walrus6()
    test_augassign_dict_inplace()
    test_augassign_attr_sidefx()
    test_unpack_msgs()


if __name__ == '__main__':
    test_all()
