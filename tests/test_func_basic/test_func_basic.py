
def propagate(la):
    return la, la


def ident(x):
    return x


def boing(c, d):
    return ident(c)


def bla():
    return 8


def bwa():
    d = 'hoi'
    return d


def hap(y):
    return y


class xevious:
    def solvalou(self, x):
        return x


def pacman(a):
    return 1


def qbert():
    c = 1
    a = 1
    pacman(a)
    b = 1
    a = c
    d = 1
    e = 1
    x = xevious()
    x.y = d
    x.z = 'hoi'
    x.solvalou(e)

    return b


def best_move(board):
    max_move = (1, 2)
    max_mobility = 1
    return max_move, max_mobility


def test_basic():
    assert boing(1, 1.0) == 1


def test_nested():
    a = 1
    h = boing(boing(a, 1.0), boing(3.0, a))
    assert h == 1


def test_local():
    assert qbert() == 1


def test_return_int():
    assert bla() == 8


def test_return_str():
    assert bwa() == 'hoi'


def test_return_float():
    assert hap(1.0) == 1.0


def test_return_tuple_of_lists():
    assert propagate([1]) == ([1],[1])
    assert propagate([2]) == ([2],[2])


def test_return_tuple():
    board = 1
    move, mob = best_move(board)
    assert move == (1,2)
    assert mob == 1


def row_perm_rec(numbers):
    return numbers[0]


def test_return_indexed_value():
    puzzlerows = [[8]]
    assert row_perm_rec(puzzlerows[0]) == 8


def split_ones(xs):
    if not xs:
        return [], []
    return [x for x in xs if x > 1], [x for x in xs if x <= 1]


def copy_list(xs):
    return [x for x in xs]


class Splitter:
    def split(self, xs):
        return [x for x in xs if x > 1], [x for x in xs if x <= 1]


def test_return_declared_type():
    # the declared return type merges over all calls, so differs from the
    # type inferred for a call that only returns empty lists
    assert split_ones([3, 1, 2]) == ([3, 2], [1])
    hi, lo = split_ones([])
    assert len(hi) == 0 and len(lo) == 0
    assert str(hi) == '[]' and str(lo) == '[]'

    r = split_ones([])
    assert r == ([], [])
    r = split_ones([3, 1, 2])
    assert r == ([3, 2], [1])

    assert copy_list([1, 2]) == [1, 2]
    e = copy_list([])
    assert len(e) == 0

    s = Splitter()
    assert s.split([3, 1]) == ([3], [1])
    a, b = s.split([])
    assert len(a) == 0 and len(b) == 0


def het_pair(xs):
    return [x for x in xs], 'a'


def nest_list(xs):
    return [[x for x in xs]]


def dict_of_list(xs):
    return {1: [x for x in xs]}


class DeclHolder:
    def __init__(self):
        self.v = copy_list([])
        self.p, self.q = split_ones([])


def wrap_copy():
    return copy_list([])


def test_return_declared_type2():
    assert het_pair([1]) == ([1], 'a')
    assert nest_list([1]) == [[1]]
    assert dict_of_list([1]) == {1: [1]}

    # nested unpacking, chained assignment
    (a, b), c = split_ones([]), 1
    assert len(a) == 0 and len(b) == 0 and c == 1
    d = e = copy_list([])
    assert len(d) == 0 and len(e) == 0

    # iterating over the result
    n = 0
    for y in copy_list([]):
        n += 1
    assert n == 0
    assert len([y for y in copy_list([])]) == 0
    assert len({y for y in copy_list([])}) == 0
    assert sum(1 for y in copy_list([])) == 0

    # item of the result
    x = split_ones([])[0]
    assert len(x) == 0
    x2 = split_ones([])[-1]
    assert len(x2) == 0
    h = het_pair([])[0]
    assert len(h) == 0 and het_pair([])[1] == 'a'
    m = nest_list([])[0]
    assert len(m) == 0
    dl = dict_of_list([])[1]
    assert len(dl) == 0
    p, q = nest_list([])[0], 1
    assert len(p) == 0 and q == 1
    for z in nest_list([])[0]:
        n += 1
    assert n == 0

    # attributes, containers, return, conditional
    o = DeclHolder()
    assert len(o.v) == 0 and len(o.p) == 0 and len(o.q) == 0
    assert len(wrap_copy()) == 0
    l = [copy_list([])]
    assert len(l) == 1 and len(l[0]) == 0
    t = (copy_list([]), 1)
    assert len(t[0]) == 0
    w = copy_list([]) if n == 0 else copy_list([])
    assert len(w) == 0
    w2 = copy_list([]) or copy_list([])
    assert len(w2) == 0


def test_all():
    test_basic()
    test_nested()
    test_local()
    test_return_int()
    test_return_str()
    test_return_float()
    test_return_tuple()
    test_return_tuple_of_lists()
    test_return_indexed_value()
    test_return_declared_type()
    test_return_declared_type2()


if __name__ == '__main__':
    test_all()
