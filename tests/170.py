
# --- model list.__str__ call to elem.__repr__
class Vertex(object):
    def __repr__(self):
        return 'rrrepr'
print [Vertex()]

# --- always true/false, but should work
print [0,1][isinstance(7.0, float)]
print [0,1][isinstance(7, int)]

# --- initialize class attrs in .cpp file
class blah:
    blah = 'blah'
    blah2 = ('blah', 'blah')
    blah3 = abs(-1)
print blah.blah, blah.blah2, blah.blah3

# --- inf
a,b = -1e500, 1e500; print a,b

# --- argh
print sorted('hopla')

# --- dict<void *, void*> *
d = {}
print d

# --- cl attr problem
class FilebasedMazeGame:
    hop = 18
    def __init__(self):
        a = FilebasedMazeGame.hop
        print a

FilebasedMazeGame()

# --- define cl before use
def print_aap():
    aap = Aap()
    print aap

class Aap:
    def __repr__(self):
        return 'hrngh!'

print_aap()

# --- virtual case
class hop:
    def hop(self):
        self.hop2()

class hop2(hop):
    def hop2(self):
        print 'hop2'

hop2().hop()

# --- str.split
s = " foo zbr bar "

print "default separator:"
print s.split(None)
print s.split(None, 0)
print s.split(None, 1)

print "space separator:"
print s.split(' ')
print s.split(' ', 0)

# --- comparison
class g: pass
e, f = g(), g()
print (e < f) + (e > f), [0,1][e == f]


