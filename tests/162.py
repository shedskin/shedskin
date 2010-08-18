
class City(object):
    def __init__(self):
        self.latitude = 1

class SortedTree(object):
    def __init__(self, compareKey):
        self.compareKey = compareKey

class Map(object):
    def __init__(self):
        st = SortedTree(lambda x: x.latitude)
        st.compareKey(c)

c = City()
m = Map()

print "1, 3, 5".replace(",", "")
print "1, 3, 5".replace(",", "", -1)
print "1, 3, 5".replace(",", "", 0)
print "1, 3, 5".replace(",", "", 1)

a = []
a = [[]]
a = [[1]]

b = []
b = [1]

d = ()
d = (5,)

print a, b, d

def bla(t):
    print t

bla(())
bla((1,))

def oink():
    return [[1]]
    return [[]]

oink()

def test(t=()):
  if t:
      print t
  else:
      test(t + (5,))

test()

e = {}
e[2,3] = 4

f = {}
f[5] = 6

print e, f

import os
x = os.listdir('.')


