import collections
import time

BLACK, WHITE = 1, -1

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

# initial state (base-3 numbers, 0..3**8-1. digit is 0, 1, 2 -> white, empty, black)
def init_state():
    global state_0, state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8, state_9, state_10, state_11, state_12, state_13, state_14, state_15, state_16, state_17, state_18, state_19, state_20, state_21, state_22, state_23, state_24, state_25, state_26, state_27, state_28, state_29, state_30, state_31, state_32, state_33, state_34, state_35, state_36, state_37, state_38, state_39, state_40, state_41, state_42, state_43, state_44, state_45
    state_0 = 3280
    state_1 = 3280
    state_2 = 3280
    state_3 = 3280
    state_4 = 3280
    state_5 = 3280
    state_6 = 3280
    state_7 = 3280
    state_8 = 3280
    state_9 = 3280
    state_10 = 3280
    state_11 = 3280
    state_12 = 3280
    state_13 = 3280
    state_14 = 3280
    state_15 = 3280
    state_16 = 3280
    state_17 = 3280
    state_18 = 3280
    state_19 = 3280
    state_20 = 3280
    state_21 = 3280
    state_22 = 3280
    state_23 = 3280
    state_24 = 3280
    state_25 = 3280
    state_26 = 3280
    state_27 = 3280
    state_28 = 3280
    state_29 = 3280
    state_30 = 3280
    state_31 = 3280
    state_32 = 3280
    state_33 = 3280
    state_34 = 3280
    state_35 = 3280
    state_36 = 3280
    state_37 = 3280
    state_38 = 3280
    state_39 = 3280
    state_40 = 3280
    state_41 = 3280
    state_42 = 3280
    state_43 = 3280
    state_44 = 3280
    state_45 = 3280

def str_state(number):
    digits = []
    while number > 0:
        number, digit = divmod(number, 3)
        digits.append(str(digit))
    return ''.join(digits).ljust(8, '0')

def states():
    return [
        state_0, state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8, state_9, state_10, state_11, state_12, state_13, state_14, state_15, state_16, state_17, state_18, state_19, state_20, state_21, state_22, state_23, state_24, state_25, state_26, state_27, state_28, state_29, state_30, state_31, state_32, state_33, state_34, state_35, state_36, state_37, state_38, state_39, state_40, state_41, state_42, state_43, state_44, state_45
    ]

# topology (for each position, which lines cross the position and at which line index)
topology = collections.defaultdict(list)
for l, line in enumerate(lines):
    pos = line.start
    for idx in range(line.length):
        topology[pos].append((l, idx))
        pos = (pos[0]+line.dx, pos[1]+line.dy)


# textual board representation
def get_board(line_from, line_to):
    board = [['.' for i in range(8)] for j in range(8)]
    for i in range(8):
        for j in range(8):
            for (l, idx) in topology[i, j]:
                if line_from <= l < line_to:
                    board[j][i] = {'1': '.', '0': 'o', '2': 'x'}[str_state(states()[l])[idx]]
    return '\n'.join([''.join(row) for row in board])


def calc_pos(l, j):
    line = lines[l]
    return (line.start[0]+j*line.dx, line.start[1]+j*line.dy)


# for each line state, idx and turn, determine flipped discs
def state_flips(s, idx, turn):
    flips = []
    s2 = str_state(s)

    if s2[idx] == '1':
        for r in (
            range(idx-1, -1, -1), # flip left
            range(idx+1, 8), # flip right
        ):
            flips2 = []
            for j in r:
                if s2[j] == '1':
                    break
                elif s2[j] == turn:
                    flips.extend(flips2)
                    break
                else:
                    flips2.append(j)
    return tuple(flips)

# lookup table: state, idx -> pattern nr
flippers_x = {}
flips_nr = {}
nr_flips = {}
for s in range(3**8):
    for idx in range(8):
        flips = state_flips(s, idx, '2')
        if flips not in flips_nr:
            nr = len(flips_nr)
            flips_nr[flips] = nr
            nr_flips[nr] = flips
        flippers_x[s << 10 | idx << 2 | BLACK+1] = flips_nr[flips]

        flips = state_flips(s, idx, '0')
        if flips not in flips_nr:
            nr = len(flips_nr)
            flips_nr[flips] = nr
            nr_flips[nr] = flips
        flippers_x[s << 10 | idx << 2 | WHITE+1] = flips_nr[flips]

#print(flips_nr)
#print(nr_flips)

# check that all line states match
def check_board():
    a = get_board(0, 8)
    print(a)
    print()
    b = get_board(8, 16)
    c = get_board(16, 31)
    d = get_board(31, 46)
    assert a == b == c == d
    return a


# generate function tables
def gen_funcs():
    # 64 empty square moves (4 unused)
    move_funcs = []
    for j in range(8):
        for i in range(8):
            human_move = 'abcdefgh'[i] + str(j+1)
            func_name = f'put_{human_move}'
            move_funcs.append(func_name)
            print(f'class {func_name}(Put):')
            print('    def go(self):')
            for (l, idx) in topology[i, j]:
                print(f"        global state_{l}")
            for (l, idx) in topology[i, j]:
                print(f'        flipnr = flippers_x[state_{l} << 10 | {idx << 2} | turn+1]')
                print(f'        line_flip_func[{l} << 6 | flipnr].go()')
            for (l, idx) in topology[i, j]:
                print(f"        state_{l} += turn * {3**idx}")
            print()

    print('move_table = [')
    for name in move_funcs:
        print(f'   {name}(),')
    print(']')
    print()

    # 830 flip patterns (831 including noop)
    patterns = list(flips_nr)
    flipfuncs = set()
    for i, line in enumerate(lines):
        for p in patterns:
            if p and max(p) < line.length-1:
                posn = sorted([calc_pos(i, j) for j in p])
                flipfuncs.add(tuple(posn))

    for flipfunc in flipfuncs:
        human_moves = '_'.join(['abcdefgh'[i] + str(j+1) for (i, j) in flipfunc])
        print(f'class flip_{human_moves}(Flip):')
        print('    def go(self):')
        line_idcs = collections.defaultdict(list)
        for pos in flipfunc:
            for (l, idx) in topology[pos]:
                line_idcs[l].append(idx)
        for l in line_idcs:
            print(f"        global state_{l}")
        for (l, idcs) in line_idcs.items():
            value = sum(3**idx for idx in idcs)
            print(f"        state_{l} += turn * {2 * value}")
        print()

    print('line_flip_func = {}')
    for l in range(46):
        for nr, flips in nr_flips.items():
            posn = sorted([calc_pos(l, idx) for idx in flips if idx < lines[l].length-1])
            human_moves = '_'.join(['abcdefgh'[i] + str(j+1) for (i, j) in posn])
            print(f'line_flip_func[{l << 6 | nr}] = flip_{human_moves}()')

class Put:
    pass

class Flip:
    pass

class flip_(Flip):
    def go(self):
        pass

class put_a1(Put):
    def go(self):
        global state_0
        global state_8
        global state_16
        global state_38
        flipnr = flippers_x[state_0 << 10 | 0 | turn+1]
        line_flip_func[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 10 | 0 | turn+1]
        line_flip_func[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_16 << 10 | 0 | turn+1]
        line_flip_func[16 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 10 | 0 | turn+1]
        line_flip_func[38 << 6 | flipnr].go()
        state_0 += turn * 1
        state_8 += turn * 1
        state_16 += turn * 1
        state_38 += turn * 1

class put_b1(Put):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        flipnr = flippers_x[state_0 << 10 | 4 | turn+1]
        line_flip_func[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 10 | 0 | turn+1]
        line_flip_func[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_17 << 10 | 4 | turn+1]
        line_flip_func[17 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 10 | 0 | turn+1]
        line_flip_func[39 << 6 | flipnr].go()
        state_0 += turn * 3
        state_9 += turn * 1
        state_17 += turn * 3
        state_39 += turn * 1

class put_c1(Put):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        flipnr = flippers_x[state_0 << 10 | 8 | turn+1]
        line_flip_func[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 10 | 0 | turn+1]
        line_flip_func[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_18 << 10 | 8 | turn+1]
        line_flip_func[18 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 10 | 0 | turn+1]
        line_flip_func[40 << 6 | flipnr].go()
        state_0 += turn * 9
        state_10 += turn * 1
        state_18 += turn * 9
        state_40 += turn * 1

class put_d1(Put):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        flipnr = flippers_x[state_0 << 10 | 12 | turn+1]
        line_flip_func[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 10 | 0 | turn+1]
        line_flip_func[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_19 << 10 | 12 | turn+1]
        line_flip_func[19 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 10 | 0 | turn+1]
        line_flip_func[41 << 6 | flipnr].go()
        state_0 += turn * 27
        state_11 += turn * 1
        state_19 += turn * 27
        state_41 += turn * 1

class put_e1(Put):
    def go(self):
        global state_0
        global state_12
        global state_20
        global state_42
        flipnr = flippers_x[state_0 << 10 | 16 | turn+1]
        line_flip_func[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 10 | 0 | turn+1]
        line_flip_func[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 10 | 16 | turn+1]
        line_flip_func[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_42 << 10 | 0 | turn+1]
        line_flip_func[42 << 6 | flipnr].go()
        state_0 += turn * 81
        state_12 += turn * 1
        state_20 += turn * 81
        state_42 += turn * 1

class put_f1(Put):
    def go(self):
        global state_0
        global state_13
        global state_21
        global state_43
        flipnr = flippers_x[state_0 << 10 | 20 | turn+1]
        line_flip_func[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 10 | 0 | turn+1]
        line_flip_func[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 10 | 20 | turn+1]
        line_flip_func[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_43 << 10 | 0 | turn+1]
        line_flip_func[43 << 6 | flipnr].go()
        state_0 += turn * 243
        state_13 += turn * 1
        state_21 += turn * 243
        state_43 += turn * 1

class put_g1(Put):
    def go(self):
        global state_0
        global state_14
        global state_22
        global state_44
        flipnr = flippers_x[state_0 << 10 | 24 | turn+1]
        line_flip_func[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 10 | 0 | turn+1]
        line_flip_func[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 10 | 24 | turn+1]
        line_flip_func[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_44 << 10 | 0 | turn+1]
        line_flip_func[44 << 6 | flipnr].go()
        state_0 += turn * 729
        state_14 += turn * 1
        state_22 += turn * 729
        state_44 += turn * 1

class put_h1(Put):
    def go(self):
        global state_0
        global state_15
        global state_23
        global state_45
        flipnr = flippers_x[state_0 << 10 | 28 | turn+1]
        line_flip_func[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 10 | 0 | turn+1]
        line_flip_func[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 10 | 28 | turn+1]
        line_flip_func[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_45 << 10 | 0 | turn+1]
        line_flip_func[45 << 6 | flipnr].go()
        state_0 += turn * 2187
        state_15 += turn * 1
        state_23 += turn * 2187
        state_45 += turn * 1

class put_a2(Put):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        flipnr = flippers_x[state_1 << 10 | 0 | turn+1]
        line_flip_func[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 10 | 4 | turn+1]
        line_flip_func[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_17 << 10 | 0 | turn+1]
        line_flip_func[17 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 10 | 0 | turn+1]
        line_flip_func[37 << 6 | flipnr].go()
        state_1 += turn * 1
        state_8 += turn * 3
        state_17 += turn * 1
        state_37 += turn * 1

class put_b2(Put):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        flipnr = flippers_x[state_1 << 10 | 4 | turn+1]
        line_flip_func[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 10 | 4 | turn+1]
        line_flip_func[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_18 << 10 | 4 | turn+1]
        line_flip_func[18 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 10 | 4 | turn+1]
        line_flip_func[38 << 6 | flipnr].go()
        state_1 += turn * 3
        state_9 += turn * 3
        state_18 += turn * 3
        state_38 += turn * 3

class put_c2(Put):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        flipnr = flippers_x[state_1 << 10 | 8 | turn+1]
        line_flip_func[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 10 | 4 | turn+1]
        line_flip_func[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_19 << 10 | 8 | turn+1]
        line_flip_func[19 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 10 | 4 | turn+1]
        line_flip_func[39 << 6 | flipnr].go()
        state_1 += turn * 9
        state_10 += turn * 3
        state_19 += turn * 9
        state_39 += turn * 3

class put_d2(Put):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        flipnr = flippers_x[state_1 << 10 | 12 | turn+1]
        line_flip_func[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 10 | 4 | turn+1]
        line_flip_func[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 10 | 12 | turn+1]
        line_flip_func[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 10 | 4 | turn+1]
        line_flip_func[40 << 6 | flipnr].go()
        state_1 += turn * 27
        state_11 += turn * 3
        state_20 += turn * 27
        state_40 += turn * 3

class put_e2(Put):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        flipnr = flippers_x[state_1 << 10 | 16 | turn+1]
        line_flip_func[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 10 | 4 | turn+1]
        line_flip_func[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 10 | 16 | turn+1]
        line_flip_func[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 10 | 4 | turn+1]
        line_flip_func[41 << 6 | flipnr].go()
        state_1 += turn * 81
        state_12 += turn * 3
        state_21 += turn * 81
        state_41 += turn * 3

class put_f2(Put):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        flipnr = flippers_x[state_1 << 10 | 20 | turn+1]
        line_flip_func[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 10 | 4 | turn+1]
        line_flip_func[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 10 | 20 | turn+1]
        line_flip_func[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_42 << 10 | 4 | turn+1]
        line_flip_func[42 << 6 | flipnr].go()
        state_1 += turn * 243
        state_13 += turn * 3
        state_22 += turn * 243
        state_42 += turn * 3

class put_g2(Put):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        flipnr = flippers_x[state_1 << 10 | 24 | turn+1]
        line_flip_func[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 10 | 4 | turn+1]
        line_flip_func[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 10 | 24 | turn+1]
        line_flip_func[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_43 << 10 | 4 | turn+1]
        line_flip_func[43 << 6 | flipnr].go()
        state_1 += turn * 729
        state_14 += turn * 3
        state_23 += turn * 729
        state_43 += turn * 3

class put_h2(Put):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        flipnr = flippers_x[state_1 << 10 | 28 | turn+1]
        line_flip_func[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 10 | 4 | turn+1]
        line_flip_func[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 10 | 24 | turn+1]
        line_flip_func[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_44 << 10 | 4 | turn+1]
        line_flip_func[44 << 6 | flipnr].go()
        state_1 += turn * 2187
        state_15 += turn * 3
        state_24 += turn * 729
        state_44 += turn * 3

class put_a3(Put):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        flipnr = flippers_x[state_2 << 10 | 0 | turn+1]
        line_flip_func[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 10 | 8 | turn+1]
        line_flip_func[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_18 << 10 | 0 | turn+1]
        line_flip_func[18 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 10 | 0 | turn+1]
        line_flip_func[36 << 6 | flipnr].go()
        state_2 += turn * 1
        state_8 += turn * 9
        state_18 += turn * 1
        state_36 += turn * 1

class put_b3(Put):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        flipnr = flippers_x[state_2 << 10 | 4 | turn+1]
        line_flip_func[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 10 | 8 | turn+1]
        line_flip_func[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_19 << 10 | 4 | turn+1]
        line_flip_func[19 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 10 | 4 | turn+1]
        line_flip_func[37 << 6 | flipnr].go()
        state_2 += turn * 3
        state_9 += turn * 9
        state_19 += turn * 3
        state_37 += turn * 3

class put_c3(Put):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        flipnr = flippers_x[state_2 << 10 | 8 | turn+1]
        line_flip_func[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 10 | 8 | turn+1]
        line_flip_func[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 10 | 8 | turn+1]
        line_flip_func[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 10 | 8 | turn+1]
        line_flip_func[38 << 6 | flipnr].go()
        state_2 += turn * 9
        state_10 += turn * 9
        state_20 += turn * 9
        state_38 += turn * 9

class put_d3(Put):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        flipnr = flippers_x[state_2 << 10 | 12 | turn+1]
        line_flip_func[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 10 | 8 | turn+1]
        line_flip_func[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 10 | 12 | turn+1]
        line_flip_func[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 10 | 8 | turn+1]
        line_flip_func[39 << 6 | flipnr].go()
        state_2 += turn * 27
        state_11 += turn * 9
        state_21 += turn * 27
        state_39 += turn * 9

class put_e3(Put):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        flipnr = flippers_x[state_2 << 10 | 16 | turn+1]
        line_flip_func[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 10 | 8 | turn+1]
        line_flip_func[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 10 | 16 | turn+1]
        line_flip_func[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 10 | 8 | turn+1]
        line_flip_func[40 << 6 | flipnr].go()
        state_2 += turn * 81
        state_12 += turn * 9
        state_22 += turn * 81
        state_40 += turn * 9

class put_f3(Put):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        flipnr = flippers_x[state_2 << 10 | 20 | turn+1]
        line_flip_func[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 10 | 8 | turn+1]
        line_flip_func[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 10 | 20 | turn+1]
        line_flip_func[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 10 | 8 | turn+1]
        line_flip_func[41 << 6 | flipnr].go()
        state_2 += turn * 243
        state_13 += turn * 9
        state_23 += turn * 243
        state_41 += turn * 9

class put_g3(Put):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        flipnr = flippers_x[state_2 << 10 | 24 | turn+1]
        line_flip_func[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 10 | 8 | turn+1]
        line_flip_func[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 10 | 20 | turn+1]
        line_flip_func[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_42 << 10 | 8 | turn+1]
        line_flip_func[42 << 6 | flipnr].go()
        state_2 += turn * 729
        state_14 += turn * 9
        state_24 += turn * 243
        state_42 += turn * 9

class put_h3(Put):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        flipnr = flippers_x[state_2 << 10 | 28 | turn+1]
        line_flip_func[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 10 | 8 | turn+1]
        line_flip_func[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 10 | 20 | turn+1]
        line_flip_func[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_43 << 10 | 8 | turn+1]
        line_flip_func[43 << 6 | flipnr].go()
        state_2 += turn * 2187
        state_15 += turn * 9
        state_25 += turn * 243
        state_43 += turn * 9

class put_a4(Put):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        flipnr = flippers_x[state_3 << 10 | 0 | turn+1]
        line_flip_func[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 10 | 12 | turn+1]
        line_flip_func[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_19 << 10 | 0 | turn+1]
        line_flip_func[19 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 10 | 0 | turn+1]
        line_flip_func[35 << 6 | flipnr].go()
        state_3 += turn * 1
        state_8 += turn * 27
        state_19 += turn * 1
        state_35 += turn * 1

class put_b4(Put):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        flipnr = flippers_x[state_3 << 10 | 4 | turn+1]
        line_flip_func[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 10 | 12 | turn+1]
        line_flip_func[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 10 | 4 | turn+1]
        line_flip_func[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 10 | 4 | turn+1]
        line_flip_func[36 << 6 | flipnr].go()
        state_3 += turn * 3
        state_9 += turn * 27
        state_20 += turn * 3
        state_36 += turn * 3

class put_c4(Put):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        flipnr = flippers_x[state_3 << 10 | 8 | turn+1]
        line_flip_func[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 10 | 12 | turn+1]
        line_flip_func[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 10 | 8 | turn+1]
        line_flip_func[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 10 | 8 | turn+1]
        line_flip_func[37 << 6 | flipnr].go()
        state_3 += turn * 9
        state_10 += turn * 27
        state_21 += turn * 9
        state_37 += turn * 9

class put_d4(Put):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        flipnr = flippers_x[state_3 << 10 | 12 | turn+1]
        line_flip_func[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 10 | 12 | turn+1]
        line_flip_func[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 10 | 12 | turn+1]
        line_flip_func[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 10 | 12 | turn+1]
        line_flip_func[38 << 6 | flipnr].go()
        state_3 += turn * 27
        state_11 += turn * 27
        state_22 += turn * 27
        state_38 += turn * 27

class put_e4(Put):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        flipnr = flippers_x[state_3 << 10 | 16 | turn+1]
        line_flip_func[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 10 | 12 | turn+1]
        line_flip_func[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 10 | 16 | turn+1]
        line_flip_func[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 10 | 12 | turn+1]
        line_flip_func[39 << 6 | flipnr].go()
        state_3 += turn * 81
        state_12 += turn * 27
        state_23 += turn * 81
        state_39 += turn * 27

class put_f4(Put):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        flipnr = flippers_x[state_3 << 10 | 20 | turn+1]
        line_flip_func[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 10 | 12 | turn+1]
        line_flip_func[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 10 | 16 | turn+1]
        line_flip_func[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 10 | 12 | turn+1]
        line_flip_func[40 << 6 | flipnr].go()
        state_3 += turn * 243
        state_13 += turn * 27
        state_24 += turn * 81
        state_40 += turn * 27

class put_g4(Put):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        flipnr = flippers_x[state_3 << 10 | 24 | turn+1]
        line_flip_func[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 10 | 12 | turn+1]
        line_flip_func[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 10 | 16 | turn+1]
        line_flip_func[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 10 | 12 | turn+1]
        line_flip_func[41 << 6 | flipnr].go()
        state_3 += turn * 729
        state_14 += turn * 27
        state_25 += turn * 81
        state_41 += turn * 27

class put_h4(Put):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        flipnr = flippers_x[state_3 << 10 | 28 | turn+1]
        line_flip_func[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 10 | 12 | turn+1]
        line_flip_func[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 10 | 16 | turn+1]
        line_flip_func[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_42 << 10 | 12 | turn+1]
        line_flip_func[42 << 6 | flipnr].go()
        state_3 += turn * 2187
        state_15 += turn * 27
        state_26 += turn * 81
        state_42 += turn * 27

class put_a5(Put):
    def go(self):
        global state_4
        global state_8
        global state_20
        global state_34
        flipnr = flippers_x[state_4 << 10 | 0 | turn+1]
        line_flip_func[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 10 | 16 | turn+1]
        line_flip_func[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 10 | 0 | turn+1]
        line_flip_func[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_34 << 10 | 0 | turn+1]
        line_flip_func[34 << 6 | flipnr].go()
        state_4 += turn * 1
        state_8 += turn * 81
        state_20 += turn * 1
        state_34 += turn * 1

class put_b5(Put):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        flipnr = flippers_x[state_4 << 10 | 4 | turn+1]
        line_flip_func[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 10 | 16 | turn+1]
        line_flip_func[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 10 | 4 | turn+1]
        line_flip_func[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 10 | 4 | turn+1]
        line_flip_func[35 << 6 | flipnr].go()
        state_4 += turn * 3
        state_9 += turn * 81
        state_21 += turn * 3
        state_35 += turn * 3

class put_c5(Put):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        flipnr = flippers_x[state_4 << 10 | 8 | turn+1]
        line_flip_func[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 10 | 16 | turn+1]
        line_flip_func[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 10 | 8 | turn+1]
        line_flip_func[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 10 | 8 | turn+1]
        line_flip_func[36 << 6 | flipnr].go()
        state_4 += turn * 9
        state_10 += turn * 81
        state_22 += turn * 9
        state_36 += turn * 9

class put_d5(Put):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        flipnr = flippers_x[state_4 << 10 | 12 | turn+1]
        line_flip_func[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 10 | 16 | turn+1]
        line_flip_func[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 10 | 12 | turn+1]
        line_flip_func[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 10 | 12 | turn+1]
        line_flip_func[37 << 6 | flipnr].go()
        state_4 += turn * 27
        state_11 += turn * 81
        state_23 += turn * 27
        state_37 += turn * 27

class put_e5(Put):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        flipnr = flippers_x[state_4 << 10 | 16 | turn+1]
        line_flip_func[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 10 | 16 | turn+1]
        line_flip_func[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 10 | 12 | turn+1]
        line_flip_func[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 10 | 16 | turn+1]
        line_flip_func[38 << 6 | flipnr].go()
        state_4 += turn * 81
        state_12 += turn * 81
        state_24 += turn * 27
        state_38 += turn * 81

class put_f5(Put):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        flipnr = flippers_x[state_4 << 10 | 20 | turn+1]
        line_flip_func[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 10 | 16 | turn+1]
        line_flip_func[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 10 | 12 | turn+1]
        line_flip_func[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 10 | 16 | turn+1]
        line_flip_func[39 << 6 | flipnr].go()
        state_4 += turn * 243
        state_13 += turn * 81
        state_25 += turn * 27
        state_39 += turn * 81

class put_g5(Put):
    def go(self):
        global state_4
        global state_14
        global state_26
        global state_40
        flipnr = flippers_x[state_4 << 10 | 24 | turn+1]
        line_flip_func[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 10 | 16 | turn+1]
        line_flip_func[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 10 | 12 | turn+1]
        line_flip_func[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 10 | 16 | turn+1]
        line_flip_func[40 << 6 | flipnr].go()
        state_4 += turn * 729
        state_14 += turn * 81
        state_26 += turn * 27
        state_40 += turn * 81

class put_h5(Put):
    def go(self):
        global state_4
        global state_15
        global state_27
        global state_41
        flipnr = flippers_x[state_4 << 10 | 28 | turn+1]
        line_flip_func[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 10 | 16 | turn+1]
        line_flip_func[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_27 << 10 | 12 | turn+1]
        line_flip_func[27 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 10 | 16 | turn+1]
        line_flip_func[41 << 6 | flipnr].go()
        state_4 += turn * 2187
        state_15 += turn * 81
        state_27 += turn * 27
        state_41 += turn * 81

class put_a6(Put):
    def go(self):
        global state_5
        global state_8
        global state_21
        global state_33
        flipnr = flippers_x[state_5 << 10 | 0 | turn+1]
        line_flip_func[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 10 | 20 | turn+1]
        line_flip_func[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 10 | 0 | turn+1]
        line_flip_func[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_33 << 10 | 0 | turn+1]
        line_flip_func[33 << 6 | flipnr].go()
        state_5 += turn * 1
        state_8 += turn * 243
        state_21 += turn * 1
        state_33 += turn * 1

class put_b6(Put):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        flipnr = flippers_x[state_5 << 10 | 4 | turn+1]
        line_flip_func[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 10 | 20 | turn+1]
        line_flip_func[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 10 | 4 | turn+1]
        line_flip_func[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_34 << 10 | 4 | turn+1]
        line_flip_func[34 << 6 | flipnr].go()
        state_5 += turn * 3
        state_9 += turn * 243
        state_22 += turn * 3
        state_34 += turn * 3

class put_c6(Put):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        flipnr = flippers_x[state_5 << 10 | 8 | turn+1]
        line_flip_func[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 10 | 20 | turn+1]
        line_flip_func[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 10 | 8 | turn+1]
        line_flip_func[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 10 | 8 | turn+1]
        line_flip_func[35 << 6 | flipnr].go()
        state_5 += turn * 9
        state_10 += turn * 243
        state_23 += turn * 9
        state_35 += turn * 9

class put_d6(Put):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        flipnr = flippers_x[state_5 << 10 | 12 | turn+1]
        line_flip_func[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 10 | 20 | turn+1]
        line_flip_func[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 10 | 8 | turn+1]
        line_flip_func[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 10 | 12 | turn+1]
        line_flip_func[36 << 6 | flipnr].go()
        state_5 += turn * 27
        state_11 += turn * 243
        state_24 += turn * 9
        state_36 += turn * 27

class put_e6(Put):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        flipnr = flippers_x[state_5 << 10 | 16 | turn+1]
        line_flip_func[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 10 | 20 | turn+1]
        line_flip_func[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 10 | 8 | turn+1]
        line_flip_func[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 10 | 16 | turn+1]
        line_flip_func[37 << 6 | flipnr].go()
        state_5 += turn * 81
        state_12 += turn * 243
        state_25 += turn * 9
        state_37 += turn * 81

class put_f6(Put):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        flipnr = flippers_x[state_5 << 10 | 20 | turn+1]
        line_flip_func[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 10 | 20 | turn+1]
        line_flip_func[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 10 | 8 | turn+1]
        line_flip_func[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 10 | 20 | turn+1]
        line_flip_func[38 << 6 | flipnr].go()
        state_5 += turn * 243
        state_13 += turn * 243
        state_26 += turn * 9
        state_38 += turn * 243

class put_g6(Put):
    def go(self):
        global state_5
        global state_14
        global state_27
        global state_39
        flipnr = flippers_x[state_5 << 10 | 24 | turn+1]
        line_flip_func[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 10 | 20 | turn+1]
        line_flip_func[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_27 << 10 | 8 | turn+1]
        line_flip_func[27 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 10 | 20 | turn+1]
        line_flip_func[39 << 6 | flipnr].go()
        state_5 += turn * 729
        state_14 += turn * 243
        state_27 += turn * 9
        state_39 += turn * 243

class put_h6(Put):
    def go(self):
        global state_5
        global state_15
        global state_28
        global state_40
        flipnr = flippers_x[state_5 << 10 | 28 | turn+1]
        line_flip_func[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 10 | 20 | turn+1]
        line_flip_func[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_28 << 10 | 8 | turn+1]
        line_flip_func[28 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 10 | 20 | turn+1]
        line_flip_func[40 << 6 | flipnr].go()
        state_5 += turn * 2187
        state_15 += turn * 243
        state_28 += turn * 9
        state_40 += turn * 243

class put_a7(Put):
    def go(self):
        global state_6
        global state_8
        global state_22
        global state_32
        flipnr = flippers_x[state_6 << 10 | 0 | turn+1]
        line_flip_func[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 10 | 24 | turn+1]
        line_flip_func[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 10 | 0 | turn+1]
        line_flip_func[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_32 << 10 | 0 | turn+1]
        line_flip_func[32 << 6 | flipnr].go()
        state_6 += turn * 1
        state_8 += turn * 729
        state_22 += turn * 1
        state_32 += turn * 1

class put_b7(Put):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        flipnr = flippers_x[state_6 << 10 | 4 | turn+1]
        line_flip_func[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 10 | 24 | turn+1]
        line_flip_func[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 10 | 4 | turn+1]
        line_flip_func[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_33 << 10 | 4 | turn+1]
        line_flip_func[33 << 6 | flipnr].go()
        state_6 += turn * 3
        state_9 += turn * 729
        state_23 += turn * 3
        state_33 += turn * 3

class put_c7(Put):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        flipnr = flippers_x[state_6 << 10 | 8 | turn+1]
        line_flip_func[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 10 | 24 | turn+1]
        line_flip_func[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 10 | 4 | turn+1]
        line_flip_func[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_34 << 10 | 8 | turn+1]
        line_flip_func[34 << 6 | flipnr].go()
        state_6 += turn * 9
        state_10 += turn * 729
        state_24 += turn * 3
        state_34 += turn * 9

class put_d7(Put):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        flipnr = flippers_x[state_6 << 10 | 12 | turn+1]
        line_flip_func[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 10 | 24 | turn+1]
        line_flip_func[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 10 | 4 | turn+1]
        line_flip_func[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 10 | 12 | turn+1]
        line_flip_func[35 << 6 | flipnr].go()
        state_6 += turn * 27
        state_11 += turn * 729
        state_25 += turn * 3
        state_35 += turn * 27

class put_e7(Put):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        flipnr = flippers_x[state_6 << 10 | 16 | turn+1]
        line_flip_func[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 10 | 24 | turn+1]
        line_flip_func[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 10 | 4 | turn+1]
        line_flip_func[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 10 | 16 | turn+1]
        line_flip_func[36 << 6 | flipnr].go()
        state_6 += turn * 81
        state_12 += turn * 729
        state_26 += turn * 3
        state_36 += turn * 81

class put_f7(Put):
    def go(self):
        global state_6
        global state_13
        global state_27
        global state_37
        flipnr = flippers_x[state_6 << 10 | 20 | turn+1]
        line_flip_func[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 10 | 24 | turn+1]
        line_flip_func[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_27 << 10 | 4 | turn+1]
        line_flip_func[27 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 10 | 20 | turn+1]
        line_flip_func[37 << 6 | flipnr].go()
        state_6 += turn * 243
        state_13 += turn * 729
        state_27 += turn * 3
        state_37 += turn * 243

class put_g7(Put):
    def go(self):
        global state_6
        global state_14
        global state_28
        global state_38
        flipnr = flippers_x[state_6 << 10 | 24 | turn+1]
        line_flip_func[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 10 | 24 | turn+1]
        line_flip_func[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_28 << 10 | 4 | turn+1]
        line_flip_func[28 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 10 | 24 | turn+1]
        line_flip_func[38 << 6 | flipnr].go()
        state_6 += turn * 729
        state_14 += turn * 729
        state_28 += turn * 3
        state_38 += turn * 729

class put_h7(Put):
    def go(self):
        global state_6
        global state_15
        global state_29
        global state_39
        flipnr = flippers_x[state_6 << 10 | 28 | turn+1]
        line_flip_func[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 10 | 24 | turn+1]
        line_flip_func[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_29 << 10 | 4 | turn+1]
        line_flip_func[29 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 10 | 24 | turn+1]
        line_flip_func[39 << 6 | flipnr].go()
        state_6 += turn * 2187
        state_15 += turn * 729
        state_29 += turn * 3
        state_39 += turn * 729

class put_a8(Put):
    def go(self):
        global state_7
        global state_8
        global state_23
        global state_31
        flipnr = flippers_x[state_7 << 10 | 0 | turn+1]
        line_flip_func[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 10 | 28 | turn+1]
        line_flip_func[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 10 | 0 | turn+1]
        line_flip_func[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_31 << 10 | 0 | turn+1]
        line_flip_func[31 << 6 | flipnr].go()
        state_7 += turn * 1
        state_8 += turn * 2187
        state_23 += turn * 1
        state_31 += turn * 1

