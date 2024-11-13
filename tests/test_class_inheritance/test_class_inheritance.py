class Father:
    def __init__(self, a):
        self.a = a
        b = 1

    def f(self, x):
        return x * self.a


class Son(Father):
    def g(self, x):
        return x * self.a * self.a


class Mother:
    def __init__(self, a):
        self.a = a
        b = 2

    def f(self, x):
        return x * self.a


class Daughter(Mother):
    def g(self, x):
        return x * self.a**self.a

class C1:
    def m1(self):
        self.a1 = 1

    def m2(self):
        self.a2 = 2


class C2(C1):
    def m2(self):
        self.a = 3


class C3(C2):
    def m2(self):
        self.a2 = 4


class RenderObject:
    def __init__(self, shader):
        self.shader = shader


class Plane(RenderObject):
    def __init__(self, plane, dist, shader):
        RenderObject.__init__(self, shader)
        self.plane = plane
        self.dist = dist


class Sphere(RenderObject):
    def __init__(self, pos, radius, shader):
        RenderObject.__init__(self, shader)
        self.pos = pos
        self.radius = radius


class World:
    def __init__(self):
        self.objects = []


class C:
    pass


class A(C):
    def woof(self):
        return 'woof'


class B(C):
    def meow(self):
        return 'meow'


def flop():
    pass


class Flip:
    pass


class flip_none(Flip):
    def flop(self):
        return 1


class flip_a3_a4(Flip):
    def flop(self):
        return 2




def test_inheritance1():
    w = World()
    w.objects.append(Plane(6, 7, 8))
    w.objects.append(Sphere(6, 7, 9))
    assert len(w.objects) == 2
    assert w.objects[0].shader == 8
    assert w.objects[1].shader == 9


def test_inheritance2():
    father = Father(3)
    assert father.f(4) == 12

    son = Son(4)
    assert son.g(5) == 80

    daughter = Daughter(4)
    assert daughter.g(5) == 1280


def test_inheritance3():
    c3 = C3()
    c3.m1()
    c3.m2()
    assert c3.a1 == 1
    assert c3.a2 == 4


def test_inheritance4():
    flip_funcs = [
        flip_none(),
        flip_a3_a4(),
    ]

    xx = flip_funcs[0]
    assert xx.flop() == 1

    xx = flip_funcs[1]
    assert xx.flop() == 2


def test_all():
    test_inheritance1()
    test_inheritance2()
    test_inheritance3()
    test_inheritance4()

if __name__ == '__main__':
    test_all() 

