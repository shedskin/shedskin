
def add1(x): return x+1

def add2(x): return x+2

class Klass:
    def __init__(self, name):
        self.name = name


def test_dict():
    d = {1: "2", 2: "4"}
    assert list(d.keys()) == [1, 2]
    assert list(d.values()) == ['2', '4']
    assert list(d.items()) == [(1, '2'), (2, '4')]



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


if __name__ == "__main__":
    test_all()



