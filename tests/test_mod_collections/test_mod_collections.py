from collections import defaultdict
from collections import deque


def test_defaultdict1():
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


def test_defaultdict2():
    s3 = [("red", 1), ("blue", 2), ("red", 3), ("blue", 4), ("red", 1), ("blue", 4)]
    d3 = defaultdict(set)
    for k3, v3 in s3:
        d3[k3].add(v3)

    assert list(sorted(d3.items())) == [('blue', {2, 4}), ('red', {1, 3})]
    assert list(sorted(d3.keys())) == ['blue', 'red']


def test_defaultdict3():
    d = defaultdict(list)
    d[1].append('4')
    d[1].append('5')
    d[2] = ['6', '7']

    assert d[1] == ['4', '5']
    assert d[2] == ['6', '7']

    keys = set()
    for key, value in d.items():
        keys.add(key)
    assert keys == set([1,2])


def test_deque1():
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


def test_deque2():

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

    assert ([0, 1][4 in d], [0, 1][9 in d]) == (1, 0)

    d.rotate(3)
    assert list(d) == [1, 4, 5, 7, 6, 4, 2]

    d.rotate(-2)
    assert list(d) == [5, 7, 6, 4, 2, 1, 4]

    d.clear()
    assert not list(d)


def test_deque3():
    d = deque([1,2,2,2,3,4])
    assert d.count(2) == 3
    assert d.count(5) == 0

    assert d.index(3) == 4  # TODO start, stop args
    #d.index(17)  # TODO better valueerror msg

    d.reverse()
    assert list(d) == [4,3,2,2,2,1]


def test_deque4():
    d = deque([1,2,3,4])
    assert list(d) == [1,2,3,4]

    d.insert(1, 7)
    assert list(d) == [1,7,2,3,4]

    e = d.copy()
    assert list(e) == [1,7,2,3,4]

    d.append(3)
    assert list(d) == [1,7,2,3,4,3]

    assert d.index(3) == 3
    assert d.index(3, 4) == 5
    assert d.index(2, 1, -2) == 2


def test_deque_maxlen():
    d = deque([1,2,3], maxlen=4)
    assert d.maxlen == 4

    assert str(d) == 'deque([1, 2, 3], maxlen=4)'

    d.append(4)
    assert list(d) == [1,2,3,4]

    d.append(5)
    assert list(d) == [2,3,4,5]

    d.appendleft(6)
    assert list(d) == [6,2,3,4]

    #d.insert(2, 7) TODO works, add test?

    d.extend([7,8])
    assert list(d) == [3,4,7,8]

    d.extendleft([9,10])
    assert list(d) == [10,9,3,4]

    e = d.copy()
    assert e.maxlen == 4


def test_deque_maxlen_on_init():
    # regression test: maxlen used to be applied *after* the initial
    # extend(), so an iterable longer than maxlen wasn't truncated
    d = deque([1,2,3,4,5,6], maxlen=3)
    assert list(d) == [4,5,6]
    assert d.maxlen == 3

    e = deque([1,2], maxlen=3)
    assert list(e) == [1,2]
    assert e.maxlen == 3


def test_deque_eq():
    # regression test: deque used to fall back to pyobj's default
    # __eq__ (pointer identity), so equal-content deques compared unequal
    assert deque([1,2,3]) == deque([1,2,3])
    assert not (deque([1,2,3]) == deque([1,2,4]))
    assert deque([1,2,3]) != deque([1,2,4])
    assert not (deque([1,2,3]) != deque([1,2,3]))
    assert deque([1,2]) != deque([1,2,3])

    # equality ignores maxlen, matching real deque semantics
    assert deque([1,2,3], maxlen=5) == deque([1,2,3], maxlen=10)

    assert deque([]) == deque([])


def test_deque_insert_out_of_range():
    # regression test: insert used to compute an invalid iterator for
    # out-of-range indices instead of clamping like list.insert, which
    # silently corrupted the deque (large positive index) or crashed
    # (large negative index)
    d = deque([1, 2, 3])
    d.insert(100, 9)
    assert list(d) == [1, 2, 3, 9]

    e = deque([1, 2, 3])
    e.insert(-100, 8)
    assert list(e) == [8, 1, 2, 3]

    f = deque([1, 2, 3])
    f.insert(3, 9)
    assert list(f) == [1, 2, 3, 9]

    g = deque([1, 2, 3])
    g.insert(-1, 9)
    assert list(g) == [1, 2, 9, 3]


def test_deque_remove_missing():
    d = deque([1,2,3])
    raised = False
    try:
        d.remove(9)
    except ValueError:
        raised = True
    assert raised
    # value untouched
    assert list(d) == [1,2,3]


def test_all():
    test_defaultdict1()
    test_defaultdict2()
    test_defaultdict3()
    test_deque1()
    test_deque2()
    test_deque3()
    test_deque4()
    test_deque_maxlen()
    test_deque_maxlen_on_init()
    test_deque_eq()
    test_deque_insert_out_of_range()
    test_deque_remove_missing()


if __name__ == '__main__':
    test_all()