class put_b8(Put):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        flipnr = flippers_x[state_7 << 10 | 4 | turn+1]
        line_flip_func[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 10 | 28 | turn+1]
        line_flip_func[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 10 | 0 | turn+1]
        line_flip_func[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_32 << 10 | 4 | turn+1]
        line_flip_func[32 << 6 | flipnr].go()
        state_7 += turn * 3
        state_9 += turn * 2187
        state_24 += turn * 1
        state_32 += turn * 3

class put_c8(Put):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        flipnr = flippers_x[state_7 << 10 | 8 | turn+1]
        line_flip_func[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 10 | 28 | turn+1]
        line_flip_func[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 10 | 0 | turn+1]
        line_flip_func[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_33 << 10 | 8 | turn+1]
        line_flip_func[33 << 6 | flipnr].go()
        state_7 += turn * 9
        state_10 += turn * 2187
        state_25 += turn * 1
        state_33 += turn * 9

class put_d8(Put):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        flipnr = flippers_x[state_7 << 10 | 12 | turn+1]
        line_flip_func[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 10 | 28 | turn+1]
        line_flip_func[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 10 | 0 | turn+1]
        line_flip_func[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_34 << 10 | 12 | turn+1]
        line_flip_func[34 << 6 | flipnr].go()
        state_7 += turn * 27
        state_11 += turn * 2187
        state_26 += turn * 1
        state_34 += turn * 27

class put_e8(Put):
    def go(self):
        global state_7
        global state_12
        global state_27
        global state_35
        flipnr = flippers_x[state_7 << 10 | 16 | turn+1]
        line_flip_func[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 10 | 28 | turn+1]
        line_flip_func[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_27 << 10 | 0 | turn+1]
        line_flip_func[27 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 10 | 16 | turn+1]
        line_flip_func[35 << 6 | flipnr].go()
        state_7 += turn * 81
        state_12 += turn * 2187
        state_27 += turn * 1
        state_35 += turn * 81

class put_f8(Put):
    def go(self):
        global state_7
        global state_13
        global state_28
        global state_36
        flipnr = flippers_x[state_7 << 10 | 20 | turn+1]
        line_flip_func[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 10 | 28 | turn+1]
        line_flip_func[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_28 << 10 | 0 | turn+1]
        line_flip_func[28 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 10 | 20 | turn+1]
        line_flip_func[36 << 6 | flipnr].go()
        state_7 += turn * 243
        state_13 += turn * 2187
        state_28 += turn * 1
        state_36 += turn * 243

class put_g8(Put):
    def go(self):
        global state_7
        global state_14
        global state_29
        global state_37
        flipnr = flippers_x[state_7 << 10 | 24 | turn+1]
        line_flip_func[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 10 | 28 | turn+1]
        line_flip_func[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_29 << 10 | 0 | turn+1]
        line_flip_func[29 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 10 | 24 | turn+1]
        line_flip_func[37 << 6 | flipnr].go()
        state_7 += turn * 729
        state_14 += turn * 2187
        state_29 += turn * 1
        state_37 += turn * 729

class put_h8(Put):
    def go(self):
        global state_7
        global state_15
        global state_30
        global state_38
        flipnr = flippers_x[state_7 << 10 | 28 | turn+1]
        line_flip_func[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 10 | 28 | turn+1]
        line_flip_func[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_30 << 10 | 0 | turn+1]
        line_flip_func[30 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 10 | 28 | turn+1]
        line_flip_func[38 << 6 | flipnr].go()
        state_7 += turn * 2187
        state_15 += turn * 2187
        state_30 += turn * 1
        state_38 += turn * 2187

move_table = [
   put_a1(),
   put_b1(),
   put_c1(),
   put_d1(),
   put_e1(),
   put_f1(),
   put_g1(),
   put_h1(),
   put_a2(),
   put_b2(),
   put_c2(),
   put_d2(),
   put_e2(),
   put_f2(),
   put_g2(),
   put_h2(),
   put_a3(),
   put_b3(),
   put_c3(),
   put_d3(),
   put_e3(),
   put_f3(),
   put_g3(),
   put_h3(),
   put_a4(),
   put_b4(),
   put_c4(),
   put_d4(),
   put_e4(),
   put_f4(),
   put_g4(),
   put_h4(),
   put_a5(),
   put_b5(),
   put_c5(),
   put_d5(),
   put_e5(),
   put_f5(),
   put_g5(),
   put_h5(),
   put_a6(),
   put_b6(),
   put_c6(),
   put_d6(),
   put_e6(),
   put_f6(),
   put_g6(),
   put_h6(),
   put_a7(),
   put_b7(),
   put_c7(),
   put_d7(),
   put_e7(),
   put_f7(),
   put_g7(),
   put_h7(),
   put_a8(),
   put_b8(),
   put_c8(),
   put_d8(),
   put_e8(),
   put_f8(),
   put_g8(),
   put_h8(),
]

