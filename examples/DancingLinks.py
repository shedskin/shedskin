## implements the Dancing Links algorithm, following Knuth's paper

class MatrixElement:
    def __init__(self):
        self.up = None
        self.down = None
        self.right = None
        self.left = None
        self.column = None

updates = 0
udates = [0] * 324
nodes = 0

filename = None
def setfilename(s):
    global filename
    filename = s

class Column(MatrixElement):
    def __init__(self, name):
        MatrixElement.__init__(self)
        self.size = 0
        self.name = name
        self.down = self
        self.up = self
        self.extra = None

    def cover(self):
        global updates
        updates += 1
        udates[level] += 1

        self.right.left = self.left
        self.left.right = self.right
        i = self.down
        while i != self:
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1
                j = j.right
            i = i.down

    def uncover(self):
        i = self.up
        while i != self:
            j = i.left
            while j != i:
                j.column.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up
        self.right.left = self
        self.left.right = self

    def __str__(self):
        return self.name

def search(k):
    global o, solutions, level, nodes
    level = k
    if root.right == root:
        printsolution(o)
        solutions += 1
        return

    nodes += 1
    j = root.right
    s = j.size
    c = j
    j = j.right
    while j != root:
        if j.size < s:
            c = j
            s = j.size
        j = j.right

    ## Don't use S heuristic
#    c = root.right

    c.cover()
    r = c.down
    while r != c:
        o.append(r)
        j = r.right
        while j != r:
            j.column.cover()
            j = j.right
        search(k+1)
        level = k
        r = o.pop(-1)
        c = r.column
        j = r.left
        while j != r:
            j.column.uncover()
            j = j.left
        r = r.down
    c.uncover()

    if k == 0:
        count = 0
        j = root.right
        while j != root:
            count += 1
            j = j.right
        print 'nodes =', nodes
        print 'solutions =', solutions

def printsolution(o):
    print '### solution!'
    for row in o:
        r = row
        s = r.column.name
        r = r.right
        while r != row:
            s += ' ' + r.column.name
            r = r.right
        print s

def printmatrix(root):
    c = root.right
    while c != root:
        r = c.down
        while r != c:
            printrow(r)
            r = r.down
        c = c.right

def printrow(r):
    s = r.column.name
    next = r.right
    while next != r:
        s += ' ' + next.column.name
        next = next.right
    print s

def setroot(r):
    global root
    root = r

solutions = 0
o = []

def setprintsolution(f):
    global printsolution
    printsolution = f