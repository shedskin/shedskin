#!/usr/bin/env python

from ss import *
from sets import Set
import traceback, sys, os, time

tests = [

('''fixes for 0.0.29; datetime''', '''
#equality..
hex=['A','B','C','D','E','F']
try:
    print hex.index('A'.upper())
    print hex.count('A'+'')
except Exception, e:
    print e

#datetime
from datetime import date, tzinfo, timedelta, datetime

# enable keyword args
print date(2007,4,3).replace(month=11)

# template problem
class TZ2(tzinfo):
    def utcoffset(self, dt): return timedelta(0,0,0,0,-339)

try:
    dt = datetime(2007,4,3, tzinfo=TZ2())
    print dt
except Exception, e:
    print e

#random.randrange
import random

print random.randrange(1)
print random.randrange(0,1)
print random.randrange(0,1,1)

#staticmethod decorator
class C:
    @staticmethod
    def id(x):
        return x
print C.id(1)

#improve import mechanism
import os.path
print os.getcwd()

from os import path 
print path.curdir

from os.path import curdir
print curdir

import os as os2
print os2.path.curdir

#mod improvements
v = '1 %(aap)s, 1 %(aap)s, %% 2 %(bert)s..' 
d = {'aap': 'aapje', 'bert': 'bertjes'}
print v % d

w = '1 %(aap)s, %% 1 %(aap)d, 2 %(bert)c..' 
f = {'aap': 70, 'bert': 71}
print w % f

t = (70,70,70)
print '1 %s %% %d %c..' % t

t2 = ('x', 71)
print ' %%%c, en %%%c.. huhu' % t2

t3 = (70, 71, 72, 73, 74)
print '%c %d %x %s %r' % t3

t4 = (70.0, 71.0, 72.0, 73.0, 74.0)
v4 = '%c %d %x %s %r' 
print v4 % t4

print '%(aap)s %(bert)d %% %(bert)c' % {'aap': 'hallo', 'bert': 72}

#match_object.group def arg
import re
p = re.compile(r'\d+')
m = p.search('Call 65490 for printing, 49152 for user code.')
print m.group()

#do not special-case __init__
class Error(Exception):
    def __init__(self, x):
        print 'error.__init__', x

class ParsingError(Error):
    pass

class MissingSectionHeaderError(ParsingError):
    def __init__(self):
        print 'missingsectionheadererror.__init__'
        Error.__init__(self, '4')

Error('3')
MissingSectionHeaderError()

#base class not identifier
import testdata.bert as b

class A(b.zeug):
    def hup(self):
        print self.hallo(4)

A().hup()

#property decorator
class huppa:
    @property
    def huppa(self):
        return 28

print huppa().huppa

# inherit from parent first, etc.
class InterpolationError(Exception):
    def __init__(self, option, section):
        print option, section

class InterpolationSyntaxError(InterpolationError):
    pass

InterpolationSyntaxError('a', 'b')

''', '''
output(equal=True)
'''),

('''fixes for 0.0.28; socket''', '''
#time.strptime
import time
print time.strftime("%d %b %Y %H:%M:%S", time.strptime("2001-11-12 18:31:01", "%Y-%m-%d %H:%M:%S")) 
print time.strftime("%Y", time.strptime("2001", "%Y"))

#improve default arguments
import bert
print bert.def1()

print bert.def2()
bert.a = 16
print bert.huh()
print bert.def2()

print bert.def3()

def bleh(l=[1,2]):
    return l
print bleh()

bert.def4()

#C++ bool type 
def h(x):
    if x in ['False', '0']: return 0
    elif x in ['True', '1']: return 1
    else: return 2

print hex(1==2), hex(1!=2)
print oct(1==2), oct(1!=2)
print abs(1==2), abs(1!=2)
print h(str(1==2)), h(str(1!=2))
print h(repr(1==2)), h(repr(1!=2))
print int(1==2), int(1!=2)
print float(1==2), float(1!=2)
print ord(chr(1==2)), ord(chr(1!=2))

#random.sample/choice 
import random
print random.sample(xrange(1), 1)
print random.sample(set([1]), 1)

#fast_for_neg in listcomp_for
print [(i, i) for i in range(29, -1, -1)]

#works, but add as test
def ah():
   pass
def bh(func=ah):
   func()
bh()

# sorted, list.sort: cmp and reverse args 
def mut(a,b):
    return -cmp(a,b)

def cmut(a,b):
    return -cmp(a,b)

print sorted([5,1,3,2,4])
print sorted([5,1,3,2,4], reverse=True)
print sorted([5,1,3,2,4], cmp=mut)
print sorted([5,1,3,2,4], cmp=mut, reverse=True)

print sorted(set([5,1,3,2,4]))
print sorted(set([5,1,3,2,4]), reverse=True)
print sorted(set([5,1,3,2,4]), cmp=mut)
print sorted(set([5,1,3,2,4]), cmp=mut, reverse=True)

print sorted('abcde')
print sorted('abcde', reverse=True)
print sorted('abcde', cmp=cmut)
print sorted('abcde', cmp=cmut, reverse=True)

l = [1,4,5,2,3]
l.sort(); print l
l.sort(cmp=mut); print l
l.sort(reverse=True); print l
l.sort(cmp=mut, reverse=True); print l

# tempvars/new nodes and inheritance (XXX add more here)
class network:
    def shortestpath(self):
        for node in set([1]): 
            print node

        print [node for node in [1]]

class smallworld(network):
    pass

s = smallworld() 
s.shortestpath()

# ss-progs regression
class LowLevel:
   def bslTxRx(self, blkout=None):
       pass

class BootStrapLoader(LowLevel):
   def actionRun(self):
       self.bslTxRx()

bsl = BootStrapLoader()
bsl.actionRun()

# test compilation
import socket
import stat

# test all cases
a = 1

print [x for x in range(1,10,1)]
print [x for x in range(10,1,-1)]
print [x for x in range(1,10,+1)]
print [x for x in range(1,10,a)]
print [x for x in range(10,1,-a)]
print [x for x in range(1,10,+a)]
print [x for x in range(1,10,a*1)]
print [x for x in range(1,10,-(-1))]
print [x for x in range(1,10,+(+a))]

for x in range(1,10,1): print x,
print
for x in range(1,10,+1): print x,
print
for x in range(1,10,a): print x,
print
for x in range(1,10,+a): print x,
print
for x in range(1,10,-(-1)): print x,
print
for x in range(1,10,+(+1)): print x,
print
for x in range(1,10,+(+a)): print x,
print
for x in range(10,1,-1): print x,
print
for x in range(10,1,-a): print x,
print

''', '''
output(equal=True)

'''),

('''fixes for 0.0.27; re, time''', '''
#re
import re

try:
	a = re.compile(r'\\b(?P<email_name>[\\w.-]+?)@(?P<email_domain>[a-z.-]{3,})\\b', re.IGNORECASE)
	b = 'bob (BoB@gmaiL.com) said to sally (sally123_43.d@hOtmail.co.uk) that no-name (not_a-real@em_ail.dres) was annoying...'
	
	print a.search(b, 20).group(0)
	print a.match(b, 5).expand(r'the found name: \\g<email_name>\\nthe domain: \\g<email_domain>')
	print a.subn(r'\\1 AT \\g<email_domain>', b)
	print a.sub(r'<a href="mailto:\\g<0>">\\1</a>', b)
#	print a.findall(b)
	
	c = re.compile(r\'\'\'
		\\b
		(?P<protocol>https?|(ftp)|(?P<mailto>mailto))
		:(?(mailto)|//)
		(
			(?P<user>[\\w._-]+?)
			(?(mailto)
					
				|
					:(?P<pass>[\\w._-]*?)
			)
			@
		)?
		(?P<domain>[\\w.-]+)
		(?(mailto)
				
			|
				(?P<path>/[^\\s]*)
		)
		\\b
		\'\'\', re.X)
	d = 'fasdf mailto:bob@gmail.com, dasdfed ftp://haha:hoho@bla.com/files, http://fsesdf@asd.com orRLY!!?!L!? \\
	https://example.com/OMG.html'
	
	allm = c.finditer(d)
	i = 1
	for mo in allm:
		s = str(i) + ': \\n'
		s += '\\tfull: ' + mo.group(0)
		s += '\\n\\tnamed: '
		
		gd = mo.groupdict()
		for k in sorted(gd):
			if gd[k] == None: continue
			s += '\\n\\t\\t' + k + ': ' + gd[k]
		
		print s
		i += 1
	
	print re.split(r'\\W+', b)
	print re.split(r'(\\W+)', b, 2)
	
except re.error, msg:
	print msg

#time
import time
try:
    print time.mktime(time.struct_time((1970, 2, 17, 23, 33, 34, 1, 48, -1)))
    print time.mktime((1970, 2, 17, 23, 33, 34, 3, 17, -1))
    print time.localtime(4142014)    
#    print time.localtime()
#    print time.localtime(time.mktime(time.localtime()))
#    print time.gmtime(time.mktime(time.gmtime()))
#    print time.asctime()
    print time.asctime(time.struct_time((2008, 6, 24, 12, 50, 00, 0, 120, -1)))
#    print time.ctime()
    print time.ctime(1000000)
    y = (2008, 6, 24, 12, 50, 00, 0, 120, -1)
    x = time.struct_time(y)
    print x
    print x.tm_mon
    print x[6]
#    print time.strftime("%R",time.localtime())
#    print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    print time.strftime("%a, %d %b %Y %H:%M:%S",
            (2008, 6, 24, 12, 50, 00, 0, 120, -1))
#    print time.strftime("%d %b %Y %H:%M:%S", time.strptime("2001-11-12 18:31:01", "%Y-%m-%d %H:%M:%S")) # XXX %a
#    print time.strftime("%Y", time.strptime("2001", "%Y")) # XXX %a
#    print time.timezone
    print time.tzname

except TypeError, e:
    print e

#corner cases
print int(''.isdigit())
print int(''.isalpha())
print int(''.isalnum())
print int(''.islower())
print int(''.isupper())
print int(''.istitle())

#glob, fnmatch
import glob
print glob.glob('ss.py')
import fnmatch
print int(fnmatch.fnmatch('ss.py', 'ss.[py]y'))

#staticmethod, property
class woef(object):
    def x(a):
        print a
    def y(self, b):
        print b

    def getz(self):
        return 15+self._x
    def setz(self, x):
        self._x = x

    x = staticmethod(x)
    z = property(getz, setz)

w = woef()
w.y(4321)
woef.x(1234)

woef.k = 1
woef.k

w.z = 14
print w.z

class base:
    def x():
        return 12

    def gety(self):
        return self.value
    def sety(self, val):
        self.value = val

    x = staticmethod(x)
    y = property(gety, sety)
    z = 21

class der(base):
    pass

print der.x()
derder = der()
derder.y = 99
print derder.y
#print der.z # XXX

#unaryadd
class V:
    def __init__(self, x):
        self.x = x
    def __pos__(self):
        return V(self.x+1)
    def __neg__(self):
        return V(self.x-1)
    def __repr__(self):
        return 'V(%d)' % self.x

v = V(1)
print ++v, +-+-v

#multidir fixes
from testdata import crap
print crap.incrap()
import bert
print bert.hello(1)
from testdata import crap2
crap2.incrap2()
import testdata.crap2
tc2c2 = testdata.crap2.crap2()

#int/double crap
def to_ints(l):
    return [int(x) for x in l]

print to_ints([4.0, 4.0, 61]), to_ints((4.0, 4.0, 61))
print int(min(4.0, 4.0, 2))
print int(max(4.0, 4.0, 6))
print int(min(4.0, 4.0, 4.0, 2))
print int(max(4.0, 4.0, 4, 0, 6))
l = [6]
l.append(1.0)
print to_ints(l)

#assorted fixes
[1] != []

from collections import defaultdict
print sorted(defaultdict.fromkeys(range(7,10), 'a').items())
import collections
print sorted(collections.defaultdict.fromkeys(range(7,10), 'a').items())

from string import *
class string: pass
string.x = 4

''', '''
output(equal=True)

'''),

('''fixes for 0.0.26; os.path, defaultdict''', '''
#simple fixes
print 8+(2 if 1 else 3)
print repr('\\377ai\\37aoi\\001123\\00hoi\\01hoi\\0hoi')

# add_strs()
print 'x'+'x'+'x'

#os.path
import os.path

print os.path.join('heuk')
print os.path.join('heuk', 'emeuk')
print os.path.join('heuk', 'emeuk', 'meuk')

from os.path import *

print join('a','b','c')

realpath('ss.py')
commonprefix(['xxx', 'xxxx'])
normcase('hoei')
splitext('hoei/woei')
splitdrive('hoei/woei')
basename('hoei/woei')
dirname('hoei/woei')
exists('testdata')
lexists('testdata')
isdir('testdata')
isfile('testdata')

def bleh(arg, top, names):
    pass
def bleh2(arg, top, names):
    pass

walk('testdata', bleh, 77)
walk('testdata', bleh2, 'hoei')

getsize('ss.py')
getatime('ss.py')
getctime('ss.py')
getmtime('ss.py')

#locally overloading builtin definition 
str = '4'

t = ('aha', 2)
str, x = t

def heuk(str):
    pass
heuk('aha')

for str in ['hah']:
    pass
[0 for str in ['hah']]

for (str,bah) in [('hah', 'bah')]:
    pass
[0 for (str,bah) in [('hah', 'bah')]]

#missing string methods
print 'ab\\ncd\\r\\nef\\rghi\\n'.splitlines()
print 'ab\\ncd\\r\\nef\\rghi\\n'.splitlines(1)
print int('This Is A Title'.istitle())
print int('This is not a title'.istitle())
print 'a and b and c'.partition('and')
print 'a and b and c'.rpartition('and')

#default argument problem
def msplit(sep=0, spl=-1):
    return ['']

cnf = msplit()

#ctype
import string
print repr(string.lowercase)
print repr(string.uppercase)
print repr(string.letters)
print repr(string.printable)
print repr(string.punctuation)
print repr(string.whitespace)
print repr(string.digits)
print repr(string.hexdigits)
print repr(string.octdigits)

#dict.get problem
print {'wah': 2}.get('aap', 3)

#finish getopt
from getopt import getopt, gnu_getopt

args = ['-ahoei', '--alpha=4', 'meuk']

print getopt(args, "a:b", ["alpha=", "beta"])
print getopt(args, "a:b", {"alpha=" : 0, "beta" : 0})
print gnu_getopt(args, "a:b", ["alpha=", "beta"])
print gnu_getopt(args, "a:b", {"alpha=" : 0, "beta" : 0})
print getopt(args, "a:b", "alpha=")
print gnu_getopt(args, "a:b", "alpha=")

#OSError
import os

try:
    os.chdir('ontehunoe')

except OSError, e:
#    print e
#    print repr(e)
    print e.errno
#    print e.strerror
    print e.filename

#int(), float(), str(); test all
print int(), float(), list(), dict(), set(), tuple(), frozenset(), # XXX repr(str())

#collections.defaultdict
from collections import defaultdict

s1 = 'mississippi'
d1 = defaultdict(int)
for k1 in s1:
    d1[k1] += 1

print sorted(d1.items())

s2 = [('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]
d2 = defaultdict(list)
for k2, v2 in s2:
    d2[k2].append(v2)

print sorted(d2.items())

s3 = [('red', 1), ('blue', 2), ('red', 3), ('blue', 4), ('red', 1), ('blue', 4)]
d3 = defaultdict(set)
for k3, v3 in s3:
    d3[k3].add(v3)

print sorted(d3.items())

''', '''
output(equal=True)

'''),

('''fixes for 0.0.25''', '''
# --- more aug assignment
f = -112
print f
f /= -3
print f, f / -3
f %= -3
print f
f //= -1
print f

d={}

somme = 9.0
i=4
j=5

d[i,j] = 3.0
d[i,j] += somme
d[i,j] *= somme
d[i,j] /= somme
 
print d

e = {}
e[i,j] = -7
e[i,j] /= -2
e[i,j] *= -2
e[i,j] %= -2
e[i,j] //= -2

print e

# --- tests these for once
print max([1])
print max(1, 2)
print max(7.7, 7)
print max(7, 7.7)
print max(1, 2, 3)
print max(1, 2, 3, 4, 5)

print min([1])
print min(1, 2)
print min(6.7, 7)
print min(7, 6.7)
print min(1, 2, 3)
print min(1, 2, 3, 4, 5)

# --- virtual test case 1
class Z:
    def boink(self, a):
        pass

    def beh(self):
        print self.boink(9)

class Y(Z):
    def boink(self, a):
        return a

y = Y()
y.beh()

# --- virtual test case 2
class C:
    def boink(self):
        print 'C'

class D(C):
    pass

class A(C):
    def boink(self):
        print 'A'

class B(C):
    pass

c = D()
c.boink()

b = B()
b = A()
b.boink()

# --- virtual case 3
class CC:
    pass

class AA(CC):
    def __init__(self):
        self.a = 4

class BB(CC):
    def __init__(self):
        self.a = 5

cc = AA()
cc = BB()
print cc.a

# --- just in case
this = 1

# --- good to test also
import struct

''', '''
output(equal=True)
'''),

('''fixes for 0.0.24''', '''
# --- import problem
from testdata.bert import *
z = zeug()

# --- '_' renaming mangle
import testdata.bert

class hello:
    def hello(self):
        testdata.bert.hello(1)

s=hello().hello()

''', '''
output(equal=True)
'''),

('''fixes for 0.0.23''', '''
# --- string formatting problem
print '%i%%-%i%%' % (1,2)
numbers = (1,2)
print '%i%%-%i%%' % numbers
print '%i%%-%s%%' % (12, '21')
t2 = (12, '21')
print '%i%%-%s%%' % t2

# --- aug assign problem (or: the value of testing)
a = [1,2,3,4,5]
c = a
b = [6,7,8,9,10]

a += b
print a, c

ah = '12345'
ch = ah
bh = '67890'
ah += bh
print ah, ch

# --- __iadd__ etc.
class C:
    def __init__(self, value):
        self.value = value 

    def __iadd__(self, other):
        self.value += other.value
        return self

    def __floordiv__(self, b):
        return C(self.value // b.value)

    def __ifloordiv__(self, b):
        self.value //= b.value
        return self

    def __str__(self):
        return str(self.value)

x = C(4)
x += x
x.__iadd__(x)
print x

print [1,2].__iadd__([2,3])

y = [1,2,3]
y += set([4,5])
print y

v = 3
v += 1.5
print v

hm = []
hm += set([1])
print hm

d = C(8)
print d // C(3)
d //= C(3) 
print d

# --- inheritance problem
class Maze(object):
    def __init__(self):
        self.maze = [[0]]
        self.maze[0][0] |= 1

class ASCIIMaze(Maze):
    pass
        
maze = ASCIIMaze() 

''', '''
output(equal=True)

'''),

('''fixes for 0.0.22''', '''
# --- out of bounds can be okay 
a = range(5)
print a[:10], a[:10:2]
print a[-10:], a[-10::2]

# --- abs
class C:
  def __abs__(self):
      return self
  def __neg__(self):
      return self
  def __repr__(self):
      return 'C'

print abs(C()), abs(23), abs(-1.3), -abs(C())
      
# --- str.translate problem
import string
atable = string.maketrans("bc", "ef")
print 'abcdeg'.translate(atable, "cde")
gtable = string.maketrans("", "")
word = 'aachen\\n'
key = word.translate(gtable, "a\\n")
print 'word', repr(word)

# --- string.{capitalize, capwords, swapcase, center, atoi, atol, atof}
print string.capitalize('hoi'), ' hoi'.capitalize()
print string.capwords('yo   momma')+'!'+string.capwords(' yo momma ')+'!'+string.capwords(' yo momma ', 'mm')+'!'
allchars = ''.join([chr(x) for x in range(256)])
print repr(allchars.swapcase()), repr(string.swapcase(allchars))
print string.center('hoi', 10), string.center('hoi', 10, 'u')
print 'hoi'.center(10, 'u')
for i in range(10):
    print '!'+'hoi'.center(i)+'!'
print string.atoi('+0x10', 0), string.atol('-100l', 0), string.atof('-1.234')

# --- improve overloading
class D:
    def __int__(self): return 7
    def __float__(self): return 7.0
    def __str__(self): return '__str__'
    def __repr__(self): return '__repr__'
    def __cmp__(self, b): return 1
    def __nonzero__(self): return 1
    def __len__(self): return 1

d = D()

print [0,1][bool(d)], str(d), int(d), float(d), max([d,d]), min([d,d])
if 5: print 5
if d: print 6

''', '''
output(equal=True)


'''),

('''fixes for 0.0.21; collections.deque''', '''
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
blah(['1','2','3','4','5','6','7'], '4')

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
abert.a = 1

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


''', '''
output(equal=True)


'''),

('''fixes for 0.0.20''', '''
# --- division revisited
print -496 // 3, 496 // 3, -496 // -3, 496 // -3
print -496.0 // 3.0, 496.0 // 3.0, -496.0 // -3.0, 496.0 // -3.0
print -496.0 // 3, 496 // 3.0, -496.0 // -3, 496 // -3.0
print -496 / 3, 496 / 3, -496 / -3, 496 / -3

print '%g' % (-496.0 / 3.0), '%g' % (496.0 / 3.0), '%g' % (-496.0 / -3.0), '%g' % (496.0 / -3.0) # XXX no '%g'
print '%g' % (-496.0 / 3), '%g' % (496 / 3.0), '%g' % (-496.0 / -3), '%g' % (496 / -3.0)

xx, yy, zz = divmod(-496, 3), divmod(-496.0, 3), divmod(-496, 3.0)
print xx, yy, zz

print divmod(-496, 3), divmod(496, 3), divmod(-496, -3), divmod(496,-3)
print divmod(-496.0, 3.0), divmod(496.0, 3.0), divmod(-496.0, -3.0), divmod(496.0,-3.0)
print divmod(-496.0, 3), divmod(496, 3.0), divmod(-496.0, -3), divmod(496,-3.0)

# --- don't crash
print [0]*-4, (0,)*-4, repr('0'*-4)

# --- list.extend takes iterable
w = [1,2]
w.extend(set([3]))
print w

# --- use %.12g to print floats
print 1/3.0, 1.1234123412341234, 9.12341234e20, 1.1, 8.0

# --- slice assignment (random test) 
import random
random.seed(10)

for x in range(1000):
    l,u,s = random.randrange(-5,5), random.randrange(-5,5), random.randrange(-5,5)
    a = range(5)
    print a, 'lower', l, 'upper', u, 'step', s
    try:
        z = range(random.randrange(0,5))
        print 'xrange', z
        a[l:u:s] = z
        print 'done', a
    except ValueError, v:
        print v
        
ax = range(10)
ax[-2:-3] = [0,1]
print ax

# --- do not print space after 14
print 14,
print
print 'boe'

# --- aug assignment revisited
class hoepa:
    def __init__(self):
        self.elems = [1,2,3]
        self.smurf = 1
    def __getitem__(self, index):
        print 'get', index
        return self.elems[index]
    def __setitem__(self, index, elem):
        print 'set', index, elem
        self.elems[index] = elem

uh = hoepa()

uh[2] = 3
print uh[2]
uh[2] += 4
print uh.elems
 
ux = 1
ux += 1
print ux

uy = [1]
uy += [2]
print uy

uh.smurf += 1
print uh.smurf

blah = [1,2,4]
blah[2] += 5
print blah

ud = {'7': 7}
print ud['7']
ud['7'] = 8
ud['7'] += 1
print ud

class hoepa2:
    def __init__(self):
       self.hop = {}
    def __getitem__(self, index):
        print 'get', index
        return self.hop[index]
    def __setitem__(self, index, elem):
        print 'set', index, elem
        self.hop[index] = elem
    def __delitem__(self, index):
        del self.hop[index]

yh = hoepa2()
yh[1,2] = 10
yh[1,2] += 10
print yh[1,2]

# --- __delitem__
print yh.hop
del yh[1,2] 
print yh.hop

yx = [1,2,3]
del yx[1]
print yx

# --- some string tests
import string
print string.join(['a','b'])
print string.join(['a','b'], '_')
print string.find('abc', 'b')
print string.find('abc', 'b', 0)
print string.find('abc', 'b', 0, 3)
print string.split('a b c')
print string.split('a b c', ' ')
print string.split('a b c', ' ', 1)
print string.replace('abc', 'c', 'd') 
print string.replace('abc', 'c', 'd', 1) 
print string.count('abc', 'b')
print string.count('abc', 'b', 0)
print string.count('abc', 'b', 0, 3)
print string.expandtabs('abc')
print string.expandtabs('abc', 4)
print string.strip(' abc ')
print string.strip('xabcx', 'x')
print string.ljust('abc', 8)
print string.ljust('abc', 8, '_')
print string.rsplit('a b c', ' ', 1)

# --- recursive generator test
def A003714():
    yield 1
    for x in A003714():
        yield 2*x
        if not (x & 1):
            yield 2*x+1

hop = A003714()
for x in range(20):
    print hop.next(),
print

# --- allow 'self' as formal argument in non-method function
def blahx(self, x):
    print self, x
blahx(18, 19)


''', '''
output(equal=True)

'''),

('''random module''', '''

import random

# --- module-level functions
random.seed(37)
rstate = random.getstate()   # (state is not cross-compatible with CPython)
random.setstate(rstate)
for i in range(25):
    print "%.8f" % random.random()
    print random.randrange(-30,15)
    print random.randrange(-15,15,3)
    print random.randint(50,100)
    fibs = [0,1,1,2,3,5,8,13,21]
    print fibs
    print random.choice(fibs)
    print random.sample(fibs,3)
    random.shuffle(fibs)
    print fibs
    nums = [3.141, 2.71828, 1.41421, 1.0]
    print nums
    print random.choice(nums)
    print random.sample(nums,3)
    random.shuffle(nums)
    print nums
    print "%.8f" % random.uniform(-0.5,0.5)
    print "%.8f" % random.normalvariate(0.0, 1.0)
    print "%.8f" % random.lognormvariate(0.0, 1.0)
    print "%.8f" % random.expovariate(1.0)
    print "%.8f" % random.vonmisesvariate(0.0, 1.0)
    print "%.8f" % random.gammavariate(20.0, 1.0)
    print "%.8f" % random.gauss(0.0, 1.0)
    print "%.8f" % random.betavariate(3.0, 3.0)
    print "%.8f" % random.paretovariate(1.0)
    print "%.8f" % random.weibullvariate(1.0, 1.0)
    #print "%.8f" % random.stdgamma(1.0,1.0,1.0,1.0) # deprecated in CPython
    #print "%.8f" % random.cunifvariate(0.0,1.0)     # deprecated in CPython
    print random.getrandbits(8)
    print random.getrandbits(16)
    print random.getrandbits(30)
    print ''

# --- (test set for RNGs)
def runrng(r):
    print "%.8f" % r.random()
    print r.randrange(0,10)
    print r.randrange(-10,10,2)
    print r.randint(-5,5)
    fibs = [0,1,1,2,3,5,8,13,21]
    print fibs
    print r.choice(fibs)
    print r.sample(fibs,4)
    r.shuffle(fibs)
    print fibs
    nums = [3.141, 2.71828, 1.41421, 1.0]
    print nums
    print random.choice(nums)
    print random.sample(nums,1)
    random.shuffle(nums)
    print nums
    print "%.8f" % r.uniform(-0.5,0.5)
    print "%.8f" % r.normalvariate(0.0, 1.0)
    print "%.8f" % r.lognormvariate(0.0, 1.0)
    print "%.8f" % r.expovariate(1.0)
    print "%.8f" % r.vonmisesvariate(0.0, 1.0)
    print "%.8f" % r.gammavariate(20.0, 1.0)
    print "%.8f" % r.gauss(0.0, 1.0)
    print "%.8f" % r.betavariate(3.0, 3.0)
    print "%.8f" % r.paretovariate(1.0)
    print "%.8f" % r.weibullvariate(1.0, 1.0)
    #print "%.8f" % r.stdgamma(1.0, 1.0, 1.0, 1.0) # deprecated in CPython
    #print "%.8f" % r.cunifvariate(0.0, 1.0)       # deprecated in CPython
    print ''

# --- random.Random (Mersenne Twister)
mt = random.Random()
mt.seed()
mt.seed(79)
mtstate = mt.getstate()   # (state is not cross-compatible with CPython)
mt.setstate(mtstate)
#mt.jumpahead(1000000)    # (not yet supported)
for i in range(25): runrng(mt)

# --- random.WichmannHill
wh = random.WichmannHill()
wh.seed()
wh.seed(86)
wh.whseed()
wh.whseed(41)
whstate = wh.getstate()   # (state is not cross-compatible with CPython)
wh.setstate(whstate)
wh.jumpahead(1000000)
for i in range(25): runrng(wh)

''', '''
output(equal=True)

'''),

('''fixes for 0.0.19; iterators''', '''
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
print 1 > 2 or 3
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

''', '''
output(equal=True)

'''),

('''fixes for 0.0.18''', '''
# --- model list.__str__ call to elem.__repr__
class Vertex(object):
    def __repr__(self):
        return 'rrrepr'
print [Vertex()]

# --- always true/false, but should work
print [0,1][isinstance(7.0, float)]
print [0,1][isinstance(7, int)]

# --- initialize class attrs in .cpp file
class blah:
    blah = 'blah'
    blah2 = ('blah', 'blah')
    blah3 = abs(-1)
print blah.blah, blah.blah2, blah.blah3

# --- inf
a,b = -1e500, 1e500; print a,b

# --- argh
print sorted('hopla')

# --- dict<void *, void*> *
d = {}
print d

# --- cl attr problem
class FilebasedMazeGame: 
    hop = 18
    def __init__(self):
        a = FilebasedMazeGame.hop
        print a

FilebasedMazeGame()

# --- define cl before use
def print_aap():
    aap = Aap()
    print aap

class Aap:
    def __repr__(self):
        return 'hrngh!'

print_aap()

# --- virtual case
class hop:
    def hop(self):
        self.hop2()

class hop2(hop):
    def hop2(self):
        print 'hop2'

hop2().hop()

# --- str.split
s = " foo zbr bar "

print "default separator:"
print s.split(None)
print s.split(None, 0)
print s.split(None, 1)
 
print "space separator:"
print s.split(' ')
print s.split(' ', 0)

# --- comparison
class g: pass
e, f = g(), g()
print (e < f) + (e > f), [0,1][e == f]

''', '''
output(equal=True)

'''),

('''fixes for 0.0.17''', '''
# --- assignment expressions
bweh = (2,[4,6])
[a, (b,c)] = bweh
print a,b,c
(a,b), (c,d) = (6,9), (8,7)
print a,b,c,d
[(a,b), (c,d)] = (9,8), (7,6)
print a,b,c,d
[(a,b), (c,d)] = [(1,8), (7,2)]
print a,b,c,d
[[a,b],c] = (5,6),3
print a,b,c
[[a,b],c] = [[4,5],6]
print a,b,c
a, [b,c] = [1, (2,3)]
print a,b,c 
a, (b,c,d) = 1, (1,2,3)
print a,b,c,d
[(a,b), [c,d]] = [[1,2], (3,4)]
print a,b,c,d
njeh = [[8,7,6],[5,4,3],[2,1,0]]
[[a,b,c],[d,e,f],[g,h,i]] = njeh
print a,b,c,d,e,f,g,h,i
[dx,[a,b,c],ex] = njeh
print dx,a,b,c,ex
blah = (1,2,3,4,5,6)
a,b,c,d,e,f = blah
print a,b,c,d,e,f

# --- underscore in assignment
_ = 4
a, _ = 1, '2'
huh = 1, 2
_, b = huh
mtx = [[1,2,3],[4,5,6],[6,7,8]]
[du, [x, y, _], _] = mtx
print du, x, y
hop = [(1,(2,3))]
for _ in hop: print 'hop'
for _, (a,b) in hop: print 'hop', a, b
for a, (_,b) in hop: print 'hop', a, b
for a, _ in hop: print 'hop', a
print ['hop' for _ in hop]
print ['hop %d %d' % (a,b) for _, [a,b] in hop]
print ['hop %d %d' % (a,b) for a, [_,b] in hop]
print ['hop %d' % a for a, _ in hop]

# --- except 'tuple'
for a in range(2):
    try:
        if not a: assert 1 > 2, 'parasmurf'
        else: {1:2}[3]
    except (AssertionError, KeyError), m:
        print 'foutje3 of 4', m

# --- getopt.GetoptError test
import getopt
try:
    opts, args = getopt.getopt(['-x'], 'nf:', ['nowrap', 'flags='])
except getopt.GetoptError:
    print 'fout'

''', '''
output(equal=True)

'''),

('''frozenset''', '''
a = frozenset([1])
d = a & a
d = a | a
d = a - a
d = a ^ a
print a, d

c = set([1,2])
e = set([])
f = set()
print c, e, f
    
g = frozenset([1])
h = {}
h[g] = 4
print h
h[frozenset([3,2,1])] = 5
del h[frozenset([1])]
for x in h:
    print sorted(x), h[x]

try:
    {set([1]): 1}
except TypeError, m:
    print m
    
z,y  = [(1,2),(3,), (4,5,6)], [(3,),(4,5,6),(1,2)]
v, w = frozenset(z), frozenset(y)
print 'eq', [0, 1][v == w]
print 'hash', [0, 1][hash(v) == hash(w)]

k = set([1])
k = frozenset([2])

''', '''
output(equal=True)

'''),

('''fixes for 0.0.16''', '''
print '', 
print 'hoi', 'huh',
print 'hophop'
print '', 
print 'beh'

print [1,2,3,1].index(1)
print [1,2,3,1].index(1, 1)
print [1,2,3,1].index(1, -1)
print [1,2,3,1].index(1, -4)
print [1,2,3,1].index(1, -3, 4)

def RemoveElts(list):
   newlist=list[:]
   return newlist
print RemoveElts([3])

try:
    try: 
       {1:2}[3]
    except KeyError, e:
       raise e
except KeyError, m:
    print m

blah = set([])
blah.add(1)
print blah

def MergeAndVerify(newModList,finalModHash):
    if newModList == []:
        return finalModHash


''', '''
output(equal=True)

'''),

('''fixes for 0.0.14''', '''
# optional start/end arguments for str.{count, startswith, endswith}

def hop(b):
    if b: print 1
    else: print 0

hop('hoi'.startswith('ho', 0))
hop('hoi'.startswith('ho', 0, 3))
hop('hoi'.startswith('ho', 0, -1))
hop('hoi'.endswith('oi'))
hop('hoi'.endswith('oi', 0, 3))
hop('hoi'.endswith('ho', 0, -1))
hop('hoi'.endswith('ho', -3, 2))
hop('hoi'.startswith(':', 3))
hop('hoi:'.startswith(':', 3))

print 'hoooi'.count('o')
print 'hoooi'.count('o', 2)
print 'hoooi'.count('o', 0, -2)

# mother contour (6,5) -> (1,1) instead of (1,5)
def getopt(args, longopts):
    opts = []
    opts.append(('',))

    do_longs(opts, longopts)

def do_longs(opts, longopts):
    [o for o in longopts] 

wa = ['']

getopt(wa, wa)

# cStringIO.StringIO, file.seek 
import cStringIO, sys

s = cStringIO.StringIO(file('testdata/hopsakee').read())
print s.readlines()

s = file('testdata/hopsakee')
print s.read()

f = file('testdata/hopsakee')
print f.read()
f.seek(0)
print f.read()
f.close()

s = cStringIO.StringIO('blaat')
s.seek(-3, 2)
print s.read()

s = cStringIO.StringIO() 
s.write('hallo\\njoh')
s.seek(0, 0)
print s.readlines()
s.seek(0, 0)
s.write('hoi')
print s.readlines()

blah = set([])

''', '''
output(equal=True)

'''),

('''new print/mod/file implementation''', '''
print 1, 2, '3', '%.2f' % 4.1
print '%04x' % 0xfeda

# '..' % (..)
print '%d %x %d' % (10, 11, 12)
print '%d %s' % (1, 'een')
print '%d %s %.2f' % (1, 'een', 8.1)

# '..' % tuple
t = (10, 11, 12)
print '%x %d %x' % t
t2 = ('twee', 2)
print '%s %04x' % t2

# mod
a = '%04x' % 0xdefa
print a, a, '%02x' % 0x1234

# all chars
print '%o' % 10
print "%.4s %.4r\\n" % ("abcdefg", "\\0hoplakee")

# print to file
f = file('testdata/binf', 'w')
print >>f, 'ik haat %04x\\n' % 0xfeda, 'smurven..\\n'
f.close()

# conversions
print repr('?%% %c?' % 70), repr('?%c?%%' % 0), '%c' % 'X'
print '!%s!' % [1,2,3]
print '%.2f %d %.2f %d' % (4, 4.4, 5.5, 5)
print '%s.' % 1, '%s.' % (1,)

# %s, %r
print repr(18), repr('x')
print 'aha %s %r' % (18, 19)

# class file 
f = file('testdata/hopsakee')
print 1, f.readline(),
print f.readline(5)
print f.readline(),
f.close()

print 2, file('testdata/hopsakee').read()

print 3, file('testdata/hopsakee').readlines()

for line in file('testdata/hopsakee'):
    print 'aha', line,


''', '''
output(equal=True)

'''),

('''fixes for 0.0.13''', '''
# basic string module support
import string
print string.join(['hello', 'world!']), string.join(['hello', 'world!'], '_')

# add random.shuffle
import random
l = [1,2,3,4,5]
random.shuffle(l)
print set(l)

# add __or__ to builtin.int..
class c: # grr
   def a(self):         
       return 1|1      
   def b(self):
       return 1&1
   def c(self):
       return 1^1
   def d(self):
       return ~1

a_c = c()           
print a_c.a(), a_c.b(), a_c.c(), a_c.d()

# fake child nodes conflicting for binary tuples (e.g. one for unit and one for first)
class LowLevel:
   def comRxHeader(self):
       ('a', 'h')
       (7, 8)

bsl = LowLevel()
bsl.comRxHeader()

# self.mergeinh instead of self.merge XXX fix others
class LowLevel2:
   def bslTxRx(self, addr): 
       addr % 2

class BootStrapLoader2(LowLevel2):
    pass

bsl2 = BootStrapLoader2()
bsl2.bslTxRx(0) 

# improve parent constructor calls
class L:
    def __init__(self):
        pass

class BSL(L):
    def __init__(self, a, b):
        L.__init__(self)

BSL(1, 2)

# for/while-else construction
bla = True
while bla:
    for a in range(10):
        for b in range(10):
            pass
        else:
            print 'bah1'
        while bla:
            bla = False
            break
        else:
            print 'bah4'
        break
    else:
        print 'bah2'
else:
    print 'bah3'

# user-defined exception class problems
class MyException(Exception):
    pass

try:
    raise MyException('hoepa')
except MyException, m:
    print m

# parent constructor call and default arguments
class LowLevel3:
    def __init__(self, a=1):
        pass

class BootStrapLoader3(LowLevel3):
    def __init__(self):
        LowLevel3.__init__(self)

BootStrapLoader3() 

''', '''
output(equal=True)

'''),

('''fixes for 0.0.12''', '''
import time
time.sleep(1.01)

import sys
#print 'Python version:', sys.version
sys.stdout.flush()

a = '\\001\\00\\0boink'
print repr('hello, world')
print repr('hello\\0, world2')

print 'hello, world'
print repr('hello\\0, world2') # XXX no repr!

print repr(a), len(a)
print repr(chr(0)), len(chr(0)+chr(0))
print repr('\\0')
print repr(''.join([chr(i) for i in range(256)]))

class behh:
    def __init__(self, a, b, c):
        pass

behh(1,2,c=3)

# sudoku solver!! see: http://markbyers.com/moinmoin/moin.cgi/ShortestSudokuSolver
def r(a):
  i=a.find('0')
  if not ~i: print a; sys.exit()
  [m in [a[j] for j in range(81) if not (i-j)%9*(i/9^j/9)*(i/27^j/27|i%9/3^j%9/3)] or r(a[:i]+m+a[i+1:]) for m in '3814697265625']
  return 1 # because the type of an 'or' clause is the superset of its terms, we cannot (implicitly) return None here

r(81*'0')

''', '''
output(equal=True)

'''),

('''fixes for 0.0.11''', '''
class City(object):
    def __init__(self):
        self.latitude = 1

class SortedTree(object):
    def __init__(self, compareKey): 
        self.compareKey = compareKey

class Map(object):
    def __init__(self):
        st = SortedTree(lambda x: x.latitude)
        st.compareKey(c)

c = City()
m = Map()

print "1, 3, 5".replace(",", "")
print "1, 3, 5".replace(",", "", -1)
print "1, 3, 5".replace(",", "", 0)
print "1, 3, 5".replace(",", "", 1)

a = []
a = [[]]
a = [[1]]

b = []
b = [1]

d = ()
d = (5,)

print a, b, d

def bla(t):
    print t

bla(())
bla((1,))

def oink():
    return [[1]]
    return [[]]

oink()

def test(t=()):
  if t: 
      print t
  else: 
      test(t + (5,))
  
test()

e = {}
e[2,3] = 4

f = {}
f[5] = 6

print e, f

import os
x = os.listdir('.')

''', '''
output(equal=True)

'''),

('''fixes for 0.0.10''', '''
bla = {}
meuk = (12, 13)
z = (5,(3,4))

bla[1], (c, d) = z
print bla

class X: pass
x = X()

for x.z in [1,2,3]: print x.z
x.y, (c, d) = z

print x.y, x.z

s = ['a', 'b', 'c']
s = 'abc'
for y in s: print y
print
print s, str(s), repr(s)

t2 = 1, 'een'
print '%d %s' % t2

f = dict([(1,'1'), (2, '2')])
print f

''', '''
output(equal=True)

'''),

('''richards benchmark''', '''
#  Based on original version written in BCPL by Dr Martin Richards
#  in 1981 at Cambridge University Computer Laboratory, England
#  and a C++ version derived from a Smalltalk version written by
#  L Peter Deutsch.
#  Translation from C++, Mario Wolczko
#  Outer loop added by Alex Jacoby

# Task IDs
I_IDLE = 1
I_WORK = 2
I_HANDLERA = 3
I_HANDLERB = 4
I_DEVA = 5
I_DEVB = 6

# Packet types
K_DEV = 1000
K_WORK = 1001

# Packet

BUFSIZE = 4

BUFSIZE_RANGE = range(BUFSIZE)

class Packet(object):
    def __init__(self,l,i,k):
        self.link = l
        self.ident = i
        self.kind = k
        self.datum = 0
        self.data = [0] * BUFSIZE

    def append_to(self,lst):
        self.link = None
        if lst is None:
            return self
        else:
            p = lst
            next = p.link
            while next is not None:
                p = next
                next = p.link
            p.link = self
            return lst

# Task Records

class TaskRec(object):
    pass

class DeviceTaskRec(TaskRec):
    def __init__(self):
        self.pending = None

class IdleTaskRec(TaskRec):
    def __init__(self):
        self.control = 1
        self.count = 10000

class HandlerTaskRec(TaskRec):
    def __init__(self):
        self.work_in = None
        self.device_in = None

    def workInAdd(self,p):
        self.work_in = p.append_to(self.work_in)
        return self.work_in

    def deviceInAdd(self,p):
        self.device_in = p.append_to(self.device_in)
        return self.device_in

class WorkerTaskRec(TaskRec):
    def __init__(self):
        self.destination = I_HANDLERA
        self.count = 0
# Task

class TaskState(object):
    def __init__(self):
        self.packet_pending = True
        self.task_waiting = False
        self.task_holding = False

    def packetPending(self):
        self.packet_pending = True
        self.task_waiting = False
        self.task_holding = False
        return self

    def waiting(self):
        self.packet_pending = False
        self.task_waiting = True
        self.task_holding = False
        return self

    def running(self):
        self.packet_pending = False
        self.task_waiting = False
        self.task_holding = False
        return self
        
    def waitingWithPacket(self):
        self.packet_pending = True
        self.task_waiting = True
        self.task_holding = False
        return self
        
    def isPacketPending(self):
        return self.packet_pending

    def isTaskWaiting(self):
        return self.task_waiting

    def isTaskHolding(self):
        return self.task_holding

    def isTaskHoldingOrWaiting(self):
        return self.task_holding or (not self.packet_pending and self.task_waiting)

    def isWaitingWithPacket(self):
        return self.packet_pending and self.task_waiting and not self.task_holding





tracing = False
layout = 0

def trace(a):
    global layout
    layout -= 1
    if layout <= 0:
        print
        layout = 50
    print a
    print a,


TASKTABSIZE = 10

class TaskWorkArea(object):
    def __init__(self):
        self.taskTab = [None] * TASKTABSIZE

        self.taskList = None

        self.holdCount = 0
        self.qpktCount = 0

taskWorkArea = TaskWorkArea()

class Task(TaskState):


    def __init__(self,i,p,w,initialState,r):
        self.link = taskWorkArea.taskList
        self.ident = i
        self.priority = p
        self.input = w

        self.packet_pending = initialState.isPacketPending()
        self.task_waiting = initialState.isTaskWaiting()
        self.task_holding = initialState.isTaskHolding()

        self.handle = r

        taskWorkArea.taskList = self
        taskWorkArea.taskTab[i] = self

    def fn(self,pkt,r):
        raise NotImplementedError


    def addPacket(self,p,old):
        if self.input is None:
            self.input = p
            self.packet_pending = True
            if self.priority > old.priority:
                return self
        else:
            p.append_to(self.input)
        return old


    def runTask(self):
        if self.isWaitingWithPacket():
            msg = self.input
            self.input = msg.link
            if self.input is None:
                self.running()
            else:
                self.packetPending()
        else:
            msg = None

        self
        return self.fn(msg,self.handle)


    def waitTask(self):
        self.task_waiting = True
        return self


    def hold(self):
        taskWorkArea.holdCount += 1
        self.task_holding = True
        return self.link


    def release(self,i):
        t = self.findtcb(i)
        t.task_holding = False
        if t.priority > self.priority:
            return t
        else:
            return self


    def qpkt(self,pkt):
        t = self.findtcb(pkt.ident)
        taskWorkArea.qpktCount += 1
        pkt.link = None
        pkt.ident = self.ident
        return t.addPacket(pkt,self)


    def findtcb(self,id):
        t = taskWorkArea.taskTab[id]
        if t is None:
            raise Exception("Bad task id %d" % id)
        return t
            

# DeviceTask


class DeviceTask(Task):
    def __init__(self,i,p,w,s,r):
        Task.__init__(self,i,p,w,s,r)

    def fn(self,pkt,r):
        d = r
        assert isinstance(d, DeviceTaskRec)
        if pkt is None:
            pkt = d.pending
            if pkt is None:
                return self.waitTask()
            else:
                d.pending = None
                return self.qpkt(pkt)
        else:
            d.pending = pkt
            if tracing: trace(pkt.datum)
            return self.hold()



class HandlerTask(Task):
    def __init__(self,i,p,w,s,r):
        Task.__init__(self,i,p,w,s,r)

    def fn(self,pkt,r):
        h = r
        assert isinstance(h, HandlerTaskRec)
        if pkt is not None:
            if pkt.kind == K_WORK:
                h.workInAdd(pkt)
            else:
                h.deviceInAdd(pkt)
        work = h.work_in
        if work is None:
            return self.waitTask()
        count = work.datum
        if count >= BUFSIZE:
            h.work_in = work.link
            return self.qpkt(work)

        dev = h.device_in
        if dev is None:
            return self.waitTask()

        h.device_in = dev.link
        dev.datum = work.data[count]
        work.datum = count + 1
        return self.qpkt(dev)

# IdleTask


class IdleTask(Task):
    def __init__(self,i,p,w,s,r):
        Task.__init__(self,i,0,None,s,r)

    def fn(self,pkt,r):
        i = r
        assert isinstance(i, IdleTaskRec)
        i.count -= 1
        if i.count == 0:
            return self.hold()
        elif i.control & 1 == 0:
            i.control /= 2
            return self.release(I_DEVA)
        else:
            i.control = i.control/2 ^ 0xd008
            return self.release(I_DEVB)
            

# WorkTask


A = ord('A')

class WorkTask(Task):
    def __init__(self,i,p,w,s,r):
        Task.__init__(self,i,p,w,s,r)

    def fn(self,pkt,r):
        w = r
        assert isinstance(w, WorkerTaskRec)
        if pkt is None:
            return self.waitTask()

        if w.destination == I_HANDLERA:
            dest = I_HANDLERB
        else:
            dest = I_HANDLERA

        w.destination = dest
        pkt.ident = dest
        pkt.datum = 0

        for i in BUFSIZE_RANGE: # xrange(BUFSIZE)
            w.count += 1
            if w.count > 26:
                w.count = 1
            pkt.data[i] = A + w.count - 1

        return self.qpkt(pkt)

import time



def schedule():
    t = taskWorkArea.taskList
    while t is not None:
        pkt = None

        if tracing:
            print "tcb =",t.ident

        #print '*', t.__class__

        if t.isTaskHoldingOrWaiting():
            t = t.link
        else:
            if tracing: trace(chr(ord("0")+t.ident))
            t = t.runTask()

class Richards(object):

    def run(self, iterations):
        for i in xrange(iterations):
            taskWorkArea.holdCount = 0
            taskWorkArea.qpktCount = 0

            IdleTask(I_IDLE, 1, 10000, TaskState().running(), IdleTaskRec())

            wkq = Packet(None, 0, K_WORK)
            wkq = Packet(wkq , 0, K_WORK)
            WorkTask(I_WORK, 1000, wkq, TaskState().waitingWithPacket(), WorkerTaskRec())

            wkq = Packet(None, I_DEVA, K_DEV)
            wkq = Packet(wkq , I_DEVA, K_DEV)
            wkq = Packet(wkq , I_DEVA, K_DEV)
            HandlerTask(I_HANDLERA, 2000, wkq, TaskState().waitingWithPacket(), HandlerTaskRec())

            wkq = Packet(None, I_DEVB, K_DEV)
            wkq = Packet(wkq , I_DEVB, K_DEV)
            wkq = Packet(wkq , I_DEVB, K_DEV)
            HandlerTask(I_HANDLERB, 3000, wkq, TaskState().waitingWithPacket(), HandlerTaskRec())

            wkq = None;
            DeviceTask(I_DEVA, 4000, wkq, TaskState().waiting(), DeviceTaskRec());
            DeviceTask(I_DEVB, 5000, wkq, TaskState().waiting(), DeviceTaskRec());
            
            schedule()

            if taskWorkArea.holdCount == 9297 and taskWorkArea.qpktCount == 23246:
                pass
            else:
                return False

        return True

r = Richards()
iterations = 10
result = r.run(iterations)
print result
''', '''
output('1\\n')

'''),

('''pystone benchmark''', ''' 
# (c) Reinhold P. Weicker,  CACM Vol 27, No 10, 10/84 pg. 1013.
# --- Translated from ADA to C by Rick Richardson.
# --- Translated from C to Python by Guido van Rossum.

from time import clock

LOOPS = 50000
Ident1, Ident2, Ident3, Ident4, Ident5 = range(1,6)

class Record:
    def __init__(self, PtrComp = None, Discr = 0, EnumComp = 0,
                       IntComp = 0, StringComp = ''): # XXX '' should be None
        self.PtrComp = PtrComp
        self.Discr = Discr
        self.EnumComp = EnumComp
        self.IntComp = IntComp
        self.StringComp = StringComp

    def copy(self):
        return Record(self.PtrComp, self.Discr, self.EnumComp,
                      self.IntComp, self.StringComp)

TRUE = 1
FALSE = 0

def main(loops=LOOPS):
    benchtime, stones = pystones(loops)
#    print "Pystone(%s) time for %d passes = %g" % \
#          (__version__, loops, benchtime)
#    print "This machine benchmarks at %g pystones/second" % stones
    print 'ugh', benchtime, stones
    print "This machine benchmarks at %f pystones/second" % stones


def pystones(loops=LOOPS):
    return Proc0(loops)

IntGlob = 0
BoolGlob = FALSE
Char1Glob = ' ' # ! 
Char2Glob = ' '
Array1Glob = [0]*51
#Array2Glob = map(lambda x: x[:], [Array1Glob]*51)
Array2Glob = [x[:] for x in [Array1Glob]*51]
PtrGlb = None
PtrGlbNext = None

def Proc0(loops=LOOPS):
    global IntGlob
    global BoolGlob
    global Char1Glob
    global Char2Glob
    global Array1Glob
    global Array2Glob
    global PtrGlb
    global PtrGlbNext

    starttime = clock()
    for i in range(loops):
        pass
    nulltime = clock() - starttime

    PtrGlbNext = Record()
    PtrGlb = Record()
    PtrGlb.PtrComp = PtrGlbNext
    PtrGlb.Discr = Ident1
    PtrGlb.EnumComp = Ident3
    PtrGlb.IntComp = 40
    PtrGlb.StringComp = "DHRYSTONE PROGRAM, SOME STRING"
    String1Loc = "DHRYSTONE PROGRAM, 1'ST STRING"
    Array2Glob[8][7] = 10

    starttime = clock()

    for i in range(loops):
        Proc5()
        Proc4()
        IntLoc1 = 2
        IntLoc2 = 3
        String2Loc = "DHRYSTONE PROGRAM, 2'ND STRING"
        EnumLoc = Ident2
        BoolGlob = not Func2(String1Loc, String2Loc)
        while IntLoc1 < IntLoc2:
            IntLoc3 = 5 * IntLoc1 - IntLoc2
            IntLoc3 = Proc7(IntLoc1, IntLoc2)
            IntLoc1 = IntLoc1 + 1
        Proc8(Array1Glob, Array2Glob, IntLoc1, IntLoc3)
        PtrGlb = Proc1(PtrGlb)
        CharIndex = 'A'
        while CharIndex <= Char2Glob:
            if EnumLoc == Func1(CharIndex, 'C'):
                EnumLoc = Proc6(Ident1)
            CharIndex = chr(ord(CharIndex)+1)
        IntLoc3 = IntLoc2 * IntLoc1
        IntLoc2 = IntLoc3 / IntLoc1
        IntLoc2 = 7 * (IntLoc3 - IntLoc2) - IntLoc1
        IntLoc1 = Proc2(IntLoc1)

    benchtime = clock() - starttime - nulltime
    return benchtime, (loops / benchtime)

def Proc1(PtrParIn):
    PtrParIn.PtrComp = NextRecord = PtrGlb.copy()
    PtrParIn.IntComp = 5
    NextRecord.IntComp = PtrParIn.IntComp
    NextRecord.PtrComp = PtrParIn.PtrComp
    NextRecord.PtrComp = Proc3(NextRecord.PtrComp)
    if NextRecord.Discr == Ident1:
        NextRecord.IntComp = 6
        NextRecord.EnumComp = Proc6(PtrParIn.EnumComp)
        NextRecord.PtrComp = PtrGlb.PtrComp
        NextRecord.IntComp = Proc7(NextRecord.IntComp, 10)
    else:
        PtrParIn = NextRecord.copy()
    NextRecord.PtrComp = None
    return PtrParIn

def Proc2(IntParIO):
    IntLoc = IntParIO + 10
    while 1:
        if Char1Glob == 'A':
            IntLoc = IntLoc - 1
            IntParIO = IntLoc - IntGlob
            EnumLoc = Ident1
        if EnumLoc == Ident1:
            break
    return IntParIO

def Proc3(PtrParOut):
    global IntGlob

    if PtrGlb is not None:
        PtrParOut = PtrGlb.PtrComp
    else:
        IntGlob = 100
    PtrGlb.IntComp = Proc7(10, IntGlob)
    return PtrParOut

def Proc4():
    global Char2Glob

    BoolLoc = Char1Glob == 'A'
    BoolLoc = BoolLoc or BoolGlob
    Char2Glob = 'B'

def Proc5():
    global Char1Glob
    global BoolGlob

    Char1Glob = 'A'
    BoolGlob = FALSE

def Proc6(EnumParIn):
    EnumParOut = EnumParIn
    if not Func3(EnumParIn):
        EnumParOut = Ident4
    if EnumParIn == Ident1:
        EnumParOut = Ident1
    elif EnumParIn == Ident2:
        if IntGlob > 100:
            EnumParOut = Ident1
        else:
            EnumParOut = Ident4
    elif EnumParIn == Ident3:
        EnumParOut = Ident2
    elif EnumParIn == Ident4:
        pass
    elif EnumParIn == Ident5:
        EnumParOut = Ident3
    return EnumParOut

def Proc7(IntParI1, IntParI2):
    IntLoc = IntParI1 + 2
    IntParOut = IntParI2 + IntLoc
    return IntParOut

def Proc8(Array1Par, Array2Par, IntParI1, IntParI2):
    global IntGlob

    IntLoc = IntParI1 + 5
    Array1Par[IntLoc] = IntParI2
    Array1Par[IntLoc+1] = Array1Par[IntLoc]
    Array1Par[IntLoc+30] = IntLoc
    for IntIndex in range(IntLoc, IntLoc+2):
        Array2Par[IntLoc][IntIndex] = IntLoc
    Array2Par[IntLoc][IntLoc-1] = Array2Par[IntLoc][IntLoc-1] + 1
    Array2Par[IntLoc+20][IntLoc] = Array1Par[IntLoc]
    IntGlob = 5

def Func1(CharPar1, CharPar2):
    CharLoc1 = CharPar1
    CharLoc2 = CharLoc1
    if CharLoc2 != CharPar2:
        return Ident1
    else:
        return Ident2

def Func2(StrParI1, StrParI2):
    IntLoc = 1
    while IntLoc <= 1:
        if Func1(StrParI1[IntLoc], StrParI2[IntLoc+1]) == Ident1:
            CharLoc = 'A'
            IntLoc = IntLoc + 1
    if CharLoc >= 'W' and CharLoc <= 'Z':
        IntLoc = 7
    if CharLoc == 'X':
        return TRUE
    else:
        if StrParI1 > StrParI2:
            IntLoc = IntLoc + 7
            return TRUE
        else:
            return FALSE

def Func3(EnumParIn):
    EnumLoc = EnumParIn
    if EnumLoc == Ident3: return TRUE
    return FALSE

main(LOOPS)

''', '''
output()

'''),

('''fixes for 0.0.8''', '''
def appl(predicate, x): return predicate(x)
print [0,1][appl(lambda n: n>5, 10)], [0,1][appl(lambda n: n>10, 8)]

def split(seq, predicate):
    pair = [], []
    for el in seq:
        pair[not predicate(el)].append(el)
    return pair
print split(range(-5,6), lambda n: n%2==0)

class Obj:
    def __init__(self, n): self.n = n
    def __gt__(self, other): return self.n > other.n
    def __str__(self): return str(self.n)
def mymax(seq):
    maxval = seq[0]
    for el in seq:
        if el > maxval: # gives error
            maxval = el
    return maxval
l = [Obj(i) for i in xrange(100)]
print mymax(l), mymax(range(100))

class Num:
    def __init__(self, n): self.n = float(n)
    def __str__(self): return str(self.n)
    def __add__(self, other): return Num(self.n + other.n)
print sum([Num(i) for i in range(5)], Num(0))
print sum(range(5))

for a in 1,2: print a
for a in [1,2]: print a
for a in 1,2,3: print a

print 'aaaa'.replace('a','b', 2)
print 'aaaa'.replace('a','b', -1)

print 'aaaa'.split('a', 2)
print 'aaaa'.split('a', -1)

''', '''
output(equal=True)
#output("1 0\\n([-4, -2, 0, 2, 4], [-5, -3, -1, 1, 3, 5])\\n99 99\\n10.0\\n10\\n1\\n2\\n1\\n2\\n1\\n2\\n3\\nbbaa\\nbbbb\\n['', '', 'aa']\\n['', '', '', '', '']\\n")

'''),

('''pythonchess speed test engine''', '''
# This is an extremely simple chess like speed test program written in Python
# This program can be distributed under GNU General Public License Version 2.
# (C) Jyrki Alakuijala 2005
#
# Despite its looks, this program was written in Python, not converted to it.
# This program is incomplete, castlings, enpassant situation etc. are not properly implemented
# game ending is not recognized. The evaluator as simple as it ever could be. 
#
# The board is an 160-element array of ints, Nones and Booleans,
# The board contains the real board in squares indexed in variable 'squares'
# The oversized board is to allow for "0x88" chess programming trick for move generation.
# Other board data:
# 4x castling flags, indices [10-13], queen side white, king side white, queen side black, king side white
# turn, enpassant [26, 27]

from copy import copy

iNone = -999
iTrue = 1
iFalse = 0

setup = (4, 2, 3, 5, 6, 3, 2, 4, iNone, iNone) + (True,)*4 + (iNone, iNone) + \
  (1,) * 8 + (iNone, iNone, True, iNone, iNone, iNone, iNone, iNone,) + \
  ((0, ) * 8 + (iNone,) * 8) * 4 + \
  (-1,) * 8 + (iNone,) * 8 + \
  (-4, -2, -3, -5, -6, -3, -2, -4) + (iNone,) * 40

squares = tuple([i for i in range(128) if not i & 8])
knightMoves = (-33, -31, -18, -14, 14, 18, 31, 33)
bishopLines = (tuple(range(17, 120, 17)), tuple(range(-17, -120, -17)), tuple(range(15, 106, 15)), tuple(range(-15, -106, -15)))
rookLines = (tuple(range(1, 8)), tuple(range(-1, -8, -1)), tuple(range(16, 128, 16)), tuple(range(-16, -128, -16)))
queenLines = bishopLines + rookLines
kingMoves = (-17, -16, -15, -1, 1, 15, 16, 17)

linePieces = ((), (), (), bishopLines, rookLines, queenLines, (), (), queenLines, rookLines, bishopLines, (), ())

clearCastlingOpportunities = [None] * 0x80
for (i, v) in ((0x0, (10,)), (0x4, (10, 11)), (0x7, (11,)), (0x70, (12,)), (0x74, (12, 13)), (0x77, (13,))):
  clearCastlingOpportunities[i] = v

pieces = ".pnbrqkKQRBNP"

def evaluate(board):
  evals = (0, 100, 300, 330, 510, 950, 100000, -100000, -950, -510, -330, -300, -100)
  return sum([evals[board[i]] for i in squares])

def printBoard(board):
  for i in range(7,-1,-1):
    for j in range(8):
      ix = i * 16 + j
      print pieces[board[ix]],
    print

def move(board, mv):
  ix = (mv >> 8) & 0xff
  board[mv & 0xff] = board[ix]
  board[ix] = 0
  if clearCastlingOpportunities[ix]:
    for i in clearCastlingOpportunities[ix]:
      board[i] = False

  board[26] = not board[26] # Turn
  if (mv & 0x7fff0000) == 0:
    return
  if (mv & 0x01000000): # double step
    board[27] = mv & 7
  else:
    board[27] = iNone # no enpassant
  if (mv & 0x04000000): # castling
    toix = mv & 0xff
    if toix == 0x02:
      board[0x00] = 0
      board[0x03] = 4
    elif toix == 0x06:
      board[0x07] = 0
      board[0x05] = 4
    elif toix == 0x72:
      board[0x70] = 0
      board[0x73] = -4
    elif toix == 0x76:
      board[0x77] = 0
      board[0x75] = -4
    else:
      raise "faulty castling"
  if mv & 0x08000000: # enpassant capture
    if board[26]: # turn after this move
      board[mv & 0x07 + 64] = 0
    else:
      board[mv & 0x07 + 48] = 0
  if mv & 0x10000000: # promotion
    a = (mv & 0xff0000) >> 16
    if (a >= 0x80):
      a = a - 0x100 
    board[mv & 0xff] = a

def toString(move):
  fr = (move >> 8) & 0xff
  to = move & 0xff
  letters = "abcdefgh"
  numbers = "12345678"
  mid = "-"
  if (move & 0x04000000):
    if (move & 0x7) == 0x02:
      return "O-O-O"
    else:
      return "O-O"
  if move & 0x02000000:
    mid = "x"
  retval = letters[fr & 7] + numbers[fr >> 4] + mid + letters[to & 7] + numbers[to >> 4]
  return retval

def moveStr(board, strMove):
  moves = pseudoLegalMoves(board)
  for m in moves:
    if strMove == toString(m):
      move(board, m)
      return
  for m in moves:
    print toString(m)
  raise "no move found", strMove

def rowAttack(board, attackers, ix, dir):
  own = attackers[0]
  for k in [i + ix for i in dir]:
    if k & 0x88:
      return False
    if board[k]:
      return (board[k] * own < 0) and board[k] in attackers

def nonpawnAttacks(board, ix, color):
  return (max([board[ix + i] == color * 2 for i in knightMoves]) or 
          max([rowAttack(board, (color * 3, color * 5), ix, bishopLine) for bishopLine in bishopLines]) or
          max([rowAttack(board, (color * 4, color * 5), ix, rookLine) for rookLine in rookLines]))

nonpawnBlackAttacks = lambda board, ix: nonpawnAttacks(board, ix, -1)
nonpawnWhiteAttacks = lambda board, ix: nonpawnAttacks(board, ix, 1)

def pseudoLegalMovesWhite(board):
  retval = pseudoLegalCapturesWhite(board)
  for sq in squares:
    b = board[sq]
    if b >= 1:
      if b == 1 and not (sq + 16 & 0x88) and board[sq + 16] == 0:
        if sq >= 16 and sq < 32 and board[sq + 32] == 0:
          retval.append(sq * 0x101 + 32)
        retval.append(sq * 0x101 + 16)
      elif b == 2:
        for k in knightMoves:
          if board[k + sq] == 0:
            retval.append(sq * 0x101 + k)
      elif b == 3 or b == 5:
        for line in bishopLines:
          for k in line:
            if (k + sq & 0x88) or board[k + sq] != 0:
              break
            retval.append(sq * 0x101 + k)
      if b == 4 or b == 5:
        for line in rookLines:
          for k in line:
            if (k + sq & 0x88) or board[k + sq] != 0:
              break
            retval.append(sq * 0x101 + k)
      elif b == 6:
        for k in kingMoves:
          if not (k + sq & 0x88) and board[k + sq] == 0:
            retval.append(sq * 0x101 + k)
  if (board[10] and board[1] == 0 and board[2] == 0 and board[3] == 0 and
      not -1 in board[17:22] and
      not nonpawnBlackAttacks(board, 2) and not nonpawnBlackAttacks(board, 3) and not nonpawnBlackAttacks(board, 4)):
    retval.append(0x04000000 + 4 * 0x101 - 2)
  if (board[11] and board[5] == 0 and board[6] == 0 and
      not -1 in board[19:24] and
      not nonpawnBlackAttacks(board, 4) and not nonpawnBlackAttacks(board, 5) and not nonpawnBlackAttacks(board, 6)):
    retval.append(0x04000000 + 4 * 0x101 + 2)
  return retval

def pseudoLegalMovesBlack(board):
  retval = pseudoLegalCapturesBlack(board)
  for sq in squares:
    b = board[sq]
    if b < 0:
      if b == -1 and not (sq + 16 & 0x88) and board[sq - 16] == 0:
        if sq >= 96 and sq < 112 and board[sq - 32] == 0:
          retval.append(sq * 0x101 - 32)
        retval.append(sq * 0x101 - 16)
      elif b == -2:
        for k in knightMoves:
          if board[k + sq] == 0:
            retval.append(sq * 0x101 + k)
      elif b == -3 or b == -5: 
        for line in bishopLines:
          for k in line:
            if (k + sq & 0x88) or board[k + sq] != 0:
              break
            retval.append(sq * 0x101 + k)

      if b == -4 or b == -5:
        for line in rookLines:
          for k in line:
            if (k + sq & 0x88) or board[k + sq] != 0:
              break
            retval.append(sq * 0x101 + k)
      elif b == -6: 
        for k in kingMoves:
          if not (k + sq & 0x88) and board[k + sq] == 0:
            retval.append(sq * 0x101 + k)
  if (board[12] and board[0x71] == 0 and board[0x72] == 0 and board[0x73] == 0 and
      not 1 in board[0x61:0x65] and
      not nonpawnWhiteAttacks(board, 0x72) and not nonpawnWhiteAttacks(board, 0x73) and not nonpawnWhiteAttacks(board, 0x74)):
    retval.append(0x04000000 + 0x74 * 0x101 - 2)
  if (board[11] and board[0x75] == 0 and board[0x76] == 0 and
      not -1 in board[0x63:0x68] and
      not nonpawnWhiteAttacks(board, 0x74) and not nonpawnWhiteAttacks(board, 0x75) and not nonpawnWhiteAttacks(board, 0x76)):
    retval.append(0x04000000 + 0x74 * 0x101 + 2)
  return retval

def pseudoLegalMoves(board):
  if board[26]:
    return pseudoLegalMovesWhite(board)
  else:
    return pseudoLegalMovesBlack(board)

def pseudoLegalCapturesWhite(board):
  retval = []
  for sq in squares:
    b = board[sq]
    if b >= 1:
      if b == 1: 
        if not (sq + 17 & 0x88) and board[sq + 17] < 0:
          retval.append(0x02000000 + sq * 0x101 + 17)
        if not (sq + 15 & 0x88) and board[sq + 15] < 0:
          retval.append(0x02000000 + sq * 0x101 + 15)
        if sq >= 64 and sq < 72 and abs((sq & 7) - board[27]) == 1: # enpassant
          retval.append(0x02000000 + sq * 0x100 + (sq & 0x70) + 16 + board[27])
      elif b == 2:
        for k in knightMoves:
          if not (sq + k & 0x88) and board[k + sq] < 0:
            retval.append(0x02000000 + sq * 0x101 + k)
      elif b == 6:
        for k in kingMoves:
          if not(k + sq & 0x88) and board[k + sq] < 0:
            retval.append(0x02000000 + sq * 0x101 + k)
      else:
        for line in linePieces[b]:
          for k in line:
            if (sq + k & 0x88) or board[k + sq] >= 1:
              break
            if board[k + sq] < 0:
              retval.append(0x02000000 + sq * 0x101 + k)
              break
  return retval

def pseudoLegalCapturesBlack(board):
  retval = []
  for sq in squares:
    b = board[sq]
    if b < 0:
      if b == -1: 
        if board[sq - 17] >= 1:
          retval.append(0x02000000 + sq * 0x101 - 17)
        if board[sq - 15] >= 1:
          retval.append(0x02000000 + sq * 0x101 - 15)
        if sq >= 48 and sq < 56 and abs((sq & 7) - board[27]) == 1: # enpassant
          retval.append(0x0a000000 + sq * 0x100 + (sq & 0x70) - 16 + board[27])
      elif b == -2:
        for k in knightMoves:
          if not (sq + k & 0x88) and board[k + sq] >= 1:
            retval.append(0x02000000 + sq * 0x101 + k)
      elif b == -3:
        for line in bishopLines:
          for k in line:
            if board[k + sq] < 0:
              break
            if board[k + sq] >= 1:
              retval.append(0x02000000 + sq * 0x101 + k)
              break
      elif b == -4:
        for line in rookLines:
          for k in line:
            if board[k + sq] < 0:
              break
            if board[k + sq] >= 1:
              retval.append(0x02000000 + sq * 0x101 + k)
              break
      elif b == -5:
        for line in queenLines:
          for k in line:
            if board[k + sq] < 0:
              break
            if board[k + sq] >= 1:
              retval.append(0x02000000 + sq * 0x101 + k)
              break
      elif b == -6:
        for k in kingMoves:
          if board[k + sq] >= 1:
            retval.append(0x02000000 + sq * 0x101 + k)
  return retval

def pseudoLegalCaptures(board):
  if board[26]:
    return pseudoLegalCapturesWhite(board)
  else:
    return pseudoLegalCapturesBlack(board)

def legalMoves(board):
  allMoves = pseudoLegalMoves(board)
  retval = []
  #from copy import copy
  kingVal = 6
  if board[26]:
    kingVal = -kingVal
  for mv in allMoves:
    board2 = copy(board)
    move(board2, mv)
    #print "trying to reduce move", toString(mv)
    if not [i for i in pseudoLegalCaptures(board2) if board2[i & 0xff] == kingVal]:
      retval.append(mv)
  return retval

def alphaBetaQui(board, alpha, beta, n):
  e = evaluate(board)
  if not board[26]:
    e = -e
  if e >= beta:
    return (beta, iNone) # XXX
  if (e > alpha): 
    alpha = e
  bestMove = iNone # XXX
  if n >= -4:
    #from copy import copy
    for mv in pseudoLegalCaptures(board):
      newboard = copy(board)
      move(newboard, mv)
      value = alphaBetaQui(newboard, -beta, -alpha, n - 1)
      value = (-value[0], value[1])
      if value[0] >= beta:
        return (beta, mv)
      if (value[0] > alpha):
        alpha = value[0]
        bestMove = mv
  return (alpha, bestMove)

def alphaBeta(board, alpha, beta, n):
  if n == 0:
    return alphaBetaQui(board, alpha, beta, n)
#  from copy import copy
  bestMove = iNone # XXX

  for mv in legalMoves(board):
    newboard = copy(board)
    move(newboard, mv)
    value = alphaBeta(newboard, -beta, -alpha, n - 1)
    value = (-value[0], value[1])
    if value[0] >= beta:
      return (beta, mv)
    if (value[0] > alpha):
      alpha = value[0]
      bestMove = mv
  return (alpha, bestMove)

def speedTest():
  board = list(setup)
  moveStr(board, "c2-c4")
  moveStr(board, "e7-e5")
  moveStr(board, "d2-d4")

  res = alphaBeta(board, -99999999, 99999999, 4)
  print res
  moveStr(board, "d7-d6")
  res = alphaBeta(board, -99999999, 99999999, 4)
  print res

speedTest()
''', '''
output('(0, 33571891)\\n(0, 33567556)\\n')

'''),

('''final batch of minor fixes for 0.0.6''', '''
print 'he\\\\"'

class A:
    def __init__(self):
        pass

a = A()
a.__init__()

class B:
    def __init__(self, n):
        print 'b init with', n

    def huhu(self):
        self.__init__(4)

b = B(5)
b.huhu()

class C:
    def __init__(self):
        pass

c = C()


# Probably simpler OOP problems
class Pet:
    def speak(self): pass
class Cat(Pet):
    def speak(self): print "meow!"
class Dog(Pet):
    def speak(self): print "woof!"
def command(pet): pet.speak()
pets = Cat(), Dog()
for pet in pets: command(pet)
for pet in (pets[1], pets[0]): command(pet)

clearCastlingOpportunities = [None] 
clearCastlingOpportunities[0] = (10,)

board = [1,2,3]
board[0] = 0

print clearCastlingOpportunities, board

print range(-17, -120, -17)

v = -1
w = 4 

for x in range(w,-2,v):
    print x

for x in range(w+1,-2,2*v):
    print x

for x in range(0,w+1,1):
    print x

d = [i for i in xrange(10)]
print d
d[::2] = [1,2,3,4,5]
print d
d[::-2] = range(5)
print d

e = ["X" for i in xrange(10)]
e[::2] = "abcde"
print e

f = ["Y" for i in xrange(10)]
f[1::2] = tuple("abcde")
print f

def sgn(x):
    if x < 0: return -1
    else: return 1
for j in [-2, -1]:
    print [i for i in xrange(-10*sgn(j), -1*sgn(j), j) if True for k in range(2) if k]

''', '''
output(equal=True)

'''),

('''sudoku solver 3''', '''
# (c) Peter Cock
# --- http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/

TRIPLETS = [[0,1,2],[3,4,5],[6,7,8]]

ROW_ITER = [[(row,col) for col in range(0,9)] for row in range(0,9)]
COL_ITER = [[(row,col) for row in range(0,9)] for col in range(0,9)]
TxT_ITER = [[(row,col) for row in rows for col in cols] for rows in TRIPLETS for cols in TRIPLETS]

class soduko:
    def __init__(self, start_grid=None) :
        self.squares =[ [range(1,10)  for col in range(0,9)] for row in range(0,9)]
        
        if start_grid is not None:
            assert len(start_grid)==9, "Bad input!"
            for row in range(0,9) :
                self.set_row(row, start_grid[row])
                
        self._changed=False
    
    def copy(self) :
        soduko_copy = soduko(None)
        for row in range(0,9) :
            for col in range(0,9) :
                soduko_copy.squares[row][col] = self.squares[row][col][:] 
        soduko_copy._changed=False
        return soduko_copy
    
    def set_row(self,row, x_list) :
        assert len(x_list)==9, 'not 9'
        for col in range(0,9) :
            try :
                x = int(x_list[col])
            except :
                x = 0
            self.set_cell(row,col,x)

    def set_cell(self,row,col,x):
        if self.squares[row][col] == [x] :
            pass
        elif x not in range(1,9+1) :
            pass
        else:
            assert x in self.squares[row][col], "bugger2" 
            
            self.squares[row][col] = [x]
            self.update_neighbours(row,col,x)
            self._changed=True
            
    def cell_exclude(self, row,col,x) :
        assert x in range(1,9+1), 'inra'
        if x in self.squares[row][col] :
            self.squares[row][col].remove(x)
            assert len(self.squares[row][col]) > 0, "bugger"
            if len(self.squares[row][col]) == 1 :
                self._changed=True
                self.update_neighbours(row,col,self.squares[row][col][0])
        else :
            pass
        return

    def update_neighbours(self,set_row,set_col,x) :
        for row in range(0,9) :
            if row <> set_row :
                self.cell_exclude(row,set_col,x)
        for col in range(0,9) :
            if col <> set_col :
                self.cell_exclude(set_row,col,x)
        for triplet in TRIPLETS :
            if set_row in triplet : rows = triplet[:]
            if set_col in triplet : cols = triplet[:]
        rows.remove(set_row)
        cols.remove(set_col)
        for row in rows :
            for col in cols :
                assert row <> set_row or col <> set_col , 'meuh'
                self.cell_exclude(row,col,x)
            
    def get_cell_digit_str(self,row,col) :
        if len(self.squares[row][col])==1 :
            return str(self.squares[row][col][0])
        else :
            return "0"
            
    def __str__(self):
        answer = "   123   456   789\\n"
        for row in range(0,9) :
            answer = answer + str(row+1) \
                        +   " [" + "".join([self.get_cell_digit_str(row,col).replace("0","?") for col in range(0,3)]) \
                        + "] [" + "".join([self.get_cell_digit_str(row,col).replace("0","?") for col in range(3,6)]) \
                        + "] [" + "".join([self.get_cell_digit_str(row,col).replace("0","?") for col in range(6,9)]) \
                        + "]\\n"
            if row+1 in [3,6] : 
              answer = answer + "   ---   ---   ---\\n"
        return answer
                    
    def check(self) :
        self._changed=True
        while self._changed:
            self._changed=False
            self.check_for_single_occurances()
            self.check_for_last_in_row_col_3x3()
        return
        
    def check_for_single_occurances(self):
        for check_type in [ROW_ITER, COL_ITER, TxT_ITER]:
            for check_list in check_type :
                for x in range(1,9+1) : #1 to 9 inclusive
                    x_in_list = []
                    for (row,col) in check_list :
                        if x in self.squares[row][col] :
                            x_in_list.append((row,col))
                    if len(x_in_list)==1 :
                        (row,col) = x_in_list[0]
                        if len(self.squares[row][col]) > 1 :
                            self.set_cell(row,col,x)

    def check_for_last_in_row_col_3x3(self):
        for (type_name, check_type) in [("Row",ROW_ITER),("Col",COL_ITER),("3x3",TxT_ITER)]:
            for check_list in check_type :
                unknown_entries = []
                unassigned_values = range(1,9+1) #1-9 inclusive
                known_values = []
                for (row,col) in check_list :
                    if len(self.squares[row][col]) == 1 :
                        assert self.squares[row][col][0] not in known_values, "bugger3"

                        known_values.append(self.squares[row][col][0])

                        assert self.squares[row][col][0] in unassigned_values, "bugger4"

                        unassigned_values.remove(self.squares[row][col][0])
                    else :
                        unknown_entries.append((row,col))
                assert len(unknown_entries) + len(known_values) == 9, 'bugger5'
                assert len(unknown_entries) == len(unassigned_values), 'bugger6'
                if len(unknown_entries) == 1 :
                    x = unassigned_values[0]
                    (row,col) = unknown_entries[0]
                    self.set_cell(row,col,x)
        return
        
    def one_level_supposition(self):
        progress=True
        while progress :
            progress=False
            for row in range(0,9) :
                for col in range(0,9):
                    if len(self.squares[row][col]) > 1 :
                        bad_x = []
                        for x in self.squares[row][col] :
                            soduko_copy = self.copy()
                            try:
                                soduko_copy.set_cell(row,col,x)
                                soduko_copy.check()
                            except AssertionError, e :
                                bad_x.append(x)
                            del soduko_copy
                        if len(bad_x) == 0 :
                            pass
                        elif len(bad_x) < len(self.squares[row][col]) :
                            for x in bad_x :
                                self.cell_exclude(row,col,x)
                                self.check() 
                            progress=True
                        else :
                            assert False, "bugger7"


for x in range(50):
    t = soduko(["800000600",
                   "040500100",
                   "070090000",
                   "030020007",
                   "600008004",
                   "500000090",
                   "000030020",
                   "001006050",
                   "004000003"])

    t.check()
    t.one_level_supposition()
    t.check()
    print t
''', '''
output(equal=True)

'''),

('''sudoku solver 2''', '''
# (c) Peter Goodspeed
# --- coriolinus@gmail.com

from math import ceil
from time import time
import sys

class bmp(object):
        def __init__(self, vals=9*[True], n=-1):
                self.v = vals[0:9]
                if n>=0: self.v[n] = not self.v[n]
        def __and__(self, other):
                return bmp([self.v[i] and other.v[i] for i in xrange(9)])
        def cnt(self):
                return len([i for i in self.v if i])

class boardRep(object):
        def __init__(self, board):
                self.__fields = list(board.final)
        def fields(self):
                return self.__fields
        def __eq__(self, other):
                return self.__fields==other.fields()
        def __ne__(self, other):
                return self.__fields!=other.fields()
        def __hash__(self):
                rep=""
                for i in xrange(9):
                        for j in xrange(9):
                                rep += str(self.__fields[i][j])
                return hash(rep)

class board(object):
        notifyOnCompletion = True               #let the user know when you're done computing a game
        completeSearch = False                  #search past the first solution

        def __init__(self):
                #final numbers: a 9 by 9 grid
                self.final = [9 * [0] for i in xrange(9)]
                self.rows = 9 * [bmp()]
                self.cols = 9 * [bmp()]
                self.cels = [3 * [bmp()] for i in xrange(3)]

                #statistics
                self.__turns = 0
                self.__backtracks = 0
                self.__starttime = 0
                self.__endtime = 0
                self.__status = 0
                self.__maxdepth = 0
                self.__openspaces = 81

                #a set of all solved boards discovered so far
                self.solutions = set()
                #a set of all boards examined--should help reduce the amount of search duplication
                self.examined = set()

        def fread(self,fn=''):
                #self.__init__()
                if fn=='':
                        fn = raw_input("filename: ")
                f = file(fn, 'r')
                lines = f.readlines()
                for row in xrange(9):
                        for digit in xrange(1,10):
                                try:
                                        self.setval(row,lines[row].index(str(digit)),digit)
                                except ValueError:
                                        pass
                f.close()

        def setval(self, row, col, val):
                #add the number to the grid
                self.final[row][col] = val
                self.__openspaces -= 1

                #remove the number from the potential masks
                mask = bmp(n = val - 1)
                #rows and cols
                self.rows[row] = self.rows[row] & mask
                self.cols[col] = self.cols[col] & mask
                #cels
                cr = self.cell(row)
                cc = self.cell(col)
                self.cels[cr][cc] = self.cels[cr][cc] & mask

        def cell(self, num):
                return int(ceil((num + 1) / 3.0)) - 1

        def __str__(self):
                ret = ""
                for row in xrange(9):
                        if row == 3 or row == 6: ret += (((3 * "---") + "+") * 3)[:-1] + "\\n"
                        for col in xrange(9):
                                if col == 3 or col == 6: ret += "|"
                                if self.final[row][col]: c = str(self.final[row][col])
                                else: c = " "
                                ret += " "+c+" "
                        ret += "\\n"
                return ret

        def solve(self, notify=True, completeSearch=False):
                if self.__status == 0:
                        self.__status = 1
                        self.__starttime = time()
                        board.notifyOnCompletion = notify
                        board.completeSearch = completeSearch
                        self.__solve(self, 0)

        def openspaces(self):
                return self.__openspaces

        def __solve(self, _board, depth):
                global bekos
                bekos += 1
                if bekos == 5000:
                    self.onexit()
                    sys.exit()

                if boardRep(_board) not in self.examined:
                        self.examined.add(boardRep(_board))
            
                        #check for solution condition:
                        if _board.openspaces() <= 0:
                                self.solutions.add(boardRep(_board))
                                print 'sol', _board
                                if depth == 0: self.onexit()
                                if not board.completeSearch:
                                        self.onexit()

                        else:
                                #update the statistics
                                self.__turns += 1
                                if depth > self.__maxdepth: self.__maxdepth = depth

                                #figure out the mincount
                                mincnt, coords = _board.findmincounts()
                                if mincnt <= 0:
                                        self.__backtracks += 1
                                        if depth == 0: self.onexit()
                                else:
                                        #coords is a list of tuples of coordinates with equal, minimal counts
                                        # of possible values. Try each of them in turn.
                                        for row, col in coords:
                                                #now we iterate through possible values to put in there
                                                broken = False
                                                for val in [i for i in xrange(9) if _board.mergemask(row, col).v[i] == True]:
                                                        if not board.completeSearch and self.__status == 2: 
                                                            broken = True
                                                            break
                                                        val += 1
                                                        t = _board.clone()
                                                        t.setval(row, col, val)
                                                        self.__solve(t, depth + 1)
                                                #if we broke out of the previous loop, we also want to break out of
                                                # this one. unfortunately, "break 2" seems to be invalid syntax.
                                                if broken: break
                                                #else: didntBreak = True
                                                #if not didntBreak: break

        def clone(self):
                ret = board()
                for row in xrange(9):
                        for col in xrange(9):
                                if self.final[row][col]:
                                        ret.setval(row, col, self.final[row][col])
                return ret

        def mergemask(self, row, col):
                return self.rows[row] & self.cols[col] & self.cels[self.cell(row)][self.cell(col)]

        def findmincounts(self):
                #compute the list of lenghths of merged masks
                masks = []
                for row in xrange(9):
                        for col in xrange(9):
                                if self.final[row][col] == 0:
                                        numallowed = self.mergemask(row, col).cnt()
                                        masks.append((numallowed, row, col))
                #return the minimum number of allowed moves, and a list of cells which are
                # not currently occupied and which have that number of allowed moves
                return min(masks)[0], [(i[1],i[2]) for i in masks if i[0] == min(masks)[0]]

        def onexit(self):
                self.__endtime = time()
                self.__status = 2

                if board.notifyOnCompletion: print self.stats()['turns']

        def stats(self):
                if self.__status == 1: t = time() - self.__starttime
                else: t = self.__endtime - self.__starttime
                return {'max depth' : self.__maxdepth, 'turns' : self.__turns, 'backtracks' : self.__backtracks, 'elapsed time' : int(t), 'boards examined': len(self.examined), 'number of solutions' : len(self.solutions)}


bekos = 0
puzzle = board()
puzzle.fread('testdata/b6.pz')
#print puzzle
puzzle.solve()
''', '''
output('3649\\n')

'''),

('''conway game of life''', '''
# (c) (the sister of) Peter Goodspeed
# --- coriolinus@gmail.com

#plife.py - conway's game of life, with no object-orientation,
# a 20x20 non-wrapping grid, and no exceptions

#functions
def rawBoard():
        return [200 * [False] for i in xrange(200)]

#def fromKb():
#        eventLoop(lambda arg: raw_input(arg))

def nextI(qstr):
        global source
        if source == 1: #from keyboard
                return raw_input(qstr)
        elif source == 2: #from file
                global flines
                global fcur
                if fcur < len(flines):
                        ret = flines[fcur]
                        fcur += 1
                        return ret


def pb(board):
        #print board
        print "-" * 20
        for row in board:
                ro = ''
                for i in xrange(len(row)):
                        if row[i]: ro += "X"
                        else: ro += " "
                print ro
        print "-" * 20

def eventLoop(nextInput):
       cont = 'p'
       while cont.lower()[0] == 'p':
                board = rawBoard()

                #how many inputs should we expect?
                numcells = int(nextInput("how many cells? "))

                #get that many cells
                for i in xrange(numcells):
                        xy = str(nextInput("x,y: ")).split(',')
                        x,y = int(xy[0]),int(xy[1])
                        #set those cells
                        board[x][y] = True

                #pb(board)
                runSim(board)

                cont = nextInput("play again? (p for yes; anything else for no): ")

def runSim(board):
        #main loop for simulating life
        turns = 0
        ob = None # old board

        while turns < 10 and board != ob:
                turns += 1
                ob = board
                board = nextgen(board)
                #pb(board)
                #print
        if turns >= 10000: print "10 turns exhausted"
        else: print "stabilized on turn %s" % str(turns + 1)

def nextgen(board):
        #transform the old board into a new one
        nb = rawBoard()

        for rown in xrange(len(board)):
                for coln in xrange(len(board[rown])):
                        nn = 0
                        for r,c in neighbors(rown, coln):
                                if board[r][c]: nn += 1
                        if nn == 3: nb[rown][coln] = True
                        elif nn >= 4 or nn < 2: nb[rown][coln] = False
                        else: nb[rown][coln] = board[rown][coln]

        return nb

def neighbors(x,y):
        rl = []
        for mx in [-1,0,1]:
                for my in [-1,0,1]:
                        if not (mx == 0 and my == 0):
                                r = (x + mx, y + my)
                                if r[0] >= 0 and r[0] < 20 and r[1] >= 0 and r[1] < 20:
                                        rl.append(r)
        return rl

#main
source = 0
while source not in [1,2]:
        source = 2 #int(raw_input("1 for input from keyboard; 2 for input from file: "))

if source==2:
        fp = open('testdata/life.txt')
        flines = [line for line in fp]
        fp.close()
        fcur = 0

eventLoop(nextI)
''', '''
output(equal=True)

'''),


('''second batch of fixes for 0.0.6''', '''
x = '0,0'
b = str(x)
print b

a = [[1]]
c = [None, [2]]

print a == c

d = [3]; d = None
e = [4]; e = None

print d == e, None == d, e == None, a == None, c[0] == None, c[1] == None

class board(object):
    def mergemask(self): 
        print 'mergemask'

    def solve(self, board):
        global bekos
        bekos += 1

        #[board.mergemask() for x in range(1)] # XXX list(none) ..
        board.mergemask()
        board.mergemask()

bekos = 0
bo = board()
bo.solve(bo)

class heuk:
    aha = 4
    def bla(self):
        heuk.aha += 1
        self.ahah = 2
        print self.ahah, heuk.aha

h = heuk()
h.lala = 1
h.bla()

heuk.aha
heuk.aha += 1
print heuk.aha

heuk.noinit = 3
print heuk.noinit, h.ahah

class myiter:
    def __init__(self, container):
        self.container = container
        self.count = -1 
    def next(self):
        self.count +=1
        if self.count < len(self.container):
            return self.container[self.count]
        raise StopIteration

class container:
    def __init__(self):
        self.unit = range(3)
    def __getitem__(self, i):
        return self.unit[i] 
    def __iter__(self):
        return myiter(self) 
    def __len__(self):
        return len(self.unit)

def iter_(x):
    return x.__iter__()

i = iter_(container())
try:
    while 1:
        y = i.next()
        print y
except StopIteration: pass
''', '''
output('0,0\\n0\\n1 1 1 0 1 0\\nmergemask\\nmergemask\\n2 5\\n6\\n3 2\\n0\\n1\\n2\\n')

'''),


('''pygmy raytracer (slightly modified)''', '''
# (c) Dave Griffiths
# --- http://www.pawfal.org/index.php?page=PyGmy

from math import sin, cos, sqrt
import random, sys

def sq(a):
    return a*a


def conv_value(col):
    if col >= 1.0:
        return "255"
    elif col <= 0.0:
        return "0"
    else:
        return str(int(col*255.0))


class Shaderinfo:
    pass


class vec:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self,other):
        return vec(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self,other):
        return vec(self.x-other.x, self.y-other.y, self.z-other.z)

    def __mul__(self,amount):
        return vec(self.x*amount, self.y*amount, self.z*amount)

    def __div__(self,amount):
        return vec(self.x/amount, self.y/amount, self.z/amount)

    def __neg__(self):
        return vec(-self.x, -self.y, -self.z)

    def dot(self,other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def dist(self,other):
        return sqrt((other.x-self.x)*(other.x-self.x)+
                    (other.y-self.y)*(other.y-self.y)+
                    (other.z-self.z)*(other.z-self.z))

    def sq(self):
        return sq(self.x) + sq(self.y) + sq(self.z)

    def mag(self):
        return self.dist(vec(0.0, 0.0, 0.0))

    def norm(self):
        mag = self.mag()
        if mag != 0:
            self.x = self.x/mag
            self.y = self.y/mag
            self.z = self.z/mag

    def reflect(self,normal):
        vdn = self.dot(normal)*2
        return self - normal*vdn


class line:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def vec(self):
        return self.end - self.start


class renderobject:
    def __init__(self, shader):
        self.shader = shader


class plane(renderobject):
    def __init__(self, plane, dist, shader):
        renderobject.__init__(self, shader)
        self.plane = plane
        self.dist = dist

    def intersect(self,l):
        vd = self.plane.dot(l.vec())
        if vd == 0:
            return "none",(vec(0.0, 0.0, 0.0),vec(0.0, 0.0, 0.0))
        v0 = -(self.plane.dot(l.start)+self.dist)
        t = v0/vd
        if t<0 or t>1:
            return "none",(vec(0.0, 0.0, 0.0),vec(0.0, 0.0, 0.0))
        return "one", (l.start+(l.vec()*t), self.plane)


class sphere(renderobject):
    def __init__(self, pos, radius, shader):
        renderobject.__init__(self, shader)
        self.pos = pos
        self.radius = radius

    def intersect(self,l):
        lvec = l.vec()
        a = sq(lvec.x) + sq(lvec.y) + sq(lvec.z)

        b = 2*(lvec.x*(l.start.x-self.pos.x)+ \
               lvec.y*(l.start.y-self.pos.y)+ \
               lvec.z*(l.start.z-self.pos.z))

        c = self.pos.sq()+l.start.sq() - \
            2*(self.pos.x*l.start.x+self.pos.y*l.start.y+self.pos.z*l.start.z)-sq(self.radius)

        i = b*b - 4*a*c

        intersectiontype = "none"
        pos = vec(0.0, 0.0, 0.0)
        norm = vec(0.0, 0.0, 0.0)
        t = 0.0

        if i > 0:
            if i == 0:
                intersectiontype="one"
                t = -b/(2*a)
            else:
                intersectiontype="two"
                t = (-b - sqrt( b*b - 4*a*c )) / (2*a)

            if t>0 and t<1:
                pos = l.start + lvec*t
                norm = pos - self.pos
                norm.norm()
            else:
                intersectiontype="none"

        return intersectiontype, (pos, norm)


class light:
    def checkshadow(self, obj, objects,l):
        for ob in objects:
            if ob is not obj:
                intersects,(pos, norm) = ob.intersect(l)
                if intersects is not "none":
                    return 1
        return 0


class parallellight(light):
    def __init__(self, direction, col):
        direction.norm()
        self.direction = direction
        self.col=  col

    def inshadow(self, obj, objects, pos):
        l = line(pos, pos+self.direction*1000.0)
        return self.checkshadow(obj, objects,l)

    def light(self, shaderinfo):
        if self.inshadow(shaderinfo.thisobj, shaderinfo.objects, shaderinfo.position):
            return vec(0.0, 0.0, 0.0)
        return self.col*self.direction.dot(shaderinfo.normal)


class pointlight(light):
    def __init__(self, position, col):
        self.position = position
        self.col = col

    def inshadow(self, obj, objects, pos):
        l = line(pos, self.position)
        return self.checkshadow(obj, objects,l)

    def light(self, shaderinfo):
        if self.inshadow(shaderinfo.thisobj, shaderinfo.objects, shaderinfo.position):
            return vec(0.0, 0.0, 0.0)
        direction = shaderinfo.position - self.position
        direction.norm()
        direction = -direction
        return self.col*direction.dot(shaderinfo.normal)


class shader:
    def getreflected(self, shaderinfo):
        depth = shaderinfo.depth
        col = vec(0.0, 0.0, 0.0)
        if depth > 0:
            lray = line(shaderinfo.ray.start, shaderinfo.ray.end) #copy.copy(shaderinfo.ray)
            ray = lray.vec()
            normal = vec(shaderinfo.normal.x, shaderinfo.normal.y, shaderinfo.normal.z) #copy.copy(shaderinfo.normal)

            ray = ray.reflect(normal)
            reflected = line(shaderinfo.position,shaderinfo.position+ray)
            obj = shaderinfo.thisobj
            objects = shaderinfo.objects

            newshaderinfo = Shaderinfo() #copy.copy(shaderinfo) # XXX
            newshaderinfo.thisobj = shaderinfo.thisobj
            newshaderinfo.objects = shaderinfo.objects
            newshaderinfo.lights = shaderinfo.lights
            newshaderinfo.position = shaderinfo.position
            newshaderinfo.normal = shaderinfo.normal

            newshaderinfo.ray = reflected
            newshaderinfo.depth = depth - 1

            # todo - depth test
            for ob in objects:
                if ob is not obj:
                    intersects,(position,normal) = ob.intersect(reflected)
                    if intersects is not "none":
                        newshaderinfo.thisobj = ob
                        newshaderinfo.position = position
                        newshaderinfo.normal = normal
                        col = col + ob.shader.shade(newshaderinfo)
        return col

    def isoccluded(self, ray, shaderinfo):
        dist = ray.mag()
        test = line(shaderinfo.position, shaderinfo.position+ray)
        obj = shaderinfo.thisobj
        objects = shaderinfo.objects
        # todo - depth test
        for ob in objects:
            if ob is not obj:
                intersects,(position,normal) = ob.intersect(test)
                if intersects is not "none":
                    return 1
        return 0

    def doocclusion(self, samples, shaderinfo):
        # not really very scientific, or good in any way...
        oc = 0.0
        for i in xrange(samples):
            ray = vec(float(random.randrange(-100,100)),float(random.randrange(-100,100)),float(random.randrange(-100,100)))
            ray.norm()
            ray = ray * 2.5
            if self.isoccluded(ray, shaderinfo):
                oc = oc + 1
        oc = oc / float(samples)
        return 1-oc

    def shade(self,shaderinfo):
        col = vec(0.0, 0.0, 0.0)
        for lite in shaderinfo.lights:
            col = col + lite.light(shaderinfo)
        return col


class world:
    def __init__(self,width,height):
        self.lights = []
        self.objects = []
        self.cameratype = "persp"
        self.width = width
        self.height = height
        self.backplane = 2000.0
        self.imageplane = 5.0
        self.aspect = self.width/float(self.height)

    def render(self, filename):
        out_file = file(filename, 'w')
        # PPM header
        print >>out_file, "P3"
        print >>out_file, self.width, self.height
        print >>out_file, "256"
        total = self.width * self.height
        count = 0

        for sy in xrange(self.height):
            pixel_line = []
            for sx in xrange(self.width):
                x = 2 * (0.5-sx/float(self.width)) * self.aspect
                y = 2 * (0.5-sy/float(self.height))
                if self.cameratype=="ortho":
                    ray = line(vec(x, y, 0.0),vec(x, y, self.backplane))
                else:
                    ray = line(vec(0.0, 0.0, 0.0),vec(x, y, self.imageplane))
                    ray.end=ray.end*self.backplane

                col = vec(0.0, 0.0, 0.0)
                depth = self.backplane
                shaderinfo = Shaderinfo() #{"ray":ray,"lights":self.lights,"objects":self.objects,"depth":2}
                shaderinfo.ray = ray
                shaderinfo.lights = self.lights
                shaderinfo.objects = self.objects
                shaderinfo.depth = 2

                for obj in self.objects:
                    intersects,(position,normal) = obj.intersect(ray)
                    if intersects is not "none":
                        if position.z<depth and position.z>0:
                            depth = position.z
                            shaderinfo.thisobj = obj
                            shaderinfo.position = position
                            shaderinfo.normal = normal
                            col = obj.shader.shade(shaderinfo)

                pixel_line.append( conv_value(col.x) )
                pixel_line.append( conv_value(col.y) )
                pixel_line.append( conv_value(col.z) )
                count = count + 1

            print >>out_file, " ".join(pixel_line)
            percentstr = str(int((count/float(total))*100))+"%"
            print "\b\b\b" + percentstr
        out_file.close()


class everythingshader(shader):
    def shade(self,shaderinfo):
        col = shader.shade(self,shaderinfo)
        ref = self.getreflected(shaderinfo)
        col = col*0.5+ref*0.5
        return col*self.doocclusion(10,shaderinfo)


class spotshader(shader):
    def shade(self,shaderinfo):
        col = shader.shade(self, shaderinfo)
        position = shaderinfo.position
        jitter = sin(position.x) + cos(position.z)
        if jitter > 0.5:
            col = col / 2
        ref = self.getreflected(shaderinfo)
        return ref*0.5 + col*0.5*self.doocclusion(10,shaderinfo)


# Main
# Give sixe x and y of the image
if len(sys.argv) == 3:
    nx, ny = int(sys.argv[1]), int(sys.argv[2])
else:
    nx, ny = 160, 120
w = world(nx, ny)
numballs = 10.0
offset = vec(0.0,-5.0,55.0)
rad = 12.0
radperball = (2 * 3.141592) / numballs

for i in xrange(int(numballs)):
    x = sin(0.3+radperball*float(i))*rad
    y = cos(0.3+radperball*float(i))*rad
    w.objects.append(sphere(vec(x,0.0,y)+offset,2.0,everythingshader()))

w.objects.append(sphere(vec(3.0,3.0,0.0)+offset,5.0,everythingshader()))
w.objects.append(plane(vec(0.0,1.0,0.0),7.0, spotshader()))
w.lights.append(parallellight(vec(1.0,1.0,-1.0), vec(0.3,0.9,0.1)))
w.lights.append(pointlight(vec(5.0,100.0,-5.0), vec(0.5,0.5,1.0)))

w.render('test.ppm')
''', '''
output()

'''),

('''genetic algorithm''', '''
# (c) Bearophile

from random import random, randint, choice
from math import sin, pi
from copy import copy 

infiniteNeg = -1e302


class Individual:
    def __init__(self, ngenes):
        self.ngenes = ngenes
        self.genome = [random()<0.5 for i in xrange(ngenes)]
        self.fitness = infiniteNeg
    def bin2dec(self, inf=0, sup=0): # Sup has to be None, SS workaround *************
        if sup == 0: sup = self.ngenes - 1 # if sup is None: ...
        result = 0
        for i in xrange(inf, sup+1):
            if self.genome[i]:
                result += 1 << (i-inf)
        return result
    def computeFitness(self):
        self.fitness = self.fitnessFun(self.computeValuesGenome())
    def __repr__(self):
        return "".join([str(int(gene)) for gene in self.genome])

    def fitnessFun(self, x):
        return x + abs(sin(32*x))
    def computeValuesGenome(self, xMin=0, xMax=pi):
        scaleFactor = (xMax-xMin) / (1<<self.ngenes)
        return self.bin2dec() * scaleFactor


class SGA:
    def __init__(self):
        self.popSize = 200            # Ex. 200
        self.genomeSize = 16          # Ex. 16
        self.generationsMax = 16      # Ex. 100
        self.crossingOverProb = 0.75  # In [0,1] ex. 0.75
        self.selectivePressure = 0.75 # In [0,1] ex. 0.75
        self.geneMutationProb = 0.005  # Ex. 0.005

    def generateRandomPop(self):
        self.population = [Individual(self.genomeSize) for i in xrange(self.popSize)]

    def computeFitnessPop(self):
        for individual in self.population:
            individual.computeFitness()

    def mutatePop(self):
        nmutations = int(round(self.popSize * self.genomeSize * self.geneMutationProb))
        for i in xrange(nmutations):
            individual = choice(self.population) # don't forget to import choice too :D
            gene = randint(0, self.genomeSize-1)
            individual.genome[gene] = not individual.genome[gene] # this was a type inference problem.. thanks for detecting it! :) the aux variable you used, btw.. was polymorphic, both boolean and Individual

    def tounamentSelectionPop(self):
        pop2 = []
        for i in xrange(self.popSize):
            individual1 = choice(self.population) 
            individual2 = choice(self.population)
            if random() < self.selectivePressure:
                if individual1.fitness > individual2.fitness:
                    pop2.append(individual1)
                else:
                    pop2.append(individual2)
            else:
                if individual1.fitness > individual2.fitness:
                    pop2.append(individual2)
                else:
                    pop2.append(individual1)
        return pop2 # fixed

    def crossingOverPop(self):
        nCrossingOver = int(round(self.popSize * self.crossingOverProb))
        for i in xrange(nCrossingOver):
            ind1 = choice(self.population) 
            ind2 = choice(self.population) 
            crossPosition = randint(0, self.genomeSize-1)
            for j in xrange(crossPosition+1):
                ind1.genome[j], ind2.genome[j] = ind2.genome[j], ind1.genome[j]

    def showGeneration_bestIndFind(self):
        fitnessTot = 0.0
        bestIndividualGeneration = self.population[0]
        for individual in self.population:
            fitnessTot += individual.fitness
            if individual.fitness > bestIndividualGeneration.fitness:
                bestIndividualGeneration = individual
        if self.bestIndividual.fitness < bestIndividualGeneration.fitness:
            self.bestIndividual = copy(bestIndividualGeneration) # shallow copies should work now..


    def run(self):
        self.generateRandomPop()
        self.bestIndividual = Individual(self.genomeSize)
        for self.generation in xrange(1, self.generationsMax+1): # works now
            self.computeFitnessPop()
            self.showGeneration_bestIndFind()
            self.population = self.tounamentSelectionPop()  
            self.mutatePop()
            self.crossingOverPop()

sga = SGA()
sga.generationsMax = 3000
sga.genomeSize = 20
sga.popSize = 30
sga.geneMutationProb = 0.01
sga.run()
''', '''
output()

'''),

('''linear algebra routines''', '''
# (c) Mladen Bestvina

import copy

def inner_prod(v1, v2):
     'inner production of two vectors.'
     sum = 0
     for i in xrange(len(v1)):
            sum += v1[i] * v2[i]
     return sum

def matmulttransp(M, N):
     'M*N^t.'
     return [[inner_prod(v, w) for w in N] for v in M]

def col(M,j):
     v=[]
     rows=len(M)
     for i in xrange(rows):
          v.append(M[i][j])
     return v

def Transpose(M):
     N=[]
     cols=len(M[0])
     for i in xrange(cols):
          N.append(col(M,i))
     return N

def Minor(M,i,j):
     M1=copy.deepcopy(M)
     N=[v.pop(j) for v in M1]
     M1.pop(i)
     return M1

def sign(n):
     return 1-2*(n-2*(n/2))

def determinant(M):
     size=len(M)
     if size==1: return M[0][0]
     if size==2: return M[0][0]*M[1][1]-M[0][1]*M[1][0] # 1x1 Minors don't work
     det=0
     for i in xrange(size):
                    
          det += sign(i)*M[0][i]*determinant(Minor(M,0,i))
     return det
     
def inverse(M):
     size=len(M)
     det=determinant(M)
     if abs(det) != 1: print "error, determinant is not 1 or -1"
     N=[]
     for i in xrange(size):
          v=[]
          for j in xrange(size):
               v.append(det*sign(i+j)*determinant(Minor(M,j,i)))
          N.append(v)
     return N
     
def iterate_sort(list1,A,B,C,D,E,F):
    n=len(list1)
    for i in range(n):
        z=matmulttransp(list1[i],A)
        list1.append(z)
        z=matmulttransp(list1[i],B)

        list1.append(z)
        z=matmulttransp(list1[i],C)

        list1.append(z)
        z=matmulttransp(list1[i],D)

        list1.append(z)
        z=matmulttransp(list1[i],E)

        list1.append(z)
        z=matmulttransp(list1[i],F)

        list1.append(z)

    list1.sort()
    n=len(list1)
    last = list1[0]
    lasti = i = 1
    while i < n:
        if list1[i] != last:
            list1[lasti] = last = list1[i]
            lasti += 1
        i += 1
    list1.__delslice__(lasti,n)
        
def gen(n,list1,A,B,C,D,E,F):
    for i in range(n): iterate_sort(list1,A,B,C,D,E,F)

def inward(U):
    b01=(abs(U[0][0])<abs(U[0][1])) or \
    ((abs(U[0][0])==abs(U[0][1]) and abs(U[1][0])<abs(U[1][1]))) or \
    ((abs(U[0][0])==abs(U[0][1]) and abs(U[1][0])==abs(U[1][1]) and \
     abs(U[2][0])<abs(U[2][1])))

    b12=(abs(U[0][1])<abs(U[0][2])) or \
    ((abs(U[0][1])==abs(U[0][2]) and abs(U[1][1])<abs(U[1][2]))) or \
    ((abs(U[0][1])==abs(U[0][2]) and abs(U[1][1])==abs(U[1][2]) and \
     abs(U[2][1])<abs(U[2][2])))

    return b01 and b12

def examine(U,i,j):
    row1=abs(i)-1
    row2=j-1
    s=1
    if i<0: s=-1
    diff=abs(U[0][row1]+s*U[0][row2])-abs(U[0][row2])
    if diff<0: return -1
    if diff>0: return 1
    else:
        diff=abs(U[1][row1]+s*U[1][row2])-abs(U[1][row2])
        if diff<0: return -1
        if diff>0: return 1
        else:
            diff=abs(U[2][row1]+s*U[2][row2])-abs(U[2][row2])
            if diff<0: return -1
            if diff>0: return 1
            else: return 0

def examine3(U,i,j,k):
    row1=abs(i)-1
    row2=abs(j)-1
    row3=k-1
    s1=1
    s2=1
    if i<0: s1=-1
    if j<0: s2=-1
    diff=abs(s1*U[0][row1]+s2*U[0][row2]+U[0][row3])-abs(U[0][row3])
    if diff<0: return -1
    if diff>0: return 1
    else:
        diff=abs(s1*U[1][row1]+s2*U[1][row2]+U[1][row3])-abs(U[1][row3])
        if diff<0: return -1
        if diff>0: return 1
        else:
            diff=abs(s1*U[2][row1]+s2*U[2][row2]+U[2][row3])-abs(U[2][row3])
            if diff<0: return -1
            if diff>0: return 1
            else: return 0

def binary(n):
    if n==0: return 0
    if n==1: return 1
    m=n/2
    if 2*m==n: return 10*binary(m)
    else: return 10*binary(m)+1 
     
length=6 # wordlength

b=[[0,0,1],[0,1,0],[1,0,0]] 

A=[[1,1,0],[0,1,0],[0,0,1]]
B=inverse(A)
C=[[1,0,0],[0,1,1],[0,0,1]]
D=inverse(B)
E=[[1,0,0],[0,1,0],[1,0,1]]
F=inverse(E)

At=Transpose(A)
Bt=Transpose(B)
Ct=Transpose(C)
Dt=Transpose(D)
Et=Transpose(E)
Ft=Transpose(F)

bt=Transpose(b)

def descending(U):
    type=0

    r=examine(U,1,2)
    if r==0: return 1024
    if r==-1: type=type+1

    r=examine(U,-1,2)
    if r==0: return 1024
    if r==-1: type=type+2

    r=examine(U,1,3)
    if r==0: return 1024
    if r==-1: type=type+4

    r=examine(U,-1,3)
    if r==0: return 1024
    if r==-1: type=type+8

    r=examine(U,2,3)
    if r==0: return 1024
    if r==-1: type=type+16

    r=examine(U,-2,3)
    if r==0: return 1024
    if r==-1: type=type+32

    r=examine3(U,1,2,3)
    if r==0: return 1024
    if r==-1: type=type+64

    r=examine3(U,-1,-2,3)
    if r==0: return 1024
    if r==-1: type=type+128

    r=examine3(U,-1,2,3)
    if r==0: return 1024
    if r==-1: type=type+256

    r=examine3(U,1,-2,3)
    if r==0: return 1024
    if r==-1: type=type+512

    return type

def main2():
    list1=[bt]
    gen(length,list1,A,B,C,D,E,F)
    inlist=[x for x in list1 if inward(x)]
    types=[0]*1025
    for U in inlist:
        t=descending(U)
        types[t]+=1
        if t in [22,25,37,42,6,9,73,262]:
            pass #print t,U
    #print
    for t in reversed(range(1025)):
        if types[t]>0:
            print t, binary(t), types[t]
            break
            #print(' %03i   %012i   %i  ' %(t,binary(t),types[t]))

for x in range(10):
    main2()
''', '''
output(equal=True)


'''),

('''tic-tac-toe on arbitrary-size boards''', '''
# (c) Peter Goodspeed
# --- coriolinus@gmail.com

#import random
from math import exp
#from sets import Set
#set = Set

#functions
def sigmoid(x):
        return float(1)/(1 + exp(-x))

def sig(x, xshift=0, xcompress=1):
        return 0 + (1 * sigmoid(xcompress * (x - xshift)))

#exceptions
class SpaceNotEmpty(Exception):
        pass

class MultiVictory(Exception):
        def __init__(self, victorslist):
                self.victors = victorslist

#classes
class rectBoard(object):
        def __init__(self, edge=3):
                self.edge = edge
                self.__board = [edge * [0] for i in xrange(edge)]
                self.__empty = edge**2

        def assign(self, row, col, value):
                if(self.__board[row][col] == 0):
                        self.__board[row][col] = value
                        self.__empty -= 1
                else:
                        raise SpaceNotEmpty()

        def isfull(self):
                return self.__empty == 0

        #def valueof(self, row, col):
        #        return self.__board[row][col]

        def isvictory(self):
                victors = []
                #examine rows
                for row in self.__board:
                        if len(set(row)) == 1:
                                if row[0] != 0: victors.append(row[0])

                #examine cols
                for i in xrange(self.edge):
                        col = [row[i] for row in self.__board]
                        if len(set(col)) == 1:
                                if col[0] != 0: victors.append(col[0])

                #examine diagonals
                #left diagonal
                ld = []
                for i in xrange(self.edge): ld.append(self.__board[i][i])
                if len(set(ld)) == 1:
                        if ld[0] != 0: victors.append(ld[0])

                #right diagonal
                rd = []
                for i in xrange(self.edge): rd.append(self.__board[i][self.edge-(1+i)])
                if len(set(rd)) == 1:
                        if rd[0] != 0: victors.append(rd[0])

                #return
                if len(victors) == 0:
                        return 0
                if len(set(victors)) > 1:
                        raise MultiVictory(set(victors))
                return victors[0]

        def __str__(self):
                ret = ""
                for row in xrange(self.edge):
                        if row != 0:
                                ret += "\\n"
                                for i in xrange(self.edge):
                                        if i != 0: ret += '+'
                                        ret += "---"
                                ret += "\\n"
                        ret += " "
                        for col in xrange(self.edge):
                                if col != 0: ret += " | "
                                if self.__board[row][col] == 0: ret += ' '
                                else: ret += str(self.__board[row][col])
                return ret

        def doRow(self, fields, indices, player, scores):
                players = set(fields).difference(set([0]))

                if(len(players) == 1):
                        if list(players)[0] == player:
                                for rown, coln in indices:
                                        scores[rown][coln] += 15 * sig(fields.count(player) / float(self.edge), .5, 10)
                        else:
                                for rown, coln in indices:
                                        scores[rown][coln] += 15 * fields.count(list(players)[0]) / float(self.edge)

        def makeAImove(self, player):
                scores = [self.edge * [0] for i in xrange(self.edge)]

                for rown in xrange(self.edge):
                        row = self.__board[rown]
                        self.doRow(row, [(rown, i) for i in xrange(self.edge)], player, scores)

                for coln in xrange(self.edge):
                        col = [row[coln] for row in self.__board]
                        self.doRow(col, [(i, coln) for i in xrange(self.edge)], player, scores)

                indices = [(i, i) for i in xrange(self.edge)]
                ld = [self.__board[i][i] for i in xrange(self.edge)]
                self.doRow(ld, indices, player, scores)
                #also, because diagonals are just more useful
                for rown, coln in indices:
                        scores[rown][coln] += 1

                #now, we do the same for right diagonals
                indices = [(i, (self.edge - 1) - i) for i in xrange(self.edge)]
                rd = [self.__board[i][(self.edge - 1) - i] for i in xrange(self.edge)]
                self.doRow(rd, indices, player, scores)
                #also, because diagonals are just more useful
                for rown, coln in indices:
                        scores[rown][coln] += 1

                scorelist = []
                for rown in xrange(self.edge):
                        for coln in xrange(self.edge):
                                if(self.__board[rown][coln] == 0):
                                        scorelist.append((scores[rown][coln],(rown,coln)))
                scorelist.sort()
                scorelist.reverse()
                #print scorelist
                scorelist = [x for x in scorelist if x[0] == scorelist[0][0]]

                #return random.choice([(x[1], x[2]) for x in scorelist])

                #scorelist = [(random.random(), x[1],x[2]) for x in scorelist]
                #scorelist.sort()

                return (scorelist[0][1][0], scorelist[0][1][1])


def aigame(size=30, turn=1, players=2):
        b = rectBoard(size)

        while((not b.isfull()) and (b.isvictory() == 0)):
                if(turn==1):
                        #player turn
                        #print
                        #print b
                        r, c = b.makeAImove(turn)
                        b.assign(r,c,1)
                        turn = 2
                else:
                        #computer turn
                        r, c = b.makeAImove(turn)
                        b.assign(r,c,turn)
                        if(turn == players): turn = 1
                        else: turn += 1
        #print
        #print b.__str__()
        #print
        if(b.isvictory() == 0):
                print "Board is full! Draw!"
        else:
                print "Victory for player "+str(b.isvictory())+"!"

aigame()
''', '''
output('Board is full! Draw!\\n')

'''),

('''exception handling''', '''
class meuk: pass

try:
    raise meuk()
    print 'bad!'
except meuk:
    print 'ok!'
except int:
    print 'bad..'

try:
    assert 1 == 0
except AssertionError:
    print 'crap!'

def crapfunction():
    a,b,c=1,2,3
    assert a > b < c, "the universe won't collapse"
try: 
    crapfunction()
except AssertionError, msg:
    print 'more crap!', msg
     
class ueuk:
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        return 'ueukrepr!'

try:
    raise ueuk, 'aha! error.'
except ueuk, x:
    print x.msg
    
try:
    raise ueuk('aha! error.')
except ueuk, x:
    print x

try:
    hum = [1,2,3]
    print hum.index(4)
except ValueError:
    print 'exceptions are stupid :D'

try:
    raise ValueError('exceptions are stupid :D')
except ValueError, y:
    print y

try:
    {1:2}[3]
except KeyError, z:
    print 'bah!', z

try:
    [1].index(2)
except ValueError, v:
    print 'hah', v

''', '''
output("ok!\\ncrap!\\nmore crap! the universe won't collapse\\naha! error.\\nueukrepr!\\nexceptions are stupid :D\\nexceptions are stupid :D\\nbah! 3\\nhah list.index(x): x not in list\\n")

'''),

('''bearophile inheritance tests''', '''
class C1:
  def m1(self): self.a1 = 1
  def m2(self): self.a2 = 2
class C2(C1):
  def m2(self): self.a = 3
class C3(C2):
  def m2(self): self.a2 = 4
c3 = C3()
c3.m1()
c3.m2()
print c3.a1, c3.a2
''', '''
output('1 4\\n')

'''),

('''slice assignments''', '''
v = [1, 2, 3, 4]
v[1:3] = [5, 6, 7]
print v

v = [1, 2, 3, 4]
v[:] = [1, 2, 3, 4, 5]
print v

v = [1, 2, 3, 4]
v[1:3] = [5]
print v

v = [1, 2, 3, 4]
v[:] = []
print v

v = [1, 2, 3, 4]
del v[:]
print v

def bla(x): return x
u = [1,2,3,4]
bla(u)[1:3] = [5, 6, 7]
print u

w = []
w[:] = [1,2]
print w
''', '''
output('[1, 5, 6, 7, 4]\\n[1, 2, 3, 4, 5]\\n[1, 5, 4]\\n[]\\n[]\\n[1, 5, 6, 7, 4]\\n[1, 2]\\n')

'''),

('''some const/comparisons''', '''
class huhuhu: 
    pass

obj = huhuhu()
if obj is obj:
    print 'ok1'
if obj is not None:
    print 'ok2'

obj = None
if obj is None:
    print 'ok3'
if obj == None:
    print 'ok4'
if obj is not None:
    print 'bad'
if obj != None:
    print 'bad'

if not obj:
    print 'ok5'

bla = "hoei"
if bla == 'hoei':
    print 'ok6'
if bla is 'hoei':
    print 'ok7'
if bla != 'meuk':
    print 'ok8'
if bla is not 'meuk':
    print 'ok9'
''', '''
output(''.join(['ok%d\\n'%n for n in range(1,10)]))

'''),

('''inheritance in pygmy III''', '''
class renderobject:
	def intersect(self,l):
		return "none", (l, l)

class plane(renderobject):
	def intersect(self,l):		
		return "one", (l, l)
	
class sphere(renderobject):
    def intersect(self,l):
        return "none", (l, l)

p = plane()
s = sphere()

print p.intersect(1)
print s.intersect(2)

meuk = [p, s]
for obj in meuk:
    print obj.intersect(1)
''', '''
output("('one', (1, 1))\\n('none', (2, 2))\\n('one', (1, 1))\\n('none', (1, 1))\\n")

'''),

('''inheritance in pygmy II''', '''
class renderobject: pass
class plane(renderobject): pass
class sphere(renderobject): pass

class light: 
    def hoei(self): print 'hoei!'

class parallellight(light): pass
class pointlight(light): pass

objects = []
objects.append(plane())
objects.append(sphere())

lights = []
lights.append(parallellight())
lights.append(pointlight())

lights[0].hoei()
''', '''
output('hoei!\\n')

'''),

('''inheritance in pygmy I''','''
class renderobject:
	def __init__(self, shader):
		self.shader=shader		
	
class plane(renderobject):
	def __init__(self,plane,dist,shader):
		renderobject.__init__(self,shader)
		self.plane=plane
		self.dist=dist
		
class sphere(renderobject):
	def __init__(self, pos, radius, shader):
		renderobject.__init__(self,shader)
		self.pos=pos
		self.radius=radius

class world:
    def __init__(self):
        self.objects = []

w = world()
w.objects.append(plane(6,7,8))
w.objects.append(sphere(6,7,8))
''', '''
output()

'''),

('''some basic inheritance''', '''
class father(object):
    def __init__(self,a):
        self.a=a
        b=1
    def f(self,x):
	    return x*self.a

class son(father):
    def g(self,x):
        return x*self.a*self.a

myfather=father(3)
print myfather.f(4)
myson=son(4)
print myson.g(5)

class mother(object):
    def __init__(self,a):
        self.a=a
        b=1
    def f(self,x):
	    return x*self.a

class daughter(mother):
    def g(self,x):
        return x*self.a*self.a

mydaughter = daughter(4)
print mydaughter.g(5)

''', '''
output('12\\n80\\n80\\n')

'''),
    
('''collection of minor fixes for 0.0.6''', '''
def gen():
    m = []
    l = [1]
    m.append(l)

    return m

m = gen()
print m

z=1 and 1

a = range(10)
a.__delslice__(1,4)
print a

import copy

b=[[0,1]] 

c=copy.deepcopy(b)
c[0].pop(0)

print c, b

AH = [1,2]
print [[1 for x in AH] for y in AH]

for x in xrange(2,1,-1):
    print x

print []*10

a = range(5); del a[0:2]; print a

class Individual:
    def __init__(self, ngenes): self.genome = [True] * ngenes
individual = Individual(3)
individual.genome[1] = not individual.genome[1]
print individual.genome

#d,e = -1e500, 1e500; print d, e

if not (1==2 or 2==3):
    print 'jammer'

class wahoe:
    def hoe(self):
        for self.smurf in range(3):
            print self.smurf

wahoe().hoe()

def fun():
    global aa
    aa += 1
    return 200
aa = 1
print aa
print 97 <= fun() <= 122
print aa
print 200 == fun() == 150
print aa

def true(): return True

print true() == true() in [True]
print 1 < 2 < 3 < 4

print 'hash(l)', [hash(i) for i in xrange(3)]
print 'hash(float(l))', [hash(float(i)) for i in xrange(3)]

class Toggle:
    def __init__(self, start_state):
        self.bool = start_state
    def value(self):
        return(self.bool)
    def activate(self):
        self.bool = not self.bool
        return(self)
t = Toggle(True)
print t.value()
t.activate()
print t.value()

print [None for i in xrange(3)]

maxint = 2147483647
minint = -maxint-1
print maxint
print minint

s1 = set((1,2,3)); s4 = set([1,4]); print s4 > s1, s4 >= s1

#python 2.4
#print set([1,2,3]).issubset((1,2,3))
#print set([1,2,3]).issuperset((1,2,3))

s1 = set((1,2,3)); s2 = set([1,4]); print sorted(set((1,2,3)) & set([1,4]))
s1 = set((1,2,3)); s2 = set([1,4]); s3 = set([5]); print sorted(s1 | s2 | s3) # associativity
print sorted(set([1,2]).union((2,)).union([3]))
s5 = set("abcd"); s6 = set("cdef"); print sorted(s5 ^ s6) # mixing
print

s1 &= s2
print sorted(s2)
s1 -= s2
print sorted(s1)
s1 ^= s2
print sorted(s1)

s7 = set([(1,2),(1,3),(1,4)])
s7 |= set([(1,6)]) # not (1,6)
print sorted(s7)

ah = [(2.1, 4), (1.0, 9), (1.0, 7)]
ah.sort()
print ah

p, q, r = set('ab'), set('abcde'), set('def')
print q <= q, q > r, q >= r

y = ("a", "b", "c")
zed = "a"
print zed is y[0]

class Printer:
    def __str__(self): return "10"
    def __repr__(self): return "20"
pr = Printer(); print Printer(), pr, repr(pr)

class Printer2:
    def __repr__(self): return "20"
print Printer2(), repr(Printer2())

class Printer3:
    pass

print Printer3()

def test(): pass
print test()

l = []; print [l.append(i%2) for i in xrange(5)]

def test2(x):
    if x:
        return (1,"a")
print test2(1)
print test2(0)

uh = [1]
uh = None
print uh

def fun3(): a = 1
result = fun3()
print result

s = dict.fromkeys(xrange(2))
for i in xrange(2):
    if i in s: print "*"

b2 = 3; b2 *= 1.5; print '%.1f' % b2

class A:
  def __init__(self, a): self.a = a
  def __add__(self, V): return A(self.a+V.a)
  def __mul__(self, n): return A(self.a*n)

v = A(1); v += A(2); print v.a
v = A(1) + A(2); print v.a
print (v * 2).a
v *= 2; print v.a

def mut1(aap=[1]):
    aap.append(2)
    print aap
mut1(); mut1(); mut1()

def mut2(a=None):
    if a is None:
        a = []
    print a
    a.append("*")
mut2(); mut2(); mut2()

def fun2(a, b=4, c='1'): 
    return (a+b)*c
print fun2(c='2', a=3, b=4), fun2(a=1, b=2, c='8')

def fun4(a, b=7, c='1', d=1, e=1.0):
    print a, b, c, d, int(e)

fun4(1,2,e=2.0,c='8')

''', '''
output("[[1]]\\n[0, 4, 5, 6, 7, 8, 9]\\n[[1]] [[0, 1]]\\n[[1, 1], [1, 1]]\\n2\\n[]\\n[2, 3, 4]\\n[1, 0, 1]\\njammer\\n0\\n1\\n2\\n1\\n0\\n2\\n0\\n3\\n1\\n1\\nhash(l) [0, 1, 2]\\nhash(float(l)) [0, 49152, 81920]\\n1\\n0\\n[0, 0, 0]\\n2147483647\\n-2147483648\\n0 0\\n[1]\\n[1, 2, 3, 4, 5]\\n[1, 2, 3]\\n['a', 'b', 'e', 'f']\\n\\n[1, 4]\\n[]\\n[1, 4]\\n[(1, 2), (1, 3), (1, 4), (1, 6)]\\n[(1.0, 7), (1.0, 9), (2.1, 4)]\\n1 0 0\\n1\\n10 10 20\\n20 20\\nPrinter3 instance\\n0\\n[0, 0, 0, 0, 0]\\n(1, 'a')\\n0\\n0\\n0\\n*\\n*\\n4.5\\n3\\n3\\n6\\n6\\n[1, 2]\\n[1, 2, 2]\\n[1, 2, 2, 2]\\n[]\\n[]\\n[]\\n2222222 888\\n1 2 8 1 2\\n")

'''),

('''more minor fixes''', '''
x = [0,1]
i, x[i] = 1, 2
print x

from math import *
sin(pi)

print repr('    '.strip())

print 'a\\vb'.split()

s1={1:"a",2:"b"}; s2={1:"a",2:"b"}; print s1 == s2, s1 != s2

print "ab cd\\tef\\ngh\\ril\\vmn\\fop".split()

a=2; b=3; print bool(a==b)

def test():
    s1, s2 = "ab", "AB"
    alist = ["_"] * 2 
    for pos in range(2):
        alist[ord(s1[pos])-ord('a')] = s2[pos]
    return alist
print test()

def f(s): return [s[0] for j in xrange(1)]

print [(i,j+k) for (k,j) in enumerate(xrange(3)) for i in xrange(j) for z in range(2)]

print "a".join(["a","b"])
"".join(set(["he", "oh"]))
"**".join({" oh":1, "he":0})

''','''
output("[0, 2]\\n''\\n['a', 'b']\\n1 0\\n['ab', 'cd', 'ef', 'gh', 'il', 'mn', 'op']\\n0\\n['A', 'B']\\n[(0, 2), (0, 2), (0, 4), (0, 4), (1, 4), (1, 4)]\\naab\\n")

'''),

('''list comprehension problem: parents''', '''
class node:    
    def __init__(self):     
        self.input = [8]

def incoming(node): 
    return [link for link in node.input] 

print incoming(node())
''', '''
output('[8]\\n')

'''),

('''collection of minor fixes for 0.0.5''', '''
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

""" "\\n\\t" """
print """ "\\n\\t" """

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

import random as rr
from random import randint as ri
#print rr.randint(0,0), rr.randint(0,2), ri(8, 12)

def union(): pass
union()

for (i,ee) in reversed(list(enumerate(reversed([1,2,3])))):
    print i, ee

print set([1,2,3]).symmetric_difference(set([2,3,4]))

print {1:2, 2:3}.copy()

ff = file('testdata/bla','w')
print >>ff, 'niet op scherm'
print >>file('testdata/bla2','w'), 'huhuhu'

ss = "abcdefghijklmnopqrst"; print ss[2:9:2]
mm = [""]; print ["*" for c in mm if c]

print "yxxy".split("x")
print "   ".split(" ")
print "hopplop".split("op")
print "x\\t\\nxxx\\r".split()

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
        return 1
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
''', '''
#output("hello, world!\\n['\\\\r', 'a', 'h']\\n['\\\\r', 'b', 'c']\\n['\\\\r', 'c', 'd', 'e']\\n12 255 16\\n255 255 ff 12\\n \\"\\n\\t\\" \\nset([1])\\nset([1, 2, 3])\\n[1, 2, 3]\\n3\\n2\\n1\\na b\\na b c d e\\na b\\na b c d e\\n3\\nset([1, 2, 3]) - set([3, 4, 5]) = set([1, 2]) = set([1, 2])\\nset([1, 2]) set([])\\nset([]) 1 1\\n1\\nset([1, 2])\\nset([1, 2])\\n1\\n2\\n3\\n2 1\\n1 2\\n0 3\\nset([1, 4])\\n{1: 2, 2: 3}\\ncegi\\n[]\\n['y', '', 'y']\\n['', '', '', '']\\n['h', 'pl', '']\\n['x', 'xxx']\\nCNF\\n['\\\\xf6', '\\\\xf7', '\\\\xf8', '\\\\xf9', '\\\\xfa', '\\\\xfb', '\\\\xfc', '\\\\xfd', '\\\\xfe', '\\\\xff']\\n0 0 0 1 0\\n[[2, 1], [3], [4, 5, 6]]\\n[0, 1, 2, 3, 4]\\n6\\n10\\n{1: None, 2: None, 3: None}\\n{1: None, 2: None, 3: None}\\n{1: 7, 2: 7, 3: 7}\\n{1: 4.0, 2: 4.0, 3: 4.0}\\n{1: 'string', 2: 'string', 3: 'string'}\\nhoihoi\\n1\\n1<2\\nfred = fred\\nfred = fred = fred\\n(3, 4) 3 4\\n1 1 1\\n27 27 27\\n3.0 3.0\\n4 9\\n1 2\\n(1, 2) 1 2\\n1 2\\n2 1\\n1 2\\n[1, 2]\\n")
output("hello, world!\\n['a', 'h']\\n['b', 'c']\\n['c', 'd', 'e']\\n12 255 16\\n255 255 ff 12\\n \\"\\n\\t\\" \\nset([1])\\nset([1, 2, 3])\\n[1, 2, 3]\\n3\\n2\\n1\\na b\\na b c d e\\na b\\na b c d e\\n3\\nset([1, 2, 3]) - set([3, 4, 5]) = set([1, 2]) = set([1, 2])\\nset([1, 2]) set([])\\nset([]) 1 1\\n1\\nset([1, 2])\\nset([1, 2])\\n1\\n2\\n3\\n2 1\\n1 2\\n0 3\\nset([1, 4])\\n{1: 2, 2: 3}\\ncegi\\n[]\\n['y', '', 'y']\\n['', '', '', '']\\n['h', 'pl', '']\\n['x', 'xxx']\\nCNF\\n['\\\\xf6', '\\\\xf7', '\\\\xf8', '\\\\xf9', '\\\\xfa', '\\\\xfb', '\\\\xfc', '\\\\xfd', '\\\\xfe', '\\\\xff']\\n0 0 0 1 0\\n[[2, 1], [3], [4, 5, 6]]\\n[0, 1, 2, 3, 4]\\n6\\n10\\n[0, 1, 2, 3, 4]\\n[1, 2, 3, 4]\\n{1: 0, 2: 0, 3: 0}\\n{1: 0, 2: 0, 3: 0}\\n{1: 7, 2: 7, 3: 7}\\n{1: 4.0, 2: 4.0, 3: 4.0}\\n{1: 'string', 2: 'string', 3: 'string'}\\nhoihoi\\n1\\n1<2\\nfred = fred\\nfred = fred = fred\\n(3, 4) 3 4\\n1 1 1\\n27 27 27\\n3 3\\n4 9\\n1 2\\n(1, 2) 1 2\\n1 2\\n2 1\\n1 2\\n[1, 2]\\n")

'''),

('''voronoi''', '''
# Textual Voronoi code modified from: <abhishek@ocf.berkeley.edu>
# http://www.ocf.berkeley.edu/~Eabhishek/

from random import random # for generateRandomPoints
from math import sqrt

def generateRandomPoints(npoints=6):
    """Generate a few random points v1...vn"""
    print npoints, "points x,y:"
    points = []
    for i in xrange(npoints):
        xrand, yrand = random(), random()
        print xrand, yrand
        for xoff in range(-1, 2):
            for yoff in range(-1, 2):
                points.append( (xrand + xoff, yrand + yoff) )
    return points


def closest(x,y,points):
    """Function to find the closest of the vi."""
    best,good = 99.0*99.0, 99.0*99.0
    for px, py in points:
        dist = (x-px)*(x-px) + (y-py)*(y-py)
        if dist < best:
            best, good = dist, best
        elif dist < good:
            good = dist
    return sqrt(best) / sqrt(good)


def generateScreen(points, rows=40, cols=80):
    yfact = 1.0 / cols
    xfact = 1.0 / rows
    screen = []
    chars = " -.,+*$&#~~"
    for i in xrange(rows):
        x = i*xfact
        line = [ chars[int(10*closest(x, j*yfact, points))] for j in xrange(cols) ]
        screen.extend( line )
        screen.append("\\n")
    return "".join(screen)


from time import clock
points = generateRandomPoints(10)
print
t1 = clock()
print generateScreen(points, 40, 80)
t2 = clock()
print round(t2-t1, 3)
''', '''
output()

'''),

('''pascal triangle''', '''
def pascal(n):
    """pascal(n): print n first lines of Pascal's
    triangle (shortest version)."""
    r = [[1]]
    for i in xrange(1, n):
        r += [[1] + [sum(r[-1][j:j+2]) for j in range(i)]]
    return r

print pascal(9)
''', '''
output('[[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1], [1, 5, 10, 10, 5, 1], [1, 6, 15, 20, 15, 6, 1], [1, 7, 21, 35, 35, 21, 7, 1], [1, 8, 28, 56, 70, 56, 28, 8, 1]]\\n')
'''),

('''mandelbrot''', '''
def mandelbrot(max_iterations=1000):
    # By Daniel Rosengren, modified
    #   http://www.timestretch.com/FractalBenchmark.html
    # See also vectorized Python+Numeric+Pygame version:
    #   http://www.pygame.org/pcr/mandelbrot/index.php
    bailout = 16
    for y in xrange(-39, 39):
        line = []
        for x in xrange(-39, 39):
            cr = y/40.0 - 0.5
            ci = x/40.0
            zi = 0.0
            zr = 0.0
            i = 0
            while True:
                i += 1
                temp = zr * zi
                zr2 = zr * zr
                zi2 = zi * zi
                zr = zr2 - zi2 + cr
                zi = temp + temp + ci
                if zi2 + zr2 > bailout:
                    line.append(" ")
                    break
                if i > max_iterations:
                    line.append("#")
                    break
        print "".join(line)

for x in range(10):
    mandelbrot()
''', '''
output()
'''),

('''n-queens problem''', '''
# From: http://en.wikipedia.org/wiki/Eight_queens_puzzle

def n_queens(n, width):
    if n == 0:
        return [[]] # one solution, the empty list
    else:
        return add_queen(n-1, width, n_queens(n-1, width))

def add_queen(new_row, width, previous_solutions):
    solutions = []
    for sol in previous_solutions:
        for new_col in range(width):
            if safe_queen(new_row, new_col, sol):
                solutions.append(sol + [new_col])
    return solutions

def safe_queen(new_row, new_col, sol):
    for row in range(new_row):
        if (sol[row] == new_col or                  
            sol[row] + row == new_col + new_row or 
            sol[row] - row == new_col - new_row): 
                return 0
    return 1

n = 12
solutions = n_queens(n, n)
print len(solutions), "solutions."

''', '''
output('14200 solutions.\\n')
'''),

('''convex hull''', '''
# (c) Bearophile

from random import random
#from sets import Set

points = [ (random(), random()) for i in xrange(200) ]

def isntRightTurn(e):
    p0, p1 = e[-3]
    q0, q1 = e[-2]
    r0, r1 = e[-1]
    return q0*r1 + p0*q1 + r0*p1 >= q0*p1 + r0*q1 + p0*r1

def half(points):
    extrema = points[0:2]
    for p in points[2:]:
        extrema.append(p)
        while len(extrema)>2 and isntRightTurn(extrema):
            del extrema[-2]
    return extrema

points = sorted(set(points)) 
upper = half(points) 
points.reverse()
lower = half(points) 
print upper + lower[1:-1]
''', '''
output()
'''),

('''delete list/dict item/slice/sliceobj''', '''
a = range(10)
b = a[1::3]
print b

del a[9]
print a
del a[1:3]
print a
del a[::2]
print a

d = {1: 4, 2: 5}
del d[1]
print d
''', '''
output('[1, 4, 7]\\n[0, 1, 2, 3, 4, 5, 6, 7, 8]\\n[0, 3, 4, 5, 6, 7, 8]\\n[3, 5, 7]\\n{2: 5}\\n')

'''),

('''list(tuple) etc. sorting, test for sys.argv, splitting''', '''
import sys

a = [(2,3),(3,2),(),(2,),(3,4,5),(2,2),(1,4),(4,1),(4,2),(4,3),(3,4),(4,4),(4,5),(1,5),(1,20),(20,1),(20,2)]
print sorted(a)

b = [[3,2],[1,3]]
print sorted(b)

c = ['b','c','aa']
print sorted(c)

print sys.argv[1:]

if (0 or 0 or 1) and 1:
    print 'yay'

ah = 'hatsie flatsie pots'
print ah.split(), ah == ' '.join(ah.split())

print 'hoei hoei'.split()
print 'hoei hoei\\\\n'.split()

print ['hoei\\\\n']
print 'hoei\\\\n'
''', '''
output("[(), (1, 4), (1, 5), (1, 20), (2,), (2, 2), (2, 3), (3, 2), (3, 4), (3, 4, 5), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (20, 1), (20, 2)]\\n[[1, 3], [3, 2]]\\n['aa', 'b', 'c']\\n[]\\nyay\\n['hatsie', 'flatsie', 'pots'] 1\\n['hoei', 'hoei']\\n['hoei', 'hoei\\\\\\\\n']\\n['hoei\\\\\\\\n']\\nhoei\\\\n\\n")

'''),

('''two problem cases discovered by someone on python-list''', '''
def main():
   ws = open("testdata/hoppa","r").read().split()
   d = {}
   for i, w in enumerate(ws):
       s = "".join(sorted(list(w.lower())))
       d.setdefault(s, []).append(i)
   for l in d.values():
       if len(l) > 1:
           print [ws[i] for i in l]

main()

def subsets(sequence):
   result = [[]] * (2**len(sequence))
   for i,e in enumerate(sequence):
       i2, el = 2**i, [e]
       for j in xrange(i2):
           result[j+i2] = result[j] + el
   return result

print subsets(range(4))

''', '''
output("['hop', 'hop']\\n[[], [0], [1], [0, 1], [2], [0, 2], [1, 2], [0, 1, 2], [3], [0, 3], [1, 3], [0, 1, 3], [2, 3], [0, 2, 3], [1, 2, 3], [0, 1, 2, 3]]\\n")

'''),

('''more problems discovered by Luis Gonzales''', '''
print 'hello, world!'                    # [str]

l = 'luis gonzales'                      # [str]
print l[3:7]                             # [str]
print l[1::2]                            # [str]

t = (1,2,3,4,5)                          # [tuple(int)]
print t[1:4]                             # [tuple(int)]

s = 'we are testing shedskin on windows' # [str]
 
d = {}                                   # [dict(str, int)]
 
for i in s:                              # [str]
    if not i in d:                       # []
        d[i]= 1                          # [int]
    else:
        d[i]= d[i] + 1                   # [int]
   
for k,v in d.items():                    # [tuple(str, int)]
    if k == ' ':
        print k, ':', v                      # [str], [str], [int]

x=[]                                     # [list(dude)]
 
class dude:                              # age: [int], last: [str], name: [str]
    def __init__(self, name, last , age): # self: [dude], name: [str]*, last: [str]*, age: [int]*
        self.name = name                 # [str]
        self.last = last                 # [str]
        self.age = age                   # [int]
        x.append(self)                   # []
    def __repr__(self):                  # self: [dude]
        return '%s %s is %s years old' %(self.name, self.last, str(self.age)) # [str]
 
dude('luis','gonzalez',35)               # [dude]
print x[0]                               # [dude]
''', '''
output('hello, world!\\ns go\\nusgnae\\n(2, 3, 4)\\n  : 5\\nluis gonzalez is 35 years old\\n')

'''),

('''fast program for finding primes up to n, by Wensheng Wang''', '''
# (c) Wensheng Wang

from math import sqrt

def primes(n):                           # n: [int]
   "primes(n): return a list of prime numbers <=n."

   if n == 2:                            # [int]
       return [2]                        # [list(int)]
   elif n<2:                             # [int]
       return []                         # [list(int)]
   s = range(3, n+2, 2)                  # [list(int)]
   mroot = n ** 0.5                      # [float]
   #mroot = sqrt(n)
   half = len(s)                         # [int]
   i = 0                                 # [int]
   m = 3                                 # [int]
   while m <= mroot:                     # [int]
       if s[i]:                          # [int]
           j = (m*m - 3) / 2             # [int]
           s[j] = 0                      # [int]
           while j < half:               # [int]
               s[j] = 0                  # [int]
               j += m                    # [int]
       i += 1                            # [int]
       m = 2 * i + 3                     # [int]
   if s[-1] > n:
       s[-1] = 0
   #return [2] + filter(None, s)
   return [2] + [x for x in s if x]      # [list(int)]

print primes(100)                        # [list(int)]
''', '''
output('[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]\\n')
'''),

('''problems found by Luis Gonzales and someone else on python-list''', '''
print 'hello, world!'

for x in range(10,14):                   # [list(int)]
    print x**3                           # [int]

y = 'luis'                               # [str]
for i in y:                              # [str]
    print i                              # [str]

print [i*2 for i in 'luis']              # [list(str)]

f = open('testdata/hoppa')                        # [file]
print 'lc', [l for l in f]               # [str], [list(str)]
f.close()                                # []

f = open('testdata/hoppa')                        # [file]
print 'read', f.read()                   # [str], [str]
f.close()                                # []

f = file('testdata/hoppa')                        # [file]
print 'lines', f.readlines()             # [str], [list(str)]
f.close()                                # []

conv = {"A": 0, "B": 1}                  # [dict(str, int)]
print conv["A"], conv["B"]               # [int], [int]

print [{"A": 0, "B": 1}[c] for c in "ABABABA"] # [list(int)]
''', '''
output("hello, world!\\n1000\\n1331\\n1728\\n2197\\nl\\nu\\ni\\ns\\n['ll', 'uu', 'ii', 'ss']\\nlc ['hop\\\\n', 'hop\\\\n', 'hoppa!\\\\n']\\nread hop\\nhop\\nhoppa!\\n\\nlines ['hop\\\\n', 'hop\\\\n', 'hoppa!\\\\n']\\n0 1\\n[0, 1, 0, 1, 0, 1, 0]\\n")

'''),

('small factorization program by Rohit Krishna Kumar', '''
# A simple program to find the prime factors of a given number.
# (c) Rohit Krishna Kumar
# --- http://www.geocities.com/rohitkkumar

import math

def prime(n):                            # n: [int]
    if(n==1):                            # [int]
        return False                     # [int]
    if(n==2):                            # [int]
        return True                      # [int]
    if(not n%2):                         # [int]
        return False                     # [int]
    for i in range(3,int(math.sqrt(n))+1,2): # [list(int)]
        if(not n%i):                     # [int]
            return False                 # [int]
    return True                          # [int]
    
def factorize(n,l):                      # n: [int], l: [list(int)]
    for i in range(2,int(math.sqrt(n))+1): # [list(int)]
        if(not n%i):                     # [int]
            if(prime(i)):                # [int]
                l.append(i)              # []
            else:
                factorize(i,l)           # []
            if(prime(n/i)):              # [int]
                l.append(n/i)            # []
            else:
                factorize(n/i,l)         # []
            break                

factors=[]                               # [list(int)]
n='2079283419'                             # [int]
#raw_input("Number to factorize:")      # [str]
factorize(int(n),factors)                # []
print factors                            # [list(int)]
''', '''
output('[3, 3, 3, 1097, 70201]\\n')

'''),

('sudoku solver 1', '''
# (c) Jack Ha
# --- jack.ha@gmail.com

def validMove(puzzle, x, y, number):     # puzzle: [list(list(int))], x: [int], y: [int], number: [int]
        #see if the number is in any row, column or his own 3x3 square
        blnOK = True                     # [int]
        px = x / 3                       # [int]
        py = y / 3                       # [int]
        if puzzle[x][y] != 0:            # [int]
                blnOK = False            # [int]
        if blnOK:                        # []
                for i in range(9):       # [list(int)]
                        if puzzle[i][y] == number: # [int]
                                blnOK = False # [int]
        if blnOK:                        # []
                for j in range(9):       # [list(int)]
                        if puzzle[x][j] == number: # [int]
                                blnOK = False # [int]
        if blnOK:                        # []
                for i in range(3):       # [list(int)]
                        for j in range(3): # [list(int)]
                                if puzzle[px*3+i][py*3+j] == number: # [int]
                                        blnOK = False # [int]
        return blnOK                     # [int]

def findallMoves(puzzle,x,y):            # puzzle: [list(list(int))], x: [int], y: [int]
        returnList = []                  # [list(int)]
        for n in range(1,10):            # [list(int)]
                if validMove(puzzle, x, y, n): # [int]
                        returnList.append(n) # []
        return returnList                # [list(int)]

def solvePuzzleStep(puzzle):             # puzzle: [list(list(int))]
        isChanged = False                # [int]
        for y in range(9):               # [list(int)]
                for x in range(9):       # [list(int)]
                        if puzzle[x][y] == 0: # [int]
                                allMoves = findallMoves(puzzle, x, y) # [list(int)]
                                if len(allMoves) == 1: # [int]
                                        puzzle[x][y] = allMoves[0] # [int]
                                        isChanged = True # [int]
        return isChanged                 # [int]

#try to solve as much as possible without lookahead
def solvePuzzleSimple(puzzle):           # puzzle: [list(list(int))]
        iterationCount = 0               # [int]
        while solvePuzzleStep(puzzle) == True: # [int]
                iterationCount += 1      # [int]

hashtable = {}                           # [dict(int, int)]

def calc_hash(puzzle):                   # puzzle: [list(list(int))]
        hashcode = 0                     # [int]
        for c in range(9):               # [list(int)]
                hashcode = hashcode * 17 + hash(tuple(puzzle[c])) # [int]
        return hashcode                  # [int]

def hash_add(puzzle):                    # puzzle: [list(list(int))]
        hashtable[calc_hash(puzzle)] = 1 # [int]

def hash_lookup(puzzle):                 # puzzle: [list(list(int))]
        return hashtable.has_key(calc_hash(puzzle)) # [int]

#solve with lookahead
#unit is 3x3, (i,j) is coords of unit. l is the list of all todo's
def perm(puzzle, i, j, l, u):            # puzzle: [list(list(int))], i: [int], j: [int], l: [list(int)], u: [list(tuple(int))]
        global iterations
        iterations += 1                  # [int]
        if (u == []) and (l == []):      # [int]
                print "Solved!"          # [str]
                #printpuzzle(puzzle)      # []
                print "iterations: ", iterations # [str], [int]
                return True              # [int]
        else:
                if l == []:              # [int]
                        #here we have all permutations for one unit

                        #some simple moves
                        puzzlebackup = [] # [list(tuple(int))]
                        for c in range(9): # [list(int)]
                                puzzlebackup.append(tuple(puzzle[c])) # []
                        solvePuzzleSimple(puzzle) # []

                        #next unit to fill
                        for c in range(len(u)): # [list(int)]
                                if not hash_lookup(puzzle): # [int]
                                        inew, jnew = u.pop(c) # [tuple(int)]
                                        l = genMoveList(puzzle, inew, jnew) # [list(int)]
                                        #only print new situations
                                        #print "inew, jnew, l, u:", inew, jnew, l, u # [str], [int], [int], [list(int)], [list(tuple(int))]
                                        #printpuzzle(puzzle) # []
                                        #print "iterations: ", iterations # [str], [int]
                                        if perm (puzzle, inew, jnew, l, u): # [int]
                                                return True # [int]
                                        else:
                                                hash_add(puzzle) # []
                                        u.insert(c, (inew, jnew)) # []

                        #undo simple moves
                        for y in range(9): # [list(int)]
                                for x in range(9): # [list(int)]
                                        puzzle[x][y] = puzzlebackup[x][y] # [int]
                        hash_add(puzzle) # []
                        return False     # [int]
                else:
                        #try all possibilities of one unit
                        ii = i * 3       # [int]
                        jj = j * 3       # [int]
                        for m in range(len(l)): # [list(int)]
                                #find first empty
                                for y in range(3): # [list(int)]
                                        for x in range(3): # [list(int)]
                                                if validMove(puzzle, x+ii, y+jj, l[m]): # [int]
                                                        puzzle[x+ii][y+jj] = l[m] # [int]
                                                        backup = l.pop(m) # [int]
                                                        if (perm(puzzle, i, j, l, u)): # [int]
                                                                return True # [int]
                                                        else:
                                                                hash_add(puzzle) # []
                                                        l.insert(m, backup) # []
                                                        puzzle[x+ii][y+jj] = 0 # [int]
                        return False     # [int]

#gen move list for unit (i,j)
def genMoveList(puzzle, i, j):           # puzzle: [list(list(int))], i: [int], j: [int]
        l = range(1,10)                  # [list(int)]
        for y in range(3):               # [list(int)]
                for x in range(3):       # [list(int)]
                        p = puzzle[i*3+x][j*3+y] # [int]
                        if p != 0:       # [int]
                                l.remove(p) # []
        return l                         # [list(int)]

def printpuzzle(puzzle):                 # puzzle: [list(list(int))]
        for x in range(9):               # [list(int)]
                s = ' '                  # [str]
                for y in range(9):       # [list(int)]
                        p = puzzle[x][y] # [int]
                        if p == 0:       # [int]
                                s += '.' # [str]
                        else:
                                s += str(puzzle[x][y]) # [str]
                        s += ' '         # [str]
                print s                  # [str]

def main():
        puzzle = [[0, 9, 3, 0, 8, 0, 4, 0, 0], # [list(list(int))]
                          [0, 4, 0, 0, 3, 0, 0, 0, 0], # [list(int)]
                          [6, 0, 0, 0, 0, 9, 2, 0, 5], # [list(int)]
                          [3, 0, 0, 0, 0, 0, 0, 9, 0], # [list(int)]
                          [0, 2, 7, 0, 0, 0, 5, 1, 0], # [list(int)]
                          [0, 8, 0, 0, 0, 0, 0, 0, 4], # [list(int)]
                          [7, 0, 1, 6, 0, 0, 0, 0, 2], # [list(int)]
                          [0, 0, 0, 0, 7, 0, 0, 6, 0], # [list(int)]
                          [0, 0, 4, 0, 1, 0, 8, 5, 0]] # [list(int)]

        #create todo unit(each 3x3) list (this is also the order that they will be tried!)
        u = []                           # [list(tuple(int))]
        lcount = []                      # [list(int)]
        for y in range(3):               # [list(int)]
                for x in range(3):       # [list(int)]
                        u.append((x,y))  # []
                        lcount.append(len(genMoveList(puzzle, x, y))) # []

        #sort
        for j in range(0,9):             # [list(int)]
                for i in range(j,9):     # [list(int)]
                        if i != j:       # [int]
                                if lcount[i] < lcount[j]: # [int]
                                        u[i], u[j] = u[j], u[i]
                                        lcount[i], lcount[j] = lcount[j], lcount[i]

        l = genMoveList(puzzle, 0, 0)    # [list(int)]
        perm (puzzle, 0, 0, l, u)        # [int]

iterations = 0                           # [int]
for x in range(30):
    main()                                   # []
''', '''
output(equal=True)

'''),

('neural network simulator', ''' 
# (c) Mark Dufour
# --- mark.dufour@gmail.com

from random import random
from math import sqrt, e

sigmoid = lambda x: pow((1+pow(e,-x)),-1) # [lambda0]
deriv = lambda x: pow(e,-x) * pow((1+pow(e,-x)),-2) # [lambda0]

class link:                             # in_node: [node], weight: [float], activation: [], out_node: [node], delta: [], input: [], output: [], unit: []
    def __init__(self, in_node, out_node): # self: [nlink], in_node: [node]*, out_node: [node]*
        self.in_node = in_node; self.out_node = out_node # [node]
        self.weight = (random()-0.5)/2  # [float]
        
class node:                              # in_node: [], weight: [], activation: [float], out_node: [], delta: [float], output: [list(nlink)], input: [list(nlink)], unit: []
    def __init__(self, input_nodes):     # self: [node], input_nodes: [list(node)]
    	self.input, self.output = [], []    # [list(nlink)], [list(nlink)]
        for node in input_nodes:         # [list(node)]
            l = link(node,self)         # [nlink]
            self.input.append(l)         # []
            node.output.append(l)        # []

def incoming(node): return sum([link.in_node.activation * link.weight for link in node.input]) # [float]

def neural_network_output(network, input): # network: [list(list(node))], input: [list(int)]
    # set input layer activations
    for index, node in enumerate(network[0]): # [tuple(int, node)]
        node.activation = input[index]   # [int]
        
    # forward propagate output 
    for layer in network[1:]:            # [list(list(node))]
        for node in layer:               # [list(node)]
            node.activation = sigmoid(incoming(node)) # [float]

    return [node.activation for node in network[-1]] # [list(float)]

def back_propagate_error(network, answer): # network: [list(list(node))], answer: [list(int)]
    #output = [node.activation for node in network[-1]] # [list(float)]

    # output layer deltas
    for index, node in enumerate(network[-1]): # [tuple(int, node)]
        node.delta = deriv(incoming(node)) * (answer[index] - node.activation) # [float]

    # backward propagate error
    for layer in network[-2::-1]:        # [list(list(node))]
        for node in layer:               # [list(node)]
            node.delta = deriv(incoming(node)) * sum([link.out_node.delta * link.weight for link in node.output]) # [float]
            for link in node.output:     # [list(nlink)]
                link.weight += alpha * node.activation * link.out_node.delta # [float]
	         
def append_error(network, examples):     # network: [list(list(node))], examples: [list(tuple(list(int)))]
    compare = [(neural_network_output(network, example)[0], answer[0]) for example, answer in examples] # [list(tuple(float, int))]
    errors.append(sqrt((1.0/len(examples))*sum([pow(answer-output,2) for output, answer in compare]))) # [tuple(float, int)]

def train_network(network, examples, epochs): # network: [list(list(node))], examples: [list(tuple(list(int)))], epochs: [int]
    global errors
    errors = []                          # [list(float)]
    append_error(network, examples)      # []

    for epoch in range(epochs):          # [list(int)]
        for example, answer in examples: # [tuple(list(int))]
            output = neural_network_output(network, example) # [list(float)]
	    back_propagate_error(network, answer) # []
	    #print_weights(network)

	append_error(network, examples)         # []
     
#def print_weights(network):
#    for number, layer in enumerate(network[-2::-1]):
#        print 'layer', number
#        for node in layer: 
#	    print [link.weight for link in node.output]

alpha = 0.5                              # [float]

input_layer = [node([]) for n in range(10)] # [list(node)]
hidden_layer = [node(input_layer) for n in range(4)] # [list(node)]
output_layer = [node(hidden_layer) for n in range(1)] # [list(node)]

network = [input_layer, hidden_layer, output_layer] # [list(list(node))]

examples = [ ([1,0,0,1,1,2,0,1,0,0], [1]), # [list(tuple(list(int)))]
             ([1,0,0,1,2,0,0,0,2,2], [0]), # [tuple(list(int))]
	     ([0,1,0,0,1,0,0,0,3,0], [1]),      # [list(int)]
	     ([1,0,1,1,2,0,1,0,2,1], [1]),      # [tuple(list(int))]
 	     ([1,0,1,0,2,2,0,1,0,3], [0]),     # [tuple(list(int))]
	     ([0,1,0,1,1,1,1,1,1,0], [1]),      # [tuple(list(int))]
	     ([0,1,0,0,0,0,1,0,3,0], [0]),      # [list(int)]
	     ([0,0,0,1,1,1,1,1,2,0], [1]),      # [list(int)]
	     ([0,1,1,0,2,0,1,0,3,3], [0]),      # [list(int)]
	     ([1,1,1,1,2,2,0,1,1,1], [0]),      # [list(int)]
	     ([0,0,0,0,0,0,0,0,2,0], [0]),      # [list(int)]
	     ([1,1,1,1,2,0,0,0,3,2], [1]) ]     # [list(int)]

epochs = 1000                            # [int]
train_network(network, examples, epochs) # []
print [neural_network_output(network, example) for example, answer in examples] # [list(list(float))]
''', '''
output()

'''),

('simplified version of neural network sim: prealloc problem, callfunc([]), ifa crash', '''
class node:                              # activation: [int]*
    def __init__(self, input):
        pass
        
def neural_network_output(network, input): # network: [list(list(node))], input: [list(int)]
    for node in network[0]:                 # [list(node)]
        node.activation = 1              # [int]

    for index, node in enumerate(network[0]): # [tuple2(int, node)]
        node.activation = input[index]   # [int]
        
    return [node.activation for node in network[0]] # [list(int)]

input_layer = [node([]) for n in range(10)] # [list(node)]
hidden_layer = [node(input_layer) for n in range(4)] # [list(node)]
output_layer = [node(hidden_layer) for n in range(1)] # [list(node)]

network = [input_layer, hidden_layer, output_layer] # [list(list(node))]

examples = [ ([1,0,0,1,1,2,0,1,0,0], [1]), # [list(tuple2(list(int), list(int)))]
             ([1,0,0,1,2,0,0,0,2,2], [0]) ] # [list(int)]

print [neural_network_output(network, example) for example, answer in examples] # [list(list(int))]
''', '''
output('[[1, 0, 0, 1, 1, 2, 0, 1, 0, 0], [1, 0, 0, 1, 2, 0, 0, 0, 2, 2]]\\n')

'''),

('testing new C++ tuple class', '''
l = [(b,a) for a,b in enumerate([1,2,3])] # [list(tuple(int))]
print l                                  # [list(tuple(int))]

for a,b in enumerate([1.1,2.2,3.3]):     # [tuple2(int, float)]
    print 'huhu', a, '%.1f' % b                   # [str], [int], [float]

def bla():
    return ('1',2.2)                     # [tuple2(str, float)]

x,y = bla()                              # [tuple2(str, float)]
z,v = bla()                              # [tuple2(str, float)]
''', '''
output('[(1, 0), (2, 1), (3, 2)]\\nhuhu 0 1.1\\nhuhu 1 2.2\\nhuhu 2 3.3\\n')

'''),

('slice objects', '''
a = [1,2,3,4,5]                          # [list(int)]

print a[:-1]                             # [list(int)]
print a[1:3]                             # [list(int)]
print a[::]                              # [list(int)]
print a[:3:]                             # [list(int)]
print a[::-1]                            # [list(int)]
''', '''
output('[1, 2, 3, 4]\\n[2, 3]\\n[1, 2, 3, 4, 5]\\n[1, 2, 3]\\n[5, 4, 3, 2, 1]\\n')

'''),

('handle such constructors that flow together only via function template arguments', '''
class node:                              # activation: [int]*
    def __init__(self, euh, input):      # self: [node], euh: [int], input: [list(int)]
        pass

d = [11]                                 # [list(int)]
e = [12]                                 # [list(int)]

x = []                                   # [list(int)]
y = x                                    # [list(int)]
a = node(1, y)                           # [node]
b = node(2, d)                           # [node]
c = node(3, e)                           # [node]

''', ''' 
output()

'''),

('use a forward dataflow analysis for constructors that do not flow to instance variable assignments', '''
def bla(x):                              # x: [A]*
    a = []                               # [list(A)]
    return a                             # [list(A)]
    return [x]                           # [list(A)]


a = bla(1)                               # [list(int)]
b = bla(1.1)                             # [list(float)]


d = []                                   # [list(str)]
c = d                                    # [list(str)]
c = ['1']                                # [list(str)]

if d == []:                              # [int]
    print 'yo'                           # [str]
if c == []:
    print 'no'
''', '''
output('yo\\n')

'''),

('bootstrapping builtins: enumerate, zip, min, max, sum', '''
def enumerate(x):                        # x: [pyiter(A)]
    i = 0                                # [int]
    result = []                          # [list(tuple2(int, A))]
    for e in x:                          # [pyiter(A)]
        result.append((i,e))             # []
        i += 1
    return result                        # [list(tuple2(int, A))]
    
print enumerate(['0','1','2'])           # [list(tuple2(int, str))]
print enumerate((2,1,0))                 # [list(tuple(int))]
print enumerate({1: 2, 3: 4})            # [list(tuple(int))]

def mini(arg1, arg2=None):                # arg1: [A], arg2: [pyobj]
    return arg1.getunit()                # [pyobj]

def maxi(arg1, arg2=None):                # arg1: [], arg2: []
    return arg1.getunit()                # []

print mini([8,7,9])                       # [int]
print mini(2,1)                           # [int]
print mini(1.1,2.1)                       # [float]

def __zip2(a, b):                           # a: [pyiter(A)], b: [pyiter(B)]
    la = [e for e in a]                  # [list(A)]
    lb = [e for e in b]                  # [list(B)]

    result = []                          # [list(tuple2(A, B))]

    for i in range(mini(len(la), len(lb))): # [list(int)]
        result.append((la[i], lb[i]))    # []
    return result                        # [list(tuple2(A, B))]
    

print zip({1:2, 2:3}, (1.1,2.2,3.3))     # [list(tuple2(int, float))]
print zip((1.1,2.2,3.3), {1:2, 2:3})     # [list(tuple2(float, int))]

def sum(l):                              # l: [pyiter(A)]
    first = True                         # [int]
    for e in l:                          # [pyiter(A)]
        if first:                        # []
            result = e                   # [A]
            first = False                # [int]
        else:
            result += e                  # [A]
    return result                        # [A]

print sum([1,2,3,4])                     # [int]
print sum({1.1: 2.2, 3.3: 4.4})          # [float]
''', '''
output("[(0, '0'), (1, '1'), (2, '2')]\\n[(0, 2), (1, 1), (2, 0)]\\n[(0, 1), (1, 3)]\\n7\\n1\\n1.1\\n[(1, 1.1), (2, 2.2)]\\n[(1.1, 1), (2.2, 2)]\\n10\\n4.4\\n")


'''),

('nested tuple assignments', '''
d = (1, (1.1, 'u'))                      # [tuple2(int, tuple2(float, str))]

a, (b, c) = d                            # [tuple2(int, tuple2(float, str))]
e, f = d                                 # [tuple2(int, tuple2(float, str))]


for x,(y,z) in [d]:                      # [tuple2(int, tuple2(float, str))]
    x                                    # [int]
    y                                    # [float]
    z                                    # [str]

l = [((v,u),w) for u,(v,w) in [d]]       # [list(tuple2(tuple2(float, int), str))]

print 'u', l                                  # [list(tuple2(tuple2(float, int), str))]
''', '''
output("u [((1.1, 1), 'u')]\\n")

'''),

('for an assignment b=a, disable stack allocation for both a and b', '''
def bla():
    a = []                               # [list(int)]
    a.append(1)                          # []

    b = a                                # [list(int)]

    a = []                               # [list(int)]
    a.append(2)                          # []

    print b                              # [list(int)]

bla()                                    # []
''', '''
output('[1]\\n')

'''),

('negative indices', '''
a = [1,2,3]                              # [list(int)]

print a[0], a[1], a[-2], a[-1]           # [int], [int], [int], [int]

d = {-1: 2}                              # [dict(int, int)]

print d[-1]                              # [int]
''', '''
output('1 2 2 3\\n2\\n')

'''),

('empty list constructor that doesn\'t flow to any instance var assignment', '''
def row_perm_rec(numbers):               # numbers: [list(int)]
        hoppa_row = []                   # []
        hoppa_row = ['.']                # [list(str)]

def solve_row(numbers, old_row):                  # numbers: [list(int)]
    old_row.append('u')

    row_perm_rec(8)                # []


puzzlerows = [[2]]                       # [list(list(int))]

puzzleboard = [['']]                     # [list(list(str))]

solve_row(17, puzzleboard[0])                 # []
''', '''
output()


'''),

('merging uniform binary and non-binary tuples', '''
a = (1,2)                                # [tuple(int)]
b = (1,2,3)                              # [tuple(int)]

c = a                                    # [tuple(int)]
c = b                                    # [tuple(int)]

d = a+b                                  # [tuple(int)]
print d                                  # [tuple(int)]

def bla(x):                              # x: [A]
    pass

bla(a)                                   # []
bla(b)                                   # []
bla([1,2,3])                               # []

dc = {}                                  # [dict(tuple(int), int)]
dc[a] = 2                                # [int]
dc[b] = 3                                # [int]

print a, dc[a], b, dc[b]                 # [tuple(int)], [int], [tuple(int)], [int]
''', '''
output('(1, 2, 1, 2, 3)\\n(1, 2) 2 (1, 2, 3) 3\\n')

'''),

('problem with default arguments (extracted from test 34)', '''
def row_perm_rec(numbers):               # numbers: [list(int)]
    range(numbers[0])                    # [list(int)]

puzzlecolumns = [[7]]                    # [list(list(int))]
puzzlerows = [[8]]                         # [list(int)]

['u']                          # [list(str)]

row_perm_rec(puzzlerows[0])                 # []
''', '''

'''),

('two new problems with the othello player', '''
board = 1                                # [int]

def best_move(board):                    # board: [int]
    max_move = (1,2)                     # [tuple2(int, int)]
    max_mobility = 1                     # [int]

    return max_move, max_mobility        # [tuple2(tuple2(int, int), int)]
    
move, mob = best_move(board)                 # [tuple2(tuple2(int, int), int)]
''', '''
output()

'''),

('built-in object hashing, required for dictionaries XXX user overloading of __hash__, __eq__', '''
t = (1,2,3)                              # [tuple(int)]
v = (1,)                                 # [tuple(int)]
w = (1,2,3)                              # [tuple(int)]

e = {}                                   # [dict(tuple(int), int)]
e[t] = 1                                 # [int]
e[v] = 2                                 # [int]
e[w] = 3                                 # [int]

print e[t], e[v], e[w]                   # [int], [int], [int]

''', '''
output('3 2 3\\n')

'''),

('non-standard fibonacci; avoid STL namespace', '''
n = 8                                    # [int]
count = 0                                # [int]

f = 1                                    # [int]
s = 1                                    # [int]
nums = []                                # [list(tuple2(int, int))]
while n > 0:                             # [int]
   count += 1                            # [int]
   nums.append((count, f))               # []
   temp = f                              # [int]
   f = s                                 # [int]
   s = temp + s                          # [int]
   n -= 1                                # [int]
print nums                               # [list(tuple2(int, int))]
''', '''
output('[(1, 1), (2, 1), (3, 2), (4, 3), (5, 5), (6, 8), (7, 13), (8, 21)]\\n')

'''),

('disable static preallocation (three cases)', '''
def escapement():
    a = vars1()                          # [list(int)]
    return a                             # [list(int)]

def vars1():
    return [1,2]                         # [list(int)]

x = escapement()                         # [list(int)]
y = escapement()                         # [list(int)]
y.append(3)                              # []
print x                                  # [list(int)]


def escapement2():
    bla(vars3())                         # []

def bla(x):                              # x: [list(int)]*
    global bye
    bye = x                              # [list(int)]

def vars3():
    return [1]                           # [list(int)]

def joink():
    x = vars3()                          # [list(int)]

escapement2()                            # []
bye.append(2)                            # []
joink()                                  # []
print bye                                # [list(int)]


def transitive():
    a = vars2()                          # [list(int)]
    hoi()                                # []
    print a                              # [list(int)]

def vars2():
    return [1,2]                         # [list(int)]

def hoi():
    a = vars2()                          # [list(int)]
    a.append(3)                          # []

transitive()                             # []
''', '''
output('[1, 2]\\n[1, 2]\\n[1, 2]\\n')

'''),


('variable lookup process', '''
def bla():
    return x, y                          # [tuple2(int, int)]

def blu():
    global x
    x = 2                                # [int]
 
y = 2                                    # [int]
blu()                                    # []
print bla()                              # [tuple2(int, int)]
''', '''
output('(2, 2)\\n')

'''),

('overloading equality operator', '''
class fred:                              # y: [int]*
    def __eq__(self, x):                 # self: [fred], x: [fred]
        return self.y == x.y             # [int]

a = fred()                               # [fred]
a.y = 1                                  # [int]
b = fred()                               # [fred]
b.y = 2                                  # [int]

print a == b                             # [int]
print a == a                             # [int]
print b == b                             # [int]
''', '''
output('0\\n1\\n1\\n')

'''),

('method templates', '''

class fred:                              # x: [float, int]*
    def bla(self):                       # self: [fred(A)]
        self.meth_templ(1, 1)            # [int]
        self.meth_templ(1.0, 1)          # [float]

        self.hop(self.x)                 # [A]

    def meth_templ(self, x, z):          # self: [fred(A)], x: [B]r, z: [int]
        y = x                            # [B]
        return y                         # [B]

    def hop(self, x):                    # self: [fred(A)], x: [A]r
        return x                         # [A]

a = fred()                               # [fred(int)]
a.x = 1                                  # [int]
a.bla()                                  # []

b = fred()                               # [fred(float)]
b.x = 1.0                                # [float]
b.bla()                                  # []
''', '''
output()

'''),

('compound constants, e.g. [(1,2),(3,4)], following from __eq__ and __contains__', '''
a = (1,2)                                # [tuple2(int, int)]
a in [(1,2),(3,4)]                       # [int]
(1,2) in [(1,2),(3,4)]                   # [int]

a == (2,3)                               # []
(1,2) == a                               # []

b = [1]                                  # [list(int)]
b == []                                  # [int]
[] == b                                  # [list(int)]
b == [1]                                 # [int]
1 in b                                   # [int]
1 in [1]                                 # [int]
[1] == [1]                               # [int]

#b == 'hoi'                               # [int]
#'hoi' == b                               # [int]
'hoi' == 'hoi'                           # [int]

for c in [(2,3),(3,4)]:                  # [tuple2(int, int)]
    if c == (2,3):                       # []
        pass

[v for v in [(1,),(2,),(3,)] if v != (1,)] # [list(tuple(int))]

e = 1
a in [(1,e)]                             # [int]
''', '''
output()

'''),

('general class splitting and template seeding', '''
class bla:                               # xx: [float, int]*
    pass

a = bla()                                # [bla(int)]
a.xx = 1                                 # [int]

b = bla()                                # [bla(float)]
b.xx = 1.0                               # [float]

def joink(d):                            # d: [bla(A)]
    c = bla()                            # [bla(A)]
    c.xx = d.xx                          # [A]
    return c                             # [bla(A)]

e = joink(a)                                 # [bla(int)]
f = joink(b)                                 # [bla(float)]
''', '''
check('e', ['bla(int)'])
check('f', ['bla(float)'])
output()

'''),

('comparison/containment tests, e.g. \'[(1,2)]==[(1,2)]\' and \'((1,)) in [((2,)),((1,))]\'', '''
print [1,2] == [1,2]                     # [int]
print [(1,2),(2,3)] == [(1,2),(2,3)]     # [int]
print [(1,4),(2,3)] == [(1,2),(2,3)]     # [int]

print 1 in (1,2,3)                       # [int]
print 1 in (1,2)                         # [int]
print 3 in (1,2)                         # [int]

print (1,2) in [(1,2),(2,3)]             # [int]
print (1,4) in [(1,2),(2,3)]             # [int]

print ((1,)) in [((2,)),((1,))]          # [int]
print ((3,)) in [((2,)),((1,))]          # [int]

print [1] in ([2],[1])                   # [int]
''', '''
output('1\\n1\\n0\\n1\\n1\\n0\\n1\\n0\\n1\\n0\\n1\\n')

'''),

('othello player playing against itself', '''
# (c) Mark Dufour, Haifang Ni
# --- mark.dufour@gmail.com

empty, black, white = 0, 1, -1           # [int], [int], [int]

board = [[empty for x in range(8)] for y in range(8)] # [list(list(int))]
board[3][3] = board[4][4] = white        # [int]
board[3][4] = board[4][3] = black        # [int]

player, depth = {white: 'human', black: 'lalaoth'}, 3 # [dict(int, str)], [int]

def possible_move(board, x, y, color):   # board: [list(list(int))], x: [int], y: [int], color: [int]
    if board[x][y] != empty:             # [int]
        return False                     # [int]
    for direction in [(1, 1), (-1, 1), (0, 1), (1, -1), (-1, -1), (0, -1), (1, 0), (-1, 0)]: # [list(tuple2(int, int))]
        if flip_in_direction(board, x, y, direction, color): # [int]
            return True                  # [int]
    return False                         # [int]
        
def flip_in_direction(board, x, y, direction, color): # board: [list(list(int))], x: [int], y: [int], direction: [tuple2(int, int)], color: [int]
    other_color = False                  # [int]
    while True:                          # [int]
        x, y = x+direction[0], y+direction[1] # [int], [int]
        if x not in range(8) or y not in range(8): # [int]
            return False                 # [int]
        square = board[x][y]             # [int]
        if square == empty: return False # [int]
        if square != color: other_color = True # [int]
        else: return other_color         # [int]

def flip_stones(board, move, color):     # board: [list(list(int))], move: [tuple2(int, int)], color: [int]*
    global flips
    flips += 1                           # [int]
    for direction in [(1, 1), (-1, 1), (0, 1), (1, -1), (-1, -1), (0, -1), (1, 0), (-1, 0)]: # [list(tuple2(int, int))]
        if flip_in_direction(board, move[0], move[1], direction, color): # [int]
             x, y = move[0]+direction[0], move[1]+direction[1] # [int], [int]
             while board[x][y] != color: # [int]
               board[x][y] = color       # [int]
               x, y = x+direction[0], y+direction[1] # [int], [int]
    board[move[0]][move[1]] = color      # [int]

#def print_board(board, turn):            # board: [], turn: []
#    for line in board:                   # []
#        print ' '.join([{white: 'O', black: 'X', empty: '.'}[square] for square in line]) # []
#    print 'turn:', player[turn]          # [], []
#    print 'black:', stone_count(board, black), 'white:', stone_count(board, white) # [], [], [], []

def possible_moves(board, color):        # board: [list(list(int))], color: [int]
    return [(x,y) for x in range(8) for y in range(8) if possible_move(board, x, y, color)] # [list(tuple2(int, int))]
#def coordinates(move):                   # move: []
#    return (int(move[1])-1, 'abcdefgh'.index(move[0])) # []
def stone_count(board, color):           # board: [list(list(int))], color: [int]
    return sum([len([square for square in line if square == color]) for line in board]) # [list(int)]
#def human_move(move):                    # move: []
#    return 'abcdefgh'[move[0]]+str(move[1]+1) # []

def best_move(board, color, first, step=1): # board: [list(list(int))], color: [int]*, first: [int], step: [int]
    max_move, max_mobility, max_score = None, 0, 0 # [none], [int], [int]
    #print 'possible', possible_moves(board, color) # [str], [list(tuple2(int, int))]

    for move in possible_moves(board, color): # [list(tuple2(int, int))]
        #print 'board before'             # [str]
        #print_board(board, color)        # []

        #print 'move', move               # [str], [tuple2(int, int)]
        if move in [(0,0),(0,7),(7,0),(7,7)]:      # [list(tuple2(int, int))]
            mobility, score = 64, 64     # [int], [int]
            if color != first:           # [int]
                mobility = 64-mobility   # [int]
        else:
            testboard = [[square for square in line] for line in board] # [list(list(int))]
            flip_stones(testboard, move, color) # []
            #print_board(testboard, color) # []

            if step < depth:             # [int]
                #print 'deeper'           # [str]
                next_move, mobility = best_move(testboard, -color, first, step+1) # [tuple2(tuple2(int, int), int)]
            else:
                #print 'mobility'         # [str]
                mobility = len(possible_moves(testboard, first)) # [int]
            score = mobility             # [int]
            if color != first:           # [int]
                score = 64-score         # [int]
        if score >= max_score:           # []
            max_move, max_mobility, max_score = move, mobility, score # [tuple2(int, int)], [int], [int]

    #print 'done'                         # [str]
    return max_move, max_mobility        # [tuple2(tuple2(int, int), int)]
    
flips = 0                                # [int]
steps = 0                                # [int]
turn = black                             # [int]
while possible_moves(board, black) or possible_moves(board, white): # [list(tuple2(int, int))]
    if possible_moves(board, turn):      # [list(tuple2(int, int))]
        #print_board(board, turn)         # []
        #print 'flips', flips             # [str], [int]
#        steps += 1                       # [int]
#        if steps > 5:                    # [int]
#            break

        #if turn == black:                # [int]
        move, mobility = best_move(board, turn, turn) # [tuple2(tuple2(int, int), int)]
        #else:
        #    move = coordinates(raw_input()) # [tuple2(int, int)]
        if not possible_move(board, move[0], move[1], turn): # [int]
            print 'impossible!'          # [str]
            turn = -turn                 # [int]
        else:
            flip_stones(board, move, turn) # []
    turn = -turn                         # [int]

#print_board(board, turn)
print 'flips', flips                     # [str], [int]

if stone_count(board, black) == stone_count(board, white): # [int]
    print 'draw!'                        # [str]
else:
    if stone_count(board, black) > stone_count(board, white): print player[black], 'wins!' # [str], [str]
    else: print player[white], 'wins!'   # [str], [str]
''', '''
output('flips 43771\\nhuman wins!\\n')

'''),

('return tuple2(tuple2, int)', '''
def best_move(xx):                       # xx: [int]
    return (0, 0), 0                     # [tuple2(tuple2(int, int), int)]
    
a, b = best_move(1)                      # [tuple2(tuple2(int, int), int)]
''', '''
check('a', ['tuple(int)'])
#check('a', ['tuple2(int, int)'])
check('b', ['int'])
output()

'''),

('list comprehensions with multiple qualifiers XXX \'1\'', '''
print [(2*a, b) for a in range(4) if a > 0 for b in ['1','2']] # [list(tuple2(int, str))]
''', '''
output("[(2, '1'), (2, '2'), (4, '1'), (4, '2'), (6, '1'), (6, '2')]\\n")
'''),

('compact combination: swap bin. tuples in list comprehion parameterized on iterable', '''
def flatsie(iter):                       # iter: [pyiter(tuple2(A, B))]
    return [(bh,ah) for (ah,bh) in iter] # [tuple2(int, float)]

print flatsie([(1,2.1),(2,4.1)])         # [list(tuple2(float, int))]
print flatsie({(2,3.1): [1,2,3]})        # [list(tuple2(float, int))]
print flatsie({(1,4.1): None})           # [list(tuple2(float, int))]
print flatsie(((7.7,1),))                # [list(tuple2(int, float))]
''', '''
output('[(2.1, 1), (4.1, 2)]\\n[(3.1, 2)]\\n[(4.1, 1)]\\n[(1, 7.7)]\\n')

'''),

('use list comprehension to swap binary tuples in list','''
l = [(1,2.0),(2,4.0)]                    # [list(tuple2(int, float))]
m = [(bh, ah) for (ah, bh) in l]         # [list(tuple2(float, int))]
''', '''
check('l', ['list(tuple(int, float))'])
check('m', ['list(tuple(float, int))'])
output()

'''),

('internal modeling of binary tuple', '''
t = (1, 2.0)                             # [tuple2(int, float)]
a = t[0]                                     # [int]
b = t[1]                                     # [float]

l = [(1, 2.0)]                           # [list(tuple2(int, float))]
aha = l[0]                               # [tuple2(int, float)]

c = aha[0]                                   # [int]
d = aha[1]                                   # [float]

for e,f in l:
    pass
''', '''
check('a', ['int'])
check('b', ['float'])
check('c', ['int'])
check('d', ['float'])
check('e', ['int'])
check('f', ['float'])
output()

'''),

('ifa: split tuple, then list; binary tuple via dict.items()', '''
range(4)                                 # [list(int)]

a = {}                                   # [dict(int, float)]
a[4] = 1.0                               # [float]
x = a.items()                                # [list(tuple(int))]

bert = (1,2,3)                           # [tuple(int)]
hans = (1.0,2.0,3.0)                     # [tuple(float)]

bert_list = [bert]                       # [list(tuple(int))]
hans_list = [hans]                       # [list(tuple(float))]
''', '''
check('bert_list', ['list(tuple(int))'])
check('hans_list', ['list(tuple(float))'])
check('x', ['list(tuple(int, float))'])

output()
'''),

('parameterize list comprehension on pyiter (dict, list) XXX add set', '''
def doubles(x):                          # x: [pyiter(A)]
    return [2*e for e in x]              # [list(A)]

f = {1: 1.1, 2: 2.2}                     # [dict(int, float)]
h = {3.1: 3, 2.3: 4}                     # [dict(float, int)]

print doubles(f)                         # [list(int)]
print doubles(h)                         # [list(float)]
print doubles([1.1, 2.2, 3.3])           # [list(float)]
''', '''
output('[2, 4]\\n[4.6, 6.2]\\n[2.2, 4.4, 6.6]\\n')

'''),

('ifa: infinite split loop', '''
def doubles(x):                          # x: [dict(B, A)]
    return x.values()                    # [list(A)]

f = {1: 1.0}     
h = {3.0: 3}      

a = doubles(f)      
b = doubles(h)     
''', ''' 
check('a', ['list(float)'])
check('b', ['list(int)'])
output()

'''),

('simple list comprehension parameterization','''
def bla(l):                              # l: [list(A)]
    return [y for y in l]                # [list(A)]

a = bla([1, 2, 3])                                 # [list(int)]
b = bla([1.1, 2.2, 3.3])                               # [list(float)]
print a, b
''', '''
check('a', ['list(int)'])
check('b', ['list(float)'])
output('[1, 2, 3] [1.1, 2.2, 3.3]\\n')

'''),

('ifa: simple dict splitting on unit; merging', '''
f = {}                                   # [dict(float, int)]
f[1.0] = 1                               # [int]

g = {}                                   # [dict(int, float)]
g[1] = 1.0                               # [float]

e = {}                                   # [dict(int, float)]
e[4] = 1.0                               # [float]

''', '''
check('f', ['dict(float, int)'])
check('g', ['dict(int, float)'])
check('e', ['dict(int, float)'])
cl = gx.modules['builtin'].classes['dict']
assert cl.dcpa - len(cl.unused) -1 == 2
output()

'''),

('ifa: compound list constructors can cause excessive splitting','''
a = [[0],[1],[2],[3],[4],[5],[6],[7],[8],[9],[0],[1],[2],[3],[4],[5],[6],[7],[8],[9],[0],[1],[2],[3],[4],[5],[6],[7],[8],[9],[0],[1],[2],[3],[4],[5],[6],[7],[8],[9],[0],[1],[2],[3],[4],[5],[6],[7],[8],[9],[0],[1],[2],[3],[4],[5],[6],[7],[8],[9]]
c = a[0]                                 # [list(int)]
c.append(1)                              # []

b = [['']]                               # [list(list(str))]
d = b[0]                                 # [list(str)]
d.append('')                             # []
''', '''

'''),

('ifa: simplified version of the problem. plus: do not disable builtin template parameters.', '''
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

a = []                                   # [list(int)]
ident(a)                                 # [list(int)]
u = a                                    # [list(int)]
u.append(1)                              # []

b = ['']                                 # [list(str)]
ident(b).append('')                      # []
b.extend(b)                              # []
''', '''

'''),

('ifa: add some slicing to the previous unit test', '''
def row_perm_rec():
    hoppa_row = []                       # [list(str)]

    new_row = ['']                   # [list(str)]

    a = hoppa_row                        # [list(str)]

    new_row.extend(a)                # []
    hoppa_row = new_row[:]
    hoppa_row.append('u')                # []

    return hoppa_row

numbers = [1]                            # [list(int)]
numberscopy = numbers[:]                 # [list(int)]

s = row_perm_rec()                       # []
''', '''
output()

'''),

('ifa: mixing strings and lists of strings in the same list', '''
def row_perm_rec():
    hoppa_row = 'impossible'         # [str]
    hoppa_row = []                   # [list(str)]

    a = hoppa_row                    # [pyobj]
    hoppa_row.extend(a)              # []
    hoppa_row.append('u')            # []

    return hoppa_row                 # [pyobj]

a = [[7]]                                # [list(list(int))]
s = row_perm_rec()                       # [pyobj]
puzzleboard = [['']]                     # [list(list(str))]
puzzleboard[1][1] = s[1]                 # [str]
''', '''
check('s', ['pyobj'])
check('a', ['list(list(int))'])
check('puzzleboard', ['list(list(str))'])
output()

'''),

('nasty problem in masked sat solver with default arguments and templates', '''
def solve_rec():
    la_mods = [1]                        # [list(int)]
    for var in la_mods:                  # [list(int)]
        lookahead_variable(var, la_mods)      # []
        propagate(var, la_mods)          # []

def propagate(lit, mods, bla=0):         # lit: [int], mods: [list(int)], bla: [int]
    pass

def lookahead_variable(var, mods):       # var: [int], mods: [list(int)]
    propagate(10, mods)                  # []

solve_rec()                              # []
''', '''

'''),

('accessing global variable via subscript, before it is created XXX fix this later', '''
def propagate(lit):                      # lit: [int]
    global lit_mask # XXX
    lit_mask[lit] |= 1                   # [int]

def lookahead():                     # mods: [list(int)]
    global lit_mask
    lit_mask = [1] 

lookahead()
propagate(10)
''', '''
'''),

('ifa: seeding of l.c. allocation site inside template', '''
vars = [1]                               # [list(int)]

def bla():
    return [var for var in vars]                # []

a = bla()                                    # []
''', '''
check('a', ['list(int)'])

'''),

('(incorrectly) bootstrapping the builtin reduce', '''
def reduce(f, l, i=-1):                  # f: [lambda0], l: [list(int)], i: [int]r
    if not l:                            # [list(int)]
        if i != -1: return i             # [int]
        print '*** ERROR! *** reduce() called with empty sequence and no initial value' # [str]

    if i != -1:                          # [int]
        r = f(i, l[0])                   # [int]
    else:
        r = l[0]                         # [int]

    for i in range(len(l)-1):            # [list(int)]
        r = f(r, l[i+1])                 # [int]

    return r                             # [int]

acc = lambda x,y: x+y                    # [lambda0]
score = [1,2,3,4]                        # [list(int)]

print reduce(acc, score, 0)              # [int]
''', '''
output('10\\n')

'''),

('rewrite code generation for binary operations','''
a = 1                                    # [int]
a += 2                                   # [int]
print a                                  # [int]

b = [1]                                  # [list(int)]
b += [2]                                 # [list(int)]
print b                                  # [list(int)]

print 2*b                                # [list(int)]
print b*2                                # [list(int)]

print 2*'hoi'                            # [str]
print 'hoi'*2                            # [str]

class fred: 
    def __add__(self, b):                # self: [fred], b: [pyobj]r
        return b                         # [pyobj]
    def __augadd__(self, b):             # self: [fred], b: [pyobj]
        pass
class bert:
    def __add__(self, b):                # self: [bert], b: [pyobj]r
        return b                         # [pyobj]
    def __augadd__(self, b):             # self: [bert], b: [pyobj]
        pass
 
p = fred()                               # [fred]
p = bert()                               # [bert]

p += p                                   # [pyobj]
p = p + p                                # [pyobj]

print sum([1,2,3,4])                     # [int]
print sum([1.25, 2.25, 3.25, 4.25])      # [float]
''', '''
output()
'''),

('weird simple mess-up', '''
nrofvars = [1][0] 
vars = range(nrofvars+1)                 
''', '''

'''),

('simple iterator, applying int(x) to each element', '''
cnf = ['']                               # [list(str)]

for x in cnf:                            # [list(str)]
    d = int(x)                               # [int]
''', '''
check('cnf', ['list(str)'])
check('d', ['int'])

'''),

('two simple list comprehensions, one nested', '''
u = [' p  o', 'c o ']                    # [list(str)]
cnf = [x.strip().split() for x in u if not x.startswith('x')] # [list(list(str))]
cnf2 = [[3] for x in u]                  # [list(list(int))]
''', '''
check('u', ['list(str)'])
check('cnf', ['list(list(str))'])
check('cnf2', ['list(list(int))'])

'''),

('simple list(list(str))', '''
cnf = [''.split()]                       # [list()]
''', '''
check('cnf', ['list(list(str))'])
'''),

('simple constructor code test XXX ua', '''
a = [1,2,3,4]                            # [list(int)]
b = [1.0]                                # [list(float)]
#c = [1,2,2.0]                            # [list(pyobj)]

d = [(1,)]                               # [list(tuple(int))]

e = [[1, 2],[2, 3, 4]]                   # [list(list(int))]

#f = [[1, 2.0],[2, 3, 4]]                 # [list(list(pyobj))]
''', '''
check('a', ['list(int)'])
check('b', ['list(float)'])
#check('c', ['list(float)'])
check('d', ['list(tuple(int))'])
check('e', ['list(list(int))'])
#check('f', ['list(list(float))'])

'''),

('ifa: some more gruesome test XXX merge idents, compile', '''
def duplll(x):                           # x: [list(A)]
    return [x]                           # [list(list(A))]

a = duplll([1])                          # [list(list(int))]
b = duplll([1.0])                        # [list(list(float))]

def ident(x):                            # x: [list(list(A))]r
    return x                             # [list(list(A))]
def meuk(x):                             # x: [list(list(A))]
    return ident(x)                      # [list(list(A))]

c = meuk(a)                              # [list(list(int))]
d = meuk(b)                              # [list(list(float))]

def makel(x):                            # x: [list(A)]
    return [x]                           # [list(list(A))]

def dupl(x):                             # x: [list(list(A))]
    return [makel(x[0])]                 # [list(list(list(A)))]

y = [[('1',)]]                           # [list(list(tuple(str)))]
dupl(y)                                  # [list(list(list(tuple(str))))]

dupl([[1]])                              # [list(list(list(int)))]

#d = [[1]]                                # [list(list(int))]
d = [[1.0]]                              # [list(list(float))]
d                                        # [list(list(pyobj))]

def ident2(x):                           # x: [list(pyobj)]r
    return x                             # [list(pyobj)]

bh = []                                  # [list(pyobj)]
#ident2(bh).append(1)                     # []
ident2(bh).append(1.0)                   # []

ah = []                                  # [list(pyobj)]
ident2(ah).append(1)                     # []
#ident2(ah).append(1.0)                   # []
''', '''

'''),

('ifa: completely remove unused contours from allocation table!', '''
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

def makel(x):                            # x: [list(A)]
    return [x]                           # [list(list(A))]

def dupl(x):                             # x: [list(list(A))]
    return [makel(x[0])]                 # [list(list(list(A)))]

y = [[1.0]]                              # [list(list(float))]
dupl(y)                                  # [list(list(list(float)))]
dupl([[1]])                              # [list(list(list(int)))]

ah = []                                  # [list(float)]
ident(ah).append(1.0)                    # []

bh = []                                  # [list(int)]
ident(bh).append(1)                      # []
''', '''



'''),


('calling a polymorphic function with list(int) and list(list(int))', '''
def meuk(x):                             # x: [A]r
    return x                             # [A]

meuk([1])                                  # [int]
meuk([[1]])                                # [list(int)]
''', '''
output()

'''),

('ifa: simple nested types: list(tuple), list(list(int)), list(list(float))', '''
a = (1,)                                # [tuple(int)]
b = [a]                                  # [list(tuple(int))]

c = [1]                                  # [list(int)]
e = [1.0]                                # [list(float)]

d = [c]                                  # [list(list(int))]
f = [e]                                  # [list(list(float))]
''', '''
check('a', ['tuple(int)'])
check('b', ['list(tuple(int))'])
check('c', ['list(int)'])
check('d', ['list(list(int))'])
check('e', ['list(float)'])
check('f', ['list(list(float))'])
output()

'''),

('ifa: unnecessarily splitting truly polymorphic lists XXX finalize and merge XXX ua', '''
def ident(x):                            # x: [list(pyobj)]r
    return x                             # [list(pyobj)]

ah = []                                  # [list(pyobj)]
ident(ah).append(1)                      # []
#ident(ah).append(1.0)                    # []

bh = []                                  # [list(pyobj)]
#ident(bh).append(1)                      # []
ident(bh).append(1.0)                    # []
''', '''
check('ah', ['list(int)'])
check('bh', ['list(float)'])

'''),

('ifa: simple truly polymorphic list XXX output, ua', '''
def ident(x):                            # x: [list(pyobj)]r
    return x                             # [list(pyobj)]

ah = []                                  # [list(pyobj)]
#ident(ah).append(1)                      # []
ident(ah).append(1.0)                    # []
''', '''
check('ah', ['list(float)'])


'''),

('ifa: some more use of [bla]', '''
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

b = [1.0]                                # [list(float)]
a = [1]                                  # [list(int)]
a = [2]                                  # [list(int)]
ident(a).append(1)                       # []
ident(b).append(1.0)                     # []
  
def hoppa(y):                            # y: [list(A)]
    k = [1.0]                            # [list(float)]
    l = [y[0]]                           # [list(A)]
    return l                             # [list(A)]

c = hoppa(a)                             # [list(int)]
d = hoppa(b)                             # [list(float)]
''', '''
check('a', ['list(int)'])
check('b', ['list(float)'])
check('c', ['list(int)'])
check('d', ['list(float)'])
dupl = gx.main_module.funcs['hoppa']
assert typesetreprnew(dupl.vars['k'], dupl, False) == '[list(float)]'
output()

'''),

('ifa: return [arg[0]]', '''
def dupl(y):                             # y: [list(A)]
    return [y[0]]                        # [list(A)]

a = [1]                                  # [list(int)]
a = [2]                                  # [list(int)]
b = [1.0]                                # [list(float)]
c = dupl(a)                                  # [list(int)]
d = dupl(b)                                  # [list(float)]
''', '''
check('a', ['list(int)'])
check('b', ['list(float)'])
check('c', ['list(int)'])
check('d', ['list(float)'])
output()

'''),

('ifa: combined ident, dupl, makel; 15 allocation sites', '''
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

a = []                                   # [list(int)]
a = []                                   # [list(int)]
b = []                                   # [list(float)]
c = []                                   # [list(int)]
ident(a).append(1)                       # []
ident(b).append(1.0)                     # []
ident(c).append(1)                       # []

def dupl(y):                             # y: [list(A)]
    k = []                               # [list(float)]
    k.append(1.0)                        # []

    v = []                               # [list(int)]
    v.append(1)                          # []

    l = []                               # [list(A)]
    l.append(y[0])                     # []

    return l                             # [list(A)]

b = []                                   # [list(float)]
b.append(1.0)                            # []
dupl(b)                                  # [list(float)]

a = []                                   # [list(int)]
a = []                                   # [list(int)]
a = []                                   # [list(int)]
a = []                                   # [list(int)]
a = []                                   # [list(int)]
a = []                                   # [list(int)]
a.append(1)                              # []
dupl(a)                                  # [list(int)]

def makel(x):                            # x: [A]
    l = []                               # [list(A)]
    l.append(x)                          # []
    return l                             # [list(A)]

d = makel(1)                                 # [list(int)]
e = makel(1.0)                               # [list(float)]
''', '''
check('a', ['list(int)'])
check('b', ['list(float)'])
check('c', ['list(int)'])
check('d', ['list(int)'])
check('e', ['list(float)'])
dupl = gx.main_module.funcs['dupl']
assert typesetreprnew(dupl.vars['l'], dupl, False) == '[list(A)]'
assert typesetreprnew(dupl.vars['k'], dupl, False) == '[list(float)]'
assert typesetreprnew(dupl.vars['v'], dupl, False) == '[list(int)]'
makel = gx.main_module.funcs['makel']
assert typesetreprnew(makel.vars['l'], makel, False) == '[list(A)]'
output()

'''),

('ifa: splitting + changing and non-changing containers in dependent function', '''
def ident(x):                        
    return x                        

b = []                                   
a = []                                  
ident(b).append(1.0)                   
ident(a).append(1)                    
  
def hoppa(y):                    
    k = []                        
    k.append(1.0)                  
    l = []                          
    l.append(y[0])                   
    return l

c = hoppa(a)                           
d = hoppa(b)                          
''', '''
check('a', ['list(int)'])
check('b', ['list(float)'])
check('c', ['list(int)'])
check('d', ['list(float)'])
hoppa = gx.main_module.funcs['hoppa']
assert typesetreprnew(hoppa.vars['l'], hoppa, False) == '[list(A)]'
assert typesetreprnew(hoppa.vars['k'], hoppa, False) == '[list(float)]'
output()

'''),

('ifa: non-changing container inside function', '''
def dupl(y):                             # y: [list(int)]
    k = []                               # [list(float)]
    k.append(1.0)                        # []

a = []                                   # [list(int)]
a = []                                   # [list(int)]
a.append(1)                              # []
dupl(a)                                  # []
''', '''
check('a', ['list(int)'])
hoppa = gx.main_module.funcs['dupl']
assert typesetreprnew(hoppa.vars['k'], hoppa, False) == '[list(float)]'
output()

'''),

('ifa: list duplication', '''
a = []                                   # [list(int)]
a.append(1)                              # []
b = []                                   # [list(float)]
b.append(1.0)                            # []

def dupl(y):                             # y: [list(A)]
    l = []                               # [list(A)]
    l.append(y[0])                       # []
    return l                             # [list(A)]

c = dupl(a)                                  # [list(int)]
d = dupl(b)                                  # [list(float)]
''', '''
check('a', ['list(int)'])
check('b', ['list(float)'])
check('c', ['list(int)'])
check('d', ['list(float)'])
output()

'''),

('ifa: split simple imprecision point', '''
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

a = []                                   # [list(int)]
a = []                                   # [list(int)]
b = []                                   # [list(float)]
c = []                                   # [list(int)]
ident(a).append(1)                       # []
ident(b).append(1.0)                     # []
ident(c).append(1)                       # []
''','''
check('a', ['list(int)'])
check('b', ['list(float)'])
check('c', ['list(int)'])
output()

'''),

('ifa: create list based on argument type', '''
def makel(x):                            # x: [A]
    l = []                               # [list(A)]
    l.append(x)                          # []
    return l                             # [list(A)]

c = makel(1)                                 # [list(int)]
d = makel(1.0)                               # [list(float)]
''', '''
check('c', ['list(int)'])
check('d', ['list(float)'])
output()

'''),

#('reflective visitor, coupled with bootstrapped transformer module', '''
#import transformer
#
#ast = transformer.parse('huhu')          # [ast::Module()]
#
#class visitor:                           # __class__: [class visitor]*
#    def dispatch(self, node):            # self: [visitor()], node: [ast::Stmt(), ast::Module()]
#        name = 'visit'+node.__class__.__name__ # [str]
#        meth = getattr(self, name)       # [function (class visitor, 'visitModule'), function (class visitor, 'visitStmt')]
#        meth(node)                       # []
#        
#    def visitModule(self, node):         # self: [visitor()], node: [ast::Stmt(), ast::Module()]
#        print 'module'                   # [str]
#
#    def visitStmt(self, node):           # self: [visitor()], node: [ast::Stmt(), ast::Module()]
#        print 'stmt'                     # [str]
#
#v = visitor()                            # [visitor()]
#v.dispatch(ast)                          # []
#v.dispatch(ast.node)                     # []
#''', '''
#output('module\\nstmt\\n')
#'''),

#('simple reflective visitor class, using __class__.__name__','''
#class Evert:                             # __class__: [class Evert]*
#    pass
#
#class Bert:                              # __class__: [class Bert]*
#    pass
#
#class visitor:                           # __class__: [class visitor]*
#    def dispatch(self, x):               # self: [visitor()], x: [Evert(), Bert()]
#        name = 'visit'+x.__class__.__name__ # [str]
#        meth = getattr(self, name)       # [function (class visitor, 'visitBert'), function (class visitor, 'visitEvert')]
#        meth(4)                          # [int, float]
#
#    def visitBert(self, a):              # self: [visitor()], a: [int]
#        print 'bert'                     # [str]
#        return 1                         # [int]
#
#    def visitEvert(self, a):             # self: [visitor()], a: [int]
#        print 'evert..'                  # [str]
#        return 1.0                       # [float]
#
#    def visitJaap(self):                 # self: []
#        print 'jaap!!'                   # [str]
#
#a = Evert()                              # [Evert()]
#a = Bert()                               # [Bert()]
#
#v = visitor()                            # [visitor()]
#v.dispatch(a)                            # []
#''', '''
#output('bert\\n')
#
#'''),

('__class__ and __name__ attributes','''
class evert:                             # __class__: [class evert]*
    pass

bla = evert()                            # [evert()]

cl = bla.__class__                       # [class evert]

print cl                                 # [class evert]
print cl.__name__                        # [str]

print type(bla)                          # [class evert]
print type(bla).__name__                 # [str]

if cl == type(evert()):                  # [int]
   print 'equal!'                        # [str]

if type('2') == type('3'):               # [int]
   print 'equal str!'                    # [str]

if type(1) == type('1'):                 # [int]
   print 'equal non-equal!'              # [str]
''', '''
output('class evert\\nevert\\nclass evert\\nevert\\nequal!\\nequal str!\\n')
'''),

('mod operator on string and tuple XXX', '''
print 'hoi %d %s' % (2, '3')             # [str]
''', '''
output('hoi 2 3\\n')
'''),

('simple template functioning','''
class Const: 
    def __repr__(self):                  # self: [Const()]
        return 'const'                   # [str]
class Name: 
    def __repr__(self):                  # self: [Name()]
        return 'name'                    # [str]

class Assign:                            # y: [int]*, x: [int, str]*
    def __init__(self, expr, i):         # self: [Assign(str), Assign(int)], expr: [Name(), Const()], i: [int, str]
        print expr                       # [Name(), Const()]

expr = Const()                           # [Const()]
expr = Name()                            # [Name()]
assign = Assign(expr, 1)                 # [Assign(int)]
assign.x = 1                             # [int]
assign.y = 7                             # [int]

bla = Const()                            # [Const()]
ass2 = Assign(bla, '1')                  # [Assign(str)]
ass2.x = '1'                             # [str]
ass2.y = 8                               # [int]
''', '''
output('name\\nconst\\n')

'''),

('parameterizing linked list values','''
class bert:      
    pass

class evert:
    pass

class node:                              # value: [bert(), evert()]*, next: [node(bert()), node(evert())]*
    pass

b = bert()                               # [bert]
e = evert()                              # [evert]

n = node()                               # [node(bert)]
n.next = n                               # [node(bert)]
n.value = b                              # [bert]

m = node()                               # [node(evert)]
m.next = m                               # [node(evert)]
m.value = e                              # [evert]
''','''
check('n', ['node(bert)'])
check('m', ['node(evert)'])

output()

'''),

('template local vars, expressions', '''
def hoi(a, b, e):                        # a: [int, float], b: [int, float], e: [int]
    c = a                                # [int, float]
    d = b                                # [int, float]
    f = 1                                # [int]
    g = 1                                # [int]
    h = f+g                              # [int]
    s = 'ho'+'i'                         # [str]
    return c+d                           # [int, float]


hoi(1, 2, 3)                             # [int]
hoi(1.0, 2.0, 4)                         # [float]
''', '''
output()
'''),

('unused default argument of setdefault', '''
a={}                                     # [dict(int->list(float))]
a.setdefault(1,[]).append(1.0)           # []

b= a[1]                                  # [list(float)]
''','''
check('b', ['list(float)'])
'''),

('simple deep copy test (XXX)', '''
import copy

class bert:
    pass

a = [1,2]                                # [list(int)]
b = copy.deepcopy(a)                     # [list(int)]

a[0] = 3

print a, b
''', '''
output('[3, 2] [1, 2]\\n')
'''),

('direct lambda call with multiple targets', '''
def yoyo(a):                             # a: [int]
   print 'yoyo', a                       # [str], [int]

def yoyoyo(b):                           # b: [int]
   print 'yoyoyo', b                     # [str], [int]


x = yoyo                                 # [yoyo]
x = yoyoyo                               # [lambda0]
x(1)                                     # []
''', '''
output()
'''),

#('''reflection mechanism used in compiler..''', '''
#class cnode: pass
#
#class ASTVisitor:
#    def dispatch(self, node, name, *args): # self: [ASTVisitor()], node: [cnode()], name: [str], args: [tuple(int)]
#        meth = getattr(self, 'visit'+name) # [function (class ASTVisitor, 'visitZ'), function (class ASTVisitor, 'visitD'), function (class ASTVisitor, 'visitY'), function (class ASTVisitor, 'visitX')]
#
#        meth(node, *args)                # []
#
#    def visitX(self, node, nr):          # self: [ASTVisitor()], node: [cnode()], nr: [int]
#        print 'x', nr                    # [str], [int]
#
#    def visitY(self, node, nr):          # self: [ASTVisitor()], node: [cnode()], nr: [int]
#        print 'y', nr                    # [str], [int]
#
#    def visitD(self, node, nr=7):        # self: [ASTVisitor()], node: [cnode()], nr: [int]
#        print 'd', nr                    # [str], [int]
#
#    def visitZ(self, node, nr=8, bla=9): # self: [ASTVisitor()], node: [cnode()], nr: [int], bla: [int]
#        print 'z', nr, bla               # [str], [int], [int]
#
#vi = ASTVisitor()                        # [ASTVisitor()]
#node = cnode()                           # [cnode()]
#
#vi.dispatch(node, 'X', 1)                # []
#vi.dispatch(node, 'Y', 2)                # []
#vi.dispatch(node, 'D')                   # []
#vi.dispatch(node, 'Z', 4)                # []
#''', '''
#output('x 1\\ny 2\\nd 7\\nz 4 9\\n')
#'''),

('''default arguments, function templates (XXX)''', '''
#def hoi(a, b, c=1, d=1):                 # a: [int], b: [int], c: [int, float]r, d: [int]
#    print a, b, c, d                     # [int], [int], [int, float], [int]
#    return c                             # [int, float]
#
#
#hoi(1,2)                                 # [int]
#hoi(1,2,3)                               # [int]
#hoi(1,2,3,4)                             # [int]
#
#hoi(1,2,3.1)                             # [int, float]

def hoi(a, b, c=1, d=1):                 # a: [int], b: [int], c: [int, float]r, d: [int]
    print a, b, c, d                     # [int], [int], [int, float], [int]
    return c                             # [int, float]

hoi(1,2)                                 # [int]
hoi(1,2,3)                               # [int]
hoi(1,2,3,4)                             # [int]

''', '''
output('1 2 1 1\\n1 2 3 1\\n1 2 3 4\\n')
'''),

('''determine target functions in cartesian_product()''', '''
import testdata.bert

class zeug: 
    def meuk(self):                      # self: [zeug()]
        return '2'                       # [str]

def hoi(): return 1                    # [float]


print hoi()                              # [float]
a = zeug()                               # [zeug()]

print testdata.bert.hello(1)                      # [str]
z = testdata.bert.zeug()                          # [bert::zeug()]
z.hallo(1)                               # [int]

print a.meuk()                           # [str]

l1 = lambda x,y: x+y                     # [lambda0]
print l1(1,2)                            # [int]
''', '''
output('1\\n1\\nhello\\n2\\n3\\n')
'''),

('''builtins behave as templates, generate self.merge should reflect this XXX''', '''

a = []                                   # [list(int)]
a.append(1)                              # []

b = []                                   # [list(str)]
b.append('1')                            # []

c = []                                   # [list(list(int))]
c.append([1])                            # []

#d = []
#d.append(1)
#d.append('1')
''', '''
output()
'''),

('''passing *args (XXX default args, keywords)''', '''

def hoppa(node, a, b):                   # node: [int], a: [int, float], b: [int, float]r
    print a, b                           # [int, float], [int, float]
    return b                             # [int, float]

def visit(node, *args):                  # node: [int], args: [tuple(float,int)]
    print node, args                     # [int], [tuple(float,int)]

    return hoppa(node, *args)            # [int, float]


visit(1,2,2)                           # [int, float]
visit(2,2,3,4,4,5)                       # [int, float]
''', '''
output('1 (2, 2)\\n2 2\\n2 (2, 3, 4, 4, 5)\\n2 3\\n')
'''),

('''def ident(): use function template, or cast to real return value''', '''
def ident(x, y, z):                      # x: [int, str]r, y: [int, str], z: [float]
    return x                             # [int, str]

def retint():
    return 1                             # [int]

a = ident(1, 1, 1.1)                     # [int]
b = ident('1', '1', 1.1)                 # [str]
c = retint()                             # [int]
''', '''
output()
'''),

('''simple template merging''', '''
class bert:                              # c: [int, str]*, bla: [int, float]*
    def hoppa(self, b, d):               # self: [bert(int;float), bert(str;int)], b: [int, float]*, d: [int, str]*
        self.bla = b                     # [int, float]
        self.c = d                       # [int, str]
    def flops(self, e, f):               # self: [bert(int;float), bert(str;int)], e: [str], f: [int, float, str]
        pass
    def unbox(self, g, h):               # self: [bert(int;float), bert(str;int)], g: [int], h: [int]
        pass

a = bert()                               # [bert(str;int)]
a.hoppa(1, '1')                          # []
a.flops('1',1)                           # []
a.unbox(1, 2)                            # []

b = bert()                               # [bert(int;float)]
b.hoppa(1.0,1)                           # []
b.flops('1',1.0)                         # []
b.unbox(1, 2)                            # []

c = bert()                               # [bert(str;int)]
c.hoppa(2, '1')                          # []
c.flops('1',1)                         # []

''', '''
output()
'''),

('''boxing unboxed actuals to boxed formals XXX ua''', '''
def hoi(a, b):                           # a: [int, str], b: [int]
    a                                    # [int, str]
    a = 'hoi'                            # [str]
    print a                              # [int, str]
hoi('1', 1)                                # []
''', '''
output('hoi\\n')
'''),

('''None as 0-pointer tests''', '''
class bert:
    def __repr__(self):                  # self: []
        return 'bert'                    # [str]

y = None                                 # [None]
y = bert()                               # [bert()]

if y:                                    # [int]
    print y                            # [str]

z = None                                 # [None]
z = [1]                                  # [int]

if z:                                    # [int]
    print z                            # [str]
''', '''
output('bert\\n[1]\\n')
'''),

('''simple Set test''', '''
#from sets import Set

a = set([1,2])                           # [Set(int)]
a.add(3)                                 # []
print a                                  # [Set(int)]
''', '''
output('set([1, 2, 3])\\n')
'''),

('''passing non-local arguments through (nested) list comprehensions''', '''
def hoi():                               # dinges: [list(int)], bla: [list(int)]
    bla = [1,2]                          # [list(int)]
    dinges = [1,2]                       # [list(int)]
    jada = [1,2]                         # [list(int)]

    u = [x for x in bla]                 # [list(int)]
    v = [[a for a in bla] for c in dinges] # [list(list(int))]
    w = [[[a for a in jada] for c in bla] for d in dinges] # [list(list(list(int)))]

    print u                              # [list(int)]
    print v                              # [list(list(int))]
    print w                              # [list(list(list(int)))]

    return bla                           # [list(int)]
    return dinges                        # [list(int)]

print hoi()                              # [list(int)]
''', '''
output('[1, 2]\\n[[1, 2], [1, 2]]\\n[[[1, 2], [1, 2]], [[1, 2], [1, 2]]]\\n[1, 2]\\n')
'''),

('''do not flow everything to each self''', '''
#a = 1                                    # [int]
#a = 2                                    # [int]
a = [1]                                  # [list(int)]
a = 'hoi'                                # [str]
print a                                  # [int, list(int), str]

def hoi(a, b):                           # a: [int], b: [int]
    pass

hoi(1, 2)                                # []
''', '''
output()
#m = merged(gx.types)
#assert typesetrepr(m[gx.modules['builtin_'].classes['list'].funcs['__repr__'].vars['self']]) == '[list(int)]'
#assert typesetrepr(m[gx.modules['builtin_'].classes['int_'].funcs['__repr__'].vars['self']]) == '[int]'
#assert typesetrepr(m[gx.modules['builtin_'].classes['str_'].funcs['__repr__'].vars['self']]) == '[str]'
#assert typesetrepr(m[gx.main_module.funcs['hoi'].vars['a']]) == '[int]'
#assert typesetrepr(m[gx.main_module.funcs['hoi'].vars['b']]) == '[int]'
'''),

('''2*list, list*2, 2*str, pyobj*str/list, etc.. XXX ua''', '''
x = [1]                                  # [list(int)]
x*2                                      # [list(int)]

a=[1,2]                                  # [list(int)]
b=2                                      # [int]
print b*a                                # [list(int)]
print a*b                                # [list(int)]

#e=2.0                                    # [float]
e=2                                      # [int]
print e*a                                # [list(int)]
print a*e                                # [list(int)]

d='hoi'                                  # [str]
d=[1,2]                                  # [list(int)]
c=2                                      # [int]
print c*d                                # [list(int), str]
print d*c                                # [list(int), str]

z='hoi'                                  # [str]
print z*2                                # [str]
print 2*z                                # [str]

k = 4                                    # [int]
q = 1                                    # [int]
q = k                                    # [int]
r = '1'                                  # [str]
r = '2'                                  # [str]
r = [1]                                  # [list(int)]
l = [2]                                  # [list(int)]
r = l                                    # [list(int)]

print q*r                                # [list(int), str]
print k*l                                # [list(int)]

print 1+1                                # [int]
print 1+2                                # [int]
''', '''
output(6*'[1, 2, 1, 2]\\n'+2*'hoihoi\\n'+2*'[2, 2, 2, 2]\\n'+'2\\n3\\n')
'''),

('''default argument crap (XXX)''', '''
def hu(n, s=-1):                         # s: [int], n: [int]
    return [s]                           # [list(int)]

a = hu(10)                                   # [list(int)]
#b = hu(10,'2')                               # [list(int,str)]
c = [i for i in hu(10)]                      # [list(int)]
''', '''
check('a', ['list(int)'])
#check('b', ['list(int,str)'])
check('c', ['list(int)'])
'''),

('modules, namespaces, lambdas', '''
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
''', '''
output()
'''),


('list-comprehension calling default argument', '''
def hu(n, s=-1):                         # s: [int], n: [int]
    return [1]                           # [list(int)]

a = [i for i in hu(10)]                      # []
''','''
check('a', ['list(int)'])
'''),

('mask algorithm', '''
# (c) Mark Dufour
# --- mark.dufour@gmail.com

def reduce(f, l, i=-1):                  # f: [lambda0], i: [int], l: [list(int)], r: [int]
    if not l:                            # [list(int)]
        if i != -1: return i             # [int]
        print '*** ERROR! *** reduce() called with empty sequence and no initial value' # [str]

    if i != -1:                          # [int]
        r = f(i, l[0])                   # [int]
    else:
        r = l[0]                         # [int]

    for i in range(len(l)-1):            # [int]
        r = f(r, l[i+1])                 # [int]

    return r                             # [int]

argv = ['','testdata/uuf250-010.cnf']             # [list(str)]

# solver

cnf = [l.strip().split() for l in file(argv[1]) if l[0] not in 'c0%\\n'] # [list(list(str))]
clauses = [[int(x) for x in l[:-1] if x != ''] for l in cnf if l[0] != 'p'] # [list(list(int))]
nrofvars = [int(l[2]) for l in cnf if l[0] == 'p'][0] # [int]
vars = range(nrofvars+1)                 # [list(int)]
occurrence = [[] for l in 2*vars] 
for clause in clauses:                   # [list(int)]
    for lit in clause: occurrence[lit].append(clause) # [int]
fixedt = [-1 for var in vars]            # [list(int)]

nodecount, propcount = 0, 0              # [int], [int]

def solve_rec():                         # la_mods: [list(int)], var: [int], prop_mods: [list(int)], choice: [int]*
    global nodecount
    nodecount += 1                       # []
    if nodecount == 100:
        return 1

    if not -1 in fixedt[1:]:             # [int]
        print 'v', ' '.join([str((2*fixedt[i]-1)*i) for i in range(1,nrofvars+1)]) # [list(str)]
        return 1                         # [int]

    la_mods = []                         # [list(int)]
    var = lookahead(la_mods)             # [int]
    #print 'select', var                  # [str], [int]
    if not var: return backtrack(la_mods) # [int]

    for choice in [var,-var]:            # [int]
        prop_mods = []                   # [list(int)]
        if propagate(choice, prop_mods) and solve_rec(): return 1 # [int]
        backtrack(prop_mods)             # [int]

    return backtrack(la_mods)            # [int]

def propagate(lit, mods, failed_literal=0): # lit_truth: [int], current: [int], unfixed: [int]*, mods: [list(int)], clause: [list(int)], lit: [int]*, length: [int], failed_literal: [int]
    global bincount, propcount
    current = len(mods)                  # [int]
    mods.append(lit)                     # [None]
    #print 'prop', lit                    # [str], [int]

    while 1:                             # [int]
        if fixedt[abs(lit)] == -1:       # [int]
            fixedt[abs(lit)] = (lit>0)   # [int]
            propcount += 1               # []
            mask_propagate(lit)          # []
                
            for clause in occurrence[-lit]: # [list(int)]
                length, unfixed = info(clause) # [tuple(int)]

                if length == 0:          # [int]
                    #print 'dead', lit    # [str], [int]
                    return 0             # [int]
                elif length == 1: mods.append(unfixed) # [None]
                elif length == 2:        # [int]
                    bincount += 1        # []
                    if failed_literal: mask_binclause(unfixed_lits(clause)) # []

        elif fixedt[abs(lit)] != (lit>0): return 0 # [int]

        current += 1                     # []
        if current == len(mods): break   # [int]
        lit = mods[current]              # [int]

    return 1                             # [int]

def mask_propagate(lit):                 # lit: [int]
    global lit_mask, part_mask # XXX 
    lit_mask[lit] |= part_mask           # []

def mask_binclause(lits):                # lit: [int], lits: [list(int)]
    global global_mask, lit_mask # XXX
    for lit in lits: global_mask |= lit_mask[-lit] # [int]

hoppa = 0xffffffff

def lookahead(mods):                     # mods: [list(int)], i: [int], u: [list(int)], var: [int], part: [list(int)]
    global global_mask, lit_mask, part_mask, some_failure 

    global_mask = hoppa                # [int]
    lit_mask = [0 for var in range(2*(nrofvars+1))] # [list(int)]
    u = unfixed_vars()                   # [list(int)]

    parts = [u[(i*len(u))>>5:((i+1)*len(u))>>5] for i in range(32)] # [list(list(int))]
    masks = [1<<i for i in range(32)]    # [list(int)]

    some_failure = 0                     # [int]
    dif = [-1 for var in range(nrofvars+1)] # [list(int)]

    while global_mask != 0:              # [int]
        #print 'next iteration'           # [str]
        #print binstr(global_mask)        # [str]

        lit_mask = [m & (hoppa-global_mask) for m in lit_mask] # [list(int)]
	
        for i in range(32):              # [int]
            part, part_mask = parts[i], masks[i] # [list(int)], [int]
            
            if global_mask & part_mask == 0: # [int]
                #print 'skip', part_mask  # [str], [int]
                continue
            global_mask &= (hoppa) ^ part_mask # []
            for var in part:             # [int]
	            if fixedt[var] == -1 and not lookahead_variable(var, mods, dif): return 0 # [int]

    if some_failure:                     # [int]
        #print 'final iteration'          # [str]
        dif = [-1 for var in range(nrofvars+1)] # [list(int)]
        for var in unfixed_vars():       # [int]
            if not lookahead_variable(var, mods, dif): # [int]
                 print 'error'           # [str]
    return dif.index(max(dif))           # [int]

def lookahead_variable(var, mods, dif):  # mods: [list(int)], dif: [list(int)], choice: [int]*, var: [int], prop: [int]
    global bincount, some_failure
    score = []                           # [list(int)]
    
    for choice in [var,-var]:            # [int]
        prop_mods = []                   # [list(int)]
        bincount = 0                     # [int]
        prop = propagate(choice, prop_mods) # [int]
        backtrack(prop_mods)             # [int]
        if not prop:                     # [int]
#            print 'failed literal', choice
            some_failure = 1             # [int]
            if not propagate(-choice, mods, 1): return 0 # [int]
            break
        score.append(bincount)           # [None]
	    
    dif[var] = reduce(lambda x,y: 1024*x*y+x+y, score, 0) # [int]
    return 1                             # [int]

def backtrack(mods):                     # lit: [int], mods: [list(int)]
    for lit in mods: fixedt[abs(lit)] = -1 # [int]
    return 0                             # [int]

def info(clause):                        # lit: [int], clause: [list(int)], unfixed: [int], len: [int]
    len, unfixed = 0, 0                  # [int], [int]
    for lit in clause:                   # [int]
        if fixedt[abs(lit)] == -1: unfixed, len = lit, len+1 # [int], [int]
        elif fixedt[abs(lit)] == (lit>0): return -1, 0 # [tuple(int)]
    return len, unfixed                  # [tuple(int)]

def unfixed_vars(): 
    return [var for var in range(1,nrofvars+1) if fixedt[var] == -1] # [list(int)]

def unfixed_lits(clause):                # lit: [int]*, clause: [list(int)], result: [list(int)]r
    result = []                          # [list(int)]
    for lit in clause:                   # [int]
        if fixedt[abs(lit)] == -1: result.append(lit) # [None]
    return result                        # [list(int)]

if not solve_rec():                      # [int]
    print 'unsatisfiable'                # [str]
print 'nodes', nodecount, 'propagations', propcount # [str], [int], [str], [int]
''','''
output(equal=True)
'''),

('double visitCallFunc in visitListComp.. argh', '''
argv = ['','testdata/uuf250-010.cnf']             # [list(str)]

def ffile(name):                          # name: [str]
    return [1]                           # [list(int)]

x = argv[0]                              # [str]
cnf = [y for y in ffile(x)]               # [list(int)]
''', '''
check('cnf', ['list(int)'])
'''),

('copy-by-value test (XXX print inside templates XXX ua)', '''
b = 'b'                                  # [str]
bert = [b,'e','r','t']                   # [list(str)]
print bert                               # [list(str)]

#c = 1                                    # [int]
c = 'c'                                  # [str]
cert = [c,'3','r','t']                     # [list(int,str)]
#cert = [c,3,'r','t']                     # [list(int,str)]
print c                                  # [int, str]
print cert                               # [list(int,str)]

def huhu(s):                             # s: [str]r
   # s += 'hola'                          # []
   # print s                              # [str]
    return s                             # [str]
def huhu2(s):                            # s: [int, str]r
    s += 'hola'                          # []
   # print s                              # [int, str]
    return s                             # [int, str]
    
d = 'crap'                               # [str]
huhu(d)                                  # [str]
print d                                  # [str]
f = 1
huhu(f)

#e = 2                                    # [int]
e = 'crap'                               # [str]
huhu2(e)                                 # [int, str]
print e                                  # [int, str]
''', '''
output("['b', 'e', 'r', 't']\\nc\\n['c', '3', 'r', 't']\\ncrap\\ncrap\\n")
'''),

('japanese puzzle solver by Jack Ha', '''
# (c) Jack Ha 
# --- jack.ha@gmail.com

# code

def row_fit(numbers, startnum, length):  # i: [int], startnum: [int]*, length: [int], s: [int], numbers: [list(int)]
#    print 'row_fit'                      # [str]
    s = 0                                # [int]
    for i in range(startnum, len(numbers)): # [int]
        s += numbers[i]                  # [int]
    if s+len(numbers)-startnum-1 <= length: # [int]
        #print 't16'                      # [str]
        return True                      # [int]
    else:
        return False                     # [int]
        
def possible_row(new_row, old_row, startold): # i: [int], old_row: [list(str)], startold: [int], new_row: [list(str)]
    #print 'possible_row'                 # [str]
    for i in range(len(new_row)):        # [int]
        if old_row[startold+i] <> 'u':   # [int]
            #print 't14'                  # [str]
            if (new_row[i] <> 'u') and (old_row[startold+i] <> new_row[i]): # [int]
                #print 't15'              # [str]
                return False             # [int]
    return True                          # [int]

def row_perm_rec(numbers, startnum, length, old_row, startold): # pos: [int]*, all_empty: [int], numbers: [list(int)], old_row: [list(str)], all_full: [int], hoppa_row: [str, list(str)]r, startnum: [int]*, new_row: [list(str)]r, a: [str, list(str)], i: [int], length: [int]*, startold: [int], x: [int]
    #print 'row_perm_rec', numbers, startnum, length # [str], [list(int)], [int], [int]
    if len(numbers) == startnum:         # [int]
        new_row = []                     # [list(str)]
        for i in range(length):          # [int]
            new_row.append('.')          # [None]
        #print 'ret'                      # [str]
        return new_row                   # [list(str)]
    else:
        #print 't1'                       # [str]
        hoppa_row = 'impossible'         # [str]
        if row_fit(numbers, startnum, length): # [int]
            #print 't2'                   # [str]
            hoppa_row = []               # [list(str)]
            for pos in range(length-numbers[startnum]+1): # [int]
                all_empty = True         # [int]
                for i in range(pos):     # [int]
                    if old_row[startold+i] <> '.' and old_row[startold+i] <> 'u': # [int]
                        #print 't3'       # [str]
                        all_empty = False # [int]
                all_full = True          # [int]
                for i in range(numbers[startnum]): # [int]
                    if old_row[startold+pos+i] <> 'X' and old_row[startold+pos+i] <> 'u': # [int]
                        #print 't4'       # [str]
                        all_full = False # [int]
                if all_empty and all_full: # [int]
                    #print 't5'           # [str]
                    new_row = []         # [list(str)]
                    x = 0                # [int]
                    for i in range(pos): # [int]
                        new_row.append('.') # [None]
                    for i in range(numbers[startnum]): # [int]
                        new_row.append('X') # [None]
                    if pos+numbers[startnum] < length: # [int]
                        new_row.append('.') # [None]
                        x = 1            # [int]
                    
                    a = row_perm_rec(numbers, startnum+1, length-numbers[startnum]-pos-x, old_row, startold+numbers[startnum]+pos+x) # [str, list(str)]
#                    #print 'test0'
                    if a <> 'impossible' or a == []: # [int]
                        #print 't6'       # [str]
                        if a == []:      # [int]
                            #print 't7'   # [str]
                            if length-numbers[startnum]-pos-x <> 0: # [int]
                                #print 't8' # [str]
                                a = 'impossible' # [str]
                        if a <> 'impossible': # [int]
                            #print 't9'   # [str]
                            new_row.extend(a) # [str, list(str)]
                            if possible_row(new_row, old_row, startold): # [int]
                                #print 't10' # [str]
                                if hoppa_row == []: # [int]
                                    #print 't11' # [str]
                                    hoppa_row = new_row[:] # [str, list(str)]
                                for i in range(length): # [int]
                                    if (hoppa_row[i] <> 'u'): # [int]
                                        #print 't12' # [str]
                                        if (hoppa_row[i] <> new_row[i]): # [int]
                                            #print 't13' # [str]
                                            hoppa_row[i] = 'u' # [str]
        return hoppa_row                 # [str, list(str)]

def solve_row(numbers, length, old_row = []): # i: [int], numberscopy: [list(int)], old_row: [list(str)], length: [int]*, numbers: [list(int)], row: [str, list(str)]r
    #print 'solve_row'                    # [str]
    if old_row == []:                    # [int]
        for i in range(length):          # [int]
            old_row.append('u')          # [None]
    numberscopy = numbers[:]             # [list(int)]
    #print 'before'                       # [str]
    row = row_perm_rec(numberscopy, 0, length, old_row, 0) # [str, list(str)]
    #print 'after'                        # [str]
    if row <> 'impossible':              # [int]
        if row == []:                    # [int]
            for i in range(length):      # [int]
                row.append('u')          # [None]
        # following not used
        #new_row = []                     # [list(str)]
        #for i in range(length):          # [int]
        #    if (old_row[i] == 'u') or (old_row[i] == row[i]): # [int]
        #        new_row.append(row[i])   # [None]
        #    else:
        #        new_row.append('u')      # [None]
    return row                           # [str, list(str)]

def print_puzzle(puzzle, puzzleboard):   # puzzle: [list(list(list(int)))], y: [int], x: [int], puzzleboard: [list(list(str))]
    for y in range(len(puzzle[1])):      # [int]
        for x in range(len(puzzle[0])):  # [int]
            print puzzleboard[y][x],     # [str]
        print
    
def check_puzzle(puzzlecolumns, puzzlerows): # puzzlecolumns: [list(list(int))], puzzlerows: [list(list(int))], i: [list(int)], sum1: [int], sum2: [int]
    sum1 = 0                             # [int]
    for i in puzzlecolumns:              # [list(int)]
        sum1 += sum(i)                   # [int]
    sum2 = 0                             # [int]
    for i in puzzlerows:                 # [list(int)]
        sum2 += sum(i)                   # [int]

#    print "Sum:", sum1, sum2, "Area:", len(puzzlecolumns)*len(puzzlerows), "Ratio:", float(sum2)/float(len(puzzlecolumns)*len(puzzlerows)) # [str], [int], [int], [str], [int], [str], [float]
    return sum1 == sum2                  # [int]

def create_empty(x,y):                   # a: [list(list(str))]r, i: [int], j: [int], y: [int]*, x: [int]*
    r = []                               # [list(str)]
    a = []                               # [list(list(str))]
    for i in range(x):                   # [int]
        r.append('u')                    # [None]
    for j in range(y):                   # [int]
        a.append(r[:])                   # [None]
    return a                             # [list(list(str))]
    
def solve_puzzle(puzzlecolumns, puzzlerows): # changed: [int], rounds: [int], puzzlerows: [list(list(int))], newcol: [str, list(str)], sizeX: [int]*, sizeY: [int]*, puzzlecolumns: [list(list(int))], s: [str, list(str)], y: [int], x: [int], col: [list(str)], puzzleboard: [list(list(str))]
    sizeX = len(puzzlecolumns)           # [int]
    sizeY = len(puzzlerows)              # [int]
#    print 'X size:', sizeX, 'Y size:', sizeY # [str], [int], [str], [int]
    puzzleboard = create_empty(sizeX, sizeY) # [list(list(str))]
    #print_puzzle([puzzlecolumns,puzzlerows], puzzleboard) # []
    changed = True                       # [int]
    rounds = 0                           # [int]
    while changed:                       # [int]
        changed = False                  # [int]
        for y in range(sizeY):           # [int]
#            print '- ',                  # [str]
            s = solve_row(puzzlerows[y], sizeX, puzzleboard[y])[:] # [str, list(str)]
            for x in range(sizeX):       # [int]
                if puzzleboard[y][x] <> s[x]: changed = True # [int]
                puzzleboard[y][x] = s[x] # [str]
        #print
        #print "Rounds:", rounds          # [str], [int]
        #print_puzzle([puzzlecolumns,puzzlerows], puzzleboard) # []
        for x in range(sizeX):           # [int]
#            print '|',                   # [str]
            col = []                     # [list(str)]
            for y in range(sizeY):       # [int]
                col.append(puzzleboard[y][x]) # [None]
            newcol = solve_row(puzzlecolumns[x], sizeY, col) # [str, list(str)]
            for y in range(sizeY):       # [int]
                if puzzleboard[y][x] <> newcol[y]: changed = True # [int]
                puzzleboard[y][x] = newcol[y] # [str]
        rounds += 1                      # [int]
        #print
        #print_puzzle([puzzlecolumns,puzzlerows], puzzleboard) # []
        #print "Rounds:", rounds          # [str], [int]
    print 'Rounds:', rounds
    return                               # [None]


def bert():                              # puzzlecolumns: [list(list(int))], puzzlerows: [list(list(int))]
    puzzlecolumns = [[6],[8,3],[10,5],[10,6],[16,3],[10,3,2],[8,1,2],[6,5,2,1,2],[4,2,3,1,2,2],[3,1,4,1,1,1],[3,1,4,2,1],[5,5,2,3,1],[6,3,3,1],[5,5,2,3,1],[4,1,3,2,1],[2,1,4,1,1,1],[4,2,4,1,2,2],[6,5,2,1,2],[9,1,2],[10,3,2],[17,3],[11,6],[11,5],[9,3],[7]] # [list(list(int))]

    puzzlerows = [[5],[6,7],[8,9],[10,4,9],[25],[25],[8,5,8],[7,3,7],[7,3,1,3,7],[5,2,1,1,2,5],[4,1,1,1,1,3],[1,1,3,1,3,1],[1,5,5,1],[2,5,5,2],[2,3,1,3,2],[6,3,6],[4,3,3,3,4],[3,3],[3,2,2,3],[3,9,3],[3,5,3],[4,3,4],[3,3],[2,2],[5]] # [list(list(int))]

    if check_puzzle(puzzlecolumns, puzzlerows): # [int]
        solve_puzzle(puzzlecolumns, puzzlerows) # []
    else:
        print "Puzzle is incorrect, sum of rows <> sum of columns" # [str]

bert()                                   # []
''', '''
output('Rounds: 9\\n')
'''),

('unboxing in the face of real polymorphism XXX ua', '''
#a = 1                                    # [int]
#a = 1                                    # [int]
b = 1                                    # [int]
a = 'hoi'                                # [str]

print a                                  # [int, str]
print b                                  # [int]
''', '''
output('hoi\\n1\\n')
'''),

('merge integers..', '''
def qbert(a):                            # a: [int]
    print a                              # [int]

a=1                                      # [int]
b=2                                      # [int]
qbert(1)                                 # []
qbert(2)                                 # []
qbert(a)                                 # []
qbert(b)                                 # []
''','''
assert len(cv.funcs['qbert'].vars['a'].types()) == 1
output('1\\n2\\n1\\n2\\n')
'''),

('class copy test', '''
#class list:                              # unit: [int]*
#    def maonetuhcount(self):             # self: []
#        return 1                         # [int]
#
#    def __len__(self):                   # self: [list(int)]
#        return 1                         # [int]
#
#class int_: 
#    def __repr__(self):                  # self: [int]
#        return ''                        # [str]

puzzlecolumns = [1]                    
print puzzlecolumns.__len__()
''','''
'''),

('pisang sat solver', '''
# (c) Mark Dufour 
# --- mark.dufour@gmail.com

def reduce(f, l, i=-1):                  # f: [lambda0], i: [int], l: [list(int)], r: [int]
    if not l:                            # [list(int)]
        if i != -1: return i             # [int]
        print '*** ERROR! *** reduce() called with empty sequence and no initial value' # [str]

    if i != -1:                          # [int]
        r = f(i, l[0])                   # [int]
    else:
        r = l[0]                         # [int]

    for i in range(len(l)-1):            # [int]
        r = f(r, l[i+1])                 # [int]

    return r                             # [int]

# prelims

argv = ['','testdata/uuf250-010.cnf']             # [list(str)]

cnf = [l.strip().split() for l in file(argv[1]) if l[0] not in 'c%0\\n'] # [list(list(str))]
clauses = [[int(x) for x in m[:-1]] for m in cnf if m[0] != 'p'] # [list(list(int))]
nrofvars = [int(n[2]) for n in cnf if n[0] == 'p'][0] # [int]
vars = range(nrofvars+1)                 # [list(int)]
occurrence = [[] for l in vars+range(-nrofvars,0)] # [list(list(list(int)))]
for clause in clauses:                   # [list(int)]
    for lit in clause: occurrence[lit].append(clause) # [int]
fixedt = [-1 for var in vars]            # [list(int)]

def solve_rec():                         # la_mods: [list(int)], var: [int], prop_mods: [list(int)], choice: [int]
    global nodecount
    nodecount += 1                       # []
    if nodecount == 100:
        return 1
    if not -1 in fixedt[1:]:             # [int]
        print 'v', ' '.join([str((2*fixedt[i]-1)*i) for i in vars[1:]]) # [str], [str]
        return 1                         # [int]

    la_mods = []                         # [list(int)]
    var = lookahead(la_mods)             # [int]
    #print 'select', var                  # [str], [int]
    if not var: return backtrack(la_mods) # [int]

    for choice in [var, -var]:           # [int]
        prop_mods = []                   # [list(int)]
        if propagate(choice, prop_mods) and solve_rec(): return 1 # [int]
        backtrack(prop_mods)             # [int]

    return backtrack(la_mods)            # [int]

def propagate(lit, mods):                # current: [int], unfixed: [int], mods: [list(int)], clause: [list(int)], lit: [int], length: [int]
    global bincount

    current = len(mods)                  # [int]
    mods.append(lit)                     # []

    while 1:                             # [int]
        if fixedt[abs(lit)] == -1:       # [int]
            fixedt[abs(lit)] = (lit>0)   # [int]
            for clause in occurrence[-lit]: # [list(int)]
                length, unfixed = info(clause) # [tuple(int)]
                
                if length == 0: return 0 # [int]
                elif length == 1: mods.append(unfixed) # []
                elif length == 2: bincount += 1 # []

        elif fixedt[abs(lit)] != (lit>0): return 0 # [int]

        current += 1                     # []
        if current == len(mods): break   # [int]
        lit = mods[current]              # [int]

    return 1                             # [int]

def lookahead(mods):                     # mods: [list(int)], dif: [list(int)], choice: [int], score: [list(int)], prop_mods: [list(int)], var: [int], prop: [int]
    global bincount

    dif = [-1 for var in vars]           # [list(int)]
    for var in unfixed_vars():           # [int]
        score = []                       # [list(int)]
        for choice in [var, -var]:       # [int]
            prop_mods = []               # [list(int)]
            bincount = 0                 # [int]
            prop = propagate(choice, prop_mods) # [int]
            backtrack(prop_mods)         # [int]
            if not prop:                 # [int]
                if not propagate(-choice, mods): return 0 # [int]
                break
            score.append(bincount)       # []
        dif[var] = reduce(lambda x, y: 1024*x*y+x+y, score, 0) # [int]
 
    return dif.index(max(dif))           # [int]

def backtrack(mods):                     # lit: [int], mods: [list(int)]
    for lit in mods: fixedt[abs(lit)] = -1 # [int]
    return 0                             # [int]

def info(clause):                        # lit: [int], clause: [list(int)], unfixed: [int], len: [int]
    len, unfixed = 0, 0                  # [int], [int]
    for lit in clause:                   # [int]
        if fixedt[abs(lit)] == -1: unfixed, len = lit, len+1 # [int], [int]
        elif fixedt[abs(lit)] == (lit>0): return -1, 0 # [tuple(int)]
    return len, unfixed                  # [tuple(int)]

def unfixed_vars(): return [var for var in vars[1:] if fixedt[var] == -1] # [list(int)]
    
nodecount = 0                            # [int]
if not solve_rec():                      # [int]
    print 'unsatisfiable', nodecount     # [str], [int]
''', '''
output(equal=True)
'''),

('pisang: list comprehension types', '''
argv = ['','testdata/uuf250-010.cnf']             # [list(str)]

cnf = [l.strip().split() for l in file(argv[1]) if l[0] not in 'c%0\\n'] 
clauses = [[int(x) for x in m[:-1]] for m in cnf if m[0] != 'p'] 
nrofvars = [int(n[2]) for n in cnf if n[0] == 'p'][0] 
vars = range(nrofvars+1)                
occurrence = [[[c for c in clauses if -v in c],[c for c in clauses if v in c]] for v in vars] 
fixedt = [-1 for var in vars]            
''', '''
check('cnf',['list(list(str))'])
check('clauses',['list(list(int))'])
check('nrofvars',['int'])
check('occurrence',['list(list(list(list(int))))'])
check('fixedt',['list(int)'])
output()
'''),

('simple cpa crap','''
def propagate(la):                       # la: [list(int)]
    print la, la                         # [str], [str]

propagate([1])                           # []
propagate([2])                           # []
''', '''
'''),

('pears','''
class pears:                           # type: [str]*, amount: [int, float]*, music: [str]*, unit: [int, float, str]*
    def __init__(self, amount, hype):    # self: [pears(float,str), pears(int,int), pears(int,float)], type: [str]*, amount: [int, float]*
        self.amount = amount             # [int, float]
        self.hype = hype                 # [str]

    def shakeit(self, times):          # self: [pears(int,float)], times: [int]
        pass

    def setunit(self, unit):             # self: [pears(float,str), pears(int,int), pears(int,float)], unit: [int, float, str]*
        self.unit = unit                 # [int, float, str]

    def __repr__(self):                  # self: [pears(int,float)]
        return self.hype                 # [str]

#print 'pears simulator'                

p = pears(2, 'it')                   # [pears(int,float)]
p.setunit(1.0)                           # []
q = pears(2, 'it')                   # [pears(int,int)]
q.setunit(1)                             # []
r = pears(2.0, 'it')                 # [pears(float,str)]
r.setunit('ha')                          # []

p.shakeit(7)                           # []
p.music = 'cool'                         # [str]

m = [1,2,3,4]                            # [list(int)]

lp = [q,q]                               # [list(pears(int,int))]
print p, m, lp                           # [str], [str], [str]
''','''
output('it [1, 2, 3, 4] [it, it]\\n')
'''),

('__setitem__','''
cube = [(1,2),(3,4)]                     # [list_tuple_int]
cube[0] = (1,2)                          # [tuple_int]
''','''
check('cube',['list(tuple(int))'])
#check('cube',['list(tuple2(int, int))'])
'''),

('list_list_int_tuple_int','''
cube = [[1,2],(3,4)]                     
''','''
check('cube',['list(pyseq(int))'])
'''),

('fred = fred + fred', '''
class integer: pass
        
class fred:                                 
    def __add__(self, x):              
        i = integer()                   
        return i                         

def hoei():     
    a = fred()   
    return a+a    

a = hoei()        
''','''
check('a',['integer'])
'''),

('function nested for-in..','''

def hoei(cube):                          # x: [tuple_int], cube: [list_tuple_int], pos: [tuple_int]
    for pos in cube:                     # [list_tuple_int]
        x = pos                          # [tuple_int]
    return x                             # [tuple_int]

cube = [(1,2),(3,4),(5,6)]               # [list_tuple_int]
b = hoei(cube)                               # [tuple_int]
''','''
check('b',['tuple(int)'])
#check('b',['tuple2(int, int)'])
'''),

('simple for-in', '''
for a in [(1,2),(3,4)]:                  # [list_tuple_int]
    pass
''','''
check('a',['tuple(int)'])
#check('a',['tuple2(int, int)'])
'''),

('list_float_tuple_int XXX ua', '''
def gettuple():       
    return (5,6)                    

a = gettuple()                     
cube = [(1,2),(3,4),a,gettuple()]  
#cube.append(1.0)                  
''','''
check('a',['tuple(int)'])
#check('a',['tuple2(int, int)'])
check('cube',['list(tuple(int))'])
#check('cube',['list(tuple2(int, int))'])
'''),

('return self.unit', '''
cube = []                          
cube.append(1.0)                    
y = cube[0]                          
''','''
check('y',['float'])
'''),

('simple list indexing', '''
#class list:                              # unit: [float]*
#    def append(self, x):                 # x: [float], self: [list_float]
#        self.unit = x                    # [float]
#
#    def __getitem__(self, i):            # i: [int], a: [float], self: [list_float]
#        a = self.unit                    # [float]
#        return a                         # [float]

cube = []                                # [list_float]
cube.append(1.0)                         # []

y = cube[0]                                  # [float]
''','''
check('y',['float'])
'''),

('the same, now using append', '''
cube = []                                # [list_float_int]
#cube.append(1)                           # [None]
cube.append(1.0)                         # [None]
''', '''
check('cube',['list(float)'])
'''),

('simple real data polymorphism on list XXX ua', '''
cube = []                                # [list_int_float]
cube.unit = 1.0                          # [float]
#cube.unit = 'doh'                          # [float]
#cube.unit = 1                            # [int]

''', '''
check('cube', ['list(float)'])
'''),

('max escape', '''
class integer:    
    def __gt__(self, b):            # self: [integer], b: [integer]
        return 1

def maxi(a, b):                           # a: [integer]r, b: [integer]r
    if a > b:                            # [bool]
        return a                         # [integer]
    return b                             # [integer]

def qbert():                             # a: [integer], c: [integer]r, b: [integer]
    a = integer()                        # [integer]
    b = integer()                        # [integer]
    c = maxi(a, b)                        # [integer]
    return c                             # [integer]

qbert()                                  # [integer]
''', '''
#escape(1, [('qbert','c'), ('max','b'),('max','a')])
#escape(0, [('qbert','a'), ('qbert','b')])
'''),

('basic escape analysis cases', '''
class xevious:                           # y: [int]*, z: [str]*
    def solvalou(self, x):               # x: [int]*, self: [xevious_str]
        return x                         # [int]

def pacman(a):                           # a: [int]
    return 1                             # [int]

def qbert():                             # a: [int], c: [int], b: [int]*, e: [int]*, d: [int]*, x: [xevious_str]
    c = 1                                # [int]
    a = 1                                # [int]
    pacman(a)                            # [int]
    b = 1                                # [int]
    a = c                                # [int]
    d = 1                                # [int]
    e = 1                                # [int]
    x = xevious()                        # [xevious_str]
    x.y = d                              # [int]
    x.z = 'hoi'                          # [str]
    x.solvalou(e)                        # [int]

    return b                             # [int]

qbert()                                  # [int]
''', '''
#escape(2, [('qbert','d')])
#escape(1, [('qbert','b'),('xevious','solvalou','x')])
#escape(0, [('qbert','a'),('qbert','e'),('qbert','c'),('qbert','x')])
'''),

('typerepr for simple data polymorphism', '''
class fred:                    
    def init(self, whatsit):    
        self.thingy = whatsit    
        return whatsit

h = fred()  
c = h.init(1)    

g = fred()  
e = g.init('ho') 
''','''
check('h', ['fred(int)'])
check('g', ['fred(str)'])
check('e', ['str'])
check('c', ['int'])
'''),

('stupid escape visitor mess-up', '''
class fred:                              # thingy: [int]
    def hottum(self, x):                 # [fred], [str]
        b = 4                            # [int]
        return b                         # [int]

def hottum():                             
    pass

h = fred()                               # [fred]
c = h.hottum('jo')                       # [int]
''', '''
check('c', ['int'])
'''),

('max, integer class, __gt__, bool type', '''
class integer:
    def __gt__(self, b):
        return 1

def maxi(a, b):                           # [integer], [integer]
    if a > b:                            # [bool]
        return a                         # [integer]
    return b                             # [integer]

a = integer()                            # [integer]
b = integer()                            # [integer]
c = maxi(a, b)                            # [integer]
d = a > b                                # [bool]
''', '''
check('c',['integer'])
check('d',['int'])
'''),

('self.__setattr__ -> __getattr__', '''
class fred:                              # a: []
    def huh(self):                       # []
        self.a = 1                       # [int]

a = fred()                               # [fred]
a.huh()
b = a.a                                  # [int]
''', '''
check('b',['int'])
'''),

('__setattr__ -> __getattr__', '''
class fred:                              # hallo: [int]
   pass

a = fred()                               # [fred_int]
a.hallo = 1                              # [int]
b = a.hallo                              # [int]

c = fred()                               # [fred_str]
c.a = 'god'                              # [str]
d = c.a                                  # [str]
''', '''
check('b',['int'])
check('d',['str'])
'''),

('addition operator', '''
class fred:                      
    def __add__(self, x):                # [fred], [fred]
        return x                         # [int]

a = fred()                               # [fred] = [fred]
b = a + a                                # [int] = [int]
''', '''
output(equal=True)
#check('b',['int'])

'''),

#('two-dim. duplication', '''
#class fred:                       
#    def init(self, whatsit):     
#        self.thingy = whatsit   
#        return whatsit         
#
##    def hottum(self, x):      
#        self.woink(1)        
#        b = self.woink(x)   
#        return b           
#
#    def woink(self, y):   
#        return y         
#
#def hottum(x):          
#    a = 1.0            
#    a = x             
#    return x         
#
#hottum(1)       
#hottum(1)        
#a = hottum('hoi')      
#
#h = fred()          
#b = h.hottum('jo')       
#c = h.init(1)             
#
#beh = 1               
#beh = 1.0              
#g = fred()              
#d = g.hottum(beh)            
#e = g.init(1)                 
#
#i = fred()                 
#j = i.init('hop')               
#k = i.init(1)                    
#''','''
#check('a', ['str'])
#check('h', ['fred_int'])
#check('g', ['fred_int'])
##check i
#check('b', ['str'])
#check('c', ['int'])
#check('beh', ['int','float'])
#check('d', ['int','float'])
#check('e', ['int'])
#check('k', ['int'])
#check('j', ['str'])
#'''),

('nameclash', '''
def aap(y):
    return y    
def hap(y):
    return y   
x = aap(1)
y = hap(1.0)
''','''
check('x', ['int'])
check('y', ['float'])
'''),

('return via', '''
def bwa(): 
    d = 'hoi'
    return d
a = bwa()
''','''
check('a',['str'])
'''),

('return const', '''
def bla():
    return 8
a = bla()
''','''
check('a',['int'])
'''),

('simple class method', '''
class fred:
    def speak(self, x):
        return x
b = fred()
c = b.speak('goedzo!')
''','''
check('c', ['str'])
'''),

('list instantiation', '''
a = [1]
''','''
check('a',['list(int)'])
'''),

('boing boing boing', '''
def ident(x):
    return x
def boing(c, d):
    return ident(c)
a = 1
h = boing(boing(a,1.0),boing(3.0,a))
''','''
check('h', ['int'])
'''),

('simple class', '''
class fred: pass
x = fred()
''','''
check('x', ['fred'])
'''),

('double call', '''
def ident(x):
    return x
def boing(c, d):
    return ident(c)
aap = boing(1,1.0)
''','''
check('aap', ['int'])
'''),

('simple assignment', '''
a = 1
''','''
check('a', ['int'])
''')]

