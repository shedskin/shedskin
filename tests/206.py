# -*- coding: utf-8 -*-
from __future__ import print_function

# check bounds after wrapping..
alist = range(5)
for i in range(-10,10):
    try:
        print(alist[i], i)
    except IndexError:
        print('nope', i)
try:
    print([][-1])
except IndexError:
    print('nope..')

# fix examples/Gh0stenstein
px = 0xff << 24
print (px == 0xff000000)

# some datetime tests
import datetime
print(datetime.datetime.today().date())
print(datetime.datetime.utcnow().date())

# float(str) inf
bignumstr = '1' + 500 * '0'
print(float(bignumstr))

# optimize: for .. in enumerate(str)
for ix, ex in enumerate('poehee'):
    print(ix, ex)

# optimize: name in (expr, expr, ..)
z = 12
print(z in (10,12,14))
print(z not in (7,8,9))
z = 8
print(z in (10,12,14))
print(z not in (7,8,9))

# different output in python3
a = set([1,2])                           # [Set(int)]
a.add(3)                                 # []
print(a)                                  # [Set(int)]

gs = frozenset([1])
h = {}
h[gs] = 4
print(h)

def mapp():
    allchr = [chr(c) for c in range(256)]
    return allchr
print(mapp()[-10:])

ar = list(range(10))
ar.__delslice__(1,4)
print(ar)

class ueuk(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return 'x'
    def __repr__(self):
        return 'ueukrepr!'

try:
    raise ueuk('aha! error.')
except ueuk as errx:
    print(errx)

# TODO
# __div__ -> __truediv__, __floordiv__

import string
print(string.join(['hello', 'world!']), string.join(['hello', 'world!'], '_'))

# empty set?
blah2 = set([])
print(blah2)

print(repr(''.join([chr(i) for i in range(256)])))

b = [1,2,3]
g = iter(b)
for _ in range(5):
    print(next(g, -1))
print()

# --- end-of-file problem
print([line for line in open('testdata/scene.txt') if line.startswith('material')])

# TODO str.join etc?

# --- slice assignment (random test)
#import random
#random.seed(10)
#
#for x in range(1000):
#    l,u,s = random.randrange(-5,5), random.randrange(-5,5), random.randrange(-5,5)
#    a = list(range(5))
#    print(a, 'lower', l, 'upper', u, 'step', s)
#    try:
#        z = list(range(random.randrange(0,5)))
#        print('xrange', z)
#        a[l:u:s] = z
#        print('done', a)
#    except ValueError as v:
#        print(v)

# --- use %.12g to print floats
print(1/3.0, 1.1234123412341234, 1.1, 8.0)
#print 9.12341234e20 # XXX difference on win, e020?

# string.maketrans
import string
si = 'abcde'
trans = string.maketrans('abc', 'xyz')
print(si.translate(trans))

# --- str.translate problem
import string
atable = string.maketrans("bc", "ef")
print('abcdeg'.translate(atable, "cde"))
gtable = string.maketrans("", "")
word = 'aachen\n'
key = word.translate(gtable, "a\n")
print('word', repr(word))

# --- string.{capitalize, capwords, swapcase, center, atoi, atol, atof}
print(string.capitalize('hoi'), ' hoi'.capitalize())
print(string.capwords('yo   momma')+'!'+string.capwords(' yo momma ')+'!'+string.capwords(' yo momma ', 'mm')+'!')
allchars = ''.join([chr(cx) for cx in range(256)])
print(repr(allchars.swapcase()), repr(string.swapcase(allchars)))
print(string.center('hoi', 10), string.center('hoi', 10, 'u'))
print('hoi'.center(10, 'u'))
for i in range(10):
    print('!'+'hoi'.center(i)+'!')
print(string.atoi('+0x10', 0), string.atol('-100l', 0), string.atof('-1.234'))

#multidir fixes
from testdata import crap
print(crap.incrap())
import testdata.bert180 as bert
print(bert.hello(1))
from testdata import crap2
crap2.incrap2()
import testdata.crap2
tc2c2 = testdata.crap2.crap2()

# sorted, list.sort: cmp and reverse args
def mut(a,b):
    return -cmp(a,b)

def cmut(a,b):
    return -cmp(a,b)

print(sorted([5,1,3,2,4]))
print(sorted([5,1,3,2,4], reverse=True))
print(sorted([5,1,3,2,4], cmp=mut))
print(sorted([5,1,3,2,4], cmp=mut, reverse=True))

print(sorted(set([5,1,3,2,4])))
print(sorted(set([5,1,3,2,4]), reverse=True))
print(sorted(set([5,1,3,2,4]), cmp=mut))
print(sorted(set([5,1,3,2,4]), cmp=mut, reverse=True))

print(sorted('abcde'))
print(sorted('abcde', reverse=True))
print(sorted('abcde', cmp=cmut))
print(sorted('abcde', cmp=cmut, reverse=True))

ls = [1,4,5,2,3]
ls.sort(); print(ls)
ls.sort(cmp=mut); print(ls)
ls.sort(reverse=True); print(ls)
ls.sort(cmp=mut, reverse=True); print(ls)

# oct
print(oct(1==2), oct(1!=2))
print(oct(200), oct(-200), oct(0))

print(repr('\377ai\37aoi\001123\00hoi\01hoi\0hoi'))
print(repr(string.whitespace))

#int(), float(), str(); test all
print(int(), float(), list(), dict(), set(), tuple(), frozenset(),) # XXX repr(str())

# range segfault
broken_range = range(3,0,1)
print(list(broken_range))

# now iterators: dict_items, dict_keys, dict_values..
print({1:2}.items())

# print(.. end=..)
