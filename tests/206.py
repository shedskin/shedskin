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
