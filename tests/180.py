
#re
import re

try:
        a = re.compile(r'\b(?P<email_name>[\w.-]+?)@(?P<email_domain>[a-z.-]{3,})\b', re.IGNORECASE)
        b = 'bob (BoB@gmaiL.com) said to sally (sally123_43.d@hOtmail.co.uk) that no-name (not_a-real@em_ail.dres) was annoying...'

        print a.search(b, 20).group(0)
        print a.match(b, 5).expand(r'the found name: \g<email_name>\nthe domain: \g<email_domain>')
        print a.subn(r'\1 AT \g<email_domain>', b)
        print a.sub(r'<a href="mailto:\g<0>">\1</a>', b)
#       print a.findall(b)

        c = re.compile(r'''
                \b
                (?P<protocol>https?|(ftp)|(?P<mailto>mailto))
                :(?(mailto)|//)
                (
                        (?P<user>[\w._-]+?)
                        (?(mailto)

                                |
                                        :(?P<pass>[\w._-]*?)
                        )
                        @
                )?
                (?P<domain>[\w.-]+)
                (?(mailto)

                        |
                                (?P<path>/[^\s]*)
                )
                \b
                ''', re.X)
        d = 'fasdf mailto:bob@gmail.com, dasdfed ftp://haha:hoho@bla.com/files, http://fsesdf@asd.com orRLY!!?!L!? \
        https://example.com/OMG.html'

        allm = c.finditer(d)
        i = 1
        for mo in allm:
                s = str(i) + ': \n'
                s += '\tfull: ' + mo.group(0)
                s += '\n\tnamed: '

                gd = mo.groupdict()
                for k in sorted(gd):
                        if gd[k] == None: continue
                        s += '\n\t\t' + k + ': ' + gd[k]

                print s
                i += 1

        print re.split(r'\W+', b)
        print re.split(r'(\W+)', b, 2)

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
print glob.glob('run.py')
import fnmatch
print int(fnmatch.fnmatch('run.py', 'run.[py]y'))

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
import testdata.bert2 as bert
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


