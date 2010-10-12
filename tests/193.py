
# __init__ not called
from testdata import Material

# ugly imports
from testdata.bert import *
print os.getcwd(), len(sys.argv)

# isinstance problem
from testdata.bert import zeug
print isinstance(zeug(), zeug)

# dict corruption
x = 62
S = {}
t2 = (-25,9)
for i in range(-x, x+1):
   for j in range(-x, x+1):
       S[i, j] = 'hi'
if t2 in S:
    print "we got 'em"

# cast subtype in container
class Bla:
    pass
class Sub(Bla):
    pass
blas = [Bla()]
blas = [Sub()]

# generator and FAST_FOR_NEG
def gen(s):
    for i in range(1,10,s):
        yield i

for i in gen(2):
    print i

# argument unpacking
def blah((a,(b,c)), d):
    print a, b, c, d
t1 = (4, (3,2))
t2 = (7,8)
blah(t1, 1)
blah((1, (2,3)), 4)
blah((6,t2), 9)

class Oink:
    def __getitem__(self, (x,y)):
        print 'get', x, y
        return x*y
    def __setitem__(self, (x,y), z):
        print 'set', x, y, z
oink = Oink()
oink[4,5] = oink[2,3]
oink[t2] = oink[t2]
