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

# cStringIO.StringIO, file.seek
import cStringIO, sys

sio = cStringIO.StringIO(open('testdata/hopsakee').read())
print(sio.readlines())

sio = cStringIO.StringIO('blaat')
sio.seek(-3, 2)
print(sio.read())

sio = cStringIO.StringIO()
print(sio.tell())
sio.write('hallo\njoh')
print(sio.tell())
sio.seek(0, 0)
print(sio.tell())
print(sio.readlines())
print(sio.tell())
sio.seek(0, 0)
print(sio.tell())
sio.write('hoi')
print(sio.tell())
print(sio.readlines())
print(sio.tell())

blah2 = set([])

print(repr(''.join([chr(i) for i in range(256)])))

b = [1,2,3]
g = iter(b)
for _ in range(5):
    print(next(g, -1))
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
trans = string.maketrans('abc', 'xyz')
print(si.translate(trans))

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

# os.path.walk
from os.path import walk
def bleh(arg, top, names):
    pass
def bleh2(arg, top, names):
    pass
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
print(open('run.py').next().strip())

#backticks, scalar
ahh = 19
hoi = 'hoi'
print(`18`, `ahh+1`, `hoi`)

from sys import maxint as MAXINT
from sys import maxsize as MAXSIZE
maxint = MAXINT
maxsize = MAXSIZE
print(maxint == maxsize)

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

import csv
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


print('hello\0world')

# filter, map, zip -> no lists anymore!!! (see removed itertools.ifilter/imap/izip?)

collector = set()
collector.add(frozenset([1,2]))
collector.add(frozenset([1,2,3]))
print(sorted(collector))

# late binding
from testdata import board
from testdata import piece
piece.latebinding()

# {IOError, OSError}.{errno, strerror}
try :
    print("Try block")
    fd = open("nosuchfile") # open will fail
    print("File opened")
except IOError as errr:
    print(errr, repr(errr))
    print(errr.errno, errr.strerror, errr.filename)
#import os XXX fix under windows
#try:
#    os.chdir('meuheuheu')
#except OSError as e2:
#    print e2, repr(e2)
#    print e2.errno, e2.strerror, e2.filename

# char_cache out of bounds
for nnn in '"\xd8\xc3A~s':
    print(repr(nnn))

# different length args to map
def hoppa2(a, b):
    if b: return a+b
    return a+'X'
print(list(map(hoppa2, 'banaan', 'aap')))

def hoppa3(a, b):
    if b: return a+b
    return a
print(list(map(hoppa3, range(8), range(4))))

print(list(map(max, ['a','bc'], ['d'], ['e'])))

print(list(map(set, [[1]])))

# hashing
print(hash(-1))
print(hash(True))
print(hash(12.345))

# open('U')
# MAC
with open('cr.txt', 'w') as f1:
    f1.write('hello world\r')
    f1.write('bye\r')
with open('cr.txt', 'r') as f1:
    for line in f1:
        print(line,)
print('---')
with open('cr.txt', 'rU') as f1:
    for line in f1:
        print(line,)
print('===')

# UNIX
with open('lf.txt', 'w') as f1:
    f1.write('hello world\n')
    f1.write('bye\n')
with open('lf.txt', 'r') as f1:
    for line in f1:
        print(line,)
print('---')
with open('lf.txt', 'rU') as f1:
    for line in f1:
        print(line,)
print('===')

##  DOS
with open('crlf.txt', 'w') as f1:
    f1.write('hello world\r\n')
    f1.write('bye\r\n')
    f1.write('foo\r')
    f1.write('bar\n')
    f1.write('baz\r\n')
    f1.write('qux')
with open('crlf.txt', 'r') as f1:
    for line in f1:
        print('%r' % line,)
print('---')
with open('crlf.txt', 'rU') as f1:
    for line in f1:
        print('%r' % line,)
print('===')

#generator and arg unpacking
def genpack((i,j),a,b):
    yield i
    yield j
    yield a
    yield b
ttt = (1,2)
for aaa in genpack(ttt,3,4):
    print(aaa)

# exception printing
valeur = ValueError('valeur')
print(valeur)
print(repr(valeur))
#print(valeur.message)
print(valeur.__class__.__name__)

# ConfigParser.items model
import ConfigParser
p = ConfigParser.ConfigParser()
p.read("testdata/symbols.INI")
for entry in p.items("symbols"):
    print(entry)
itemz = p.defaults().items()
print(itemz)
sections = p.sections()
print(sections)

# qualify & add include for class name
from testdata import iec2
from testdata import d1541
IEC = iec2.IECBus()
hop = d1541.D1541(IEC, 8)
print(hop.get_data())

#os.popen2 improvement
import os
child_stdin, child_stdout = os.popen2(["echo", "a  text"], "r")
print(repr(child_stdout.read()))
child_stdin, child_stdout = os.popen2(iter(["echo", "a  text"]), "r")
print(repr(child_stdout.read()))
child_stdin, child_stdout = os.popen2(("echo", "a  text"), "r")
print(repr(child_stdout.read()))
child_stdin, child_stdout = os.popen2("echo a  text", "r")
print(repr(child_stdout.read()))

# default print precision?
import math
print(math.cosh(2))
