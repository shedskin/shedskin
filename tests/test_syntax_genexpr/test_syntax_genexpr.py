

def test_sum():
    xs = range(10)
    ys = range(10, 20)
    assert sum(x+y for x,y in zip(xs,ys)) == 190


def test_list():
    assert list(i for i in range(2)) == [0,1]


def test_set_comprehensions():  # TODO seperate 'syntax_comprehension' tests
    sc = {2*a for a in range(5)}
    assert sc == {0, 2, 4, 6, 8}

    ap = {xk+1 for xk in [2*yz for yz in range(10, 20)]}
    assert ap == {33, 35, 37, 39, 21, 23, 25, 27, 29, 31}

    ar = {sum(z) for z in [(2*w, 3*w) for w in range(10, 20)]}
    assert ar == {65, 70, 75, 80, 50, 85, 55, 90, 60, 95}

    uh = ((c, c**2) for c in range(10))
    sp = {u+v for u,v in uh}
    assert sp == {0, 2, 6, 72, 42, 12, 20, 56, 90, 30}


def test_set_comprehensions2():  # TODO causes max iterations whene merging with above func!?
    # primes to 100
    primes = [2] + sorted(set(range(3,100,2)) - {x for step in range(3, int(100**0.5) + 1, 2) if step %3 or step==3 for x in range(step * 3, 100, step * 2)})
    assert primes == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


def test_dict_comprehensions():  # TODO to seperate 'syntax_comprehension' tests?
    sc = {2*a for a in range(5)}
    da = {b: b*'x' for b in sc}
    assert da == {0: '', 2: 'xx', 4: 'xxxx', 6: 'xxxxxx', 8: 'xxxxxxxx'}

    # anagram of palindrome
    x = 'banbana'
    anapali = (len([v % 2 == 1 for t, v in {k:x.count(k) for k in list(set(x))}.items() if v % 2 == 1]) <= 1)
    assert anapali


def test_exhausted():
    xs = [1, 2]
    g = (x for x in xs)
    assert sum(g) == 3
    xs.append(3)
    assert sum(g) == 0
    assert list(g) == []
    assert sorted(g) == []
    assert not any(g)
    for x in g:
        assert False

    h = (10 // y for y in [1, 0, 2])
    assert next(h) == 10
    try:
        next(h)
        assert False
    except ZeroDivisionError:
        pass
    assert list(h) == []


CALLS = []
XS = [1, 2]

def make_iter():
    CALLS.append('make')
    return [3, 4]


def test_eager_iterable():  # outermost iterable is evaluated at creation (PEP 289)
    global XS
    g = (x for x in make_iter())
    CALLS.append('created')
    assert list(g) == [3, 4]
    assert CALLS == ['make', 'created']

    h = (x * y for x in XS for y in make_iter())
    XS = [7, 8]
    assert list(h) == [3, 4, 6, 8]

    try:
        e = (x for x in [1 // len(CALLS[:0])])
        assert False
    except ZeroDivisionError:
        pass


def test_all():
    test_eager_iterable()
    test_sum()
    test_list()
    test_set_comprehensions()
    test_set_comprehensions2()
    test_dict_comprehensions()
    test_exhausted()


if __name__ == "__main__":
    test_all()
