from __future__ import print_function

# !$!#$
try:
    [1].pop(-2)
except IndexError as e:
    print(e)
try:
    [].pop(0)
except IndexError as e:
    print(e)
try:
    [].remove(0)
except ValueError as e:
    print(e)
l = []
l.insert(4, 1)
l.insert(-1, 2)
l.insert(-10, 3)
print(l)

# basic __call__ overloading
class meuk:
    def __call__(self, x, y):
        print('called with:', x, y)
        return 'return'
m = meuk()
x = m(7,1)
print(x)
class mycall:
    def __call__(self, x):
        return -x
print(max(list(range(17,80)), key=mycall()))

# basic __iter__ overloading
class itermeuk:
    def __iter__(self):
        return iter('itermeuk')

i = itermeuk()
for x in i:
    print(x)

# __contains__ fallback to __iter__
import string
print([x for x in string.ascii_lowercase if x in i])

# dict.__init__ takes iterable iterable
da = iter([1,2])
db = iter([3,4])
dd = dict([da,db])
print(sorted(dd))

# writelines takes iterable
a = open('testdata/blah','w')
a.writelines(set(['hoi\n', 'mama\n']))
a.close()
