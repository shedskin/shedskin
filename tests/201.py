# unpacking negative integers
import struct
s = struct.pack('h', -12)
xx, = struct.unpack('h', s)
print xx
s = struct.pack('i', -13)
xx, = struct.unpack('i', s)
print xx
s = struct.pack('l', -14)
xx, = struct.unpack('l', s)

# block comment fix
print xx
print "hi there"

#{ comment here ok

# nothing

#} not ok

print "hi there 3"

# virtual function: merge parent as well

class X:
   def __str__(self):
       return 'X'

class Y(X):
   def __str__(self):
       return 'Y'

class A:
    def woef(self, l):
        print l

class B(A):
    def woef(self, l):
        print l

x = A()
x.woef(X())

y = A()
y = B()
y.woef(Y())

# using builtin names
class meuh:
    def set(self, x):
        self.x = x
    def filter(self, x):
        self.x = x
    def array(self, x):
        self.x = x

mmm = meuh()
mmm.set(8)
mmm.filter(8)
mmm.array(8)
print mmm.x

# class passing is not supported, but at least we shouldn't crash on this
class wowf:
    pass

x = wowf
x

# type inference bug uncovered by C64 SVN (list type is left unsplit)
class BRKHandler:
    pass

class Tape(BRKHandler):
    pass
    
class IECMember(BRKHandler):
    pass
    
class ComputerDevice(IECMember):
    pass

def wop(a, b):
    t = Tape()
    c = ComputerDevice()
    hooks = [t, c]
    x, y = 1, 1.0
    y = 1.0
    blah = [x, y]

bla = Tape()
bla = IECMember()
bla = ComputerDevice()

wop(bla, bla)

# default args and inheritance
class Alpha:
    def func(self, value=True):
        print("value is:" + str(value))

class Beta(Alpha):
    pass

beta = Beta()
beta.func();

# changing list while iterating over it..
testdellastelem = []
testdellastelem.append("test1")
testdellastelem.append("test2")
testdellastelem.append("test3")
for v in testdellastelem:
  if (v == "test3"):
    testdellastelem.remove("test3")
print testdellastelem
testdellastelem = []
testdellastelem.append("test1")
testdellastelem.append("test2")
testdellastelem.append("test3")
for v in testdellastelem:
  if (v == "test2"):
    testdellastelem.remove("test3")
print testdellastelem
testdellastelem = []
testdellastelem.append("test1")
testdellastelem.append("test2")
testdellastelem.append("test3")
for v in testdellastelem:
  if (v == "test2"):
    testdellastelem.remove("test1")
print testdellastelem

# global declaration ignored
day = 0
def wopp():
    global day
    for day in range(3):
        print day
wopp()
print day