tests.reverse()
failures = []

def check(name, typelist):
    ts = typesetreprnew(cv.globals[name], None, False) 
    if ts != '['+typelist[0]+']':
        print 'expected for', name+':'
        print '['+typelist[0]+']'
        print 'and not:'
        print ts

        raise Exception('hell')

def getvar(name):
    if len(name) == 3:
        return cv.classes[name[0]].funcs[name[1]].vars[name[2]]
    return cv.funcs[name[0]].vars[name[1]]

def unittest(i):
    global gx, cv, number, code, name, test
    number = i
    (name,code,test) = tests[i]

    # analysis
    try:
        print '*** test:', name, i

        t1 = os.times()
        gx = analysis(code, True)
        results[i]['analysis'] = os.times()[0]-t1[0]
        cv = gx.main_module.mv

        exec test 

        print '*** success:', name, i
        print
    except:
        print '*** failure:', name
        print
        traceback.print_exc()
        failures.append(i)
        return

    return

def output(text=None, equal=False):
    global native_output
    if only_analyze: return

    # compare with compiled c++ output
    print '*** compiling & running..'

    os.system('make clean')

    # --- unix 
    if sys.platform != 'win32':
        os.system('make') # >& /dev/null')
        t1 = os.times()
        com = os.popen('./test')

    # --- windows
    else:
        os.system('make')
        t1 = os.times()
        com = os.popen('test')

    native_output = ''.join(com.readlines())

    if com.close():
        print 'does not compile:', name
        raise Exception('hell')

    results[number]['runtime'] = os.times()[2]-t1[2]

    # --- run test in CPython
    if equal or try_cpython: 
        print '*** running test using CPython..'
        file('wahh','w').write(code)
        t1 = os.times()
        com2 = os.popen('python wahh')
        if equal:
            text = ''.join(com2.readlines())
        else: 
            com2.readlines()
        com2.close()
        results[number]['cpython'] = os.times()[2]-t1[2]

    # --- run test using Psyco
    if try_psyco:
        print '*** running test using CPython/Psyco..'
        file('wahh','w').write('import psyco\npsyco.profile()\n'+code)
        t1 = os.times()
        com2 = os.popen('python wahh')
        if equal:
            text = ''.join(com2.readlines())
        else: 
            com2.readlines()
        com2.close()
        results[number]['psyco'] = os.times()[2]-t1[2]

    if text and native_output != text:
        print 'output:'
        print native_output
        print 'expected output:', name
        print text

        #for (i, (a,b)) in enumerate(zip(text, native_output)):
        #    if a != b:
        #        native_output = native_output[:i]+'>>>'+native_output[i:]
        #        break

        raise Exception('hell')

