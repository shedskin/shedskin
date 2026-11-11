# looking up a value that is silently converted to the element type

import collections

t = (1, 2, 3)
l = [1, 2, 3]
s = {1, 2, 3}
d = {1: 'a', 2: 'b'}
q = collections.deque(l)
x = 2.5

print(x in t)
print(x not in l)
print(x in s)
print(x in d)
print(x in q)
print(x in (1, 2))
print(t.count(x))
print(l.index(2.0))
print(d.get(x))
print(d[2.0])
print(None in l)
print(l.count(None))

# no warning
print(2 in [1.0, 2.5])
print(2.5 in [1.0, 2.5])
print(None in ['a', None])
print(2 in l, x in [x])

#*WARNING* 101.py:12: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:13: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:14: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:15: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:16: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:17: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:18: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:19: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:20: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:21: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 101.py:22: looking up None among numbers: it is treated as 0
#*WARNING* 101.py:23: looking up None among numbers: it is treated as 0
