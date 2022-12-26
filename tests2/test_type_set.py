
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


def test_all():
    test_set1()
    test_set2()
    test_frozenset()
    test_frozenset_hash()

if __name__ == "__main__":
    test_all()

