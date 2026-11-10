# container conversion/casting (#1178): a value used as another type than its
# own is cast if that is possible, and a literal (or another expression that
# creates a new container) is built as the other type directly


from collections import Counter


class A:
    def name(self):
        return 'A'


class B(A):
    def name(self):
        return 'B'


def total(l):
    return sum(l)


def test_literal():
    a = [1.5]
    a = [1, 2]
    assert a == [1, 2]
    assert a[0] / 2 == 0.5

    s = {1.5}
    s = {1, 2}
    assert sorted(s) == [1, 2]
    assert {1, 2} == {1.0, 2.0}

    d = {1: 1.5}
    d = {2: 3}
    assert d[2] / 2 == 1.5

    t = (1.5, 2.5)
    t = (1, 2)
    assert t[1] / 4 == 0.5

    nested = [[1.5]]
    nested.append([1])
    assert nested == [[1.5], [1]]
    sets = [{1.5}]
    sets.append({1})
    assert sets == [{1.5}, {1}]


def test_ifexp():
    x = 3
    a = [1.5]
    a = [1] if x > 2 else [2]
    assert a[0] / 2 == 0.5
    a = [1] if x < 2 else [2, 3]
    assert a[1] / 2 == 1.5

    assert total([0.5]) == 0.5
    assert total([1] if x > 2 else [2, 3]) == 1
    assert total([1] if x < 2 else [2, 3]) == 5


def test_subscript_assign():
    d = {1: [1.5]}
    d[2] = [1]
    d[3] = [4, 5]
    assert d[2][0] / 2 == 0.5
    assert sorted(d.items()) == [(1, [1.5]), (2, [1]), (3, [4, 5])]

    l = [[1.5]]
    l[0] = [7]
    assert l[0][0] / 2 == 3.5

    m = [(1.5, 'a')]
    m[0] = (2, 'b')
    assert m[0][0] / 4 == 0.5

    n = [[1]]
    n[0] = None
    assert n[0] is None
    e = {1: 'a'}
    e[2] = None
    assert e[2] is None

    la = [A(), B()]
    la[0] = B()
    assert [x.name() for x in la] == ['B', 'B']
    lists = [[A()]]
    lists[0] = [B()]
    assert lists[0][0].name() == 'B'


def test_lookup():
    # a tuple of ints, looked up among tuples of floats
    visited = {(1.0, 2.0)}
    assert (1, 2) in visited
    assert (2, 1) not in visited

    d = {(1.0, 2.0): 'a'}
    d[(3, 4)] = 'b'
    assert len(d) == 2
    assert d[(1, 2)] == 'a'
    assert d.get((3, 4)) == 'b'
    assert d.get((5, 6)) is None
    assert (1, 2) in d
    assert d.pop((1, 2)) == 'a'
    del d[(3, 4)]
    assert len(d) == 0

    l = [(0.0, 0.0), (1.0, 2.0)]
    assert l.index((1, 2)) == 1
    assert l.count((1, 2)) == 1
    assert (1, 2) in l
    l.remove((0, 0))
    assert l == [(1, 2)]

    lists = [[1.5], [2.0]]
    assert [2] in lists
    assert lists.index([2]) == 1


def test_operator():
    s = {1.0, 2.5}
    assert sorted(s | {3}) == [1, 2.5, 3]
    assert sorted(s & {1}) == [1]
    assert sorted(s - {1}) == [2.5]
    assert sorted(s ^ {1, 5}) == [2.5, 5]

    d = {1: 1.5}
    assert sorted((d | {2: 3}).items()) == [(1, 1.5), (2, 3)]

    a = [1.5]
    assert a + [2] == [1.5, 2]
    assert [3] + a == [3, 1.5]
    assert a + [2, 3] == [1.5, 2, 3]


def test_empty():
    assert len(set() | {1}) == 1
    assert {1} | set() == {1}
    assert len({} | {1: 2}) == 1
    assert [] + [1] == [1]
    assert [] + [1, 2] == [1, 2]
    assert Counter() + Counter('ab') == Counter('ab')


def test_class_instances():
    # containers of (sub)class instances have the same representation
    la = [A(), B()]
    lb = [B()]
    la = lb
    assert [x.name() for x in la] == ['B']
    la = [A()]
    la.extend(lb)
    assert [x.name() for x in la + lb] == ['A', 'B', 'B']

    ll = [[A()], lb]
    assert [[x.name() for x in l] for l in ll] == [['A'], ['B']]

    d = {1: [A()]}
    d[2] = lb
    d[3] = [B()]
    assert [x.name() for x in d[2] + d[3]] == ['B', 'B']

    nones = [None]
    strs = [['s'], nones]
    assert strs == [['s'], [None]]


def test_all():
    test_literal()
    test_ifexp()
    test_subscript_assign()
    test_lookup()
    test_operator()
    test_empty()
    test_class_instances()


if __name__ == '__main__':
    test_all()
