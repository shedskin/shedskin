
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
word = 'aachen\n'
key = word.translate(gtable, "a\n")
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
    def __nonzero__(self): return True
    def __len__(self): return 1

d = D()

print [0,1][bool(d)], str(d), int(d), float(d), max([d,d]), min([d,d])
if 5: print 5
if d: print 6


