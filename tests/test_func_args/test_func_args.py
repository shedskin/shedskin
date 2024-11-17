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


# def test_args_kwargs():
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


def hap(a=1, b=2, /, c=3, *, d=4, e=5):
    return a+b+c+d+e


class Bert:
    def hap(self, a=1, b=2, /, c=3):
        return a+b+c


def test_poskw_only():
    assert hap(5,4,3,d=2,e=1) == 15
    assert hap(5,4,c=3,d=3,e=2) == 17

    bert = Bert()
    assert bert.hap(5,4,3) == 12
    assert bert.hap(5,4,c=4) == 13


TRUE = True
def test_default_args(arg=TRUE, arg2=[], arg3=''.join(3*['x']), arg4=17.7):
    assert arg
    assert arg2 == []
    assert arg3 == 'xxx'
    assert arg4 == 17.7


def test_all():
    test_tuple_arg()
    test_baz()
    test_boo()
    test_hoi()
    # test_args_kwargs()
    test_node()
    test_klass()
    test_msplit()
    test_poskw_only()
    test_default_args()


if __name__ == '__main__':
    test_all() 

