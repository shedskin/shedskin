

def test_set1():
    s1 = set([1,2])
    s1.add(3)
    assert list(sorted(s1)) == [1,2,3]

def test_set2():
    a = set([1,2,3,4,5])
    b = set([3,4])
    assert list(sorted(a & b)) == [3, 4]
    assert list(sorted(a | b)) == [1, 2, 3, 4, 5]
    assert list(sorted(b | b)) == [3, 4]
    assert list(sorted(a - a)) == []
    assert list(sorted(a ^ a)) == []
    assert list(sorted(a.intersection(b))) == [3, 4]
    assert list(sorted(a.union(b))) == [1, 2, 3, 4, 5]
    assert list(sorted(a.difference(b))) == [1, 2, 5]


def test_set3():
    aa = set()
    aa.add(1)
    aa.add(2)
    assert list(sorted(aa.union(set([1, 3])))) == [1, 2, 3]

    s1 = set([1, 2, 3])
    s2 = set([3, 4, 5])
    assert sorted(s1.copy() - s2.copy()) == sorted(s1 - s2)
    assert not s1.issubset(s2)

    s1.difference_update(s2)
    assert sorted(s1) == [1, 2]

    s2.clear()
    assert s2 == set()

    s1.remove(1)
    assert s1 == set([2])

    s1.discard(2)
    assert s1 == set()

    assert set([2, 1]).issubset(set([3, 1, 2, 4]))

    s1.update(set([1, 2]))
    assert s1.issuperset(set([1]))

    af = set([1, 2, 3])
    assert sorted(af.intersection(s1)) == [1, 2]

    af.intersection_update(s1)
    assert af == set([1,2])

    s3 = set([3, 2, 1])
    while s3:
        s3.pop()
    assert s3 == set()


    s6 = set(["a", "b", "c"])

    assert not s6.isdisjoint(s6)
    assert not s6.isdisjoint(["a"])
    assert s6.isdisjoint(["d"])

    sa1 = set([1, 2, 3])
    sa2 = set([3, 4, 5])
    sa3 = set([4, 5, 6])

    assert sa1.difference(sa2) == set([1, 2])
    assert sa1.difference(sa3) == sa1
    assert sa1.difference([1, 2, 3]) == set([])
    assert sa2.difference([4, 5, 6]) == set([3])

    assert sa1.intersection([4, 5, 6]) == set([])
    assert sa1.intersection([3, 4, 5, 6]) == set([3])

    sa4 = set(["a", "b", "d"])
    sa5 = set(["d", "e", "f"])

    assert sa4.intersection(sa5) == sa4.intersection(["d", "e", "f"])

    low = set([1,2,3,4])
    high = set([4,5,6,9])
    assert list(sorted(low.symmetric_difference(high))) == [1, 2, 3, 5, 6, 9]

def test_set4():

    s1 = set(range(3))
    s1.update(list(range(2, 5)), list(range(12, 14)))
    assert sorted(s1) == [0, 1, 2, 3, 4, 12, 13]
    s1.update(list(range(2, 5)), list(range(12, 14)), list(range(18, 20)))
    assert sorted(s1) == [0, 1, 2, 3, 4, 12, 13, 18, 19]

    s2 = set(range(4))
    assert sorted(s2.union(set(range(6)), (6, 7))) == [0, 1, 2, 3, 4, 5, 6, 7]
    assert sorted(s2.union([5], [3, 4], list(range(3)))) == [0, 1, 2, 3, 4, 5]
    assert sorted(s2.intersection(list(range(1, 4)), list(range(2, 5)))) == [2, 3]
    assert sorted(s2.intersection(list(range(3)), [2], list(range(4)))) == [2]
    assert sorted(s2.difference(list(range(2)), list(range(3)))) == [3]
    assert sorted(s2.difference(list(range(2)), list(range(3)), [3, 6])) == []

    s3 = set(range(4))
    s3.intersection_update(list(range(2)), list(range(3)))
    assert sorted(s3) == [0, 1]

    s4 = set(range(3))
    s4.intersection_update(list(range(2)), list(range(3)), list(range(4)))
    assert sorted(s4) == [0, 1]

    s5 = set(range(4))
    s5.difference_update(list(range(2)), list(range(3)))
    assert sorted(s5) == [3]

    s6 = set(range(5))
    s6.difference_update(list(range(2)), list(range(3)), [3, 6])
    assert sorted(s6) == [4]


def test_frozenset():
    a = frozenset([1,2,3,4,5])
    b = frozenset([3,4])
    assert list(sorted(a & b)) == [3, 4]
    assert list(sorted(a | b)) == [1, 2, 3, 4, 5]
    assert list(sorted(b | b)) == [3, 4]
    assert list(sorted(a - a)) == []
    assert list(sorted(a ^ a)) == []
    assert list(sorted(a.intersection(b))) == [3, 4]
    assert list(sorted(a.union(b))) == [1, 2, 3, 4, 5]
    assert list(sorted(a.difference(b))) == [1, 2, 5]

def test_frozenset_hash():
    z, y = [(1, 2), (3,), (4, 5, 6)], [(3,), (4, 5, 6), (1, 2)]
    v, w = frozenset(z), frozenset(y)
    assert hash(v) == hash(w)

def test_set_cmp():
    a = set([1, 2])
    b = set([2, 3])
    assert not a >= b
    assert not a <= b
    assert not a == b
    assert a != b

def test_frozenset_cmp():
    a = frozenset([1, 2])
    b = frozenset([2, 3])
    assert not a >= b
    assert not a <= b
    assert not a == b
    assert a != b

def test_set_binary_elem():
    a = set()
    a.add(b"foo")
    assert len(a) == 1


def test_set_augmented_assign():
    set1 = set()
    set1 |= set([2, 3])
    assert sorted(set1) == [2,3]

    set2 = set()
    set2 &= set([2, 3])
    assert sorted(set2) == []

    set3 = set()
    set3 ^= set([2, 3])
    assert sorted(set3) == [2,3]

    set4 = set()
    set4 -= set([2, 3])
    assert sorted(set4) == []


def test_set_syntax():
    s = {1, 2}
    assert len(s) == 2
    assert 1 in s
    assert 2 in s
    assert s == set([1,2])


def test_all():
    test_set1()
    test_set2()
    test_set3()
    test_set4()
    test_set_cmp()
    test_frozenset()
    test_frozenset_hash()
    test_frozenset_cmp()
    test_set_binary_elem()
    test_set_augmented_assign()
    test_set_syntax()

if __name__ == "__main__":
    test_all()

