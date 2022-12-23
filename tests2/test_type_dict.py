
def add1(x): return x+1

def add2(x): return x+2

def test_dict():
    assert {"wah": 2}.get("aap", 3) == 3 # dict.get problem

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



# def test_problem_cases():
#     "these two cases don't work!"
#     e = {}
#     e[4] = 1.0
#     assert e.items() == [(4, 1.0)] ## FIXME doesn't work

#     g = {}
#     g['f1'] = add1
#     g['f2'] = add2
#     assert g['f1'](10) == 11
#     assert g['f2'](10) == 12


def test_all():
    test_dict()
    test_setdefault()
    test_misc()
    test_complex_keys()
    # test_problem_cases()


if __name__ == "__main__":
    test_all()



