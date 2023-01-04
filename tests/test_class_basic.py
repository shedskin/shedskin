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



def test_all():
    test_class_person()
    test_class_edge()
    test_class_attrs()
    test_class_instance_attrs()



if __name__ == "__main__":
    test_all()