# --- parse arguments and options

args, options = [], Set()

for arg in sys.argv[1:]:
    if arg.startswith('-'): 
        options.update(arg[1:])
    else: args.append(int(arg))

if not 'p' in options:
    print '*** SHEDSKIN Python->C++ Compiler ***'
    print 'Copyright 2005-2008 Mark Dufour; License GNU GPL version 3 (See LICENSE)'
    print

if 'h' in options:
    print "format:"
    print "./unit.py [options] [test-number]*"
    print "(no test-number means all tests; two test-numbers indicate interval; use -l option for selecting individual tests)"
    print
    print "options:"
    print "'-p': print test"
    print "'-a': only analyze and generate code"
    print "'-l': give individual test numbers"
    print "'-t': show available tests"
    print "'-r': reverse test order"
    print "'-f': break after first failure"
    print "'-n': show analysis times"
    print "'-o': show running times"
    print "'-y': show psyco times"
    print "'-c': show cpython times"
    print "'-s': use hardcoded set of tests"

    sys.exit()

# --- print test
if 'p' in options: 
    print tests[args[0]][1]
    sys.exit()

# --- determine test list
if 'l' in options:
    test_nrs = args
elif len(args) == 1:
    test_nrs = [args[0]]
elif len(args) == 2:
    if args[0] > args[1]: 
        args[0], args[1] = args[1], args[0]
        options.add('r')
    test_nrs = range(args[0],args[1])
