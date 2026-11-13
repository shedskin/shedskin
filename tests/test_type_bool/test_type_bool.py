from collections import defaultdict


def test_bool():
    assert bool(0) == False
    assert bool(1) == True
    assert int(True) == 1
    assert int(False) == 0

    assert not (True & True & False)
    assert (True & True & True)

    assert True & 1
    assert not 1 & False
    assert True * 5 == 5
    assert False * 5 == 0

    assert True *  [1, 2] == [1, 2]
    assert False * [1, 2] == []


def test_empty():
    assert bool([]) == bool(None)
    assert bool(set()) == bool(())
    assert bool({}) == bool("")
    assert bool(0.0) == bool(0)


class Bert:
    pass


class Bert2:
    def __bool__(self):
        return False

class Bert3:
    def __len__(self):
        return 0


def test_custom():
    b = Bert()
    assert bool(b)

    b2 = Bert2()
    assert not bool(b2)

    b3 = Bert3()
    assert not bool(b3)


def test_containers():
    # dict with bool values (dict<K, __ss_bool> instantiates __ne/__none)
    d = {0: True, 1: False}
    e = {0: True, 1: False}
    f = {0: True, 1: True}

    assert d == e
    assert not (d != e)
    assert d != f
    assert not (d == f)

    assert d[0] == True
    assert d.get(1, True) == False
    assert d.get(7, True) == True
    assert sorted(d.values()) == [False, True]
    assert sorted(d.items()) == [(0, True), (1, False)]

    g = d.copy()
    assert g == d
    assert g.pop(0, False) == True
    assert sorted(g.items()) == [(1, False)]

    # bool as dict key
    dd = {True: 0, False: 1}
    assert dd[True] == 0
    assert dd[False] == 1
    assert sorted(dd.keys()) == [False, True]

    # set/list/tuple of bools
    s = {True, False}
    assert sorted(s) == [False, True]
    assert True in s

    l = [True, False]
    assert l == [True, False]
    assert not (l != [True, False])
    assert l != [False, True]
    assert sorted(l) == [False, True]
    assert l.count(True) == 1
    assert l.index(False) == 1

    t = (True, False)
    assert t == (True, False)
    assert t != (True, True)
    assert t < (True, True)


def test_attributes():
    t, f = True, False
    assert t.real == 1
    assert t.imag == 0
    assert t.numerator == 1
    assert t.denominator == 1
    assert t.conjugate() == 1
    assert f.real == 0
    assert f.numerator == 0
    assert t.as_integer_ratio() == (1, 1)
    assert f.as_integer_ratio() == (0, 1)


def test_arithmetic():
    # a bool acts as an int in arithmetic
    t, f = True, False
    i, x = 2, 2.0

    # true division gives a float
    assert True / 2 == 0.5
    assert str(t / i) == '0.5'
    assert str(t / t) == '1.0'
    assert str(3 / t) == '3.0'
    assert str(f / i) == '0.0'
    assert str(t / x) == '0.5'
    assert str(x / t) == '2.0'

    # floor division and modulo stay int
    assert str(True // 2) == '0'
    assert str(t // i) == '0'
    assert str(t // t) == '1'
    assert str(7 // t) == '7'
    assert str(t // x) == '0.0'
    assert str(x // t) == '2.0'
    assert str(t % i) == '1'
    assert str(5 % t) == '0'
    assert str(t % x) == '1.0'
    assert divmod(t, i) == (0, 1)
    assert divmod(5, t) == (5, 0)
    assert divmod(t, t) == (1, 0)
    assert str(divmod(t, x)) == '(0.0, 1.0)'

    # power
    assert str(2 ** True) == '2'
    assert str(i ** t) == '2'
    assert str(i ** f) == '1'
    assert str(True ** 2) == '1'
    assert str(t ** t) == '1'
    assert str(f ** f) == '1'
    assert str(x ** t) == '2.0'
    assert str(t ** x) == '1.0'
    assert str(pow(t, i)) == '1'
    assert str(pow(i, t)) == '2'
    assert pow(3, t, 5) == 3
    assert pow(t, 3, 5) == 1

    # other operators
    assert str(t + t) == '2'
    assert str(t * 3) == '3'
    assert str(t - f) == '1'
    assert str(i - t) == '1'
    assert str(t + x) == '3.0'
    assert str(-t) == '-1'
    assert str(-t // 2) == '-1'
    assert str(divmod(-t, 2)) == '(-1, 1)'
    assert str(pow(-t, 3)) == '-1'
    assert str((-t) ** 2) == '1'
    assert str(~t // 2) == '-1'
    assert str(+t // 2) == '0'
    assert str(-t / 2) == '-0.5'
    assert str(-t % 5) == '4'
    assert t << 40 == 1099511627776
    assert 8 >> t == 4
    assert str(t & f) == 'False'
    assert str(t | f) == 'True'
    assert str(t & 3) == '1'

    # augmented assignment
    a = 7
    a //= t
    assert str(a) == '7'
    a **= t
    assert str(a) == '7'
    b = 7.0
    b /= t
    assert str(b) == '7.0'

    # division by False
    for k in range(4):
        try:
            if k == 0:
                print(t / f)
            elif k == 1:
                print(t // f)
            elif k == 2:
                print(t % f)
            else:
                print(divmod(t, f))
            assert False
        except ZeroDivisionError:
            pass


def test_factory():
    assert bool() == False
    assert not bool()
    b = bool()
    assert b is False

    seen = defaultdict(bool)
    assert seen['q'] == False
    seen['a'] = True
    assert seen['a']
    assert not seen['b']
    assert sorted(seen.items()) == [('a', True), ('b', False), ('q', False)]

    assert list(map(bool, [0, 1, 2])) == [False, True, True]
    assert list(filter(bool, [0, 3, 0, 4])) == [3, 4]
    assert sorted([2, 0, 1], key=bool) == [0, 2, 1]


def test_all():
    test_bool()
    test_attributes()
    test_arithmetic()
    test_factory()
    test_empty()
    test_custom()
    test_containers()


if __name__ == "__main__":
    test_all()
