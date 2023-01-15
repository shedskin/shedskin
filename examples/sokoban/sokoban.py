from collections import deque

class Direction:
    def __init__(self, dx, dy, letter):
        self.dx, self.dy, self.letter = dx, dy, letter

class Open:
    def __init__(self, cur, csol, x, y):
        self.cur, self.csol, self.x, self.y = cur, csol, x, y

class Board(object):
    def __init__(self, board):
        data = list(filter(None, board.splitlines()))
        self.nrows = max(len(r) for r in data)
        self.sdata = b''
        self.ddata = b''

        maps = {' ':b' ', '.': b'.', '@':b' ', '#':b'#', '$':b' '}
        mapd = {' ':b' ', '.': b' ', '@':b'@', '#':b' ', '$':b'*'}

        for r, row in enumerate(data):
            for c, ch in enumerate(row):
                self.sdata += maps[ch]
                self.ddata += mapd[ch]
                if ch == '@':
                    self.px = c
                    self.py = r

    def move(self, x, y, dx, dy, data):
        if self.sdata[(y+dy) * self.nrows + x+dx] == ord('#') or \
           data[(y+dy) * self.nrows + x+dx] != ord(' '):
            return None

        data2 = bytearray(data)
        data2[y * self.nrows + x] = ord(' ')
        data2[(y+dy) * self.nrows + x+dx] = ord('@')
        return bytes(data2)

    def push(self, x, y, dx, dy, data):
        if self.sdata[(y+2*dy) * self.nrows + x+2*dx] == ord('#') or \
           data[(y+2*dy) * self.nrows + x+2*dx] != ord(' '):
            return None

        data2 = bytearray(data)
        data2[y * self.nrows + x] = ord(' ')
        data2[(y+dy) * self.nrows + x+dx] = ord('@')
        data2[(y+2*dy) * self.nrows + x+2*dx] = ord('*')
        return bytes(data2)

    def is_solved(self, data):
        for i in range(len(data)):
            if (self.sdata[i] == ord('.')) != (data[i] == ord('*')):
                return False
        return True

    def solve(self):
        todo = deque()
        todo.append(Open(self.ddata, "", self.px, self.py))

        visited = set()
        visited.add(self.ddata)

        dirs = (
            Direction( 0, -1, 'u'),
            Direction( 1,  0, 'r'),
            Direction( 0,  1, 'd'),
            Direction(-1,  0, 'l'),
        )

        while todo:
            o = todo.popleft()
            cur, csol, x, y = o.cur, o.csol, o.x, o.y

            for i in range(4):
                temp = cur
                dir = dirs[i]
                dx, dy = dir.dx, dir.dy

                if temp[(y+dy) * self.nrows + x+dx] == ord('*'):
                    temp = self.push(x, y, dx, dy, temp)
                    if temp and temp not in visited:
                        if self.is_solved(temp):
                            return csol + dir.letter.upper()
                        todo.append(Open(temp, csol + dir.letter.upper(), x+dx, y+dy))
                        visited.add(temp)
                else:
                    temp = self.move(x, y, dx, dy, temp)
                    if temp and temp not in visited:
                        if self.is_solved(temp):
                            return csol + dir.letter
                        todo.append(Open(temp, csol + dir.letter, x+dx, y+dy))
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

print(level)
print()
b = Board(level)
print(b.solve())
