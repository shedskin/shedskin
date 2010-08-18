
def appl(predicate, x): return predicate(x)
print [0,1][appl(lambda n: n>5, 10)], [0,1][appl(lambda n: n>10, 8)]

def split(seq, predicate):
    pair = [], []
    for el in seq:
        pair[not predicate(el)].append(el)
    return pair
print split(range(-5,6), lambda n: n%2==0)

#class Obj:
#    def __init__(self, n): self.n = n
#    def __gt__(self, other): return self.n > other.n
#    def __str__(self): return str(self.n)
#def mymax(seq):
#    maxval = seq[0]
#    for el in seq:
#        if el > maxval: # gives error
#            maxval = el
#    return maxval
#l = [Obj(i) for i in xrange(100)]
#print mymax(l), mymax(range(100))

class Num:
    def __init__(self, n): self.n = float(n)
    def __str__(self): return str(self.n)
    def __add__(self, other): return Num(self.n + other.n)
print sum([Num(i) for i in range(5)], Num(0))
print sum(range(5))

for a in 1,2: print a
for a in [1,2]: print a
for a in 1,2,3: print a

print 'aaaa'.replace('a','b', 2)
print 'aaaa'.replace('a','b', -1)

print 'aaaa'.split('a', 2)
print 'aaaa'.split('a', -1)


