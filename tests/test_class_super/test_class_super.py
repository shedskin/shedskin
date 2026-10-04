

class A:
    def __init__(self, x):
        self.x = x


class B(A):
    def __init__(self, x, y):
        super().__init__(x) ## this form is not supported
        self.y = y


class C(B):
    def __init__(self, x, y, z):
        super(C, self).__init__(x, y)
        self.z = z


def test_super():
    c = C('a', 'b', 'c')
    assert c.x == 'a'
    assert c.y == 'b'
    assert c.z == 'c'


class A1:
    def __init__(self, x):
        self.x = x


class B1(A1):
    def __init__(self, x, y):
        A1.__init__(self, x)
        self.y = y

class C1(B1):
    def __init__(self, x, y, z):
        B1.__init__(self, x, y)
        self.z = z


def test_init():
    c = C1('a', 'b', 'c')
    assert c.x == 'a'
    assert c.y == 'b'
    assert c.z == 'c'


class A2:
    def step(self):
        return 1


class B2(A2):
    def step(self):
        return super().step() + 10


class C2(B2):
    pass


class D2(C2):
    def step(self):
        return C2.step(self) + 100  # inherited method, via the class


def test_super_method():
    # A2 is also instantiated, so 'step' is read via both class and instance
    assert A2().step() == 1
    assert B2().step() == 11
    assert C2().step() == 11
    assert D2().step() == 111


def test_all():
    test_super()
    test_init()
    test_super_method()


if __name__ == '__main__':
    test_all()
