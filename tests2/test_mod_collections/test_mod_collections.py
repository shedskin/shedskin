from collections import defaultdict
from collections import deque



def test_collections_defaultdict1():
    s1 = "mississippi"
    d1 = defaultdict(int)
    for k1 in s1:
        d1[k1] += 1
    assert list(sorted(d1.keys())) == ['i', 'm', 'p', 's']

    s2 = [("yellow", 1), ("blue", 2), ("yellow", 3), ("blue", 4), ("red", 1)]
    d2 = defaultdict(list)
    for k2, v2 in s2:
        d2[k2].append(v2)
    assert list(sorted(d2.items())) == [('blue', [2, 4]), ('red', [1]), ('yellow', [1, 3])]


def test_collections_defaultdict2():
    s3 = [("red", 1), ("blue", 2), ("red", 3), ("blue", 4), ("red", 1), ("blue", 4)]
    d3 = defaultdict(set)
    for k3, v3 in s3:
        d3[k3].add(v3)

    # assert list(sorted(d3.items())) == [('blue', {2, 4}), ('red', {1, 3})]
    assert list(sorted(d3.keys())) == ['blue', 'red']



def test_collections_deque1():
    d = deque([3, 2, 1])
    d.append(4)
    d.appendleft(0)

    assert len(d) == 5

    assert [d[i] for i in range(len(d))] == [0, 3, 2, 1, 4]

    assert d.pop() == 4
    assert d.popleft() == 0

    assert list(d) == [3,2,1]

    while d:
        d.pop()

    assert list(d) == []


def test_collections_deque2():

    d = deque([3, 2, 1])
    e = iter(d)
    assert list(e) == [3,2,1]

    d.extend([4, 5])
    assert list(d) == [3, 2, 1, 4, 5]

    d.extendleft([6, 7])
    assert list(d) == [7, 6, 3, 2, 1, 4, 5]

    assert list(sorted(d)) == [1, 2, 3, 4, 5, 6, 7]
    assert [e for e in reversed(d)] == [5, 4, 1, 2, 3, 6, 7]

    d[2] = d[-2] = 4
    assert list(d) == [7, 6, 4, 2, 1, 4, 5]
    
    # assert [0, 1][4 in d], [0, 1][9 in d] == (1, 0) ## FIXME

    d.rotate(3)
    assert list(d) == [1, 4, 5, 7, 6, 4, 2]

    d.rotate(-2)
    assert list(d) == [5, 7, 6, 4, 2, 1, 4]

    d.clear()
    assert not list(d)





def test_all():
    test_collections_defaultdict1()
    test_collections_defaultdict2()
    test_collections_deque1()
    test_collections_deque2()

if __name__ == '__main__':
    test_all()
