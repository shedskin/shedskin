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


def test_person():
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



def test_edge():
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



def test_all():
    test_person()
    test_edge()


if __name__ == "__main__":
    test_all()
