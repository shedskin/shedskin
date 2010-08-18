
# --- string formatting problem
print '%i%%-%i%%' % (1,2)
numbers = (1,2)
print '%i%%-%i%%' % numbers
print '%i%%-%s%%' % (12, '21')
t2 = (12, '21')
print '%i%%-%s%%' % t2

# --- aug assign problem (or: the value of testing)
a = [1,2,3,4,5]
c = a
b = [6,7,8,9,10]

a += b
print a, c

ah = '12345'
ch = ah
bh = '67890'
ah += bh
print ah, ch

# --- __iadd__ etc.
class C:
    def __init__(self, value):
        self.value = value

    def __iadd__(self, other):
        self.value += other.value
        return self

    def __floordiv__(self, b):
        return C(self.value // b.value)

    def __ifloordiv__(self, b):
        self.value //= b.value
        return self

    def __str__(self):
        return str(self.value)

x = C(4)
x += x
x.__iadd__(x)
print x

print [1,2].__iadd__([2,3])

y = [1,2,3]
y += set([4,5])
print y

v = 3
v += 1.5
print v

hm = []
hm += set([1])
print hm

d = C(8)
print d // C(3)
d //= C(3)
print d

# --- inheritance problem
class Maze(object):
    def __init__(self):
        self.maze = [[0]]
        self.maze[0][0] |= 1

class ASCIIMaze(Maze):
    pass

maze = ASCIIMaze()


