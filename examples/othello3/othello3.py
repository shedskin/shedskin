import collections

class Line:
    def __init__(self, start, end, length, dx, dy):
        self.start = start
        self.end = end
        self.length = length
        self.dx = dx
        self.dy = dy

# define all 46 lines
lines = [
    Line((0,0), (7,0), 8, 1, 0), # horizontal
    Line((0,1), (7,1), 8, 1, 0),
    Line((0,2), (7,2), 8, 1, 0),
    Line((0,3), (7,3), 8, 1, 0),
    Line((0,4), (7,4), 8, 1, 0),
    Line((0,5), (7,5), 8, 1, 0),
    Line((0,6), (7,6), 8, 1, 0),
    Line((0,7), (7,7), 8, 1, 0),

    Line((0,0), (0,7), 8, 0, 1), # vertical
    Line((1,0), (1,7), 8, 0, 1),
    Line((2,0), (2,7), 8, 0, 1),
    Line((3,0), (3,7), 8, 0, 1),
    Line((4,0), (4,7), 8, 0, 1),
    Line((5,0), (5,7), 8, 0, 1),
    Line((6,0), (6,7), 8, 0, 1),
    Line((7,0), (7,7), 8, 0, 1),

    Line((0,0), (0,0), 1, 1, -1), # diagonal asc
    Line((0,1), (1,0), 2, 1, -1),
    Line((0,2), (2,0), 3, 1, -1),
    Line((0,3), (3,0), 4, 1, -1),
    Line((0,4), (4,0), 5, 1, -1),
    Line((0,5), (5,0), 6, 1, -1),
    Line((0,6), (6,0), 7, 1, -1),
    Line((0,7), (7,0), 8, 1, -1),
    Line((1,7), (7,1), 7, 1, -1),
    Line((2,7), (7,2), 6, 1, -1),
    Line((3,7), (7,3), 5, 1, -1),
    Line((4,7), (7,4), 4, 1, -1),
    Line((5,7), (7,5), 3, 1, -1),
    Line((6,7), (7,6), 2, 1, -1),
    Line((7,7), (7,7), 1, 1, -1),

    Line((0,7), (0,7), 1, 1, 1), # diagonal desc
    Line((0,6), (1,7), 2, 1, 1),
    Line((0,5), (2,7), 3, 1, 1),
    Line((0,4), (3,7), 4, 1, 1),
    Line((0,3), (4,7), 5, 1, 1),
    Line((0,2), (5,7), 6, 1, 1),
    Line((0,1), (6,7), 7, 1, 1),
    Line((0,0), (7,7), 8, 1, 1),
    Line((1,0), (7,6), 7, 1, 1),
    Line((2,0), (7,5), 6, 1, 1),
    Line((3,0), (7,4), 5, 1, 1),
    Line((4,0), (7,3), 4, 1, 1),
    Line((5,0), (7,2), 3, 1, 1),
    Line((6,0), (7,1), 2, 1, 1),
    Line((7,0), (7,0), 1, 1, 1),
]

# initial state
state = [['.' for _ in range(line.length)] for line in lines]

# topology (for each position, which lines cross the position and at which line index)
topology = collections.defaultdict(list)
for l, line in enumerate(lines):
    pos = line.start
    for idx in range(line.length):
        topology[pos].append((l, idx))
        pos = (pos[0]+line.dx, pos[1]+line.dy)


def get_board(line_from, line_to):
    board = [['.' for i in range(8)] for j in range(8)]
    for i in range(8):
        for j in range(8):
            for (l, idx) in topology[i, j]:
                if line_from <= l < line_to:
                    board[j][i] = state[l][idx]
    return '\n'.join([''.join(row) for row in board])


def calc_pos(l, j):
    line = lines[l]
    return (line.start[0]+j*line.dx, line.start[1]+j*line.dy)


def place(pos, turn):
    for line, idx in topology[pos]:
        state[line][idx] = turn


def state_flips(s, idx, turn):
    flips = []

    if s[idx] == '.':
        for r in (
            range(idx-1, -1, -1), # flip left
            range(idx+1, len(s)), # flip right
        ):
            flips2 = []
            for j in r:
                if s[j] == '.':
                    continue
                elif s[j] == turn:
                    flips.extend(flips2)
                else:
                    flips2.append(j)

    return flips

# for each line state, idx and turn, determine flipped discs

def product(iterables): # shedskin: avoid itertools.product splat operator
    result = [[]]
    for pool in iterables:
        result = [x+[y] for x in result for y in pool]
    return result

flippers_x = {}
flippers_o = {}
for state_len in range(1,9):
    for s in product(state_len*['.ox']):
        s2 = ''.join(s)
        for idx in range(state_len):
            flippers_x[s2, idx] = state_flips(s2, idx, 'x')
            flippers_o[s2, idx] = state_flips(s2, idx, 'o')


def move(pos, turn):
    legal = False
    for l, idx in topology[pos]:
        if turn == 'x':
            flips = flippers_x.get((''.join(state[l]), idx), [])
        else:
            flips = flippers_o.get((''.join(state[l]), idx), [])

        if flips:
            legal = True
            for j in flips:
                place(calc_pos(l, j), turn)
    if legal:
        place(pos, turn)


def check_board():
    a = get_board(0, 8)
    print(a)
    print()
    b = get_board(8, 16)
    c = get_board(16, 31)
    d = get_board(35, 46)
    assert a == b == c == d
    return a


place((3,3), 'o')
place((3,4), 'x')
place((4,4), 'o')
place((4,3), 'x')

check_board()
move((5, 4), 'x')
check_board()
move((3, 5), 'o')
check_board()