class flip_d8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 1998
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_d2_e2_f2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        state_1 += turn * 702
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_c5_d5_e5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2178
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_c2_d3_f5_g6(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_11
        global state_21
        global state_4
        global state_13
        global state_25
        global state_5
        global state_14
        global state_27
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 672
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_b1_c1_e1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2130
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_a4_a5_a7(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_6
        global state_22
        global state_32
        state_3 += turn * 2
        state_8 += turn * 1674
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_d3_e3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        state_2 += turn * 216
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18

class flip_c2_c3_c5_c6_c7(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_1 += turn * 18
        state_10 += turn * 2130
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_c3_d3_e3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        state_2 += turn * 234
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18

class flip_f6_g6(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 1944
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_b6_c6_d6_e6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        state_5 += turn * 240
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162

class flip_d4_d5_d6_d7(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_3 += turn * 54
        state_11 += turn * 2160
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_b3_c4_d5(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_10
        global state_21
        global state_4
        global state_11
        global state_23
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 78
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54

class flip_e2_e3_e4_e5_e6_e7(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_1 += turn * 162
        state_12 += turn * 2184
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_g2_g3_g4(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        state_1 += turn * 1458
        state_14 += turn * 78
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54

class flip_a2_a4_a5_a6_a7(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_1 += turn * 2
        state_8 += turn * 2166
        state_17 += turn * 2
        state_37 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_d7_e7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        state_6 += turn * 216
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162

class flip_f7_g6(Flip):
    def go(self):
        global state_6
        global state_13
        global state_27
        global state_37
        global state_5
        global state_14
        global state_39
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 24
        state_37 += turn * 486
        state_5 += turn * 1458
        state_14 += turn * 486
        state_39 += turn * 486

class flip_a3_a4(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        state_2 += turn * 2
        state_8 += turn * 72
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2

class flip_e3_e4_e6(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_5
        global state_25
        global state_37
        state_2 += turn * 162
        state_12 += turn * 558
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_c2_c3_c4_c5(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        state_1 += turn * 18
        state_10 += turn * 240
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18

class flip_c3_c4_c5_c6(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        state_2 += turn * 18
        state_10 += turn * 720
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_h6_h7(Flip):
    def go(self):
        global state_5
        global state_15
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_5 += turn * 4374
        state_15 += turn * 1944
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_d4_d5(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        state_3 += turn * 54
        state_11 += turn * 216
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54

class flip_b7_d7_e7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2166
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_c5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18

class flip_h3_h4_h6_h7(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_2 += turn * 4374
        state_15 += turn * 2016
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_b3_c4(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_10
        global state_21
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 24
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18

class flip_c3_d4_f6_g7(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_11
        global state_22
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 2016
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_e5_e7(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_6
        global state_26
        global state_36
        state_4 += turn * 162
        state_12 += turn * 1620
        state_24 += turn * 54
        state_38 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_f4_g5(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_4
        global state_14
        global state_26
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 216
        state_4 += turn * 1458
        state_14 += turn * 162
        state_26 += turn * 54

class flip_d2_f4(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_3
        global state_13
        global state_24
        state_1 += turn * 54
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 60
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 162

class flip_c1_d1_e1_g1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_14
        global state_22
        global state_44
        state_0 += turn * 1692
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b8_c8_d8_e8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2184
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_c8_e8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2124
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_e4_e5_e7(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_6
        global state_26
        global state_36
        state_3 += turn * 162
        state_12 += turn * 1674
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_a4_a6_a7(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_3 += turn * 2
        state_8 += turn * 1998
        state_19 += turn * 2
        state_35 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_c3_d3_e3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2178
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_b2_c2_d2_e2_g2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_14
        global state_23
        global state_43
        state_1 += turn * 1698
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_e5_e6_e7(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_4 += turn * 162
        state_12 += turn * 2106
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_b2_d2_e2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        state_1 += turn * 222
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6

class flip_d5_f7(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_6
        global state_13
        global state_27
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 540
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_a3_a5_a6_a7(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_2 += turn * 2
        state_8 += turn * 2124
        state_18 += turn * 2
        state_36 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_b2_c3_e5_f6(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 672
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_b8_c8_e8_f8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        state_7 += turn * 672
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_g2_g4_g5(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        state_1 += turn * 1458
        state_14 += turn * 222
        state_23 += turn * 1458
        state_43 += turn * 6
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b8_d8_e8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2166
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_h5_h6(Flip):
    def go(self):
        global state_4
        global state_15
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        state_4 += turn * 4374
        state_15 += turn * 648
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_c3_d3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2016
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_c4_e4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2124
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_e3_e5_e6_e7(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_2 += turn * 162
        state_12 += turn * 2124
        state_22 += turn * 162
        state_40 += turn * 18
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_d2_d3_d4_d6(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_5
        global state_24
        global state_36
        state_1 += turn * 54
        state_11 += turn * 564
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_b6_c6_d6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2022
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_e6_e7(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_5 += turn * 162
        state_12 += turn * 1944
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_f5_g5(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 1944
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b4_c4_e4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_12
        global state_23
        global state_39
        state_3 += turn * 186
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54

class flip_d2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 1998
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_e4_e6_e7(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_3 += turn * 162
        state_12 += turn * 1998
        state_23 += turn * 162
        state_39 += turn * 54
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_f2_f3_f4_f5_f6_f7(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_1 += turn * 486
        state_13 += turn * 2184
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_f7(Flip):
    def go(self):
        global state_6
        global state_13
        global state_27
        global state_37
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_c4_d3(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_2
        global state_11
        global state_39
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 72
        state_37 += turn * 18
        state_2 += turn * 54
        state_11 += turn * 18
        state_39 += turn * 18

class flip_d5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54

class flip_c3_d3_e3_f3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        state_2 += turn * 720
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_b5_b6(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        state_4 += turn * 6
        state_9 += turn * 648
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_c3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18

class flip_b4_c4_e4_f4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        state_3 += turn * 672
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_c2_c4_c5_c6(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        state_1 += turn * 18
        state_10 += turn * 708
        state_19 += turn * 18
        state_39 += turn * 6
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_b3_c2(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_1
        global state_10
        global state_39
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 24
        state_37 += turn * 6
        state_1 += turn * 18
        state_10 += turn * 6
        state_39 += turn * 6

class flip_b7_c6_d5(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_4
        global state_11
        global state_37
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 78
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54

class flip_g4_g6_g7(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_3 += turn * 1458
        state_14 += turn * 1998
        state_25 += turn * 162
        state_41 += turn * 54
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b2_b3(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        state_1 += turn * 6
        state_9 += turn * 24
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6

class flip_d3_d4_d5_d6_d7(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_2 += turn * 54
        state_11 += turn * 2178
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_a2_a4(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_3
        global state_19
        global state_35
        state_1 += turn * 2
        state_8 += turn * 60
        state_17 += turn * 2
        state_37 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2

class flip_g2_g3_g5_g6(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        state_1 += turn * 1458
        state_14 += turn * 672
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_e2_g2(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_14
        global state_23
        global state_43
        state_1 += turn * 1620
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_b6_c5_d4_e3_f2(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_4
        global state_10
        global state_36
        global state_3
        global state_11
        global state_38
        global state_2
        global state_12
        global state_40
        global state_1
        global state_13
        global state_42
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 726
        state_34 += turn * 6
        state_4 += turn * 18
        state_10 += turn * 162
        state_36 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_c4_c5_c6_c7(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_3 += turn * 18
        state_10 += turn * 2160
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_d2_d4_d5_d6(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        state_1 += turn * 54
        state_11 += turn * 708
        state_20 += turn * 54
        state_40 += turn * 6
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_d4_e4_g4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_14
        global state_25
        global state_41
        state_3 += turn * 1674
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_a3_a5_a6(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        state_2 += turn * 2
        state_8 += turn * 666
        state_18 += turn * 2
        state_36 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_e8(Flip):
    def go(self):
        global state_7
        global state_12
        global state_27
        global state_35
        state_7 += turn * 162
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162

class flip_a2_a3_a5_a6_a7(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_1 += turn * 2
        state_8 += turn * 2130
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_d2_d3_d5_d6(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        state_1 += turn * 54
        state_11 += turn * 672
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_f2_f3_f4_f6_f7(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_1 += turn * 486
        state_13 += turn * 2022
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_f3_f4_f5(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        state_2 += turn * 486
        state_13 += turn * 234
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162

class flip_c4_e6(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_5
        global state_12
        global state_25
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 180
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18

class flip_b7_c6_d5_e4_f3(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 726
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_c4_d5_e6(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_11
        global state_23
        global state_5
        global state_12
        global state_25
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 234
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18

class flip_b3_c4_d5_e6_f7(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_10
        global state_21
        global state_4
        global state_11
        global state_23
        global state_5
        global state_12
        global state_25
        global state_6
        global state_13
        global state_27
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 726
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_d8_e8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2160
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_f3_f4_f5_f6_f7(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_2 += turn * 486
        state_13 += turn * 2178
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_c8_d8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2016
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_h4_h6(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        global state_5
        global state_28
        global state_40
        state_3 += turn * 4374
        state_15 += turn * 540
        state_26 += turn * 162
        state_42 += turn * 54
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_d3_f5_g6(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_4
        global state_13
        global state_25
        global state_5
        global state_14
        global state_27
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 666
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_e2_e3_e5_e6(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        state_1 += turn * 162
        state_12 += turn * 672
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_f3_f4_f6_f7(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_2 += turn * 486
        state_13 += turn * 2016
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_b3_d3_e3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2166
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_b5_c5_d5_f5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_13
        global state_25
        global state_39
        state_4 += turn * 564
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_h3_h5(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_4
        global state_27
        global state_41
        state_2 += turn * 4374
        state_15 += turn * 180
        state_25 += turn * 486
        state_43 += turn * 18
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162

class flip_b2_c3_d4_e5_f6(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 726
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_b1_c1_e1_f1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        state_0 += turn * 672
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_c6_d5_f3_g2(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_4
        global state_11
        global state_37
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 2016
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_c4_d4_e4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        state_3 += turn * 234
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54

class flip_c5_d5_f5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_13
        global state_25
        global state_39
        state_4 += turn * 558
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_b4_b6(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_5
        global state_22
        global state_34
        state_3 += turn * 6
        state_9 += turn * 540
        state_20 += turn * 6
        state_36 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_e5_f6(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_5
        global state_13
        global state_26
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 648
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_c8_e8_f8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        state_7 += turn * 666
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_a4_a5_a6_a7(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_3 += turn * 2
        state_8 += turn * 2160
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_f4_f5_f6_f7(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_3 += turn * 486
        state_13 += turn * 2160
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_b2_c2_d2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2022
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_c3_e3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_12
        global state_22
        global state_40
        state_2 += turn * 180
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18

class flip_b2_c2_d2_e2_f2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        state_1 += turn * 726
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_c6_e6_f6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        state_5 += turn * 666
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_e2_e3_e5(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_4
        global state_24
        global state_38
        state_1 += turn * 162
        state_12 += turn * 186
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_b1_c1_d1_f1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_13
        global state_21
        global state_43
        state_0 += turn * 564
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_d4_f2(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_1
        global state_13
        global state_42
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 540
        state_38 += turn * 54
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_d3_e3_g3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_14
        global state_24
        global state_42
        state_2 += turn * 1674
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_d3_d4_d6(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_5
        global state_24
        global state_36
        state_2 += turn * 54
        state_11 += turn * 558
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_d5_d7(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_6
        global state_25
        global state_35
        state_4 += turn * 54
        state_11 += turn * 1620
        state_23 += turn * 54
        state_37 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_e1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2106
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_c4_e4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_12
        global state_23
        global state_39
        state_3 += turn * 180
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54

class flip_g2_g3_g4_g5_g7(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_6
        global state_28
        global state_38
        state_1 += turn * 1458
        state_14 += turn * 1698
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b7_c6_d5_e4_f3_g2(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 2184
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_a2_a3_a4_a5_a6(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        state_1 += turn * 2
        state_8 += turn * 726
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_f4_f5_f6(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        state_3 += turn * 486
        state_13 += turn * 702
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_e6_f6(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        state_5 += turn * 648
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_d7_e6_f5_g4(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_5
        global state_12
        global state_37
        global state_4
        global state_13
        global state_39
        global state_3
        global state_14
        global state_41
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 240
        state_35 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_37 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_39 += turn * 162
        state_3 += turn * 1458
        state_14 += turn * 54
        state_41 += turn * 54

class flip_g2_g3_g4_g6(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_5
        global state_27
        global state_39
        state_1 += turn * 1458
        state_14 += turn * 564
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_b4_b6_b7(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_3 += turn * 6
        state_9 += turn * 1998
        state_20 += turn * 6
        state_36 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_d7_e6_f5(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_5
        global state_12
        global state_37
        global state_4
        global state_13
        global state_39
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 78
        state_35 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_37 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_39 += turn * 162

class flip_h4_h6_h7(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_3 += turn * 4374
        state_15 += turn * 1998
        state_26 += turn * 162
        state_42 += turn * 54
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_c2_d2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        state_1 += turn * 72
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6

class flip_d7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54

class flip_b3_b4_b5_b6_b7(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_2 += turn * 6
        state_9 += turn * 2178
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_c6_d6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        state_5 += turn * 72
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54

class flip_c6_d5_e4_f3(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 720
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_b4_c4_d4_e4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        state_3 += turn * 240
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54

class flip_b1_c1_d1_e1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2184
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_f8_g8(Flip):
    def go(self):
        global state_7
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 1944
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_b2_c2_e2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_12
        global state_21
        global state_41
        state_1 += turn * 186
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6

class flip_a7(Flip):
    def go(self):
        global state_6
        global state_8
        global state_22
        global state_32
        state_6 += turn * 2
        state_8 += turn * 1458
        state_22 += turn * 2
        state_32 += turn * 2

class flip_b2_c3_e5_f6_g7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 2130
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_b2_d4_e5_f6_g7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 2166
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_e2_g4(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_3
        global state_14
        global state_25
        state_1 += turn * 162
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 60
        state_3 += turn * 1458
        state_14 += turn * 54
        state_25 += turn * 162

class flip_e2_f2(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        state_1 += turn * 648
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_d2_e3_f4(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_12
        global state_22
        global state_3
        global state_13
        global state_24
        state_1 += turn * 54
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 78
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 162

class flip_b3_b5_b6_b7(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_2 += turn * 6
        state_9 += turn * 2124
        state_19 += turn * 6
        state_37 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_e5_f4_g3(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_3
        global state_13
        global state_40
        global state_2
        global state_14
        global state_42
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 702
        state_38 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_g3_g4_g5_g7(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_6
        global state_28
        global state_38
        state_2 += turn * 1458
        state_14 += turn * 1692
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_e3_f2(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_1
        global state_13
        global state_42
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 648
        state_40 += turn * 18
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_d6_e6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        state_5 += turn * 216
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162

class flip_b2_b4_b5_b6_b7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_1 += turn * 6
        state_9 += turn * 2166
        state_18 += turn * 6
        state_38 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_c7_d7_e7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2178
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_c3_d2(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_1
        global state_11
        global state_40
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 72
        state_38 += turn * 18
        state_1 += turn * 54
        state_11 += turn * 6
        state_40 += turn * 6

class flip_e7_f6_g5(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_5
        global state_13
        global state_38
        global state_4
        global state_14
        global state_40
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 78
        state_36 += turn * 162
        state_5 += turn * 486
        state_13 += turn * 486
        state_38 += turn * 486
        state_4 += turn * 1458
        state_14 += turn * 162
        state_40 += turn * 162

class flip_c4_c5(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        state_3 += turn * 18
        state_10 += turn * 216
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18

class flip_h2_h4_h5_h6(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        state_1 += turn * 4374
        state_15 += turn * 708
        state_24 += turn * 1458
        state_44 += turn * 6
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_f4_g3(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_2
        global state_14
        global state_42
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 648
        state_40 += turn * 54
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_c1_d1_e1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2178
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b8_c8_e8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2130
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_h4_h5_h6(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        state_3 += turn * 4374
        state_15 += turn * 702
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_b7_d5(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_4
        global state_11
        global state_37
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 60
        state_33 += turn * 6
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54

class flip_h7(Flip):
    def go(self):
        global state_6
        global state_15
        global state_29
        global state_39
        state_6 += turn * 4374
        state_15 += turn * 1458
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_b7_c6_e4_f3(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 672
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_c2_d3_e4_f5_g6(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_11
        global state_21
        global state_3
        global state_12
        global state_23
        global state_4
        global state_13
        global state_25
        global state_5
        global state_14
        global state_27
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 726
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_d2_d4(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_3
        global state_22
        global state_38
        state_1 += turn * 54
        state_11 += turn * 60
        state_20 += turn * 54
        state_40 += turn * 6
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54

class flip_f3_f5_f6_f7(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_2 += turn * 486
        state_13 += turn * 2124
        state_23 += turn * 486
        state_41 += turn * 18
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_c6_e4_f3_g2(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 2124
        state_35 += turn * 18
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_a3_a4_a5(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        state_2 += turn * 2
        state_8 += turn * 234
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2

class flip_c7_e7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_12
        global state_26
        global state_36
        state_6 += turn * 180
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162

class flip_c3_e5(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_4
        global state_12
        global state_24
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 180
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54

class flip_a2_a3_a5_a6(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        state_1 += turn * 2
        state_8 += turn * 672
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_b4_c5(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_10
        global state_22
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 24
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 18

class flip_b4_d2(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_1
        global state_11
        global state_40
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 60
        state_36 += turn * 6
        state_1 += turn * 54
        state_11 += turn * 6
        state_40 += turn * 6

class flip_c6_d6_e6_f6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        state_5 += turn * 720
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_b8_d8_e8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        state_7 += turn * 222
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162

class flip_c5_d5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        state_4 += turn * 72
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54

class flip_c6_d6_e6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        state_5 += turn * 234
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162

class flip_b2_b4_b5(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        state_1 += turn * 6
        state_9 += turn * 222
        state_18 += turn * 6
        state_38 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6

class flip_a5_a6_a7(Flip):
    def go(self):
        global state_4
        global state_8
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_4 += turn * 2
        state_8 += turn * 2106
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_b5_c5_e5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_12
        global state_24
        global state_38
        state_4 += turn * 186
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_d7_e7_f7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        state_6 += turn * 702
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_f2_f3_f4_f5(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        state_1 += turn * 486
        state_13 += turn * 240
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162

class flip_f3_g2(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_1
        global state_14
        global state_43
        state_2 += turn * 486
        state_13 += turn * 18
        state_23 += turn * 1944
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_e4_f5(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_4
        global state_13
        global state_25
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 216
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54

class flip_g2_g3(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        state_1 += turn * 1458
        state_14 += turn * 24
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18

class flip_a2_a3_a5(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_4
        global state_20
        global state_34
        state_1 += turn * 2
        state_8 += turn * 186
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2

class flip_c7_e7_f7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        state_6 += turn * 666
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_d3_d4(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        state_2 += turn * 54
        state_11 += turn * 72
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54

class flip_h2_h3(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        state_1 += turn * 4374
        state_15 += turn * 24
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18

class flip_b8_c8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        state_7 += turn * 24
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18

class flip_e4_f3_g2(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 2106
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_d4_e3(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_2
        global state_12
        global state_40
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 216
        state_38 += turn * 54
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18

class flip_c4_d5_f7(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_11
        global state_23
        global state_6
        global state_13
        global state_27
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 558
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_c4_d5(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_11
        global state_23
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 72
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54

class flip_c1_d1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2016
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_a3(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        state_2 += turn * 2
        state_8 += turn * 18
        state_18 += turn * 2
        state_36 += turn * 2

class flip_d4_f6(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_5
        global state_13
        global state_26
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 540
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_c3_d4_f6(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_11
        global state_22
        global state_5
        global state_13
        global state_26
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 558
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_b3_c3_d3_e3_g3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_14
        global state_24
        global state_42
        state_2 += turn * 1698
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_b3_b4_b5(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        state_2 += turn * 6
        state_9 += turn * 234
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6

class flip_e4_e6(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_5
        global state_25
        global state_37
        state_3 += turn * 162
        state_12 += turn * 540
        state_23 += turn * 162
        state_39 += turn * 54
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_g4_g5_g6(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        state_3 += turn * 1458
        state_14 += turn * 702
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_e8_f8(Flip):
    def go(self):
        global state_7
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        state_7 += turn * 648
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_b6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6

class flip_f2_f3_f5_f6_f7(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_1 += turn * 486
        state_13 += turn * 2130
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_c6_e4_f3(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 666
        state_35 += turn * 18
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_c6_d6_e6_g6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_14
        global state_27
        global state_39
        state_5 += turn * 1692
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_c8_d8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        state_7 += turn * 72
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54

class flip_h2_h3_h4_h6(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_5
        global state_28
        global state_40
        state_1 += turn * 4374
        state_15 += turn * 564
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_b1_c1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        state_0 += turn * 24
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2

class flip_b1_c1_d1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        state_0 += turn * 78
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2

class flip_b8_c8_d8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        state_7 += turn * 78
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54

class flip_c7_d6_e5_f4(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_5
        global state_11
        global state_36
        global state_4
        global state_12
        global state_38
        global state_3
        global state_13
        global state_40
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 240
        state_34 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_36 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54

class flip_c6_d5_e4_f3_g2(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 2178
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_c2_c4(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_21
        global state_37
        state_1 += turn * 18
        state_10 += turn * 60
        state_19 += turn * 18
        state_39 += turn * 6
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18

class flip_e3_e5_e6(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        state_2 += turn * 162
        state_12 += turn * 666
        state_22 += turn * 162
        state_40 += turn * 18
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_e2_e3(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        state_1 += turn * 162
        state_12 += turn * 24
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18

class flip_h3(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        state_2 += turn * 4374
        state_15 += turn * 18
        state_25 += turn * 486
        state_43 += turn * 18

class flip_e4_f3(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_2
        global state_13
        global state_41
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 648
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_b7_d7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_11
        global state_25
        global state_35
        state_6 += turn * 60
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54

class flip_e1_f1(Flip):
    def go(self):
        global state_0
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        state_0 += turn * 648
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_d3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 1998
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_b8_d8_e8_f8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        state_7 += turn * 708
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_d3_e3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2160
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_e3(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18

class flip_b5_c4(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_3
        global state_10
        global state_37
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 24
        state_35 += turn * 6
        state_3 += turn * 18
        state_10 += turn * 54
        state_37 += turn * 18

class flip_b3_c3_d3_f3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_13
        global state_23
        global state_41
        state_2 += turn * 564
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_c2_c3_c4_c6_c7(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_1 += turn * 18
        state_10 += turn * 2022
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_c7_d6_f4_g3(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_5
        global state_11
        global state_36
        global state_3
        global state_13
        global state_40
        global state_2
        global state_14
        global state_42
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 672
        state_34 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_36 += turn * 54
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_d6_e6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2160
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_b7_c7_d7_f7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_13
        global state_27
        global state_37
        state_6 += turn * 564
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_f2_g2(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 1944
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_d4_f4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_13
        global state_24
        global state_40
        state_3 += turn * 540
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_g5_g6(Flip):
    def go(self):
        global state_4
        global state_14
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        state_4 += turn * 1458
        state_14 += turn * 648
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_h2_h3_h5_h6(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        state_1 += turn * 4374
        state_15 += turn * 672
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_g2_g3_g4_g5_g6_g7(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_1 += turn * 1458
        state_14 += turn * 2184
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_d4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 1998
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_d5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 1998
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_d3_e3_f3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        state_2 += turn * 702
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_c7_e5_f4(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_4
        global state_12
        global state_38
        global state_3
        global state_13
        global state_40
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 222
        state_34 += turn * 18
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54

class flip_b4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6

class flip_c3_c4(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        state_2 += turn * 18
        state_10 += turn * 72
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18

class flip_e2_e4_e5_e6_e7(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_1 += turn * 162
        state_12 += turn * 2166
        state_21 += turn * 162
        state_41 += turn * 6
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_f4_f5(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        state_3 += turn * 486
        state_13 += turn * 216
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162

class flip_d7_f5_g4(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_4
        global state_13
        global state_39
        global state_3
        global state_14
        global state_41
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 222
        state_35 += turn * 54
        state_4 += turn * 486
        state_13 += turn * 162
        state_39 += turn * 162
        state_3 += turn * 1458
        state_14 += turn * 54
        state_41 += turn * 54

class flip_b2_c2_d2_f2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_13
        global state_22
        global state_42
        state_1 += turn * 564
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_b4_d4_e4_f4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        state_3 += turn * 708
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_c1_d1_e1_f1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        state_0 += turn * 720
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_c3_d4_e5_f6(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 720
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_d2_e2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2160
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_b2_b3_b4_b5_b7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_6
        global state_23
        global state_33
        state_1 += turn * 6
        state_9 += turn * 1698
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_e5_g3(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_2
        global state_14
        global state_42
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 540
        state_38 += turn * 162
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_f3_g4(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_14
        global state_25
        state_2 += turn * 486
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 72
        state_3 += turn * 1458
        state_14 += turn * 54
        state_25 += turn * 162

class flip_b1_d1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_11
        global state_19
        global state_41
        state_0 += turn * 60
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2

class flip_f2_f3_f4_f5_f6(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        state_1 += turn * 486
        state_13 += turn * 726
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_b5_b6_b7(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_4 += turn * 6
        state_9 += turn * 2106
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_f6_g5(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        global state_4
        global state_14
        global state_40
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 72
        state_38 += turn * 486
        state_4 += turn * 1458
        state_14 += turn * 162
        state_40 += turn * 162

class flip_d4_e5(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_12
        global state_24
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 216
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54

class flip_c3_d4_e5(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 234
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54

class flip_h5_h6_h7(Flip):
    def go(self):
        global state_4
        global state_15
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_4 += turn * 4374
        state_15 += turn * 2106
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_b7_c7_d7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2022
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b6_c6_e6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2130
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_c7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18

class flip_b4_b5_b6(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        state_3 += turn * 6
        state_9 += turn * 702
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_c6_e6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_12
        global state_25
        global state_37
        state_5 += turn * 180
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162

class flip_d2_d3_d5(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_4
        global state_23
        global state_37
        state_1 += turn * 54
        state_11 += turn * 186
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54

class flip_h2_h3_h5(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_4
        global state_27
        global state_41
        state_1 += turn * 4374
        state_15 += turn * 186
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162

class flip_a5(Flip):
    def go(self):
        global state_4
        global state_8
        global state_20
        global state_34
        state_4 += turn * 2
        state_8 += turn * 162
        state_20 += turn * 2
        state_34 += turn * 2

class flip_e2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2106
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_b2_d2_e2_f2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        state_1 += turn * 708
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_c7_d7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2016
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_e1_g1(Flip):
    def go(self):
        global state_0
        global state_12
        global state_20
        global state_42
        global state_14
        global state_22
        global state_44
        state_0 += turn * 1620
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6

class flip_b5_c4_e2(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_3
        global state_10
        global state_37
        global state_1
        global state_12
        global state_41
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 186
        state_35 += turn * 6
        state_3 += turn * 18
        state_10 += turn * 54
        state_37 += turn * 18
        state_1 += turn * 162
        state_12 += turn * 6
        state_41 += turn * 6

class flip_d4_e5_f6_g7(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 2160
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_c2_e4_f5(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_12
        global state_23
        global state_4
        global state_13
        global state_25
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 222
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54

class flip_c2_c3_c4_c5_c6_c7(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_1 += turn * 18
        state_10 += turn * 2184
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_g2_g3_g4_g6_g7(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_1 += turn * 1458
        state_14 += turn * 2022
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_e3_f4(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_13
        global state_24
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 72
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 162

class flip_e2_f3_g4(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_13
        global state_23
        global state_3
        global state_14
        global state_25
        state_1 += turn * 162
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 78
        state_2 += turn * 486
        state_13 += turn * 18
        state_23 += turn * 486
        state_3 += turn * 1458
        state_14 += turn * 54
        state_25 += turn * 162

class flip_c1_d1_f1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_13
        global state_21
        global state_43
        state_0 += turn * 558
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_g6(Flip):
    def go(self):
        global state_5
        global state_14
        global state_27
        global state_39
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_f4(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_d5_e5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        state_4 += turn * 216
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_d2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        state_1 += turn * 54
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6

class flip_c3_d4(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_11
        global state_22
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 72
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54

class flip_c2_e2_f2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        state_1 += turn * 666
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_c5_d4_f2(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_3
        global state_11
        global state_38
        global state_1
        global state_13
        global state_42
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 558
        state_36 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_g4_g6(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        global state_5
        global state_27
        global state_39
        state_3 += turn * 1458
        state_14 += turn * 540
        state_25 += turn * 162
        state_41 += turn * 54
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_c4_d5_e6_f7(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_11
        global state_23
        global state_5
        global state_12
        global state_25
        global state_6
        global state_13
        global state_27
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 720
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_c3_c5_c6_c7(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_2 += turn * 18
        state_10 += turn * 2124
        state_20 += turn * 18
        state_38 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_b2_b4(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_20
        global state_36
        state_1 += turn * 6
        state_9 += turn * 60
        state_18 += turn * 6
        state_38 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6

class flip_e3_e5(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_4
        global state_24
        global state_38
        state_2 += turn * 162
        state_12 += turn * 180
        state_22 += turn * 162
        state_40 += turn * 18
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_c7_e5(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_4
        global state_12
        global state_38
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 60
        state_34 += turn * 18
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162

class flip_d5_e4_f3_g2(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 2160
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_e5(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_b5_c5_d5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2022
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b7_c6_d5_f3_g2(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_4
        global state_11
        global state_37
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 2022
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_e5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2106
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_c6_e4(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_3
        global state_12
        global state_39
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 180
        state_35 += turn * 18
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54

class flip_d3_f3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_13
        global state_23
        global state_41
        state_2 += turn * 540
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_b6_c5_e3_f2(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_4
        global state_10
        global state_36
        global state_2
        global state_12
        global state_40
        global state_1
        global state_13
        global state_42
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 672
        state_34 += turn * 6
        state_4 += turn * 18
        state_10 += turn * 162
        state_36 += turn * 18
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_c3_d3_f3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_13
        global state_23
        global state_41
        state_2 += turn * 558
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_b4_d4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_11
        global state_22
        global state_38
        state_3 += turn * 60
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54

class flip_b6_c6_d6_f6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_13
        global state_26
        global state_38
        state_5 += turn * 564
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_b6_c5_d4_e3(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_4
        global state_10
        global state_36
        global state_3
        global state_11
        global state_38
        global state_2
        global state_12
        global state_40
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 240
        state_34 += turn * 6
        state_4 += turn * 18
        state_10 += turn * 162
        state_36 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18

class flip_e7_f6(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_5
        global state_13
        global state_38
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 24
        state_36 += turn * 162
        state_5 += turn * 486
        state_13 += turn * 486
        state_38 += turn * 486

class flip_c2_c3_c4_c5_c6(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        state_1 += turn * 18
        state_10 += turn * 726
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_a2_a3_a4_a5(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        state_1 += turn * 2
        state_8 += turn * 240
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2

class flip_d3_e4_f5_g6(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_12
        global state_23
        global state_4
        global state_13
        global state_25
        global state_5
        global state_14
        global state_27
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 720
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_d7_e7_g7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_14
        global state_28
        global state_38
        state_6 += turn * 1674
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b2_c2_e2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2130
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_f3_f4_f5_f6(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        state_2 += turn * 486
        state_13 += turn * 720
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_c7_e5_f4_g3(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_4
        global state_12
        global state_38
        global state_3
        global state_13
        global state_40
        global state_2
        global state_14
        global state_42
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 708
        state_34 += turn * 18
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_c5_e3_f2(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_2
        global state_12
        global state_40
        global state_1
        global state_13
        global state_42
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 666
        state_36 += turn * 18
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_e3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2106
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_g3_g4_g5(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        state_2 += turn * 1458
        state_14 += turn * 234
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b8_c8_d8_e8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        state_7 += turn * 240
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162

class flip_h3_h4_h5(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        state_2 += turn * 4374
        state_15 += turn * 234
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162

class flip_h3_h4_h5_h6(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        state_2 += turn * 4374
        state_15 += turn * 720
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_c3_c4_c5_c6_c7(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_2 += turn * 18
        state_10 += turn * 2178
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_b2_c3_d4_e5_f6_g7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 2184
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_g2_g4_g5_g6_g7(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_1 += turn * 1458
        state_14 += turn * 2166
        state_23 += turn * 1458
        state_43 += turn * 6
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_c6_d6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2016
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_d3_e4(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_12
        global state_23
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 72
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162

class flip_d1_e1_g1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_14
        global state_22
        global state_44
        state_0 += turn * 1674
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b2_b3_b5_b6_b7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_1 += turn * 6
        state_9 += turn * 2130
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_b7_d5_e4_f3_g2(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 2166
        state_33 += turn * 6
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_d2_d3_d5_d6_d7(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_1 += turn * 54
        state_11 += turn * 2130
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_d6_d7(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_5 += turn * 54
        state_11 += turn * 1944
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_f1_g1(Flip):
    def go(self):
        global state_0
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 1944
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_e8_g8(Flip):
    def go(self):
        global state_7
        global state_12
        global state_27
        global state_35
        global state_14
        global state_29
        global state_37
        state_7 += turn * 1620
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_b2_b3_b4(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        state_1 += turn * 6
        state_9 += turn * 78
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6

class flip_d7_f5(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_4
        global state_13
        global state_39
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 60
        state_35 += turn * 54
        state_4 += turn * 486
        state_13 += turn * 162
        state_39 += turn * 162

class flip_b4_c5_d6_e7(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_10
        global state_22
        global state_5
        global state_11
        global state_24
        global state_6
        global state_12
        global state_26
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 240
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 18
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 6

class flip_d4_d6(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_5
        global state_24
        global state_36
        state_3 += turn * 54
        state_11 += turn * 540
        state_22 += turn * 54
        state_38 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_c5_d5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2016
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b3_c3_d3_e3_f3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        state_2 += turn * 726
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_b6_c7(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_6
        global state_10
        global state_24
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 24
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 6

class flip_e6_f5_g4(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_4
        global state_13
        global state_39
        global state_3
        global state_14
        global state_41
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 234
        state_37 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_39 += turn * 162
        state_3 += turn * 1458
        state_14 += turn * 54
        state_41 += turn * 54

class flip_b2_c3_d4_e5_g7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        global state_6
        global state_14
        global state_28
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 1698
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_b8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        state_7 += turn * 6
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6

class flip_c7_d7_e7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        state_6 += turn * 234
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162

class flip_e4_g2(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_1
        global state_14
        global state_43
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 1620
        state_39 += turn * 54
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_g2(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        state_1 += turn * 1458
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_a4_a5_a6(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        state_3 += turn * 2
        state_8 += turn * 702
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_e5_g7(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_6
        global state_14
        global state_28
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 1620
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_e5_f5(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        state_4 += turn * 648
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_d7_e6_g4(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_5
        global state_12
        global state_37
        global state_3
        global state_14
        global state_41
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 186
        state_35 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_37 += turn * 162
        state_3 += turn * 1458
        state_14 += turn * 54
        state_41 += turn * 54

class flip_b8_c8_e8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_12
        global state_27
        global state_35
        state_7 += turn * 186
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162

class flip_b6_c5_d4(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_4
        global state_10
        global state_36
        global state_3
        global state_11
        global state_38
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 78
        state_34 += turn * 6
        state_4 += turn * 18
        state_10 += turn * 162
        state_36 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54

class flip_f6_f7(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_5 += turn * 486
        state_13 += turn * 1944
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_d7_e6(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_5
        global state_12
        global state_37
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 24
        state_35 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_37 += turn * 162

class flip_b3_d5_e6(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_4
        global state_11
        global state_23
        global state_5
        global state_12
        global state_25
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 222
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18

class flip_b4_c3_d2(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_2
        global state_10
        global state_38
        global state_1
        global state_11
        global state_40
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 78
        state_36 += turn * 6
        state_2 += turn * 18
        state_10 += turn * 18
        state_38 += turn * 18
        state_1 += turn * 54
        state_11 += turn * 6
        state_40 += turn * 6

class flip_b3_b4_b5_b7(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_6
        global state_23
        global state_33
        state_2 += turn * 6
        state_9 += turn * 1692
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_b6_c6_e6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_12
        global state_25
        global state_37
        state_5 += turn * 186
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162

class flip_h5(Flip):
    def go(self):
        global state_4
        global state_15
        global state_27
        global state_41
        state_4 += turn * 4374
        state_15 += turn * 162
        state_27 += turn * 54
        state_41 += turn * 162

class flip_b6_c5(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_4
        global state_10
        global state_36
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 24
        state_34 += turn * 6
        state_4 += turn * 18
        state_10 += turn * 162
        state_36 += turn * 18

class flip_d3_d4_d5(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        state_2 += turn * 54
        state_11 += turn * 234
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54

class flip_d5_d6(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        state_4 += turn * 54
        state_11 += turn * 648
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_b3_b5(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_4
        global state_21
        global state_35
        state_2 += turn * 6
        state_9 += turn * 180
        state_19 += turn * 6
        state_37 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6

class flip_b7_c7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        state_6 += turn * 24
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18

class flip_e1(Flip):
    def go(self):
        global state_0
        global state_12
        global state_20
        global state_42
        state_0 += turn * 162
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2

class flip_g6_g7(Flip):
    def go(self):
        global state_5
        global state_14
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_5 += turn * 1458
        state_14 += turn * 1944
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b2_c2_d2_e2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2184
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_e5_e6(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        state_4 += turn * 162
        state_12 += turn * 648
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_h5_h7(Flip):
    def go(self):
        global state_4
        global state_15
        global state_27
        global state_41
        global state_6
        global state_29
        global state_39
        state_4 += turn * 4374
        state_15 += turn * 1620
        state_27 += turn * 54
        state_41 += turn * 162
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_a2_a3_a4_a5_a6_a7(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_1 += turn * 2
        state_8 += turn * 2184
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_b3_c3_d3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2022
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_e4_e5_e6(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        state_3 += turn * 162
        state_12 += turn * 702
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_d5_e4_f3(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 702
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_c3_c4_c5(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        state_2 += turn * 18
        state_10 += turn * 234
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18

class flip_f2_f3_f5(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_4
        global state_25
        global state_39
        state_1 += turn * 486
        state_13 += turn * 186
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162

class flip_e3_e4_e5(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        state_2 += turn * 162
        state_12 += turn * 234
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_c5_d4_e3(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_3
        global state_11
        global state_38
        global state_2
        global state_12
        global state_40
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 234
        state_36 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18

class flip_f8(Flip):
    def go(self):
        global state_7
        global state_13
        global state_28
        global state_36
        state_7 += turn * 486
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_c7_d6(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_5
        global state_11
        global state_36
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 24
        state_34 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_36 += turn * 54

class flip_c5_c7(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_6
        global state_24
        global state_34
        state_4 += turn * 18
        state_10 += turn * 1620
        state_22 += turn * 18
        state_36 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_b1_c1_d1_e1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        state_0 += turn * 240
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2

class flip_e6_f5(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_4
        global state_13
        global state_39
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 72
        state_37 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_39 += turn * 162

class flip_h2_h3_h5_h6_h7(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_1 += turn * 4374
        state_15 += turn * 2130
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_b7_c7_d7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        state_6 += turn * 78
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54

class flip_b3_d5_e6_f7(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_4
        global state_11
        global state_23
        global state_5
        global state_12
        global state_25
        global state_6
        global state_13
        global state_27
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 708
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_d6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54

class flip_c6_d5(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_4
        global state_11
        global state_37
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 72
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54

class flip_b8_c8_d8_e8_f8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        state_7 += turn * 726
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_e7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2106
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_c8_d8_e8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        state_7 += turn * 234
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162

class flip_a5_a7(Flip):
    def go(self):
        global state_4
        global state_8
        global state_20
        global state_34
        global state_6
        global state_22
        global state_32
        state_4 += turn * 2
        state_8 += turn * 1620
        state_20 += turn * 2
        state_34 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_e5_g5(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_14
        global state_26
        global state_40
        state_4 += turn * 1620
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_f3_f4(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        state_2 += turn * 486
        state_13 += turn * 72
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54

class flip_b2_b4_b5_b6(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        state_1 += turn * 6
        state_9 += turn * 708
        state_18 += turn * 6
        state_38 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_c2_d3_e4_f5(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_11
        global state_21
        global state_3
        global state_12
        global state_23
        global state_4
        global state_13
        global state_25
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 240
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54

class flip_c4_d4_f4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_13
        global state_24
        global state_40
        state_3 += turn * 558
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_d2_e3_g5(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_12
        global state_22
        global state_4
        global state_14
        global state_26
        state_1 += turn * 54
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 186
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 162
        state_4 += turn * 1458
        state_14 += turn * 162
        state_26 += turn * 54

class flip_d5_f3_g2(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 1998
        state_37 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_b5_c5_d5_e5_f5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        state_4 += turn * 726
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_d6_e5_f4(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_4
        global state_12
        global state_38
        global state_3
        global state_13
        global state_40
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 234
        state_36 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54

class flip_g2_g3_g5(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_4
        global state_26
        global state_40
        state_1 += turn * 1458
        state_14 += turn * 186
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162

class flip_d3_d5_d6_d7(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_2 += turn * 54
        state_11 += turn * 2124
        state_21 += turn * 54
        state_39 += turn * 18
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_f3_f4_f6(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_5
        global state_26
        global state_38
        state_2 += turn * 486
        state_13 += turn * 558
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_c3_e3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2124
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_g5_g6_g7(Flip):
    def go(self):
        global state_4
        global state_14
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_4 += turn * 1458
        state_14 += turn * 2106
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_c7_d6_e5_f4_g3(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_5
        global state_11
        global state_36
        global state_4
        global state_12
        global state_38
        global state_3
        global state_13
        global state_40
        global state_2
        global state_14
        global state_42
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 726
        state_34 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_36 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_c4_d4_e4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2178
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_c7_d7_e7_g7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_14
        global state_28
        global state_38
        state_6 += turn * 1692
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_d2_d3_d4_d5_d6_d7(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_1 += turn * 54
        state_11 += turn * 2184
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_b3_d3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_11
        global state_21
        global state_39
        state_2 += turn * 60
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18

class flip_h2_h4_h5(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        state_1 += turn * 4374
        state_15 += turn * 222
        state_24 += turn * 1458
        state_44 += turn * 6
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162

class flip_c5_d5_e5_g5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_14
        global state_26
        global state_40
        state_4 += turn * 1692
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b2_c3_d4_f6(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_3
        global state_11
        global state_22
        global state_5
        global state_13
        global state_26
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 564
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_f5_f7(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_6
        global state_27
        global state_37
        state_4 += turn * 486
        state_13 += turn * 1620
        state_25 += turn * 54
        state_39 += turn * 162
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_e4_g4(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_14
        global state_25
        global state_41
        state_3 += turn * 1620
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_g4(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        state_3 += turn * 1458
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_a6_a7(Flip):
    def go(self):
        global state_5
        global state_8
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_5 += turn * 2
        state_8 += turn * 1944
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_f2(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        state_1 += turn * 486
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_c7_e7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2124
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b2_b3_b4_b5(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        state_1 += turn * 6
        state_9 += turn * 240
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6

class flip_b2_b3_b4_b6_b7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_1 += turn * 6
        state_9 += turn * 2022
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_d6_e6_g6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_14
        global state_27
        global state_39
        state_5 += turn * 1674
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_h3_h5_h6_h7(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_2 += turn * 4374
        state_15 += turn * 2124
        state_25 += turn * 486
        state_43 += turn * 18
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_d4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54

class flip_b1_d1_e1_f1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        state_0 += turn * 708
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_h2_h4(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_3
        global state_26
        global state_42
        state_1 += turn * 4374
        state_15 += turn * 60
        state_24 += turn * 1458
        state_44 += turn * 6
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54

class flip_c2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6

class flip_d3_e4_f5(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_12
        global state_23
        global state_4
        global state_13
        global state_25
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 234
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54

class flip_b4_c4_d4_e4_f4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        state_3 += turn * 726
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_d2_e2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        state_1 += turn * 216
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6

class flip_b7_d5_e4_f3(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 708
        state_33 += turn * 6
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_b2_c3_d4_f6_g7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_3
        global state_11
        global state_22
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 2022
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_b6_c5_e3(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_4
        global state_10
        global state_36
        global state_2
        global state_12
        global state_40
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 186
        state_34 += turn * 6
        state_4 += turn * 18
        state_10 += turn * 162
        state_36 += turn * 18
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18

class flip_b5_c5_d5_e5_g5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_14
        global state_26
        global state_40
        state_4 += turn * 1698
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b3_d3_e3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        state_2 += turn * 222
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18

class flip_e2_e3_e4_e6(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_5
        global state_25
        global state_37
        state_1 += turn * 162
        state_12 += turn * 564
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_e7(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162

class flip_d4_e5_f6(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 702
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_b2_d2_e2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2166
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_a3_a4_a5_a7(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_6
        global state_22
        global state_32
        state_2 += turn * 2
        state_8 += turn * 1692
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_f2_f4_f5_f6_f7(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_1 += turn * 486
        state_13 += turn * 2166
        state_22 += turn * 486
        state_42 += turn * 6
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_f2_f4(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_3
        global state_24
        global state_40
        state_1 += turn * 486
        state_13 += turn * 60
        state_22 += turn * 486
        state_42 += turn * 6
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54

class flip_b5_c5_d5_e5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2184
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_g2_g4_g5_g6(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        state_1 += turn * 1458
        state_14 += turn * 708
        state_23 += turn * 1458
        state_43 += turn * 6
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_b3_c4_e6_f7(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_10
        global state_21
        global state_5
        global state_12
        global state_25
        global state_6
        global state_13
        global state_27
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 672
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_h3_h4(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        state_2 += turn * 4374
        state_15 += turn * 72
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54

class flip_c6_d7(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_6
        global state_11
        global state_25
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 72
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 6

class flip_d2_d4_d5(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        state_1 += turn * 54
        state_11 += turn * 222
        state_20 += turn * 54
        state_40 += turn * 6
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54

class flip_d4_d5_d7(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_6
        global state_25
        global state_35
        state_3 += turn * 54
        state_11 += turn * 1674
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_c6_e6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2124
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_d3_e2(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_1
        global state_12
        global state_41
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 216
        state_39 += turn * 18
        state_1 += turn * 162
        state_12 += turn * 6
        state_41 += turn * 6

class flip_c1_d1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        state_0 += turn * 72
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2

class flip_b7_d7_e7_f7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        state_6 += turn * 708
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_e2_e3_e4_e5_e7(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_6
        global state_26
        global state_36
        state_1 += turn * 162
        state_12 += turn * 1698
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_d1_e1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        state_0 += turn * 216
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2

class flip_b7_c6_d5_e4_g2(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        global state_1
        global state_14
        global state_43
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 1698
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_b5_c6(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_5
        global state_10
        global state_23
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 24
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 18

class flip_b4_c4_d4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2022
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_a4_a6(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        global state_5
        global state_21
        global state_33
        state_3 += turn * 2
        state_8 += turn * 540
        state_19 += turn * 2
        state_35 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_b3_c3_e3_f3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        state_2 += turn * 672
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_c2_c4_c5(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        state_1 += turn * 18
        state_10 += turn * 222
        state_19 += turn * 18
        state_39 += turn * 6
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18

class flip_b7_c7_e7_f7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        state_6 += turn * 672
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_a3_a4_a6_a7(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_2 += turn * 2
        state_8 += turn * 2016
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_b5_c5_d5_e5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        state_4 += turn * 240
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_c4_c5_c7(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_6
        global state_24
        global state_34
        state_3 += turn * 18
        state_10 += turn * 1674
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_c5_d5_e5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        state_4 += turn * 234
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_h2_h3_h4_h5(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        state_1 += turn * 4374
        state_15 += turn * 240
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162

class flip_b2_c3_d4_e5(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 240
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54

class flip_d7_f7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_13
        global state_27
        global state_37
        state_6 += turn * 540
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_e5_f6_g7(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 2106
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_b4_c5_e7(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_10
        global state_22
        global state_6
        global state_12
        global state_26
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 186
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 18
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 6

class flip_f4_g4(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 1944
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_c2_e2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2124
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_h4_h5_h7(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_6
        global state_29
        global state_39
        state_3 += turn * 4374
        state_15 += turn * 1674
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_g2_g3_g4_g5_g6(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        state_1 += turn * 1458
        state_14 += turn * 726
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_e4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2106
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_b1_d1_e1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        state_0 += turn * 222
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2

class flip_f6_g7(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        global state_6
        global state_14
        global state_28
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 1944
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_e2_e3_e4_e6_e7(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_1 += turn * 162
        state_12 += turn * 2022
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_b7_d5_e4(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 222
        state_33 += turn * 6
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54

class flip_b3_c3_d3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        state_2 += turn * 78
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18

class flip_b6_c5_d4_f2(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_4
        global state_10
        global state_36
        global state_3
        global state_11
        global state_38
        global state_1
        global state_13
        global state_42
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 564
        state_34 += turn * 6
        state_4 += turn * 18
        state_10 += turn * 162
        state_36 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_d6_f4(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_3
        global state_13
        global state_40
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 180
        state_36 += turn * 54
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54

class flip_f7_g7(Flip):
    def go(self):
        global state_6
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 1944
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_a2_a4_a5_a6(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        state_1 += turn * 2
        state_8 += turn * 708
        state_17 += turn * 2
        state_37 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_b3_b5_b6(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        state_2 += turn * 6
        state_9 += turn * 666
        state_19 += turn * 6
        state_37 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_d5_e4_g2(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_3
        global state_12
        global state_39
        global state_1
        global state_14
        global state_43
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 1674
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_d8_e8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        state_7 += turn * 216
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162

class flip_b1_d1_e1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2166
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b6_d4(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_3
        global state_11
        global state_38
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 60
        state_34 += turn * 6
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54

class flip_b2_c2_e2_f2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        state_1 += turn * 672
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_c2_e4_f5_g6(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_12
        global state_23
        global state_4
        global state_13
        global state_25
        global state_5
        global state_14
        global state_27
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 708
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_f5_g4(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_3
        global state_14
        global state_41
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 216
        state_39 += turn * 162
        state_3 += turn * 1458
        state_14 += turn * 54
        state_41 += turn * 54

class flip_a3_a4_a5_a6_a7(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_2 += turn * 2
        state_8 += turn * 2178
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_g3_g4_g5_g6(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        state_2 += turn * 1458
        state_14 += turn * 720
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_g8(Flip):
    def go(self):
        global state_7
        global state_14
        global state_29
        global state_37
        state_7 += turn * 1458
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_c3_e5_f6_g7(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 2124
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_f3_g3(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 1944
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_f6(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_b3_c3_d3_e3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        state_2 += turn * 240
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18

class flip_d2_d3(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        state_1 += turn * 54
        state_11 += turn * 24
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18

class flip_g2_g4(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_3
        global state_25
        global state_41
        state_1 += turn * 1458
        state_14 += turn * 60
        state_23 += turn * 1458
        state_43 += turn * 6
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54

class flip_d6_e5(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_4
        global state_12
        global state_38
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 72
        state_36 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162

class flip_f4_f5_f7(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_6
        global state_27
        global state_37
        state_3 += turn * 486
        state_13 += turn * 1674
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_e6_f7(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_6
        global state_13
        global state_27
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 648
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_d4_e4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        state_3 += turn * 216
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54

class flip_b5_c5_d5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        state_4 += turn * 78
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54

class flip_b8_c8_d8_e8_g8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_14
        global state_29
        global state_37
        state_7 += turn * 1698
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_c3_c4_c5_c7(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_6
        global state_24
        global state_34
        state_2 += turn * 18
        state_10 += turn * 1692
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_c6_d5_e4_g2(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        global state_1
        global state_14
        global state_43
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 1692
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_d8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        state_7 += turn * 54
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54

class flip_c2_d2_e2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        state_1 += turn * 234
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6

class flip_a4(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        state_3 += turn * 2
        state_8 += turn * 54
        state_19 += turn * 2
        state_35 += turn * 2

class flip_d5_e5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2160
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_d5_f3(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_2
        global state_13
        global state_41
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 540
        state_37 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_c5_d4_e3_f2(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_3
        global state_11
        global state_38
        global state_2
        global state_12
        global state_40
        global state_1
        global state_13
        global state_42
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 720
        state_36 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_d2_d3_d4_d5_d7(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_6
        global state_25
        global state_35
        state_1 += turn * 54
        state_11 += turn * 1698
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_a2_a3_a4_a6(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_5
        global state_21
        global state_33
        state_1 += turn * 2
        state_8 += turn * 564
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_d5_d6_d7(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_4 += turn * 54
        state_11 += turn * 2106
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_h2_h3_h4_h5_h7(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_6
        global state_29
        global state_39
        state_1 += turn * 4374
        state_15 += turn * 1698
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_c2_e2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_12
        global state_21
        global state_41
        state_1 += turn * 180
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6

class flip_e2_f3(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_13
        global state_23
        state_1 += turn * 162
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 24
        state_2 += turn * 486
        state_13 += turn * 18
        state_23 += turn * 486

class flip_d6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 1998
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_b7_c7_d7_e7_f7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        state_6 += turn * 726
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_d3_f5(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_4
        global state_13
        global state_25
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 180
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54

class flip_b7_d7_e7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        state_6 += turn * 222
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162

class flip_b4_d6(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_5
        global state_11
        global state_24
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 60
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 18

class flip_e3_g5(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_4
        global state_14
        global state_26
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 180
        state_4 += turn * 1458
        state_14 += turn * 162
        state_26 += turn * 54

class flip_e3_f3(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        state_2 += turn * 648
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_b4_c4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        state_3 += turn * 24
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18

class flip_e2_e4_e5(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        state_1 += turn * 162
        state_12 += turn * 222
        state_21 += turn * 162
        state_41 += turn * 6
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_c3_e3_f3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        state_2 += turn * 666
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_c5_d4(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_3
        global state_11
        global state_38
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 72
        state_36 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54

class flip_c7_d7_e7_f7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        state_6 += turn * 720
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_a2_a3_a4_a6_a7(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_5
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_1 += turn * 2
        state_8 += turn * 2022
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_b5_b7(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_6
        global state_23
        global state_33
        state_4 += turn * 6
        state_9 += turn * 1620
        state_21 += turn * 6
        state_35 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_b3_d5(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_4
        global state_11
        global state_23
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 60
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54

class flip_h2_h3_h4_h5_h6_h7(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_1 += turn * 4374
        state_15 += turn * 2184
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_b3_c3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        state_2 += turn * 24
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18

class flip_d5_e4(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_3
        global state_12
        global state_39
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 216
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54

class flip_c8_d8_e8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2178
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_c2_c3_c4_c5_c7(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_6
        global state_24
        global state_34
        state_1 += turn * 18
        state_10 += turn * 1698
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_c1_e1_f1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        state_0 += turn * 666
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_b5_d5_e5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2166
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_g3_g5(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_4
        global state_26
        global state_40
        state_2 += turn * 1458
        state_14 += turn * 180
        state_24 += turn * 486
        state_42 += turn * 18
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162

class flip_e2_e4(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_3
        global state_23
        global state_39
        state_1 += turn * 162
        state_12 += turn * 60
        state_21 += turn * 162
        state_41 += turn * 6
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54

class flip_c4_d3_e2(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_2
        global state_11
        global state_39
        global state_1
        global state_12
        global state_41
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 234
        state_37 += turn * 18
        state_2 += turn * 54
        state_11 += turn * 18
        state_39 += turn * 18
        state_1 += turn * 162
        state_12 += turn * 6
        state_41 += turn * 6

class flip_e4_g6(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_5
        global state_14
        global state_27
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 540
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_c5_d6_e7(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_5
        global state_11
        global state_24
        global state_6
        global state_12
        global state_26
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 234
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 18
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 6

class flip_c6_d6_e6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2178
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_b3_c3_d3_e3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2184
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_e4_f4(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        state_3 += turn * 648
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_c4_d4_e4_g4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_14
        global state_25
        global state_41
        state_3 += turn * 1692
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_d1_e1_f1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        state_0 += turn * 702
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_e3_e4(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        state_2 += turn * 162
        state_12 += turn * 72
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54

class flip_c5_e7(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_6
        global state_12
        global state_26
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 180
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 6

class flip_c1_d1_e1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        state_0 += turn * 234
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2

class flip_d3_d4_d5_d7(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_6
        global state_25
        global state_35
        state_2 += turn * 54
        state_11 += turn * 1692
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_c4_d4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        state_3 += turn * 72
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54

class flip_b6_c6_e6_f6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        state_5 += turn * 672
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_c1_e1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2124
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b4_c4_d4_e4_g4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_14
        global state_25
        global state_41
        state_3 += turn * 1698
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_f2_g3(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_14
        global state_24
        state_1 += turn * 486
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 24
        state_2 += turn * 1458
        state_14 += turn * 18
        state_24 += turn * 486

class flip_e7_g7(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_14
        global state_28
        global state_38
        state_6 += turn * 1620
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_e3_e4_e5_e6(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        state_2 += turn * 162
        state_12 += turn * 720
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_b1_c1_d1_e1_g1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_14
        global state_22
        global state_44
        state_0 += turn * 1698
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b4_b5_b6_b7(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_3 += turn * 6
        state_9 += turn * 2160
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_e4_e5(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        state_3 += turn * 162
        state_12 += turn * 216
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_b4_d6_e7(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_5
        global state_11
        global state_24
        global state_6
        global state_12
        global state_26
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 222
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 18
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 6

class flip_d2_d3_d4_d5(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        state_1 += turn * 54
        state_11 += turn * 240
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54

class flip_f4_f6(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_5
        global state_26
        global state_38
        state_3 += turn * 486
        state_13 += turn * 540
        state_24 += turn * 162
        state_40 += turn * 54
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_b2_c2_d2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        state_1 += turn * 78
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6

class flip_b5_c5_e5_f5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        state_4 += turn * 672
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_b8_c8_d8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2022
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_b6_d6_e6_f6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        state_5 += turn * 708
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_c5_e5_f5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        state_4 += turn * 666
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_c2_c3_c5_c6(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        state_1 += turn * 18
        state_10 += turn * 672
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_f2_f4_f5(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        state_1 += turn * 486
        state_13 += turn * 222
        state_22 += turn * 486
        state_42 += turn * 6
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162

class flip_c6_c7(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_5 += turn * 18
        state_10 += turn * 1944
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_a2_a3(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        state_1 += turn * 2
        state_8 += turn * 24
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2

class flip_h2(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        state_1 += turn * 4374
        state_15 += turn * 6
        state_24 += turn * 1458
        state_44 += turn * 6

class flip_b3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6

class flip_c1_e1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_12
        global state_20
        global state_42
        state_0 += turn * 180
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2

class flip_f2_f4_f5_f6(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        state_1 += turn * 486
        state_13 += turn * 708
        state_22 += turn * 486
        state_42 += turn * 6
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_f5_f6(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        state_4 += turn * 486
        state_13 += turn * 648
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_b5_d5_e5_f5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        state_4 += turn * 708
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_d7_e7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2160
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_h4_h5(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        state_3 += turn * 4374
        state_15 += turn * 216
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162

class flip_a3_a5(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_4
        global state_20
        global state_34
        state_2 += turn * 2
        state_8 += turn * 180
        state_18 += turn * 2
        state_36 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2

class flip_c7_d6_e5_g3(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_5
        global state_11
        global state_36
        global state_4
        global state_12
        global state_38
        global state_2
        global state_14
        global state_42
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 564
        state_34 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_36 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_d5_e5_f5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        state_4 += turn * 702
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_c2_c3_c4_c6(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_5
        global state_23
        global state_35
        state_1 += turn * 18
        state_10 += turn * 564
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_b2_d2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_11
        global state_20
        global state_40
        state_1 += turn * 60
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6

class flip_f3_f5(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_4
        global state_25
        global state_39
        state_2 += turn * 486
        state_13 += turn * 180
        state_23 += turn * 486
        state_41 += turn * 18
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162

class flip_g4_g5_g6_g7(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_3 += turn * 1458
        state_14 += turn * 2160
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_e6_g4(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_3
        global state_14
        global state_41
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 180
        state_37 += turn * 162
        state_3 += turn * 1458
        state_14 += turn * 54
        state_41 += turn * 54

class flip_c2_c3_c4(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        state_1 += turn * 18
        state_10 += turn * 78
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18

class flip_h3_h5_h6(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        state_2 += turn * 4374
        state_15 += turn * 666
        state_25 += turn * 486
        state_43 += turn * 18
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_e7_g5(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_4
        global state_14
        global state_40
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 60
        state_36 += turn * 162
        state_4 += turn * 1458
        state_14 += turn * 162
        state_40 += turn * 162

class flip_c2_d3(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_11
        global state_21
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 24
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54

class flip_c6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18

class flip_h2_h4_h5_h6_h7(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_1 += turn * 4374
        state_15 += turn * 2166
        state_24 += turn * 1458
        state_44 += turn * 6
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_g2_g3_g5_g6_g7(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_1 += turn * 1458
        state_14 += turn * 2130
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b4_b5(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        state_3 += turn * 6
        state_9 += turn * 216
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6

class flip_c8_e8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_12
        global state_27
        global state_35
        state_7 += turn * 180
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162

class flip_d4_d6_d7(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_3 += turn * 54
        state_11 += turn * 1998
        state_22 += turn * 54
        state_38 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_b1_c1_e1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_12
        global state_20
        global state_42
        state_0 += turn * 186
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2

class flip_b2_b3_b4_b5_b6(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        state_1 += turn * 6
        state_9 += turn * 726
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_c5_e3(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_2
        global state_12
        global state_40
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 180
        state_36 += turn * 18
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18

class flip_a2_a3_a4_a5_a7(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_6
        global state_22
        global state_32
        state_1 += turn * 2
        state_8 += turn * 1698
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_6 += turn * 2
        state_22 += turn * 2
        state_32 += turn * 2

class flip_b2_c3_e5(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_4
        global state_12
        global state_24
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 186
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54

class flip_h4_h5_h6_h7(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_3 += turn * 4374
        state_15 += turn * 2160
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_b5_d3(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_2
        global state_11
        global state_39
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 60
        state_35 += turn * 6
        state_2 += turn * 54
        state_11 += turn * 18
        state_39 += turn * 18

class flip_b7_c7_d7_e7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        state_6 += turn * 240
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162

class flip_b5_c4_d3(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_3
        global state_10
        global state_37
        global state_2
        global state_11
        global state_39
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 78
        state_35 += turn * 6
        state_3 += turn * 18
        state_10 += turn * 54
        state_37 += turn * 18
        state_2 += turn * 54
        state_11 += turn * 18
        state_39 += turn * 18

class flip_b8_c8_d8_f8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_13
        global state_28
        global state_36
        state_7 += turn * 564
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_c2_d3_f5(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_11
        global state_21
        global state_4
        global state_13
        global state_25
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 186
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54

class flip_b5_d5_e5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        state_4 += turn * 222
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_d2_d3_d4(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        state_1 += turn * 54
        state_11 += turn * 78
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54

class flip_e2_e3_e4(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        state_1 += turn * 162
        state_12 += turn * 78
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54

class flip_h2_h3_h4(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        state_1 += turn * 4374
        state_15 += turn * 78
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54

class flip_b3_b4_b6_b7(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_2 += turn * 6
        state_9 += turn * 2016
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_b6_d6_e6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2166
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_g3_g5_g6(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        state_2 += turn * 1458
        state_14 += turn * 666
        state_24 += turn * 486
        state_42 += turn * 18
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_g3_g4_g6_g7(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_2 += turn * 1458
        state_14 += turn * 2016
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_c3_d3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        state_2 += turn * 72
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18

class flip_b1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        state_0 += turn * 6
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2

class flip_d4_e4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2160
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_c5_d5_e5_f5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        state_4 += turn * 720
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_f5_g6(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_5
        global state_14
        global state_27
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 648
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_d8_e8_f8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        state_7 += turn * 702
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_g3_g4_g6(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_5
        global state_27
        global state_39
        state_2 += turn * 1458
        state_14 += turn * 558
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486

class flip_h3_h4_h6(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_5
        global state_28
        global state_40
        state_2 += turn * 4374
        state_15 += turn * 558
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_h3_h4_h5_h7(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_6
        global state_29
        global state_39
        state_2 += turn * 4374
        state_15 += turn * 1692
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_c4_e4_f4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        state_3 += turn * 666
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_d5_e5_g5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        global state_14
        global state_26
        global state_40
        state_4 += turn * 1674
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_g2_g3_g4_g5(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        state_1 += turn * 1458
        state_14 += turn * 240
        state_23 += turn * 1458
        state_43 += turn * 6
        state_2 += turn * 1458
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162

class flip_e4_f5_g6(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_4
        global state_13
        global state_25
        global state_5
        global state_14
        global state_27
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 702
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_d6_e7(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_6
        global state_12
        global state_26
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 216
        state_6 += turn * 162
        state_12 += turn * 1458
        state_26 += turn * 6

class flip_f3_f5_f6(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        state_2 += turn * 486
        state_13 += turn * 666
        state_23 += turn * 486
        state_41 += turn * 18
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_f5_f6_f7(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_4 += turn * 486
        state_13 += turn * 2106
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_d6_e6_f6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        state_5 += turn * 702
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_a3_a4_a6(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_5
        global state_21
        global state_33
        state_2 += turn * 2
        state_8 += turn * 558
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_c4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18

class flip_f2_f3_f4_f5_f7(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_6
        global state_27
        global state_37
        state_1 += turn * 486
        state_13 += turn * 1698
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_d3_d5_d6(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        state_2 += turn * 54
        state_11 += turn * 666
        state_21 += turn * 54
        state_39 += turn * 18
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_a2(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        state_1 += turn * 2
        state_8 += turn * 6
        state_17 += turn * 2
        state_37 += turn * 2

class flip_c3_d4_e5_f6_g7(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 2178
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_b7_c7_d7_e7_g7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_14
        global state_28
        global state_38
        state_6 += turn * 1698
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_c2_e4(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_12
        global state_23
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 60
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162

class flip_c4_e6_f7(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_5
        global state_12
        global state_25
        global state_6
        global state_13
        global state_27
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 666
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_c3_c5_c6(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        state_2 += turn * 18
        state_10 += turn * 666
        state_20 += turn * 18
        state_38 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_e3_g3(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_14
        global state_24
        global state_42
        state_2 += turn * 1620
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_b2_b3_b4_b5_b6_b7(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_1 += turn * 6
        state_9 += turn * 2184
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_e4_e5_e6_e7(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_3 += turn * 162
        state_12 += turn * 2160
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_b7_c6_e4_f3_g2(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_3
        global state_12
        global state_39
        global state_2
        global state_13
        global state_41
        global state_1
        global state_14
        global state_43
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 2130
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18
        state_1 += turn * 1458
        state_14 += turn * 6
        state_43 += turn * 6

class flip_g3(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        state_2 += turn * 1458
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_f1(Flip):
    def go(self):
        global state_0
        global state_13
        global state_21
        global state_43
        state_0 += turn * 486
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_c8_d8_e8_f8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        state_7 += turn * 720
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_d3_d5(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_4
        global state_23
        global state_37
        state_2 += turn * 54
        state_11 += turn * 180
        state_21 += turn * 54
        state_39 += turn * 18
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54

class flip_c3_e5_f6(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 666
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_b7_c7_e7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2130
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_c4_d4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2016
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_b1_c1_d1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2022
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_a2_a4_a5(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        state_1 += turn * 2
        state_8 += turn * 222
        state_17 += turn * 2
        state_37 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2

class flip_c3_c4_c6_c7(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_2 += turn * 18
        state_10 += turn * 2016
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_d6_f4_g3(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_3
        global state_13
        global state_40
        global state_2
        global state_14
        global state_42
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 666
        state_36 += turn * 54
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_c2_d3_e4(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_11
        global state_21
        global state_3
        global state_12
        global state_23
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 78
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162

class flip_h6(Flip):
    def go(self):
        global state_5
        global state_15
        global state_28
        global state_40
        state_5 += turn * 4374
        state_15 += turn * 486
        state_28 += turn * 18
        state_40 += turn * 486

class flip_b6_c6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        state_5 += turn * 24
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18

class flip_c5_e5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_12
        global state_24
        global state_38
        state_4 += turn * 180
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_g4_g5_g7(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_6
        global state_28
        global state_38
        state_3 += turn * 1458
        state_14 += turn * 1674
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6

class flip_b4_c5_d6(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_10
        global state_22
        global state_5
        global state_11
        global state_24
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 78
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 18

class flip_e2(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        state_1 += turn * 162
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6

class flip_b4_d4_e4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2166
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_d2_d3_d4_d6_d7(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_1 += turn * 54
        state_11 += turn * 2022
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_c4_d4_e4_f4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        state_3 += turn * 720
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_e2_e4_e5_e6(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        state_1 += turn * 162
        state_12 += turn * 708
        state_21 += turn * 162
        state_41 += turn * 6
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_h3_h4_h5_h6_h7(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_2 += turn * 4374
        state_15 += turn * 2178
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_c8_d8_f8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_13
        global state_28
        global state_36
        state_7 += turn * 558
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_b7_c7_e7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_12
        global state_26
        global state_36
        state_6 += turn * 186
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162

class flip_c2_d2_e2_g2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_14
        global state_23
        global state_43
        state_1 += turn * 1692
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_d4_e5_g7(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_12
        global state_24
        global state_6
        global state_14
        global state_28
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 1674
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_c3_c4_c6(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        global state_5
        global state_23
        global state_35
        state_2 += turn * 18
        state_10 += turn * 558
        state_20 += turn * 18
        state_38 += turn * 18
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_f2_f3(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        state_1 += turn * 486
        state_13 += turn * 24
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18

class flip_c7_d7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        state_6 += turn * 72
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54

class flip_e7_f7(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        state_6 += turn * 648
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_b4_c4_d4_f4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_13
        global state_24
        global state_40
        state_3 += turn * 564
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_b3_c4_d5_e6(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_10
        global state_21
        global state_4
        global state_11
        global state_23
        global state_5
        global state_12
        global state_25
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 240
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18

class flip_b2_c3(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 24
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18

class flip_f3_f4_f5_f7(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        global state_6
        global state_27
        global state_37
        state_2 += turn * 486
        state_13 += turn * 1692
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_b7_c7_d7_e7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 2184
        state_9 += turn * 1458
        state_23 += turn * 6
        state_33 += turn * 6
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_12 += turn * 1458
        state_26 += turn * 6
        state_36 += turn * 162
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_d5_e6_f7(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_5
        global state_12
        global state_25
        global state_6
        global state_13
        global state_27
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 702
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_g3_g4_g5_g6_g7(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_2 += turn * 1458
        state_14 += turn * 2178
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_d4_d5_d6(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        state_3 += turn * 54
        state_11 += turn * 702
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_d2_e3_f4_g5(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_12
        global state_22
        global state_3
        global state_13
        global state_24
        global state_4
        global state_14
        global state_26
        state_1 += turn * 54
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 240
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 162
        state_4 += turn * 1458
        state_14 += turn * 162
        state_26 += turn * 54

class flip_a2_a3_a4(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        state_1 += turn * 2
        state_8 += turn * 78
        state_17 += turn * 2
        state_37 += turn * 2
        state_2 += turn * 2
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2

class flip_g1(Flip):
    def go(self):
        global state_0
        global state_14
        global state_22
        global state_44
        state_0 += turn * 1458
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b2_d4_e5_f6(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        global state_5
        global state_13
        global state_26
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 708
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18

class flip_b7_c6(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 24
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18

class flip_b2_d4_e5(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 222
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54

class flip_e5_f4(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_3
        global state_13
        global state_40
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 216
        state_38 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54

class flip_b5_c5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        state_4 += turn * 24
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18

class flip_d6_f6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_13
        global state_26
        global state_38
        state_5 += turn * 540
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_d1_e1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 2160
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_d1_f1_g1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += turn * 1998
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2
        state_14 += turn * 2
        state_22 += turn * 1458
        state_44 += turn * 2

class flip_b4_d4_e4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        state_3 += turn * 222
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54

class flip_b6_c6_d6_e6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2184
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_g5_g7(Flip):
    def go(self):
        global state_4
        global state_14
        global state_26
        global state_40
        global state_6
        global state_28
        global state_38
        state_4 += turn * 1458
        state_14 += turn * 1620
        state_26 += turn * 54
        state_40 += turn * 162
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_e3_f4_g5(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_13
        global state_24
        global state_4
        global state_14
        global state_26
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 234
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 162
        state_4 += turn * 1458
        state_14 += turn * 162
        state_26 += turn * 54

class flip_b3_b4_b5_b6(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        state_2 += turn * 6
        state_9 += turn * 720
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_c5_c6(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        state_4 += turn * 18
        state_10 += turn * 648
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_b6_d6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_11
        global state_24
        global state_36
        state_5 += turn * 60
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54

class flip_b3_c3_e3_f3_g3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += turn * 2130
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_h4(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        state_3 += turn * 4374
        state_15 += turn * 54
        state_26 += turn * 162
        state_42 += turn * 54

class flip_d2_f4_g5(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_3
        global state_13
        global state_24
        global state_4
        global state_14
        global state_26
        state_1 += turn * 54
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 222
        state_3 += turn * 486
        state_13 += turn * 54
        state_24 += turn * 162
        state_4 += turn * 1458
        state_14 += turn * 162
        state_26 += turn * 54

class flip_b3_c4_e6(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_10
        global state_21
        global state_5
        global state_12
        global state_25
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 186
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18

class flip_b5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6

class flip_b3_b4(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        state_2 += turn * 6
        state_9 += turn * 72
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6

class flip_c3_c5(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_4
        global state_22
        global state_36
        state_2 += turn * 18
        state_10 += turn * 180
        state_20 += turn * 18
        state_38 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18

class flip_a5_a6(Flip):
    def go(self):
        global state_4
        global state_8
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        state_4 += turn * 2
        state_8 += turn * 648
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_g3_g4(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        state_2 += turn * 1458
        state_14 += turn * 72
        state_24 += turn * 486
        state_42 += turn * 18
        state_3 += turn * 1458
        state_25 += turn * 162
        state_41 += turn * 54

class flip_d2_f2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_13
        global state_22
        global state_42
        state_1 += turn * 540
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_f4_f6_f7(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_5
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_3 += turn * 486
        state_13 += turn * 1998
        state_24 += turn * 162
        state_40 += turn * 54
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_6 += turn * 486
        state_27 += turn * 6
        state_37 += turn * 486

class flip_b2_b3_b4_b6(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_5
        global state_22
        global state_34
        state_1 += turn * 6
        state_9 += turn * 564
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_e6_g6(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_14
        global state_27
        global state_39
        state_5 += turn * 1620
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_f2_f3_f5_f6(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_4
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        state_1 += turn * 486
        state_13 += turn * 672
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_4 += turn * 486
        state_25 += turn * 54
        state_39 += turn * 162
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_b2_c3_d4(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        global state_3
        global state_11
        global state_22
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 78
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54

class flip_c4_c6_c7(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_3 += turn * 18
        state_10 += turn * 1998
        state_21 += turn * 18
        state_37 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_f2_f3_f4(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        state_1 += turn * 486
        state_13 += turn * 78
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54

class flip_b2_d4(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_11
        global state_22
        state_1 += turn * 6
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 60
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54

class flip_b2_c2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        state_1 += turn * 24
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6

class flip_c4_c6(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_5
        global state_23
        global state_35
        state_3 += turn * 18
        state_10 += turn * 540
        state_21 += turn * 18
        state_37 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_c8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        state_7 += turn * 18
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18

class flip_b4_b5_b7(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        global state_6
        global state_23
        global state_33
        state_3 += turn * 6
        state_9 += turn * 1674
        state_20 += turn * 6
        state_36 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_c2_c3(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        state_1 += turn * 18
        state_10 += turn * 24
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18

class flip_d6_e5_f4_g3(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_4
        global state_12
        global state_38
        global state_3
        global state_13
        global state_40
        global state_2
        global state_14
        global state_42
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 720
        state_36 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_c6_d6_f6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_13
        global state_26
        global state_38
        state_5 += turn * 558
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_e6_f6_g6(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += turn * 2106
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_a6(Flip):
    def go(self):
        global state_5
        global state_8
        global state_21
        global state_33
        state_5 += turn * 2
        state_8 += turn * 486
        state_21 += turn * 2
        state_33 += turn * 2

class flip_d5_f5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_13
        global state_25
        global state_39
        state_4 += turn * 540
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_c2_d3_e4_g6(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_11
        global state_21
        global state_3
        global state_12
        global state_23
        global state_5
        global state_14
        global state_27
        state_1 += turn * 18
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 564
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_d4_e3_f2(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_2
        global state_12
        global state_40
        global state_1
        global state_13
        global state_42
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 702
        state_38 += turn * 54
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_b5_d5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_11
        global state_23
        global state_37
        state_4 += turn * 60
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 54

class flip_b5_c5_e5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2130
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 6
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_c2_d2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2016
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_c2_d2_e2_f2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        state_1 += turn * 720
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_b4_c4_d4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        state_3 += turn * 78
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54

class flip_g7(Flip):
    def go(self):
        global state_6
        global state_14
        global state_28
        global state_38
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b6_b7(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_5 += turn * 6
        state_9 += turn * 1944
        state_22 += turn * 6
        state_34 += turn * 6
        state_6 += turn * 6
        state_23 += turn * 6
        state_33 += turn * 6

class flip_b2_b3_b5_b6(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_4
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        state_1 += turn * 6
        state_9 += turn * 672
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_b3_d3_e3_f3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        state_2 += turn * 708
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_f5(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        state_4 += turn * 486
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162

class flip_d1_f1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        global state_13
        global state_21
        global state_43
        state_0 += turn * 540
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_c5_d6(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_5
        global state_11
        global state_24
        state_4 += turn * 18
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 72
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 18

class flip_d5_e6(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_5
        global state_12
        global state_25
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_37 += turn * 216
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18

class flip_c3_d3_e3_g3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        global state_14
        global state_24
        global state_42
        state_2 += turn * 1692
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18
        state_14 += turn * 18
        state_24 += turn * 486
        state_42 += turn * 18

class flip_d3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 18

class flip_c1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        state_0 += turn * 18
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2

class flip_d8_e8_g8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_14
        global state_29
        global state_37
        state_7 += turn * 1674
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_f2_f3_f4_f6(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        global state_5
        global state_26
        global state_38
        state_1 += turn * 486
        state_13 += turn * 564
        state_22 += turn * 486
        state_42 += turn * 6
        state_2 += turn * 486
        state_23 += turn * 486
        state_41 += turn * 18
        state_3 += turn * 486
        state_24 += turn * 162
        state_40 += turn * 54
        state_5 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_c6_d5_f3(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_4
        global state_11
        global state_37
        global state_2
        global state_13
        global state_41
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 558
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_d2_e2_g2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_14
        global state_23
        global state_43
        state_1 += turn * 1674
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_c5_c6_c7(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_4 += turn * 18
        state_10 += turn * 2106
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_c3_d4_e5_g7(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_11
        global state_22
        global state_4
        global state_12
        global state_24
        global state_6
        global state_14
        global state_28
        state_2 += turn * 18
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 1692
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_24 += turn * 54
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_b5_c4_d3_e2(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_3
        global state_10
        global state_37
        global state_2
        global state_11
        global state_39
        global state_1
        global state_12
        global state_41
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 240
        state_35 += turn * 6
        state_3 += turn * 18
        state_10 += turn * 54
        state_37 += turn * 18
        state_2 += turn * 54
        state_11 += turn * 18
        state_39 += turn * 18
        state_1 += turn * 162
        state_12 += turn * 6
        state_41 += turn * 6

class flip_d2_d3_d4_d5_d6(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        state_1 += turn * 54
        state_11 += turn * 726
        state_20 += turn * 54
        state_40 += turn * 6
        state_2 += turn * 54
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_e8_f8_g8(Flip):
    def go(self):
        global state_7
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += turn * 2106
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_c2_c4_c5_c6_c7(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_1 += turn * 18
        state_10 += turn * 2166
        state_19 += turn * 18
        state_39 += turn * 6
        state_3 += turn * 18
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18
        state_6 += turn * 18
        state_24 += turn * 6
        state_34 += turn * 18

class flip_d6_e5_g3(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_4
        global state_12
        global state_38
        global state_2
        global state_14
        global state_42
        state_5 += turn * 54
        state_11 += turn * 486
        state_24 += turn * 558
        state_36 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162
        state_2 += turn * 1458
        state_14 += turn * 18
        state_42 += turn * 18

class flip_h2_h3_h4_h5_h6(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        state_1 += turn * 4374
        state_15 += turn * 726
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_4 += turn * 4374
        state_27 += turn * 54
        state_41 += turn * 162
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486

class flip_e6(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        state_5 += turn * 162
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162

class flip_g3_g5_g6_g7(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_4
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_2 += turn * 1458
        state_14 += turn * 2124
        state_24 += turn * 486
        state_42 += turn * 18
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162
        state_5 += turn * 1458
        state_27 += turn * 18
        state_39 += turn * 486
        state_6 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_b7_c6_d5_f3(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_4
        global state_11
        global state_37
        global state_2
        global state_13
        global state_41
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 564
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_2 += turn * 486
        state_13 += turn * 18
        state_41 += turn * 18

class flip_d4_f6_g7(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_5
        global state_13
        global state_26
        global state_6
        global state_14
        global state_28
        state_3 += turn * 54
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 1998
        state_5 += turn * 486
        state_13 += turn * 486
        state_26 += turn * 18
        state_6 += turn * 1458
        state_14 += turn * 1458
        state_28 += turn * 6

class flip_a3_a4_a5_a6(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        state_2 += turn * 2
        state_8 += turn * 720
        state_18 += turn * 2
        state_36 += turn * 2
        state_3 += turn * 2
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2
        state_5 += turn * 2
        state_21 += turn * 2
        state_33 += turn * 2

class flip_d4_e4_f4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        state_3 += turn * 702
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54

class flip_b6_c6_d6_e6_f6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        state_5 += turn * 726
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_13 += turn * 486
        state_26 += turn * 18
        state_38 += turn * 486

class flip_d3_e4_g6(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_12
        global state_23
        global state_5
        global state_14
        global state_27
        state_2 += turn * 54
        state_11 += turn * 18
        state_21 += turn * 54
        state_39 += turn * 558
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_5 += turn * 1458
        state_14 += turn * 486
        state_27 += turn * 18

class flip_b4_c4_d4_e4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2184
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_11 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_b4_c3(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_2
        global state_10
        global state_38
        state_3 += turn * 6
        state_9 += turn * 54
        state_20 += turn * 24
        state_36 += turn * 6
        state_2 += turn * 18
        state_10 += turn * 18
        state_38 += turn * 18

class flip_c6_d5_e4(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 234
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54

class flip_b5_c6_d7(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_5
        global state_10
        global state_23
        global state_6
        global state_11
        global state_25
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 78
        state_5 += turn * 18
        state_10 += turn * 486
        state_23 += turn * 18
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 6

class flip_b2_c2_d2_e2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        state_1 += turn * 240
        state_9 += turn * 6
        state_18 += turn * 6
        state_38 += turn * 6
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6

class flip_c5_e5_f5_g5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += turn * 2124
        state_10 += turn * 162
        state_22 += turn * 18
        state_36 += turn * 18
        state_12 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_13 += turn * 162
        state_25 += turn * 54
        state_39 += turn * 162
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b3_b4_b6(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        global state_5
        global state_22
        global state_34
        state_2 += turn * 6
        state_9 += turn * 558
        state_19 += turn * 6
        state_37 += turn * 6
        state_3 += turn * 6
        state_20 += turn * 6
        state_36 += turn * 6
        state_5 += turn * 6
        state_22 += turn * 6
        state_34 += turn * 6

class flip_b1_c1_d1_e1_f1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        state_0 += turn * 726
        state_9 += turn * 2
        state_17 += turn * 6
        state_39 += turn * 2
        state_10 += turn * 2
        state_18 += turn * 18
        state_40 += turn * 2
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2
        state_12 += turn * 2
        state_20 += turn * 162
        state_42 += turn * 2
        state_13 += turn * 2
        state_21 += turn * 486
        state_43 += turn * 2

class flip_b5_d3_e2(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_2
        global state_11
        global state_39
        global state_1
        global state_12
        global state_41
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 222
        state_35 += turn * 6
        state_2 += turn * 54
        state_11 += turn * 18
        state_39 += turn * 18
        state_1 += turn * 162
        state_12 += turn * 6
        state_41 += turn * 6

class flip_h2_h3_h4_h6_h7(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        global state_5
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_1 += turn * 4374
        state_15 += turn * 2022
        state_24 += turn * 1458
        state_44 += turn * 6
        state_2 += turn * 4374
        state_25 += turn * 486
        state_43 += turn * 18
        state_3 += turn * 4374
        state_26 += turn * 162
        state_42 += turn * 54
        state_5 += turn * 4374
        state_28 += turn * 18
        state_40 += turn * 486
        state_6 += turn * 4374
        state_29 += turn * 6
        state_39 += turn * 1458

class flip_b4_c4_e4_f4_g4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += turn * 2130
        state_9 += turn * 54
        state_20 += turn * 6
        state_36 += turn * 6
        state_10 += turn * 54
        state_21 += turn * 18
        state_37 += turn * 18
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54
        state_13 += turn * 54
        state_24 += turn * 162
        state_40 += turn * 54
        state_14 += turn * 54
        state_25 += turn * 162
        state_41 += turn * 54

class flip_c8_d8_e8_g8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        global state_14
        global state_29
        global state_37
        state_7 += turn * 1692
        state_10 += turn * 4374
        state_25 += turn * 2
        state_33 += turn * 18
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_12 += turn * 4374
        state_27 += turn * 2
        state_35 += turn * 162
        state_14 += turn * 4374
        state_29 += turn * 2
        state_37 += turn * 1458

class flip_b3_c3_e3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        global state_12
        global state_22
        global state_40
        state_2 += turn * 186
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 6
        state_10 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_12 += turn * 18
        state_22 += turn * 162
        state_40 += turn * 18

class flip_d8_f8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        global state_13
        global state_28
        global state_36
        state_7 += turn * 540
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54
        state_13 += turn * 4374
        state_28 += turn * 2
        state_36 += turn * 486

class flip_e2_e3_e4_e5(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        state_1 += turn * 162
        state_12 += turn * 240
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162

class flip_e3_e4_e5_e7(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_6
        global state_26
        global state_36
        state_2 += turn * 162
        state_12 += turn * 1692
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_b7_c6_d5_e4(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_4
        global state_11
        global state_37
        global state_3
        global state_12
        global state_39
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 240
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_37 += turn * 54
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54

class flip_b6_c6_d6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        state_5 += turn * 78
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54

class flip_c2_d2_e2_f2_g2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += turn * 2178
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_12 += turn * 6
        state_21 += turn * 162
        state_41 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6
        state_14 += turn * 6
        state_23 += turn * 1458
        state_43 += turn * 6

class flip_g5(Flip):
    def go(self):
        global state_4
        global state_14
        global state_26
        global state_40
        state_4 += turn * 1458
        state_14 += turn * 162
        state_26 += turn * 54
        state_40 += turn * 162

class flip_c7_d7_f7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        global state_13
        global state_27
        global state_37
        state_6 += turn * 558
        state_10 += turn * 1458
        state_24 += turn * 6
        state_34 += turn * 18
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486

class flip_f3(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        state_2 += turn * 486
        state_13 += turn * 18
        state_23 += turn * 486
        state_41 += turn * 18

class flip_b6_d6_e6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        state_5 += turn * 222
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162

class flip_e2_e3_e4_e5_e6(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        state_1 += turn * 162
        state_12 += turn * 726
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162

class flip_e2_e3_e5_e6_e7(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_1 += turn * 162
        state_12 += turn * 2130
        state_21 += turn * 162
        state_41 += turn * 6
        state_2 += turn * 162
        state_22 += turn * 162
        state_40 += turn * 18
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_b6_d4_e3(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_3
        global state_11
        global state_38
        global state_2
        global state_12
        global state_40
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 222
        state_34 += turn * 6
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18

class flip_d1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        state_0 += turn * 54
        state_11 += turn * 2
        state_19 += turn * 54
        state_41 += turn * 2

class flip_b8_d8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_11
        global state_26
        global state_34
        state_7 += turn * 60
        state_9 += turn * 4374
        state_24 += turn * 2
        state_32 += turn * 6
        state_11 += turn * 4374
        state_26 += turn * 2
        state_34 += turn * 54

class flip_c7_d6_f4(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_5
        global state_11
        global state_36
        global state_3
        global state_13
        global state_40
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 186
        state_34 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_36 += turn * 54
        state_3 += turn * 486
        state_13 += turn * 54
        state_40 += turn * 54

class flip_b6_d4_e3_f2(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_3
        global state_11
        global state_38
        global state_2
        global state_12
        global state_40
        global state_1
        global state_13
        global state_42
        state_5 += turn * 6
        state_9 += turn * 486
        state_22 += turn * 708
        state_34 += turn * 6
        state_3 += turn * 54
        state_11 += turn * 54
        state_38 += turn * 54
        state_2 += turn * 162
        state_12 += turn * 18
        state_40 += turn * 18
        state_1 += turn * 486
        state_13 += turn * 6
        state_42 += turn * 6

class flip_d3_d4_d5_d6(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        state_2 += turn * 54
        state_11 += turn * 720
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54

class flip_c4_c5_c6(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        state_3 += turn * 18
        state_10 += turn * 702
        state_21 += turn * 18
        state_37 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18
        state_5 += turn * 18
        state_23 += turn * 18
        state_35 += turn * 18

class flip_g4_g5(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        state_3 += turn * 1458
        state_14 += turn * 216
        state_25 += turn * 162
        state_41 += turn * 54
        state_4 += turn * 1458
        state_26 += turn * 54
        state_40 += turn * 162

class flip_b2_b3_b5(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        global state_4
        global state_21
        global state_35
        state_1 += turn * 6
        state_9 += turn * 186
        state_18 += turn * 6
        state_38 += turn * 6
        state_2 += turn * 6
        state_19 += turn * 6
        state_37 += turn * 6
        state_4 += turn * 6
        state_21 += turn * 6
        state_35 += turn * 6

class flip_d7_f7_g7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += turn * 1998
        state_11 += turn * 1458
        state_25 += turn * 6
        state_35 += turn * 54
        state_13 += turn * 1458
        state_27 += turn * 6
        state_37 += turn * 486
        state_14 += turn * 1458
        state_28 += turn * 6
        state_38 += turn * 1458

class flip_d2_d4_d5_d6_d7(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_3
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_1 += turn * 54
        state_11 += turn * 2166
        state_20 += turn * 54
        state_40 += turn * 6
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_4 += turn * 54
        state_23 += turn * 54
        state_37 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_b3_c4_d5_f7(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_10
        global state_21
        global state_4
        global state_11
        global state_23
        global state_6
        global state_13
        global state_27
        state_2 += turn * 6
        state_9 += turn * 18
        state_19 += turn * 6
        state_37 += turn * 564
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 18
        state_4 += turn * 54
        state_11 += turn * 162
        state_23 += turn * 54
        state_6 += turn * 486
        state_13 += turn * 1458
        state_27 += turn * 6

class flip_c2_c3_c5(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        global state_4
        global state_22
        global state_36
        state_1 += turn * 18
        state_10 += turn * 186
        state_19 += turn * 18
        state_39 += turn * 6
        state_2 += turn * 18
        state_20 += turn * 18
        state_38 += turn * 18
        state_4 += turn * 18
        state_22 += turn * 18
        state_36 += turn * 18

class flip_d2_e3(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_12
        global state_22
        state_1 += turn * 54
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 24
        state_2 += turn * 162
        state_12 += turn * 18
        state_22 += turn * 162

class flip_b5_d7(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_6
        global state_11
        global state_25
        state_4 += turn * 6
        state_9 += turn * 162
        state_21 += turn * 6
        state_35 += turn * 60
        state_6 += turn * 54
        state_11 += turn * 1458
        state_25 += turn * 6

class flip_c4_e2(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_1
        global state_12
        global state_41
        state_3 += turn * 18
        state_10 += turn * 54
        state_21 += turn * 180
        state_37 += turn * 18
        state_1 += turn * 162
        state_12 += turn * 6
        state_41 += turn * 6

class flip_e4(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        state_3 += turn * 162
        state_12 += turn * 54
        state_23 += turn * 162
        state_39 += turn * 54

class flip_c2_d2_f2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        global state_13
        global state_22
        global state_42
        state_1 += turn * 558
        state_10 += turn * 6
        state_19 += turn * 18
        state_39 += turn * 6
        state_11 += turn * 6
        state_20 += turn * 54
        state_40 += turn * 6
        state_13 += turn * 6
        state_22 += turn * 486
        state_42 += turn * 6

class flip_d3_d4_d6_d7(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        global state_5
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_2 += turn * 54
        state_11 += turn * 2016
        state_21 += turn * 54
        state_39 += turn * 18
        state_3 += turn * 54
        state_22 += turn * 54
        state_38 += turn * 54
        state_5 += turn * 54
        state_24 += turn * 18
        state_36 += turn * 54
        state_6 += turn * 54
        state_25 += turn * 6
        state_35 += turn * 54

class flip_a4_a5(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        state_3 += turn * 2
        state_8 += turn * 216
        state_19 += turn * 2
        state_35 += turn * 2
        state_4 += turn * 2
        state_20 += turn * 2
        state_34 += turn * 2

class flip_e3_e4_e6_e7(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_2 += turn * 162
        state_12 += turn * 2016
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_e3_e4_e5_e6_e7(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_2 += turn * 162
        state_12 += turn * 2178
        state_22 += turn * 162
        state_40 += turn * 18
        state_3 += turn * 162
        state_23 += turn * 162
        state_39 += turn * 54
        state_4 += turn * 162
        state_24 += turn * 54
        state_38 += turn * 162
        state_5 += turn * 162
        state_25 += turn * 18
        state_37 += turn * 162
        state_6 += turn * 162
        state_26 += turn * 6
        state_36 += turn * 162

class flip_c7_d6_e5(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_5
        global state_11
        global state_36
        global state_4
        global state_12
        global state_38
        state_6 += turn * 18
        state_10 += turn * 1458
        state_24 += turn * 78
        state_34 += turn * 18
        state_5 += turn * 54
        state_11 += turn * 486
        state_36 += turn * 54
        state_4 += turn * 162
        state_12 += turn * 162
        state_38 += turn * 162

class flip_b6_c6_d6_e6_g6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        global state_14
        global state_27
        global state_39
        state_5 += turn * 1698
        state_9 += turn * 486
        state_22 += turn * 6
        state_34 += turn * 6
        state_10 += turn * 486
        state_23 += turn * 18
        state_35 += turn * 18
        state_11 += turn * 486
        state_24 += turn * 18
        state_36 += turn * 54
        state_12 += turn * 486
        state_25 += turn * 18
        state_37 += turn * 162
        state_14 += turn * 486
        state_27 += turn * 18
        state_39 += turn * 486

class flip_b7_c6_e4(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        global state_3
        global state_12
        global state_39
        state_6 += turn * 6
        state_9 += turn * 1458
        state_23 += turn * 186
        state_33 += turn * 6
        state_5 += turn * 18
        state_10 += turn * 486
        state_35 += turn * 18
        state_3 += turn * 162
        state_12 += turn * 54
        state_39 += turn * 54

line_flip_func = {}
line_flip_func[0] = flip_()
line_flip_func[1] = flip_b1()
line_flip_func[2] = flip_c1()
line_flip_func[3] = flip_b1_c1()
line_flip_func[4] = flip_b1_c1()
line_flip_func[5] = flip_d1()
line_flip_func[6] = flip_b1_d1()
line_flip_func[7] = flip_c1_d1()
line_flip_func[8] = flip_b1_c1_d1()
line_flip_func[9] = flip_b1_c1_d1()
line_flip_func[10] = flip_c1_d1()
line_flip_func[11] = flip_e1()
line_flip_func[12] = flip_c1_e1()
line_flip_func[13] = flip_b1_c1_e1()
line_flip_func[14] = flip_d1_e1()
line_flip_func[15] = flip_b1_d1_e1()
line_flip_func[16] = flip_c1_d1_e1()
line_flip_func[17] = flip_b1_c1_d1_e1()
line_flip_func[18] = flip_b1_c1_d1_e1()
line_flip_func[19] = flip_c1_d1_e1()
line_flip_func[20] = flip_d1_e1()
line_flip_func[21] = flip_f1()
line_flip_func[22] = flip_d1_f1()
line_flip_func[23] = flip_c1_d1_f1()
line_flip_func[24] = flip_b1_c1_d1_f1()
line_flip_func[25] = flip_e1_f1()
line_flip_func[26] = flip_c1_e1_f1()
line_flip_func[27] = flip_b1_c1_e1_f1()
line_flip_func[28] = flip_d1_e1_f1()
line_flip_func[29] = flip_b1_d1_e1_f1()
line_flip_func[30] = flip_c1_d1_e1_f1()
line_flip_func[31] = flip_b1_c1_d1_e1_f1()
line_flip_func[32] = flip_b1_c1_d1_e1_f1()
line_flip_func[33] = flip_c1_d1_e1_f1()
line_flip_func[34] = flip_d1_e1_f1()
line_flip_func[35] = flip_e1_f1()
line_flip_func[36] = flip_g1()
line_flip_func[37] = flip_e1_g1()
line_flip_func[38] = flip_d1_e1_g1()
line_flip_func[39] = flip_c1_d1_e1_g1()
line_flip_func[40] = flip_b1_c1_d1_e1_g1()
line_flip_func[41] = flip_f1_g1()
line_flip_func[42] = flip_d1_f1_g1()
line_flip_func[43] = flip_c1_d1_f1_g1()
line_flip_func[44] = flip_b1_c1_d1_f1_g1()
line_flip_func[45] = flip_e1_f1_g1()
line_flip_func[46] = flip_c1_e1_f1_g1()
line_flip_func[47] = flip_b1_c1_e1_f1_g1()
line_flip_func[48] = flip_d1_e1_f1_g1()
line_flip_func[49] = flip_b1_d1_e1_f1_g1()
line_flip_func[50] = flip_c1_d1_e1_f1_g1()
line_flip_func[51] = flip_b1_c1_d1_e1_f1_g1()
line_flip_func[52] = flip_b1_c1_d1_e1_f1_g1()
line_flip_func[53] = flip_c1_d1_e1_f1_g1()
line_flip_func[54] = flip_d1_e1_f1_g1()
line_flip_func[55] = flip_e1_f1_g1()
line_flip_func[56] = flip_f1_g1()
line_flip_func[64] = flip_()
line_flip_func[65] = flip_b2()
line_flip_func[66] = flip_c2()
line_flip_func[67] = flip_b2_c2()
line_flip_func[68] = flip_b2_c2()
line_flip_func[69] = flip_d2()
line_flip_func[70] = flip_b2_d2()
line_flip_func[71] = flip_c2_d2()
line_flip_func[72] = flip_b2_c2_d2()
line_flip_func[73] = flip_b2_c2_d2()
line_flip_func[74] = flip_c2_d2()
line_flip_func[75] = flip_e2()
line_flip_func[76] = flip_c2_e2()
line_flip_func[77] = flip_b2_c2_e2()
line_flip_func[78] = flip_d2_e2()
line_flip_func[79] = flip_b2_d2_e2()
line_flip_func[80] = flip_c2_d2_e2()
line_flip_func[81] = flip_b2_c2_d2_e2()
line_flip_func[82] = flip_b2_c2_d2_e2()
line_flip_func[83] = flip_c2_d2_e2()
line_flip_func[84] = flip_d2_e2()
line_flip_func[85] = flip_f2()
line_flip_func[86] = flip_d2_f2()
line_flip_func[87] = flip_c2_d2_f2()
line_flip_func[88] = flip_b2_c2_d2_f2()
line_flip_func[89] = flip_e2_f2()
line_flip_func[90] = flip_c2_e2_f2()
line_flip_func[91] = flip_b2_c2_e2_f2()
line_flip_func[92] = flip_d2_e2_f2()
line_flip_func[93] = flip_b2_d2_e2_f2()
line_flip_func[94] = flip_c2_d2_e2_f2()
line_flip_func[95] = flip_b2_c2_d2_e2_f2()
line_flip_func[96] = flip_b2_c2_d2_e2_f2()
line_flip_func[97] = flip_c2_d2_e2_f2()
line_flip_func[98] = flip_d2_e2_f2()
line_flip_func[99] = flip_e2_f2()
line_flip_func[100] = flip_g2()
line_flip_func[101] = flip_e2_g2()
line_flip_func[102] = flip_d2_e2_g2()
line_flip_func[103] = flip_c2_d2_e2_g2()
line_flip_func[104] = flip_b2_c2_d2_e2_g2()
line_flip_func[105] = flip_f2_g2()
line_flip_func[106] = flip_d2_f2_g2()
line_flip_func[107] = flip_c2_d2_f2_g2()
line_flip_func[108] = flip_b2_c2_d2_f2_g2()
line_flip_func[109] = flip_e2_f2_g2()
line_flip_func[110] = flip_c2_e2_f2_g2()
line_flip_func[111] = flip_b2_c2_e2_f2_g2()
line_flip_func[112] = flip_d2_e2_f2_g2()
line_flip_func[113] = flip_b2_d2_e2_f2_g2()
line_flip_func[114] = flip_c2_d2_e2_f2_g2()
line_flip_func[115] = flip_b2_c2_d2_e2_f2_g2()
line_flip_func[116] = flip_b2_c2_d2_e2_f2_g2()
line_flip_func[117] = flip_c2_d2_e2_f2_g2()
line_flip_func[118] = flip_d2_e2_f2_g2()
line_flip_func[119] = flip_e2_f2_g2()
line_flip_func[120] = flip_f2_g2()
line_flip_func[128] = flip_()
line_flip_func[129] = flip_b3()
line_flip_func[130] = flip_c3()
line_flip_func[131] = flip_b3_c3()
line_flip_func[132] = flip_b3_c3()
line_flip_func[133] = flip_d3()
line_flip_func[134] = flip_b3_d3()
line_flip_func[135] = flip_c3_d3()
line_flip_func[136] = flip_b3_c3_d3()
line_flip_func[137] = flip_b3_c3_d3()
line_flip_func[138] = flip_c3_d3()
line_flip_func[139] = flip_e3()
line_flip_func[140] = flip_c3_e3()
line_flip_func[141] = flip_b3_c3_e3()
line_flip_func[142] = flip_d3_e3()
line_flip_func[143] = flip_b3_d3_e3()
line_flip_func[144] = flip_c3_d3_e3()
line_flip_func[145] = flip_b3_c3_d3_e3()
line_flip_func[146] = flip_b3_c3_d3_e3()
line_flip_func[147] = flip_c3_d3_e3()
line_flip_func[148] = flip_d3_e3()
line_flip_func[149] = flip_f3()
line_flip_func[150] = flip_d3_f3()
line_flip_func[151] = flip_c3_d3_f3()
line_flip_func[152] = flip_b3_c3_d3_f3()
line_flip_func[153] = flip_e3_f3()
line_flip_func[154] = flip_c3_e3_f3()
line_flip_func[155] = flip_b3_c3_e3_f3()
line_flip_func[156] = flip_d3_e3_f3()
line_flip_func[157] = flip_b3_d3_e3_f3()
line_flip_func[158] = flip_c3_d3_e3_f3()
line_flip_func[159] = flip_b3_c3_d3_e3_f3()
line_flip_func[160] = flip_b3_c3_d3_e3_f3()
line_flip_func[161] = flip_c3_d3_e3_f3()
line_flip_func[162] = flip_d3_e3_f3()
line_flip_func[163] = flip_e3_f3()
line_flip_func[164] = flip_g3()
line_flip_func[165] = flip_e3_g3()
line_flip_func[166] = flip_d3_e3_g3()
line_flip_func[167] = flip_c3_d3_e3_g3()
line_flip_func[168] = flip_b3_c3_d3_e3_g3()
line_flip_func[169] = flip_f3_g3()
line_flip_func[170] = flip_d3_f3_g3()
line_flip_func[171] = flip_c3_d3_f3_g3()
line_flip_func[172] = flip_b3_c3_d3_f3_g3()
line_flip_func[173] = flip_e3_f3_g3()
line_flip_func[174] = flip_c3_e3_f3_g3()
line_flip_func[175] = flip_b3_c3_e3_f3_g3()
line_flip_func[176] = flip_d3_e3_f3_g3()
line_flip_func[177] = flip_b3_d3_e3_f3_g3()
line_flip_func[178] = flip_c3_d3_e3_f3_g3()
line_flip_func[179] = flip_b3_c3_d3_e3_f3_g3()
line_flip_func[180] = flip_b3_c3_d3_e3_f3_g3()
line_flip_func[181] = flip_c3_d3_e3_f3_g3()
line_flip_func[182] = flip_d3_e3_f3_g3()
line_flip_func[183] = flip_e3_f3_g3()
line_flip_func[184] = flip_f3_g3()
line_flip_func[192] = flip_()
line_flip_func[193] = flip_b4()
line_flip_func[194] = flip_c4()
line_flip_func[195] = flip_b4_c4()
line_flip_func[196] = flip_b4_c4()
line_flip_func[197] = flip_d4()
line_flip_func[198] = flip_b4_d4()
line_flip_func[199] = flip_c4_d4()
line_flip_func[200] = flip_b4_c4_d4()
line_flip_func[201] = flip_b4_c4_d4()
line_flip_func[202] = flip_c4_d4()
line_flip_func[203] = flip_e4()
line_flip_func[204] = flip_c4_e4()
line_flip_func[205] = flip_b4_c4_e4()
line_flip_func[206] = flip_d4_e4()
line_flip_func[207] = flip_b4_d4_e4()
line_flip_func[208] = flip_c4_d4_e4()
line_flip_func[209] = flip_b4_c4_d4_e4()
line_flip_func[210] = flip_b4_c4_d4_e4()
line_flip_func[211] = flip_c4_d4_e4()
line_flip_func[212] = flip_d4_e4()
line_flip_func[213] = flip_f4()
line_flip_func[214] = flip_d4_f4()
line_flip_func[215] = flip_c4_d4_f4()
line_flip_func[216] = flip_b4_c4_d4_f4()
line_flip_func[217] = flip_e4_f4()
line_flip_func[218] = flip_c4_e4_f4()
line_flip_func[219] = flip_b4_c4_e4_f4()
line_flip_func[220] = flip_d4_e4_f4()
line_flip_func[221] = flip_b4_d4_e4_f4()
line_flip_func[222] = flip_c4_d4_e4_f4()
line_flip_func[223] = flip_b4_c4_d4_e4_f4()
line_flip_func[224] = flip_b4_c4_d4_e4_f4()
line_flip_func[225] = flip_c4_d4_e4_f4()
line_flip_func[226] = flip_d4_e4_f4()
line_flip_func[227] = flip_e4_f4()
line_flip_func[228] = flip_g4()
line_flip_func[229] = flip_e4_g4()
line_flip_func[230] = flip_d4_e4_g4()
line_flip_func[231] = flip_c4_d4_e4_g4()
line_flip_func[232] = flip_b4_c4_d4_e4_g4()
line_flip_func[233] = flip_f4_g4()
line_flip_func[234] = flip_d4_f4_g4()
line_flip_func[235] = flip_c4_d4_f4_g4()
line_flip_func[236] = flip_b4_c4_d4_f4_g4()
line_flip_func[237] = flip_e4_f4_g4()
line_flip_func[238] = flip_c4_e4_f4_g4()
line_flip_func[239] = flip_b4_c4_e4_f4_g4()
line_flip_func[240] = flip_d4_e4_f4_g4()
line_flip_func[241] = flip_b4_d4_e4_f4_g4()
line_flip_func[242] = flip_c4_d4_e4_f4_g4()
line_flip_func[243] = flip_b4_c4_d4_e4_f4_g4()
line_flip_func[244] = flip_b4_c4_d4_e4_f4_g4()
line_flip_func[245] = flip_c4_d4_e4_f4_g4()
line_flip_func[246] = flip_d4_e4_f4_g4()
line_flip_func[247] = flip_e4_f4_g4()
line_flip_func[248] = flip_f4_g4()
line_flip_func[256] = flip_()
line_flip_func[257] = flip_b5()
line_flip_func[258] = flip_c5()
line_flip_func[259] = flip_b5_c5()
line_flip_func[260] = flip_b5_c5()
line_flip_func[261] = flip_d5()
line_flip_func[262] = flip_b5_d5()
line_flip_func[263] = flip_c5_d5()
line_flip_func[264] = flip_b5_c5_d5()
line_flip_func[265] = flip_b5_c5_d5()
line_flip_func[266] = flip_c5_d5()
line_flip_func[267] = flip_e5()
line_flip_func[268] = flip_c5_e5()
line_flip_func[269] = flip_b5_c5_e5()
line_flip_func[270] = flip_d5_e5()
line_flip_func[271] = flip_b5_d5_e5()
line_flip_func[272] = flip_c5_d5_e5()
line_flip_func[273] = flip_b5_c5_d5_e5()
line_flip_func[274] = flip_b5_c5_d5_e5()
line_flip_func[275] = flip_c5_d5_e5()
line_flip_func[276] = flip_d5_e5()
line_flip_func[277] = flip_f5()
line_flip_func[278] = flip_d5_f5()
line_flip_func[279] = flip_c5_d5_f5()
line_flip_func[280] = flip_b5_c5_d5_f5()
line_flip_func[281] = flip_e5_f5()
line_flip_func[282] = flip_c5_e5_f5()
line_flip_func[283] = flip_b5_c5_e5_f5()
line_flip_func[284] = flip_d5_e5_f5()
line_flip_func[285] = flip_b5_d5_e5_f5()
line_flip_func[286] = flip_c5_d5_e5_f5()
line_flip_func[287] = flip_b5_c5_d5_e5_f5()
line_flip_func[288] = flip_b5_c5_d5_e5_f5()
line_flip_func[289] = flip_c5_d5_e5_f5()
line_flip_func[290] = flip_d5_e5_f5()
line_flip_func[291] = flip_e5_f5()
line_flip_func[292] = flip_g5()
line_flip_func[293] = flip_e5_g5()
line_flip_func[294] = flip_d5_e5_g5()
line_flip_func[295] = flip_c5_d5_e5_g5()
line_flip_func[296] = flip_b5_c5_d5_e5_g5()
line_flip_func[297] = flip_f5_g5()
line_flip_func[298] = flip_d5_f5_g5()
line_flip_func[299] = flip_c5_d5_f5_g5()
line_flip_func[300] = flip_b5_c5_d5_f5_g5()
line_flip_func[301] = flip_e5_f5_g5()
line_flip_func[302] = flip_c5_e5_f5_g5()
line_flip_func[303] = flip_b5_c5_e5_f5_g5()
line_flip_func[304] = flip_d5_e5_f5_g5()
line_flip_func[305] = flip_b5_d5_e5_f5_g5()
line_flip_func[306] = flip_c5_d5_e5_f5_g5()
line_flip_func[307] = flip_b5_c5_d5_e5_f5_g5()
line_flip_func[308] = flip_b5_c5_d5_e5_f5_g5()
line_flip_func[309] = flip_c5_d5_e5_f5_g5()
line_flip_func[310] = flip_d5_e5_f5_g5()
line_flip_func[311] = flip_e5_f5_g5()
line_flip_func[312] = flip_f5_g5()
line_flip_func[320] = flip_()
line_flip_func[321] = flip_b6()
line_flip_func[322] = flip_c6()
line_flip_func[323] = flip_b6_c6()
line_flip_func[324] = flip_b6_c6()
line_flip_func[325] = flip_d6()
line_flip_func[326] = flip_b6_d6()
line_flip_func[327] = flip_c6_d6()
line_flip_func[328] = flip_b6_c6_d6()
line_flip_func[329] = flip_b6_c6_d6()
line_flip_func[330] = flip_c6_d6()
line_flip_func[331] = flip_e6()
line_flip_func[332] = flip_c6_e6()
line_flip_func[333] = flip_b6_c6_e6()
line_flip_func[334] = flip_d6_e6()
line_flip_func[335] = flip_b6_d6_e6()
line_flip_func[336] = flip_c6_d6_e6()
line_flip_func[337] = flip_b6_c6_d6_e6()
line_flip_func[338] = flip_b6_c6_d6_e6()
line_flip_func[339] = flip_c6_d6_e6()
line_flip_func[340] = flip_d6_e6()
line_flip_func[341] = flip_f6()
line_flip_func[342] = flip_d6_f6()
line_flip_func[343] = flip_c6_d6_f6()
line_flip_func[344] = flip_b6_c6_d6_f6()
line_flip_func[345] = flip_e6_f6()
line_flip_func[346] = flip_c6_e6_f6()
line_flip_func[347] = flip_b6_c6_e6_f6()
line_flip_func[348] = flip_d6_e6_f6()
line_flip_func[349] = flip_b6_d6_e6_f6()
line_flip_func[350] = flip_c6_d6_e6_f6()
line_flip_func[351] = flip_b6_c6_d6_e6_f6()
line_flip_func[352] = flip_b6_c6_d6_e6_f6()
line_flip_func[353] = flip_c6_d6_e6_f6()
line_flip_func[354] = flip_d6_e6_f6()
line_flip_func[355] = flip_e6_f6()
line_flip_func[356] = flip_g6()
line_flip_func[357] = flip_e6_g6()
line_flip_func[358] = flip_d6_e6_g6()
line_flip_func[359] = flip_c6_d6_e6_g6()
line_flip_func[360] = flip_b6_c6_d6_e6_g6()
line_flip_func[361] = flip_f6_g6()
line_flip_func[362] = flip_d6_f6_g6()
line_flip_func[363] = flip_c6_d6_f6_g6()
line_flip_func[364] = flip_b6_c6_d6_f6_g6()
line_flip_func[365] = flip_e6_f6_g6()
line_flip_func[366] = flip_c6_e6_f6_g6()
line_flip_func[367] = flip_b6_c6_e6_f6_g6()
line_flip_func[368] = flip_d6_e6_f6_g6()
line_flip_func[369] = flip_b6_d6_e6_f6_g6()
line_flip_func[370] = flip_c6_d6_e6_f6_g6()
line_flip_func[371] = flip_b6_c6_d6_e6_f6_g6()
line_flip_func[372] = flip_b6_c6_d6_e6_f6_g6()
line_flip_func[373] = flip_c6_d6_e6_f6_g6()
line_flip_func[374] = flip_d6_e6_f6_g6()
line_flip_func[375] = flip_e6_f6_g6()
line_flip_func[376] = flip_f6_g6()
line_flip_func[384] = flip_()
line_flip_func[385] = flip_b7()
line_flip_func[386] = flip_c7()
line_flip_func[387] = flip_b7_c7()
line_flip_func[388] = flip_b7_c7()
line_flip_func[389] = flip_d7()
line_flip_func[390] = flip_b7_d7()
line_flip_func[391] = flip_c7_d7()
line_flip_func[392] = flip_b7_c7_d7()
line_flip_func[393] = flip_b7_c7_d7()
line_flip_func[394] = flip_c7_d7()
line_flip_func[395] = flip_e7()
line_flip_func[396] = flip_c7_e7()
line_flip_func[397] = flip_b7_c7_e7()
line_flip_func[398] = flip_d7_e7()
line_flip_func[399] = flip_b7_d7_e7()
line_flip_func[400] = flip_c7_d7_e7()
line_flip_func[401] = flip_b7_c7_d7_e7()
line_flip_func[402] = flip_b7_c7_d7_e7()
line_flip_func[403] = flip_c7_d7_e7()
line_flip_func[404] = flip_d7_e7()
line_flip_func[405] = flip_f7()
line_flip_func[406] = flip_d7_f7()
line_flip_func[407] = flip_c7_d7_f7()
line_flip_func[408] = flip_b7_c7_d7_f7()
line_flip_func[409] = flip_e7_f7()
line_flip_func[410] = flip_c7_e7_f7()
line_flip_func[411] = flip_b7_c7_e7_f7()
line_flip_func[412] = flip_d7_e7_f7()
line_flip_func[413] = flip_b7_d7_e7_f7()
line_flip_func[414] = flip_c7_d7_e7_f7()
line_flip_func[415] = flip_b7_c7_d7_e7_f7()
line_flip_func[416] = flip_b7_c7_d7_e7_f7()
line_flip_func[417] = flip_c7_d7_e7_f7()
line_flip_func[418] = flip_d7_e7_f7()
line_flip_func[419] = flip_e7_f7()
line_flip_func[420] = flip_g7()
line_flip_func[421] = flip_e7_g7()
line_flip_func[422] = flip_d7_e7_g7()
line_flip_func[423] = flip_c7_d7_e7_g7()
line_flip_func[424] = flip_b7_c7_d7_e7_g7()
line_flip_func[425] = flip_f7_g7()
line_flip_func[426] = flip_d7_f7_g7()
line_flip_func[427] = flip_c7_d7_f7_g7()
line_flip_func[428] = flip_b7_c7_d7_f7_g7()
line_flip_func[429] = flip_e7_f7_g7()
line_flip_func[430] = flip_c7_e7_f7_g7()
line_flip_func[431] = flip_b7_c7_e7_f7_g7()
line_flip_func[432] = flip_d7_e7_f7_g7()
line_flip_func[433] = flip_b7_d7_e7_f7_g7()
line_flip_func[434] = flip_c7_d7_e7_f7_g7()
line_flip_func[435] = flip_b7_c7_d7_e7_f7_g7()
line_flip_func[436] = flip_b7_c7_d7_e7_f7_g7()
line_flip_func[437] = flip_c7_d7_e7_f7_g7()
line_flip_func[438] = flip_d7_e7_f7_g7()
line_flip_func[439] = flip_e7_f7_g7()
line_flip_func[440] = flip_f7_g7()
line_flip_func[448] = flip_()
line_flip_func[449] = flip_b8()
line_flip_func[450] = flip_c8()
line_flip_func[451] = flip_b8_c8()
line_flip_func[452] = flip_b8_c8()
line_flip_func[453] = flip_d8()
line_flip_func[454] = flip_b8_d8()
line_flip_func[455] = flip_c8_d8()
line_flip_func[456] = flip_b8_c8_d8()
line_flip_func[457] = flip_b8_c8_d8()
line_flip_func[458] = flip_c8_d8()
line_flip_func[459] = flip_e8()
line_flip_func[460] = flip_c8_e8()
line_flip_func[461] = flip_b8_c8_e8()
line_flip_func[462] = flip_d8_e8()
line_flip_func[463] = flip_b8_d8_e8()
line_flip_func[464] = flip_c8_d8_e8()
line_flip_func[465] = flip_b8_c8_d8_e8()
line_flip_func[466] = flip_b8_c8_d8_e8()
line_flip_func[467] = flip_c8_d8_e8()
line_flip_func[468] = flip_d8_e8()
line_flip_func[469] = flip_f8()
line_flip_func[470] = flip_d8_f8()
line_flip_func[471] = flip_c8_d8_f8()
line_flip_func[472] = flip_b8_c8_d8_f8()
line_flip_func[473] = flip_e8_f8()
line_flip_func[474] = flip_c8_e8_f8()
line_flip_func[475] = flip_b8_c8_e8_f8()
line_flip_func[476] = flip_d8_e8_f8()
line_flip_func[477] = flip_b8_d8_e8_f8()
line_flip_func[478] = flip_c8_d8_e8_f8()
line_flip_func[479] = flip_b8_c8_d8_e8_f8()
line_flip_func[480] = flip_b8_c8_d8_e8_f8()
line_flip_func[481] = flip_c8_d8_e8_f8()
line_flip_func[482] = flip_d8_e8_f8()
line_flip_func[483] = flip_e8_f8()
line_flip_func[484] = flip_g8()
line_flip_func[485] = flip_e8_g8()
line_flip_func[486] = flip_d8_e8_g8()
line_flip_func[487] = flip_c8_d8_e8_g8()
line_flip_func[488] = flip_b8_c8_d8_e8_g8()
line_flip_func[489] = flip_f8_g8()
line_flip_func[490] = flip_d8_f8_g8()
line_flip_func[491] = flip_c8_d8_f8_g8()
line_flip_func[492] = flip_b8_c8_d8_f8_g8()
line_flip_func[493] = flip_e8_f8_g8()
line_flip_func[494] = flip_c8_e8_f8_g8()
line_flip_func[495] = flip_b8_c8_e8_f8_g8()
line_flip_func[496] = flip_d8_e8_f8_g8()
line_flip_func[497] = flip_b8_d8_e8_f8_g8()
line_flip_func[498] = flip_c8_d8_e8_f8_g8()
line_flip_func[499] = flip_b8_c8_d8_e8_f8_g8()
line_flip_func[500] = flip_b8_c8_d8_e8_f8_g8()
line_flip_func[501] = flip_c8_d8_e8_f8_g8()
line_flip_func[502] = flip_d8_e8_f8_g8()
line_flip_func[503] = flip_e8_f8_g8()
line_flip_func[504] = flip_f8_g8()
line_flip_func[512] = flip_()
line_flip_func[513] = flip_a2()
line_flip_func[514] = flip_a3()
line_flip_func[515] = flip_a2_a3()
line_flip_func[516] = flip_a2_a3()
line_flip_func[517] = flip_a4()
line_flip_func[518] = flip_a2_a4()
line_flip_func[519] = flip_a3_a4()
line_flip_func[520] = flip_a2_a3_a4()
line_flip_func[521] = flip_a2_a3_a4()
line_flip_func[522] = flip_a3_a4()
line_flip_func[523] = flip_a5()
line_flip_func[524] = flip_a3_a5()
line_flip_func[525] = flip_a2_a3_a5()
line_flip_func[526] = flip_a4_a5()
line_flip_func[527] = flip_a2_a4_a5()
line_flip_func[528] = flip_a3_a4_a5()
line_flip_func[529] = flip_a2_a3_a4_a5()
line_flip_func[530] = flip_a2_a3_a4_a5()
line_flip_func[531] = flip_a3_a4_a5()
line_flip_func[532] = flip_a4_a5()
line_flip_func[533] = flip_a6()
line_flip_func[534] = flip_a4_a6()
line_flip_func[535] = flip_a3_a4_a6()
line_flip_func[536] = flip_a2_a3_a4_a6()
line_flip_func[537] = flip_a5_a6()
line_flip_func[538] = flip_a3_a5_a6()
line_flip_func[539] = flip_a2_a3_a5_a6()
line_flip_func[540] = flip_a4_a5_a6()
line_flip_func[541] = flip_a2_a4_a5_a6()
line_flip_func[542] = flip_a3_a4_a5_a6()
line_flip_func[543] = flip_a2_a3_a4_a5_a6()
line_flip_func[544] = flip_a2_a3_a4_a5_a6()
line_flip_func[545] = flip_a3_a4_a5_a6()
line_flip_func[546] = flip_a4_a5_a6()
line_flip_func[547] = flip_a5_a6()
line_flip_func[548] = flip_a7()
line_flip_func[549] = flip_a5_a7()
line_flip_func[550] = flip_a4_a5_a7()
line_flip_func[551] = flip_a3_a4_a5_a7()
line_flip_func[552] = flip_a2_a3_a4_a5_a7()
line_flip_func[553] = flip_a6_a7()
line_flip_func[554] = flip_a4_a6_a7()
line_flip_func[555] = flip_a3_a4_a6_a7()
line_flip_func[556] = flip_a2_a3_a4_a6_a7()
line_flip_func[557] = flip_a5_a6_a7()
line_flip_func[558] = flip_a3_a5_a6_a7()
line_flip_func[559] = flip_a2_a3_a5_a6_a7()
line_flip_func[560] = flip_a4_a5_a6_a7()
line_flip_func[561] = flip_a2_a4_a5_a6_a7()
line_flip_func[562] = flip_a3_a4_a5_a6_a7()
line_flip_func[563] = flip_a2_a3_a4_a5_a6_a7()
line_flip_func[564] = flip_a2_a3_a4_a5_a6_a7()
line_flip_func[565] = flip_a3_a4_a5_a6_a7()
line_flip_func[566] = flip_a4_a5_a6_a7()
line_flip_func[567] = flip_a5_a6_a7()
line_flip_func[568] = flip_a6_a7()
line_flip_func[576] = flip_()
line_flip_func[577] = flip_b2()
line_flip_func[578] = flip_b3()
line_flip_func[579] = flip_b2_b3()
line_flip_func[580] = flip_b2_b3()
line_flip_func[581] = flip_b4()
line_flip_func[582] = flip_b2_b4()
line_flip_func[583] = flip_b3_b4()
line_flip_func[584] = flip_b2_b3_b4()
line_flip_func[585] = flip_b2_b3_b4()
line_flip_func[586] = flip_b3_b4()
line_flip_func[587] = flip_b5()
line_flip_func[588] = flip_b3_b5()
line_flip_func[589] = flip_b2_b3_b5()
line_flip_func[590] = flip_b4_b5()
line_flip_func[591] = flip_b2_b4_b5()
line_flip_func[592] = flip_b3_b4_b5()
line_flip_func[593] = flip_b2_b3_b4_b5()
line_flip_func[594] = flip_b2_b3_b4_b5()
line_flip_func[595] = flip_b3_b4_b5()
line_flip_func[596] = flip_b4_b5()
line_flip_func[597] = flip_b6()
line_flip_func[598] = flip_b4_b6()
line_flip_func[599] = flip_b3_b4_b6()
line_flip_func[600] = flip_b2_b3_b4_b6()
line_flip_func[601] = flip_b5_b6()
line_flip_func[602] = flip_b3_b5_b6()
line_flip_func[603] = flip_b2_b3_b5_b6()
line_flip_func[604] = flip_b4_b5_b6()
line_flip_func[605] = flip_b2_b4_b5_b6()
line_flip_func[606] = flip_b3_b4_b5_b6()
line_flip_func[607] = flip_b2_b3_b4_b5_b6()
line_flip_func[608] = flip_b2_b3_b4_b5_b6()
line_flip_func[609] = flip_b3_b4_b5_b6()
line_flip_func[610] = flip_b4_b5_b6()
line_flip_func[611] = flip_b5_b6()
line_flip_func[612] = flip_b7()
line_flip_func[613] = flip_b5_b7()
line_flip_func[614] = flip_b4_b5_b7()
line_flip_func[615] = flip_b3_b4_b5_b7()
line_flip_func[616] = flip_b2_b3_b4_b5_b7()
line_flip_func[617] = flip_b6_b7()
line_flip_func[618] = flip_b4_b6_b7()
line_flip_func[619] = flip_b3_b4_b6_b7()
line_flip_func[620] = flip_b2_b3_b4_b6_b7()
line_flip_func[621] = flip_b5_b6_b7()
line_flip_func[622] = flip_b3_b5_b6_b7()
line_flip_func[623] = flip_b2_b3_b5_b6_b7()
line_flip_func[624] = flip_b4_b5_b6_b7()
line_flip_func[625] = flip_b2_b4_b5_b6_b7()
line_flip_func[626] = flip_b3_b4_b5_b6_b7()
line_flip_func[627] = flip_b2_b3_b4_b5_b6_b7()
line_flip_func[628] = flip_b2_b3_b4_b5_b6_b7()
line_flip_func[629] = flip_b3_b4_b5_b6_b7()
line_flip_func[630] = flip_b4_b5_b6_b7()
line_flip_func[631] = flip_b5_b6_b7()
line_flip_func[632] = flip_b6_b7()
line_flip_func[640] = flip_()
line_flip_func[641] = flip_c2()
line_flip_func[642] = flip_c3()
line_flip_func[643] = flip_c2_c3()
line_flip_func[644] = flip_c2_c3()
line_flip_func[645] = flip_c4()
line_flip_func[646] = flip_c2_c4()
line_flip_func[647] = flip_c3_c4()
line_flip_func[648] = flip_c2_c3_c4()
line_flip_func[649] = flip_c2_c3_c4()
line_flip_func[650] = flip_c3_c4()
line_flip_func[651] = flip_c5()
line_flip_func[652] = flip_c3_c5()
line_flip_func[653] = flip_c2_c3_c5()
line_flip_func[654] = flip_c4_c5()
line_flip_func[655] = flip_c2_c4_c5()
line_flip_func[656] = flip_c3_c4_c5()
line_flip_func[657] = flip_c2_c3_c4_c5()
line_flip_func[658] = flip_c2_c3_c4_c5()
line_flip_func[659] = flip_c3_c4_c5()
line_flip_func[660] = flip_c4_c5()
line_flip_func[661] = flip_c6()
line_flip_func[662] = flip_c4_c6()
line_flip_func[663] = flip_c3_c4_c6()
line_flip_func[664] = flip_c2_c3_c4_c6()
line_flip_func[665] = flip_c5_c6()
line_flip_func[666] = flip_c3_c5_c6()
line_flip_func[667] = flip_c2_c3_c5_c6()
line_flip_func[668] = flip_c4_c5_c6()
line_flip_func[669] = flip_c2_c4_c5_c6()
line_flip_func[670] = flip_c3_c4_c5_c6()
line_flip_func[671] = flip_c2_c3_c4_c5_c6()
line_flip_func[672] = flip_c2_c3_c4_c5_c6()
line_flip_func[673] = flip_c3_c4_c5_c6()
line_flip_func[674] = flip_c4_c5_c6()
line_flip_func[675] = flip_c5_c6()
line_flip_func[676] = flip_c7()
line_flip_func[677] = flip_c5_c7()
line_flip_func[678] = flip_c4_c5_c7()
line_flip_func[679] = flip_c3_c4_c5_c7()
line_flip_func[680] = flip_c2_c3_c4_c5_c7()
line_flip_func[681] = flip_c6_c7()
line_flip_func[682] = flip_c4_c6_c7()
line_flip_func[683] = flip_c3_c4_c6_c7()
line_flip_func[684] = flip_c2_c3_c4_c6_c7()
line_flip_func[685] = flip_c5_c6_c7()
line_flip_func[686] = flip_c3_c5_c6_c7()
line_flip_func[687] = flip_c2_c3_c5_c6_c7()
line_flip_func[688] = flip_c4_c5_c6_c7()
line_flip_func[689] = flip_c2_c4_c5_c6_c7()
line_flip_func[690] = flip_c3_c4_c5_c6_c7()
line_flip_func[691] = flip_c2_c3_c4_c5_c6_c7()
line_flip_func[692] = flip_c2_c3_c4_c5_c6_c7()
line_flip_func[693] = flip_c3_c4_c5_c6_c7()
line_flip_func[694] = flip_c4_c5_c6_c7()
line_flip_func[695] = flip_c5_c6_c7()
line_flip_func[696] = flip_c6_c7()
line_flip_func[704] = flip_()
line_flip_func[705] = flip_d2()
line_flip_func[706] = flip_d3()
line_flip_func[707] = flip_d2_d3()
line_flip_func[708] = flip_d2_d3()
line_flip_func[709] = flip_d4()
line_flip_func[710] = flip_d2_d4()
line_flip_func[711] = flip_d3_d4()
line_flip_func[712] = flip_d2_d3_d4()
line_flip_func[713] = flip_d2_d3_d4()
line_flip_func[714] = flip_d3_d4()
line_flip_func[715] = flip_d5()
line_flip_func[716] = flip_d3_d5()
line_flip_func[717] = flip_d2_d3_d5()
line_flip_func[718] = flip_d4_d5()
line_flip_func[719] = flip_d2_d4_d5()
line_flip_func[720] = flip_d3_d4_d5()
line_flip_func[721] = flip_d2_d3_d4_d5()
line_flip_func[722] = flip_d2_d3_d4_d5()
line_flip_func[723] = flip_d3_d4_d5()
line_flip_func[724] = flip_d4_d5()
line_flip_func[725] = flip_d6()
line_flip_func[726] = flip_d4_d6()
line_flip_func[727] = flip_d3_d4_d6()
line_flip_func[728] = flip_d2_d3_d4_d6()
line_flip_func[729] = flip_d5_d6()
line_flip_func[730] = flip_d3_d5_d6()
line_flip_func[731] = flip_d2_d3_d5_d6()
line_flip_func[732] = flip_d4_d5_d6()
line_flip_func[733] = flip_d2_d4_d5_d6()
line_flip_func[734] = flip_d3_d4_d5_d6()
line_flip_func[735] = flip_d2_d3_d4_d5_d6()
line_flip_func[736] = flip_d2_d3_d4_d5_d6()
line_flip_func[737] = flip_d3_d4_d5_d6()
line_flip_func[738] = flip_d4_d5_d6()
line_flip_func[739] = flip_d5_d6()
line_flip_func[740] = flip_d7()
line_flip_func[741] = flip_d5_d7()
line_flip_func[742] = flip_d4_d5_d7()
line_flip_func[743] = flip_d3_d4_d5_d7()
line_flip_func[744] = flip_d2_d3_d4_d5_d7()
line_flip_func[745] = flip_d6_d7()
line_flip_func[746] = flip_d4_d6_d7()
line_flip_func[747] = flip_d3_d4_d6_d7()
line_flip_func[748] = flip_d2_d3_d4_d6_d7()
line_flip_func[749] = flip_d5_d6_d7()
line_flip_func[750] = flip_d3_d5_d6_d7()
line_flip_func[751] = flip_d2_d3_d5_d6_d7()
line_flip_func[752] = flip_d4_d5_d6_d7()
line_flip_func[753] = flip_d2_d4_d5_d6_d7()
line_flip_func[754] = flip_d3_d4_d5_d6_d7()
line_flip_func[755] = flip_d2_d3_d4_d5_d6_d7()
line_flip_func[756] = flip_d2_d3_d4_d5_d6_d7()
line_flip_func[757] = flip_d3_d4_d5_d6_d7()
line_flip_func[758] = flip_d4_d5_d6_d7()
line_flip_func[759] = flip_d5_d6_d7()
line_flip_func[760] = flip_d6_d7()
line_flip_func[768] = flip_()
line_flip_func[769] = flip_e2()
line_flip_func[770] = flip_e3()
line_flip_func[771] = flip_e2_e3()
line_flip_func[772] = flip_e2_e3()
line_flip_func[773] = flip_e4()
line_flip_func[774] = flip_e2_e4()
line_flip_func[775] = flip_e3_e4()
line_flip_func[776] = flip_e2_e3_e4()
line_flip_func[777] = flip_e2_e3_e4()
line_flip_func[778] = flip_e3_e4()
line_flip_func[779] = flip_e5()
line_flip_func[780] = flip_e3_e5()
line_flip_func[781] = flip_e2_e3_e5()
line_flip_func[782] = flip_e4_e5()
line_flip_func[783] = flip_e2_e4_e5()
line_flip_func[784] = flip_e3_e4_e5()
line_flip_func[785] = flip_e2_e3_e4_e5()
line_flip_func[786] = flip_e2_e3_e4_e5()
line_flip_func[787] = flip_e3_e4_e5()
line_flip_func[788] = flip_e4_e5()
line_flip_func[789] = flip_e6()
line_flip_func[790] = flip_e4_e6()
line_flip_func[791] = flip_e3_e4_e6()
line_flip_func[792] = flip_e2_e3_e4_e6()
line_flip_func[793] = flip_e5_e6()
line_flip_func[794] = flip_e3_e5_e6()
line_flip_func[795] = flip_e2_e3_e5_e6()
line_flip_func[796] = flip_e4_e5_e6()
line_flip_func[797] = flip_e2_e4_e5_e6()
line_flip_func[798] = flip_e3_e4_e5_e6()
line_flip_func[799] = flip_e2_e3_e4_e5_e6()
line_flip_func[800] = flip_e2_e3_e4_e5_e6()
line_flip_func[801] = flip_e3_e4_e5_e6()
line_flip_func[802] = flip_e4_e5_e6()
line_flip_func[803] = flip_e5_e6()
line_flip_func[804] = flip_e7()
line_flip_func[805] = flip_e5_e7()
line_flip_func[806] = flip_e4_e5_e7()
line_flip_func[807] = flip_e3_e4_e5_e7()
line_flip_func[808] = flip_e2_e3_e4_e5_e7()
line_flip_func[809] = flip_e6_e7()
line_flip_func[810] = flip_e4_e6_e7()
line_flip_func[811] = flip_e3_e4_e6_e7()
line_flip_func[812] = flip_e2_e3_e4_e6_e7()
line_flip_func[813] = flip_e5_e6_e7()
line_flip_func[814] = flip_e3_e5_e6_e7()
line_flip_func[815] = flip_e2_e3_e5_e6_e7()
line_flip_func[816] = flip_e4_e5_e6_e7()
line_flip_func[817] = flip_e2_e4_e5_e6_e7()
line_flip_func[818] = flip_e3_e4_e5_e6_e7()
line_flip_func[819] = flip_e2_e3_e4_e5_e6_e7()
line_flip_func[820] = flip_e2_e3_e4_e5_e6_e7()
line_flip_func[821] = flip_e3_e4_e5_e6_e7()
line_flip_func[822] = flip_e4_e5_e6_e7()
line_flip_func[823] = flip_e5_e6_e7()
line_flip_func[824] = flip_e6_e7()
line_flip_func[832] = flip_()
line_flip_func[833] = flip_f2()
line_flip_func[834] = flip_f3()
line_flip_func[835] = flip_f2_f3()
line_flip_func[836] = flip_f2_f3()
line_flip_func[837] = flip_f4()
line_flip_func[838] = flip_f2_f4()
line_flip_func[839] = flip_f3_f4()
line_flip_func[840] = flip_f2_f3_f4()
line_flip_func[841] = flip_f2_f3_f4()
line_flip_func[842] = flip_f3_f4()
line_flip_func[843] = flip_f5()
line_flip_func[844] = flip_f3_f5()
line_flip_func[845] = flip_f2_f3_f5()
line_flip_func[846] = flip_f4_f5()
line_flip_func[847] = flip_f2_f4_f5()
line_flip_func[848] = flip_f3_f4_f5()
line_flip_func[849] = flip_f2_f3_f4_f5()
line_flip_func[850] = flip_f2_f3_f4_f5()
line_flip_func[851] = flip_f3_f4_f5()
line_flip_func[852] = flip_f4_f5()
line_flip_func[853] = flip_f6()
line_flip_func[854] = flip_f4_f6()
line_flip_func[855] = flip_f3_f4_f6()
line_flip_func[856] = flip_f2_f3_f4_f6()
line_flip_func[857] = flip_f5_f6()
line_flip_func[858] = flip_f3_f5_f6()
line_flip_func[859] = flip_f2_f3_f5_f6()
line_flip_func[860] = flip_f4_f5_f6()
line_flip_func[861] = flip_f2_f4_f5_f6()
line_flip_func[862] = flip_f3_f4_f5_f6()
line_flip_func[863] = flip_f2_f3_f4_f5_f6()
line_flip_func[864] = flip_f2_f3_f4_f5_f6()
line_flip_func[865] = flip_f3_f4_f5_f6()
line_flip_func[866] = flip_f4_f5_f6()
line_flip_func[867] = flip_f5_f6()
line_flip_func[868] = flip_f7()
line_flip_func[869] = flip_f5_f7()
line_flip_func[870] = flip_f4_f5_f7()
line_flip_func[871] = flip_f3_f4_f5_f7()
line_flip_func[872] = flip_f2_f3_f4_f5_f7()
line_flip_func[873] = flip_f6_f7()
line_flip_func[874] = flip_f4_f6_f7()
line_flip_func[875] = flip_f3_f4_f6_f7()
line_flip_func[876] = flip_f2_f3_f4_f6_f7()
line_flip_func[877] = flip_f5_f6_f7()
line_flip_func[878] = flip_f3_f5_f6_f7()
line_flip_func[879] = flip_f2_f3_f5_f6_f7()
line_flip_func[880] = flip_f4_f5_f6_f7()
line_flip_func[881] = flip_f2_f4_f5_f6_f7()
line_flip_func[882] = flip_f3_f4_f5_f6_f7()
line_flip_func[883] = flip_f2_f3_f4_f5_f6_f7()
line_flip_func[884] = flip_f2_f3_f4_f5_f6_f7()
line_flip_func[885] = flip_f3_f4_f5_f6_f7()
line_flip_func[886] = flip_f4_f5_f6_f7()
line_flip_func[887] = flip_f5_f6_f7()
line_flip_func[888] = flip_f6_f7()
line_flip_func[896] = flip_()
line_flip_func[897] = flip_g2()
line_flip_func[898] = flip_g3()
line_flip_func[899] = flip_g2_g3()
line_flip_func[900] = flip_g2_g3()
line_flip_func[901] = flip_g4()
line_flip_func[902] = flip_g2_g4()
line_flip_func[903] = flip_g3_g4()
line_flip_func[904] = flip_g2_g3_g4()
line_flip_func[905] = flip_g2_g3_g4()
line_flip_func[906] = flip_g3_g4()
line_flip_func[907] = flip_g5()
line_flip_func[908] = flip_g3_g5()
line_flip_func[909] = flip_g2_g3_g5()
line_flip_func[910] = flip_g4_g5()
line_flip_func[911] = flip_g2_g4_g5()
line_flip_func[912] = flip_g3_g4_g5()
line_flip_func[913] = flip_g2_g3_g4_g5()
line_flip_func[914] = flip_g2_g3_g4_g5()
line_flip_func[915] = flip_g3_g4_g5()
line_flip_func[916] = flip_g4_g5()
line_flip_func[917] = flip_g6()
line_flip_func[918] = flip_g4_g6()
line_flip_func[919] = flip_g3_g4_g6()
line_flip_func[920] = flip_g2_g3_g4_g6()
line_flip_func[921] = flip_g5_g6()
line_flip_func[922] = flip_g3_g5_g6()
line_flip_func[923] = flip_g2_g3_g5_g6()
line_flip_func[924] = flip_g4_g5_g6()
line_flip_func[925] = flip_g2_g4_g5_g6()
line_flip_func[926] = flip_g3_g4_g5_g6()
line_flip_func[927] = flip_g2_g3_g4_g5_g6()
line_flip_func[928] = flip_g2_g3_g4_g5_g6()
line_flip_func[929] = flip_g3_g4_g5_g6()
line_flip_func[930] = flip_g4_g5_g6()
line_flip_func[931] = flip_g5_g6()
line_flip_func[932] = flip_g7()
line_flip_func[933] = flip_g5_g7()
line_flip_func[934] = flip_g4_g5_g7()
line_flip_func[935] = flip_g3_g4_g5_g7()
line_flip_func[936] = flip_g2_g3_g4_g5_g7()
line_flip_func[937] = flip_g6_g7()
line_flip_func[938] = flip_g4_g6_g7()
line_flip_func[939] = flip_g3_g4_g6_g7()
line_flip_func[940] = flip_g2_g3_g4_g6_g7()
line_flip_func[941] = flip_g5_g6_g7()
line_flip_func[942] = flip_g3_g5_g6_g7()
line_flip_func[943] = flip_g2_g3_g5_g6_g7()
line_flip_func[944] = flip_g4_g5_g6_g7()
line_flip_func[945] = flip_g2_g4_g5_g6_g7()
line_flip_func[946] = flip_g3_g4_g5_g6_g7()
line_flip_func[947] = flip_g2_g3_g4_g5_g6_g7()
line_flip_func[948] = flip_g2_g3_g4_g5_g6_g7()
line_flip_func[949] = flip_g3_g4_g5_g6_g7()
line_flip_func[950] = flip_g4_g5_g6_g7()
line_flip_func[951] = flip_g5_g6_g7()
line_flip_func[952] = flip_g6_g7()
line_flip_func[960] = flip_()
line_flip_func[961] = flip_h2()
line_flip_func[962] = flip_h3()
line_flip_func[963] = flip_h2_h3()
line_flip_func[964] = flip_h2_h3()
line_flip_func[965] = flip_h4()
line_flip_func[966] = flip_h2_h4()
line_flip_func[967] = flip_h3_h4()
line_flip_func[968] = flip_h2_h3_h4()
line_flip_func[969] = flip_h2_h3_h4()
line_flip_func[970] = flip_h3_h4()
line_flip_func[971] = flip_h5()
line_flip_func[972] = flip_h3_h5()
line_flip_func[973] = flip_h2_h3_h5()
line_flip_func[974] = flip_h4_h5()
line_flip_func[975] = flip_h2_h4_h5()
line_flip_func[976] = flip_h3_h4_h5()
line_flip_func[977] = flip_h2_h3_h4_h5()
line_flip_func[978] = flip_h2_h3_h4_h5()
line_flip_func[979] = flip_h3_h4_h5()
line_flip_func[980] = flip_h4_h5()
line_flip_func[981] = flip_h6()
line_flip_func[982] = flip_h4_h6()
line_flip_func[983] = flip_h3_h4_h6()
line_flip_func[984] = flip_h2_h3_h4_h6()
line_flip_func[985] = flip_h5_h6()
line_flip_func[986] = flip_h3_h5_h6()
line_flip_func[987] = flip_h2_h3_h5_h6()
line_flip_func[988] = flip_h4_h5_h6()
line_flip_func[989] = flip_h2_h4_h5_h6()
line_flip_func[990] = flip_h3_h4_h5_h6()
line_flip_func[991] = flip_h2_h3_h4_h5_h6()
line_flip_func[992] = flip_h2_h3_h4_h5_h6()
line_flip_func[993] = flip_h3_h4_h5_h6()
line_flip_func[994] = flip_h4_h5_h6()
line_flip_func[995] = flip_h5_h6()
line_flip_func[996] = flip_h7()
line_flip_func[997] = flip_h5_h7()
line_flip_func[998] = flip_h4_h5_h7()
line_flip_func[999] = flip_h3_h4_h5_h7()
line_flip_func[1000] = flip_h2_h3_h4_h5_h7()
line_flip_func[1001] = flip_h6_h7()
line_flip_func[1002] = flip_h4_h6_h7()
line_flip_func[1003] = flip_h3_h4_h6_h7()
line_flip_func[1004] = flip_h2_h3_h4_h6_h7()
line_flip_func[1005] = flip_h5_h6_h7()
line_flip_func[1006] = flip_h3_h5_h6_h7()
line_flip_func[1007] = flip_h2_h3_h5_h6_h7()
line_flip_func[1008] = flip_h4_h5_h6_h7()
line_flip_func[1009] = flip_h2_h4_h5_h6_h7()
line_flip_func[1010] = flip_h3_h4_h5_h6_h7()
line_flip_func[1011] = flip_h2_h3_h4_h5_h6_h7()
line_flip_func[1012] = flip_h2_h3_h4_h5_h6_h7()
line_flip_func[1013] = flip_h3_h4_h5_h6_h7()
line_flip_func[1014] = flip_h4_h5_h6_h7()
line_flip_func[1015] = flip_h5_h6_h7()
line_flip_func[1016] = flip_h6_h7()
line_flip_func[1024] = flip_()
line_flip_func[1025] = flip_()
line_flip_func[1026] = flip_()
line_flip_func[1027] = flip_()
line_flip_func[1028] = flip_()
line_flip_func[1029] = flip_()
line_flip_func[1030] = flip_()
line_flip_func[1031] = flip_()
line_flip_func[1032] = flip_()
line_flip_func[1033] = flip_()
line_flip_func[1034] = flip_()
line_flip_func[1035] = flip_()
line_flip_func[1036] = flip_()
line_flip_func[1037] = flip_()
line_flip_func[1038] = flip_()
line_flip_func[1039] = flip_()
line_flip_func[1040] = flip_()
line_flip_func[1041] = flip_()
line_flip_func[1042] = flip_()
line_flip_func[1043] = flip_()
line_flip_func[1044] = flip_()
line_flip_func[1045] = flip_()
line_flip_func[1046] = flip_()
line_flip_func[1047] = flip_()
line_flip_func[1048] = flip_()
line_flip_func[1049] = flip_()
line_flip_func[1050] = flip_()
line_flip_func[1051] = flip_()
line_flip_func[1052] = flip_()
line_flip_func[1053] = flip_()
line_flip_func[1054] = flip_()
line_flip_func[1055] = flip_()
line_flip_func[1056] = flip_()
line_flip_func[1057] = flip_()
line_flip_func[1058] = flip_()
line_flip_func[1059] = flip_()
line_flip_func[1060] = flip_()
line_flip_func[1061] = flip_()
line_flip_func[1062] = flip_()
line_flip_func[1063] = flip_()
line_flip_func[1064] = flip_()
line_flip_func[1065] = flip_()
line_flip_func[1066] = flip_()
line_flip_func[1067] = flip_()
line_flip_func[1068] = flip_()
line_flip_func[1069] = flip_()
line_flip_func[1070] = flip_()
line_flip_func[1071] = flip_()
line_flip_func[1072] = flip_()
line_flip_func[1073] = flip_()
line_flip_func[1074] = flip_()
line_flip_func[1075] = flip_()
line_flip_func[1076] = flip_()
line_flip_func[1077] = flip_()
line_flip_func[1078] = flip_()
line_flip_func[1079] = flip_()
line_flip_func[1080] = flip_()
line_flip_func[1088] = flip_()
line_flip_func[1089] = flip_()
line_flip_func[1090] = flip_()
line_flip_func[1091] = flip_()
line_flip_func[1092] = flip_()
line_flip_func[1093] = flip_()
line_flip_func[1094] = flip_()
line_flip_func[1095] = flip_()
line_flip_func[1096] = flip_()
line_flip_func[1097] = flip_()
line_flip_func[1098] = flip_()
line_flip_func[1099] = flip_()
line_flip_func[1100] = flip_()
line_flip_func[1101] = flip_()
line_flip_func[1102] = flip_()
line_flip_func[1103] = flip_()
line_flip_func[1104] = flip_()
line_flip_func[1105] = flip_()
line_flip_func[1106] = flip_()
line_flip_func[1107] = flip_()
line_flip_func[1108] = flip_()
line_flip_func[1109] = flip_()
line_flip_func[1110] = flip_()
line_flip_func[1111] = flip_()
line_flip_func[1112] = flip_()
line_flip_func[1113] = flip_()
line_flip_func[1114] = flip_()
line_flip_func[1115] = flip_()
line_flip_func[1116] = flip_()
line_flip_func[1117] = flip_()
line_flip_func[1118] = flip_()
line_flip_func[1119] = flip_()
line_flip_func[1120] = flip_()
line_flip_func[1121] = flip_()
line_flip_func[1122] = flip_()
line_flip_func[1123] = flip_()
line_flip_func[1124] = flip_()
line_flip_func[1125] = flip_()
line_flip_func[1126] = flip_()
line_flip_func[1127] = flip_()
line_flip_func[1128] = flip_()
line_flip_func[1129] = flip_()
line_flip_func[1130] = flip_()
line_flip_func[1131] = flip_()
line_flip_func[1132] = flip_()
line_flip_func[1133] = flip_()
line_flip_func[1134] = flip_()
line_flip_func[1135] = flip_()
line_flip_func[1136] = flip_()
line_flip_func[1137] = flip_()
line_flip_func[1138] = flip_()
line_flip_func[1139] = flip_()
line_flip_func[1140] = flip_()
line_flip_func[1141] = flip_()
line_flip_func[1142] = flip_()
line_flip_func[1143] = flip_()
line_flip_func[1144] = flip_()
line_flip_func[1152] = flip_()
line_flip_func[1153] = flip_b2()
line_flip_func[1154] = flip_()
line_flip_func[1155] = flip_b2()
line_flip_func[1156] = flip_b2()
line_flip_func[1157] = flip_()
line_flip_func[1158] = flip_b2()
line_flip_func[1159] = flip_()
line_flip_func[1160] = flip_b2()
line_flip_func[1161] = flip_b2()
line_flip_func[1162] = flip_()
line_flip_func[1163] = flip_()
line_flip_func[1164] = flip_()
line_flip_func[1165] = flip_b2()
line_flip_func[1166] = flip_()
line_flip_func[1167] = flip_b2()
line_flip_func[1168] = flip_()
line_flip_func[1169] = flip_b2()
line_flip_func[1170] = flip_b2()
line_flip_func[1171] = flip_()
line_flip_func[1172] = flip_()
line_flip_func[1173] = flip_()
line_flip_func[1174] = flip_()
line_flip_func[1175] = flip_()
line_flip_func[1176] = flip_b2()
line_flip_func[1177] = flip_()
line_flip_func[1178] = flip_()
line_flip_func[1179] = flip_b2()
line_flip_func[1180] = flip_()
line_flip_func[1181] = flip_b2()
line_flip_func[1182] = flip_()
line_flip_func[1183] = flip_b2()
line_flip_func[1184] = flip_b2()
line_flip_func[1185] = flip_()
line_flip_func[1186] = flip_()
line_flip_func[1187] = flip_()
line_flip_func[1188] = flip_()
line_flip_func[1189] = flip_()
line_flip_func[1190] = flip_()
line_flip_func[1191] = flip_()
line_flip_func[1192] = flip_b2()
line_flip_func[1193] = flip_()
line_flip_func[1194] = flip_()
line_flip_func[1195] = flip_()
line_flip_func[1196] = flip_b2()
line_flip_func[1197] = flip_()
line_flip_func[1198] = flip_()
line_flip_func[1199] = flip_b2()
line_flip_func[1200] = flip_()
line_flip_func[1201] = flip_b2()
line_flip_func[1202] = flip_()
line_flip_func[1203] = flip_b2()
line_flip_func[1204] = flip_b2()
line_flip_func[1205] = flip_()
line_flip_func[1206] = flip_()
line_flip_func[1207] = flip_()
line_flip_func[1208] = flip_()
line_flip_func[1216] = flip_()
line_flip_func[1217] = flip_b3()
line_flip_func[1218] = flip_c2()
line_flip_func[1219] = flip_b3_c2()
line_flip_func[1220] = flip_b3_c2()
line_flip_func[1221] = flip_()
line_flip_func[1222] = flip_b3()
line_flip_func[1223] = flip_c2()
line_flip_func[1224] = flip_b3_c2()
line_flip_func[1225] = flip_b3_c2()
line_flip_func[1226] = flip_c2()
line_flip_func[1227] = flip_()
line_flip_func[1228] = flip_c2()
line_flip_func[1229] = flip_b3_c2()
line_flip_func[1230] = flip_()
line_flip_func[1231] = flip_b3()
line_flip_func[1232] = flip_c2()
line_flip_func[1233] = flip_b3_c2()
line_flip_func[1234] = flip_b3_c2()
line_flip_func[1235] = flip_c2()
line_flip_func[1236] = flip_()
line_flip_func[1237] = flip_()
line_flip_func[1238] = flip_()
line_flip_func[1239] = flip_c2()
line_flip_func[1240] = flip_b3_c2()
line_flip_func[1241] = flip_()
line_flip_func[1242] = flip_c2()
line_flip_func[1243] = flip_b3_c2()
line_flip_func[1244] = flip_()
line_flip_func[1245] = flip_b3()
line_flip_func[1246] = flip_c2()
line_flip_func[1247] = flip_b3_c2()
line_flip_func[1248] = flip_b3_c2()
line_flip_func[1249] = flip_c2()
line_flip_func[1250] = flip_()
line_flip_func[1251] = flip_()
line_flip_func[1252] = flip_()
line_flip_func[1253] = flip_()
line_flip_func[1254] = flip_()
line_flip_func[1255] = flip_c2()
line_flip_func[1256] = flip_b3_c2()
line_flip_func[1257] = flip_()
line_flip_func[1258] = flip_()
line_flip_func[1259] = flip_c2()
line_flip_func[1260] = flip_b3_c2()
line_flip_func[1261] = flip_()
line_flip_func[1262] = flip_c2()
line_flip_func[1263] = flip_b3_c2()
line_flip_func[1264] = flip_()
line_flip_func[1265] = flip_b3()
line_flip_func[1266] = flip_c2()
line_flip_func[1267] = flip_b3_c2()
line_flip_func[1268] = flip_b3_c2()
line_flip_func[1269] = flip_c2()
line_flip_func[1270] = flip_()
line_flip_func[1271] = flip_()
line_flip_func[1272] = flip_()
line_flip_func[1280] = flip_()
line_flip_func[1281] = flip_b4()
line_flip_func[1282] = flip_c3()
line_flip_func[1283] = flip_b4_c3()
line_flip_func[1284] = flip_b4_c3()
line_flip_func[1285] = flip_d2()
line_flip_func[1286] = flip_b4_d2()
line_flip_func[1287] = flip_c3_d2()
line_flip_func[1288] = flip_b4_c3_d2()
line_flip_func[1289] = flip_b4_c3_d2()
line_flip_func[1290] = flip_c3_d2()
line_flip_func[1291] = flip_()
line_flip_func[1292] = flip_c3()
line_flip_func[1293] = flip_b4_c3()
line_flip_func[1294] = flip_d2()
line_flip_func[1295] = flip_b4_d2()
line_flip_func[1296] = flip_c3_d2()
line_flip_func[1297] = flip_b4_c3_d2()
line_flip_func[1298] = flip_b4_c3_d2()
line_flip_func[1299] = flip_c3_d2()
line_flip_func[1300] = flip_d2()
line_flip_func[1301] = flip_()
line_flip_func[1302] = flip_d2()
line_flip_func[1303] = flip_c3_d2()
line_flip_func[1304] = flip_b4_c3_d2()
line_flip_func[1305] = flip_()
line_flip_func[1306] = flip_c3()
line_flip_func[1307] = flip_b4_c3()
line_flip_func[1308] = flip_d2()
line_flip_func[1309] = flip_b4_d2()
line_flip_func[1310] = flip_c3_d2()
line_flip_func[1311] = flip_b4_c3_d2()
line_flip_func[1312] = flip_b4_c3_d2()
line_flip_func[1313] = flip_c3_d2()
line_flip_func[1314] = flip_d2()
line_flip_func[1315] = flip_()
line_flip_func[1316] = flip_()
line_flip_func[1317] = flip_()
line_flip_func[1318] = flip_d2()
line_flip_func[1319] = flip_c3_d2()
line_flip_func[1320] = flip_b4_c3_d2()
line_flip_func[1321] = flip_()
line_flip_func[1322] = flip_d2()
line_flip_func[1323] = flip_c3_d2()
line_flip_func[1324] = flip_b4_c3_d2()
line_flip_func[1325] = flip_()
line_flip_func[1326] = flip_c3()
line_flip_func[1327] = flip_b4_c3()
line_flip_func[1328] = flip_d2()
line_flip_func[1329] = flip_b4_d2()
line_flip_func[1330] = flip_c3_d2()
line_flip_func[1331] = flip_b4_c3_d2()
line_flip_func[1332] = flip_b4_c3_d2()
line_flip_func[1333] = flip_c3_d2()
line_flip_func[1334] = flip_d2()
line_flip_func[1335] = flip_()
line_flip_func[1336] = flip_()
line_flip_func[1344] = flip_()
line_flip_func[1345] = flip_b5()
line_flip_func[1346] = flip_c4()
line_flip_func[1347] = flip_b5_c4()
line_flip_func[1348] = flip_b5_c4()
line_flip_func[1349] = flip_d3()
line_flip_func[1350] = flip_b5_d3()
line_flip_func[1351] = flip_c4_d3()
line_flip_func[1352] = flip_b5_c4_d3()
line_flip_func[1353] = flip_b5_c4_d3()
line_flip_func[1354] = flip_c4_d3()
line_flip_func[1355] = flip_e2()
line_flip_func[1356] = flip_c4_e2()
line_flip_func[1357] = flip_b5_c4_e2()
line_flip_func[1358] = flip_d3_e2()
line_flip_func[1359] = flip_b5_d3_e2()
line_flip_func[1360] = flip_c4_d3_e2()
line_flip_func[1361] = flip_b5_c4_d3_e2()
line_flip_func[1362] = flip_b5_c4_d3_e2()
line_flip_func[1363] = flip_c4_d3_e2()
line_flip_func[1364] = flip_d3_e2()
line_flip_func[1365] = flip_()
line_flip_func[1366] = flip_d3()
line_flip_func[1367] = flip_c4_d3()
line_flip_func[1368] = flip_b5_c4_d3()
line_flip_func[1369] = flip_e2()
line_flip_func[1370] = flip_c4_e2()
line_flip_func[1371] = flip_b5_c4_e2()
line_flip_func[1372] = flip_d3_e2()
line_flip_func[1373] = flip_b5_d3_e2()
line_flip_func[1374] = flip_c4_d3_e2()
line_flip_func[1375] = flip_b5_c4_d3_e2()
line_flip_func[1376] = flip_b5_c4_d3_e2()
line_flip_func[1377] = flip_c4_d3_e2()
line_flip_func[1378] = flip_d3_e2()
line_flip_func[1379] = flip_e2()
line_flip_func[1380] = flip_()
line_flip_func[1381] = flip_e2()
line_flip_func[1382] = flip_d3_e2()
line_flip_func[1383] = flip_c4_d3_e2()
line_flip_func[1384] = flip_b5_c4_d3_e2()
line_flip_func[1385] = flip_()
line_flip_func[1386] = flip_d3()
line_flip_func[1387] = flip_c4_d3()
line_flip_func[1388] = flip_b5_c4_d3()
line_flip_func[1389] = flip_e2()
line_flip_func[1390] = flip_c4_e2()
line_flip_func[1391] = flip_b5_c4_e2()
line_flip_func[1392] = flip_d3_e2()
line_flip_func[1393] = flip_b5_d3_e2()
line_flip_func[1394] = flip_c4_d3_e2()
line_flip_func[1395] = flip_b5_c4_d3_e2()
line_flip_func[1396] = flip_b5_c4_d3_e2()
line_flip_func[1397] = flip_c4_d3_e2()
line_flip_func[1398] = flip_d3_e2()
line_flip_func[1399] = flip_e2()
line_flip_func[1400] = flip_()
line_flip_func[1408] = flip_()
line_flip_func[1409] = flip_b6()
line_flip_func[1410] = flip_c5()
line_flip_func[1411] = flip_b6_c5()
line_flip_func[1412] = flip_b6_c5()
line_flip_func[1413] = flip_d4()
line_flip_func[1414] = flip_b6_d4()
line_flip_func[1415] = flip_c5_d4()
line_flip_func[1416] = flip_b6_c5_d4()
line_flip_func[1417] = flip_b6_c5_d4()
line_flip_func[1418] = flip_c5_d4()
line_flip_func[1419] = flip_e3()
line_flip_func[1420] = flip_c5_e3()
line_flip_func[1421] = flip_b6_c5_e3()
line_flip_func[1422] = flip_d4_e3()
line_flip_func[1423] = flip_b6_d4_e3()
line_flip_func[1424] = flip_c5_d4_e3()
line_flip_func[1425] = flip_b6_c5_d4_e3()
line_flip_func[1426] = flip_b6_c5_d4_e3()
line_flip_func[1427] = flip_c5_d4_e3()
line_flip_func[1428] = flip_d4_e3()
line_flip_func[1429] = flip_f2()
line_flip_func[1430] = flip_d4_f2()
line_flip_func[1431] = flip_c5_d4_f2()
line_flip_func[1432] = flip_b6_c5_d4_f2()
line_flip_func[1433] = flip_e3_f2()
line_flip_func[1434] = flip_c5_e3_f2()
line_flip_func[1435] = flip_b6_c5_e3_f2()
line_flip_func[1436] = flip_d4_e3_f2()
line_flip_func[1437] = flip_b6_d4_e3_f2()
line_flip_func[1438] = flip_c5_d4_e3_f2()
line_flip_func[1439] = flip_b6_c5_d4_e3_f2()
line_flip_func[1440] = flip_b6_c5_d4_e3_f2()
line_flip_func[1441] = flip_c5_d4_e3_f2()
line_flip_func[1442] = flip_d4_e3_f2()
line_flip_func[1443] = flip_e3_f2()
line_flip_func[1444] = flip_()
line_flip_func[1445] = flip_e3()
line_flip_func[1446] = flip_d4_e3()
line_flip_func[1447] = flip_c5_d4_e3()
line_flip_func[1448] = flip_b6_c5_d4_e3()
line_flip_func[1449] = flip_f2()
line_flip_func[1450] = flip_d4_f2()
line_flip_func[1451] = flip_c5_d4_f2()
line_flip_func[1452] = flip_b6_c5_d4_f2()
line_flip_func[1453] = flip_e3_f2()
line_flip_func[1454] = flip_c5_e3_f2()
line_flip_func[1455] = flip_b6_c5_e3_f2()
line_flip_func[1456] = flip_d4_e3_f2()
line_flip_func[1457] = flip_b6_d4_e3_f2()
line_flip_func[1458] = flip_c5_d4_e3_f2()
line_flip_func[1459] = flip_b6_c5_d4_e3_f2()
line_flip_func[1460] = flip_b6_c5_d4_e3_f2()
line_flip_func[1461] = flip_c5_d4_e3_f2()
line_flip_func[1462] = flip_d4_e3_f2()
line_flip_func[1463] = flip_e3_f2()
line_flip_func[1464] = flip_f2()
line_flip_func[1472] = flip_()
line_flip_func[1473] = flip_b7()
line_flip_func[1474] = flip_c6()
line_flip_func[1475] = flip_b7_c6()
line_flip_func[1476] = flip_b7_c6()
line_flip_func[1477] = flip_d5()
line_flip_func[1478] = flip_b7_d5()
line_flip_func[1479] = flip_c6_d5()
line_flip_func[1480] = flip_b7_c6_d5()
line_flip_func[1481] = flip_b7_c6_d5()
line_flip_func[1482] = flip_c6_d5()
line_flip_func[1483] = flip_e4()
line_flip_func[1484] = flip_c6_e4()
line_flip_func[1485] = flip_b7_c6_e4()
line_flip_func[1486] = flip_d5_e4()
line_flip_func[1487] = flip_b7_d5_e4()
line_flip_func[1488] = flip_c6_d5_e4()
line_flip_func[1489] = flip_b7_c6_d5_e4()
line_flip_func[1490] = flip_b7_c6_d5_e4()
line_flip_func[1491] = flip_c6_d5_e4()
line_flip_func[1492] = flip_d5_e4()
line_flip_func[1493] = flip_f3()
line_flip_func[1494] = flip_d5_f3()
line_flip_func[1495] = flip_c6_d5_f3()
line_flip_func[1496] = flip_b7_c6_d5_f3()
line_flip_func[1497] = flip_e4_f3()
line_flip_func[1498] = flip_c6_e4_f3()
line_flip_func[1499] = flip_b7_c6_e4_f3()
line_flip_func[1500] = flip_d5_e4_f3()
line_flip_func[1501] = flip_b7_d5_e4_f3()
line_flip_func[1502] = flip_c6_d5_e4_f3()
line_flip_func[1503] = flip_b7_c6_d5_e4_f3()
line_flip_func[1504] = flip_b7_c6_d5_e4_f3()
line_flip_func[1505] = flip_c6_d5_e4_f3()
line_flip_func[1506] = flip_d5_e4_f3()
line_flip_func[1507] = flip_e4_f3()
line_flip_func[1508] = flip_g2()
line_flip_func[1509] = flip_e4_g2()
line_flip_func[1510] = flip_d5_e4_g2()
line_flip_func[1511] = flip_c6_d5_e4_g2()
line_flip_func[1512] = flip_b7_c6_d5_e4_g2()
line_flip_func[1513] = flip_f3_g2()
line_flip_func[1514] = flip_d5_f3_g2()
line_flip_func[1515] = flip_c6_d5_f3_g2()
line_flip_func[1516] = flip_b7_c6_d5_f3_g2()
line_flip_func[1517] = flip_e4_f3_g2()
line_flip_func[1518] = flip_c6_e4_f3_g2()
line_flip_func[1519] = flip_b7_c6_e4_f3_g2()
line_flip_func[1520] = flip_d5_e4_f3_g2()
line_flip_func[1521] = flip_b7_d5_e4_f3_g2()
line_flip_func[1522] = flip_c6_d5_e4_f3_g2()
line_flip_func[1523] = flip_b7_c6_d5_e4_f3_g2()
line_flip_func[1524] = flip_b7_c6_d5_e4_f3_g2()
line_flip_func[1525] = flip_c6_d5_e4_f3_g2()
line_flip_func[1526] = flip_d5_e4_f3_g2()
line_flip_func[1527] = flip_e4_f3_g2()
line_flip_func[1528] = flip_f3_g2()
line_flip_func[1536] = flip_()
line_flip_func[1537] = flip_c7()
line_flip_func[1538] = flip_d6()
line_flip_func[1539] = flip_c7_d6()
line_flip_func[1540] = flip_c7_d6()
line_flip_func[1541] = flip_e5()
line_flip_func[1542] = flip_c7_e5()
line_flip_func[1543] = flip_d6_e5()
line_flip_func[1544] = flip_c7_d6_e5()
line_flip_func[1545] = flip_c7_d6_e5()
line_flip_func[1546] = flip_d6_e5()
line_flip_func[1547] = flip_f4()
line_flip_func[1548] = flip_d6_f4()
line_flip_func[1549] = flip_c7_d6_f4()
line_flip_func[1550] = flip_e5_f4()
line_flip_func[1551] = flip_c7_e5_f4()
line_flip_func[1552] = flip_d6_e5_f4()
line_flip_func[1553] = flip_c7_d6_e5_f4()
line_flip_func[1554] = flip_c7_d6_e5_f4()
line_flip_func[1555] = flip_d6_e5_f4()
line_flip_func[1556] = flip_e5_f4()
line_flip_func[1557] = flip_g3()
line_flip_func[1558] = flip_e5_g3()
line_flip_func[1559] = flip_d6_e5_g3()
line_flip_func[1560] = flip_c7_d6_e5_g3()
line_flip_func[1561] = flip_f4_g3()
line_flip_func[1562] = flip_d6_f4_g3()
line_flip_func[1563] = flip_c7_d6_f4_g3()
line_flip_func[1564] = flip_e5_f4_g3()
line_flip_func[1565] = flip_c7_e5_f4_g3()
line_flip_func[1566] = flip_d6_e5_f4_g3()
line_flip_func[1567] = flip_c7_d6_e5_f4_g3()
line_flip_func[1568] = flip_c7_d6_e5_f4_g3()
line_flip_func[1569] = flip_d6_e5_f4_g3()
line_flip_func[1570] = flip_e5_f4_g3()
line_flip_func[1571] = flip_f4_g3()
line_flip_func[1572] = flip_()
line_flip_func[1573] = flip_f4()
line_flip_func[1574] = flip_e5_f4()
line_flip_func[1575] = flip_d6_e5_f4()
line_flip_func[1576] = flip_c7_d6_e5_f4()
line_flip_func[1577] = flip_g3()
line_flip_func[1578] = flip_e5_g3()
line_flip_func[1579] = flip_d6_e5_g3()
line_flip_func[1580] = flip_c7_d6_e5_g3()
line_flip_func[1581] = flip_f4_g3()
line_flip_func[1582] = flip_d6_f4_g3()
line_flip_func[1583] = flip_c7_d6_f4_g3()
line_flip_func[1584] = flip_e5_f4_g3()
line_flip_func[1585] = flip_c7_e5_f4_g3()
line_flip_func[1586] = flip_d6_e5_f4_g3()
line_flip_func[1587] = flip_c7_d6_e5_f4_g3()
line_flip_func[1588] = flip_c7_d6_e5_f4_g3()
line_flip_func[1589] = flip_d6_e5_f4_g3()
line_flip_func[1590] = flip_e5_f4_g3()
line_flip_func[1591] = flip_f4_g3()
line_flip_func[1592] = flip_g3()
line_flip_func[1600] = flip_()
line_flip_func[1601] = flip_d7()
line_flip_func[1602] = flip_e6()
line_flip_func[1603] = flip_d7_e6()
line_flip_func[1604] = flip_d7_e6()
line_flip_func[1605] = flip_f5()
line_flip_func[1606] = flip_d7_f5()
line_flip_func[1607] = flip_e6_f5()
line_flip_func[1608] = flip_d7_e6_f5()
line_flip_func[1609] = flip_d7_e6_f5()
line_flip_func[1610] = flip_e6_f5()
line_flip_func[1611] = flip_g4()
line_flip_func[1612] = flip_e6_g4()
line_flip_func[1613] = flip_d7_e6_g4()
line_flip_func[1614] = flip_f5_g4()
line_flip_func[1615] = flip_d7_f5_g4()
line_flip_func[1616] = flip_e6_f5_g4()
line_flip_func[1617] = flip_d7_e6_f5_g4()
line_flip_func[1618] = flip_d7_e6_f5_g4()
line_flip_func[1619] = flip_e6_f5_g4()
line_flip_func[1620] = flip_f5_g4()
line_flip_func[1621] = flip_()
line_flip_func[1622] = flip_f5()
line_flip_func[1623] = flip_e6_f5()
line_flip_func[1624] = flip_d7_e6_f5()
line_flip_func[1625] = flip_g4()
line_flip_func[1626] = flip_e6_g4()
line_flip_func[1627] = flip_d7_e6_g4()
line_flip_func[1628] = flip_f5_g4()
line_flip_func[1629] = flip_d7_f5_g4()
line_flip_func[1630] = flip_e6_f5_g4()
line_flip_func[1631] = flip_d7_e6_f5_g4()
line_flip_func[1632] = flip_d7_e6_f5_g4()
line_flip_func[1633] = flip_e6_f5_g4()
line_flip_func[1634] = flip_f5_g4()
line_flip_func[1635] = flip_g4()
line_flip_func[1636] = flip_()
line_flip_func[1637] = flip_g4()
line_flip_func[1638] = flip_f5_g4()
line_flip_func[1639] = flip_e6_f5_g4()
line_flip_func[1640] = flip_d7_e6_f5_g4()
line_flip_func[1641] = flip_()
line_flip_func[1642] = flip_f5()
line_flip_func[1643] = flip_e6_f5()
line_flip_func[1644] = flip_d7_e6_f5()
line_flip_func[1645] = flip_g4()
line_flip_func[1646] = flip_e6_g4()
line_flip_func[1647] = flip_d7_e6_g4()
line_flip_func[1648] = flip_f5_g4()
line_flip_func[1649] = flip_d7_f5_g4()
line_flip_func[1650] = flip_e6_f5_g4()
line_flip_func[1651] = flip_d7_e6_f5_g4()
line_flip_func[1652] = flip_d7_e6_f5_g4()
line_flip_func[1653] = flip_e6_f5_g4()
line_flip_func[1654] = flip_f5_g4()
line_flip_func[1655] = flip_g4()
line_flip_func[1656] = flip_()
line_flip_func[1664] = flip_()
line_flip_func[1665] = flip_e7()
line_flip_func[1666] = flip_f6()
line_flip_func[1667] = flip_e7_f6()
line_flip_func[1668] = flip_e7_f6()
line_flip_func[1669] = flip_g5()
line_flip_func[1670] = flip_e7_g5()
line_flip_func[1671] = flip_f6_g5()
line_flip_func[1672] = flip_e7_f6_g5()
line_flip_func[1673] = flip_e7_f6_g5()
line_flip_func[1674] = flip_f6_g5()
line_flip_func[1675] = flip_()
line_flip_func[1676] = flip_f6()
line_flip_func[1677] = flip_e7_f6()
line_flip_func[1678] = flip_g5()
line_flip_func[1679] = flip_e7_g5()
line_flip_func[1680] = flip_f6_g5()
line_flip_func[1681] = flip_e7_f6_g5()
line_flip_func[1682] = flip_e7_f6_g5()
line_flip_func[1683] = flip_f6_g5()
line_flip_func[1684] = flip_g5()
line_flip_func[1685] = flip_()
line_flip_func[1686] = flip_g5()
line_flip_func[1687] = flip_f6_g5()
line_flip_func[1688] = flip_e7_f6_g5()
line_flip_func[1689] = flip_()
line_flip_func[1690] = flip_f6()
line_flip_func[1691] = flip_e7_f6()
line_flip_func[1692] = flip_g5()
line_flip_func[1693] = flip_e7_g5()
line_flip_func[1694] = flip_f6_g5()
line_flip_func[1695] = flip_e7_f6_g5()
line_flip_func[1696] = flip_e7_f6_g5()
line_flip_func[1697] = flip_f6_g5()
line_flip_func[1698] = flip_g5()
line_flip_func[1699] = flip_()
line_flip_func[1700] = flip_()
line_flip_func[1701] = flip_()
line_flip_func[1702] = flip_g5()
line_flip_func[1703] = flip_f6_g5()
line_flip_func[1704] = flip_e7_f6_g5()
line_flip_func[1705] = flip_()
line_flip_func[1706] = flip_g5()
line_flip_func[1707] = flip_f6_g5()
line_flip_func[1708] = flip_e7_f6_g5()
line_flip_func[1709] = flip_()
line_flip_func[1710] = flip_f6()
line_flip_func[1711] = flip_e7_f6()
line_flip_func[1712] = flip_g5()
line_flip_func[1713] = flip_e7_g5()
line_flip_func[1714] = flip_f6_g5()
line_flip_func[1715] = flip_e7_f6_g5()
line_flip_func[1716] = flip_e7_f6_g5()
line_flip_func[1717] = flip_f6_g5()
line_flip_func[1718] = flip_g5()
line_flip_func[1719] = flip_()
line_flip_func[1720] = flip_()
line_flip_func[1728] = flip_()
line_flip_func[1729] = flip_f7()
line_flip_func[1730] = flip_g6()
line_flip_func[1731] = flip_f7_g6()
line_flip_func[1732] = flip_f7_g6()
line_flip_func[1733] = flip_()
line_flip_func[1734] = flip_f7()
line_flip_func[1735] = flip_g6()
line_flip_func[1736] = flip_f7_g6()
line_flip_func[1737] = flip_f7_g6()
line_flip_func[1738] = flip_g6()
line_flip_func[1739] = flip_()
line_flip_func[1740] = flip_g6()
line_flip_func[1741] = flip_f7_g6()
line_flip_func[1742] = flip_()
line_flip_func[1743] = flip_f7()
line_flip_func[1744] = flip_g6()
line_flip_func[1745] = flip_f7_g6()
line_flip_func[1746] = flip_f7_g6()
line_flip_func[1747] = flip_g6()
line_flip_func[1748] = flip_()
line_flip_func[1749] = flip_()
line_flip_func[1750] = flip_()
line_flip_func[1751] = flip_g6()
line_flip_func[1752] = flip_f7_g6()
line_flip_func[1753] = flip_()
line_flip_func[1754] = flip_g6()
line_flip_func[1755] = flip_f7_g6()
line_flip_func[1756] = flip_()
line_flip_func[1757] = flip_f7()
line_flip_func[1758] = flip_g6()
line_flip_func[1759] = flip_f7_g6()
line_flip_func[1760] = flip_f7_g6()
line_flip_func[1761] = flip_g6()
line_flip_func[1762] = flip_()
line_flip_func[1763] = flip_()
line_flip_func[1764] = flip_()
line_flip_func[1765] = flip_()
line_flip_func[1766] = flip_()
line_flip_func[1767] = flip_g6()
line_flip_func[1768] = flip_f7_g6()
line_flip_func[1769] = flip_()
line_flip_func[1770] = flip_()
line_flip_func[1771] = flip_g6()
line_flip_func[1772] = flip_f7_g6()
line_flip_func[1773] = flip_()
line_flip_func[1774] = flip_g6()
line_flip_func[1775] = flip_f7_g6()
line_flip_func[1776] = flip_()
line_flip_func[1777] = flip_f7()
line_flip_func[1778] = flip_g6()
line_flip_func[1779] = flip_f7_g6()
line_flip_func[1780] = flip_f7_g6()
line_flip_func[1781] = flip_g6()
line_flip_func[1782] = flip_()
line_flip_func[1783] = flip_()
line_flip_func[1784] = flip_()
line_flip_func[1792] = flip_()
line_flip_func[1793] = flip_g7()
line_flip_func[1794] = flip_()
line_flip_func[1795] = flip_g7()
line_flip_func[1796] = flip_g7()
line_flip_func[1797] = flip_()
line_flip_func[1798] = flip_g7()
line_flip_func[1799] = flip_()
line_flip_func[1800] = flip_g7()
line_flip_func[1801] = flip_g7()
line_flip_func[1802] = flip_()
line_flip_func[1803] = flip_()
line_flip_func[1804] = flip_()
line_flip_func[1805] = flip_g7()
line_flip_func[1806] = flip_()
line_flip_func[1807] = flip_g7()
line_flip_func[1808] = flip_()
line_flip_func[1809] = flip_g7()
line_flip_func[1810] = flip_g7()
line_flip_func[1811] = flip_()
line_flip_func[1812] = flip_()
line_flip_func[1813] = flip_()
line_flip_func[1814] = flip_()
line_flip_func[1815] = flip_()
line_flip_func[1816] = flip_g7()
line_flip_func[1817] = flip_()
line_flip_func[1818] = flip_()
line_flip_func[1819] = flip_g7()
line_flip_func[1820] = flip_()
line_flip_func[1821] = flip_g7()
line_flip_func[1822] = flip_()
line_flip_func[1823] = flip_g7()
line_flip_func[1824] = flip_g7()
line_flip_func[1825] = flip_()
line_flip_func[1826] = flip_()
line_flip_func[1827] = flip_()
line_flip_func[1828] = flip_()
line_flip_func[1829] = flip_()
line_flip_func[1830] = flip_()
line_flip_func[1831] = flip_()
line_flip_func[1832] = flip_g7()
line_flip_func[1833] = flip_()
line_flip_func[1834] = flip_()
line_flip_func[1835] = flip_()
line_flip_func[1836] = flip_g7()
line_flip_func[1837] = flip_()
line_flip_func[1838] = flip_()
line_flip_func[1839] = flip_g7()
line_flip_func[1840] = flip_()
line_flip_func[1841] = flip_g7()
line_flip_func[1842] = flip_()
line_flip_func[1843] = flip_g7()
line_flip_func[1844] = flip_g7()
line_flip_func[1845] = flip_()
line_flip_func[1846] = flip_()
line_flip_func[1847] = flip_()
line_flip_func[1848] = flip_()
line_flip_func[1856] = flip_()
line_flip_func[1857] = flip_()
line_flip_func[1858] = flip_()
line_flip_func[1859] = flip_()
line_flip_func[1860] = flip_()
line_flip_func[1861] = flip_()
line_flip_func[1862] = flip_()
line_flip_func[1863] = flip_()
line_flip_func[1864] = flip_()
line_flip_func[1865] = flip_()
line_flip_func[1866] = flip_()
line_flip_func[1867] = flip_()
line_flip_func[1868] = flip_()
line_flip_func[1869] = flip_()
line_flip_func[1870] = flip_()
line_flip_func[1871] = flip_()
line_flip_func[1872] = flip_()
line_flip_func[1873] = flip_()
line_flip_func[1874] = flip_()
line_flip_func[1875] = flip_()
line_flip_func[1876] = flip_()
line_flip_func[1877] = flip_()
line_flip_func[1878] = flip_()
line_flip_func[1879] = flip_()
line_flip_func[1880] = flip_()
line_flip_func[1881] = flip_()
line_flip_func[1882] = flip_()
line_flip_func[1883] = flip_()
line_flip_func[1884] = flip_()
line_flip_func[1885] = flip_()
line_flip_func[1886] = flip_()
line_flip_func[1887] = flip_()
line_flip_func[1888] = flip_()
line_flip_func[1889] = flip_()
line_flip_func[1890] = flip_()
line_flip_func[1891] = flip_()
line_flip_func[1892] = flip_()
line_flip_func[1893] = flip_()
line_flip_func[1894] = flip_()
line_flip_func[1895] = flip_()
line_flip_func[1896] = flip_()
line_flip_func[1897] = flip_()
line_flip_func[1898] = flip_()
line_flip_func[1899] = flip_()
line_flip_func[1900] = flip_()
line_flip_func[1901] = flip_()
line_flip_func[1902] = flip_()
line_flip_func[1903] = flip_()
line_flip_func[1904] = flip_()
line_flip_func[1905] = flip_()
line_flip_func[1906] = flip_()
line_flip_func[1907] = flip_()
line_flip_func[1908] = flip_()
line_flip_func[1909] = flip_()
line_flip_func[1910] = flip_()
line_flip_func[1911] = flip_()
line_flip_func[1912] = flip_()
line_flip_func[1920] = flip_()
line_flip_func[1921] = flip_()
line_flip_func[1922] = flip_()
line_flip_func[1923] = flip_()
line_flip_func[1924] = flip_()
line_flip_func[1925] = flip_()
line_flip_func[1926] = flip_()
line_flip_func[1927] = flip_()
line_flip_func[1928] = flip_()
line_flip_func[1929] = flip_()
line_flip_func[1930] = flip_()
line_flip_func[1931] = flip_()
line_flip_func[1932] = flip_()
line_flip_func[1933] = flip_()
line_flip_func[1934] = flip_()
line_flip_func[1935] = flip_()
line_flip_func[1936] = flip_()
line_flip_func[1937] = flip_()
line_flip_func[1938] = flip_()
line_flip_func[1939] = flip_()
line_flip_func[1940] = flip_()
line_flip_func[1941] = flip_()
line_flip_func[1942] = flip_()
line_flip_func[1943] = flip_()
line_flip_func[1944] = flip_()
line_flip_func[1945] = flip_()
line_flip_func[1946] = flip_()
line_flip_func[1947] = flip_()
line_flip_func[1948] = flip_()
line_flip_func[1949] = flip_()
line_flip_func[1950] = flip_()
line_flip_func[1951] = flip_()
line_flip_func[1952] = flip_()
line_flip_func[1953] = flip_()
line_flip_func[1954] = flip_()
line_flip_func[1955] = flip_()
line_flip_func[1956] = flip_()
line_flip_func[1957] = flip_()
line_flip_func[1958] = flip_()
line_flip_func[1959] = flip_()
line_flip_func[1960] = flip_()
line_flip_func[1961] = flip_()
line_flip_func[1962] = flip_()
line_flip_func[1963] = flip_()
line_flip_func[1964] = flip_()
line_flip_func[1965] = flip_()
line_flip_func[1966] = flip_()
line_flip_func[1967] = flip_()
line_flip_func[1968] = flip_()
line_flip_func[1969] = flip_()
line_flip_func[1970] = flip_()
line_flip_func[1971] = flip_()
line_flip_func[1972] = flip_()
line_flip_func[1973] = flip_()
line_flip_func[1974] = flip_()
line_flip_func[1975] = flip_()
line_flip_func[1976] = flip_()
line_flip_func[1984] = flip_()
line_flip_func[1985] = flip_()
line_flip_func[1986] = flip_()
line_flip_func[1987] = flip_()
line_flip_func[1988] = flip_()
line_flip_func[1989] = flip_()
line_flip_func[1990] = flip_()
line_flip_func[1991] = flip_()
line_flip_func[1992] = flip_()
line_flip_func[1993] = flip_()
line_flip_func[1994] = flip_()
line_flip_func[1995] = flip_()
line_flip_func[1996] = flip_()
line_flip_func[1997] = flip_()
line_flip_func[1998] = flip_()
line_flip_func[1999] = flip_()
line_flip_func[2000] = flip_()
line_flip_func[2001] = flip_()
line_flip_func[2002] = flip_()
line_flip_func[2003] = flip_()
line_flip_func[2004] = flip_()
line_flip_func[2005] = flip_()
line_flip_func[2006] = flip_()
line_flip_func[2007] = flip_()
line_flip_func[2008] = flip_()
line_flip_func[2009] = flip_()
line_flip_func[2010] = flip_()
line_flip_func[2011] = flip_()
line_flip_func[2012] = flip_()
line_flip_func[2013] = flip_()
line_flip_func[2014] = flip_()
line_flip_func[2015] = flip_()
line_flip_func[2016] = flip_()
line_flip_func[2017] = flip_()
line_flip_func[2018] = flip_()
line_flip_func[2019] = flip_()
line_flip_func[2020] = flip_()
line_flip_func[2021] = flip_()
line_flip_func[2022] = flip_()
line_flip_func[2023] = flip_()
line_flip_func[2024] = flip_()
line_flip_func[2025] = flip_()
line_flip_func[2026] = flip_()
line_flip_func[2027] = flip_()
line_flip_func[2028] = flip_()
line_flip_func[2029] = flip_()
line_flip_func[2030] = flip_()
line_flip_func[2031] = flip_()
line_flip_func[2032] = flip_()
line_flip_func[2033] = flip_()
line_flip_func[2034] = flip_()
line_flip_func[2035] = flip_()
line_flip_func[2036] = flip_()
line_flip_func[2037] = flip_()
line_flip_func[2038] = flip_()
line_flip_func[2039] = flip_()
line_flip_func[2040] = flip_()
line_flip_func[2048] = flip_()
line_flip_func[2049] = flip_()
line_flip_func[2050] = flip_()
line_flip_func[2051] = flip_()
line_flip_func[2052] = flip_()
line_flip_func[2053] = flip_()
line_flip_func[2054] = flip_()
line_flip_func[2055] = flip_()
line_flip_func[2056] = flip_()
line_flip_func[2057] = flip_()
line_flip_func[2058] = flip_()
line_flip_func[2059] = flip_()
line_flip_func[2060] = flip_()
line_flip_func[2061] = flip_()
line_flip_func[2062] = flip_()
line_flip_func[2063] = flip_()
line_flip_func[2064] = flip_()
line_flip_func[2065] = flip_()
line_flip_func[2066] = flip_()
line_flip_func[2067] = flip_()
line_flip_func[2068] = flip_()
line_flip_func[2069] = flip_()
line_flip_func[2070] = flip_()
line_flip_func[2071] = flip_()
line_flip_func[2072] = flip_()
line_flip_func[2073] = flip_()
line_flip_func[2074] = flip_()
line_flip_func[2075] = flip_()
line_flip_func[2076] = flip_()
line_flip_func[2077] = flip_()
line_flip_func[2078] = flip_()
line_flip_func[2079] = flip_()
line_flip_func[2080] = flip_()
line_flip_func[2081] = flip_()
line_flip_func[2082] = flip_()
line_flip_func[2083] = flip_()
line_flip_func[2084] = flip_()
line_flip_func[2085] = flip_()
line_flip_func[2086] = flip_()
line_flip_func[2087] = flip_()
line_flip_func[2088] = flip_()
line_flip_func[2089] = flip_()
line_flip_func[2090] = flip_()
line_flip_func[2091] = flip_()
line_flip_func[2092] = flip_()
line_flip_func[2093] = flip_()
line_flip_func[2094] = flip_()
line_flip_func[2095] = flip_()
line_flip_func[2096] = flip_()
line_flip_func[2097] = flip_()
line_flip_func[2098] = flip_()
line_flip_func[2099] = flip_()
line_flip_func[2100] = flip_()
line_flip_func[2101] = flip_()
line_flip_func[2102] = flip_()
line_flip_func[2103] = flip_()
line_flip_func[2104] = flip_()
line_flip_func[2112] = flip_()
line_flip_func[2113] = flip_b7()
line_flip_func[2114] = flip_()
line_flip_func[2115] = flip_b7()
line_flip_func[2116] = flip_b7()
line_flip_func[2117] = flip_()
line_flip_func[2118] = flip_b7()
line_flip_func[2119] = flip_()
line_flip_func[2120] = flip_b7()
line_flip_func[2121] = flip_b7()
line_flip_func[2122] = flip_()
line_flip_func[2123] = flip_()
line_flip_func[2124] = flip_()
line_flip_func[2125] = flip_b7()
line_flip_func[2126] = flip_()
line_flip_func[2127] = flip_b7()
line_flip_func[2128] = flip_()
line_flip_func[2129] = flip_b7()
line_flip_func[2130] = flip_b7()
line_flip_func[2131] = flip_()
line_flip_func[2132] = flip_()
line_flip_func[2133] = flip_()
line_flip_func[2134] = flip_()
line_flip_func[2135] = flip_()
line_flip_func[2136] = flip_b7()
line_flip_func[2137] = flip_()
line_flip_func[2138] = flip_()
line_flip_func[2139] = flip_b7()
line_flip_func[2140] = flip_()
line_flip_func[2141] = flip_b7()
line_flip_func[2142] = flip_()
line_flip_func[2143] = flip_b7()
line_flip_func[2144] = flip_b7()
line_flip_func[2145] = flip_()
line_flip_func[2146] = flip_()
line_flip_func[2147] = flip_()
line_flip_func[2148] = flip_()
line_flip_func[2149] = flip_()
line_flip_func[2150] = flip_()
line_flip_func[2151] = flip_()
line_flip_func[2152] = flip_b7()
line_flip_func[2153] = flip_()
line_flip_func[2154] = flip_()
line_flip_func[2155] = flip_()
line_flip_func[2156] = flip_b7()
line_flip_func[2157] = flip_()
line_flip_func[2158] = flip_()
line_flip_func[2159] = flip_b7()
line_flip_func[2160] = flip_()
line_flip_func[2161] = flip_b7()
line_flip_func[2162] = flip_()
line_flip_func[2163] = flip_b7()
line_flip_func[2164] = flip_b7()
line_flip_func[2165] = flip_()
line_flip_func[2166] = flip_()
line_flip_func[2167] = flip_()
line_flip_func[2168] = flip_()
line_flip_func[2176] = flip_()
line_flip_func[2177] = flip_b6()
line_flip_func[2178] = flip_c7()
line_flip_func[2179] = flip_b6_c7()
line_flip_func[2180] = flip_b6_c7()
line_flip_func[2181] = flip_()
line_flip_func[2182] = flip_b6()
line_flip_func[2183] = flip_c7()
line_flip_func[2184] = flip_b6_c7()
line_flip_func[2185] = flip_b6_c7()
line_flip_func[2186] = flip_c7()
line_flip_func[2187] = flip_()
line_flip_func[2188] = flip_c7()
line_flip_func[2189] = flip_b6_c7()
line_flip_func[2190] = flip_()
line_flip_func[2191] = flip_b6()
line_flip_func[2192] = flip_c7()
line_flip_func[2193] = flip_b6_c7()
line_flip_func[2194] = flip_b6_c7()
line_flip_func[2195] = flip_c7()
line_flip_func[2196] = flip_()
line_flip_func[2197] = flip_()
line_flip_func[2198] = flip_()
line_flip_func[2199] = flip_c7()
line_flip_func[2200] = flip_b6_c7()
line_flip_func[2201] = flip_()
line_flip_func[2202] = flip_c7()
line_flip_func[2203] = flip_b6_c7()
line_flip_func[2204] = flip_()
line_flip_func[2205] = flip_b6()
line_flip_func[2206] = flip_c7()
line_flip_func[2207] = flip_b6_c7()
line_flip_func[2208] = flip_b6_c7()
line_flip_func[2209] = flip_c7()
line_flip_func[2210] = flip_()
line_flip_func[2211] = flip_()
line_flip_func[2212] = flip_()
line_flip_func[2213] = flip_()
line_flip_func[2214] = flip_()
line_flip_func[2215] = flip_c7()
line_flip_func[2216] = flip_b6_c7()
line_flip_func[2217] = flip_()
line_flip_func[2218] = flip_()
line_flip_func[2219] = flip_c7()
line_flip_func[2220] = flip_b6_c7()
line_flip_func[2221] = flip_()
line_flip_func[2222] = flip_c7()
line_flip_func[2223] = flip_b6_c7()
line_flip_func[2224] = flip_()
line_flip_func[2225] = flip_b6()
line_flip_func[2226] = flip_c7()
line_flip_func[2227] = flip_b6_c7()
line_flip_func[2228] = flip_b6_c7()
line_flip_func[2229] = flip_c7()
line_flip_func[2230] = flip_()
line_flip_func[2231] = flip_()
line_flip_func[2232] = flip_()
line_flip_func[2240] = flip_()
line_flip_func[2241] = flip_b5()
line_flip_func[2242] = flip_c6()
line_flip_func[2243] = flip_b5_c6()
line_flip_func[2244] = flip_b5_c6()
line_flip_func[2245] = flip_d7()
line_flip_func[2246] = flip_b5_d7()
line_flip_func[2247] = flip_c6_d7()
line_flip_func[2248] = flip_b5_c6_d7()
line_flip_func[2249] = flip_b5_c6_d7()
line_flip_func[2250] = flip_c6_d7()
line_flip_func[2251] = flip_()
line_flip_func[2252] = flip_c6()
line_flip_func[2253] = flip_b5_c6()
line_flip_func[2254] = flip_d7()
line_flip_func[2255] = flip_b5_d7()
line_flip_func[2256] = flip_c6_d7()
line_flip_func[2257] = flip_b5_c6_d7()
line_flip_func[2258] = flip_b5_c6_d7()
line_flip_func[2259] = flip_c6_d7()
line_flip_func[2260] = flip_d7()
line_flip_func[2261] = flip_()
line_flip_func[2262] = flip_d7()
line_flip_func[2263] = flip_c6_d7()
line_flip_func[2264] = flip_b5_c6_d7()
line_flip_func[2265] = flip_()
line_flip_func[2266] = flip_c6()
line_flip_func[2267] = flip_b5_c6()
line_flip_func[2268] = flip_d7()
line_flip_func[2269] = flip_b5_d7()
line_flip_func[2270] = flip_c6_d7()
line_flip_func[2271] = flip_b5_c6_d7()
line_flip_func[2272] = flip_b5_c6_d7()
line_flip_func[2273] = flip_c6_d7()
line_flip_func[2274] = flip_d7()
line_flip_func[2275] = flip_()
line_flip_func[2276] = flip_()
line_flip_func[2277] = flip_()
line_flip_func[2278] = flip_d7()
line_flip_func[2279] = flip_c6_d7()
line_flip_func[2280] = flip_b5_c6_d7()
line_flip_func[2281] = flip_()
line_flip_func[2282] = flip_d7()
line_flip_func[2283] = flip_c6_d7()
line_flip_func[2284] = flip_b5_c6_d7()
line_flip_func[2285] = flip_()
line_flip_func[2286] = flip_c6()
line_flip_func[2287] = flip_b5_c6()
line_flip_func[2288] = flip_d7()
line_flip_func[2289] = flip_b5_d7()
line_flip_func[2290] = flip_c6_d7()
line_flip_func[2291] = flip_b5_c6_d7()
line_flip_func[2292] = flip_b5_c6_d7()
line_flip_func[2293] = flip_c6_d7()
line_flip_func[2294] = flip_d7()
line_flip_func[2295] = flip_()
line_flip_func[2296] = flip_()
line_flip_func[2304] = flip_()
line_flip_func[2305] = flip_b4()
line_flip_func[2306] = flip_c5()
line_flip_func[2307] = flip_b4_c5()
line_flip_func[2308] = flip_b4_c5()
line_flip_func[2309] = flip_d6()
line_flip_func[2310] = flip_b4_d6()
line_flip_func[2311] = flip_c5_d6()
line_flip_func[2312] = flip_b4_c5_d6()
line_flip_func[2313] = flip_b4_c5_d6()
line_flip_func[2314] = flip_c5_d6()
line_flip_func[2315] = flip_e7()
line_flip_func[2316] = flip_c5_e7()
line_flip_func[2317] = flip_b4_c5_e7()
line_flip_func[2318] = flip_d6_e7()
line_flip_func[2319] = flip_b4_d6_e7()
line_flip_func[2320] = flip_c5_d6_e7()
line_flip_func[2321] = flip_b4_c5_d6_e7()
line_flip_func[2322] = flip_b4_c5_d6_e7()
line_flip_func[2323] = flip_c5_d6_e7()
line_flip_func[2324] = flip_d6_e7()
line_flip_func[2325] = flip_()
line_flip_func[2326] = flip_d6()
line_flip_func[2327] = flip_c5_d6()
line_flip_func[2328] = flip_b4_c5_d6()
line_flip_func[2329] = flip_e7()
line_flip_func[2330] = flip_c5_e7()
line_flip_func[2331] = flip_b4_c5_e7()
line_flip_func[2332] = flip_d6_e7()
line_flip_func[2333] = flip_b4_d6_e7()
line_flip_func[2334] = flip_c5_d6_e7()
line_flip_func[2335] = flip_b4_c5_d6_e7()
line_flip_func[2336] = flip_b4_c5_d6_e7()
line_flip_func[2337] = flip_c5_d6_e7()
line_flip_func[2338] = flip_d6_e7()
line_flip_func[2339] = flip_e7()
line_flip_func[2340] = flip_()
line_flip_func[2341] = flip_e7()
line_flip_func[2342] = flip_d6_e7()
line_flip_func[2343] = flip_c5_d6_e7()
line_flip_func[2344] = flip_b4_c5_d6_e7()
line_flip_func[2345] = flip_()
line_flip_func[2346] = flip_d6()
line_flip_func[2347] = flip_c5_d6()
line_flip_func[2348] = flip_b4_c5_d6()
line_flip_func[2349] = flip_e7()
line_flip_func[2350] = flip_c5_e7()
line_flip_func[2351] = flip_b4_c5_e7()
line_flip_func[2352] = flip_d6_e7()
line_flip_func[2353] = flip_b4_d6_e7()
line_flip_func[2354] = flip_c5_d6_e7()
line_flip_func[2355] = flip_b4_c5_d6_e7()
line_flip_func[2356] = flip_b4_c5_d6_e7()
line_flip_func[2357] = flip_c5_d6_e7()
line_flip_func[2358] = flip_d6_e7()
line_flip_func[2359] = flip_e7()
line_flip_func[2360] = flip_()
line_flip_func[2368] = flip_()
line_flip_func[2369] = flip_b3()
line_flip_func[2370] = flip_c4()
line_flip_func[2371] = flip_b3_c4()
line_flip_func[2372] = flip_b3_c4()
line_flip_func[2373] = flip_d5()
line_flip_func[2374] = flip_b3_d5()
line_flip_func[2375] = flip_c4_d5()
line_flip_func[2376] = flip_b3_c4_d5()
line_flip_func[2377] = flip_b3_c4_d5()
line_flip_func[2378] = flip_c4_d5()
line_flip_func[2379] = flip_e6()
line_flip_func[2380] = flip_c4_e6()
line_flip_func[2381] = flip_b3_c4_e6()
line_flip_func[2382] = flip_d5_e6()
line_flip_func[2383] = flip_b3_d5_e6()
line_flip_func[2384] = flip_c4_d5_e6()
line_flip_func[2385] = flip_b3_c4_d5_e6()
line_flip_func[2386] = flip_b3_c4_d5_e6()
line_flip_func[2387] = flip_c4_d5_e6()
line_flip_func[2388] = flip_d5_e6()
line_flip_func[2389] = flip_f7()
line_flip_func[2390] = flip_d5_f7()
line_flip_func[2391] = flip_c4_d5_f7()
line_flip_func[2392] = flip_b3_c4_d5_f7()
line_flip_func[2393] = flip_e6_f7()
line_flip_func[2394] = flip_c4_e6_f7()
line_flip_func[2395] = flip_b3_c4_e6_f7()
line_flip_func[2396] = flip_d5_e6_f7()
line_flip_func[2397] = flip_b3_d5_e6_f7()
line_flip_func[2398] = flip_c4_d5_e6_f7()
line_flip_func[2399] = flip_b3_c4_d5_e6_f7()
line_flip_func[2400] = flip_b3_c4_d5_e6_f7()
line_flip_func[2401] = flip_c4_d5_e6_f7()
line_flip_func[2402] = flip_d5_e6_f7()
line_flip_func[2403] = flip_e6_f7()
line_flip_func[2404] = flip_()
line_flip_func[2405] = flip_e6()
line_flip_func[2406] = flip_d5_e6()
line_flip_func[2407] = flip_c4_d5_e6()
line_flip_func[2408] = flip_b3_c4_d5_e6()
line_flip_func[2409] = flip_f7()
line_flip_func[2410] = flip_d5_f7()
line_flip_func[2411] = flip_c4_d5_f7()
line_flip_func[2412] = flip_b3_c4_d5_f7()
line_flip_func[2413] = flip_e6_f7()
line_flip_func[2414] = flip_c4_e6_f7()
line_flip_func[2415] = flip_b3_c4_e6_f7()
line_flip_func[2416] = flip_d5_e6_f7()
line_flip_func[2417] = flip_b3_d5_e6_f7()
line_flip_func[2418] = flip_c4_d5_e6_f7()
line_flip_func[2419] = flip_b3_c4_d5_e6_f7()
line_flip_func[2420] = flip_b3_c4_d5_e6_f7()
line_flip_func[2421] = flip_c4_d5_e6_f7()
line_flip_func[2422] = flip_d5_e6_f7()
line_flip_func[2423] = flip_e6_f7()
line_flip_func[2424] = flip_f7()
line_flip_func[2432] = flip_()
line_flip_func[2433] = flip_b2()
line_flip_func[2434] = flip_c3()
line_flip_func[2435] = flip_b2_c3()
line_flip_func[2436] = flip_b2_c3()
line_flip_func[2437] = flip_d4()
line_flip_func[2438] = flip_b2_d4()
line_flip_func[2439] = flip_c3_d4()
line_flip_func[2440] = flip_b2_c3_d4()
line_flip_func[2441] = flip_b2_c3_d4()
line_flip_func[2442] = flip_c3_d4()
line_flip_func[2443] = flip_e5()
line_flip_func[2444] = flip_c3_e5()
line_flip_func[2445] = flip_b2_c3_e5()
line_flip_func[2446] = flip_d4_e5()
line_flip_func[2447] = flip_b2_d4_e5()
line_flip_func[2448] = flip_c3_d4_e5()
line_flip_func[2449] = flip_b2_c3_d4_e5()
line_flip_func[2450] = flip_b2_c3_d4_e5()
line_flip_func[2451] = flip_c3_d4_e5()
line_flip_func[2452] = flip_d4_e5()
line_flip_func[2453] = flip_f6()
line_flip_func[2454] = flip_d4_f6()
line_flip_func[2455] = flip_c3_d4_f6()
line_flip_func[2456] = flip_b2_c3_d4_f6()
line_flip_func[2457] = flip_e5_f6()
line_flip_func[2458] = flip_c3_e5_f6()
line_flip_func[2459] = flip_b2_c3_e5_f6()
line_flip_func[2460] = flip_d4_e5_f6()
line_flip_func[2461] = flip_b2_d4_e5_f6()
line_flip_func[2462] = flip_c3_d4_e5_f6()
line_flip_func[2463] = flip_b2_c3_d4_e5_f6()
line_flip_func[2464] = flip_b2_c3_d4_e5_f6()
line_flip_func[2465] = flip_c3_d4_e5_f6()
line_flip_func[2466] = flip_d4_e5_f6()
line_flip_func[2467] = flip_e5_f6()
line_flip_func[2468] = flip_g7()
line_flip_func[2469] = flip_e5_g7()
line_flip_func[2470] = flip_d4_e5_g7()
line_flip_func[2471] = flip_c3_d4_e5_g7()
line_flip_func[2472] = flip_b2_c3_d4_e5_g7()
line_flip_func[2473] = flip_f6_g7()
line_flip_func[2474] = flip_d4_f6_g7()
line_flip_func[2475] = flip_c3_d4_f6_g7()
line_flip_func[2476] = flip_b2_c3_d4_f6_g7()
line_flip_func[2477] = flip_e5_f6_g7()
line_flip_func[2478] = flip_c3_e5_f6_g7()
line_flip_func[2479] = flip_b2_c3_e5_f6_g7()
line_flip_func[2480] = flip_d4_e5_f6_g7()
line_flip_func[2481] = flip_b2_d4_e5_f6_g7()
line_flip_func[2482] = flip_c3_d4_e5_f6_g7()
line_flip_func[2483] = flip_b2_c3_d4_e5_f6_g7()
line_flip_func[2484] = flip_b2_c3_d4_e5_f6_g7()
line_flip_func[2485] = flip_c3_d4_e5_f6_g7()
line_flip_func[2486] = flip_d4_e5_f6_g7()
line_flip_func[2487] = flip_e5_f6_g7()
line_flip_func[2488] = flip_f6_g7()
line_flip_func[2496] = flip_()
line_flip_func[2497] = flip_c2()
line_flip_func[2498] = flip_d3()
line_flip_func[2499] = flip_c2_d3()
line_flip_func[2500] = flip_c2_d3()
line_flip_func[2501] = flip_e4()
line_flip_func[2502] = flip_c2_e4()
line_flip_func[2503] = flip_d3_e4()
line_flip_func[2504] = flip_c2_d3_e4()
line_flip_func[2505] = flip_c2_d3_e4()
line_flip_func[2506] = flip_d3_e4()
line_flip_func[2507] = flip_f5()
line_flip_func[2508] = flip_d3_f5()
line_flip_func[2509] = flip_c2_d3_f5()
line_flip_func[2510] = flip_e4_f5()
line_flip_func[2511] = flip_c2_e4_f5()
line_flip_func[2512] = flip_d3_e4_f5()
line_flip_func[2513] = flip_c2_d3_e4_f5()
line_flip_func[2514] = flip_c2_d3_e4_f5()
line_flip_func[2515] = flip_d3_e4_f5()
line_flip_func[2516] = flip_e4_f5()
line_flip_func[2517] = flip_g6()
line_flip_func[2518] = flip_e4_g6()
line_flip_func[2519] = flip_d3_e4_g6()
line_flip_func[2520] = flip_c2_d3_e4_g6()
line_flip_func[2521] = flip_f5_g6()
line_flip_func[2522] = flip_d3_f5_g6()
line_flip_func[2523] = flip_c2_d3_f5_g6()
line_flip_func[2524] = flip_e4_f5_g6()
line_flip_func[2525] = flip_c2_e4_f5_g6()
line_flip_func[2526] = flip_d3_e4_f5_g6()
line_flip_func[2527] = flip_c2_d3_e4_f5_g6()
line_flip_func[2528] = flip_c2_d3_e4_f5_g6()
line_flip_func[2529] = flip_d3_e4_f5_g6()
line_flip_func[2530] = flip_e4_f5_g6()
line_flip_func[2531] = flip_f5_g6()
line_flip_func[2532] = flip_()
line_flip_func[2533] = flip_f5()
line_flip_func[2534] = flip_e4_f5()
line_flip_func[2535] = flip_d3_e4_f5()
line_flip_func[2536] = flip_c2_d3_e4_f5()
line_flip_func[2537] = flip_g6()
line_flip_func[2538] = flip_e4_g6()
line_flip_func[2539] = flip_d3_e4_g6()
line_flip_func[2540] = flip_c2_d3_e4_g6()
line_flip_func[2541] = flip_f5_g6()
line_flip_func[2542] = flip_d3_f5_g6()
line_flip_func[2543] = flip_c2_d3_f5_g6()
line_flip_func[2544] = flip_e4_f5_g6()
line_flip_func[2545] = flip_c2_e4_f5_g6()
line_flip_func[2546] = flip_d3_e4_f5_g6()
line_flip_func[2547] = flip_c2_d3_e4_f5_g6()
line_flip_func[2548] = flip_c2_d3_e4_f5_g6()
line_flip_func[2549] = flip_d3_e4_f5_g6()
line_flip_func[2550] = flip_e4_f5_g6()
line_flip_func[2551] = flip_f5_g6()
line_flip_func[2552] = flip_g6()
line_flip_func[2560] = flip_()
line_flip_func[2561] = flip_d2()
line_flip_func[2562] = flip_e3()
line_flip_func[2563] = flip_d2_e3()
line_flip_func[2564] = flip_d2_e3()
line_flip_func[2565] = flip_f4()
line_flip_func[2566] = flip_d2_f4()
line_flip_func[2567] = flip_e3_f4()
line_flip_func[2568] = flip_d2_e3_f4()
line_flip_func[2569] = flip_d2_e3_f4()
line_flip_func[2570] = flip_e3_f4()
line_flip_func[2571] = flip_g5()
line_flip_func[2572] = flip_e3_g5()
line_flip_func[2573] = flip_d2_e3_g5()
line_flip_func[2574] = flip_f4_g5()
line_flip_func[2575] = flip_d2_f4_g5()
line_flip_func[2576] = flip_e3_f4_g5()
line_flip_func[2577] = flip_d2_e3_f4_g5()
line_flip_func[2578] = flip_d2_e3_f4_g5()
line_flip_func[2579] = flip_e3_f4_g5()
line_flip_func[2580] = flip_f4_g5()
line_flip_func[2581] = flip_()
line_flip_func[2582] = flip_f4()
line_flip_func[2583] = flip_e3_f4()
line_flip_func[2584] = flip_d2_e3_f4()
line_flip_func[2585] = flip_g5()
line_flip_func[2586] = flip_e3_g5()
line_flip_func[2587] = flip_d2_e3_g5()
line_flip_func[2588] = flip_f4_g5()
line_flip_func[2589] = flip_d2_f4_g5()
line_flip_func[2590] = flip_e3_f4_g5()
line_flip_func[2591] = flip_d2_e3_f4_g5()
line_flip_func[2592] = flip_d2_e3_f4_g5()
line_flip_func[2593] = flip_e3_f4_g5()
line_flip_func[2594] = flip_f4_g5()
line_flip_func[2595] = flip_g5()
line_flip_func[2596] = flip_()
line_flip_func[2597] = flip_g5()
line_flip_func[2598] = flip_f4_g5()
line_flip_func[2599] = flip_e3_f4_g5()
line_flip_func[2600] = flip_d2_e3_f4_g5()
line_flip_func[2601] = flip_()
line_flip_func[2602] = flip_f4()
line_flip_func[2603] = flip_e3_f4()
line_flip_func[2604] = flip_d2_e3_f4()
line_flip_func[2605] = flip_g5()
line_flip_func[2606] = flip_e3_g5()
line_flip_func[2607] = flip_d2_e3_g5()
line_flip_func[2608] = flip_f4_g5()
line_flip_func[2609] = flip_d2_f4_g5()
line_flip_func[2610] = flip_e3_f4_g5()
line_flip_func[2611] = flip_d2_e3_f4_g5()
line_flip_func[2612] = flip_d2_e3_f4_g5()
line_flip_func[2613] = flip_e3_f4_g5()
line_flip_func[2614] = flip_f4_g5()
line_flip_func[2615] = flip_g5()
line_flip_func[2616] = flip_()
line_flip_func[2624] = flip_()
line_flip_func[2625] = flip_e2()
line_flip_func[2626] = flip_f3()
line_flip_func[2627] = flip_e2_f3()
line_flip_func[2628] = flip_e2_f3()
line_flip_func[2629] = flip_g4()
line_flip_func[2630] = flip_e2_g4()
line_flip_func[2631] = flip_f3_g4()
line_flip_func[2632] = flip_e2_f3_g4()
line_flip_func[2633] = flip_e2_f3_g4()
line_flip_func[2634] = flip_f3_g4()
line_flip_func[2635] = flip_()
line_flip_func[2636] = flip_f3()
line_flip_func[2637] = flip_e2_f3()
line_flip_func[2638] = flip_g4()
line_flip_func[2639] = flip_e2_g4()
line_flip_func[2640] = flip_f3_g4()
line_flip_func[2641] = flip_e2_f3_g4()
line_flip_func[2642] = flip_e2_f3_g4()
line_flip_func[2643] = flip_f3_g4()
line_flip_func[2644] = flip_g4()
line_flip_func[2645] = flip_()
line_flip_func[2646] = flip_g4()
line_flip_func[2647] = flip_f3_g4()
line_flip_func[2648] = flip_e2_f3_g4()
line_flip_func[2649] = flip_()
line_flip_func[2650] = flip_f3()
line_flip_func[2651] = flip_e2_f3()
line_flip_func[2652] = flip_g4()
line_flip_func[2653] = flip_e2_g4()
line_flip_func[2654] = flip_f3_g4()
line_flip_func[2655] = flip_e2_f3_g4()
line_flip_func[2656] = flip_e2_f3_g4()
line_flip_func[2657] = flip_f3_g4()
line_flip_func[2658] = flip_g4()
line_flip_func[2659] = flip_()
line_flip_func[2660] = flip_()
line_flip_func[2661] = flip_()
line_flip_func[2662] = flip_g4()
line_flip_func[2663] = flip_f3_g4()
line_flip_func[2664] = flip_e2_f3_g4()
line_flip_func[2665] = flip_()
line_flip_func[2666] = flip_g4()
line_flip_func[2667] = flip_f3_g4()
line_flip_func[2668] = flip_e2_f3_g4()
line_flip_func[2669] = flip_()
line_flip_func[2670] = flip_f3()
line_flip_func[2671] = flip_e2_f3()
line_flip_func[2672] = flip_g4()
line_flip_func[2673] = flip_e2_g4()
line_flip_func[2674] = flip_f3_g4()
line_flip_func[2675] = flip_e2_f3_g4()
line_flip_func[2676] = flip_e2_f3_g4()
line_flip_func[2677] = flip_f3_g4()
line_flip_func[2678] = flip_g4()
line_flip_func[2679] = flip_()
line_flip_func[2680] = flip_()
line_flip_func[2688] = flip_()
line_flip_func[2689] = flip_f2()
line_flip_func[2690] = flip_g3()
line_flip_func[2691] = flip_f2_g3()
line_flip_func[2692] = flip_f2_g3()
line_flip_func[2693] = flip_()
line_flip_func[2694] = flip_f2()
line_flip_func[2695] = flip_g3()
line_flip_func[2696] = flip_f2_g3()
line_flip_func[2697] = flip_f2_g3()
line_flip_func[2698] = flip_g3()
line_flip_func[2699] = flip_()
line_flip_func[2700] = flip_g3()
line_flip_func[2701] = flip_f2_g3()
line_flip_func[2702] = flip_()
line_flip_func[2703] = flip_f2()
line_flip_func[2704] = flip_g3()
line_flip_func[2705] = flip_f2_g3()
line_flip_func[2706] = flip_f2_g3()
line_flip_func[2707] = flip_g3()
line_flip_func[2708] = flip_()
line_flip_func[2709] = flip_()
line_flip_func[2710] = flip_()
line_flip_func[2711] = flip_g3()
line_flip_func[2712] = flip_f2_g3()
line_flip_func[2713] = flip_()
line_flip_func[2714] = flip_g3()
line_flip_func[2715] = flip_f2_g3()
line_flip_func[2716] = flip_()
line_flip_func[2717] = flip_f2()
line_flip_func[2718] = flip_g3()
line_flip_func[2719] = flip_f2_g3()
line_flip_func[2720] = flip_f2_g3()
line_flip_func[2721] = flip_g3()
line_flip_func[2722] = flip_()
line_flip_func[2723] = flip_()
line_flip_func[2724] = flip_()
line_flip_func[2725] = flip_()
line_flip_func[2726] = flip_()
line_flip_func[2727] = flip_g3()
line_flip_func[2728] = flip_f2_g3()
line_flip_func[2729] = flip_()
line_flip_func[2730] = flip_()
line_flip_func[2731] = flip_g3()
line_flip_func[2732] = flip_f2_g3()
line_flip_func[2733] = flip_()
line_flip_func[2734] = flip_g3()
line_flip_func[2735] = flip_f2_g3()
line_flip_func[2736] = flip_()
line_flip_func[2737] = flip_f2()
line_flip_func[2738] = flip_g3()
line_flip_func[2739] = flip_f2_g3()
line_flip_func[2740] = flip_f2_g3()
line_flip_func[2741] = flip_g3()
line_flip_func[2742] = flip_()
line_flip_func[2743] = flip_()
line_flip_func[2744] = flip_()
line_flip_func[2752] = flip_()
line_flip_func[2753] = flip_g2()
line_flip_func[2754] = flip_()
line_flip_func[2755] = flip_g2()
line_flip_func[2756] = flip_g2()
line_flip_func[2757] = flip_()
line_flip_func[2758] = flip_g2()
line_flip_func[2759] = flip_()
line_flip_func[2760] = flip_g2()
line_flip_func[2761] = flip_g2()
line_flip_func[2762] = flip_()
line_flip_func[2763] = flip_()
line_flip_func[2764] = flip_()
line_flip_func[2765] = flip_g2()
line_flip_func[2766] = flip_()
line_flip_func[2767] = flip_g2()
line_flip_func[2768] = flip_()
line_flip_func[2769] = flip_g2()
line_flip_func[2770] = flip_g2()
line_flip_func[2771] = flip_()
line_flip_func[2772] = flip_()
line_flip_func[2773] = flip_()
line_flip_func[2774] = flip_()
line_flip_func[2775] = flip_()
line_flip_func[2776] = flip_g2()
line_flip_func[2777] = flip_()
line_flip_func[2778] = flip_()
line_flip_func[2779] = flip_g2()
line_flip_func[2780] = flip_()
line_flip_func[2781] = flip_g2()
line_flip_func[2782] = flip_()
line_flip_func[2783] = flip_g2()
line_flip_func[2784] = flip_g2()
line_flip_func[2785] = flip_()
line_flip_func[2786] = flip_()
line_flip_func[2787] = flip_()
line_flip_func[2788] = flip_()
line_flip_func[2789] = flip_()
line_flip_func[2790] = flip_()
line_flip_func[2791] = flip_()
line_flip_func[2792] = flip_g2()
line_flip_func[2793] = flip_()
line_flip_func[2794] = flip_()
line_flip_func[2795] = flip_()
line_flip_func[2796] = flip_g2()
line_flip_func[2797] = flip_()
line_flip_func[2798] = flip_()
line_flip_func[2799] = flip_g2()
line_flip_func[2800] = flip_()
line_flip_func[2801] = flip_g2()
line_flip_func[2802] = flip_()
line_flip_func[2803] = flip_g2()
line_flip_func[2804] = flip_g2()
line_flip_func[2805] = flip_()
line_flip_func[2806] = flip_()
line_flip_func[2807] = flip_()
line_flip_func[2808] = flip_()
line_flip_func[2816] = flip_()
line_flip_func[2817] = flip_()
line_flip_func[2818] = flip_()
line_flip_func[2819] = flip_()
line_flip_func[2820] = flip_()
line_flip_func[2821] = flip_()
line_flip_func[2822] = flip_()
line_flip_func[2823] = flip_()
line_flip_func[2824] = flip_()
line_flip_func[2825] = flip_()
line_flip_func[2826] = flip_()
line_flip_func[2827] = flip_()
line_flip_func[2828] = flip_()
line_flip_func[2829] = flip_()
line_flip_func[2830] = flip_()
line_flip_func[2831] = flip_()
line_flip_func[2832] = flip_()
line_flip_func[2833] = flip_()
line_flip_func[2834] = flip_()
line_flip_func[2835] = flip_()
line_flip_func[2836] = flip_()
line_flip_func[2837] = flip_()
line_flip_func[2838] = flip_()
line_flip_func[2839] = flip_()
line_flip_func[2840] = flip_()
line_flip_func[2841] = flip_()
line_flip_func[2842] = flip_()
line_flip_func[2843] = flip_()
line_flip_func[2844] = flip_()
line_flip_func[2845] = flip_()
line_flip_func[2846] = flip_()
line_flip_func[2847] = flip_()
line_flip_func[2848] = flip_()
line_flip_func[2849] = flip_()
line_flip_func[2850] = flip_()
line_flip_func[2851] = flip_()
line_flip_func[2852] = flip_()
line_flip_func[2853] = flip_()
line_flip_func[2854] = flip_()
line_flip_func[2855] = flip_()
line_flip_func[2856] = flip_()
line_flip_func[2857] = flip_()
line_flip_func[2858] = flip_()
line_flip_func[2859] = flip_()
line_flip_func[2860] = flip_()
line_flip_func[2861] = flip_()
line_flip_func[2862] = flip_()
line_flip_func[2863] = flip_()
line_flip_func[2864] = flip_()
line_flip_func[2865] = flip_()
line_flip_func[2866] = flip_()
line_flip_func[2867] = flip_()
line_flip_func[2868] = flip_()
line_flip_func[2869] = flip_()
line_flip_func[2870] = flip_()
line_flip_func[2871] = flip_()
line_flip_func[2872] = flip_()
line_flip_func[2880] = flip_()
line_flip_func[2881] = flip_()
line_flip_func[2882] = flip_()
line_flip_func[2883] = flip_()
line_flip_func[2884] = flip_()
line_flip_func[2885] = flip_()
line_flip_func[2886] = flip_()
line_flip_func[2887] = flip_()
line_flip_func[2888] = flip_()
line_flip_func[2889] = flip_()
line_flip_func[2890] = flip_()
line_flip_func[2891] = flip_()
line_flip_func[2892] = flip_()
line_flip_func[2893] = flip_()
line_flip_func[2894] = flip_()
line_flip_func[2895] = flip_()
line_flip_func[2896] = flip_()
line_flip_func[2897] = flip_()
line_flip_func[2898] = flip_()
line_flip_func[2899] = flip_()
line_flip_func[2900] = flip_()
line_flip_func[2901] = flip_()
line_flip_func[2902] = flip_()
line_flip_func[2903] = flip_()
line_flip_func[2904] = flip_()
line_flip_func[2905] = flip_()
line_flip_func[2906] = flip_()
line_flip_func[2907] = flip_()
line_flip_func[2908] = flip_()
line_flip_func[2909] = flip_()
line_flip_func[2910] = flip_()
line_flip_func[2911] = flip_()
line_flip_func[2912] = flip_()
line_flip_func[2913] = flip_()
line_flip_func[2914] = flip_()
line_flip_func[2915] = flip_()
line_flip_func[2916] = flip_()
line_flip_func[2917] = flip_()
line_flip_func[2918] = flip_()
line_flip_func[2919] = flip_()
line_flip_func[2920] = flip_()
line_flip_func[2921] = flip_()
line_flip_func[2922] = flip_()
line_flip_func[2923] = flip_()
line_flip_func[2924] = flip_()
line_flip_func[2925] = flip_()
line_flip_func[2926] = flip_()
line_flip_func[2927] = flip_()
line_flip_func[2928] = flip_()
line_flip_func[2929] = flip_()
line_flip_func[2930] = flip_()
line_flip_func[2931] = flip_()
line_flip_func[2932] = flip_()
line_flip_func[2933] = flip_()
line_flip_func[2934] = flip_()
line_flip_func[2935] = flip_()
line_flip_func[2936] = flip_()

#gen_funcs()
#stop

# italian line
italian = 'F5D6C4D3E6F4E3F3C6F6G5G6E7F7C3G4D2C5H3H4E2F2G3C1C2E1D1B3F1G1F8D7C7G7A3B4B6B1H8B5A6A5A4B7A8G8H7H6H5G2H1H2A1D8E8C8B2A2B8A7'
human_moves = [italian[i*2:(i+1)*2] for i in range(len(italian)//2)]
moves = ['ABCDEFGH'.index(h[0]) + 8 * (int(h[1])-1) for h in human_moves]

# setup initial board state
t0 = time.time()

for x in range(1000):
    init_state()

    turn = BLACK
    put_d5().go()
    put_e4().go()
    turn = WHITE
    put_d4().go()
    put_e5().go()
#    check_board()
    turn = BLACK

    for mv in moves:
        move_table[mv].go()
#        check_board()
        turn = -turn

t = 60000 // (time.time()-t0)

check_board()

nx = sum(str_state(states()[l]).count('2') for l in range(8))
no = sum(str_state(states()[l]).count('0') for l in range(8))

print(f'{nx}-{no}')
print()

print('moves/sec: %d' % t)
