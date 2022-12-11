def baz(x, y, z = 3):
    return x, y, z

def boo(x, y, z='g'):
    return x, y, z



def test_t1():
    assert baz(1, 2, 3) == (1, 2, 3)
    assert baz(1, 3) == (1, 3, 3)

def test_t2():
    assert boo(z = 'z', y = 'y', x = 'x') == ('x', 'y', 'z')
    assert boo(y = 'y', x = 'x') == ('x', 'y', 'g')
    assert boo('x', y = 'y') == ('x', 'y', 'g')


class A:
    def foo(self, x = 3, y = 'hello'):
        return x, y

def test_t3():
    assert A().foo(y = 'world', x = 42) == (42, 'world')


if __name__ == '__main__':
    test_t1()
    test_t2()
    test_t3()
