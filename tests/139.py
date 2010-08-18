
def gen():
    m = []
    l = [1]
    m.append(l)

    return m

m = gen()
print m

z=1 and 1

a = range(10)
a.__delslice__(1,4)
print a

import copy

b=[[0,1]]

c=copy.deepcopy(b)
c[0].pop(0)

print c, b

AH = [1,2]
print [[1 for x in AH] for y in AH]

for x in xrange(2,1,-1):
    print x

print []*10

a = range(5); del a[0:2]; print a

class Individual:
    def __init__(self, ngenes): self.genome = [True] * ngenes
individual = Individual(3)
individual.genome[1] = not individual.genome[1]
print individual.genome

#d,e = -1e500, 1e500; print d, e

if not (1==2 or 2==3):
    print 'jammer'

class wahoe:
    def hoe(self):
        for self.smurf in range(3):
            print self.smurf

wahoe().hoe()

def fun():
    global aa
    aa += 1
    return 200
aa = 1
print aa
print 97 <= fun() <= 122
print aa
print 200 == fun() == 150
print aa

def true(): return True

print true() == true() in [True]
print 1 < 2 < 3 < 4

print 'hash(l)', [hash(i) for i in xrange(3)]
#print 'hash(float(l))', [hash(float(i)) for i in xrange(3)] XXX difference
[hash(float(i)) for i in xrange(3)]

class Toggle:
    def __init__(self, start_state):
        self.bool = start_state
    def value(self):
        return(self.bool)
    def activate(self):
        self.bool = not self.bool
        return(self)
t = Toggle(True)
print t.value()
t.activate()
print t.value()

print [None for i in xrange(3)]

maxint = 2147483647
minint = -maxint-1
print maxint
print minint

s1 = set((1,2,3)); s4 = set([1,4]); print s4 > s1, s4 >= s1

#python 2.4
#print set([1,2,3]).issubset((1,2,3))
#print set([1,2,3]).issuperset((1,2,3))

s1 = set((1,2,3)); s2 = set([1,4]); print sorted(set((1,2,3)) & set([1,4]))
s1 = set((1,2,3)); s2 = set([1,4]); s3 = set([5]); print sorted(s1 | s2 | s3) # associativity
print sorted(set([1,2]).union((2,)).union([3]))
s5 = set("abcd"); s6 = set("cdef"); print sorted(s5 ^ s6) # mixing
print

s1 &= s2
print sorted(s2)
s1 -= s2
print sorted(s1)
s1 ^= s2
print sorted(s1)

s7 = set([(1,2),(1,3),(1,4)])
s7 |= set([(1,6)]) # not (1,6)
print sorted(s7)

ah = [(2.1, 4), (1.0, 9), (1.0, 7)]
ah.sort()
print ['%.2f %d' % trt for trt in ah]

p, q, r = set('ab'), set('abcde'), set('def')
print q <= q, q > r, q >= r

y = ("a", "b", "c")
zed = "a"
print zed is y[0]

class Printer:
    def __str__(self): return "10"
    def __repr__(self): return "20"
pr = Printer(); print Printer(), pr, repr(pr)

class Printer2:
    def __repr__(self): return "20"
print Printer2(), repr(Printer2())

class Printer3:
    pass

#print Printer3()

def test(): pass
print test()

l = []; print [l.append(i%2) for i in xrange(5)]

def test2(x):
    if x:
        return (1,"a")
print test2(1)
print test2(0)

uh = [1]
uh = None
print uh

def fun3(): a = 1
result = fun3()
print result

s = dict.fromkeys(xrange(2))
for i in xrange(2):
    if i in s: print "*"

b2 = 3; b2 *= 1.5; print '%.1f' % b2

class A:
  def __init__(self, a): self.a = a
  def __add__(self, V): return A(self.a+V.a)
  def __mul__(self, n): return A(self.a*n)

v = A(1); v += A(2); print v.a
v = A(1) + A(2); print v.a
print (v * 2).a
v *= 2; print v.a

def mut1(aap=[1]):
    aap.append(2)
    print aap
mut1(); mut1(); mut1()

def mut2(a=None):
    if a is None:
        a = []
    print a
    a.append("*")
mut2(); mut2(); mut2()

def fun2(a, b=4, c='1'):
    return (a+b)*c
print fun2(c='2', a=3, b=4), fun2(a=1, b=2, c='8')

def fun4(a, b=7, c='1', d=1, e=1.0):
    print a, b, c, d, int(e)

fun4(1,2,e=2.0,c='8')


