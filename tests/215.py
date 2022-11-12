# test changes for examples3

# division
a = 9/2
print(a)
b = 9//2
print(b)

# bytes/bytearray
c = b'blup'
d = c[1]
print(d)
for x in c:
    print(x)

n = 66
bla = b'%c%c' % (n, n+1)
print(bla)

# reduce
from functools import reduce

print(reduce(lambda a,b: a+b, [3,5,7]))
print(reduce(lambda a,b: a-b, set([3,5,7]), 1))

