from collections import defaultdict
from collections import deque
from collections import Counter
import copy


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


def test_defaultdict_copy():
    # regression test: copy() used to drop the default_factory, so
    # missing-key access on the copy raised KeyError instead of using
    # the factory like the original does
    d = defaultdict(int)
    d['a'] = 1

    e = d.copy()
    assert e['a'] == 1

    e['b'] += 1
    assert e['b'] == 1
    assert d['a'] == 1
    assert 'b' not in d


def test_defaultdict_copy_module():
    # regression test: defaultdict had no __copy__/__deepcopy__ overrides,
    # so copy.copy()/copy.deepcopy() fell back to plain dict's versions,
    # silently downgrading the result to a dict and dropping default_factory
    d = defaultdict(int, {'a': 1})

    e = copy.copy(d)
    assert e['a'] == 1
    e['b'] += 1
    assert e['b'] == 1
    assert 'b' not in d

    f = copy.deepcopy(d)
    assert f['a'] == 1
    f['c'] += 1
    assert f['c'] == 1
    assert 'c' not in d


def test_defaultdict_from_pairs():
    # regression test: the constructor backing defaultdict(factory, iterable)
    # hardcoded the value type as __ss_int internally, so this only worked
    # when the value type actually was int; any other value type (str here)
    # failed to compile
    d = defaultdict(str, [(1, "a"), (2, "b")])
    assert d[1] == "a"
    assert d[2] == "b"
    assert d[99] == ""


def test_defaultdict_type_identity():
    # regression test: defaultdict never got its own class object, so every
    # defaultdict instance's __class__ silently stayed the base dict's. We
    # can't check this with isinstance()/type(): shedskin always evaluates
    # isinstance() to True and doesn't support type() at all. __repr__ is
    # overridden specifically for defaultdict, so it's a usable observable
    # proxy for whether an object is "really" a defaultdict.
    d = defaultdict(int)
    d['a'] = 1
    plain = dict()
    plain['a'] = 1

    assert repr(d) != repr(plain)
    assert repr(d).startswith('defaultdict(')
    assert not repr(plain).startswith('defaultdict(')

    # copy() must preserve the type too, not just the runtime __class__:
    # a prior version of this fix set __class__ correctly but copy()'s
    # type-inference stub still returned a plain dict, so the copy silently
    # lost the default_factory as far as the compiler was concerned
    e = d.copy()
    assert repr(e).startswith('defaultdict(')


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

    f = deque(maxlen=5)
    f.extend(range(10))
    assert list(f) == [5,6,7,8,9]


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


def test_deque_maxlen_negative():
    # regression test: maxlen used the C++ sentinel -1 to mean "no maxlen",
    # but any other negative value (e.g. -5) silently also behaved as
    # unbounded instead of raising ValueError like real deque, because the
    # bound check compared a signed maxlen against an unsigned size() and
    # always came out false for negative values
    raised = False
    try:
        deque([1, 2, 3], maxlen=-5)
    except ValueError:
        raised = True
    assert raised

    # 0 is a legitimate maxlen (always-empty deque) and must still work
    d = deque([1, 2, 3], maxlen=0)
    assert list(d) == []
    assert d.maxlen == 0


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


def test_deque_unhashable():
    # regression test: deque defines __eq__ but had no __hash__ override,
    # so it silently fell back to the default identity-based hash instead
    # of being unhashable like real deque (and like this module's dict)
    d = deque([1, 2, 3])
    raised = False
    try:
        hash(d)
    except TypeError:
        raised = True
    assert raised


def test_counter_construct_empty():
    c = Counter()
    c['a'] += 1
    c['a'] += 1
    c['b'] += 1
    assert sorted(c.items()) == [('a', 2), ('b', 1)]


def test_counter_construct_iterable():
    c = Counter('mississippi')
    assert sorted(c.items()) == [('i', 4), ('m', 1), ('p', 2), ('s', 4)]


def test_counter_construct_mapping():
    c = Counter({'x': 3, 'y': 1})
    assert sorted(c.items()) == [('x', 3), ('y', 1)]


def test_counter_missing_key():
    # unlike defaultdict, a missing key returns 0 but is NOT inserted
    c = Counter('aab')
    assert c['z'] == 0
    assert 'z' not in c
    assert sorted(c.keys()) == ['a', 'b']


def test_counter_most_common_all():
    c = Counter('mississippi')
    # counts, order-independent (ties aren't insertion-ordered in this
    # module's dict; see test_counter_most_common_distinct_counts for an
    # order-sensitive check)
    assert sorted(c.most_common()) == sorted(c.items())
    assert len(c.most_common()) == 4


def test_counter_most_common_distinct_counts():
    # all-distinct counts, so ordering is unambiguous even though this
    # module's dict isn't insertion-ordered like a real Python dict
    c = Counter()
    c['a'] = 5
    c['b'] = 3
    c['c'] = 1
    assert c.most_common() == [('a', 5), ('b', 3), ('c', 1)]
    assert c.most_common(2) == [('a', 5), ('b', 3)]
    assert c.most_common(0) == []


def test_counter_elements():
    c = Counter('mississippi')
    assert sorted(c.elements()) == sorted('mississippi')


def test_counter_elements_skips_nonpositive():
    c = Counter()
    c['a'] = 2
    c['b'] = 0
    c['c'] = -1
    assert sorted(c.elements()) == ['a', 'a']


