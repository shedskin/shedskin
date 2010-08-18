
bla = {}
meuk = (12, 13)
z = (5,(3,4))

bla[1], (c, d) = z
print bla

class X: pass
x = X()

for x.z in [1,2,3]: print x.z
x.y, (c, d) = z

print x.y, x.z

s = ['a', 'b', 'c']
s = 'abc'
for y in s: print y
print
print s, str(s), repr(s)

t2 = 1, 'een'
print '%d %s' % t2

f = dict([(1,'1'), (2, '2')])
print f


