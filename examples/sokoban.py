# sokoban, from: http://rosettacode.org/wiki/Sokoban

from array import array
from collections import deque
 
def tab_to_str(tab):
    return "".join(arr.tostring() for arr in tab)
 
def copy_tab(tab):
    return [arr.__copy__() for arr in tab]
 
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
 
        open.append((copy_tab(self.ddata), "", self.px, self.py))
        visited.add(tab_to_str(self.ddata))
 
        dirs = ((0, -1, 'u', 'U'), ( 1, 0, 'r', 'R'),
                (0,  1, 'd', 'D'), (-1, 0, 'l', 'L'))
 
        while open:
            cur, csol, x, y = open.popleft()
 
            for i in xrange(4):
                temp = copy_tab(cur)
                dx, dy = dirs[i][0], dirs[i][1]
 
                if temp[y+dy][x+dx] == '*':
                    if self.push(x, y, dx, dy, temp) and \
                       tab_to_str(temp) not in visited:
                        if self.is_solved(temp):
                            return csol + dirs[i][3]
                        open.append((copy_tab(temp),
                                     csol + dirs[i][3], x+dx, y+dy))
                        visited.add(tab_to_str(temp))
                elif self.move(x, y, dx, dy, temp) and \
                     tab_to_str(temp) not in visited:
                    if self.is_solved(temp):
                        return csol + dirs[i][2]
                    open.append((copy_tab(temp),
                                 csol + dirs[i][2], x+dx, y+dy))
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
