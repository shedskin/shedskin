
print 'hello, world!'

from random import *
x = 10*random()

from sys import stdin, stdout
for line in sorted(file('testdata/words')):
    print sorted(set(line.strip()))
#stdout.write(stdin.read())

print int('12'), int('ff', 16), int('20', 8)
print '%d %s %x' % (255, '255', 255), '%o' % 10

char = 2
typedef = 3
typename = 4
std = 6
public = 7
template = 8
virtual = 9
static = 10
namespace = 11
using = 12
private = 13
protected = 14
new = 15
delete = 16

t = (1,2)
t2 = (1.0,2)

""" "\n\t" """
print """ "\n\t" """

print set({1:2})
aa = set()
aa.add(1); aa.add(2)
print aa.union(set([1,3]))

l = [1,2,3]
if l: print l
while l: print l.pop()

a, b = "ab"
print a, b
a, b, c, d, e = "abcde"
print a, b, c, d, e
a, b = tuple("ab")
print a, b
a, b, c, d, e = tuple("abcde")
print a, b, c, d, e

print max({1:2, 3:4})

s1 = set([1,2,3])
s2 = set([3,4,5])
print str(s1.copy())+' - '+str(s2.copy())+' =', s1.difference(s2), '=', s1 - s2
s1.difference_update(s2)
s2.clear()
print s1, s2
s1.remove(1)
s1.discard(2)
print s1, s1.issubset(s2), set([2,1]).issubset(set([3,1,2,4]))
s1.update(set([1,2]))
print s1.issuperset(set([1]))

af = set([1,2,3])
print af.intersection(s1)
af.intersection_update(s1)
print af

s3 = set([3,2,1])
while s3: print s3.pop()


s6 = set(["a", "b", "c"])

assert not s6.isdisjoint(s6)
assert not s6.isdisjoint(["a"])
assert s6.isdisjoint(["d"])

import random as rr
from random import randint as ri
#print rr.randint(0,0), rr.randint(0,2), ri(8, 12)

def union(): pass
union()

for (i,ee) in reversed(list(enumerate(reversed([1,2,3])))):
    print i, ee

print set([1,2,3]).symmetric_difference(set([2,3,4]))

###################################################################
sa1 = set([1,2,3])
sa2 = set([3,4,5])
sa3 = set([4,5,6])

assert sa1.difference(sa2) == set([1, 2])
assert sa1.difference(sa3) == sa1
assert sa1.difference([1, 2, 3]) == set([])
assert sa2.difference([4, 5, 6]) == set([3])

assert sa1.intersection([4, 5, 6]) == set([])
assert sa1.intersection([3, 4, 5, 6]) == set([3])

sa4 = set(["a", "b", "d"])
sa5 = set(["d", "e", "f"])

assert sa4.intersection(sa5) == sa4.intersection(["d", "e", "f"])
###################################################################

print {1:2, 2:3}.copy()

ff = file('testdata/bla','w')
print >>ff, 'niet op scherm'
print >>file('testdata/bla2','w'), 'huhuhu'

ss = "abcdefghijklmnopqrst"; print ss[2:9:2]
mm = [""]; print ["*" for c in mm if c]

print "yxxy".split("x")
print "   ".split(" ")
print "hopplop".split("op")
print "x\t\nxxx\r".split()

class CNF:
    def CNF(self):
        print 'CNF'

cnf = CNF()
cnf.CNF()

class Tester:
    def __init__(self):
        self.data = None
    def isempty(self):
        return self.data is None

Tester().isempty()

class void:
    def bla(self): pass
vv = void(); vv.bla()

def mapp():
    allchr = [chr(c) for c in xrange(256)]
    return allchr
print mapp()[-10:]

ap = set([1])
bp = set([2])
print ap > bp, ap >= bp, ap == bp, ap != bp, [2,3] <= [1,2,3]
print sorted([[3],[2,1],[4,5,6]])

class Test:
    def __init__(self):
        self.n = 5
        print [i for i in range(self.n)]
test = Test()

print sum([1,2,3])
print sum([1,2,3],4)
print sum([[1],[2],[3,4]], [0])
print sum([[1],[2],[3,4]], [])

print dict.fromkeys([1,2,3])
print dict.fromkeys([1,2,3])

print dict.fromkeys([1,2,3], 7)
print dict.fromkeys([1,2,3], 4.0)
print dict.fromkeys([1,2,3], 'string')

if 4 > 2 > 1:
    print 'hoihoi'
print 1 <= 2 == 2
if 1<2: print '1<2'

class fred:
    def __eq__(self, b):
        return True
fr = fred()

if fr == fr:
    print 'fred = fred'
# the following line should give a warning
if fr == fr == fr:
    print 'fred = fred = fred'

mmt = mma, mmb = 3, 4
print mmt, mma, mmb

mmc = mmd = mme = 1
print mmc, mmd, mme

mmf = mmg = mmh = 9*mma
print mmf, mmg, mmh

mma = 9
from math import sqrt
mmi = mmj = sqrt(mma)
print int(mmi), int(mmj)

mma, mmb = mmb, mma
print mma, mmb

mma, mmb = 1, 2
print mma, mmb

mmt = 1, 2
mma, mmb = mmt
print mmt, mma, mmb

mma,mmb = mmt = mmc,mmd = 1,2
print mma, mmb

mma, mmb = mmb, mma = 1, 2
print mma, mmb

meuk = [1,2]
mma, mmb = meuk
print mma, mmb

mmx = [1,2]
print mmx


from sys import exit
exit()
exit(-1)

