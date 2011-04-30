
#equality..
hx=['A','B','C','D','E','F']
try:
    print hx.index('A'.upper())
    print hx.count('A'+'')
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
#print v4 % t4 XXX 2.7?

print '%(aap)s %(bert)d %% %(bert)c' % {'aap': 'hallo', 'bert': 72}

#re.sub replacement function
import re

def hexrepl(match):
   value = int(match.group())
   return hex(value)

p = re.compile(r'\d+')
print p.sub('****', 'Call 65490 for printing, 49152 for user code.', 1)
print p.sub(hexrepl, 'Call 65490 for printing, 49152 for user code.', 1)
print p.sub(hexrepl, 'Call 65490 for printing, 49152 for user code.')
print re.sub(r'\d+', '****', 'Call 65490 for printing, 49152 for user code.', 2)
print re.sub(r'\d+', hexrepl, 'Call 65490 for printing, 49152 for user code.', 2)

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

# ignore __getattr__, __setattr__ for ancestor calls
class RawConfigParser:
    KWEK = 'kwek!'

class MyConfigParser(RawConfigParser):
    def read(self):
        self.sections = RawConfigParser.KWEK

configg = MyConfigParser()
configg.read()

# inheritance lookup
class HUP:
    def hup(self, x):
        print 'huppa', x

class HOP(HUP):
    pass

class HOPPA(HOP):
    def __init__(self):
        HOP.hup(self, 8)
        HOPPA.hup(self, 9)

HOPPA()

#ConfigParser # XXX readfp
import ConfigParser

config = ConfigParser.ConfigParser(defaults={'aha': 'hah'})

config.read("testdata/test.conf")

print config.getint('ematter', 'pages'), config.getfloat('ematter', 'pages')
print int(config.getboolean('ematter', 'hop'))

print int(config.has_section('ematteu'))
config.add_section('meuk')
config.set('meuk', 'submeuk1', 'oi')
config.set('meuk', 'submeuk2', 'bwah')
if config.has_section('meuk') and config.has_option('meuk', 'submeuk1'):
    config.remove_option('meuk', 'submeuk1')
config.add_section('bagger')
config.remove_section('bagger')

# dump entire config file
for section in sorted(config.sections()):
    print section
    for option in sorted(config.options(section)):
        print " ", option, "=", config.get(section, option)

print config.get('ematter', 'pages', vars={'var': 'blah'})

fl = open('testdata/test.ini', 'w')
config.write(fl)
fl.close()
print sorted(open('testdata/test.ini').readlines())

print config.defaults().items()
print sorted(config.items('ematter', vars={'var': 'blah'}))

rcp = ConfigParser.RawConfigParser()
rcp.read(["testdata/test.conf"])

print rcp.get('ematter', 'pages') #, vars={'var': 'blah'})
print sorted(rcp.items('ematter'))

# catch str exception
try:
    raise '2888'
except:
    print 'welja'


