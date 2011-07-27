
# casting
class Foo:
   def __init__(self):
       a = None
       self.v = [1]
       self.v = a
       print self.v

       w = self.v
       w = a
       print w

       x = [1,2,3]
       x[1:2] = []
       x[1:2] = [4,5]
       print x

       self.x = [1,2,3]
       self.x[1:2] = []
       print self.x

f1 = Foo()

# print None
a = [None]
print a
b = None
print b

# ugliness
ss = set([frozenset([1,2,3])])
ss.discard(set([1,2,3]))
print ss

# complex
c = complex(7.1, 4.7)
print c, c.real, c.imag
d = complex(7)
print d, d.real, d.imag
e = c+d
print e, e.real, e.imag
f = 1.2+complex()
print f
g = complex()+1.3
print g
d = 7+1.1j
c += d
c += 8.4
c += 2
c += 9j
print c
print (7+4j)*(9+5j), 3*(7+4j)
c,d = 2+2j, -3+4j
print c.conjugate()
print abs(c)
print 7-c, c-7, c-d
print 2/c, c/2, c/d
print +c, ++c, -d, --d
print 1-1j
print int(1j == 1j), int(1j != 1j)
print hash(12+10j)
print int(bool(0j)), int(bool(1+1j))
print divmod((5+5j), (1+2j))
print (5+5j)//(1+2j), (5+5j)%(1+2j)
print divmod((5+5j), 2)
print (5+5j)//2, (5+5j)%2
#print divmod((5+5j), 2.2)
print (5+5j)//2.2, (5+5j)%2.2
print divmod((5.5+5.5j), 2)
print (5.5+5.5j)//2, (5.5+5.5j)%2
#print divmod((5.5+5.5j), 2.8)
print (5.5+5.5j)//2.8, (5.5+5.5j)%2.8

# complex(str)
import re

def parsevalue(s):
    if not s:
        return 0+0j
    mult = 1+0j
    if s[-1] == 'j':
        s = s[:-1]
        mult = 0+1j
    if s in ['+', '-']:
        s += '1'
    return float(s)*mult

def hak(s):
    pat = '(?P<%s>[+-]?([\d\.]+e[+-]?\d+|[\d\.]*)j?)'
    imag = re.compile(pat % 'one' + pat % 'two' + '?$')
    m = imag.match(s.strip())
    if m:
        return parsevalue(m.group('one')) + parsevalue(m.group('two'))
    else:
        raise ValueError('complex() arg is a malformed string')

print hak(' 2.4+0j' ), hak('2.4'), hak(' .4j'), hak('1-j')
print hak('-10-j'), hak('+10.1+2.4j'), hak('+j')
print hak('2e02'), hak('2e-02-2e+01j'), hak('-1.3e-3.1j')

print complex(' 2.4+0j' ), complex('2.4'), complex(' .4j'), complex('1-j')
print complex('-10-j'), complex('+10.1+2.4j'), complex('+j')
#print complex('2e02'), complex('2e-02-2e+01j'), complex('-1.3e-3.1j') XXX 2.7?

class PI:
    def __float__(self):
        return 3.14
print complex(PI())

# %% woes
print "%%(%s)s" % 'ole'
print '%%(bert)s %(bert)s' % {'bert': 18}
ddd = {'bert': 19.9}
print '%%(bert)s %(bert)s' % ddd

# re.group multiple int/str arguments
imag = re.compile('(a)(b)')
m = imag.match('ab')
print m.group(), m.group(0), m.group(1), m.group(2)
print m.group(0, 2), m.group(2, 1, 1, 2)
imag = re.compile('(?P<one>a)(?P<two>b)')
m = imag.match('ab')
print m.group(), m.group('one'), m.group('two')
print m.group('two', 'one')
wap = m.group('one')
print wap
hop = m.group('one', 'two', 'one')
print hop

# join empty list
el = ['hap'][7:8]
print ' '.join(el)

# this works now
#def p(msg):
#    print msg
#p(15)
#p("hello")

# hash(None)
dwek = {('a', 'b', None): 18}
print dwek[('a', 'b', None)]

# merge_simple_types
lrp = []
print [lrp.append(0)]

# inheritance from Exception descendant
class X(RuntimeError):
    def __init__(self, msg=None):
        RuntimeError.__init__(self, msg)
        print 'ole', msg
X()


