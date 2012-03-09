# set.__ior__ etc. model
class waf:
    def __init__(self, value):
        self.value = value

    def __iand__(self, b):
        return waf(self.value + b.value)

    def __isub__(self, b):
        return waf(self.value - b.value)

wa = waf(4)
wa &= waf(9)
wa -= waf(2)
print wa.value

set1 = set()
set1 |= set([2,3])
print set1

set2 = set()
set2 &= set([2,3])
print set2

set3 = set()
set3 ^= set([2,3])
print set3

set4 = set()
set4 -= set([2,3])
print set4

# overflow in pow, use long long internally
print pow(290797,2,50515093)

# float.is_integer
print 7.7.is_integer()
print 7.0.is_integer()
a = 3.14
print a.is_integer(), (a+a).is_integer()
print 2*a.is_integer()

# model __eq__ from __contains__
#class Point:
#    def __init__(self, x, y):
#        self.x, self.y = x, y
#    def __eq__(self, other):
#        return (self.x, self.y) == (other.x, other.y)
#    def __str__(self):
#        return 'Point(%s, %s)' % (self.x, self.y)

#def wof():
#    a = b = c = d = Point(7,8)
#    p = Point(7,8)
#    return p if p not in (a, b, c, d) else None

#print wof()

# context of inherited method?
import testdata.CCMView

class GameView(testdata.CCMView.CCMView):
    pass

gv = GameView()
gv.wa()
