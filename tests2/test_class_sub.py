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


def test_inheritence1():
    father = Father(3)
    assert father.f(4) == 12

    son = Son(4)
    assert son.g(5) == 80

    daughter = Daughter(4)
    assert daughter.g(5) == 1280


def test_inheritence2():
    c3 = C3()
    c3.m1()
    c3.m2()
    assert c3.a1 == 1
    assert c3.a2 == 4


def test_all():
    test_inheritence1()
    test_inheritence2()

if __name__ == '__main__':
    test_all() 

