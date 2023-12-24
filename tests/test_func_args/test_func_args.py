def hoi(a, b, c=1, d=1):
   return a, b, c, d

def baz(x, y, z = 3):
    return x, y, z

def boo(x, y, z='g'):
    return x, y, z

# default argument problem
def msplit(sep=0, spl=-1):
    return [""]

# def foo(*args): # this is not yet supported
#     return args

# def moo(**kwds): # this is not yet supported
#     return kwds

# def test_foo():
#     assert foo(1,2,3) == (1,2,3)
#     assert moo(a=1) == {'a':1}

class Klass:
    def foo(self, x = 3, y = 'hello'):
        return x, y


class Node:
    def __init__(self):
        self.input = [8]

def take_tuple1(arg):
    return arg[1]

def take_tuple2(arg):
    return arg[2]

def test_tuple_arg():
    assert take_tuple1((1,2,3)) == 2
    assert take_tuple2(('a','b','c')) == 'c'

def test_hoi():
    assert hoi(1,2) == (1,2,1,1)
    assert hoi(1,2,3) == (1,2,3,1)
    assert hoi(1,2,3,4) == (1,2,3,4)
    # assert hoi(1,2,3.1) == (1,2,3.1,1) ## Not supported

def test_node():
    node = Node()
    assert [link for link in node.input] == [8]

def test_baz():
    assert baz(1, 2, 3) == (1, 2, 3)
    assert baz(1, 3) == (1, 3, 3)

def test_boo():
    assert boo(z = 'z', y = 'y', x = 'x') == ('x', 'y', 'z')
    assert boo(y = 'y', x = 'x') == ('x', 'y', 'g')
    assert boo('x', y = 'y') == ('x', 'y', 'g')

def test_klass():
    assert Klass().foo(y = 'world', x = 42) == (42, 'world')

def test_msplit():
    assert msplit() == [""]


def test_all():
    test_tuple_arg()
    test_baz()
    test_boo()
    test_hoi()
    # test_foo()
    test_node()
    test_klass()
    test_msplit()


if __name__ == '__main__':
    test_all() 

