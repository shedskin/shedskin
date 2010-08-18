
#simple fixes
print 8+(2 if 1 else 3)
print repr('\377ai\37aoi\001123\00hoi\01hoi\0hoi')

# add_strs()
print 'x'+'x'+'x'

#os.path
import os.path

print os.path.join('heuk')
print os.path.join('heuk', 'emeuk')
print os.path.join('heuk', 'emeuk', 'meuk')

from os.path import *

print join('a','b','c')

realpath('unit.py')
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

getsize('unit.py')
getatime('unit.py')
getctime('unit.py')
getmtime('unit.py')

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
print 'ab\ncd\r\nef\rghi\n'.splitlines()
print 'ab\ncd\r\nef\rghi\n'.splitlines(1)
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


