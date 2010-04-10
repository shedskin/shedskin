
l = lambda x: -x
a = [1 for x in range(10)]
b = (x for x in range(10))

def blah(x):
    yield x
    yield x+1
c = list(blah(4))

print 'subsub:'
print l(3)
#print a
#print list(b)
#print c
