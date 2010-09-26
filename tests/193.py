
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
