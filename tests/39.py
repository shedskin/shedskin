
import testdata.bert
from testdata.bert import hello, zeug
#from sets import Set

class jurk:
    pass

testdata.bert.hello(4)                            # []
hello(4)                                 # [str]

s2 = jurk()                              # [jurk()]

s4 = set()                               # [Set(float)]
s4.add(1.0)                              # []
s3 = set([1,2,3])                        # [Set(int)]

kn = testdata.bert.zeug()                         # [zeug()]
kn.hallo(4)                              # []

l1 = lambda x,y: x+y                     # [lambda0]
l2 = lambda x,y: x-y                     # [lambda0]
l5 = l2                                  # [lambda0]
l3 = lambda x,y: 1.0                     # [lambda1]
def l4(x, y): return x*y                 # [int]

def toepas(l):                           # l: [lambda0]
    return l(1,2)                        # [int]

print toepas(l1)                         # [int]
print toepas(l5)                         # [int]
print l3(1.0, 'hoi')                     # [float]
a = l4                                   # [lambda0]
a(3,3)                                   # [int]
print toepas(a)                          # [int]

