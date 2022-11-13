
# defaultdict
from collections import defaultdict
s3 = [('red', 1), ('blue', 2), ('red', 3), ('blue', 4), ('red', 1), ('blue', 4)]
d3 = defaultdict(set)
for k3, v3 in s3:
    d3[k3].add(v3)

print(sorted(d3.items()))

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

#print('hello\0world') # TODO ???

# filter, map, zip, range -> no more lists!!! (see also removed itertools.ifilter/imap/izip)

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