def test_counter_update_iterable():
    c = Counter('aab')
    c.update('abc')
    assert sorted(c.items()) == [('a', 3), ('b', 2), ('c', 1)]


def test_counter_update_mapping():
    c = Counter({'p': 1, 'q': 2})
    c.update({'p': 5})
    assert sorted(c.items()) == [('p', 6), ('q', 2)]


def test_counter_subtract_iterable():
    c = Counter('aab')
    c.subtract('bb')
    # subtract(), unlike the arithmetic operators, keeps zero/negative counts
    assert sorted(c.items()) == [('a', 2), ('b', -1)]


def test_counter_subtract_mapping():
    c = Counter({'a': 3, 'b': 1})
    c.subtract({'a': 1})
    assert sorted(c.items()) == [('a', 2), ('b', 1)]


def test_counter_add_operator():
    a = Counter('abbccc')
    b = Counter('bccd')
    assert sorted((a + b).items()) == [('a', 1), ('b', 3), ('c', 5), ('d', 1)]


def test_counter_sub_operator():
    a = Counter('abbccc')
    b = Counter('bccd')
    # non-positive results are dropped, unlike subtract()
    assert sorted((a - b).items()) == [('a', 1), ('b', 1), ('c', 1)]


def test_counter_and_operator():
    a = Counter('abbccc')
    b = Counter('bccd')
    assert sorted((a & b).items()) == [('b', 1), ('c', 2)]


def test_counter_or_operator():
    a = Counter('abbccc')
    b = Counter('bccd')
    assert sorted((a | b).items()) == [('a', 1), ('b', 2), ('c', 3), ('d', 1)]


def test_counter_unary_pos():
    c = Counter()
    c['x'] = 3
    c['y'] = -2
    c['z'] = 0
    assert sorted((+c).items()) == [('x', 3)]


def test_counter_unary_neg():
    c = Counter()
    c['x'] = 3
    c['y'] = -2
    c['z'] = 0
    assert sorted((-c).items()) == [('y', 2)]


def test_counter_iadd():
    c = Counter('aab')
    c += Counter('a')
    assert sorted(c.items()) == [('a', 3), ('b', 1)]


def test_counter_isub_drops_nonpositive():
    c = Counter('aab')
    c -= Counter('aaaa')
    # in-place operators drop non-positive results too, like their
    # non-in-place counterparts (this differs from subtract())
    assert sorted(c.items()) == [('b', 1)]


def test_counter_ior():
    c = Counter('aab')
    c |= Counter('zzz')
    assert sorted(c.items()) == [('a', 2), ('b', 1), ('z', 3)]


def test_counter_iand():
    c = Counter('aab')
    c &= Counter('ab')
    assert sorted(c.items()) == [('a', 1), ('b', 1)]


def test_counter_copy():
    a = Counter('abc')
    b = a.copy()
    b['a'] += 100
    assert sorted(a.items()) == [('a', 1), ('b', 1), ('c', 1)]
    assert sorted(b.items()) == [('a', 101), ('b', 1), ('c', 1)]


def test_counter_copy_module():
    a = Counter('abc')

    b = copy.copy(a)
    b['a'] += 100
    assert sorted(a.items()) == [('a', 1), ('b', 1), ('c', 1)]
    assert sorted(b.items()) == [('a', 101), ('b', 1), ('c', 1)]

    d = copy.deepcopy(a)
    d['a'] += 100
    assert sorted(a.items()) == [('a', 1), ('b', 1), ('c', 1)]
    assert sorted(d.items()) == [('a', 101), ('b', 1), ('c', 1)]


def test_counter_type_identity():
    # same rationale as test_defaultdict_type_identity: isinstance()/type()
    # aren't usable here, so repr() is the observable proxy
    c = Counter('a')
    plain = dict()
    plain['a'] = 1

    assert repr(c).startswith('Counter(')
    assert not repr(plain).startswith('Counter(')


def test_all():
    test_defaultdict1()
    test_defaultdict2()
    test_defaultdict3()
    test_defaultdict_copy()
    test_defaultdict_copy_module()
    test_defaultdict_from_pairs()
    test_defaultdict_type_identity()
    test_deque1()
    test_deque2()
    test_deque3()
    test_deque4()
    test_deque_maxlen()
    test_deque_maxlen_on_init()
    test_deque_maxlen_negative()
    test_deque_eq()
    test_deque_insert_out_of_range()
    test_deque_remove_missing()
    test_deque_unhashable()
    test_counter_construct_empty()
    test_counter_construct_iterable()
    test_counter_construct_mapping()
    test_counter_missing_key()
    test_counter_most_common_all()
    test_counter_most_common_distinct_counts()
    test_counter_elements()
    test_counter_elements_skips_nonpositive()
    test_counter_update_iterable()
    test_counter_update_mapping()
    test_counter_subtract_iterable()
    test_counter_subtract_mapping()
    test_counter_add_operator()
    test_counter_sub_operator()
    test_counter_and_operator()
    test_counter_or_operator()
    test_counter_unary_pos()
    test_counter_unary_neg()
    test_counter_iadd()
    test_counter_isub_drops_nonpositive()
    test_counter_ior()
    test_counter_iand()
    test_counter_copy()
    test_counter_copy_module()
    test_counter_type_identity()


if __name__ == '__main__':
    test_all()
