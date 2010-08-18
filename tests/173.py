
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



