# test changes for examples3

# division
a = 9/2
print(a)
b = 9//2
print(b)

# bytes
c = b'blup'
d = c[1]
print(d)
for x in c:
    print(x)

n = 66
bla = b'%c%c' % (n, n+1)
print(bla)

bs = set()
bs.add(b'wop')
print(b'wo'+b'p' in bs)

# bytearray
ba = bytearray(c)
ba[2] = ord('a')
print(ba)

# reduce
from functools import reduce

print(reduce(lambda a,b: a+b, [3,5,7]))
print(reduce(lambda a,b: a-b, set([3,5,7]), 1))

# reversed(range)
print(reversed(range(10,20,2)))

# TODO
# __div__ -> __truediv__, __floordiv__

# TODO support slice objects??
#ar = list(range(10))
#ar.__delitem__(slice(1,4))
#print(ar)

# now iterators: dict_items, dict_keys, dict_values, like reversed, enumerate, itertools.imap?
#print({1:2}.items())

# print(.. end=..)

