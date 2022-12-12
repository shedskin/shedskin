
# re search empty string, match_object.span
import re
r = re.compile('^a?$')
print(r.search('').start())
print(r.search('').end())
print(r.search('').span())
print(r.search('a').start())
print(r.search('a').end())
print(r.search('a').span())

# id
foo_a="foo";foo_b="foo";foo_c="foo";
print(id(foo_a)==id(foo_b)==id(foo_c))

# reduce fixes, more tests
#from math import fabs
#print(reduce(lambda x,y: x + fabs(y), range(10)))
#print(reduce(lambda x,y: x + fabs(y), range(10), 1))
#print(reduce(lambda x,y: x + fabs(y), range(10), 1.0))
#print(reduce(lambda x,y: x + fabs(y), map(float, range(10))))
#print(reduce(lambda x,y: x + fabs(y), map(float, range(10)), 2))
#print(reduce(lambda x,y: x + fabs(y), map(float, range(10)), 2.0))
class Aap:
    def __init__(self, value):
        self.value = value
    def __add__(self, other):
        return Aap(self.value+other.value)
    def __str__(self):
        return 'Aap(%s)' % self.value
    def __repr__(self):
        return str(self)
aaplist = [Aap(3), Aap(4), Aap(5)]
print(sum(aaplist, Aap(6)))
#print(reduce(lambda a,b:a+b, aaplist), reduce(lambda a,b:a+b, aaplist, Aap(6)))

# set methods now often take multiple args
sett = set(range(3))
sett.update(list(range(2,5)), list(range(12,14)))
print(sorted(sett))
sett.update(list(range(2,5)), list(range(12,14)), list(range(18, 20)))
print(sorted(sett))

sett = set(range(4))
print(sorted(sett.union(set(range(6)), (6,7))))
print(sorted(sett.union([5], [3, 4], list(range(3)))))
print(sorted(sett.intersection(list(range(1, 4)), list(range(2, 5)))))
print(sorted(sett.intersection(list(range(3)), [2], list(range(4)))))
print(sorted(sett.difference(list(range(2)), list(range(3)))))
print(sorted(sett.difference(list(range(2)), list(range(3)), [3, 6])))

sett = set(range(4))
sett.intersection_update(list(range(2)), list(range(3)))
print(sorted(sett))
sett = set(range(3))
sett.intersection_update(list(range(2)), list(range(3)), list(range(4)))
print(sorted(sett))

sett = set(range(4))
sett.difference_update(list(range(2)), list(range(3)))
print(sorted(sett))
sett = set(range(5))
sett.difference_update(list(range(2)), list(range(3)), [3, 6])
print(sorted(sett))

#cannot hurt to test this
print([].__class__.__name__)
print('hoi'.__class__.__name__)

#string formatting asterisk
print("%d * %d" % (1,2))
print("%d* %% %d" % (1,2))
print("%d%% *%d" % (1,2))

#rich comparison fallbacks
class inst(object):
    def __init__(self, num, opcode='add', pc='1'):
        self.opcode = opcode
        self.pc = pc
        self.num = num
    
    def __lt__( self, other):
        return self.num < other.num

    def __repr__(self): 
        return "%d" % self.num
        
Seq = [inst(3),inst(1),inst(4),inst(2)]
print(Seq)
print(sorted(Seq))

class LT:
    def __gt__(self, o):
        print('gt!')
        return False
    def __le__(self, o):
        print('le!')
        return True
print(LT() < LT())
print(LT() >= LT())

class LT2:
    def __lt__(self, o):
        print('lt!')
        return False
    def __ge__(self, o):
        print('ge!')
        return True
print(LT2() > LT2())
print(LT2() <= LT2())

#complex
a = 4j + 3j
print(a)
b = a.real
print(sum([1j, 2j, 3j]))
print('%s' % (1+3j))
print(1==0j, 0.0==0j, 1.0==0j, 0j==0.0)

