import collections

def product(iterables):  # shedskin: avoid itertools.product splat operator
    result = [[]]
    for pool in iterables:
        result = [x+[y] for x in result for y in pool]
    return result

def str_base(number, base):  # base-3 helper
    digits = []
    while number > 0:
        number, digit = divmod(number, base)
        digits.append(str(digit))
    return ''.join(digits)

def str_state(s):
    return str_base(s, 3).ljust(8, '0')

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
state = [0 for line in lines]

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
                    board[j][i] = {'0': '.', '1': 'o', '2': 'x'}[str_state(state[l])[idx]]
    return '\n'.join([''.join(row) for row in board])


def calc_pos(l, j):
    line = lines[l]
    return (line.start[0]+j*line.dx, line.start[1]+j*line.dy)


def place(pos, turn):
    for l, idx in topology[pos]:
        state[l] += {'x': 2, 'o': 1}[turn] * 3**idx


def flip(pos, turn):
    for l, idx in topology[pos]:
        state[l] += {'x': 1, 'o': -1}[turn] * 3**idx


def state_flips(s, idx, turn):
    flips = []
    s2 = str_state(s)

    if s2[idx] == '0':
        for r in (
            range(idx-1, -1, -1), # flip left
            range(idx+1, 8), # flip right
        ):
            flips2 = []
            for j in r:
                if s2[j] == '0':
                    break
                elif s2[j] == turn:
                    flips.extend(flips2)
                    break
                else:
                    flips2.append(j)
    return flips

# for each line state, idx and turn, determine flipped discs
flippers_x = {}
flippers_o = {}
for s in range(3**8):
    for idx in range(8):
        flippers_x[s, idx] = state_flips(s, idx, '2')
        flippers_o[s, idx] = state_flips(s, idx, '1')

#patterns = set([tuple(v) for v in flippers_x.values()])
#print(len(patterns))
#flipfuncs = set()
#for i, l in enumerate(lines):
#    for p in patterns:
#        if p and max(p) < l.length-1:
#            posn = sorted([calc_pos(i, j) for j in p])
#            flipfuncs.add(f'flip_{posn}')
#print(flipfuncs)
#print(len(flipfuncs))

def move(pos, turn):
    legal = False
    for l, idx in topology[pos]:
        if turn == 'x':
            flips = flippers_x.get((state[l], idx), [])
        else:
            flips = flippers_o.get((state[l], idx), [])
        if flips:
            legal = True
            for j in flips:
                flip(calc_pos(l, j), turn)

    assert legal
    if legal:
        place(pos, turn)


def check_board():
    a = get_board(0, 8)
    print(a)
    print()
    b = get_board(8, 16)
#    print(b)
#    print()
    c = get_board(16, 31)
#    print(c)
#    print()
    d = get_board(31, 46)
#    print(d)
#    print()
    assert a == b == c == d
    return a

place((3,3), 'o')
place((3,4), 'x')
place((4,4), 'o')
place((4,3), 'x')
#check_board()

italian = 'F5D6C4D3E6F4E3F3C6F6G5G6E7F7C3G4D2C5H3H4E2F2G3C1C2E1D1B3F1G1F8D7C7G7A3B4B6B1H8B5A6A5A4B7A8G8H7H6H5G2H1H2A1D8E8C8B2A2B8A7'
turn = 'x'
for i in range(60):
    human_move = italian[i*2:(i+1)*2]
    pos = ('ABCDEFGH'.index(human_move[0]), int(human_move[1])-1)
    move(pos, turn)
#    check_board()
    if turn == 'x':
        turn = 'o'
    else:
        turn = 'x'

check_board()

nx = sum(str_base(state[l], 3).count('2') for l in range(8))
no = sum(str_base(state[l], 3).count('1') for l in range(8))
print(f'{nx}-{no}')
