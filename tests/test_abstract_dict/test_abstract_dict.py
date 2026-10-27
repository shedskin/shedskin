# dict, defaultdict and Counter used abstractly: mixed in one container, or
# passed through the same function, so that the C++ static type is the base
# dict and behavior must follow the dynamic type (see issue #795)

from collections import defaultdict, Counter


def make_dicts():
    return [{'a': 1, 'b': 2}, defaultdict(int, {'a': 1, 'b': 2}), Counter({'a': 1, 'b': 2})]


def kind(r):
    if r.startswith('defaultdict('):
        return 'defaultdict'
    if r.startswith('Counter('):
        return 'Counter'
    return 'dict'


def lookup(d, k):
    try:
        return d[k]
    except KeyError:
        return -1


def append(d):
    try:
        d['x'].append(1)
        d['x'].append(2)
    except KeyError:
        return [-1]
    return d['x']


def inc(d):
    try:
        d['q'] += 3
        d['q'] += 1
    except KeyError:
        return -1
    return d['q']


def rm(d):
    try:
        del d['nope']
    except KeyError:
        return False
    return True


def union(x, y):
    return x | y


def same(x, y):
    return x == y


def build(n, counting):
    d = Counter() if counting else defaultdict(int)
    for i in range(n):
        d[i % 3] += 1
    return d


def test_basics():
    for d in make_dicts():
        assert len(d) == 2
        assert 'a' in d and 'zz' not in d
        assert sorted(d) == ['a', 'b']
        assert sorted(d.keys()) == ['a', 'b']
        assert sorted(d.values()) == [1, 2]
        assert sorted(d.items()) == [('a', 1), ('b', 2)]
        assert d.get('a', 0) == 1
        assert d.get('zz', 7) == 7
        assert [k for k in d if d[k] > 1] == ['b']


def test_getitem_missing():
    d, dd, c = make_dicts()
    assert lookup(d, 'zz') == -1
    assert 'zz' not in d
    assert lookup(dd, 'zz') == 0
    assert 'zz' in dd  # defaultdict inserts
    assert lookup(c, 'zz') == 0
    assert 'zz' not in c  # Counter does not


def test_getitem_missing_list_values():
    assert append({}) == [-1]
    assert append(defaultdict(list)) == [1, 2]


def test_addtoitem():
    d, dd, c = make_dicts()
    assert inc(d) == -1
    assert inc(dd) == 4
    assert inc(c) == 4
    assert inc({'q': 1}) == 5


def test_delitem():
    d, dd, c = make_dicts()
    assert not rm(d)
    assert not rm(dd)
    assert rm(c)  # Counter ignores missing keys


def test_copy():
    for d in make_dicts():
        e = d.copy()
        assert kind(repr(e)) == kind(repr(d))
        assert e == d
        e['a'] = 10
        assert d['a'] == 1

    dd = make_dicts()[1]
    e = dd.copy()
    assert e['new'] == 0  # default_factory survives the copy


def test_update_on_abstract():
    for d in make_dicts():
        d.update({'a': 5, 'c': 1})
        if kind(repr(d)) == 'Counter':
            assert sorted(d.items()) == [('a', 6), ('b', 2), ('c', 1)]
        else:
            assert sorted(d.items()) == [('a', 5), ('b', 2), ('c', 1)]


def test_update_with_abstract():
    c = Counter('ab')
    dd = defaultdict(int)
    plain = {}
    for d in make_dicts():
        c.update(d)
        dd.update(d)
        plain.update(d)
    assert sorted(c.items()) == [('a', 4), ('b', 7)]
    assert sorted(dd.items()) == [('a', 1), ('b', 2)]
    assert sorted(plain.items()) == [('a', 1), ('b', 2)]

    c = Counter()
    for d in make_dicts():
        c.subtract(d)
    assert sorted(c.items()) == [('a', -3), ('b', -6)]


def test_ior_on_abstract():
    for d in make_dicts():
        d |= {'a': 5, 'b': -1, 'c': 0}
        if kind(repr(d)) == 'Counter':
            # maximum of counts, non-positive results dropped
            assert sorted(d.items()) == [('a', 5), ('b', 2)]
        else:
            assert sorted(d.items()) == [('a', 5), ('b', -1), ('c', 0)]


def test_ior_with_abstract():
    c = Counter({'a': 3})
    for d in make_dicts():
        c |= d
    assert sorted(c.items()) == [('a', 3), ('b', 2)]


def test_or_on_abstract():
    d, dd, c = make_dicts()
    r = union(d, {'a': 0})
    assert kind(repr(r)) == 'dict' and r == {'a': 0, 'b': 2}
    r = union(dd, {'a': 0})
    assert kind(repr(r)) == 'defaultdict' and r == {'a': 0, 'b': 2}
    r = union(c, Counter({'a': 3, 'c': 1}))
    assert kind(repr(r)) == 'Counter' and sorted(r.items()) == [('a', 3), ('b', 2), ('c', 1)]


def test_eq():
    for d in make_dicts():
        for e in make_dicts():
            assert same(d, e)
            assert not (d != e)

    # Counter compares as a multiset only against another Counter
    assert same(Counter({'a': 1, 'b': 0}), Counter({'a': 1}))
    assert not same(Counter({'a': 1, 'b': 0}), {'a': 1})
    assert not same({'a': 1}, Counter({'a': 1, 'b': 0}))
    assert Counter({'a': 1, 'b': 0}) != {'a': 1}


def test_counter_ordering_with_dict():
    c = Counter({'a': 1})
    try:
        c <= {'a': 1}
        assert False
    except TypeError as e:
        assert str(e) == "'<=' not supported between instances of 'Counter' and 'dict'"
    try:
        c > {'a': 1}
        assert False
    except TypeError:
        pass
    assert c <= Counter({'a': 2})


def test_repr():
    d, dd, c = make_dicts()
    assert repr(d) == "{'a': 1, 'b': 2}"
    assert repr(c) == "Counter({'b': 2, 'a': 1})"
    assert str(c) == "Counter({'b': 2, 'a': 1})"


def test_conditional():
    a = build(7, True)
    b = build(7, False)
    assert a == b
    assert kind(repr(a)) == 'Counter' and kind(repr(b)) == 'defaultdict'
    assert a[10] == 0 and 10 not in a
    assert b[10] == 0 and 10 in b


def test_all():
    test_basics()
    test_getitem_missing()
    test_getitem_missing_list_values()
    test_addtoitem()
    test_delitem()
    test_copy()
    test_update_on_abstract()
    test_update_with_abstract()
    test_ior_on_abstract()
    test_ior_with_abstract()
    test_or_on_abstract()
    test_eq()
    test_counter_ordering_with_dict()
    test_repr()
    test_conditional()


if __name__ == '__main__':
    test_all()