else:
    test_nrs = range(len(tests))

if 'r' in options:
    test_nrs.reverse()

# --- only print tests
if 't' in options:
    for test in test_nrs:
        print str(test)+': '+tests[test][0]
    sys.exit()

only_analyze = 'a' in options
try_cpython = 'c' in options
try_psyco = 'y' in options
analysis_time = 'n' in options
runtime = 'o' in options

if 's' in options:
    test_nrs = [99, 122, 123, 132, 133, 148, 149, 151, 153, 154, 157]

disabled = [34, 41, 42, 49, 58, 80, 85, 116, 121, 117, 145, 149]
results = [{} for test in tests]

# --- execute tests
for test in test_nrs:
    if test not in disabled:
        unittest(test)
        #print 'end', os.times()
    if failures and 'f' in options:
        break

if not failures: 
    print '*** no failures, yay!'

    # --- performance table
    if runtime or analysis_time or try_cpython or try_psyco:
        print '*** performance table:\n'
        header = '\t'
        if try_cpython: header += 'cpython\t'
        if try_psyco: header += 'psyco\t'
        if runtime: header += 'time\t'
        if try_cpython and runtime: header += 'xcpy\t'
        if try_psyco and runtime: header += 'xpsy\t'
        if analysis_time: header += 'anal\t'
        header += 'loc'
        print header

        for i in test_nrs:
            if runtime and results[i]['runtime'] == 0:
                print "UHOH", i
                results[i]['runtime'] = 0.00001

            line = str(i)+'\t'

            if try_cpython: line += '%.2f\t' % results[i]['cpython']
            if try_psyco: line += '%.2f\t' % results[i]['psyco']
            if runtime: line += '%.2f\t' % results[i]['runtime']
            if try_cpython and runtime: line += '%.2f\t' % (results[i]['cpython'] / results[i]['runtime'])
            if try_psyco and runtime: line += '%.2f\t' % (results[i]['psyco'] / results[i]['runtime'])
            if analysis_time: line += '%.2f\t' % results[i]['analysis']
            line += str(len([x for x in tests[i][1].split('\n') if x.strip() and x.strip()[0] != '#'])-1) # loc
            line += '\t'+tests[i][0]

            print line
else:
    print '*** tests failed:', len(failures)
    print [(i, tests[i][0]) for i in failures] 




