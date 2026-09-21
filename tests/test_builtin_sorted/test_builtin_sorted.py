
a = [
    (2, 3),
    (3, 2),
    (),
    (2,),
    (3, 4, 5),
    (2, 2),
    (1, 4),
    (4, 1),
    (4, 2),
    (4, 3),
    (3, 4),
    (4, 4),
    (4, 5),
    (1, 5),
    (1, 20),
    (20, 1),
    (20, 2),
]

a_sorted = [
    (),
    (1, 4),
    (1, 5),
    (1, 20),
    (2,),
    (2, 2),
    (2, 3),
    (3, 2),
    (3, 4),
    (3, 4, 5),
    (4, 1),
    (4, 2),
    (4, 3),
    (4, 4),
    (4, 5),
    (20, 1),
    (20, 2)
]


def test_sorted1():
    assert list(sorted(a)) == a_sorted


def test_sorted2():
    b = [[3, 2], [1, 3]]
    assert list(sorted(b)) == [[1, 3], [3, 2]]
    assert sorted([[3], [2, 1], [4, 5, 6]]) == [[2, 1], [3], [4, 5, 6]]


def test_sorted3():
    c = ["b", "c", "aa"]
    assert list(sorted(c)) == ['aa', 'b', 'c']


def test_reversed():
    assert [z for z in reversed(range(10))] == [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    assert list(reversed(['a','c','b'])) == ['b', 'c', 'a']


def test_sort_dict():
    digit_dict = {
        1: {1: (1, 2, 3, 4, 5), 2: (1, 3, 5), 3: ()},
        2: {1: (2,), 2: (), 3: (4,)},
        3: {1: (2, 4), 2: (), 3: ()},
        4: {1: (4, 5), 2: (1, 5), 3: ()},
        5: {1: (4,), 2: (), 3: (2,)},
        6: {1: (), 2: (), 3: (2,)},
        7: {1: (2, 3, 4, 5), 2: (3, 5), 3: ()},
        8: {1: (), 2: (), 3: ()},
        9: {1: (4,), 2: (), 3: ()},
        0: {1: (), 2: (3,), 3: ()},
    }

    xs = []
    for d in sorted(digit_dict):
        d2 = digit_dict[d]
        for g in sorted(d2):
            xs.append(((d, g), d2[g]))

    assert xs == [
        ((0, 1), ()),
        ((0, 2), (3,)),
        ((0, 3), ()),
        ((1, 1), (1, 2, 3, 4, 5)),
        ((1, 2), (1, 3, 5)),
        ((1, 3), ()),
        ((2, 1), (2,)),
        ((2, 2), ()),
        ((2, 3), (4,)),
        ((3, 1), (2, 4)),
        ((3, 2), ()),
        ((3, 3), ()),
        ((4, 1), (4, 5)),
        ((4, 2), (1, 5)),
        ((4, 3), ()),
        ((5, 1), (4,)),
        ((5, 2), ()),
        ((5, 3), (2,)),
        ((6, 1), ()),
        ((6, 2), ()),
        ((6, 3), (2,)),
        ((7, 1), (2, 3, 4, 5)),
        ((7, 2), (3, 5)),
        ((7, 3), ()),
        ((8, 1), ()),
        ((8, 2), ()),
        ((8, 3), ()),
        ((9, 1), (4,)),
        ((9, 2), ()),
        ((9, 3), ()),
    ]


def test_sorted_key_kwarg():
    words = ["banana", "kiwi", "fig", "apple"]
    assert sorted(words, key=len) == ["fig", "kiwi", "apple", "banana"]
    assert sorted(words, key=lambda w: w[-1]) == ["banana", "apple", "fig", "kiwi"]


def test_sorted_reverse_kwarg():
    nums = [5, 2, 8, 1, 9, 3]
    assert sorted(nums, reverse=True) == [9, 8, 5, 3, 2, 1]
    assert sorted(nums, reverse=False) == [1, 2, 3, 5, 8, 9]


def test_sorted_key_and_reverse_kwargs():
    words = ["banana", "kiwi", "fig", "apple"]
    # keywords in declared order
    assert sorted(words, key=len, reverse=True) == ["banana", "apple", "kiwi", "fig"]
    # keywords passed out of declared order
    assert sorted(words, reverse=True, key=len) == ["banana", "apple", "kiwi", "fig"]


def test_sorted_positional_iterable_with_kwargs():
    pairs = [(1, "b"), (3, "a"), (2, "c")]
    assert sorted(pairs, key=lambda p: p[1]) == [(3, "a"), (1, "b"), (2, "c")]
    assert sorted(pairs, key=lambda p: p[1], reverse=True) == [(2, "c"), (1, "b"), (3, "a")]


def test_sorted_stable_large():
    # more than one insertion-sort run, so the merge passes are exercised
    n = 1000
    pairs = [((i * 7919) % 97, i) for i in range(n)]
    # stable: equal keys keep their original (increasing) order
    result = sorted(pairs, key=lambda p: p[0])
    assert len(result) == n
    for i in range(1, n):
        assert result[i - 1][0] <= result[i][0]
        if result[i - 1][0] == result[i][0]:
            assert result[i - 1][1] < result[i][1]
    # reverse=True is stable as well (not reversed stable order)
    result = sorted(pairs, key=lambda p: p[0], reverse=True)
    for i in range(1, n):
        assert result[i - 1][0] >= result[i][0]
        if result[i - 1][0] == result[i][0]:
            assert result[i - 1][1] < result[i][1]
    # key function that allocates (may trigger collections while sorting)
    words = [str((i * 31337) % 1009) for i in range(n)]
    result2 = sorted(words, key=lambda w: w + "!" * (len(w) % 3))
    for i in range(1, n):
        assert result2[i - 1] + "!" * (len(result2[i - 1]) % 3) <= result2[i] + "!" * (len(result2[i]) % 3)
    assert sorted(result2) == sorted(words)
    # plain sort of objects, all sizes around the run boundary
    for m in range(28, 70):
        l = [str((i * 13) % m) for i in range(m)]
        assert sorted(l) == sorted(sorted(l, reverse=True))
        l.sort()
        for i in range(1, m):
            assert l[i - 1] <= l[i]


def test_all():
    test_sorted1()
    test_sorted2()
    test_sorted3()
    test_reversed()
    test_sort_dict()
    test_sorted_key_kwarg()
    test_sorted_reverse_kwarg()
    test_sorted_key_and_reverse_kwargs()
    test_sorted_positional_iterable_with_kwargs()
    test_sorted_stable_large()


if __name__ == '__main__':
    test_all()
