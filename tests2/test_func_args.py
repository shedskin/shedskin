# def hoi(a, b, e):
#     c = a
#     d = b
#     f = 1
#     g = 1
#     h = f+g
#     s = 'ho'+'i'                         # [str]
#     return c+d                           # [int, float]


# hoi(1, 2, 3)                             # [int]
# hoi(1.0, 2.0, 4)                         # [float]

# #def hoi(a, b, c=1, d=1):                 # a: [int], b: [int], c: [int, float]r, d: [int]
# #    print a, b, c, d                     # [int], [int], [int, float], [int]
# #    return c                             # [int, float]
# #
# #
# #hoi(1,2) 
# #hoi(1,2,3) 
# #hoi(1,2,3,4)                             # [int]
# #
# #hoi(1,2,3.1)                             # [int, float]

# def hoi(a, b, c=1, d=1):                 # a: [int], b: [int], c: [int, float]r, d: [int]
#     print(a, b, c, d)                     # [int], [int], [int, float], [int]
#     return c                             # [int, float]

# hoi(1,2) 
# hoi(1,2,3)
# hoi(1,2,3,4)                             # [int]


# def hoi(a, b):                           # a: [int, str], b: [int]
#     a                                    # [int, str]
#     a = 'hoi'                            # [str]
#     print(a)                              # [int, str]
# hoi('1', 1)                                # []




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
    test_baz()
    test_boo()
    # test_foo()
    test_klass()
    test_msplit()


if __name__ == '__main__':
    test_all() 

