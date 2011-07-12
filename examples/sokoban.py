from array import array
from collections import deque

class Direction:
    def __init__(self, dx, dy, letter):
        self.dx, self.dy, self.letter = dx, dy, letter

class Open:
    def __init__(self, cur, csol, x, y):
        self.cur, self.csol, self.x, self.y = cur, csol, x, y

class Board(object):
    def __init__(self, board):
        data = filter(None, board.splitlines())
        self.nrows = max(len(r) for r in data)
        self.sdata = ""
        self.ddata = ""

        maps = {' ':' ', '.': '.', '@':' ', '#':'#', '$':' '}
        mapd = {' ':' ', '.': ' ', '@':'@', '#':' ', '$':'*'}

        for r, row in enumerate(data):
            for c, ch in enumerate(row):
                self.sdata += maps[ch]
                self.ddata += mapd[ch]
                if ch == '@':
                    self.px = c
                    self.py = r

    def move(self, x, y, dx, dy, data):
        if self.sdata[(y+dy) * self.nrows + x+dx] == '#' or \
           data[(y+dy) * self.nrows + x+dx] != ' ':
            return (False, None)

        data2 = array("c", data)
        data2[y * self.nrows + x] = ' '
        data2[(y+dy) * self.nrows + x+dx] = '@'
        return (True, data2.tostring())

    def push(self, x, y, dx, dy, data):
        if self.sdata[(y+2*dy) * self.nrows + x+2*dx] == '#' or \
           data[(y+2*dy) * self.nrows + x+2*dx] != ' ':
            return (False, None)

        data2 = array("c", data)
        data2[y * self.nrows + x] = ' '
        data2[(y+dy) * self.nrows + x+dx] = '@'
        data2[(y+2*dy) * self.nrows + x+2*dx] = '*'
        return (True, data2.tostring())

    def is_solved(self, data):
        for i in xrange(len(data)):
            if (self.sdata[i] == '.') != (data[i] == '*'):
                return False
        return True

    def solve(self):
        open = deque()
        open.append(Open(self.ddata, "", self.px, self.py))

        visited = set()
        visited.add(self.ddata)

        dirs = (
            Direction( 0, -1, 'u'), 
            Direction( 1,  0, 'r'),
            Direction( 0,  1, 'd'), 
            Direction(-1,  0, 'l'),
        )

        while open:
            o = open.popleft()
            cur, csol, x, y = o.cur, o.csol, o.x, o.y

            for i in xrange(4):
                temp = cur
                dir = dirs[i]
                dx, dy = dir.dx, dir.dy

                if temp[(y+dy) * self.nrows + x+dx] == '*':
                    r, temp = self.push(x, y, dx, dy, temp)
                    if r and temp not in visited:
                        if self.is_solved(temp):
                            return csol + dir.letter.upper()
                        open.append(Open(temp, csol + dir.letter.upper(), x+dx, y+dy))
                        visited.add(temp)
                else:
                    r, temp = self.move(x, y, dx, dy, temp)
                    if r and temp not in visited:
                        if self.is_solved(temp):
                            return csol + dir.letter
                        open.append(Open(temp, csol + dir.letter, x+dx, y+dy))
                        visited.add(temp)

        return "No solution"


level = """\
#######
#     #
#     #
#. #  #
#. $$ #
#.$$  #
#.#  @#
#######"""

print level, "\n"
b = Board(level)
print b.solve()
