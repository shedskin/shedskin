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


class MyBase:
    pass

class MyChild(MyBase):
    def __call__(self, x, y):
        return x * y

class MyOtherChild(MyBase):
    def __call__(self, x, y):
        return x * y


def test_virtual_dunder():
    a = MyChild()
    a = MyOtherChild()
    assert a(2, 'hop') == 'hophop'



class RedundantObjectBase(MyBase, object):
    def __call__(self, x, y):
        return x + y


def test_redundant_object_base():
    # regression test: an explicit, redundant 'object' base alongside a real
    # base is still single inheritance and must not be rejected as
    # multiple inheritance
    a = RedundantObjectBase()
    assert a(2, 3) == 5


class Bert:
    def hophop(self, a):
        raise NotImplementedError('oops')

class Gert(Bert):
    def hophop(self, a):
        return 'flup'

class Arie(Bert):
    def hophop(self, a):
        return 'flap'

class Jort(Bert):
    pass


def test_virtual_case():
    # hophop is called for Jort, but only via inheritance
    b = Jort()
    error = ''
    try:
        l = b.hophop(12)
    except NotImplementedError as e:
        error = str(e)
    assert error == 'oops'

    b = Arie()
    l = b.hophop(17)
    assert l == 'flap'
    b = Gert()
    l = b.hophop(17)
    assert l == 'flup'


class KwBase:  # 1031-D1: C++ keywords as parameter names
    def get(self, key, default=None):
        return default

    def make(self, new, template):
        return new + template


class KwSub(KwBase):
    def get(self, key, default=None):
        return key

    def make(self, new, template):
        return new * template


def test_virtual_cpp_keyword_formals():
    res = [(o.get('a', 'b'), o.make(2, 3)) for o in [KwBase(), KwSub()]]
    assert res == [('b', 5), ('a', 6)]


class RetE:
    def name(self):
        return 'E'


class RetN(RetE):
    def name(self):
        return 'N'


class RetV(RetE):
    def name(self):
        return 'V'


class RetBase:  # 1029-C3, 1030-C3: new containers returned by overrides
    def empty_list(self):
        return []

    def empty_dict(self):
        return {}

    def empty_set(self):
        return set()

    def objs(self):
        return [RetN(), RetN()]


class RetSub(RetBase):
    def empty_list(self):
        return [1, 2]

    def empty_dict(self):
        return {1: 2}

    def empty_set(self):
        return {1, 2}

    def objs(self):
        return [RetV()]


def test_virtual_return_new_container():
    objs = [RetBase(), RetSub()]
    assert [o.empty_list() for o in objs] == [[], [1, 2]]
    assert [o.empty_dict() for o in objs] == [{}, {1: 2}]
    assert [sorted(o.empty_set()) for o in objs] == [[], [1, 2]]
    assert [[x.name() for x in o.objs()] for o in objs] == [['N', 'N'], ['V']]


class StopIterSub(StopIteration):
    pass


def test_builtin_attribute_not_shadowed():
    # StopIteration itself is not instantiated here, so its 'value'
    # attribute must not be redeclared in the subclass (1106-B8)
    ok = False
    try:
        raise StopIterSub('ss')
    except StopIterSub as e:
        ok = e.value == 'ss'
    assert ok


class CallA:  # 818: calling methods via the class, as in 'A.f(obj, ..)'
    def __init__(self):
        self.n = 1

    def f(self, y=10):
        return self.n + y

    def g(self):
        return CallA.f(self, 1)  # non-virtual, also in subclasses

    def h(self, other):
        return CallA.f(other, self.n)


class CallB(CallA):
    def f(self, y=20):
        return 100 + CallA.f(self, y)


class CallC(CallB):
    def __init__(self):
        self.n = 5


class CallD(CallC):
    def f(self, y=30):
        return 1000 + CallB.f(self, y)


class CallE:
    def __init__(self):
        self.n = 7

    def f(self):
        return self.n


class CallF(CallE):
    def f(self):
        return 'f'


class CallG:
    def call(self, a):
        return CallA.f(a, 2)


def test_class_call():
    a, b, c, d = CallA(), CallB(), CallC(), CallD()
    assert CallA.f(a) == 11
    assert CallA.f(a, 2) == 3
    assert CallA.f(a, y=3) == 4
    assert CallA.f(b) == 11
    assert CallB.f(b, 1) == 102
    assert CallC.f(c, 3) == 108  # inherited from CallB
    assert CallD.f(d) == 1135
    assert CallG().call(d) == 7
    assert [o.g() for o in (a, b, c, d)] == [2, 2, 6, 6]
    assert d.h(a) == 6

    objs = [a, b, c, d]
    assert [CallA.f(o, 2) for o in objs] == [3, 3, 7, 7]
    assert [CallA.f(o) for o in objs] == [11, 11, 15, 15]

    e, f = CallE(), CallF()
    assert CallE.f(f) + 1 == 8  # different return types
    assert CallF.f(f) + 'g' == 'fg'


def test_all():
    test_inheritance1()
    test_inheritance2()
    test_inheritance3()
    test_inheritance4()

    test_virtual_dunder()
    test_virtual_case()
    test_redundant_object_base()
    test_virtual_cpp_keyword_formals()
    test_virtual_return_new_container()
    test_builtin_attribute_not_shadowed()
    test_class_call()


if __name__ == '__main__':
    test_all()
