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

# unicode basics  # TODO non-ascii so run.py doesn't work
ss = u'\u91cf\u5b50\u529b\u5b66'
print(repr(ss))  #, s
t = ss.encode('utf-8')
print(repr(t))  #, t
u = t.decode('utf-8')
print(repr(u))  #, u
l = [ss, u]
print(l)
print(repr(ss[1]))  #, s[1]
print(len(ss))

# some datetime tests
import datetime
print(datetime.datetime.today().date())
print(datetime.datetime.utcnow().date())

# float(str) inf
bignumstr = '1' + 500 * '0'
print(float(bignumstr))

# optimize: for .. in enumerate(str)
for i, e in enumerate('poehee'):
    print(i, e)

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

g = frozenset([1])
h = {}
h[g] = 4
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
except ueuk as x:
    print(x)

# TODO
# __div__ -> __truediv__, __floordiv__

import string
print(string.join(['hello', 'world!']), string.join(['hello', 'world!'], '_'))

# cStringIO.StringIO, file.seek
import cStringIO, sys

s = cStringIO.StringIO(open('testdata/hopsakee').read())
print(s.readlines())

s = cStringIO.StringIO('blaat')
s.seek(-3, 2)
print(s.read())

s = cStringIO.StringIO()
print(s.tell())
s.write('hallo\njoh')
print(s.tell())
s.seek(0, 0)
print(s.tell())
print(s.readlines())
print(s.tell())
s.seek(0, 0)
print(s.tell())
s.write('hoi')
print(s.tell())
print(s.readlines())
print(s.tell())
blah = set([])

print(repr(''.join([chr(i) for i in range(256)])))

b = [1,2,3]
g = iter(b)
for x in range(5):
    print(next(g),)  # TODO fillvalue modeling
print()

# --- end-of-file problem
print([l for l in open('testdata/scene.txt') if l.startswith('material')])

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
t1 = string.maketrans('abc', 'xyz')
print(si.translate(t1))

# reversed(range)
import random
random.seed(1)

for z in range(1000):
    l,u,s = random.randrange(-5,5), random.randrange(-5,5), random.randrange(-5,5)
    print(l, u, s)

    try:
        x = range(l,u,s)
        y = reversed(range(l,u,s))

        xl = [e for e in x]
        yl = [e for e in y]

        print(xl, yl, [0, 1][xl == list(reversed(yl))])

    except ValueError as v:
        print(v)

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
allchars = ''.join([chr(x) for x in range(256)])
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

l = [1,4,5,2,3]
l.sort(); print(l)
l.sort(cmp=mut); print(l)
l.sort(reverse=True); print(l)
l.sort(cmp=mut, reverse=True); print(l)


print(oct(1==2), oct(1!=2))

walk('testdata', bleh, 77)
walk('testdata', bleh2, 'hoei')

print(repr('\377ai\37aoi\001123\00hoi\01hoi\0hoi'))
print(repr(string.whitespace))

#int(), float(), str(); test all
print(int(), float(), list(), dict(), set(), tuple(), frozenset(),) # XXX repr(str())

from collections import defaultdict
s3 = [('red', 1), ('blue', 2), ('red', 3), ('blue', 4), ('red', 1), ('blue', 4)]
d3 = defaultdict(set)
for k3, v3 in s3:
    d3[k3].add(v3)

print(sorted(d3.items()))

#ConfigParser # XXX readfp
import ConfigParser

config = ConfigParser.ConfigParser(defaults={'aha': 'hah'})

config.read("testdata/test.conf")

print(config.getint('ematter', 'pages'), config.getfloat('ematter', 'pages'))
print(int(config.getboolean('ematter', 'hop')))

print(int(config.has_section('ematteu')))
config.add_section('meuk')
config.set('meuk', 'submeuk1', 'oi')
config.set('meuk', 'submeuk2', 'bwah')
if config.has_section('meuk') and config.has_option('meuk', 'submeuk1'):
    config.remove_option('meuk', 'submeuk1')
config.add_section('bagger')
config.remove_section('bagger')

# dump entire config file
for section in sorted(config.sections()):
    print(section)
    for option in sorted(config.options(section)):
        print(" ", option, "=", config.get(section, option))

print(config.get('ematter', 'pages', vars={'var': 'blah'}))

fl = open('testdata/test.ini', 'w')
config.write(fl)
fl.close()
print(sorted(open('testdata/test.ini').readlines()))

print(config.defaults().items())
print(sorted(config.items('ematter', vars={'var': 'blah'})))

rcp = ConfigParser.RawConfigParser()
rcp.read(["testdata/test.conf"])

print(rcp.get('ematter', 'pages')) #, vars={'var': 'blah'})
print(sorted(rcp.items('ematter')))

# file.next
print(next(open('run.py')).strip())

#backticks, scalar
ahh = 19
hoi = 'hoi'
print(`18`, `ahh+1`, `hoi`)

from sys import maxint as MAXINT
from sys import maxsize as MAXSIZE
a = MAXINT
bb = MAXSIZE
print(a == bb)

#bisect should model __cmp__, fix sorting problem
from bisect import insort
class A(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return "A(%s, %s)" % (self.x, self.y)
    def __cmp__(self, other):
        return cmp(self.x + self.y, other.x + other.y)

pairs = [[18, 6], [28, 5], [35, 26], [31, 28], [3, 3], [32, 37], [11, 17], [28, 29]]
items = []
for pair in pairs:
    insort(items, A(pair[0], pair[1]))
print(items)

# TODO with expr1 as bla, expr2..

print(sorted(csv.list_dialects()))

#csv default writer lineterminator?

#    print(math.factorial(hm), end=' ')

# argument unpacking
def blah((a,(b,c)), d):
    print(a, b, c, d)
t1 = (4, (3,2))
t2 = (7,8)
blah(t1, 1)
blah((1, (2,3)), 4)
blah((6,t2), 9)


class Oink:
    def __getitem__(self, (x,y)):
        print('get', x, y)
        return x*y
    def __setitem__(self, (x,y), z):
        print('set', x, y, z)
oink = Oink()
oink[4,5] = oink[2,3]
oink[t2] = oink[t2]

arr2 = array.array('c')
arr2.extend('hoei')
print(arr2.count('h'), arr2.index('h'))
arr2[-1] = 'X'
arr2.insert(0, '-')
arr2.fromlist(['a', 'b'])
print(arr2, arr2.tolist(), arr2.tostring())
print(arr2[0])


initial = (
    '         \n'  #   0 -  9
    '         \n'  #  10 - 19
    ' rnbqkbnr\n'  #  20 - 29
    ' pppppppp\n'  #  30 - 39
    ' ........\n'  #  40 - 49
    ' ........\n'  #  50 - 59
    ' ........\n'  #  60 - 69
    ' ........\n'  #  70 - 79
    ' PPPPPPPP\n'  #  80 - 89
    ' RNBQKBNR\n'  #  90 - 99
    '         \n'  # 100 -109
    '         \n'  # 110 -119
)

def print_pos(board):
    print()
    uni_pieces = {'R':u'♜', 'N':u'♞', 'B':u'♝', 'Q':u'♛', 'K':u'♚', 'P':u'♟',
                  'r':u'♖', 'n':u'♘', 'b':u'♗', 'q':u'♕', 'k':u'♔', 'p':u'♙', '.':u'·'}

    for k in sorted(uni_pieces):
        print(k, uni_pieces[k])

print_pos(initial)

print('hello\0world')

# filter, map -> no lists anymore!!!

collector = set()
collector.add(frozenset([1,2]))
collector.add(frozenset([1,2,3]))
print(sorted(collector))
