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
            print(f"        state_{l} += 2 * turn * {value}")
        print()

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
        state_7 += 2 * turn * 999
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_1 += 2 * turn * 351
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_4 += 2 * turn * 1089
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 336
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

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
        state_0 += 2 * turn * 1065
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_3 += 2 * turn * 1
        state_8 += 2 * turn * 837
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

class flip_d3_e3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_12
        global state_22
        global state_40
        state_2 += 2 * turn * 108
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 1065
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_2 += 2 * turn * 117
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9

class flip_f6_g6(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        global state_14
        global state_27
        global state_39
        state_5 += 2 * turn * 972
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_5 += 2 * turn * 120
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 1080
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 39
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 1092
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 39
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 1083
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

class flip_d7_e7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_12
        global state_26
        global state_36
        state_6 += 2 * turn * 108
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

class flip_f7_g6(Flip):
    def go(self):
        global state_6
        global state_13
        global state_27
        global state_37
        global state_5
        global state_14
        global state_39
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 12
        state_37 += 2 * turn * 243
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_39 += 2 * turn * 243

class flip_a3_a4(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_3
        global state_19
        global state_35
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 36
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 279
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 120
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 360
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_h6_h7(Flip):
    def go(self):
        global state_5
        global state_15
        global state_28
        global state_40
        global state_6
        global state_29
        global state_39
        state_5 += 2 * turn * 2187
        state_15 += 2 * turn * 972
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

class flip_d4_d5(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_23
        global state_37
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 108
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

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
        state_6 += 2 * turn * 1083
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_c5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9

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
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 1008
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

class flip_b3_c4(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_10
        global state_21
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 12
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 1008
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

class flip_e5_e7(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_6
        global state_26
        global state_36
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 810
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

class flip_f4_g5(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_4
        global state_14
        global state_26
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 108
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27

class flip_d2_f4(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_3
        global state_13
        global state_24
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 30
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81

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
        state_0 += 2 * turn * 846
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_7 += 2 * turn * 1092
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_7 += 2 * turn * 1062
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 837
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_3 += 2 * turn * 1
        state_8 += 2 * turn * 999
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_2 += 2 * turn * 1089
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_1 += 2 * turn * 849
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 1053
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_1 += 2 * turn * 111
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3

class flip_d5_f7(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_6
        global state_13
        global state_27
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 270
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

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
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 1062
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 336
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

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
        state_7 += 2 * turn * 336
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 111
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_7 += 2 * turn * 1083
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

class flip_h5_h6(Flip):
    def go(self):
        global state_4
        global state_15
        global state_27
        global state_41
        global state_5
        global state_28
        global state_40
        state_4 += 2 * turn * 2187
        state_15 += 2 * turn * 324
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

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
        state_2 += 2 * turn * 1008
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_3 += 2 * turn * 1062
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 1062
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 282
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_5 += 2 * turn * 1011
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_e6_e7(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_6
        global state_26
        global state_36
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 972
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

class flip_f5_g5(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_14
        global state_26
        global state_40
        state_4 += 2 * turn * 972
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_3 += 2 * turn * 93
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_1 += 2 * turn * 999
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 999
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 1092
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_f7(Flip):
    def go(self):
        global state_6
        global state_13
        global state_27
        global state_37
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_c4_d3(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_2
        global state_11
        global state_39
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 36
        state_37 += 2 * turn * 9
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_39 += 2 * turn * 9

class flip_d5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

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
        state_2 += 2 * turn * 360
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

class flip_b5_b6(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_5
        global state_22
        global state_34
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 324
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

class flip_c3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9

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
        state_3 += 2 * turn * 336
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 354
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_b3_c2(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_1
        global state_10
        global state_39
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 12
        state_37 += 2 * turn * 3
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_39 += 2 * turn * 3

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 39
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27

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
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 999
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_b2_b3(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_19
        global state_37
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 12
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 1089
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

class flip_a2_a4(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_3
        global state_19
        global state_35
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 30
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 336
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_e2_g2(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_14
        global state_23
        global state_43
        state_1 += 2 * turn * 810
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 363
        state_34 += 2 * turn * 3
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_36 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 1080
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 354
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_3 += 2 * turn * 837
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 333
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

class flip_e8(Flip):
    def go(self):
        global state_7
        global state_12
        global state_27
        global state_35
        state_7 += 2 * turn * 81
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 1065
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 336
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 1011
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 117
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

class flip_c4_e6(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_5
        global state_12
        global state_25
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 90
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 363
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 117
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 363
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

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
        state_7 += 2 * turn * 1080
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 1089
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_7 += 2 * turn * 1008
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

class flip_h4_h6(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        global state_5
        global state_28
        global state_40
        state_3 += 2 * turn * 2187
        state_15 += 2 * turn * 270
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 333
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 336
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 1008
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_2 += 2 * turn * 1083
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_4 += 2 * turn * 282
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

class flip_h3_h5(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_4
        global state_27
        global state_41
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 90
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 363
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

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
        state_0 += 2 * turn * 336
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

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
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 1008
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

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
        state_3 += 2 * turn * 117
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_4 += 2 * turn * 279
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

class flip_b4_b6(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_5
        global state_22
        global state_34
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 270
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

class flip_e5_f6(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_5
        global state_13
        global state_26
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 324
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

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
        state_7 += 2 * turn * 333
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

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
        state_3 += 2 * turn * 1
        state_8 += 2 * turn * 1080
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 1080
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_1 += 2 * turn * 1011
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

class flip_c3_e3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_12
        global state_22
        global state_40
        state_2 += 2 * turn * 90
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9

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
        state_1 += 2 * turn * 363
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_5 += 2 * turn * 333
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 93
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_0 += 2 * turn * 282
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

class flip_d4_f2(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_1
        global state_13
        global state_42
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 270
        state_38 += 2 * turn * 27
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

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
        state_2 += 2 * turn * 837
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 279
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

class flip_d5_d7(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_6
        global state_25
        global state_35
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 810
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_0 += 2 * turn * 1053
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

class flip_c4_e4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_12
        global state_23
        global state_39
        state_3 += 2 * turn * 90
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 849
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 1092
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 363
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

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
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 351
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

class flip_e6_f6(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_13
        global state_26
        global state_38
        state_5 += 2 * turn * 324
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 120
        state_35 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_37 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_39 += 2 * turn * 81
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_41 += 2 * turn * 27

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 282
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 999
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 39
        state_35 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_37 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_39 += 2 * turn * 81

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
        state_3 += 2 * turn * 2187
        state_15 += 2 * turn * 999
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

class flip_c2_d2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_11
        global state_20
        global state_40
        state_1 += 2 * turn * 36
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3

class flip_d7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 1089
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

class flip_c6_d6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_11
        global state_24
        global state_36
        state_5 += 2 * turn * 36
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 360
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_3 += 2 * turn * 120
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_0 += 2 * turn * 1092
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

class flip_f8_g8(Flip):
    def go(self):
        global state_7
        global state_13
        global state_28
        global state_36
        global state_14
        global state_29
        global state_37
        state_7 += 2 * turn * 972
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_1 += 2 * turn * 93
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3

class flip_a7(Flip):
    def go(self):
        global state_6
        global state_8
        global state_22
        global state_32
        state_6 += 2 * turn * 1
        state_8 += 2 * turn * 729
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 1065
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 1083
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

class flip_e2_g4(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_3
        global state_14
        global state_25
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 30
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81

class flip_e2_f2(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_13
        global state_22
        global state_42
        state_1 += 2 * turn * 324
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 39
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 1062
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 351
        state_38 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 846
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_e3_f2(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_1
        global state_13
        global state_42
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 324
        state_40 += 2 * turn * 9
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

class flip_d6_e6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_12
        global state_25
        global state_37
        state_5 += 2 * turn * 108
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 1083
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_6 += 2 * turn * 1089
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_c3_d2(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_1
        global state_11
        global state_40
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 36
        state_38 += 2 * turn * 9
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_40 += 2 * turn * 3

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
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 39
        state_36 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_38 += 2 * turn * 243
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_40 += 2 * turn * 81

class flip_c4_c5(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_22
        global state_36
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 108
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 354
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

class flip_f4_g3(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_2
        global state_14
        global state_42
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 324
        state_40 += 2 * turn * 27
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_0 += 2 * turn * 1089
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_7 += 2 * turn * 1065
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_3 += 2 * turn * 2187
        state_15 += 2 * turn * 351
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

class flip_b7_d5(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_4
        global state_11
        global state_37
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 30
        state_33 += 2 * turn * 3
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27

class flip_h7(Flip):
    def go(self):
        global state_6
        global state_15
        global state_29
        global state_39
        state_6 += 2 * turn * 2187
        state_15 += 2 * turn * 729
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 336
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 363
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

class flip_d2_d4(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_3
        global state_22
        global state_38
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 30
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27

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
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 1062
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 1062
        state_35 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

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
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 117
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1

class flip_c7_e7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_12
        global state_26
        global state_36
        state_6 += 2 * turn * 90
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

class flip_c3_e5(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_4
        global state_12
        global state_24
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 90
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 336
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

class flip_b4_c5(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_10
        global state_22
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 12
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9

class flip_b4_d2(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_1
        global state_11
        global state_40
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 30
        state_36 += 2 * turn * 3
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_40 += 2 * turn * 3

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
        state_5 += 2 * turn * 360
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_7 += 2 * turn * 111
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81

class flip_c5_d5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_11
        global state_23
        global state_37
        state_4 += 2 * turn * 36
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

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
        state_5 += 2 * turn * 117
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 111
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3

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
        state_4 += 2 * turn * 1
        state_8 += 2 * turn * 1053
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_4 += 2 * turn * 93
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_6 += 2 * turn * 351
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 120
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

class flip_f3_g2(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_1
        global state_14
        global state_43
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 972
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_e4_f5(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_4
        global state_13
        global state_25
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 108
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27

class flip_g2_g3(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_2
        global state_24
        global state_42
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 12
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 93
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1

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
        state_6 += 2 * turn * 333
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_d3_d4(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_22
        global state_38
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 36
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27

class flip_h2_h3(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_2
        global state_25
        global state_43
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 12
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9

class flip_b8_c8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_10
        global state_25
        global state_33
        state_7 += 2 * turn * 12
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9

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
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 1053
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_d4_e3(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_2
        global state_12
        global state_40
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 108
        state_38 += 2 * turn * 27
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 279
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

class flip_c4_d5(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_4
        global state_11
        global state_23
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 36
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27

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
        state_0 += 2 * turn * 1008
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

class flip_a3(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 9
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1

class flip_d4_f6(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_5
        global state_13
        global state_26
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 270
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 279
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

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
        state_2 += 2 * turn * 849
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 117
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3

class flip_e4_e6(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_5
        global state_25
        global state_37
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 270
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 351
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_e8_f8(Flip):
    def go(self):
        global state_7
        global state_12
        global state_27
        global state_35
        global state_13
        global state_28
        global state_36
        state_7 += 2 * turn * 324
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

class flip_b6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 1065
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 333
        state_35 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_5 += 2 * turn * 846
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_c8_d8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_11
        global state_26
        global state_34
        state_7 += 2 * turn * 36
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 282
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

class flip_b1_c1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_10
        global state_18
        global state_40
        state_0 += 2 * turn * 12
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1

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
        state_0 += 2 * turn * 39
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1

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
        state_7 += 2 * turn * 39
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27

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
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 120
        state_34 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_36 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27

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
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 1089
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_c2_c4(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_21
        global state_37
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 30
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 333
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

class flip_e2_e3(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_22
        global state_40
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 12
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9

class flip_h3(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 9
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9

class flip_e4_f3(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_2
        global state_13
        global state_41
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 324
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

class flip_b7_d7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_11
        global state_25
        global state_35
        state_6 += 2 * turn * 30
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

class flip_e1_f1(Flip):
    def go(self):
        global state_0
        global state_12
        global state_20
        global state_42
        global state_13
        global state_21
        global state_43
        state_0 += 2 * turn * 324
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

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
        state_2 += 2 * turn * 999
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_7 += 2 * turn * 354
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

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
        state_2 += 2 * turn * 1080
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

class flip_e3(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9

class flip_b5_c4(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_3
        global state_10
        global state_37
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 12
        state_35 += 2 * turn * 3
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_37 += 2 * turn * 9

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
        state_2 += 2 * turn * 282
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 1011
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 336
        state_34 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_36 += 2 * turn * 27
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_5 += 2 * turn * 1080
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_6 += 2 * turn * 282
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_f2_g2(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_14
        global state_23
        global state_43
        state_1 += 2 * turn * 972
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

class flip_d4_f4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_13
        global state_24
        global state_40
        state_3 += 2 * turn * 270
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

class flip_g5_g6(Flip):
    def go(self):
        global state_4
        global state_14
        global state_26
        global state_40
        global state_5
        global state_27
        global state_39
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 324
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 336
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 1092
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_3 += 2 * turn * 999
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_4 += 2 * turn * 999
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_2 += 2 * turn * 351
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

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
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 111
        state_34 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27

class flip_b4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3

class flip_c3_c4(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_21
        global state_37
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 36
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 1083
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

class flip_f4_f5(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_4
        global state_25
        global state_39
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 108
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 111
        state_35 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_39 += 2 * turn * 81
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_41 += 2 * turn * 27

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
        state_1 += 2 * turn * 282
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_3 += 2 * turn * 354
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_0 += 2 * turn * 360
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 360
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

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
        state_1 += 2 * turn * 1080
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 849
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

class flip_e5_g3(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_2
        global state_14
        global state_42
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 270
        state_38 += 2 * turn * 81
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

class flip_f3_g4(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_14
        global state_25
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 36
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81

class flip_b1_d1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        global state_11
        global state_19
        global state_41
        state_0 += 2 * turn * 30
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 363
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 1053
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

class flip_f6_g5(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        global state_4
        global state_14
        global state_40
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 36
        state_38 += 2 * turn * 243
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_40 += 2 * turn * 81

class flip_d4_e5(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_4
        global state_12
        global state_24
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 108
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 117
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27

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
        state_4 += 2 * turn * 2187
        state_15 += 2 * turn * 1053
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_6 += 2 * turn * 1011
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_5 += 2 * turn * 1065
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_c7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 351
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

class flip_c6_e6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_12
        global state_25
        global state_37
        state_5 += 2 * turn * 90
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 93
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 93
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81

class flip_a5(Flip):
    def go(self):
        global state_4
        global state_8
        global state_20
        global state_34
        state_4 += 2 * turn * 1
        state_8 += 2 * turn * 81
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1

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
        state_1 += 2 * turn * 1053
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_1 += 2 * turn * 354
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_6 += 2 * turn * 1008
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_e1_g1(Flip):
    def go(self):
        global state_0
        global state_12
        global state_20
        global state_42
        global state_14
        global state_22
        global state_44
        state_0 += 2 * turn * 810
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

class flip_b2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3

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
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 93
        state_35 += 2 * turn * 3
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_37 += 2 * turn * 9
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_41 += 2 * turn * 3

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 1080
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 111
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 1092
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 1011
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_e3_f4(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_13
        global state_24
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 36
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 39
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81

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
        state_0 += 2 * turn * 279
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

class flip_g6(Flip):
    def go(self):
        global state_5
        global state_14
        global state_27
        global state_39
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_f4(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

class flip_d5_e5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_12
        global state_24
        global state_38
        state_4 += 2 * turn * 108
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

class flip_d2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3

class flip_c3_d4(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_3
        global state_11
        global state_22
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 36
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27

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
        state_1 += 2 * turn * 333
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 279
        state_36 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

class flip_g4_g6(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        global state_5
        global state_27
        global state_39
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 270
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 360
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 1062
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

class flip_b2_b4(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_20
        global state_36
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 30
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3

class flip_e3_e5(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_4
        global state_24
        global state_38
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 90
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

class flip_c7_e5(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_4
        global state_12
        global state_38
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 30
        state_34 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81

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
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 1080
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_e5(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_4 += 2 * turn * 1011
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 1011
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

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
        state_4 += 2 * turn * 1053
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

class flip_c6_e4(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_3
        global state_12
        global state_39
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 90
        state_35 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27

class flip_d3_f3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_13
        global state_23
        global state_41
        state_2 += 2 * turn * 270
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

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
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 336
        state_34 += 2 * turn * 3
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_36 += 2 * turn * 9
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

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
        state_2 += 2 * turn * 279
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

class flip_b4_d4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_11
        global state_22
        global state_38
        state_3 += 2 * turn * 30
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27

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
        state_5 += 2 * turn * 282
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 120
        state_34 += 2 * turn * 3
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_36 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9

class flip_e7_f6(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_5
        global state_13
        global state_38
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 12
        state_36 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_38 += 2 * turn * 243

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 363
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 120
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 360
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

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
        state_6 += 2 * turn * 837
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_1 += 2 * turn * 1065
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 360
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 354
        state_34 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 333
        state_36 += 2 * turn * 9
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

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
        state_2 += 2 * turn * 1053
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 117
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_7 += 2 * turn * 120
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81

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
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 117
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81

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
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 360
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 1089
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 1092
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 1083
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_5 += 2 * turn * 1008
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_d3_e4(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_3
        global state_12
        global state_23
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 36
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81

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
        state_0 += 2 * turn * 837
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 1065
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 1083
        state_33 += 2 * turn * 3
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 1065
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

class flip_d6_d7(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_6
        global state_25
        global state_35
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 972
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

class flip_f1_g1(Flip):
    def go(self):
        global state_0
        global state_13
        global state_21
        global state_43
        global state_14
        global state_22
        global state_44
        state_0 += 2 * turn * 972
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

class flip_e8_g8(Flip):
    def go(self):
        global state_7
        global state_12
        global state_27
        global state_35
        global state_14
        global state_29
        global state_37
        state_7 += 2 * turn * 810
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 39
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3

class flip_d7_f5(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_4
        global state_13
        global state_39
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 30
        state_35 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_39 += 2 * turn * 81

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 120
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3

class flip_d4_d6(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_5
        global state_24
        global state_36
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 270
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_4 += 2 * turn * 1008
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_2 += 2 * turn * 363
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

class flip_b6_c7(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_6
        global state_10
        global state_24
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 12
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3

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
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 117
        state_37 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_39 += 2 * turn * 81
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_41 += 2 * turn * 27

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 849
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

class flip_b8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        state_7 += 2 * turn * 3
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3

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
        state_6 += 2 * turn * 117
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

class flip_e4_g2(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_1
        global state_14
        global state_43
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 810
        state_39 += 2 * turn * 27
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_g2(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_3 += 2 * turn * 1
        state_8 += 2 * turn * 351
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

class flip_e5_g7(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_6
        global state_14
        global state_28
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 810
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

class flip_e5_f5(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_13
        global state_25
        global state_39
        state_4 += 2 * turn * 324
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 93
        state_35 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_37 += 2 * turn * 81
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_41 += 2 * turn * 27

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
        state_7 += 2 * turn * 93
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81

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
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 39
        state_34 += 2 * turn * 3
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_36 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27

class flip_f6_f7(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        global state_6
        global state_27
        global state_37
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 972
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_d7_e6(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_5
        global state_12
        global state_37
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 12
        state_35 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_37 += 2 * turn * 81

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 111
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 39
        state_36 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_40 += 2 * turn * 3

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 846
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_5 += 2 * turn * 93
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

class flip_h5(Flip):
    def go(self):
        global state_4
        global state_15
        global state_27
        global state_41
        state_4 += 2 * turn * 2187
        state_15 += 2 * turn * 81
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81

class flip_b6_c5(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_4
        global state_10
        global state_36
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 12
        state_34 += 2 * turn * 3
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_36 += 2 * turn * 9

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 117
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

class flip_d5_d6(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_5
        global state_24
        global state_36
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 324
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

class flip_b3_b5(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_4
        global state_21
        global state_35
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 90
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3

class flip_b7_c7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_10
        global state_24
        global state_34
        state_6 += 2 * turn * 12
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

class flip_e1(Flip):
    def go(self):
        global state_0
        global state_12
        global state_20
        global state_42
        state_0 += 2 * turn * 81
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1

class flip_g6_g7(Flip):
    def go(self):
        global state_5
        global state_14
        global state_27
        global state_39
        global state_6
        global state_28
        global state_38
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 972
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_1 += 2 * turn * 1092
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

class flip_e5_e6(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_5
        global state_25
        global state_37
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 324
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

class flip_h5_h7(Flip):
    def go(self):
        global state_4
        global state_15
        global state_27
        global state_41
        global state_6
        global state_29
        global state_39
        state_4 += 2 * turn * 2187
        state_15 += 2 * turn * 810
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 1092
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_2 += 2 * turn * 1011
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 351
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 351
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 117
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 93
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 117
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 117
        state_36 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9

class flip_f8(Flip):
    def go(self):
        global state_7
        global state_13
        global state_28
        global state_36
        state_7 += 2 * turn * 243
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

class flip_c7_d6(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_5
        global state_11
        global state_36
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 12
        state_34 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_36 += 2 * turn * 27

class flip_c5_c7(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_6
        global state_24
        global state_34
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 810
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_0 += 2 * turn * 120
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1

class flip_e6_f5(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_4
        global state_13
        global state_39
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 36
        state_37 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_39 += 2 * turn * 81

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 1065
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_6 += 2 * turn * 39
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 354
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

class flip_d6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

class flip_c6_d5(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_4
        global state_11
        global state_37
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 36
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27

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
        state_7 += 2 * turn * 363
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

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
        state_6 += 2 * turn * 1053
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_7 += 2 * turn * 117
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81

class flip_a5_a7(Flip):
    def go(self):
        global state_4
        global state_8
        global state_20
        global state_34
        global state_6
        global state_22
        global state_32
        state_4 += 2 * turn * 1
        state_8 += 2 * turn * 810
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

class flip_e5_g5(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_14
        global state_26
        global state_40
        state_4 += 2 * turn * 810
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

class flip_f3_f4(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_3
        global state_24
        global state_40
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 36
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 354
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 120
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27

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
        state_3 += 2 * turn * 279
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 93
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27

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
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 999
        state_37 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

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
        state_4 += 2 * turn * 363
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 117
        state_36 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 93
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 1062
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 279
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_2 += 2 * turn * 1062
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 1053
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 363
        state_34 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_36 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_3 += 2 * turn * 1089
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_6 += 2 * turn * 846
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 1092
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

class flip_b3_d3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_11
        global state_21
        global state_39
        state_2 += 2 * turn * 30
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 111
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81

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
        state_4 += 2 * turn * 846
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 282
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

class flip_f5_f7(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_6
        global state_27
        global state_37
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 810
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_e4_g4(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_14
        global state_25
        global state_41
        state_3 += 2 * turn * 810
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

class flip_g4(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

class flip_a6_a7(Flip):
    def go(self):
        global state_5
        global state_8
        global state_21
        global state_33
        global state_6
        global state_22
        global state_32
        state_5 += 2 * turn * 1
        state_8 += 2 * turn * 972
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

class flip_f2(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_6 += 2 * turn * 1062
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 120
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 1011
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_5 += 2 * turn * 837
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 1062
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

class flip_d4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27

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
        state_0 += 2 * turn * 354
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

class flip_h2_h4(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        global state_3
        global state_26
        global state_42
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 30
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27

class flip_c2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 117
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27

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
        state_3 += 2 * turn * 363
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

class flip_d2_e2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_12
        global state_21
        global state_41
        state_1 += 2 * turn * 108
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 354
        state_33 += 2 * turn * 3
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 1011
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 93
        state_34 += 2 * turn * 3
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_36 += 2 * turn * 9
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9

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
        state_4 += 2 * turn * 849
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_2 += 2 * turn * 111
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 282
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

class flip_e7(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 351
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

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
        state_1 += 2 * turn * 1083
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 846
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 1083
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_f2_f4(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_3
        global state_24
        global state_40
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 30
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_4 += 2 * turn * 1092
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 354
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 336
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

class flip_h3_h4(Flip):
    def go(self):
        global state_2
        global state_15
        global state_25
        global state_43
        global state_3
        global state_26
        global state_42
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 36
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27

class flip_c6_d7(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_6
        global state_11
        global state_25
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 36
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 111
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 837
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_5 += 2 * turn * 1062
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_d3_e2(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_1
        global state_12
        global state_41
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 108
        state_39 += 2 * turn * 9
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_41 += 2 * turn * 3

class flip_c1_d1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_11
        global state_19
        global state_41
        state_0 += 2 * turn * 36
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1

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
        state_6 += 2 * turn * 354
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 849
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

class flip_d1_e1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        global state_12
        global state_20
        global state_42
        state_0 += 2 * turn * 108
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 849
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_b5_c6(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_5
        global state_10
        global state_23
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 12
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9

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
        state_3 += 2 * turn * 1011
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

class flip_a4_a6(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        global state_5
        global state_21
        global state_33
        state_3 += 2 * turn * 1
        state_8 += 2 * turn * 270
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

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
        state_2 += 2 * turn * 336
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 111
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9

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
        state_6 += 2 * turn * 336
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 1008
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_4 += 2 * turn * 120
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 837
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_4 += 2 * turn * 117
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 120
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 120
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27

class flip_d7_f7(Flip):
    def go(self):
        global state_6
        global state_11
        global state_25
        global state_35
        global state_13
        global state_27
        global state_37
        state_6 += 2 * turn * 270
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 1053
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 93
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3

class flip_f4_g4(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_14
        global state_25
        global state_41
        state_3 += 2 * turn * 972
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_1 += 2 * turn * 1062
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_3 += 2 * turn * 2187
        state_15 += 2 * turn * 837
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 363
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_3 += 2 * turn * 1053
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_0 += 2 * turn * 111
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1

class flip_f6_g7(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        global state_6
        global state_14
        global state_28
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 972
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 1011
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 111
        state_33 += 2 * turn * 3
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27

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
        state_2 += 2 * turn * 39
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9

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
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 282
        state_34 += 2 * turn * 3
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_36 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

class flip_d6_f4(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_3
        global state_13
        global state_40
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 90
        state_36 += 2 * turn * 27
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27

class flip_f7_g7(Flip):
    def go(self):
        global state_6
        global state_13
        global state_27
        global state_37
        global state_14
        global state_28
        global state_38
        state_6 += 2 * turn * 972
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 354
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 333
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

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
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 837
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_d8_e8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        global state_12
        global state_27
        global state_35
        state_7 += 2 * turn * 108
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81

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
        state_0 += 2 * turn * 1083
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

class flip_b6_d4(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_3
        global state_11
        global state_38
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 30
        state_34 += 2 * turn * 3
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27

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
        state_1 += 2 * turn * 336
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 354
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

class flip_f5_g4(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_3
        global state_14
        global state_41
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 108
        state_39 += 2 * turn * 81
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_41 += 2 * turn * 27

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
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 1089
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 360
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_g8(Flip):
    def go(self):
        global state_7
        global state_14
        global state_29
        global state_37
        state_7 += 2 * turn * 729
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 1062
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

class flip_f3_g3(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_14
        global state_24
        global state_42
        state_2 += 2 * turn * 972
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

class flip_f6(Flip):
    def go(self):
        global state_5
        global state_13
        global state_26
        global state_38
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_2 += 2 * turn * 120
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9

class flip_d2_d3(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_21
        global state_39
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 12
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9

class flip_g2_g4(Flip):
    def go(self):
        global state_1
        global state_14
        global state_23
        global state_43
        global state_3
        global state_25
        global state_41
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 30
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

class flip_d6_e5(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_4
        global state_12
        global state_38
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 36
        state_36 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81

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
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 837
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_e6_f7(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_6
        global state_13
        global state_27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 324
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

class flip_d4_e4(Flip):
    def go(self):
        global state_3
        global state_11
        global state_22
        global state_38
        global state_12
        global state_23
        global state_39
        state_3 += 2 * turn * 108
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_4 += 2 * turn * 39
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

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
        state_7 += 2 * turn * 849
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 846
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 846
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_d8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        state_7 += 2 * turn * 27
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27

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
        state_1 += 2 * turn * 117
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3

class flip_a4(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        state_3 += 2 * turn * 1
        state_8 += 2 * turn * 27
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1

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
        state_4 += 2 * turn * 1080
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

class flip_d5_f3(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_2
        global state_13
        global state_41
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 270
        state_37 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 360
        state_36 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 849
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 282
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

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
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 1053
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 849
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

class flip_c2_e2(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_12
        global state_21
        global state_41
        state_1 += 2 * turn * 90
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3

class flip_e2_f3(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_2
        global state_13
        global state_23
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 12
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243

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
        state_5 += 2 * turn * 999
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_6 += 2 * turn * 363
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_d3_f5(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_4
        global state_13
        global state_25
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 90
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27

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
        state_6 += 2 * turn * 111
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

class flip_b4_d6(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_5
        global state_11
        global state_24
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 30
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9

class flip_e3_g5(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_4
        global state_14
        global state_26
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 90
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27

class flip_e3_f3(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_13
        global state_23
        global state_41
        state_2 += 2 * turn * 324
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

class flip_b4_c4(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_10
        global state_21
        global state_37
        state_3 += 2 * turn * 12
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 111
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_2 += 2 * turn * 333
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

class flip_c5_d4(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_3
        global state_11
        global state_38
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 36
        state_36 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27

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
        state_6 += 2 * turn * 360
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 1011
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

class flip_b5_b7(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_6
        global state_23
        global state_33
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 810
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

class flip_b3_d5(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_4
        global state_11
        global state_23
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 30
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 1092
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

class flip_b3_c3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_10
        global state_20
        global state_38
        state_2 += 2 * turn * 12
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9

class flip_d5_e4(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_3
        global state_12
        global state_39
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 108
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27

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
        state_7 += 2 * turn * 1089
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 849
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_0 += 2 * turn * 333
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

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
        state_4 += 2 * turn * 1083
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

class flip_g3_g5(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_4
        global state_26
        global state_40
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 90
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

class flip_e2_e4(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        global state_3
        global state_23
        global state_39
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 30
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 117
        state_37 += 2 * turn * 9
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_39 += 2 * turn * 9
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_41 += 2 * turn * 3

class flip_e4_g6(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_5
        global state_14
        global state_27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 270
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

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
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 117
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3

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
        state_5 += 2 * turn * 1089
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_2 += 2 * turn * 1092
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

class flip_e4_f4(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_13
        global state_24
        global state_40
        state_3 += 2 * turn * 324
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_3 += 2 * turn * 846
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_0 += 2 * turn * 351
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

class flip_e3_e4(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_3
        global state_23
        global state_39
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 36
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

class flip_c5_e7(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_6
        global state_12
        global state_26
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 90
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3

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
        state_0 += 2 * turn * 117
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 846
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

class flip_c4_d4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_11
        global state_22
        global state_38
        state_3 += 2 * turn * 36
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27

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
        state_5 += 2 * turn * 336
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_0 += 2 * turn * 1062
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_3 += 2 * turn * 849
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

class flip_f2_g3(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_14
        global state_24
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 12
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243

class flip_e7_g7(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_14
        global state_28
        global state_38
        state_6 += 2 * turn * 810
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 360
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_0 += 2 * turn * 849
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 1080
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

class flip_e4_e5(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        global state_4
        global state_24
        global state_38
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 108
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 111
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 120
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

class flip_f4_f6(Flip):
    def go(self):
        global state_3
        global state_13
        global state_24
        global state_40
        global state_5
        global state_26
        global state_38
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 270
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_1 += 2 * turn * 39
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3

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
        state_4 += 2 * turn * 336
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_7 += 2 * turn * 1011
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_5 += 2 * turn * 354
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_4 += 2 * turn * 333
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 336
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 111
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

class flip_c6_c7(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        global state_6
        global state_24
        global state_34
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 972
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

class flip_a2_a3(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        global state_2
        global state_18
        global state_36
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 12
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1

class flip_h2(Flip):
    def go(self):
        global state_1
        global state_15
        global state_24
        global state_44
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 3
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3

class flip_b3(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3

class flip_c1_e1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        global state_12
        global state_20
        global state_42
        state_0 += 2 * turn * 90
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 354
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

class flip_f5_f6(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_5
        global state_26
        global state_38
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 324
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_4 += 2 * turn * 354
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_6 += 2 * turn * 1080
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_h4_h5(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        global state_4
        global state_27
        global state_41
        state_3 += 2 * turn * 2187
        state_15 += 2 * turn * 108
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81

class flip_a3_a5(Flip):
    def go(self):
        global state_2
        global state_8
        global state_18
        global state_36
        global state_4
        global state_20
        global state_34
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 90
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1

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
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 282
        state_34 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_36 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_4 += 2 * turn * 351
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 282
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_b2_d2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_11
        global state_20
        global state_40
        state_1 += 2 * turn * 30
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3

class flip_f3_f5(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        global state_4
        global state_25
        global state_39
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 90
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 1080
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_e6_g4(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_3
        global state_14
        global state_41
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 90
        state_37 += 2 * turn * 81
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 27
        state_41 += 2 * turn * 27

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 39
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9

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
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 333
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

class flip_e7_g5(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_4
        global state_14
        global state_40
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 30
        state_36 += 2 * turn * 81
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_40 += 2 * turn * 81

class flip_c2_d3(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_11
        global state_21
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 12
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27

class flip_c6(Flip):
    def go(self):
        global state_5
        global state_10
        global state_23
        global state_35
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 1083
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 1065
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_b4_b5(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_4
        global state_21
        global state_35
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 108
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3

class flip_c8_e8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        global state_12
        global state_27
        global state_35
        state_7 += 2 * turn * 90
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 999
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_0 += 2 * turn * 93
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 363
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

class flip_c5_e3(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_2
        global state_12
        global state_40
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 90
        state_36 += 2 * turn * 9
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 849
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_6 += 2 * turn * 1
        state_22 += 2 * turn * 1
        state_32 += 2 * turn * 1

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 93
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27

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
        state_3 += 2 * turn * 2187
        state_15 += 2 * turn * 1080
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

class flip_b5_d3(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_2
        global state_11
        global state_39
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 30
        state_35 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_39 += 2 * turn * 9

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
        state_6 += 2 * turn * 120
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 39
        state_35 += 2 * turn * 3
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_37 += 2 * turn * 9
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_39 += 2 * turn * 9

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
        state_7 += 2 * turn * 282
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 93
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27

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
        state_4 += 2 * turn * 111
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 39
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 39
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 39
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 1008
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_5 += 2 * turn * 1083
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 333
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 1008
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_c3_d3(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_11
        global state_21
        global state_39
        state_2 += 2 * turn * 36
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9

class flip_b1(Flip):
    def go(self):
        global state_0
        global state_9
        global state_17
        global state_39
        state_0 += 2 * turn * 3
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1

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
        state_3 += 2 * turn * 1080
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_4 += 2 * turn * 360
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

class flip_f5_g6(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        global state_5
        global state_14
        global state_27
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 324
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

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
        state_7 += 2 * turn * 351
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

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
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 279
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 279
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

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
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 846
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_3 += 2 * turn * 333
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_4 += 2 * turn * 837
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 120
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3
        state_2 += 2 * turn * 729
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 351
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

class flip_d6_e7(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_6
        global state_12
        global state_26
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 108
        state_6 += 2 * turn * 81
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3

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
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 333
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 1053
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_5 += 2 * turn * 351
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 279
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

class flip_c4(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 849
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 333
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

class flip_a2(Flip):
    def go(self):
        global state_1
        global state_8
        global state_17
        global state_37
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 3
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 1089
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_6 += 2 * turn * 849
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_c2_e4(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_3
        global state_12
        global state_23
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 30
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 333
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 333
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_e3_g3(Flip):
    def go(self):
        global state_2
        global state_12
        global state_22
        global state_40
        global state_14
        global state_24
        global state_42
        state_2 += 2 * turn * 810
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 1092
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 1080
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 1065
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9
        state_1 += 2 * turn * 729
        state_14 += 2 * turn * 3
        state_43 += 2 * turn * 3

class flip_g3(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

class flip_f1(Flip):
    def go(self):
        global state_0
        global state_13
        global state_21
        global state_43
        state_0 += 2 * turn * 243
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

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
        state_7 += 2 * turn * 360
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

class flip_d3_d5(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        global state_4
        global state_23
        global state_37
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 90
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 333
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

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
        state_6 += 2 * turn * 1065
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_3 += 2 * turn * 1008
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_0 += 2 * turn * 1011
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 111
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 1008
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 333
        state_36 += 2 * turn * 27
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 39
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81

class flip_h6(Flip):
    def go(self):
        global state_5
        global state_15
        global state_28
        global state_40
        state_5 += 2 * turn * 2187
        state_15 += 2 * turn * 243
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

class flip_b6_c6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_10
        global state_23
        global state_35
        state_5 += 2 * turn * 12
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_c5_e5(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_12
        global state_24
        global state_38
        state_4 += 2 * turn * 90
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 837
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_b7(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 39
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9

class flip_e2(Flip):
    def go(self):
        global state_1
        global state_12
        global state_21
        global state_41
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3

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
        state_3 += 2 * turn * 1083
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 1011
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_3 += 2 * turn * 360
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 354
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_2 += 2 * turn * 2187
        state_15 += 2 * turn * 1089
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_7 += 2 * turn * 279
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

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
        state_6 += 2 * turn * 93
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_1 += 2 * turn * 846
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 837
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 279
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_f2_f3(Flip):
    def go(self):
        global state_1
        global state_13
        global state_22
        global state_42
        global state_2
        global state_23
        global state_41
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 12
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

class flip_c7_d7(Flip):
    def go(self):
        global state_6
        global state_10
        global state_24
        global state_34
        global state_11
        global state_25
        global state_35
        state_6 += 2 * turn * 36
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

class flip_e7_f7(Flip):
    def go(self):
        global state_6
        global state_12
        global state_26
        global state_36
        global state_13
        global state_27
        global state_37
        state_6 += 2 * turn * 324
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_3 += 2 * turn * 282
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 120
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9

class flip_b2_c3(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_2
        global state_10
        global state_20
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 12
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9

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
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 846
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_6 += 2 * turn * 1092
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_12 += 2 * turn * 729
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 351
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

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
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 1089
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 351
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 120
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27

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
        state_1 += 2 * turn * 1
        state_8 += 2 * turn * 39
        state_17 += 2 * turn * 1
        state_37 += 2 * turn * 1
        state_2 += 2 * turn * 1
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1

class flip_g1(Flip):
    def go(self):
        global state_0
        global state_14
        global state_22
        global state_44
        state_0 += 2 * turn * 729
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 354
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9

class flip_b7_c6(Flip):
    def go(self):
        global state_6
        global state_9
        global state_23
        global state_33
        global state_5
        global state_10
        global state_35
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 12
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 111
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27

class flip_e5_f4(Flip):
    def go(self):
        global state_4
        global state_12
        global state_24
        global state_38
        global state_3
        global state_13
        global state_40
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 108
        state_38 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27

class flip_b5_c5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_10
        global state_22
        global state_36
        state_4 += 2 * turn * 12
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9

class flip_d6_f6(Flip):
    def go(self):
        global state_5
        global state_11
        global state_24
        global state_36
        global state_13
        global state_26
        global state_38
        state_5 += 2 * turn * 270
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_0 += 2 * turn * 1080
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_0 += 2 * turn * 999
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1
        state_14 += 2 * turn * 1
        state_22 += 2 * turn * 729
        state_44 += 2 * turn * 1

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
        state_3 += 2 * turn * 111
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_5 += 2 * turn * 1092
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_g5_g7(Flip):
    def go(self):
        global state_4
        global state_14
        global state_26
        global state_40
        global state_6
        global state_28
        global state_38
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 810
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 117
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 360
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

class flip_c5_c6(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_5
        global state_23
        global state_35
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 324
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_b6_d6(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_11
        global state_24
        global state_36
        state_5 += 2 * turn * 30
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_2 += 2 * turn * 1065
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

class flip_h4(Flip):
    def go(self):
        global state_3
        global state_15
        global state_26
        global state_42
        state_3 += 2 * turn * 2187
        state_15 += 2 * turn * 27
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 111
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 93
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9

class flip_b5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3

class flip_b3_b4(Flip):
    def go(self):
        global state_2
        global state_9
        global state_19
        global state_37
        global state_3
        global state_20
        global state_36
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 36
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3

class flip_c3_c5(Flip):
    def go(self):
        global state_2
        global state_10
        global state_20
        global state_38
        global state_4
        global state_22
        global state_36
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 90
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9

class flip_a5_a6(Flip):
    def go(self):
        global state_4
        global state_8
        global state_20
        global state_34
        global state_5
        global state_21
        global state_33
        state_4 += 2 * turn * 1
        state_8 += 2 * turn * 324
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

class flip_g3_g4(Flip):
    def go(self):
        global state_2
        global state_14
        global state_24
        global state_42
        global state_3
        global state_25
        global state_41
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 36
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_3 += 2 * turn * 729
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

class flip_d2_f2(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_13
        global state_22
        global state_42
        state_1 += 2 * turn * 270
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 999
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_6 += 2 * turn * 243
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 282
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

class flip_e6_g6(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        global state_14
        global state_27
        global state_39
        state_5 += 2 * turn * 810
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 336
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_4 += 2 * turn * 243
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 39
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 999
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 39
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

class flip_b2_d4(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_3
        global state_11
        global state_22
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 30
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27

class flip_b2_c2(Flip):
    def go(self):
        global state_1
        global state_9
        global state_18
        global state_38
        global state_10
        global state_19
        global state_39
        state_1 += 2 * turn * 12
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3

class flip_c4_c6(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_5
        global state_23
        global state_35
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 270
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_c8(Flip):
    def go(self):
        global state_7
        global state_10
        global state_25
        global state_33
        state_7 += 2 * turn * 9
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9

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
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 837
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

class flip_c2_c3(Flip):
    def go(self):
        global state_1
        global state_10
        global state_19
        global state_39
        global state_2
        global state_20
        global state_38
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 12
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9

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
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 360
        state_36 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_5 += 2 * turn * 279
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_5 += 2 * turn * 1053
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

class flip_a6(Flip):
    def go(self):
        global state_5
        global state_8
        global state_21
        global state_33
        state_5 += 2 * turn * 1
        state_8 += 2 * turn * 243
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

class flip_d5_f5(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_13
        global state_25
        global state_39
        state_4 += 2 * turn * 270
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 282
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 351
        state_38 += 2 * turn * 27
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

class flip_b5_d5(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_11
        global state_23
        global state_37
        state_4 += 2 * turn * 30
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27

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
        state_4 += 2 * turn * 1065
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_1 += 2 * turn * 1008
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_1 += 2 * turn * 360
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_3 += 2 * turn * 39
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27

class flip_g7(Flip):
    def go(self):
        global state_6
        global state_14
        global state_28
        global state_38
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

class flip_b6_b7(Flip):
    def go(self):
        global state_5
        global state_9
        global state_22
        global state_34
        global state_6
        global state_23
        global state_33
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 972
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_6 += 2 * turn * 3
        state_23 += 2 * turn * 3
        state_33 += 2 * turn * 3

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 336
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

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
        state_2 += 2 * turn * 354
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

class flip_f5(Flip):
    def go(self):
        global state_4
        global state_13
        global state_25
        global state_39
        state_4 += 2 * turn * 243
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81

class flip_d1_f1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        global state_13
        global state_21
        global state_43
        state_0 += 2 * turn * 270
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

class flip_c5_d6(Flip):
    def go(self):
        global state_4
        global state_10
        global state_22
        global state_36
        global state_5
        global state_11
        global state_24
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 36
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9

class flip_d5_e6(Flip):
    def go(self):
        global state_4
        global state_11
        global state_23
        global state_37
        global state_5
        global state_12
        global state_25
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 108
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9

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
        state_2 += 2 * turn * 846
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_14 += 2 * turn * 9
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9

class flip_d3(Flip):
    def go(self):
        global state_2
        global state_11
        global state_21
        global state_39
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9

class flip_c1(Flip):
    def go(self):
        global state_0
        global state_10
        global state_18
        global state_40
        state_0 += 2 * turn * 9
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1

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
        state_7 += 2 * turn * 837
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 282
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_2 += 2 * turn * 243
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9
        state_3 += 2 * turn * 243
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_5 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 279
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_1 += 2 * turn * 837
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

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
        state_4 += 2 * turn * 9
        state_10 += 2 * turn * 1053
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 846
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 120
        state_35 += 2 * turn * 3
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_37 += 2 * turn * 9
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_39 += 2 * turn * 9
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_41 += 2 * turn * 3

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 363
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_7 += 2 * turn * 1053
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 1083
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_3 += 2 * turn * 9
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_6 += 2 * turn * 9
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9

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
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 279
        state_36 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 9
        state_42 += 2 * turn * 9

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 363
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_4 += 2 * turn * 2187
        state_27 += 2 * turn * 27
        state_41 += 2 * turn * 81
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243

class flip_e6(Flip):
    def go(self):
        global state_5
        global state_12
        global state_25
        global state_37
        state_5 += 2 * turn * 81
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_2 += 2 * turn * 729
        state_14 += 2 * turn * 1062
        state_24 += 2 * turn * 243
        state_42 += 2 * turn * 9
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243
        state_6 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 282
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_41 += 2 * turn * 9

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
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 999
        state_5 += 2 * turn * 243
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_6 += 2 * turn * 729
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3

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
        state_2 += 2 * turn * 1
        state_8 += 2 * turn * 360
        state_18 += 2 * turn * 1
        state_36 += 2 * turn * 1
        state_3 += 2 * turn * 1
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1
        state_5 += 2 * turn * 1
        state_21 += 2 * turn * 1
        state_33 += 2 * turn * 1

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
        state_3 += 2 * turn * 351
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27

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
        state_5 += 2 * turn * 363
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_13 += 2 * turn * 243
        state_26 += 2 * turn * 9
        state_38 += 2 * turn * 243

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 279
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_5 += 2 * turn * 729
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9

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
        state_3 += 2 * turn * 1092
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_11 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

class flip_b4_c3(Flip):
    def go(self):
        global state_3
        global state_9
        global state_20
        global state_36
        global state_2
        global state_10
        global state_38
        state_3 += 2 * turn * 3
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 12
        state_36 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_10 += 2 * turn * 9
        state_38 += 2 * turn * 9

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
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 117
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27

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
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 39
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3

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
        state_1 += 2 * turn * 120
        state_9 += 2 * turn * 3
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3

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
        state_4 += 2 * turn * 1062
        state_10 += 2 * turn * 81
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_12 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_13 += 2 * turn * 81
        state_25 += 2 * turn * 27
        state_39 += 2 * turn * 81
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 279
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_3 += 2 * turn * 3
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_5 += 2 * turn * 3
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3

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
        state_0 += 2 * turn * 363
        state_9 += 2 * turn * 1
        state_17 += 2 * turn * 3
        state_39 += 2 * turn * 1
        state_10 += 2 * turn * 1
        state_18 += 2 * turn * 9
        state_40 += 2 * turn * 1
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1
        state_12 += 2 * turn * 1
        state_20 += 2 * turn * 81
        state_42 += 2 * turn * 1
        state_13 += 2 * turn * 1
        state_21 += 2 * turn * 243
        state_43 += 2 * turn * 1

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
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 111
        state_35 += 2 * turn * 3
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 9
        state_39 += 2 * turn * 9
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_41 += 2 * turn * 3

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
        state_1 += 2 * turn * 2187
        state_15 += 2 * turn * 1011
        state_24 += 2 * turn * 729
        state_44 += 2 * turn * 3
        state_2 += 2 * turn * 2187
        state_25 += 2 * turn * 243
        state_43 += 2 * turn * 9
        state_3 += 2 * turn * 2187
        state_26 += 2 * turn * 81
        state_42 += 2 * turn * 27
        state_5 += 2 * turn * 2187
        state_28 += 2 * turn * 9
        state_40 += 2 * turn * 243
        state_6 += 2 * turn * 2187
        state_29 += 2 * turn * 3
        state_39 += 2 * turn * 729

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
        state_3 += 2 * turn * 1065
        state_9 += 2 * turn * 27
        state_20 += 2 * turn * 3
        state_36 += 2 * turn * 3
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_13 += 2 * turn * 27
        state_24 += 2 * turn * 81
        state_40 += 2 * turn * 27
        state_14 += 2 * turn * 27
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27

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
        state_7 += 2 * turn * 846
        state_10 += 2 * turn * 2187
        state_25 += 2 * turn * 1
        state_33 += 2 * turn * 9
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_12 += 2 * turn * 2187
        state_27 += 2 * turn * 1
        state_35 += 2 * turn * 81
        state_14 += 2 * turn * 2187
        state_29 += 2 * turn * 1
        state_37 += 2 * turn * 729

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
        state_2 += 2 * turn * 93
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_10 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9

class flip_d8_f8(Flip):
    def go(self):
        global state_7
        global state_11
        global state_26
        global state_34
        global state_13
        global state_28
        global state_36
        state_7 += 2 * turn * 270
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27
        state_13 += 2 * turn * 2187
        state_28 += 2 * turn * 1
        state_36 += 2 * turn * 243

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 120
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 846
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 120
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_37 += 2 * turn * 27
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27

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
        state_5 += 2 * turn * 39
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_1 += 2 * turn * 1089
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_12 += 2 * turn * 3
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3
        state_14 += 2 * turn * 3
        state_23 += 2 * turn * 729
        state_43 += 2 * turn * 3

class flip_g5(Flip):
    def go(self):
        global state_4
        global state_14
        global state_26
        global state_40
        state_4 += 2 * turn * 729
        state_14 += 2 * turn * 81
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_6 += 2 * turn * 279
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 3
        state_34 += 2 * turn * 9
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243

class flip_f3(Flip):
    def go(self):
        global state_2
        global state_13
        global state_23
        global state_41
        state_2 += 2 * turn * 243
        state_13 += 2 * turn * 9
        state_23 += 2 * turn * 243
        state_41 += 2 * turn * 9

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
        state_5 += 2 * turn * 111
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 363
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81

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
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 1065
        state_21 += 2 * turn * 81
        state_41 += 2 * turn * 3
        state_2 += 2 * turn * 81
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 111
        state_34 += 2 * turn * 3
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9

class flip_d1(Flip):
    def go(self):
        global state_0
        global state_11
        global state_19
        global state_41
        state_0 += 2 * turn * 27
        state_11 += 2 * turn * 1
        state_19 += 2 * turn * 27
        state_41 += 2 * turn * 1

class flip_b8_d8(Flip):
    def go(self):
        global state_7
        global state_9
        global state_24
        global state_32
        global state_11
        global state_26
        global state_34
        state_7 += 2 * turn * 30
        state_9 += 2 * turn * 2187
        state_24 += 2 * turn * 1
        state_32 += 2 * turn * 3
        state_11 += 2 * turn * 2187
        state_26 += 2 * turn * 1
        state_34 += 2 * turn * 27

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
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 93
        state_34 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_36 += 2 * turn * 27
        state_3 += 2 * turn * 243
        state_13 += 2 * turn * 27
        state_40 += 2 * turn * 27

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
        state_5 += 2 * turn * 3
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 354
        state_34 += 2 * turn * 3
        state_3 += 2 * turn * 27
        state_11 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_40 += 2 * turn * 9
        state_1 += 2 * turn * 243
        state_13 += 2 * turn * 3
        state_42 += 2 * turn * 3

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 360
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27

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
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 351
        state_21 += 2 * turn * 9
        state_37 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9
        state_5 += 2 * turn * 9
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9

class flip_g4_g5(Flip):
    def go(self):
        global state_3
        global state_14
        global state_25
        global state_41
        global state_4
        global state_26
        global state_40
        state_3 += 2 * turn * 729
        state_14 += 2 * turn * 108
        state_25 += 2 * turn * 81
        state_41 += 2 * turn * 27
        state_4 += 2 * turn * 729
        state_26 += 2 * turn * 27
        state_40 += 2 * turn * 81

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
        state_1 += 2 * turn * 3
        state_9 += 2 * turn * 93
        state_18 += 2 * turn * 3
        state_38 += 2 * turn * 3
        state_2 += 2 * turn * 3
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 3
        state_4 += 2 * turn * 3
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 3

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
        state_6 += 2 * turn * 999
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3
        state_37 += 2 * turn * 243
        state_14 += 2 * turn * 729
        state_28 += 2 * turn * 3
        state_38 += 2 * turn * 729

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
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 1083
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_4 += 2 * turn * 27
        state_23 += 2 * turn * 27
        state_37 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

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
        state_2 += 2 * turn * 3
        state_9 += 2 * turn * 9
        state_19 += 2 * turn * 3
        state_37 += 2 * turn * 282
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 9
        state_4 += 2 * turn * 27
        state_11 += 2 * turn * 81
        state_23 += 2 * turn * 27
        state_6 += 2 * turn * 243
        state_13 += 2 * turn * 729
        state_27 += 2 * turn * 3

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
        state_1 += 2 * turn * 9
        state_10 += 2 * turn * 93
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_2 += 2 * turn * 9
        state_20 += 2 * turn * 9
        state_38 += 2 * turn * 9
        state_4 += 2 * turn * 9
        state_22 += 2 * turn * 9
        state_36 += 2 * turn * 9

class flip_d2_e3(Flip):
    def go(self):
        global state_1
        global state_11
        global state_20
        global state_40
        global state_2
        global state_12
        global state_22
        state_1 += 2 * turn * 27
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 12
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 9
        state_22 += 2 * turn * 81

class flip_b5_d7(Flip):
    def go(self):
        global state_4
        global state_9
        global state_21
        global state_35
        global state_6
        global state_11
        global state_25
        state_4 += 2 * turn * 3
        state_9 += 2 * turn * 81
        state_21 += 2 * turn * 3
        state_35 += 2 * turn * 30
        state_6 += 2 * turn * 27
        state_11 += 2 * turn * 729
        state_25 += 2 * turn * 3

class flip_c4_e2(Flip):
    def go(self):
        global state_3
        global state_10
        global state_21
        global state_37
        global state_1
        global state_12
        global state_41
        state_3 += 2 * turn * 9
        state_10 += 2 * turn * 27
        state_21 += 2 * turn * 90
        state_37 += 2 * turn * 9
        state_1 += 2 * turn * 81
        state_12 += 2 * turn * 3
        state_41 += 2 * turn * 3

class flip_e4(Flip):
    def go(self):
        global state_3
        global state_12
        global state_23
        global state_39
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27

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
        state_1 += 2 * turn * 279
        state_10 += 2 * turn * 3
        state_19 += 2 * turn * 9
        state_39 += 2 * turn * 3
        state_11 += 2 * turn * 3
        state_20 += 2 * turn * 27
        state_40 += 2 * turn * 3
        state_13 += 2 * turn * 3
        state_22 += 2 * turn * 243
        state_42 += 2 * turn * 3

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
        state_2 += 2 * turn * 27
        state_11 += 2 * turn * 1008
        state_21 += 2 * turn * 27
        state_39 += 2 * turn * 9
        state_3 += 2 * turn * 27
        state_22 += 2 * turn * 27
        state_38 += 2 * turn * 27
        state_5 += 2 * turn * 27
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_6 += 2 * turn * 27
        state_25 += 2 * turn * 3
        state_35 += 2 * turn * 27

class flip_a4_a5(Flip):
    def go(self):
        global state_3
        global state_8
        global state_19
        global state_35
        global state_4
        global state_20
        global state_34
        state_3 += 2 * turn * 1
        state_8 += 2 * turn * 108
        state_19 += 2 * turn * 1
        state_35 += 2 * turn * 1
        state_4 += 2 * turn * 1
        state_20 += 2 * turn * 1
        state_34 += 2 * turn * 1

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 1008
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_2 += 2 * turn * 81
        state_12 += 2 * turn * 1089
        state_22 += 2 * turn * 81
        state_40 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_23 += 2 * turn * 81
        state_39 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_24 += 2 * turn * 27
        state_38 += 2 * turn * 81
        state_5 += 2 * turn * 81
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_6 += 2 * turn * 81
        state_26 += 2 * turn * 3
        state_36 += 2 * turn * 81

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
        state_6 += 2 * turn * 9
        state_10 += 2 * turn * 729
        state_24 += 2 * turn * 39
        state_34 += 2 * turn * 9
        state_5 += 2 * turn * 27
        state_11 += 2 * turn * 243
        state_36 += 2 * turn * 27
        state_4 += 2 * turn * 81
        state_12 += 2 * turn * 81
        state_38 += 2 * turn * 81

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
        state_5 += 2 * turn * 849
        state_9 += 2 * turn * 243
        state_22 += 2 * turn * 3
        state_34 += 2 * turn * 3
        state_10 += 2 * turn * 243
        state_23 += 2 * turn * 9
        state_35 += 2 * turn * 9
        state_11 += 2 * turn * 243
        state_24 += 2 * turn * 9
        state_36 += 2 * turn * 27
        state_12 += 2 * turn * 243
        state_25 += 2 * turn * 9
        state_37 += 2 * turn * 81
        state_14 += 2 * turn * 243
        state_27 += 2 * turn * 9
        state_39 += 2 * turn * 243

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
        state_6 += 2 * turn * 3
        state_9 += 2 * turn * 729
        state_23 += 2 * turn * 93
        state_33 += 2 * turn * 3
        state_5 += 2 * turn * 9
        state_10 += 2 * turn * 243
        state_35 += 2 * turn * 9
        state_3 += 2 * turn * 81
        state_12 += 2 * turn * 27
        state_39 += 2 * turn * 27

#gen_funcs()
#stop

line_flip_func = {}
for l in range(46):
    for nr, flips in nr_flips.items():
        posn = sorted([calc_pos(l, idx) for idx in flips if idx < lines[l].length-1])
        human_moves = '_'.join(['abcdefgh'[i] + str(j+1) for (i, j) in posn])
        line_flip_func[l << 6 | nr] = eval(f'flip_{human_moves}()')

# setup initial board state
turn = BLACK
put_d5().go()
put_e4().go()
turn = WHITE
put_d4().go()
put_e5().go()
check_board()
turn = BLACK

# play full italian line
italian = 'F5D6C4D3E6F4E3F3C6F6G5G6E7F7C3G4D2C5H3H4E2F2G3C1C2E1D1B3F1G1F8D7C7G7A3B4B6B1H8B5A6A5A4B7A8G8H7H6H5G2H1H2A1D8E8C8B2A2B8A7'
human_moves = [italian[i*2:(i+1)*2] for i in range(len(italian)//2)]
moves = ['ABCDEFGH'.index(h[0]) + 8 * (int(h[1])-1) for h in human_moves]

for mv in moves:
    move_table[mv].go()
    check_board()
    turn = -turn

nx = sum(str_state(states()[l]).count('2') for l in range(8))
no = sum(str_state(states()[l]).count('0') for l in range(8))
print(f'{nx}-{no}')
print()
