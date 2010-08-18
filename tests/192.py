
from __future__ import print_function

# unbound ident
import testdata.subsub
print(list(testdata.subsub.blah(4)))

# exception hierarchy
try:
    try:
        raise SystemExit('hoei')
    except Exception, msg:
        print('foute boel')
except BaseException as ork:
    print('base exc', ork)

# map external func
import math
som=sum(map(math.factorial, [1,2,3]))
print(som)
from testdata.subsub import fact
som=sum(map(fact, [1,2,3]))
print(som)
mf = math.factorial
print(map(mf, range(10)))
import testdata.subsub
som=sum(map(testdata.subsub.fact, [1,2,3]))
print(som)
tsf = testdata.subsub.fact
print(tsf(10))

# set problems
collector = set()
collector.add(frozenset([1,2]))
collector.add(frozenset([1,2,3]))
print(sorted(collector))

low_hits = set([19460, 19877, 20294, 20711, 21128, 21545, 21962, 19599, 20016, 20433, 20850, 21267, 21684, 22101, 19738, 20155, 20572, 20989, 21406, 21823]) 
high_hits = set([22052, 21605, 21158, 20711, 20264, 19817, 19370, 21903, 21456, 21009, 20562, 20115, 19668, 21754, 21307, 20860, 20413, 19966, 19519])
hits = low_hits.symmetric_difference(high_hits)
print(sorted(hits))

# generator methods
class GM:
    def loop(self):
        yield self.loop2(4)
        yield 
    def loop2(self, x):
        return x*'patattie'

g = GM()
for xn in g.loop():
    print(xn)
    
class GenMeth2:
    def __init__(self, y):
        self.y = y
    def loop(self, x):
        z = self.y
        for i in x:
            yield i+z

gm2 = GenMeth2(2)
print(list(gm2.loop([4,1,5])))

# __future__ print_function
class B:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return 'B(%d)' % self.value
        
b = B(14)
print(b, b, b, sep='hoi', end='\n\n')
print(min(1,2,3, key=lambda x:-x))

# problem with inheritance across files
from testdata.subsub import aa

class baa(aa):
  def __init__(self):
    aa.__init__(self)
    print("init b")
    self.hoppa()

baa()

# @x.setter syntax
class bert(object):
    @property
    def patat(self):
        print('get')
        return self._x

    @patat.setter
    def patat(self, y):
        print('set')
        self._x = y

b1 = bert()
b1.patat = 12
print(b1.patat)

# class-level constructors
class aazz:
  class_dict_var={}
  class_dict_var2={}
  class_dict_var3={(1,2): 7}
  kwek = []
  kwad = (1,2)
  wof = 'wof'
  s = set()
  t = s 
  z = t | s
  wa = [2*x for x in range(10)]
  def __init__(self):
    self.y = 10
    aazz.class_dict_var[4] = 5
    aazz.class_dict_var2['4'] = 5
    aazz.kwek.append('1')
    aazz.s.update(aazz.kwad)

print(aazz().y)
print(aazz.class_dict_var)
print(aazz.class_dict_var2)
print(aazz.class_dict_var3)
print(aazz.kwek)
print(aazz.kwad)
print(aazz.wof)
print(aazz.s, aazz.t, aazz.z)
print(aazz.wa)


