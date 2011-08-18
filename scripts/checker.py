from heapq import *

class A(object):
    def __init__(self, a, hash):
        self.a = a
        self._hash = hash

    def __lt__(self, o):
        print "%s.__lt__(%s)" % (self.a, o.a)
        return NotImplemented

    def __le__(self, o):
        print "%s.__le__(%s)" % (self.a, o.a)
        return NotImplemented

    def __gt__(self, o):
        print "%s.__gt__(%s)" % (self.a, o.a)
        return NotImplemented

    def __ge__(self, o):
        print "%s.__ge__(%s)" % (self.a, o.a)
        return NotImplemented

#    def __cmp__(self, o):
#        print "%s.__cmp__(%s)" % (self.a, o.a)
#        #return cmp(self._hash, o._hash)
#        return NotImplemented

    def __eq__(self, o):
        print "%s.__eq__(%s)" % (self.a, o.a)
        return NotImplemented

    def __ne__(self, o):
        print "%s.__ne__(%s)" % (self.a, o.a)
        return NotImplemented

    def __hash__(self):
        print "%s.__hash__()" % (self.a)
        return 1
#        return self._hash


a = A("a", 1)
b = A("b", 2)
c = A("c", 3)
d = A("d", 1)

print 'eq'
a == b
print 'ne'
a != b
print 'lt'
a < b
print 'gt'
a > b
print 'le'
a <= b
print 'ge'
a >= b

#heapify([a,b,c,d])
#a != b
#cmp(a,b)
#l = [a,b,c,d]
#sorted(l)
