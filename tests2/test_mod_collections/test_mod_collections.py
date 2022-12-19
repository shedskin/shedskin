from collections import defaultdict

def test_collections_defaultdict():
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


def test_all():
    test_collections_defaultdict()

if __name__ == '__main__':
    test_all()
