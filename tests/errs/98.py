# 1021-D1: no bogus warning for x.f() when the receiver can also be None
class A:
    count = 3
    def f(self):
        return 1

class B(A):
    def f(self):
        return super().f() + 1

def pick(xs):
    best = None
    for x in xs:
        if best is None or x.f() > best.f():
            best = x
    return best

print(pick([A(), B()]).f())
print(pick([A()]).count)

#*WARNING* 98.py:19: class attribute 'count' accessed without using class name
