'''
This will find solutions to the kanoodle puzzle where the "L" piece,
which looks like a "*" sign is placed with the center at (Lcol, Lrow)

implements the Dancing Links algorithm, following Knuth's paper

copyright David Austin, license GPL2

'''

import sys

updates = 0
udates = [0] * 324
nodes = 0

filename = None
def setfilename(s):
    global filename
    filename = s

class Column:
    def __init__(self, name=None):
        if name is None:
            self.up = None
            self.down = None
            self.right = None
            self.left = None
            self.column = None
        else:
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
        sys.exit() # XXX shedskin
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
        print('nodes =', nodes)
        print('solutions =', solutions)

def printsolution(o):
    print('### solution!')
    for row in o:
        r = row
        s = r.column.name
        r = r.right
        while r != row:
            s += ' ' + r.column.name
            r = r.right
        print(s)

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
    print(s)

def setroot(r):
    global root
    root = r

solutions = 0
o = []

#def setprintsolution(f):
#    global printsolution
#    printsolution = f

Lcol = 5
Lrow = 2

## some basic matrix operations

def matrixmultiply(m, n):
    r = [[0,0], [0,0]]
    for i in range(2):
        for j in range(2):
            sum = 0
            for k in range(2):
                sum += m[i][k]*n[k][j]
            r[i][j] = sum
    return r

def matrixact(m, v):
    u = [0,0]
    for i in range(2):
        sum = 0
        for j in range(2):
            sum += m[i][j]*v[j]
        u[i] = sum
    return u

## linear isometries to apply to kanoodle pieces
identity = [ [1,0], [0,1] ]
r90 = [ [0,-1], [1,0] ]
r180 = [ [-1, 0], [0, -1]]
r270 = [ [0,1], [-1,0] ]
r1 = [ [1,0], [0, -1]]
r2 = matrixmultiply(r1, r90)
r3 = matrixmultiply(r1, r180)
r4 = matrixmultiply(r1, r270)

## sets of isometries

symmetries = [identity, r90, r180, r270, r1, r2, r3, r4]
rotations = [identity, r90, r180, r270]

## classes for each of the pieces

class Omino:
    def getorientations(self):
        orientations = []
        for symmetry in self.cosets:
            orientation = []
            for cell in self.cells:
                orientation.append(matrixact(symmetry, cell))
            orientations.append(orientation)
        self.orientations = orientations

    def move(self, v):
        newcells = []
        for cell in self.cells:
            newcells.append([cell[0] + v[0], cell[1] + v[1]])
        self.cells = newcells

    def translate(self, v):
        r = []
        for orientation in self.orientations:
            s = []
            for cell in orientation:
                s.append([cell[0] + v[0], cell[1] + v[1]])
            r.append(s)
        return r

class A(Omino):
    def __init__(self):
        self.name = 'A'
        self.cells = [[0,0], [1,0], [1,1], [1,2]]
        self.cosets = symmetries
        self.getorientations()

class B(Omino):
    def __init__(self):
        self.name = 'B'
        self.cells = [[0,0], [0,1], [1,0], [1,1], [1,2]]
        self.cosets = symmetries
        self.getorientations()

class C(Omino):
    def __init__(self):
        self.name = 'C'
        self.cells = [[0,0], [1,0], [1,1], [1,2], [1,3]]
        self.cosets = symmetries
        self.getorientations()

class D(Omino):
    def __init__(self):
        self.name = 'D'
        self.cells = [ [0, -1], [-1,0], [0,0], [0,1], [0,2]]
        self.cosets = symmetries
        self.getorientations()

class E(Omino):
    def __init__(self):
        self.name = 'E'
        self.cells = [[0,0], [0,1], [1,1],[1,2], [1,3]]
        self.cosets = symmetries
        self.getorientations()

class F(Omino):
    def __init__(self):
        self.name = 'F'
        self.cells = [[0,0], [1,0],[0,1]]
        self.cosets = rotations
        self.getorientations()

class G(Omino):
    def __init__(self):
        self.name = 'G'
        self.cells = [[0,0],[1,0],[2,0],[2,1],[2,2]]
        self.cosets = rotations
        self.getorientations()

class H(Omino):
    def __init__(self):
        self.name = 'H'
        self.cells = [[0,0],[1,0],[1,1],[2,1],[2,2]]
        self.cosets = rotations
        self.getorientations()

class I(Omino):
    def __init__(self):
        self.name = 'I'
        self.cells = [[0,1], [0,0],[1,0],[2,0],[2,1]]
        self.cosets = rotations
        self.getorientations()

class J(Omino):
    def __init__(self):
        self.name = 'J'
        self.cells = [[0,0], [0,1], [0,2], [0,3]]
        self.cosets = [identity, r90]
        self.getorientations()

class K(Omino):
    def __init__(self):
        self.name = 'K'
        self.cells = [[0,0], [1,0],[1,1],[0,1]]
        self.cosets = [identity]
        self.getorientations()

class L(Omino):
    def __init__(self):
        self.name = 'L'
        self.cells = [[0,0],[-1,0],[1,0],[0,-1],[0,1]]
        self.cosets = [identity]
        self.getorientations()

def set5x11():
    global c1, ominos, rows, columns
    c1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    ominos = [A(), B(), C(), D(), E(), F(), G(), H(), I(), J(), K(), L()]
    rows = 5
    columns = 11

## set up the 5x11 board
set5x11()

## start building the matrix for the exact cover problem

root = Column('root')
root.left = root
root.right = root

last = root

## build the columns

pcolumns = {}
for col2 in c1:
    c = Column(col2)
    last.right = c
    c.left = last
    c.right = root
    root.left = c
    last = c
    pcolumns[col2] = c

last = root
for row in range(rows):
    for col in range(columns):
        c = Column('['+str(col) + ',' + str(row)+'] ')
        c.extra = [col, row]

        last.right.left = c
        c.right = last.right
        last.right = c
        c.left = last
        last = c

## check to see if a pieces fits on the board

def validatecell(c):
    if c[0] < 0 or c[0] > columns: return False
    if c[1] < 0 or c[1] > rows: return False
    return True

def validate(orientation):
    for cell in orientation:
        if validatecell(cell) == False: return False
    return True

## construct the rows of the matrix

rownums = 0
for tile in ominos:
    for col in range(columns):
        if tile.name == 'L' and col != Lcol: continue
        for row in range(rows):
            if tile.name == 'L' and row != Lrow: continue
            orientations = tile.translate([col, row])
            for orientation in orientations:
                if validate(orientation) == False: continue
                rownums += 1
                element = Column()
                element.right = element
                element.left = element

                column = pcolumns[tile.name]
                element.column = column
                element.up = column.up
                element.down = column
                column.up.down = element
                column.up = element
                column.size += 1
                rowelement = element

                column = root.right
                while column.extra != None:
                    entry = column.extra
                    for cell in orientation:
                        if entry[0] == cell[0] and entry[1] == cell[1]:
                            element = Column()
                            rowelement.right.left = element
                            element.right = rowelement.right
                            rowelement.right = element
                            element.left = rowelement

                            element.column = column
                            element.up = column.up
                            element.down = column
                            column.up.down = element
                            column.up = element
                            rowelement = element
                            column.size += 1
                    column = column.right

## apply the Dancing Links algorithm to the matrix

try:
    setroot(root)
    print('begin search')
    search(0)
    print('finished search')
except SystemExit:
    pass
