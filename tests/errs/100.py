# 1030-B1, 1031-C2: defaults and keywords of overriding methods are taken from one of them

class Base:
    def f(self, x=1):
        return x

class Sub(Base):
    def f(self, x=2):
        return x

class A:
    def g(self, x, y):
        return x - y

class B(A):
    def g(self, y, x):
        return x - y

for o in [Base(), Sub()]:
    print(o.f(5))  # no warning
    print(o.f())

for p in [A(), B()]:
    print(p.g(1, 2))  # no warning
    print(p.g(x=1, y=2))

#*WARNING* 100.py:21: overriding methods have different defaults/parameter order
#*WARNING* 100.py:25: overriding methods have different defaults/parameter order
