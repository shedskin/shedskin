
# locally override module name
import testdata.bert as game

class Game:
    def __init__(self):
        self.x = 'xxx'

def hup(game):
    game.__init__()
    print game.x
    if game:
        print 'game'

hup(Game())

# class attribute access across module
from testdata import bert

bert.zeug.purple += 1
blah = bert.zeug.purple
print blah

# template conflict
def opterr(x):
    pass

opterr(1)
#opterr('1')

# disappearing type
def ParseAction(action):
    return ('',)

def ParseRuleLine(line):
    tmp=line.split()
    for y in tmp[-1].split():
        ParseAction(y)

for x in ''.split():
    ParseRuleLine(x)

# working outside of list
a = range(5)
a[7:80] = range(5)
print a
a[10:15] = range(10)
print a
a[12:20] = range(10)
print a
a=range(5)
a[-8:-5] = [9,9]
a[1:1] = [8,8]
del a[-7:2]
print a
a=range(5)
a[4:1] = [7,12]
print a

lll = [1,2]
del lll[18:]
print lll

# split nothing
print ''.split()
print '  '.split()

# casting problem
def hoppa():
    return ['beh']
    return []
    return None

hop = hoppa()

# comment problem
def hoezee():
    '''kijk een /* C++ comment */'''
hoezee()

# list comp scoping
def knuts(j, var):
    print 'knuts!', j, var
    return [7]

itjes = [1]
globaltje = 'global'

def ahoi():
    localtje = 'localtje'
    twitjes = [2]
    print [1 for i in 3*twitjes for b2 in knuts(i, globaltje)]
    print [2 for i in 4*itjes if knuts(2*i, localtje)]

ahoi()

# overloading problem
file = open('unit.py')
print file.read(10)
file.close()

# xrange reset
xrr = xrange(2)
print xrr, list(xrr), list(reversed(xrr))
for xr in xrr:
    for yr in xrr:
        print xr, yr

# tutorial example should work at least..
#class matrix:
#    def __init__(self, hop):
#        self.unit = hop
#
#m1 = matrix([1])
#m2 = matrix([1.0])


