
v = [1, 2, 3, 4]
v[1:3] = [5, 6, 7]
print v

v = [1, 2, 3, 4]
v[:] = [1, 2, 3, 4, 5]
print v

v = [1, 2, 3, 4]
v[1:3] = [5]
print v

v = [1, 2, 3, 4]
v[:] = []
print v

v = [1, 2, 3, 4]
del v[:]
print v

def bla(x): return x
u = [1,2,3,4]
bla(u)[1:3] = [5, 6, 7]
print u

w = []
w[:] = [1,2]
print w