#colorsys
import colorsys

print('%.2f' % colorsys.ONE_THIRD)
print('%.2f' % colorsys.ONE_SIXTH)
print('%.2f' % colorsys.TWO_THIRD)

def pr(t):
    print([('%.2f'%x) for x in t])

pr(colorsys.hls_to_rgb(1.0, 0.5, 0.7))
pr(colorsys.rgb_to_hls(1.0, 0.5, 0.7))
#pr(colorsys.yiq_to_rgb(1.0, 0.5, 0.7))
pr(colorsys.rgb_to_yiq(1.0, 0.5, 0.7))
pr(colorsys.hsv_to_rgb(1.0, 0.5, 0.7))
pr(colorsys.rgb_to_hsv(1.0, 0.5, 0.7))

#equality
t1 = ('rc', (0, 0)) 
t2 =('rc', (0, 0) )
print(t1!=t2)
print(t1==t2)
print({(3,2): 0} == {(3,2): 1})

#fill in virtual variable types
class CCache:
    def Probe(self):
        self.VictimLineAddr = [1]
        self.VictimLineAddr = None

class CCache1(CCache):
    pass

class CCache2(CCache):
    pass

c = CCache1()
c = CCache2()
c.Probe()

# forward referencing vars in inherited method
class TraceParser:
    def parseProgramCode(self):
        self.basicBlockList = []
#        basicblock = 1
        for x in range(2):
            if x == 1:
                self.basicBlockList.append(basicblock)
            else:
                basicblock = 2
        print(self.basicBlockList)

class CUnifiedTraceParser(TraceParser):
    pass

CUnifiedTraceParser().parseProgramCode()

# rewrite incompatible types if possible
C1 = {1: 'een'}
C2 = (1.0, 'woef')
D = (C1, C2) if True else ({}, None)
print(D)
print([1] if True else None)
print([] if True else [1])
print([[]] == [[1]], [[1]] == [[]])
print(dict([(1,2.0)]) == dict())
print(dict([(1,2.0)]) == {})
print(set() == set([1,2]))
print((set(['a']), set([1.0])) == (set(), set()))
print((set(['a']), set([1.0])) == (set(), None))
def slicing():
    a = list(range(10))
    a[2:] = list(range(4))
    a[2:] = []
    print(a)
    b = list(map(str, a))
    b[2:] = []
    b[2:] = ['woef']
    b[2:] = [None]
    print(b)
slicing()
print([1] or [])
print([] or ['uhm'])
print(None or 'waf')
print([1]+[])
print([[]]+[[1]])
print([None]+[['uh']])
print(set([]) == set([1]))
print(set([1]) == set([1.0]))
print(1==0j)
print([1j]==[1.0])
print(0 == True, 1 == True, 2 == True)
print(0 == False, 1 == False, 2 == False)
print([x == True for x in range(3)])
print([1] == [True])

# for .., .. in somedict.iteritems()
def fastdictiteritems():
    d = {3: 4}
    for a,b in d.items():
        print(a, b)
    for c in d.items():
        print(c)

    print([(a, b) for a,b in d.items()])
    print([c for c in d.items()])

    d2 = {(3,4): (4,5)}
    for (e,f), (g,h) in d2.items():
        print(e,f,g,h)

    d3 = {1.0: 'hallo'}
    print([(x, y) for x,y in d3.items()])
fastdictiteritems()

# deepcopy improvement
import copy
class A:
    pass
class B:
    pass
def copytest():
    a = A()
    a.b = B()
    c = copy.deepcopy(a)
    a.b.x = 18
    c.b.x = 19
    print(a.b.x, c.b.x)
copytest()

# return 'nothing' in generator
def hoppagen():
    yield True
    yield False
    print('hoppa')
    return
for hoppax in hoppagen():
    print(hoppax)

# sys.exit case
import sys
sys.exit('woef')
