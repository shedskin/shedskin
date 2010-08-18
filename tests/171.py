
# --- math.pow
import math
print int(math.pow(2,3))
print pow(2.0,3.0)
print pow(2,3.0)
print pow(2.0,3)
print pow(2,3)
print pow(1000,1000,1234)

# --- end-of-file problem
print [l for l in file('testdata/scene.txt') if l.startswith('material')]

# --- append '.0' when printing 'integer' floats (but not in case of %g!)
print 8.0, '%g' % 8.0

# --- iterators
b = [1,2,3]
for a in b:
    print a,
print
print [a for a in b]

g = iter(b)
for x in range(3):
    print g.next(),
print
print [n for n in iter(b)]

h = iter(b)
e = iter(h)
for f in e:
    print f,
print

i = [1,2,3]
i = iter(i)
i = [1,2,3]

for j in i:
    print j,
print

print [j for j in i]

print [y for y in 'stroop']
print [n for n in {1: '1', 2: '2', 3: '3'}]
print [z for z in [[1],[2],[3]]]
print sorted([m for m in set([1.0,2.0,3.0])])
print [l for l in file('testdata/hoppa')]

# --- generators

def blah(a):
    while a > 0:
        yield a
        yield 17
        a -= 1

hop = blah(3)
for x in range(4):
    print hop.next(),
print
hop = blah(1)
try:
    for x in range(4):
        print hop.next(),
    print
except StopIteration:
    print 'klaar.'

# --- verify some things still work
import os.path
print os.path.split('hoempa/nohu')
import math
print '%g' % math.log(10)

# --- % revisited
print -2 % 3
print 2 % 3
print math.fmod(-2.0, 3)
print -2.0 % 3
print 4 % 3
print 4 % 3.0
print math.fmod(2.0, -3)
print -2.0 % -3
print -2.0 % -3.0
print 2.0 % -3.0
print '%g' % 3.0

# --- and/or revisited
print 0 or 5 or 4
print 0 or 0
print 1 > 2 or 3 < 4
ax = [1]
ax = []
bx = [2]
print ax or bx
print [0,1][(ax or None) is None]
print bx or None
print None or bx
print 1 and 4, 4 and 1
print bx and []

def ef(x):
    print 'hah', x
    return 0
ef(5) and ef(6)

# --- allow mixing when result is not used
n = 1
n < 0 or bx
bx and n > 1

# --- make this compile (XXX we shouldn't implicitly call parent constructors though)
class smurf:
    def __init__(self, a=-1):
        print 'hallo', a

class baviaan(smurf):
    def __init__(self, a=-1):
        print 'oehoehoe', a

smurf()
baviaan()

# --- simple itertools functions
#import itertools
#gg = itertools.count()
#print [gg.next() for i in range(10)]
#
#cycle = itertools.cycle(range(3))
#print [cycle.next() for i in range(10)]
#
#repeat = itertools.repeat([1,2,3], 10)
#print [repeat.next() for i in range(3)]

# --- xrange, enumerate, reversed as iterators
ah = xrange(10)
for x in ah: print x,
print
ah = xrange(0,10,3)
for x in ah: print x,
print
ah = xrange(10,0,-3)
for x in ah: print x,
print

bh = enumerate(xrange(10,0,-3))
print [y for y in bh]
ch = enumerate([(1.0, 's') for x in range(4)])
print [z for z in ch]

print [zz for zz in reversed(range(10))]
print [zzz for zzz in reversed(xrange(10))]

# --- dict.{iterkeys, itervalues, iteritems}
waa = {1: '2', 2: '4'}

for wax in waa.iterkeys():
    print wax,
print
for way in waa.itervalues():
    print way,
print
for wat in waa.iteritems():
    print wat,
print


