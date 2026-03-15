
def add1(x): return x+1

def add2(x): return x+2

class Klass:
    def __init__(self, name):
        self.name = name


def test_dict():
    d = {1: "2", 2: "4"}
    assert sorted(d.keys()) == [1, 2]
    assert sorted(d.values()) == ['2', '4']
    assert sorted(d.items()) == [(1, '2'), (2, '4')]



def test_dict_get():
    assert {"wah": 2}.get("aap", 3) == 3 # dict.get problem

def test_dict_del():
    d = {1: 4, 2: 5}
    del d[1]
    assert d == {2 : 5}

def test_setdefault():
    a={}
    a.setdefault(1,[]).append(1.0)
    assert a == {1: [1.0]}

def test_misc():
    a = {}
    a[1.0] = 1
    assert a[1.0] == 1

    b = {}
    b[1] = 1.0
    assert b[1] == 1.0

    c = {}
    c[4] = 1.0
    assert c[4] == 1.0

    d = {}
    d[4] = 1.0
    assert 4 in d

def test_complex_keys():
    t = (1, 2, 3)
    v = (1,)
    w = (1, 2, 3)

    e = {}

    e[t] = 1
    e[v] = 2
    e[w] = 3

    assert e[t] == 3
    assert e[v] == 2
    assert e[w] == 3

    assert e == {(1, 2, 3): 3, (1,): 2}

def test_instance_value():
    d = {}
    key = 'cicero'
    d[key] = Klass(key)
    assert d[key].name == 'cicero'


def test_negative_keys():
    d = {-1: 2}
    assert d[-1] == 2


def test_items():
    e = {}
    e[4] = 1.0
    assert list(e.items()) == [(4, 1.0)]

    assert sorted(dict([[1, 2], (3, 4)]).items()) == [(1, 2), (3, 4)]
    assert sorted(dict(["ab", "cd"]).items()) ==  [('a', 'b'), ('c', 'd')]
    assert sorted(dict(set([(1, 2.0), (3, 4.0)])).items()) == [(1, 2.0), (3, 4.0)]

# def test_func_as_value(): ## FIXME: does not work
    # g = {}
    # g['f1'] = add1
    # g['f2'] = add2
    # assert g['f1'](10) == 11
    # assert g['f2'](10) == 12

    # g[1] = add1
    # g[2] = add2
    # assert g[1](10) == 11
    # assert g[2](10) == 12


def test_dict_fromkeys():
    assert dict.fromkeys([1, 2, 3]) == {1: None, 2: None, 3: None}
    assert dict.fromkeys([1, 2, 3], 7) == {1: 7, 2: 7, 3: 7}
    assert dict.fromkeys([1, 2, 3], 4.0) == {1: 4.0, 2: 4.0, 3: 4.0}
    assert dict.fromkeys([1, 2, 3], "abc") == {1: 'abc', 2: 'abc', 3: 'abc'}


def test_pop():
    d = {-1: 2, 12: 24}

    assert d.pop(-1) == 2
    assert d.pop(7, 8) == 8
    assert d.pop(12, 9) == 24

    assert len(d) == 0


def test_update():
    # dict
    d = {1: '2', 2: '4'}
    e = {2: '5', 3: '6'}

    result = {1: '2', 2: '5', 3: '6'}
    d.update(e)
    assert d == result

    # iterable
    g = {1: '2', 2: '4'}
    g.update([(2, '5'), (3, '6')])
    assert g == result


def test_merge():
    # |, |= dict
    d = {1: '2', 2: '4'}
    e = {2: '5', 3: '6'}

    result = {1: '2', 2: '5', 3: '6'}
    assert d | e == result

    d |= e
    assert d == result

    # |= iterable
    g = {1: '2', 2: '4'}
    g |= [(2, '5'), (3, '6')]
    assert g == result


def test_frozendict():
    # init
    g = frozendict({7: '8', 8: '9'})
    assert len(g) == 2
    assert g[7] == '8'
    assert g[8] == '9'
    h = frozendict([(7, '8'), (8, '9')])
    assert g == h
    a = frozendict(['ab', 'cd'])
    assert a['a'] == 'b'
    assert a['c'] == 'd'

    # hash
    f = frozendict({20: '30'})
    t = (g, f)
    u = (f, g)
    assert t == t
    assert t != u

    # copy
    j = g.copy()
    assert j == g

    # or/ior
    k = frozendict({8: '10', 9: '12'})
    assert g | k == frozendict({7: '8', 8: '10', 9: '12'})

    oldk = k
    k |= g
    assert k == k | g
    assert len(oldk) == 2
    assert len(k) == 3

    # fromkeys
    z = frozendict.fromkeys('bahh')
    assert z == frozendict({'b': None, 'a': None, 'h': None})

    # str/repr
    assert str(f) == "frozendict({20: '30'})"
    assert repr(f) == "frozendict({20: '30'})"

    # abstract TODO


def test_all():
    test_dict()
    test_dict_get()
    test_dict_del()
    test_setdefault()
    test_misc()
    test_complex_keys()
    test_negative_keys()
    test_items()
    test_instance_value()
    # test_func_as_value()
    test_dict_fromkeys()
    test_pop()
    test_update()
    test_merge()
    test_frozendict()


if __name__ == "__main__":
    test_all()
