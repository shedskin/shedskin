from __future__ import print_function

# check bounds after wrapping..
alist = range(5)
for i in range(-10,10):
    try:
        print(alist[i], i)
    except IndexError:
        print('nope', i)
try:
    print([][-1])
except IndexError:
    print('nope..')

# fix examples/Gh0stenstein
px = 0xff << 24
print (px == 0xff000000)

# unicode basics  # TODO non-ascii so run.py doesn't work
s = u'\u91cf\u5b50\u529b\u5b66'
print(repr(s))  #, s
t = s.encode('utf-8')
print(repr(t))  #, t
u = t.decode('utf-8')
print(repr(u))  #, u
l = [s, u]
print(l)
print(repr(s[1]))  #, s[1]
print(len(s))

# some datetime tests
import datetime
print(datetime.datetime.today().date())
print(datetime.datetime.utcnow().date())

# float(str) inf
bignumstr = '1' + 500 * '0'
print(float(bignumstr))

# optimize: for .. in enumerate(str)
for i, e in enumerate('poehee'):
    print(i, e)

# optimize: name in (expr, expr, ..)
z = 12
print(z in (10,12,14))
print(z not in (7,8,9))
z = 8
print(z in (10,12,14))
print(z not in (7,8,9))

# different output in python3
a = set([1,2])                           # [Set(int)]
a.add(3)                                 # []
print(a)                                  # [Set(int)]
