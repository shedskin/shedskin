from collections import defaultdict
from itertools import product

NEIGHBOURS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ROWS, COLUMNS = 4, 4
POSITIONS = range(ROWS*COLUMNS)

def to_pos(x, y):
    return (ROWS*y)+x

POS_NEIGHS = []
for pos in POSITIONS:
    x, y = pos % ROWS, pos / ROWS
    neighs = []
    for dx, dy in NEIGHBOURS:
        nx, ny = x+dx, y+dy
        if 0 <= nx < ROWS and 0 <= ny < COLUMNS:
            neighs.append(to_pos(nx, ny))
    POS_NEIGHS.append(neighs)

class Board:
    def __init__(self, board=None):
        if board is None:
            self.state = [0 for pos in POSITIONS]
        else:
            self.state = board.state[:]

    def near(self, row, column):
        near = 0
        for pos in POS_NEIGHS[to_pos(row,column)]:
            near += self.state[pos]
        return near

    def next(self):
        new = Board(self)
        for x in range(ROWS):
            for y in range(COLUMNS):
                p = to_pos(x, y)
                item = self.state[p]
                near = self.near(x, y)
                if near != 2 and near != 3 and item:
                    new.state[p] = 0
                elif near == 3 and not item:
                    new.state[p] = 1
        return new

    def __hash__(self):
        return hash(tuple(self.state))

    def __eq__(self, other):
        return self.state == other.state

    def __repr__(self):
        return '\n'.join([''.join([str(self.state[to_pos(x, y)]) for y in range(COLUMNS)]) for x in range(ROWS)])

def process(board):
    first = board
    history = set()
    while 1:
        history.add(board)
        board = board.next()
        if board in history:
            if board == first:
                return board
            return None

def generator():
    for possibility in product((0, 1), repeat=len(POSITIONS)):
        board = Board()
        for pos, value in zip(POSITIONS, possibility):
            board.state[pos] = value
        yield board

def bruteforce():
    global count
    count = 0
    for board in map(process, generator()):
        if board is not None:
            count += 1 #print board, '\n'

if __name__ == "__main__":
    bruteforce()
    print count
