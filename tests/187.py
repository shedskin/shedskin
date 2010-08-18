
# __ss_result
print [result for result in range(4)]

# void *constant caused by unused function
def parse150():
    a = '150'
def ftpcp():
    'ah' in ('150',)
parse150()

# forward func refs
class FTP:
    def retrbinary(self, callback):
        callback('hoi')
    def retrlines(self):
        callback = print_line
        callback('hoi2')
def print_line(line):
    print line
ftp = FTP()
ftp.retrbinary(print_line)
ftp.retrlines()

# re.subn, re.re_object.subn (douglas mcneil)
import re
res = re.subn('a', 'ama', 'amadeus')
print res
res = re.compile('a').subn('ama', 'amadeus')
print res

# str.replace corner cases (douglas mcneil)
print 'faaaaaredfredbrrr'.replace('r', 'rr')
print 'aha'.replace('','men')

# strip whitespace
print int(' \t\n0x18 \t ', 16)

# check add_strs optimization
print 'hoi'
print 'hoi' + 'mams'
print 'hoi' + 'mams' + 'ik'
print 'hoi' + 'mams' + 'ik' + 'ben'
print 'hoi' + 'mams' + 'ik' + 'ben' + 'er'
print 'hoi' + 'mams' + 'ik' + 'ben' + 'er' + 'weer'
print 'h'
print 'h' + 'm'
print 'h' + 'm' + 'i'
print 'h' + 'm' + 'i' + 'b'
print 'h' + 'm' + 'i' + 'b' + 'e'
print 'h' + 'm' + 'i' + 'b' + 'e' + 'w'

# optimize addition of 1-length lists
print [1]+[2,3,4], [1,2,3]+[4]

# known problem (issue 8)
def quicksort(L):
        x = y = 0
        if L == []: return []
        pivot = L[0]
        return quicksort([x for x in L[1:] if x < pivot]) + [pivot] +                 quicksort([y for y in L[1:] if y >= pivot])

data = [1, 200, 50, 485, 22, 22, 3534, 22112]
print "quickdata: %s " % quicksort(data)

# test list.__setslice__ optimization
a = [1, 2, 3]
a[-2:] = (1, 7, 9, 10)
print a
a[-2:] = set((10,))
print a

# map, filter, reduce
def hoppa(x, y, z): return str(x+y+z)
def uhppa(a, b): return a+int(b)
amap = map(hoppa, [1,2,3], [3,4,5], [5,6,7])
print amap
bmap = map(uhppa, [1,2,3], ['3','4','5'])
print bmap
def hoppa2(a, b):
    if b: return a+b
    return a+'X'
print map(hoppa2, 'banaan', 'aap')
def hoppa3(a, b):
    if b: return a+b
    return a
print map(hoppa3, range(8), range(4))
print sorted(map(lambda u: len(u), ['aaaaa', 'aaa', 'a']))

print reduce(lambda a,b: a+b, [3,5,7])
print reduce(lambda a,b: a-b, set([3,5,7]), 1)

print filter(lambda a: 2<=a<5, range(10))
print filter(lambda c: c>'a', 'abaaac')
print filter(lambda c: c>'a', tuple('abaaac'))
print filter(None, range(3)), filter(None, 'abc'), filter(None, tuple(range(3)))

options = filter(lambda option: option != 'fake', ['duh'])
print options

# next
it1 = iter(range(4))
for i in range(10):
    print next(it1, -1)
it2 = iter('abcd')
try:
    for i in range(10):
        print next(it2)
except StopIteration:
    print 'stop'
it3 = iter('aha')
for i in range(10):
    print next(it3, None)

# sort(ed) key argument
a = range(4)
print sorted(a)
print sorted(a, cmp=lambda a,b:cmp(a,b))
print sorted(a, cmp=lambda a,b:cmp(b,a))
print sorted(a, key=lambda a:a)
print sorted(a, key=lambda a:-a)
print sorted(a, cmp=lambda a,b:cmp(a,b), key=lambda a:-a)

l = range(4)
print l
l.sort(cmp=lambda a,b:cmp(a,b))
print l
l.sort(cmp=lambda a,b:cmp(b,a))
print l
l.sort(key=lambda a:a)
print l
l.sort(key=lambda a:-a)
print l
l.sort(cmp=lambda a,b:cmp(a,b), key=lambda a:-a)
print l

print sorted('dcba', key=lambda c: c)

# missing cast
class hop:
    def __init__(self, a):
        print 'oh', a

class hop2(hop):
    def __init__(self):
        bla = None
        hop.__init__(self, bla)

class hop3(hop):
    def __init__(self):
        hop.__init__(self, 'hoi')

hop2()
hop3()

# improve local variable overloading
def bleh(a, b):
    return 1
def snrted(it, bleh):
    bleh(1, 1)
snrted(range(4), lambda a,b: a+b)

# forward var refs
def hoep():
    for x in range(10):
        if x == 8:
            print happa
        elif x == 9:
            print hoepa
        else:
            happa = x
            hoepa, banaan = x, 2
    [n for n in range(4)]

class wa:
    def wh(self):
        if False:
            y = 3
        y = 2
        print y

        if False:
            u.strip()
        u = 'hoi'

        if False:
            z += 1
        z = 2
        print z

hoep()
wa().wh()

# passing builtins around
print sorted([[2,3,4], [5,6], [7]], key=len)
print map(len, ['a','bc'])
print map(max, ['a','bc'], ['d'], ['e'])
print map(max, ['a'], ['d'], ['e'])
print map(str, range(12))
print map(list, 'abc')
print map(int, ['18', '19'])
print map(set, [[1]])
def two(f, a, b):
    return f(a, b)
def three(f, a, b, c):
    return f(a, b, c)
print two(max, 'a', 'b')
print three(max, 'a', 'b', 'c')

# __cmp and None
lamp = ['a', 'b', None]
lamp.sort()
print lamp

# bool and func pointers, misc fixes
def wopper(x):
    print 'wopper', x
wopper('wopper')

DEBUG = wopper
DEBUG = None

if DEBUG:
    DEBUG('wopper')
if not DEBUG:
    print 'no debug'
if not 18:
    DEBUG('wopper')

print 'debug' if () else 'no debug'

print int(bool(DEBUG))
print int(bool(1))

# with statement
with file('testdata/lop', 'w') as fp:
    fp.write('neh')
with file('testdata/lop') as ap:
    print repr(ap.read())
f = file('testdata/lop')
with f:
    print f.read()


