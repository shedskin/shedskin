class Person:
    a = 1

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Person: '%s'>" % self.name

    def speak(self, x):
        return x

    def huh(self):
        self.b = 1

    def goodbye(self, x):
        b = 4
        return b


def test_class_person():
    f = Person("fred")
    assert f.a == 1

    g = f.speak("goedzo?")
    assert g == "goedzo?"

    f.huh()
    assert f.b == f.a

    f.hallo = 1
    assert f.hallo == f.a

    f2 = Person("fred")
    f2.c = "hello"
    assert f2.c == "hello"

    f3 = Person("fred")
    assert f3.goodbye("jo") == 4

    y = None
    y = Person("bert")
    assert y.name == "bert"


class Edge:
    def __eq__(self, x):
        return self.y == x.y

    def bla(self):
        assert self.meth_templ(1, 1) == 1
        assert self.meth_templ(1.0, 1) == 1.0
        return self.hop(self.x)

    def meth_templ(self, x, z):
        y = x
        return y

    def hop(self, x):
        return x



def test_class_edge():
    a = Edge()
    a.x = 1
    assert a.bla() == 1

    b = Edge()
    b.x = 1.0
    assert b.bla() == 1.0

    c = Edge()
    c.y = 1

    d = Edge()
    d.y = 2

    print(c == d)
    print(c == c)
    print(d == d)


class Foo:
    class_dict_var = {}
    class_dict_var2 = {}
    class_dict_var3 = {(1, 2): 7}
    kwad = (1, 2)
    wof = "wof"
    s = set()
    t = s
    z = t | s
    wa = [2 * x for x in range(10)]

    def __init__(self):
        self.y = 10
        Foo.class_dict_var[4] = 5
        Foo.class_dict_var2["4"] = 5
        Foo.s.update(Foo.kwad)

def test_class_attrs():
    foo = Foo()

    assert foo.y == 10
    assert foo.kwad == (1, 2)

    assert Foo.class_dict_var == {4: 5}
    assert Foo.class_dict_var2 == {'4': 5}
    assert Foo.class_dict_var3 == {(1, 2): 7}
    assert Foo.kwad == (1,2)
    assert Foo.wof == "wof"
    assert sorted(Foo.s) == [1, 2]
    assert sorted(Foo.t) == [1, 2]
    assert sorted(Foo.z) == []
    assert Foo.wa == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

    assert Foo.__name__ == 'Foo'
    assert Baz.__name__ == 'Baz'
    assert ReprableChild.__name__ == 'ReprableChild'
    assert foo.__class__.__name__ == Foo.__name__

class Baz:
    def __init__(self):
        a = None
        self.v = [1]
        self.v = a
        assert self.v == None

        w = self.v
        w = a
        assert w == None

        x = [1, 2, 3]
        x[1:2] = []
        x[1:2] = [4, 5]
        assert x == [1, 4, 5]

        self.x = [1, 2, 3]
        self.x[1:2] = []
        assert self.x == [1,3]


def test_class_instance_attrs():
    b = Baz()
    assert b.x == [1,3]
    assert not b.v


class Blah:
    pass

def test_instance_str():
    b1 = Blah()
    assert 'object at 0x' in str(b1)
    b2 = Blah()

    d = {}
    d[b1] = b1
    d[b2] = b2
    assert len(d) == 2

    e = {}
    e[str(b1)] = 'b1'
    e[str(b2)] = 'b2'
    assert len(e) == 2


class Reprable:
    def __repr__(self):
        return 'Reprable()'

class ReprableChild(Reprable):
    pass


def test_instance_repr():
    # repr() of an instance must be a usable str, whether the class
    # defines __repr__ or falls back to the default.
    r = repr(Blah())
    assert 'object at 0x' in r
    assert len(r) > 12

    assert repr(Reprable()) == 'Reprable()'
    assert str(Reprable()) == 'Reprable()'
    assert repr(ReprableChild()) == 'Reprable()'
    assert str(ReprableChild()) == 'Reprable()'


class IdA:
    def __init__(self, x):
        self.x = x

class IdB(IdA):  # only the subclass defines __eq__
    def __eq__(self, other):
        return self.x == other.x

class IdC:  # no __eq__/__ne__ anywhere: compared by identity
    def __init__(self, x):
        self.x = x

class IdC2(IdC):
    pass

class IdD:
    def __init__(self, x):
        self.x = x

class IdN:  # only __ne__
    def __init__(self, x):
        self.x = x
    def __ne__(self, other):
        return self.x != other.x

def test_identity_eq():
    a1, a2 = IdA(1), IdB(1)
    l = [a1, a2]
    assert a1 == a1 and l[0] == l[0] and not a1 != a1
    assert a2 == a1 and l[1] == IdB(1) and not l[1] != IdB(1)
    b1, b2 = IdB(1), IdB(1)
    assert b1 == b2 and not b1 != b2 and b1 != IdB(2)  # '!=' is 'not __eq__'
    c1, c2, c3 = IdC(1), IdC(1), IdC2(1)
    cc = [c1, c3]
    assert not c1 == c2 and c1 != c2 and c1 == c1 and not c1 != c1
    assert cc[1] == c3 and not cc[0] == c3 and cc[0] != c3
    n = None
    if c1.x == 2:
        n = c1
    assert not n == c1 and n != c1 and not c1 == n
    n = c1
    assert n == c1 and not n != c1
    mixed = [c1, IdD(1)]
    assert mixed[0] == c1 and not mixed[1] == c1 and mixed[1] != c1
    assert c2 in [c1, c2] and c3 not in [c1, c2] and [c1, c2].index(c2) == 1
    n1, n2 = IdN(1), IdN(1)
    assert not n1 != n2 and n1 != IdN(2)

# each __eq__ below is only reached in one way, so it must be modelled there
class EqNe:
    def __init__(self, x):
        self.x = x
    def __eq__(self, other):
        return self.x == other.x

class EqIn(EqNe):
    pass

class EqList:
    def __init__(self, x):
        self.x = x
    def __eq__(self, other):
        return self.x == other.x

class EqTuple:
    def __init__(self, x):
        self.x = x
    def __eq__(self, other):
        return self.x == other.x

class EqDict:
    def __init__(self, x):
        self.x = x
    def __eq__(self, other):
        return self.x == other.x
    def __hash__(self):
        return self.x

def test_modelled_eq():
    assert not EqNe(1) != EqNe(1) and EqNe(1) != EqNe(2)  # '!=' is 'not __eq__'
    assert EqIn(1) in [EqIn(2), EqIn(1)] and EqIn(3) not in (EqIn(1), EqIn(2))
    assert not [EqList(1)] != [EqList(1)] and [EqList(1)] != [EqList(2)]
    assert (EqTuple(1), 2) == (EqTuple(1), 2) and not (EqTuple(1), 2) != (EqTuple(1), 2)
    assert {1: EqDict(1)} == {1: EqDict(1)} and {1: EqDict(1)} != {1: EqDict(2)}


def test_all():
    test_class_person()
    test_class_edge()
    test_class_attrs()
    test_class_instance_attrs()
    test_instance_str()
    test_instance_repr()
    test_identity_eq()
    test_modelled_eq()



if __name__ == "__main__":
    test_all()
