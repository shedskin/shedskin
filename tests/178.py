
# --- more aug assignment
f = -112
print f
f /= -3
print f, f / -3
f %= -3
print f
f //= -1
print f

d={}

somme = 9.0
i=4
j=5

d[i,j] = 3.0
d[i,j] += somme
d[i,j] *= somme
d[i,j] /= somme

print d

e = {}
e[i,j] = -7
e[i,j] /= -2
e[i,j] *= -2
e[i,j] %= -2
e[i,j] //= -2

print e

# --- tests these for once
print max([1])
print max(1, 2)
print max(7.7, 7)
print max(7, 7.7)
print max(1, 2, 3)
print max(1, 2, 3, 4, 5)

print min([1])
print min(1, 2)
print min(6.7, 7)
print min(7, 6.7)
print min(1, 2, 3)
print min(1, 2, 3, 4, 5)

# --- virtual test case 1
class Z:
    def boink(self, a):
        pass

    def beh(self):
        print self.boink(9)

class Y(Z):
    def boink(self, a):
        return a

y = Y()
y.beh()

# --- virtual test case 2
class C:
    def boink(self):
        print 'C'

class D(C):
    pass

class A(C):
    def boink(self):
        print 'A'

class B(C):
    pass

c = D()
c.boink()

b = B()
b = A()
b.boink()

# --- virtual case 3
class CC:
    pass

class AA(CC):
    def __init__(self):
        self.a = 4

class BB(CC):
    def __init__(self):
        self.a = 5

cc = AA()
cc = BB()
print cc.a

# --- just in case
this = 1


