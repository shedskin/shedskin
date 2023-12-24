import copy
from collections import deque

class Person:
    def __init__(self, name):
        self.name = name

class Foo:
    pass

class Baz:
    pass


def test_deepcopy_nested():
    a = [[1], [2, 3]]
    b = copy.deepcopy(a)
    assert b[1][0] == 2


def test_copy_obj1():
    p = Person('loki')

    c = copy.copy(p)
    assert c.name == 'loki'

    d = copy.deepcopy(p)
    assert d.name == 'loki'


def test_copy_obj2():
    foo = Foo()
    foo.a = 7.0

    assert foo.a == 7.0

    foo_c = copy.copy(foo)
    assert foo_c.a == 7.0

    foo_dc = copy.deepcopy(foo)
    assert foo_dc.a == 7.0

def test_copy_obj3():
    baz = Baz()
    baz.a = [1,2,3]

    assert baz.a == [1,2,3]

    baz_c = copy.copy(baz)
    assert baz_c.a == [1,2,3]

    baz_dc = copy.deepcopy(baz)
    assert baz_dc.a == [1,2,3]



def test_copy1():
    a = 1
    b = copy.copy(a)
    assert b == 1

    x = 'loki'
    y = copy.copy(x)
    assert y == 'loki'


def test_copy2():

    b = [1, 2]
    a = copy.copy(b)
    a.append(3)

    assert a == [1,2,3]
    assert b == [1,2]
    assert copy.copy(178) == 178
    assert copy.copy((1, 2)) == (1, 2)
    assert copy.deepcopy((2, 3)) == (2, 3)
    assert copy.copy("1234") == "1234"
    assert copy.deepcopy("1234") == "1234"
    assert copy.copy((1, "1")) == (1, "1")
    assert copy.deepcopy((1, "1")) == (1, "1")

    assert sorted(copy.copy(set([1, 2]))) == [1,2]
    assert sorted(copy.deepcopy(set([1, 2]))) == [1,2]

    assert copy.copy({1: 1.0}) == {1: 1.0}
    assert copy.deepcopy({1.0: 1}) == {1.0: 1}

def test_copy_deque():
    assert copy.copy(list(deque(range(10)))) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert copy.deepcopy(list(deque(range(10)))) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]



def test_all():
    test_copy1()
    test_copy2()
    test_deepcopy_nested()
    test_copy_deque()
    test_copy_obj1()
    test_copy_obj2()
    test_copy_obj3()

if __name__ == '__main__':
    test_all()
