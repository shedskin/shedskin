# sokoban, from: http://rosettacode.org/wiki/Sokoban

from array import array
from collections import deque
 
def tab_to_str(tab):
    return "".join(arr.tostring() for arr in tab)
 
def copy_tab(tab):
    return [arr.__copy__() for arr in tab]
 
class Direction:
    def __init__(self, dx, dy, letter):
        self.dx, self.dy, self.letter = dx, dy, letter

class Open:
    def __init__(self, cur, csol, x, y):
        self.cur, self.csol, self.x, self.y = cur, csol, x, y

class Board(object):
    def __init__(self, board):
        data = filter(None, board.splitlines())
        width = max(len(r) for r in data)
        xld = xrange(len(data))
        self.sdata = [array("c", " ") * width for _ in xld]
        self.ddata = [array("c", " ") * width for _ in xld]
 
        maps = {' ':' ', '.': '.', '@':' ', '#':'#', '$':' '}
        mapd = {' ':' ', '.': ' ', '@':'@', '#':' ', '$':'*'}
 
        for r, row in enumerate(data):
            for c, ch in enumerate(row):
                self.sdata[r][c] = maps[ch]
                self.ddata[r][c] = mapd[ch]
                if ch == '@':
                    self.px = c
                    self.py = r
 
    def move(self, x, y, dx, dy, data):
        if self.sdata[y+dy][x+dx] == '#' or data[y+dy][x+dx] != ' ':
            return False
 
        data[y][x] = ' '
        data[y+dy][x+dx] = '@'
        return True
 
    def push(self, x, y, dx, dy, data):
        if self.sdata[y+2*dy][x+2*dx] == '#' or \
           data[y+2*dy][x+2*dx] != ' ':
            return False
 
        data[y][x] = ' '
        data[y+dy][x+dx] = '@'
        data[y+2*dy][x+2*dx] = '*'
        return True
 
    def is_solved(self, data):
        for v in xrange(len(data)):
            for u in xrange(len(data[v])):
                if (self.sdata[v][u] == '.') != (data[v][u] == '*'):
                    return False
        return True
 
    def solve(self):
        visited = set()
        open = deque()
 
        open.append(Open(copy_tab(self.ddata), "", self.px, self.py))
        visited.add(tab_to_str(self.ddata))
 
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
                temp = copy_tab(cur)
                dir = dirs[i]
                dx, dy = dir.dx, dir.dy
 
                if temp[y+dy][x+dx] == '*':
                    if self.push(x, y, dx, dy, temp) and \
                       tab_to_str(temp) not in visited:
                        if self.is_solved(temp):
                            return csol + dir.letter.upper()
                        open.append(Open(copy_tab(temp), csol + dir.letter.upper(), x+dx, y+dy))
                        visited.add(tab_to_str(temp))
                elif self.move(x, y, dx, dy, temp) and \
                     tab_to_str(temp) not in visited:
                    if self.is_solved(temp):
                        return csol + dir.letter
                    open.append(Open(copy_tab(temp), csol + dir.letter, x+dx, y+dy))
                    visited.add(tab_to_str(temp))
 
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
