
# iter.__len__
print len(xrange(10))

# try.. else
try: print 'probeer'
except Exception: pass
else: print 'geen exceptie..'

# collections
from collections import deque

d = deque([3,2,1])
d.append(4)
d.appendleft(0)

print len(d)

for i in range(len(d)):
    print d[i],
print

print d.pop(), d.popleft()

print d

while d:
    print d
    d.pop()

d = deque([3,2,1])
e = iter(d)
print [x for x in e]

d.extend(set([4,5]))
print d
d.extendleft(set([6,7]))
print d

print sorted(d), [e for e in reversed(d)]

d[2] = d[-2] = 4
print d

print [0,1][4 in d], [0,1][9 in d]

#d.remove(1) # python 2.5
#print d

d.rotate(3)
print d
d.rotate(-2)
print d

d = deque()
print d

d.rotate(1) # no error
print d

d.clear()
print d

d.extend(xrange(10))
del d[-4]
print d

print [e for e in reversed(deque(xrange(10)))]

# bisect
from bisect import *

def blah(s, e):
    print bisect_left(s, e)
    print bisect_left(s, e, 0)
    print bisect_left(s, e, 0, len(s))
    print bisect_right(s, e)
    print bisect(s, e)

    insort_left(s, e)
    insort_right(s, e)
    insort(s, e)
    print s


blah([1,2,3,4,5,6,6,7], 4)
#blah(['1','2','3','4','5','6','7'], '4')

# copy
import copy

kb = [1,2]
ka = copy.copy(kb)
ka.append(3)
print ka, kb, copy.copy(178)

print copy.copy((1, 2)), copy.deepcopy((2, 3))
print copy.copy('1234'), copy.deepcopy('1234')
print copy.copy((1, '1')), copy.deepcopy((1, '1'))
print sorted(copy.copy(set([1, 2]))), sorted(copy.deepcopy(set([1, 2])))
print copy.copy({1 : 1.0}), copy.deepcopy({1.0 : 1})
print copy.copy(deque(range(10))), copy.deepcopy(deque(xrange(10)))

kc = [1,2]
kd = (kc,)
ke = copy.deepcopy(kd)
ke[0][0] = 3
print kd, ke

rll = [1, 2]
bll = [rll, rll]
cll = copy.deepcopy(bll)
cll[0].append(3)
print cll

class bert:
    pass

abert = bert()
abert.a = 7.0

cbert = bert()
cbert.a = 1.0

print abert.a, cbert.a

copy.copy(abert)
copy.deepcopy(abert)

class dert:
    pass

adert = dert()
adert.a = [1,2]

bdert = copy.copy(adert)
bdert = copy.deepcopy(adert)
bdert.a.append(3)

# reversed(xrange)
import random
random.seed(1)

for z in range(1000):
    l,u,s = random.randrange(-5,5), random.randrange(-5,5), random.randrange(-5,5)
    print l, u, s

    try:
        x = xrange(l,u,s)
        y = reversed(xrange(l,u,s))

        xl = [e for e in x]
        yl = [e for e in y]

        print xl, yl, [0, 1][xl == list(reversed(yl))]

    except ValueError, v:
        print v

# for _ in (x)range
total = 0
for _ in range(10):
    for _ in range(10):
        total += 1
print total

print [0 for _ in range(10)]

# remove ifa_empty_constructors
fromage = []
def non_internal(ptree):
    noni = [c for c in ptree]

ptree = [1,2]
row_pointers = [None, ptree]
non_internal(row_pointers[1])

# string.maketrans
import string
si = 'abcde'
t1 = string.maketrans('abc', 'xyz')
print si.translate(t1)

# optimize dict[..] += ..
dd = {}
dd['hoi'] = 0
dd['hoi'] += 10
print dd['hoi']



