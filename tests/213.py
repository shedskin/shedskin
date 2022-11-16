# sys.maxsize
from sys import maxsize as MAXSIZE
print(MAXSIZE > 0)

#bisect comparison overloading
from bisect import insort
class A(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return "A(%s, %s)" % (self.x, self.y)

    def __lt__(self, other):
        return self.x+self.y < other.x+other.y

    def __eq__(self, other):
        return self.x+self.y == other.x+other.y

pairs = [[18, 6], [28, 5], [35, 26], [31, 28], [3, 3], [32, 37], [11, 17], [28, 29]]
items = []
for pair in pairs:
    insort(items, A(pair[0], pair[1]))
print(items)

# TODO with expr1 as bla, expr2..

import csv
dialects = csv.list_dialects()
print('excel' in dialects)
print('excel-tab' in dialects)
# TODO 'unix' not supported atm

#csv default writer lineterminator?

class Oink:
    def __getitem__(self, xy):
        x, y = xy
        print('get', xy)
        return x*y
    def __setitem__(self, xy, z):
        x, y = xy
        print('set', x, y, z)
oink = Oink()
oink[4, 5] = oink[2, 3]
t2 = (6, 7)
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
except FileNotFoundError as errr:  # TODO except IOError
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

#generator and arg unpacking
def genpack(ij,a,b):
    i,j = ij
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

# qualify & add include for class name
from testdata import iec2
from testdata import d1541
IEC = iec2.IECBus()
hop = d1541.D1541(IEC, 8)
print(hop.get_data())

#os.popen2 improvement
#import os
#child_stdin, child_stdout = os.popen2(["echo", "a  text"], "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2(iter(["echo", "a  text"]), "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2(("echo", "a  text"), "r")
#print(repr(child_stdout.read()))
#child_stdin, child_stdout = os.popen2("echo a  text", "r")
#print(repr(child_stdout.read()))

# default print precision?
import math
print(math.cosh(2))

# print(end)
print(18, end=' ')
print(19)
