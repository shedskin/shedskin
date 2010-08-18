
print 'he\\"'

class A:
    def __init__(self):
        pass

a = A()
a.__init__()

class B:
    def __init__(self, n):
        print 'b init with', n

    def huhu(self):
        self.__init__(4)

b = B(5)
b.huhu()

class C:
    def __init__(self):
        pass

c = C()


# Probably simpler OOP problems
class Pet:
    def speak(self): pass
class Cat(Pet):
    def speak(self): print "meow!"
class Dog(Pet):
    def speak(self): print "woof!"
def command(pet): pet.speak()
pets = Cat(), Dog()
for pet in pets: command(pet)
for pet in (pets[1], pets[0]): command(pet)

clearCastlingOpportunities = [None]
clearCastlingOpportunities[0] = (10,)

board = [1,2,3]
board[0] = 0

print clearCastlingOpportunities, board

print range(-17, -120, -17)

v = -1
w = 4

for x in range(w,-2,v):
    print x

for x in range(w+1,-2,2*v):
    print x

for x in range(0,w+1,1):
    print x

d = [i for i in xrange(10)]
print d
d[::2] = [1,2,3,4,5]
print d
d[::-2] = range(5)
print d

e = ["X" for i in xrange(10)]
e[::2] = "abcde"
print e

f = ["Y" for i in xrange(10)]
f[1::2] = tuple("abcde")
print f

def sgn(x):
    if x < 0: return -1
    else: return 1
for j in [-2, -1]:
    print [i for i in xrange(-10*sgn(j), -1*sgn(j), j) if True for k in range(2) if k]


