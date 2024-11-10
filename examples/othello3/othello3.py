'''
advanced othello move generator

copyright mark dufour 2024, license GPLv3.

based on a concept by jan de graaf (
    jan.de.graaf@othello.nl,
    https://www.linkedin.com/in/jan-c-de-graaf-blijleven-9076473/
)

for each line on the board, a number describes the state of the line.

using lookup tables and generated functions (gen.py), line states are
updated efficiently for all possible flipping patterns.

more specifically, a given line state and player move on that line
determine the flipping pattern (lookup table 1, about 1MB).

a specific line and flipping pattern determine which generated
function to call to perform the correct flips (lookup table 2).

so far, the speed is comparable to a bitboard implemention
(see ref.py), at about 130M moves/sec.

performance seems quite sensitive to caching, and subtle
optimizations in the C++ compiler that may or may not be triggered.

jan's C version still appears to be much faster, possibly because of
using function pointers instead of virtual calls.
'''

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
flippers_y = {}
flips_nr = {}
nr_flips = {}
for s in range(3**8):
    for idx in range(8):
        flips = state_flips(s, idx, '2')
        if flips not in flips_nr:
            nr = len(flips_nr)
            flips_nr[flips] = nr
            nr_flips[nr] = flips
        flippers_y[s << 5 | idx << 2 | BLACK+1] = flips_nr[flips]

        flips = state_flips(s, idx, '0')
        if flips not in flips_nr:
            nr = len(flips_nr)
            flips_nr[flips] = nr
            nr_flips[nr] = flips
        flippers_y[s << 5 | idx << 2 | WHITE+1] = flips_nr[flips]

flippers_x = [0 for x in range(2**(13+3+2))]
for key, value in flippers_y.items():
    flippers_x[key] = value

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


class Put:
    pass

class Flip:
    pass

class put_a1(Put):
    def go(self):
        global state_0
        global state_8
        global state_16
        global state_38
        flipnr = flippers_x[state_0 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_16 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[16 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[38 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_0 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_17 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[17 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[39 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_0 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_18 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[18 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[40 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_0 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_19 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[19 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[41 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_0 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_42 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[42 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_0 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_43 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[43 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_0 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_44 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[44 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_0 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[0 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_45 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[45 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_1 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_17 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[17 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[37 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_1 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_18 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[18 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[38 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_1 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_19 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[19 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[39 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_1 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[40 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_1 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[41 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_1 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_42 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[42 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_1 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_43 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[43 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_1 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[1 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_44 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[44 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_2 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_18 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[18 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[36 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_2 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_19 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[19 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[37 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_2 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[38 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_2 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[39 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_2 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[40 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_2 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[41 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_2 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_42 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[42 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_2 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[2 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_43 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[43 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_3 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_19 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[19 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[35 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_3 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[36 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_3 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[37 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_3 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[38 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_3 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[39 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_3 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[40 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_3 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[41 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_3 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[3 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_42 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[42 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_4 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_20 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[20 << 6 | flipnr].go()
        flipnr = flippers_x[state_34 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[34 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_4 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[35 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_4 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[36 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_4 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[37 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_4 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[38 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_4 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[39 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_4 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[40 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_4 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[4 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_27 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[27 << 6 | flipnr].go()
        flipnr = flippers_x[state_41 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[41 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_5 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_21 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[21 << 6 | flipnr].go()
        flipnr = flippers_x[state_33 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[33 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_5 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_34 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[34 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_5 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[35 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_5 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[36 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_5 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[37 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_5 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[38 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_5 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_27 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[27 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[39 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_5 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[5 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_28 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[28 << 6 | flipnr].go()
        flipnr = flippers_x[state_40 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[40 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_6 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_22 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[22 << 6 | flipnr].go()
        flipnr = flippers_x[state_32 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[32 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_6 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_33 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[33 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_6 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_34 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[34 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_6 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[35 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_6 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[36 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_6 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_27 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[27 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[37 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_6 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_28 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[28 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[38 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_6 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[6 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_29 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[29 << 6 | flipnr].go()
        flipnr = flippers_x[state_39 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[39 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_7 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_8 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[8 << 6 | flipnr].go()
        flipnr = flippers_x[state_23 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[23 << 6 | flipnr].go()
        flipnr = flippers_x[state_31 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[31 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_7 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_9 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[9 << 6 | flipnr].go()
        flipnr = flippers_x[state_24 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[24 << 6 | flipnr].go()
        flipnr = flippers_x[state_32 << 5 | 4 | turn+1]
        if flipnr > 0:
            flip_table[32 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_7 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_10 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[10 << 6 | flipnr].go()
        flipnr = flippers_x[state_25 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[25 << 6 | flipnr].go()
        flipnr = flippers_x[state_33 << 5 | 8 | turn+1]
        if flipnr > 0:
            flip_table[33 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_7 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_11 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[11 << 6 | flipnr].go()
        flipnr = flippers_x[state_26 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[26 << 6 | flipnr].go()
        flipnr = flippers_x[state_34 << 5 | 12 | turn+1]
        if flipnr > 0:
            flip_table[34 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_7 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_12 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[12 << 6 | flipnr].go()
        flipnr = flippers_x[state_27 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[27 << 6 | flipnr].go()
        flipnr = flippers_x[state_35 << 5 | 16 | turn+1]
        if flipnr > 0:
            flip_table[35 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_7 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_13 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[13 << 6 | flipnr].go()
        flipnr = flippers_x[state_28 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[28 << 6 | flipnr].go()
        flipnr = flippers_x[state_36 << 5 | 20 | turn+1]
        if flipnr > 0:
            flip_table[36 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_7 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_14 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[14 << 6 | flipnr].go()
        flipnr = flippers_x[state_29 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[29 << 6 | flipnr].go()
        flipnr = flippers_x[state_37 << 5 | 24 | turn+1]
        if flipnr > 0:
            flip_table[37 << 6 | flipnr].go()
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
        flipnr = flippers_x[state_7 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[7 << 6 | flipnr].go()
        flipnr = flippers_x[state_15 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[15 << 6 | flipnr].go()
        flipnr = flippers_x[state_30 << 5 | 0 | turn+1]
        if flipnr > 0:
            flip_table[30 << 6 | flipnr].go()
        flipnr = flippers_x[state_38 << 5 | 28 | turn+1]
        if flipnr > 0:
            flip_table[38 << 6 | flipnr].go()
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

flip_table = [None for x in range(4096)]
flip_table[1] = flip_b1()
flip_table[65] = flip_b2()
flip_table[129] = flip_b3()
flip_table[193] = flip_b4()
flip_table[257] = flip_b5()
flip_table[321] = flip_b6()
flip_table[385] = flip_b7()
flip_table[449] = flip_b8()
flip_table[513] = flip_a2()
flip_table[577] = flip_b2()
flip_table[641] = flip_c2()
flip_table[705] = flip_d2()
flip_table[769] = flip_e2()
flip_table[833] = flip_f2()
flip_table[897] = flip_g2()
flip_table[961] = flip_h2()
flip_table[1153] = flip_b2()
flip_table[1217] = flip_b3()
flip_table[1281] = flip_b4()
flip_table[1345] = flip_b5()
flip_table[1409] = flip_b6()
flip_table[1473] = flip_b7()
flip_table[1537] = flip_c7()
flip_table[1601] = flip_d7()
flip_table[1665] = flip_e7()
flip_table[1729] = flip_f7()
flip_table[1793] = flip_g7()
flip_table[2113] = flip_b7()
flip_table[2177] = flip_b6()
flip_table[2241] = flip_b5()
flip_table[2305] = flip_b4()
flip_table[2369] = flip_b3()
flip_table[2433] = flip_b2()
flip_table[2497] = flip_c2()
flip_table[2561] = flip_d2()
flip_table[2625] = flip_e2()
flip_table[2689] = flip_f2()
flip_table[2753] = flip_g2()
flip_table[2] = flip_c1()
flip_table[66] = flip_c2()
flip_table[130] = flip_c3()
flip_table[194] = flip_c4()
flip_table[258] = flip_c5()
flip_table[322] = flip_c6()
flip_table[386] = flip_c7()
flip_table[450] = flip_c8()
flip_table[514] = flip_a3()
flip_table[578] = flip_b3()
flip_table[642] = flip_c3()
flip_table[706] = flip_d3()
flip_table[770] = flip_e3()
flip_table[834] = flip_f3()
flip_table[898] = flip_g3()
flip_table[962] = flip_h3()
flip_table[1218] = flip_c2()
flip_table[1282] = flip_c3()
flip_table[1346] = flip_c4()
flip_table[1410] = flip_c5()
flip_table[1474] = flip_c6()
flip_table[1538] = flip_d6()
flip_table[1602] = flip_e6()
flip_table[1666] = flip_f6()
flip_table[1730] = flip_g6()
flip_table[2178] = flip_c7()
flip_table[2242] = flip_c6()
flip_table[2306] = flip_c5()
flip_table[2370] = flip_c4()
flip_table[2434] = flip_c3()
flip_table[2498] = flip_d3()
flip_table[2562] = flip_e3()
flip_table[2626] = flip_f3()
flip_table[2690] = flip_g3()
flip_table[3] = flip_b1_c1()
flip_table[67] = flip_b2_c2()
flip_table[131] = flip_b3_c3()
flip_table[195] = flip_b4_c4()
flip_table[259] = flip_b5_c5()
flip_table[323] = flip_b6_c6()
flip_table[387] = flip_b7_c7()
flip_table[451] = flip_b8_c8()
flip_table[515] = flip_a2_a3()
flip_table[579] = flip_b2_b3()
flip_table[643] = flip_c2_c3()
flip_table[707] = flip_d2_d3()
flip_table[771] = flip_e2_e3()
flip_table[835] = flip_f2_f3()
flip_table[899] = flip_g2_g3()
flip_table[963] = flip_h2_h3()
flip_table[1155] = flip_b2()
flip_table[1219] = flip_b3_c2()
flip_table[1283] = flip_b4_c3()
flip_table[1347] = flip_b5_c4()
flip_table[1411] = flip_b6_c5()
flip_table[1475] = flip_b7_c6()
flip_table[1539] = flip_c7_d6()
flip_table[1603] = flip_d7_e6()
flip_table[1667] = flip_e7_f6()
flip_table[1731] = flip_f7_g6()
flip_table[1795] = flip_g7()
flip_table[2115] = flip_b7()
flip_table[2179] = flip_b6_c7()
flip_table[2243] = flip_b5_c6()
flip_table[2307] = flip_b4_c5()
flip_table[2371] = flip_b3_c4()
flip_table[2435] = flip_b2_c3()
flip_table[2499] = flip_c2_d3()
flip_table[2563] = flip_d2_e3()
flip_table[2627] = flip_e2_f3()
flip_table[2691] = flip_f2_g3()
flip_table[2755] = flip_g2()
flip_table[4] = flip_b1_c1()
flip_table[68] = flip_b2_c2()
flip_table[132] = flip_b3_c3()
flip_table[196] = flip_b4_c4()
flip_table[260] = flip_b5_c5()
flip_table[324] = flip_b6_c6()
flip_table[388] = flip_b7_c7()
flip_table[452] = flip_b8_c8()
flip_table[516] = flip_a2_a3()
flip_table[580] = flip_b2_b3()
flip_table[644] = flip_c2_c3()
flip_table[708] = flip_d2_d3()
flip_table[772] = flip_e2_e3()
flip_table[836] = flip_f2_f3()
flip_table[900] = flip_g2_g3()
flip_table[964] = flip_h2_h3()
flip_table[1156] = flip_b2()
flip_table[1220] = flip_b3_c2()
flip_table[1284] = flip_b4_c3()
flip_table[1348] = flip_b5_c4()
flip_table[1412] = flip_b6_c5()
flip_table[1476] = flip_b7_c6()
flip_table[1540] = flip_c7_d6()
flip_table[1604] = flip_d7_e6()
flip_table[1668] = flip_e7_f6()
flip_table[1732] = flip_f7_g6()
flip_table[1796] = flip_g7()
flip_table[2116] = flip_b7()
flip_table[2180] = flip_b6_c7()
flip_table[2244] = flip_b5_c6()
flip_table[2308] = flip_b4_c5()
flip_table[2372] = flip_b3_c4()
flip_table[2436] = flip_b2_c3()
flip_table[2500] = flip_c2_d3()
flip_table[2564] = flip_d2_e3()
flip_table[2628] = flip_e2_f3()
flip_table[2692] = flip_f2_g3()
flip_table[2756] = flip_g2()
flip_table[5] = flip_d1()
flip_table[69] = flip_d2()
flip_table[133] = flip_d3()
flip_table[197] = flip_d4()
flip_table[261] = flip_d5()
flip_table[325] = flip_d6()
flip_table[389] = flip_d7()
flip_table[453] = flip_d8()
flip_table[517] = flip_a4()
flip_table[581] = flip_b4()
flip_table[645] = flip_c4()
flip_table[709] = flip_d4()
flip_table[773] = flip_e4()
flip_table[837] = flip_f4()
flip_table[901] = flip_g4()
flip_table[965] = flip_h4()
flip_table[1285] = flip_d2()
flip_table[1349] = flip_d3()
flip_table[1413] = flip_d4()
flip_table[1477] = flip_d5()
flip_table[1541] = flip_e5()
flip_table[1605] = flip_f5()
flip_table[1669] = flip_g5()
flip_table[2245] = flip_d7()
flip_table[2309] = flip_d6()
flip_table[2373] = flip_d5()
flip_table[2437] = flip_d4()
flip_table[2501] = flip_e4()
flip_table[2565] = flip_f4()
flip_table[2629] = flip_g4()
flip_table[6] = flip_b1_d1()
flip_table[70] = flip_b2_d2()
flip_table[134] = flip_b3_d3()
flip_table[198] = flip_b4_d4()
flip_table[262] = flip_b5_d5()
flip_table[326] = flip_b6_d6()
flip_table[390] = flip_b7_d7()
flip_table[454] = flip_b8_d8()
flip_table[518] = flip_a2_a4()
flip_table[582] = flip_b2_b4()
flip_table[646] = flip_c2_c4()
flip_table[710] = flip_d2_d4()
flip_table[774] = flip_e2_e4()
flip_table[838] = flip_f2_f4()
flip_table[902] = flip_g2_g4()
flip_table[966] = flip_h2_h4()
flip_table[1158] = flip_b2()
flip_table[1222] = flip_b3()
flip_table[1286] = flip_b4_d2()
flip_table[1350] = flip_b5_d3()
flip_table[1414] = flip_b6_d4()
flip_table[1478] = flip_b7_d5()
flip_table[1542] = flip_c7_e5()
flip_table[1606] = flip_d7_f5()
flip_table[1670] = flip_e7_g5()
flip_table[1734] = flip_f7()
flip_table[1798] = flip_g7()
flip_table[2118] = flip_b7()
flip_table[2182] = flip_b6()
flip_table[2246] = flip_b5_d7()
flip_table[2310] = flip_b4_d6()
flip_table[2374] = flip_b3_d5()
flip_table[2438] = flip_b2_d4()
flip_table[2502] = flip_c2_e4()
flip_table[2566] = flip_d2_f4()
flip_table[2630] = flip_e2_g4()
flip_table[2694] = flip_f2()
flip_table[2758] = flip_g2()
flip_table[7] = flip_c1_d1()
flip_table[71] = flip_c2_d2()
flip_table[135] = flip_c3_d3()
flip_table[199] = flip_c4_d4()
flip_table[263] = flip_c5_d5()
flip_table[327] = flip_c6_d6()
flip_table[391] = flip_c7_d7()
flip_table[455] = flip_c8_d8()
flip_table[519] = flip_a3_a4()
flip_table[583] = flip_b3_b4()
flip_table[647] = flip_c3_c4()
flip_table[711] = flip_d3_d4()
flip_table[775] = flip_e3_e4()
flip_table[839] = flip_f3_f4()
flip_table[903] = flip_g3_g4()
flip_table[967] = flip_h3_h4()
flip_table[1223] = flip_c2()
flip_table[1287] = flip_c3_d2()
flip_table[1351] = flip_c4_d3()
flip_table[1415] = flip_c5_d4()
flip_table[1479] = flip_c6_d5()
flip_table[1543] = flip_d6_e5()
flip_table[1607] = flip_e6_f5()
flip_table[1671] = flip_f6_g5()
flip_table[1735] = flip_g6()
flip_table[2183] = flip_c7()
flip_table[2247] = flip_c6_d7()
flip_table[2311] = flip_c5_d6()
flip_table[2375] = flip_c4_d5()
flip_table[2439] = flip_c3_d4()
flip_table[2503] = flip_d3_e4()
flip_table[2567] = flip_e3_f4()
flip_table[2631] = flip_f3_g4()
flip_table[2695] = flip_g3()
flip_table[8] = flip_b1_c1_d1()
flip_table[72] = flip_b2_c2_d2()
flip_table[136] = flip_b3_c3_d3()
flip_table[200] = flip_b4_c4_d4()
flip_table[264] = flip_b5_c5_d5()
flip_table[328] = flip_b6_c6_d6()
flip_table[392] = flip_b7_c7_d7()
flip_table[456] = flip_b8_c8_d8()
flip_table[520] = flip_a2_a3_a4()
flip_table[584] = flip_b2_b3_b4()
flip_table[648] = flip_c2_c3_c4()
flip_table[712] = flip_d2_d3_d4()
flip_table[776] = flip_e2_e3_e4()
flip_table[840] = flip_f2_f3_f4()
flip_table[904] = flip_g2_g3_g4()
flip_table[968] = flip_h2_h3_h4()
flip_table[1160] = flip_b2()
flip_table[1224] = flip_b3_c2()
flip_table[1288] = flip_b4_c3_d2()
flip_table[1352] = flip_b5_c4_d3()
flip_table[1416] = flip_b6_c5_d4()
flip_table[1480] = flip_b7_c6_d5()
flip_table[1544] = flip_c7_d6_e5()
flip_table[1608] = flip_d7_e6_f5()
flip_table[1672] = flip_e7_f6_g5()
flip_table[1736] = flip_f7_g6()
flip_table[1800] = flip_g7()
flip_table[2120] = flip_b7()
flip_table[2184] = flip_b6_c7()
flip_table[2248] = flip_b5_c6_d7()
flip_table[2312] = flip_b4_c5_d6()
flip_table[2376] = flip_b3_c4_d5()
flip_table[2440] = flip_b2_c3_d4()
flip_table[2504] = flip_c2_d3_e4()
flip_table[2568] = flip_d2_e3_f4()
flip_table[2632] = flip_e2_f3_g4()
flip_table[2696] = flip_f2_g3()
flip_table[2760] = flip_g2()
flip_table[9] = flip_b1_c1_d1()
flip_table[73] = flip_b2_c2_d2()
flip_table[137] = flip_b3_c3_d3()
flip_table[201] = flip_b4_c4_d4()
flip_table[265] = flip_b5_c5_d5()
flip_table[329] = flip_b6_c6_d6()
flip_table[393] = flip_b7_c7_d7()
flip_table[457] = flip_b8_c8_d8()
flip_table[521] = flip_a2_a3_a4()
flip_table[585] = flip_b2_b3_b4()
flip_table[649] = flip_c2_c3_c4()
flip_table[713] = flip_d2_d3_d4()
flip_table[777] = flip_e2_e3_e4()
flip_table[841] = flip_f2_f3_f4()
flip_table[905] = flip_g2_g3_g4()
flip_table[969] = flip_h2_h3_h4()
flip_table[1161] = flip_b2()
flip_table[1225] = flip_b3_c2()
flip_table[1289] = flip_b4_c3_d2()
flip_table[1353] = flip_b5_c4_d3()
flip_table[1417] = flip_b6_c5_d4()
flip_table[1481] = flip_b7_c6_d5()
flip_table[1545] = flip_c7_d6_e5()
flip_table[1609] = flip_d7_e6_f5()
flip_table[1673] = flip_e7_f6_g5()
flip_table[1737] = flip_f7_g6()
flip_table[1801] = flip_g7()
flip_table[2121] = flip_b7()
flip_table[2185] = flip_b6_c7()
flip_table[2249] = flip_b5_c6_d7()
flip_table[2313] = flip_b4_c5_d6()
flip_table[2377] = flip_b3_c4_d5()
flip_table[2441] = flip_b2_c3_d4()
flip_table[2505] = flip_c2_d3_e4()
flip_table[2569] = flip_d2_e3_f4()
flip_table[2633] = flip_e2_f3_g4()
flip_table[2697] = flip_f2_g3()
flip_table[2761] = flip_g2()
flip_table[10] = flip_c1_d1()
flip_table[74] = flip_c2_d2()
flip_table[138] = flip_c3_d3()
flip_table[202] = flip_c4_d4()
flip_table[266] = flip_c5_d5()
flip_table[330] = flip_c6_d6()
flip_table[394] = flip_c7_d7()
flip_table[458] = flip_c8_d8()
flip_table[522] = flip_a3_a4()
flip_table[586] = flip_b3_b4()
flip_table[650] = flip_c3_c4()
flip_table[714] = flip_d3_d4()
flip_table[778] = flip_e3_e4()
flip_table[842] = flip_f3_f4()
flip_table[906] = flip_g3_g4()
flip_table[970] = flip_h3_h4()
flip_table[1226] = flip_c2()
flip_table[1290] = flip_c3_d2()
flip_table[1354] = flip_c4_d3()
flip_table[1418] = flip_c5_d4()
flip_table[1482] = flip_c6_d5()
flip_table[1546] = flip_d6_e5()
flip_table[1610] = flip_e6_f5()
flip_table[1674] = flip_f6_g5()
flip_table[1738] = flip_g6()
flip_table[2186] = flip_c7()
flip_table[2250] = flip_c6_d7()
flip_table[2314] = flip_c5_d6()
flip_table[2378] = flip_c4_d5()
flip_table[2442] = flip_c3_d4()
flip_table[2506] = flip_d3_e4()
flip_table[2570] = flip_e3_f4()
flip_table[2634] = flip_f3_g4()
flip_table[2698] = flip_g3()
flip_table[11] = flip_e1()
flip_table[75] = flip_e2()
flip_table[139] = flip_e3()
flip_table[203] = flip_e4()
flip_table[267] = flip_e5()
flip_table[331] = flip_e6()
flip_table[395] = flip_e7()
flip_table[459] = flip_e8()
flip_table[523] = flip_a5()
flip_table[587] = flip_b5()
flip_table[651] = flip_c5()
flip_table[715] = flip_d5()
flip_table[779] = flip_e5()
flip_table[843] = flip_f5()
flip_table[907] = flip_g5()
flip_table[971] = flip_h5()
flip_table[1355] = flip_e2()
flip_table[1419] = flip_e3()
flip_table[1483] = flip_e4()
flip_table[1547] = flip_f4()
flip_table[1611] = flip_g4()
flip_table[2315] = flip_e7()
flip_table[2379] = flip_e6()
flip_table[2443] = flip_e5()
flip_table[2507] = flip_f5()
flip_table[2571] = flip_g5()
flip_table[12] = flip_c1_e1()
flip_table[76] = flip_c2_e2()
flip_table[140] = flip_c3_e3()
flip_table[204] = flip_c4_e4()
flip_table[268] = flip_c5_e5()
flip_table[332] = flip_c6_e6()
flip_table[396] = flip_c7_e7()
flip_table[460] = flip_c8_e8()
flip_table[524] = flip_a3_a5()
flip_table[588] = flip_b3_b5()
flip_table[652] = flip_c3_c5()
flip_table[716] = flip_d3_d5()
flip_table[780] = flip_e3_e5()
flip_table[844] = flip_f3_f5()
flip_table[908] = flip_g3_g5()
flip_table[972] = flip_h3_h5()
flip_table[1228] = flip_c2()
flip_table[1292] = flip_c3()
flip_table[1356] = flip_c4_e2()
flip_table[1420] = flip_c5_e3()
flip_table[1484] = flip_c6_e4()
flip_table[1548] = flip_d6_f4()
flip_table[1612] = flip_e6_g4()
flip_table[1676] = flip_f6()
flip_table[1740] = flip_g6()
flip_table[2188] = flip_c7()
flip_table[2252] = flip_c6()
flip_table[2316] = flip_c5_e7()
flip_table[2380] = flip_c4_e6()
flip_table[2444] = flip_c3_e5()
flip_table[2508] = flip_d3_f5()
flip_table[2572] = flip_e3_g5()
flip_table[2636] = flip_f3()
flip_table[2700] = flip_g3()
flip_table[13] = flip_b1_c1_e1()
flip_table[77] = flip_b2_c2_e2()
flip_table[141] = flip_b3_c3_e3()
flip_table[205] = flip_b4_c4_e4()
flip_table[269] = flip_b5_c5_e5()
flip_table[333] = flip_b6_c6_e6()
flip_table[397] = flip_b7_c7_e7()
flip_table[461] = flip_b8_c8_e8()
flip_table[525] = flip_a2_a3_a5()
flip_table[589] = flip_b2_b3_b5()
flip_table[653] = flip_c2_c3_c5()
flip_table[717] = flip_d2_d3_d5()
flip_table[781] = flip_e2_e3_e5()
flip_table[845] = flip_f2_f3_f5()
flip_table[909] = flip_g2_g3_g5()
flip_table[973] = flip_h2_h3_h5()
flip_table[1165] = flip_b2()
flip_table[1229] = flip_b3_c2()
flip_table[1293] = flip_b4_c3()
flip_table[1357] = flip_b5_c4_e2()
flip_table[1421] = flip_b6_c5_e3()
flip_table[1485] = flip_b7_c6_e4()
flip_table[1549] = flip_c7_d6_f4()
flip_table[1613] = flip_d7_e6_g4()
flip_table[1677] = flip_e7_f6()
flip_table[1741] = flip_f7_g6()
flip_table[1805] = flip_g7()
flip_table[2125] = flip_b7()
flip_table[2189] = flip_b6_c7()
flip_table[2253] = flip_b5_c6()
flip_table[2317] = flip_b4_c5_e7()
flip_table[2381] = flip_b3_c4_e6()
flip_table[2445] = flip_b2_c3_e5()
flip_table[2509] = flip_c2_d3_f5()
flip_table[2573] = flip_d2_e3_g5()
flip_table[2637] = flip_e2_f3()
flip_table[2701] = flip_f2_g3()
flip_table[2765] = flip_g2()
flip_table[14] = flip_d1_e1()
flip_table[78] = flip_d2_e2()
flip_table[142] = flip_d3_e3()
flip_table[206] = flip_d4_e4()
flip_table[270] = flip_d5_e5()
flip_table[334] = flip_d6_e6()
flip_table[398] = flip_d7_e7()
flip_table[462] = flip_d8_e8()
flip_table[526] = flip_a4_a5()
flip_table[590] = flip_b4_b5()
flip_table[654] = flip_c4_c5()
flip_table[718] = flip_d4_d5()
flip_table[782] = flip_e4_e5()
flip_table[846] = flip_f4_f5()
flip_table[910] = flip_g4_g5()
flip_table[974] = flip_h4_h5()
flip_table[1294] = flip_d2()
flip_table[1358] = flip_d3_e2()
flip_table[1422] = flip_d4_e3()
flip_table[1486] = flip_d5_e4()
flip_table[1550] = flip_e5_f4()
flip_table[1614] = flip_f5_g4()
flip_table[1678] = flip_g5()
flip_table[2254] = flip_d7()
flip_table[2318] = flip_d6_e7()
flip_table[2382] = flip_d5_e6()
flip_table[2446] = flip_d4_e5()
flip_table[2510] = flip_e4_f5()
flip_table[2574] = flip_f4_g5()
flip_table[2638] = flip_g4()
flip_table[15] = flip_b1_d1_e1()
flip_table[79] = flip_b2_d2_e2()
flip_table[143] = flip_b3_d3_e3()
flip_table[207] = flip_b4_d4_e4()
flip_table[271] = flip_b5_d5_e5()
flip_table[335] = flip_b6_d6_e6()
flip_table[399] = flip_b7_d7_e7()
flip_table[463] = flip_b8_d8_e8()
flip_table[527] = flip_a2_a4_a5()
flip_table[591] = flip_b2_b4_b5()
flip_table[655] = flip_c2_c4_c5()
flip_table[719] = flip_d2_d4_d5()
flip_table[783] = flip_e2_e4_e5()
flip_table[847] = flip_f2_f4_f5()
flip_table[911] = flip_g2_g4_g5()
flip_table[975] = flip_h2_h4_h5()
flip_table[1167] = flip_b2()
flip_table[1231] = flip_b3()
flip_table[1295] = flip_b4_d2()
flip_table[1359] = flip_b5_d3_e2()
flip_table[1423] = flip_b6_d4_e3()
flip_table[1487] = flip_b7_d5_e4()
flip_table[1551] = flip_c7_e5_f4()
flip_table[1615] = flip_d7_f5_g4()
flip_table[1679] = flip_e7_g5()
flip_table[1743] = flip_f7()
flip_table[1807] = flip_g7()
flip_table[2127] = flip_b7()
flip_table[2191] = flip_b6()
flip_table[2255] = flip_b5_d7()
flip_table[2319] = flip_b4_d6_e7()
flip_table[2383] = flip_b3_d5_e6()
flip_table[2447] = flip_b2_d4_e5()
flip_table[2511] = flip_c2_e4_f5()
flip_table[2575] = flip_d2_f4_g5()
flip_table[2639] = flip_e2_g4()
flip_table[2703] = flip_f2()
flip_table[2767] = flip_g2()
flip_table[16] = flip_c1_d1_e1()
flip_table[80] = flip_c2_d2_e2()
flip_table[144] = flip_c3_d3_e3()
flip_table[208] = flip_c4_d4_e4()
flip_table[272] = flip_c5_d5_e5()
flip_table[336] = flip_c6_d6_e6()
flip_table[400] = flip_c7_d7_e7()
flip_table[464] = flip_c8_d8_e8()
flip_table[528] = flip_a3_a4_a5()
flip_table[592] = flip_b3_b4_b5()
flip_table[656] = flip_c3_c4_c5()
flip_table[720] = flip_d3_d4_d5()
flip_table[784] = flip_e3_e4_e5()
flip_table[848] = flip_f3_f4_f5()
flip_table[912] = flip_g3_g4_g5()
flip_table[976] = flip_h3_h4_h5()
flip_table[1232] = flip_c2()
flip_table[1296] = flip_c3_d2()
flip_table[1360] = flip_c4_d3_e2()
flip_table[1424] = flip_c5_d4_e3()
flip_table[1488] = flip_c6_d5_e4()
flip_table[1552] = flip_d6_e5_f4()
flip_table[1616] = flip_e6_f5_g4()
flip_table[1680] = flip_f6_g5()
flip_table[1744] = flip_g6()
flip_table[2192] = flip_c7()
flip_table[2256] = flip_c6_d7()
flip_table[2320] = flip_c5_d6_e7()
flip_table[2384] = flip_c4_d5_e6()
flip_table[2448] = flip_c3_d4_e5()
flip_table[2512] = flip_d3_e4_f5()
flip_table[2576] = flip_e3_f4_g5()
flip_table[2640] = flip_f3_g4()
flip_table[2704] = flip_g3()
flip_table[17] = flip_b1_c1_d1_e1()
flip_table[81] = flip_b2_c2_d2_e2()
flip_table[145] = flip_b3_c3_d3_e3()
flip_table[209] = flip_b4_c4_d4_e4()
flip_table[273] = flip_b5_c5_d5_e5()
flip_table[337] = flip_b6_c6_d6_e6()
flip_table[401] = flip_b7_c7_d7_e7()
flip_table[465] = flip_b8_c8_d8_e8()
flip_table[529] = flip_a2_a3_a4_a5()
flip_table[593] = flip_b2_b3_b4_b5()
flip_table[657] = flip_c2_c3_c4_c5()
flip_table[721] = flip_d2_d3_d4_d5()
flip_table[785] = flip_e2_e3_e4_e5()
flip_table[849] = flip_f2_f3_f4_f5()
flip_table[913] = flip_g2_g3_g4_g5()
flip_table[977] = flip_h2_h3_h4_h5()
flip_table[1169] = flip_b2()
flip_table[1233] = flip_b3_c2()
flip_table[1297] = flip_b4_c3_d2()
flip_table[1361] = flip_b5_c4_d3_e2()
flip_table[1425] = flip_b6_c5_d4_e3()
flip_table[1489] = flip_b7_c6_d5_e4()
flip_table[1553] = flip_c7_d6_e5_f4()
flip_table[1617] = flip_d7_e6_f5_g4()
flip_table[1681] = flip_e7_f6_g5()
flip_table[1745] = flip_f7_g6()
flip_table[1809] = flip_g7()
flip_table[2129] = flip_b7()
flip_table[2193] = flip_b6_c7()
flip_table[2257] = flip_b5_c6_d7()
flip_table[2321] = flip_b4_c5_d6_e7()
flip_table[2385] = flip_b3_c4_d5_e6()
flip_table[2449] = flip_b2_c3_d4_e5()
flip_table[2513] = flip_c2_d3_e4_f5()
flip_table[2577] = flip_d2_e3_f4_g5()
flip_table[2641] = flip_e2_f3_g4()
flip_table[2705] = flip_f2_g3()
flip_table[2769] = flip_g2()
flip_table[18] = flip_b1_c1_d1_e1()
flip_table[82] = flip_b2_c2_d2_e2()
flip_table[146] = flip_b3_c3_d3_e3()
flip_table[210] = flip_b4_c4_d4_e4()
flip_table[274] = flip_b5_c5_d5_e5()
flip_table[338] = flip_b6_c6_d6_e6()
flip_table[402] = flip_b7_c7_d7_e7()
flip_table[466] = flip_b8_c8_d8_e8()
flip_table[530] = flip_a2_a3_a4_a5()
flip_table[594] = flip_b2_b3_b4_b5()
flip_table[658] = flip_c2_c3_c4_c5()
flip_table[722] = flip_d2_d3_d4_d5()
flip_table[786] = flip_e2_e3_e4_e5()
flip_table[850] = flip_f2_f3_f4_f5()
flip_table[914] = flip_g2_g3_g4_g5()
flip_table[978] = flip_h2_h3_h4_h5()
flip_table[1170] = flip_b2()
flip_table[1234] = flip_b3_c2()
flip_table[1298] = flip_b4_c3_d2()
flip_table[1362] = flip_b5_c4_d3_e2()
flip_table[1426] = flip_b6_c5_d4_e3()
flip_table[1490] = flip_b7_c6_d5_e4()
flip_table[1554] = flip_c7_d6_e5_f4()
flip_table[1618] = flip_d7_e6_f5_g4()
flip_table[1682] = flip_e7_f6_g5()
flip_table[1746] = flip_f7_g6()
flip_table[1810] = flip_g7()
flip_table[2130] = flip_b7()
flip_table[2194] = flip_b6_c7()
flip_table[2258] = flip_b5_c6_d7()
flip_table[2322] = flip_b4_c5_d6_e7()
flip_table[2386] = flip_b3_c4_d5_e6()
flip_table[2450] = flip_b2_c3_d4_e5()
flip_table[2514] = flip_c2_d3_e4_f5()
flip_table[2578] = flip_d2_e3_f4_g5()
flip_table[2642] = flip_e2_f3_g4()
flip_table[2706] = flip_f2_g3()
flip_table[2770] = flip_g2()
flip_table[19] = flip_c1_d1_e1()
flip_table[83] = flip_c2_d2_e2()
flip_table[147] = flip_c3_d3_e3()
flip_table[211] = flip_c4_d4_e4()
flip_table[275] = flip_c5_d5_e5()
flip_table[339] = flip_c6_d6_e6()
flip_table[403] = flip_c7_d7_e7()
flip_table[467] = flip_c8_d8_e8()
flip_table[531] = flip_a3_a4_a5()
flip_table[595] = flip_b3_b4_b5()
flip_table[659] = flip_c3_c4_c5()
flip_table[723] = flip_d3_d4_d5()
flip_table[787] = flip_e3_e4_e5()
flip_table[851] = flip_f3_f4_f5()
flip_table[915] = flip_g3_g4_g5()
flip_table[979] = flip_h3_h4_h5()
flip_table[1235] = flip_c2()
flip_table[1299] = flip_c3_d2()
flip_table[1363] = flip_c4_d3_e2()
flip_table[1427] = flip_c5_d4_e3()
flip_table[1491] = flip_c6_d5_e4()
flip_table[1555] = flip_d6_e5_f4()
flip_table[1619] = flip_e6_f5_g4()
flip_table[1683] = flip_f6_g5()
flip_table[1747] = flip_g6()
flip_table[2195] = flip_c7()
flip_table[2259] = flip_c6_d7()
flip_table[2323] = flip_c5_d6_e7()
flip_table[2387] = flip_c4_d5_e6()
flip_table[2451] = flip_c3_d4_e5()
flip_table[2515] = flip_d3_e4_f5()
flip_table[2579] = flip_e3_f4_g5()
flip_table[2643] = flip_f3_g4()
flip_table[2707] = flip_g3()
flip_table[20] = flip_d1_e1()
flip_table[84] = flip_d2_e2()
flip_table[148] = flip_d3_e3()
flip_table[212] = flip_d4_e4()
flip_table[276] = flip_d5_e5()
flip_table[340] = flip_d6_e6()
flip_table[404] = flip_d7_e7()
flip_table[468] = flip_d8_e8()
flip_table[532] = flip_a4_a5()
flip_table[596] = flip_b4_b5()
flip_table[660] = flip_c4_c5()
flip_table[724] = flip_d4_d5()
flip_table[788] = flip_e4_e5()
flip_table[852] = flip_f4_f5()
flip_table[916] = flip_g4_g5()
flip_table[980] = flip_h4_h5()
flip_table[1300] = flip_d2()
flip_table[1364] = flip_d3_e2()
flip_table[1428] = flip_d4_e3()
flip_table[1492] = flip_d5_e4()
flip_table[1556] = flip_e5_f4()
flip_table[1620] = flip_f5_g4()
flip_table[1684] = flip_g5()
flip_table[2260] = flip_d7()
flip_table[2324] = flip_d6_e7()
flip_table[2388] = flip_d5_e6()
flip_table[2452] = flip_d4_e5()
flip_table[2516] = flip_e4_f5()
flip_table[2580] = flip_f4_g5()
flip_table[2644] = flip_g4()
flip_table[21] = flip_f1()
flip_table[85] = flip_f2()
flip_table[149] = flip_f3()
flip_table[213] = flip_f4()
flip_table[277] = flip_f5()
flip_table[341] = flip_f6()
flip_table[405] = flip_f7()
flip_table[469] = flip_f8()
flip_table[533] = flip_a6()
flip_table[597] = flip_b6()
flip_table[661] = flip_c6()
flip_table[725] = flip_d6()
flip_table[789] = flip_e6()
flip_table[853] = flip_f6()
flip_table[917] = flip_g6()
flip_table[981] = flip_h6()
flip_table[1429] = flip_f2()
flip_table[1493] = flip_f3()
flip_table[1557] = flip_g3()
flip_table[2389] = flip_f7()
flip_table[2453] = flip_f6()
flip_table[2517] = flip_g6()
flip_table[22] = flip_d1_f1()
flip_table[86] = flip_d2_f2()
flip_table[150] = flip_d3_f3()
flip_table[214] = flip_d4_f4()
flip_table[278] = flip_d5_f5()
flip_table[342] = flip_d6_f6()
flip_table[406] = flip_d7_f7()
flip_table[470] = flip_d8_f8()
flip_table[534] = flip_a4_a6()
flip_table[598] = flip_b4_b6()
flip_table[662] = flip_c4_c6()
flip_table[726] = flip_d4_d6()
flip_table[790] = flip_e4_e6()
flip_table[854] = flip_f4_f6()
flip_table[918] = flip_g4_g6()
flip_table[982] = flip_h4_h6()
flip_table[1302] = flip_d2()
flip_table[1366] = flip_d3()
flip_table[1430] = flip_d4_f2()
flip_table[1494] = flip_d5_f3()
flip_table[1558] = flip_e5_g3()
flip_table[1622] = flip_f5()
flip_table[1686] = flip_g5()
flip_table[2262] = flip_d7()
flip_table[2326] = flip_d6()
flip_table[2390] = flip_d5_f7()
flip_table[2454] = flip_d4_f6()
flip_table[2518] = flip_e4_g6()
flip_table[2582] = flip_f4()
flip_table[2646] = flip_g4()
flip_table[23] = flip_c1_d1_f1()
flip_table[87] = flip_c2_d2_f2()
flip_table[151] = flip_c3_d3_f3()
flip_table[215] = flip_c4_d4_f4()
flip_table[279] = flip_c5_d5_f5()
flip_table[343] = flip_c6_d6_f6()
flip_table[407] = flip_c7_d7_f7()
flip_table[471] = flip_c8_d8_f8()
flip_table[535] = flip_a3_a4_a6()
flip_table[599] = flip_b3_b4_b6()
flip_table[663] = flip_c3_c4_c6()
flip_table[727] = flip_d3_d4_d6()
flip_table[791] = flip_e3_e4_e6()
flip_table[855] = flip_f3_f4_f6()
flip_table[919] = flip_g3_g4_g6()
flip_table[983] = flip_h3_h4_h6()
flip_table[1239] = flip_c2()
flip_table[1303] = flip_c3_d2()
flip_table[1367] = flip_c4_d3()
flip_table[1431] = flip_c5_d4_f2()
flip_table[1495] = flip_c6_d5_f3()
flip_table[1559] = flip_d6_e5_g3()
flip_table[1623] = flip_e6_f5()
flip_table[1687] = flip_f6_g5()
flip_table[1751] = flip_g6()
flip_table[2199] = flip_c7()
flip_table[2263] = flip_c6_d7()
flip_table[2327] = flip_c5_d6()
flip_table[2391] = flip_c4_d5_f7()
flip_table[2455] = flip_c3_d4_f6()
flip_table[2519] = flip_d3_e4_g6()
flip_table[2583] = flip_e3_f4()
flip_table[2647] = flip_f3_g4()
flip_table[2711] = flip_g3()
flip_table[24] = flip_b1_c1_d1_f1()
flip_table[88] = flip_b2_c2_d2_f2()
flip_table[152] = flip_b3_c3_d3_f3()
flip_table[216] = flip_b4_c4_d4_f4()
flip_table[280] = flip_b5_c5_d5_f5()
flip_table[344] = flip_b6_c6_d6_f6()
flip_table[408] = flip_b7_c7_d7_f7()
flip_table[472] = flip_b8_c8_d8_f8()
flip_table[536] = flip_a2_a3_a4_a6()
flip_table[600] = flip_b2_b3_b4_b6()
flip_table[664] = flip_c2_c3_c4_c6()
flip_table[728] = flip_d2_d3_d4_d6()
flip_table[792] = flip_e2_e3_e4_e6()
flip_table[856] = flip_f2_f3_f4_f6()
flip_table[920] = flip_g2_g3_g4_g6()
flip_table[984] = flip_h2_h3_h4_h6()
flip_table[1176] = flip_b2()
flip_table[1240] = flip_b3_c2()
flip_table[1304] = flip_b4_c3_d2()
flip_table[1368] = flip_b5_c4_d3()
flip_table[1432] = flip_b6_c5_d4_f2()
flip_table[1496] = flip_b7_c6_d5_f3()
flip_table[1560] = flip_c7_d6_e5_g3()
flip_table[1624] = flip_d7_e6_f5()
flip_table[1688] = flip_e7_f6_g5()
flip_table[1752] = flip_f7_g6()
flip_table[1816] = flip_g7()
flip_table[2136] = flip_b7()
flip_table[2200] = flip_b6_c7()
flip_table[2264] = flip_b5_c6_d7()
flip_table[2328] = flip_b4_c5_d6()
flip_table[2392] = flip_b3_c4_d5_f7()
flip_table[2456] = flip_b2_c3_d4_f6()
flip_table[2520] = flip_c2_d3_e4_g6()
flip_table[2584] = flip_d2_e3_f4()
flip_table[2648] = flip_e2_f3_g4()
flip_table[2712] = flip_f2_g3()
flip_table[2776] = flip_g2()
flip_table[25] = flip_e1_f1()
flip_table[89] = flip_e2_f2()
flip_table[153] = flip_e3_f3()
flip_table[217] = flip_e4_f4()
flip_table[281] = flip_e5_f5()
flip_table[345] = flip_e6_f6()
flip_table[409] = flip_e7_f7()
flip_table[473] = flip_e8_f8()
flip_table[537] = flip_a5_a6()
flip_table[601] = flip_b5_b6()
flip_table[665] = flip_c5_c6()
flip_table[729] = flip_d5_d6()
flip_table[793] = flip_e5_e6()
flip_table[857] = flip_f5_f6()
flip_table[921] = flip_g5_g6()
flip_table[985] = flip_h5_h6()
flip_table[1369] = flip_e2()
flip_table[1433] = flip_e3_f2()
flip_table[1497] = flip_e4_f3()
flip_table[1561] = flip_f4_g3()
flip_table[1625] = flip_g4()
flip_table[2329] = flip_e7()
flip_table[2393] = flip_e6_f7()
flip_table[2457] = flip_e5_f6()
flip_table[2521] = flip_f5_g6()
flip_table[2585] = flip_g5()
flip_table[26] = flip_c1_e1_f1()
flip_table[90] = flip_c2_e2_f2()
flip_table[154] = flip_c3_e3_f3()
flip_table[218] = flip_c4_e4_f4()
flip_table[282] = flip_c5_e5_f5()
flip_table[346] = flip_c6_e6_f6()
flip_table[410] = flip_c7_e7_f7()
flip_table[474] = flip_c8_e8_f8()
flip_table[538] = flip_a3_a5_a6()
flip_table[602] = flip_b3_b5_b6()
flip_table[666] = flip_c3_c5_c6()
flip_table[730] = flip_d3_d5_d6()
flip_table[794] = flip_e3_e5_e6()
flip_table[858] = flip_f3_f5_f6()
flip_table[922] = flip_g3_g5_g6()
flip_table[986] = flip_h3_h5_h6()
flip_table[1242] = flip_c2()
flip_table[1306] = flip_c3()
flip_table[1370] = flip_c4_e2()
flip_table[1434] = flip_c5_e3_f2()
flip_table[1498] = flip_c6_e4_f3()
flip_table[1562] = flip_d6_f4_g3()
flip_table[1626] = flip_e6_g4()
flip_table[1690] = flip_f6()
flip_table[1754] = flip_g6()
flip_table[2202] = flip_c7()
flip_table[2266] = flip_c6()
flip_table[2330] = flip_c5_e7()
flip_table[2394] = flip_c4_e6_f7()
flip_table[2458] = flip_c3_e5_f6()
flip_table[2522] = flip_d3_f5_g6()
flip_table[2586] = flip_e3_g5()
flip_table[2650] = flip_f3()
flip_table[2714] = flip_g3()
flip_table[27] = flip_b1_c1_e1_f1()
flip_table[91] = flip_b2_c2_e2_f2()
flip_table[155] = flip_b3_c3_e3_f3()
flip_table[219] = flip_b4_c4_e4_f4()
flip_table[283] = flip_b5_c5_e5_f5()
flip_table[347] = flip_b6_c6_e6_f6()
flip_table[411] = flip_b7_c7_e7_f7()
flip_table[475] = flip_b8_c8_e8_f8()
flip_table[539] = flip_a2_a3_a5_a6()
flip_table[603] = flip_b2_b3_b5_b6()
flip_table[667] = flip_c2_c3_c5_c6()
flip_table[731] = flip_d2_d3_d5_d6()
flip_table[795] = flip_e2_e3_e5_e6()
flip_table[859] = flip_f2_f3_f5_f6()
flip_table[923] = flip_g2_g3_g5_g6()
flip_table[987] = flip_h2_h3_h5_h6()
flip_table[1179] = flip_b2()
flip_table[1243] = flip_b3_c2()
flip_table[1307] = flip_b4_c3()
flip_table[1371] = flip_b5_c4_e2()
flip_table[1435] = flip_b6_c5_e3_f2()
flip_table[1499] = flip_b7_c6_e4_f3()
flip_table[1563] = flip_c7_d6_f4_g3()
flip_table[1627] = flip_d7_e6_g4()
flip_table[1691] = flip_e7_f6()
flip_table[1755] = flip_f7_g6()
flip_table[1819] = flip_g7()
flip_table[2139] = flip_b7()
flip_table[2203] = flip_b6_c7()
flip_table[2267] = flip_b5_c6()
flip_table[2331] = flip_b4_c5_e7()
flip_table[2395] = flip_b3_c4_e6_f7()
flip_table[2459] = flip_b2_c3_e5_f6()
flip_table[2523] = flip_c2_d3_f5_g6()
flip_table[2587] = flip_d2_e3_g5()
flip_table[2651] = flip_e2_f3()
flip_table[2715] = flip_f2_g3()
flip_table[2779] = flip_g2()
flip_table[28] = flip_d1_e1_f1()
flip_table[92] = flip_d2_e2_f2()
flip_table[156] = flip_d3_e3_f3()
flip_table[220] = flip_d4_e4_f4()
flip_table[284] = flip_d5_e5_f5()
flip_table[348] = flip_d6_e6_f6()
flip_table[412] = flip_d7_e7_f7()
flip_table[476] = flip_d8_e8_f8()
flip_table[540] = flip_a4_a5_a6()
flip_table[604] = flip_b4_b5_b6()
flip_table[668] = flip_c4_c5_c6()
flip_table[732] = flip_d4_d5_d6()
flip_table[796] = flip_e4_e5_e6()
flip_table[860] = flip_f4_f5_f6()
flip_table[924] = flip_g4_g5_g6()
flip_table[988] = flip_h4_h5_h6()
flip_table[1308] = flip_d2()
flip_table[1372] = flip_d3_e2()
flip_table[1436] = flip_d4_e3_f2()
flip_table[1500] = flip_d5_e4_f3()
flip_table[1564] = flip_e5_f4_g3()
flip_table[1628] = flip_f5_g4()
flip_table[1692] = flip_g5()
flip_table[2268] = flip_d7()
flip_table[2332] = flip_d6_e7()
flip_table[2396] = flip_d5_e6_f7()
flip_table[2460] = flip_d4_e5_f6()
flip_table[2524] = flip_e4_f5_g6()
flip_table[2588] = flip_f4_g5()
flip_table[2652] = flip_g4()
flip_table[29] = flip_b1_d1_e1_f1()
flip_table[93] = flip_b2_d2_e2_f2()
flip_table[157] = flip_b3_d3_e3_f3()
flip_table[221] = flip_b4_d4_e4_f4()
flip_table[285] = flip_b5_d5_e5_f5()
flip_table[349] = flip_b6_d6_e6_f6()
flip_table[413] = flip_b7_d7_e7_f7()
flip_table[477] = flip_b8_d8_e8_f8()
flip_table[541] = flip_a2_a4_a5_a6()
flip_table[605] = flip_b2_b4_b5_b6()
flip_table[669] = flip_c2_c4_c5_c6()
flip_table[733] = flip_d2_d4_d5_d6()
flip_table[797] = flip_e2_e4_e5_e6()
flip_table[861] = flip_f2_f4_f5_f6()
flip_table[925] = flip_g2_g4_g5_g6()
flip_table[989] = flip_h2_h4_h5_h6()
flip_table[1181] = flip_b2()
flip_table[1245] = flip_b3()
flip_table[1309] = flip_b4_d2()
flip_table[1373] = flip_b5_d3_e2()
flip_table[1437] = flip_b6_d4_e3_f2()
flip_table[1501] = flip_b7_d5_e4_f3()
flip_table[1565] = flip_c7_e5_f4_g3()
flip_table[1629] = flip_d7_f5_g4()
flip_table[1693] = flip_e7_g5()
flip_table[1757] = flip_f7()
flip_table[1821] = flip_g7()
flip_table[2141] = flip_b7()
flip_table[2205] = flip_b6()
flip_table[2269] = flip_b5_d7()
flip_table[2333] = flip_b4_d6_e7()
flip_table[2397] = flip_b3_d5_e6_f7()
flip_table[2461] = flip_b2_d4_e5_f6()
flip_table[2525] = flip_c2_e4_f5_g6()
flip_table[2589] = flip_d2_f4_g5()
flip_table[2653] = flip_e2_g4()
flip_table[2717] = flip_f2()
flip_table[2781] = flip_g2()
flip_table[30] = flip_c1_d1_e1_f1()
flip_table[94] = flip_c2_d2_e2_f2()
flip_table[158] = flip_c3_d3_e3_f3()
flip_table[222] = flip_c4_d4_e4_f4()
flip_table[286] = flip_c5_d5_e5_f5()
flip_table[350] = flip_c6_d6_e6_f6()
flip_table[414] = flip_c7_d7_e7_f7()
flip_table[478] = flip_c8_d8_e8_f8()
flip_table[542] = flip_a3_a4_a5_a6()
flip_table[606] = flip_b3_b4_b5_b6()
flip_table[670] = flip_c3_c4_c5_c6()
flip_table[734] = flip_d3_d4_d5_d6()
flip_table[798] = flip_e3_e4_e5_e6()
flip_table[862] = flip_f3_f4_f5_f6()
flip_table[926] = flip_g3_g4_g5_g6()
flip_table[990] = flip_h3_h4_h5_h6()
flip_table[1246] = flip_c2()
flip_table[1310] = flip_c3_d2()
flip_table[1374] = flip_c4_d3_e2()
flip_table[1438] = flip_c5_d4_e3_f2()
flip_table[1502] = flip_c6_d5_e4_f3()
flip_table[1566] = flip_d6_e5_f4_g3()
flip_table[1630] = flip_e6_f5_g4()
flip_table[1694] = flip_f6_g5()
flip_table[1758] = flip_g6()
flip_table[2206] = flip_c7()
flip_table[2270] = flip_c6_d7()
flip_table[2334] = flip_c5_d6_e7()
flip_table[2398] = flip_c4_d5_e6_f7()
flip_table[2462] = flip_c3_d4_e5_f6()
flip_table[2526] = flip_d3_e4_f5_g6()
flip_table[2590] = flip_e3_f4_g5()
flip_table[2654] = flip_f3_g4()
flip_table[2718] = flip_g3()
flip_table[31] = flip_b1_c1_d1_e1_f1()
flip_table[95] = flip_b2_c2_d2_e2_f2()
flip_table[159] = flip_b3_c3_d3_e3_f3()
flip_table[223] = flip_b4_c4_d4_e4_f4()
flip_table[287] = flip_b5_c5_d5_e5_f5()
flip_table[351] = flip_b6_c6_d6_e6_f6()
flip_table[415] = flip_b7_c7_d7_e7_f7()
flip_table[479] = flip_b8_c8_d8_e8_f8()
flip_table[543] = flip_a2_a3_a4_a5_a6()
flip_table[607] = flip_b2_b3_b4_b5_b6()
flip_table[671] = flip_c2_c3_c4_c5_c6()
flip_table[735] = flip_d2_d3_d4_d5_d6()
flip_table[799] = flip_e2_e3_e4_e5_e6()
flip_table[863] = flip_f2_f3_f4_f5_f6()
flip_table[927] = flip_g2_g3_g4_g5_g6()
flip_table[991] = flip_h2_h3_h4_h5_h6()
flip_table[1183] = flip_b2()
flip_table[1247] = flip_b3_c2()
flip_table[1311] = flip_b4_c3_d2()
flip_table[1375] = flip_b5_c4_d3_e2()
flip_table[1439] = flip_b6_c5_d4_e3_f2()
flip_table[1503] = flip_b7_c6_d5_e4_f3()
flip_table[1567] = flip_c7_d6_e5_f4_g3()
flip_table[1631] = flip_d7_e6_f5_g4()
flip_table[1695] = flip_e7_f6_g5()
flip_table[1759] = flip_f7_g6()
flip_table[1823] = flip_g7()
flip_table[2143] = flip_b7()
flip_table[2207] = flip_b6_c7()
flip_table[2271] = flip_b5_c6_d7()
flip_table[2335] = flip_b4_c5_d6_e7()
flip_table[2399] = flip_b3_c4_d5_e6_f7()
flip_table[2463] = flip_b2_c3_d4_e5_f6()
flip_table[2527] = flip_c2_d3_e4_f5_g6()
flip_table[2591] = flip_d2_e3_f4_g5()
flip_table[2655] = flip_e2_f3_g4()
flip_table[2719] = flip_f2_g3()
flip_table[2783] = flip_g2()
flip_table[32] = flip_b1_c1_d1_e1_f1()
flip_table[96] = flip_b2_c2_d2_e2_f2()
flip_table[160] = flip_b3_c3_d3_e3_f3()
flip_table[224] = flip_b4_c4_d4_e4_f4()
flip_table[288] = flip_b5_c5_d5_e5_f5()
flip_table[352] = flip_b6_c6_d6_e6_f6()
flip_table[416] = flip_b7_c7_d7_e7_f7()
flip_table[480] = flip_b8_c8_d8_e8_f8()
flip_table[544] = flip_a2_a3_a4_a5_a6()
flip_table[608] = flip_b2_b3_b4_b5_b6()
flip_table[672] = flip_c2_c3_c4_c5_c6()
flip_table[736] = flip_d2_d3_d4_d5_d6()
flip_table[800] = flip_e2_e3_e4_e5_e6()
flip_table[864] = flip_f2_f3_f4_f5_f6()
flip_table[928] = flip_g2_g3_g4_g5_g6()
flip_table[992] = flip_h2_h3_h4_h5_h6()
flip_table[1184] = flip_b2()
flip_table[1248] = flip_b3_c2()
flip_table[1312] = flip_b4_c3_d2()
flip_table[1376] = flip_b5_c4_d3_e2()
flip_table[1440] = flip_b6_c5_d4_e3_f2()
flip_table[1504] = flip_b7_c6_d5_e4_f3()
flip_table[1568] = flip_c7_d6_e5_f4_g3()
flip_table[1632] = flip_d7_e6_f5_g4()
flip_table[1696] = flip_e7_f6_g5()
flip_table[1760] = flip_f7_g6()
flip_table[1824] = flip_g7()
flip_table[2144] = flip_b7()
flip_table[2208] = flip_b6_c7()
flip_table[2272] = flip_b5_c6_d7()
flip_table[2336] = flip_b4_c5_d6_e7()
flip_table[2400] = flip_b3_c4_d5_e6_f7()
flip_table[2464] = flip_b2_c3_d4_e5_f6()
flip_table[2528] = flip_c2_d3_e4_f5_g6()
flip_table[2592] = flip_d2_e3_f4_g5()
flip_table[2656] = flip_e2_f3_g4()
flip_table[2720] = flip_f2_g3()
flip_table[2784] = flip_g2()
flip_table[33] = flip_c1_d1_e1_f1()
flip_table[97] = flip_c2_d2_e2_f2()
flip_table[161] = flip_c3_d3_e3_f3()
flip_table[225] = flip_c4_d4_e4_f4()
flip_table[289] = flip_c5_d5_e5_f5()
flip_table[353] = flip_c6_d6_e6_f6()
flip_table[417] = flip_c7_d7_e7_f7()
flip_table[481] = flip_c8_d8_e8_f8()
flip_table[545] = flip_a3_a4_a5_a6()
flip_table[609] = flip_b3_b4_b5_b6()
flip_table[673] = flip_c3_c4_c5_c6()
flip_table[737] = flip_d3_d4_d5_d6()
flip_table[801] = flip_e3_e4_e5_e6()
flip_table[865] = flip_f3_f4_f5_f6()
flip_table[929] = flip_g3_g4_g5_g6()
flip_table[993] = flip_h3_h4_h5_h6()
flip_table[1249] = flip_c2()
flip_table[1313] = flip_c3_d2()
flip_table[1377] = flip_c4_d3_e2()
flip_table[1441] = flip_c5_d4_e3_f2()
flip_table[1505] = flip_c6_d5_e4_f3()
flip_table[1569] = flip_d6_e5_f4_g3()
flip_table[1633] = flip_e6_f5_g4()
flip_table[1697] = flip_f6_g5()
flip_table[1761] = flip_g6()
flip_table[2209] = flip_c7()
flip_table[2273] = flip_c6_d7()
flip_table[2337] = flip_c5_d6_e7()
flip_table[2401] = flip_c4_d5_e6_f7()
flip_table[2465] = flip_c3_d4_e5_f6()
flip_table[2529] = flip_d3_e4_f5_g6()
flip_table[2593] = flip_e3_f4_g5()
flip_table[2657] = flip_f3_g4()
flip_table[2721] = flip_g3()
flip_table[34] = flip_d1_e1_f1()
flip_table[98] = flip_d2_e2_f2()
flip_table[162] = flip_d3_e3_f3()
flip_table[226] = flip_d4_e4_f4()
flip_table[290] = flip_d5_e5_f5()
flip_table[354] = flip_d6_e6_f6()
flip_table[418] = flip_d7_e7_f7()
flip_table[482] = flip_d8_e8_f8()
flip_table[546] = flip_a4_a5_a6()
flip_table[610] = flip_b4_b5_b6()
flip_table[674] = flip_c4_c5_c6()
flip_table[738] = flip_d4_d5_d6()
flip_table[802] = flip_e4_e5_e6()
flip_table[866] = flip_f4_f5_f6()
flip_table[930] = flip_g4_g5_g6()
flip_table[994] = flip_h4_h5_h6()
flip_table[1314] = flip_d2()
flip_table[1378] = flip_d3_e2()
flip_table[1442] = flip_d4_e3_f2()
flip_table[1506] = flip_d5_e4_f3()
flip_table[1570] = flip_e5_f4_g3()
flip_table[1634] = flip_f5_g4()
flip_table[1698] = flip_g5()
flip_table[2274] = flip_d7()
flip_table[2338] = flip_d6_e7()
flip_table[2402] = flip_d5_e6_f7()
flip_table[2466] = flip_d4_e5_f6()
flip_table[2530] = flip_e4_f5_g6()
flip_table[2594] = flip_f4_g5()
flip_table[2658] = flip_g4()
flip_table[35] = flip_e1_f1()
flip_table[99] = flip_e2_f2()
flip_table[163] = flip_e3_f3()
flip_table[227] = flip_e4_f4()
flip_table[291] = flip_e5_f5()
flip_table[355] = flip_e6_f6()
flip_table[419] = flip_e7_f7()
flip_table[483] = flip_e8_f8()
flip_table[547] = flip_a5_a6()
flip_table[611] = flip_b5_b6()
flip_table[675] = flip_c5_c6()
flip_table[739] = flip_d5_d6()
flip_table[803] = flip_e5_e6()
flip_table[867] = flip_f5_f6()
flip_table[931] = flip_g5_g6()
flip_table[995] = flip_h5_h6()
flip_table[1379] = flip_e2()
flip_table[1443] = flip_e3_f2()
flip_table[1507] = flip_e4_f3()
flip_table[1571] = flip_f4_g3()
flip_table[1635] = flip_g4()
flip_table[2339] = flip_e7()
flip_table[2403] = flip_e6_f7()
flip_table[2467] = flip_e5_f6()
flip_table[2531] = flip_f5_g6()
flip_table[2595] = flip_g5()
flip_table[36] = flip_g1()
flip_table[100] = flip_g2()
flip_table[164] = flip_g3()
flip_table[228] = flip_g4()
flip_table[292] = flip_g5()
flip_table[356] = flip_g6()
flip_table[420] = flip_g7()
flip_table[484] = flip_g8()
flip_table[548] = flip_a7()
flip_table[612] = flip_b7()
flip_table[676] = flip_c7()
flip_table[740] = flip_d7()
flip_table[804] = flip_e7()
flip_table[868] = flip_f7()
flip_table[932] = flip_g7()
flip_table[996] = flip_h7()
flip_table[1508] = flip_g2()
flip_table[2468] = flip_g7()
flip_table[37] = flip_e1_g1()
flip_table[101] = flip_e2_g2()
flip_table[165] = flip_e3_g3()
flip_table[229] = flip_e4_g4()
flip_table[293] = flip_e5_g5()
flip_table[357] = flip_e6_g6()
flip_table[421] = flip_e7_g7()
flip_table[485] = flip_e8_g8()
flip_table[549] = flip_a5_a7()
flip_table[613] = flip_b5_b7()
flip_table[677] = flip_c5_c7()
flip_table[741] = flip_d5_d7()
flip_table[805] = flip_e5_e7()
flip_table[869] = flip_f5_f7()
flip_table[933] = flip_g5_g7()
flip_table[997] = flip_h5_h7()
flip_table[1381] = flip_e2()
flip_table[1445] = flip_e3()
flip_table[1509] = flip_e4_g2()
flip_table[1573] = flip_f4()
flip_table[1637] = flip_g4()
flip_table[2341] = flip_e7()
flip_table[2405] = flip_e6()
flip_table[2469] = flip_e5_g7()
flip_table[2533] = flip_f5()
flip_table[2597] = flip_g5()
flip_table[38] = flip_d1_e1_g1()
flip_table[102] = flip_d2_e2_g2()
flip_table[166] = flip_d3_e3_g3()
flip_table[230] = flip_d4_e4_g4()
flip_table[294] = flip_d5_e5_g5()
flip_table[358] = flip_d6_e6_g6()
flip_table[422] = flip_d7_e7_g7()
flip_table[486] = flip_d8_e8_g8()
flip_table[550] = flip_a4_a5_a7()
flip_table[614] = flip_b4_b5_b7()
flip_table[678] = flip_c4_c5_c7()
flip_table[742] = flip_d4_d5_d7()
flip_table[806] = flip_e4_e5_e7()
flip_table[870] = flip_f4_f5_f7()
flip_table[934] = flip_g4_g5_g7()
flip_table[998] = flip_h4_h5_h7()
flip_table[1318] = flip_d2()
flip_table[1382] = flip_d3_e2()
flip_table[1446] = flip_d4_e3()
flip_table[1510] = flip_d5_e4_g2()
flip_table[1574] = flip_e5_f4()
flip_table[1638] = flip_f5_g4()
flip_table[1702] = flip_g5()
flip_table[2278] = flip_d7()
flip_table[2342] = flip_d6_e7()
flip_table[2406] = flip_d5_e6()
flip_table[2470] = flip_d4_e5_g7()
flip_table[2534] = flip_e4_f5()
flip_table[2598] = flip_f4_g5()
flip_table[2662] = flip_g4()
flip_table[39] = flip_c1_d1_e1_g1()
flip_table[103] = flip_c2_d2_e2_g2()
flip_table[167] = flip_c3_d3_e3_g3()
flip_table[231] = flip_c4_d4_e4_g4()
flip_table[295] = flip_c5_d5_e5_g5()
flip_table[359] = flip_c6_d6_e6_g6()
flip_table[423] = flip_c7_d7_e7_g7()
flip_table[487] = flip_c8_d8_e8_g8()
flip_table[551] = flip_a3_a4_a5_a7()
flip_table[615] = flip_b3_b4_b5_b7()
flip_table[679] = flip_c3_c4_c5_c7()
flip_table[743] = flip_d3_d4_d5_d7()
flip_table[807] = flip_e3_e4_e5_e7()
flip_table[871] = flip_f3_f4_f5_f7()
flip_table[935] = flip_g3_g4_g5_g7()
flip_table[999] = flip_h3_h4_h5_h7()
flip_table[1255] = flip_c2()
flip_table[1319] = flip_c3_d2()
flip_table[1383] = flip_c4_d3_e2()
flip_table[1447] = flip_c5_d4_e3()
flip_table[1511] = flip_c6_d5_e4_g2()
flip_table[1575] = flip_d6_e5_f4()
flip_table[1639] = flip_e6_f5_g4()
flip_table[1703] = flip_f6_g5()
flip_table[1767] = flip_g6()
flip_table[2215] = flip_c7()
flip_table[2279] = flip_c6_d7()
flip_table[2343] = flip_c5_d6_e7()
flip_table[2407] = flip_c4_d5_e6()
flip_table[2471] = flip_c3_d4_e5_g7()
flip_table[2535] = flip_d3_e4_f5()
flip_table[2599] = flip_e3_f4_g5()
flip_table[2663] = flip_f3_g4()
flip_table[2727] = flip_g3()
flip_table[40] = flip_b1_c1_d1_e1_g1()
flip_table[104] = flip_b2_c2_d2_e2_g2()
flip_table[168] = flip_b3_c3_d3_e3_g3()
flip_table[232] = flip_b4_c4_d4_e4_g4()
flip_table[296] = flip_b5_c5_d5_e5_g5()
flip_table[360] = flip_b6_c6_d6_e6_g6()
flip_table[424] = flip_b7_c7_d7_e7_g7()
flip_table[488] = flip_b8_c8_d8_e8_g8()
flip_table[552] = flip_a2_a3_a4_a5_a7()
flip_table[616] = flip_b2_b3_b4_b5_b7()
flip_table[680] = flip_c2_c3_c4_c5_c7()
flip_table[744] = flip_d2_d3_d4_d5_d7()
flip_table[808] = flip_e2_e3_e4_e5_e7()
flip_table[872] = flip_f2_f3_f4_f5_f7()
flip_table[936] = flip_g2_g3_g4_g5_g7()
flip_table[1000] = flip_h2_h3_h4_h5_h7()
flip_table[1192] = flip_b2()
flip_table[1256] = flip_b3_c2()
flip_table[1320] = flip_b4_c3_d2()
flip_table[1384] = flip_b5_c4_d3_e2()
flip_table[1448] = flip_b6_c5_d4_e3()
flip_table[1512] = flip_b7_c6_d5_e4_g2()
flip_table[1576] = flip_c7_d6_e5_f4()
flip_table[1640] = flip_d7_e6_f5_g4()
flip_table[1704] = flip_e7_f6_g5()
flip_table[1768] = flip_f7_g6()
flip_table[1832] = flip_g7()
flip_table[2152] = flip_b7()
flip_table[2216] = flip_b6_c7()
flip_table[2280] = flip_b5_c6_d7()
flip_table[2344] = flip_b4_c5_d6_e7()
flip_table[2408] = flip_b3_c4_d5_e6()
flip_table[2472] = flip_b2_c3_d4_e5_g7()
flip_table[2536] = flip_c2_d3_e4_f5()
flip_table[2600] = flip_d2_e3_f4_g5()
flip_table[2664] = flip_e2_f3_g4()
flip_table[2728] = flip_f2_g3()
flip_table[2792] = flip_g2()
flip_table[41] = flip_f1_g1()
flip_table[105] = flip_f2_g2()
flip_table[169] = flip_f3_g3()
flip_table[233] = flip_f4_g4()
flip_table[297] = flip_f5_g5()
flip_table[361] = flip_f6_g6()
flip_table[425] = flip_f7_g7()
flip_table[489] = flip_f8_g8()
flip_table[553] = flip_a6_a7()
flip_table[617] = flip_b6_b7()
flip_table[681] = flip_c6_c7()
flip_table[745] = flip_d6_d7()
flip_table[809] = flip_e6_e7()
flip_table[873] = flip_f6_f7()
flip_table[937] = flip_g6_g7()
flip_table[1001] = flip_h6_h7()
flip_table[1449] = flip_f2()
flip_table[1513] = flip_f3_g2()
flip_table[1577] = flip_g3()
flip_table[2409] = flip_f7()
flip_table[2473] = flip_f6_g7()
flip_table[2537] = flip_g6()
flip_table[42] = flip_d1_f1_g1()
flip_table[106] = flip_d2_f2_g2()
flip_table[170] = flip_d3_f3_g3()
flip_table[234] = flip_d4_f4_g4()
flip_table[298] = flip_d5_f5_g5()
flip_table[362] = flip_d6_f6_g6()
flip_table[426] = flip_d7_f7_g7()
flip_table[490] = flip_d8_f8_g8()
flip_table[554] = flip_a4_a6_a7()
flip_table[618] = flip_b4_b6_b7()
flip_table[682] = flip_c4_c6_c7()
flip_table[746] = flip_d4_d6_d7()
flip_table[810] = flip_e4_e6_e7()
flip_table[874] = flip_f4_f6_f7()
flip_table[938] = flip_g4_g6_g7()
flip_table[1002] = flip_h4_h6_h7()
flip_table[1322] = flip_d2()
flip_table[1386] = flip_d3()
flip_table[1450] = flip_d4_f2()
flip_table[1514] = flip_d5_f3_g2()
flip_table[1578] = flip_e5_g3()
flip_table[1642] = flip_f5()
flip_table[1706] = flip_g5()
flip_table[2282] = flip_d7()
flip_table[2346] = flip_d6()
flip_table[2410] = flip_d5_f7()
flip_table[2474] = flip_d4_f6_g7()
flip_table[2538] = flip_e4_g6()
flip_table[2602] = flip_f4()
flip_table[2666] = flip_g4()
flip_table[43] = flip_c1_d1_f1_g1()
flip_table[107] = flip_c2_d2_f2_g2()
flip_table[171] = flip_c3_d3_f3_g3()
flip_table[235] = flip_c4_d4_f4_g4()
flip_table[299] = flip_c5_d5_f5_g5()
flip_table[363] = flip_c6_d6_f6_g6()
flip_table[427] = flip_c7_d7_f7_g7()
flip_table[491] = flip_c8_d8_f8_g8()
flip_table[555] = flip_a3_a4_a6_a7()
flip_table[619] = flip_b3_b4_b6_b7()
flip_table[683] = flip_c3_c4_c6_c7()
flip_table[747] = flip_d3_d4_d6_d7()
flip_table[811] = flip_e3_e4_e6_e7()
flip_table[875] = flip_f3_f4_f6_f7()
flip_table[939] = flip_g3_g4_g6_g7()
flip_table[1003] = flip_h3_h4_h6_h7()
flip_table[1259] = flip_c2()
flip_table[1323] = flip_c3_d2()
flip_table[1387] = flip_c4_d3()
flip_table[1451] = flip_c5_d4_f2()
flip_table[1515] = flip_c6_d5_f3_g2()
flip_table[1579] = flip_d6_e5_g3()
flip_table[1643] = flip_e6_f5()
flip_table[1707] = flip_f6_g5()
flip_table[1771] = flip_g6()
flip_table[2219] = flip_c7()
flip_table[2283] = flip_c6_d7()
flip_table[2347] = flip_c5_d6()
flip_table[2411] = flip_c4_d5_f7()
flip_table[2475] = flip_c3_d4_f6_g7()
flip_table[2539] = flip_d3_e4_g6()
flip_table[2603] = flip_e3_f4()
flip_table[2667] = flip_f3_g4()
flip_table[2731] = flip_g3()
flip_table[44] = flip_b1_c1_d1_f1_g1()
flip_table[108] = flip_b2_c2_d2_f2_g2()
flip_table[172] = flip_b3_c3_d3_f3_g3()
flip_table[236] = flip_b4_c4_d4_f4_g4()
flip_table[300] = flip_b5_c5_d5_f5_g5()
flip_table[364] = flip_b6_c6_d6_f6_g6()
flip_table[428] = flip_b7_c7_d7_f7_g7()
flip_table[492] = flip_b8_c8_d8_f8_g8()
flip_table[556] = flip_a2_a3_a4_a6_a7()
flip_table[620] = flip_b2_b3_b4_b6_b7()
flip_table[684] = flip_c2_c3_c4_c6_c7()
flip_table[748] = flip_d2_d3_d4_d6_d7()
flip_table[812] = flip_e2_e3_e4_e6_e7()
flip_table[876] = flip_f2_f3_f4_f6_f7()
flip_table[940] = flip_g2_g3_g4_g6_g7()
flip_table[1004] = flip_h2_h3_h4_h6_h7()
flip_table[1196] = flip_b2()
flip_table[1260] = flip_b3_c2()
flip_table[1324] = flip_b4_c3_d2()
flip_table[1388] = flip_b5_c4_d3()
flip_table[1452] = flip_b6_c5_d4_f2()
flip_table[1516] = flip_b7_c6_d5_f3_g2()
flip_table[1580] = flip_c7_d6_e5_g3()
flip_table[1644] = flip_d7_e6_f5()
flip_table[1708] = flip_e7_f6_g5()
flip_table[1772] = flip_f7_g6()
flip_table[1836] = flip_g7()
flip_table[2156] = flip_b7()
flip_table[2220] = flip_b6_c7()
flip_table[2284] = flip_b5_c6_d7()
flip_table[2348] = flip_b4_c5_d6()
flip_table[2412] = flip_b3_c4_d5_f7()
flip_table[2476] = flip_b2_c3_d4_f6_g7()
flip_table[2540] = flip_c2_d3_e4_g6()
flip_table[2604] = flip_d2_e3_f4()
flip_table[2668] = flip_e2_f3_g4()
flip_table[2732] = flip_f2_g3()
flip_table[2796] = flip_g2()
flip_table[45] = flip_e1_f1_g1()
flip_table[109] = flip_e2_f2_g2()
flip_table[173] = flip_e3_f3_g3()
flip_table[237] = flip_e4_f4_g4()
flip_table[301] = flip_e5_f5_g5()
flip_table[365] = flip_e6_f6_g6()
flip_table[429] = flip_e7_f7_g7()
flip_table[493] = flip_e8_f8_g8()
flip_table[557] = flip_a5_a6_a7()
flip_table[621] = flip_b5_b6_b7()
flip_table[685] = flip_c5_c6_c7()
flip_table[749] = flip_d5_d6_d7()
flip_table[813] = flip_e5_e6_e7()
flip_table[877] = flip_f5_f6_f7()
flip_table[941] = flip_g5_g6_g7()
flip_table[1005] = flip_h5_h6_h7()
flip_table[1389] = flip_e2()
flip_table[1453] = flip_e3_f2()
flip_table[1517] = flip_e4_f3_g2()
flip_table[1581] = flip_f4_g3()
flip_table[1645] = flip_g4()
flip_table[2349] = flip_e7()
flip_table[2413] = flip_e6_f7()
flip_table[2477] = flip_e5_f6_g7()
flip_table[2541] = flip_f5_g6()
flip_table[2605] = flip_g5()
flip_table[46] = flip_c1_e1_f1_g1()
flip_table[110] = flip_c2_e2_f2_g2()
flip_table[174] = flip_c3_e3_f3_g3()
flip_table[238] = flip_c4_e4_f4_g4()
flip_table[302] = flip_c5_e5_f5_g5()
flip_table[366] = flip_c6_e6_f6_g6()
flip_table[430] = flip_c7_e7_f7_g7()
flip_table[494] = flip_c8_e8_f8_g8()
flip_table[558] = flip_a3_a5_a6_a7()
flip_table[622] = flip_b3_b5_b6_b7()
flip_table[686] = flip_c3_c5_c6_c7()
flip_table[750] = flip_d3_d5_d6_d7()
flip_table[814] = flip_e3_e5_e6_e7()
flip_table[878] = flip_f3_f5_f6_f7()
flip_table[942] = flip_g3_g5_g6_g7()
flip_table[1006] = flip_h3_h5_h6_h7()
flip_table[1262] = flip_c2()
flip_table[1326] = flip_c3()
flip_table[1390] = flip_c4_e2()
flip_table[1454] = flip_c5_e3_f2()
flip_table[1518] = flip_c6_e4_f3_g2()
flip_table[1582] = flip_d6_f4_g3()
flip_table[1646] = flip_e6_g4()
flip_table[1710] = flip_f6()
flip_table[1774] = flip_g6()
flip_table[2222] = flip_c7()
flip_table[2286] = flip_c6()
flip_table[2350] = flip_c5_e7()
flip_table[2414] = flip_c4_e6_f7()
flip_table[2478] = flip_c3_e5_f6_g7()
flip_table[2542] = flip_d3_f5_g6()
flip_table[2606] = flip_e3_g5()
flip_table[2670] = flip_f3()
flip_table[2734] = flip_g3()
flip_table[47] = flip_b1_c1_e1_f1_g1()
flip_table[111] = flip_b2_c2_e2_f2_g2()
flip_table[175] = flip_b3_c3_e3_f3_g3()
flip_table[239] = flip_b4_c4_e4_f4_g4()
flip_table[303] = flip_b5_c5_e5_f5_g5()
flip_table[367] = flip_b6_c6_e6_f6_g6()
flip_table[431] = flip_b7_c7_e7_f7_g7()
flip_table[495] = flip_b8_c8_e8_f8_g8()
flip_table[559] = flip_a2_a3_a5_a6_a7()
flip_table[623] = flip_b2_b3_b5_b6_b7()
flip_table[687] = flip_c2_c3_c5_c6_c7()
flip_table[751] = flip_d2_d3_d5_d6_d7()
flip_table[815] = flip_e2_e3_e5_e6_e7()
flip_table[879] = flip_f2_f3_f5_f6_f7()
flip_table[943] = flip_g2_g3_g5_g6_g7()
flip_table[1007] = flip_h2_h3_h5_h6_h7()
flip_table[1199] = flip_b2()
flip_table[1263] = flip_b3_c2()
flip_table[1327] = flip_b4_c3()
flip_table[1391] = flip_b5_c4_e2()
flip_table[1455] = flip_b6_c5_e3_f2()
flip_table[1519] = flip_b7_c6_e4_f3_g2()
flip_table[1583] = flip_c7_d6_f4_g3()
flip_table[1647] = flip_d7_e6_g4()
flip_table[1711] = flip_e7_f6()
flip_table[1775] = flip_f7_g6()
flip_table[1839] = flip_g7()
flip_table[2159] = flip_b7()
flip_table[2223] = flip_b6_c7()
flip_table[2287] = flip_b5_c6()
flip_table[2351] = flip_b4_c5_e7()
flip_table[2415] = flip_b3_c4_e6_f7()
flip_table[2479] = flip_b2_c3_e5_f6_g7()
flip_table[2543] = flip_c2_d3_f5_g6()
flip_table[2607] = flip_d2_e3_g5()
flip_table[2671] = flip_e2_f3()
flip_table[2735] = flip_f2_g3()
flip_table[2799] = flip_g2()
flip_table[48] = flip_d1_e1_f1_g1()
flip_table[112] = flip_d2_e2_f2_g2()
flip_table[176] = flip_d3_e3_f3_g3()
flip_table[240] = flip_d4_e4_f4_g4()
flip_table[304] = flip_d5_e5_f5_g5()
flip_table[368] = flip_d6_e6_f6_g6()
flip_table[432] = flip_d7_e7_f7_g7()
flip_table[496] = flip_d8_e8_f8_g8()
flip_table[560] = flip_a4_a5_a6_a7()
flip_table[624] = flip_b4_b5_b6_b7()
flip_table[688] = flip_c4_c5_c6_c7()
flip_table[752] = flip_d4_d5_d6_d7()
flip_table[816] = flip_e4_e5_e6_e7()
flip_table[880] = flip_f4_f5_f6_f7()
flip_table[944] = flip_g4_g5_g6_g7()
flip_table[1008] = flip_h4_h5_h6_h7()
flip_table[1328] = flip_d2()
flip_table[1392] = flip_d3_e2()
flip_table[1456] = flip_d4_e3_f2()
flip_table[1520] = flip_d5_e4_f3_g2()
flip_table[1584] = flip_e5_f4_g3()
flip_table[1648] = flip_f5_g4()
flip_table[1712] = flip_g5()
flip_table[2288] = flip_d7()
flip_table[2352] = flip_d6_e7()
flip_table[2416] = flip_d5_e6_f7()
flip_table[2480] = flip_d4_e5_f6_g7()
flip_table[2544] = flip_e4_f5_g6()
flip_table[2608] = flip_f4_g5()
flip_table[2672] = flip_g4()
flip_table[49] = flip_b1_d1_e1_f1_g1()
flip_table[113] = flip_b2_d2_e2_f2_g2()
flip_table[177] = flip_b3_d3_e3_f3_g3()
flip_table[241] = flip_b4_d4_e4_f4_g4()
flip_table[305] = flip_b5_d5_e5_f5_g5()
flip_table[369] = flip_b6_d6_e6_f6_g6()
flip_table[433] = flip_b7_d7_e7_f7_g7()
flip_table[497] = flip_b8_d8_e8_f8_g8()
flip_table[561] = flip_a2_a4_a5_a6_a7()
flip_table[625] = flip_b2_b4_b5_b6_b7()
flip_table[689] = flip_c2_c4_c5_c6_c7()
flip_table[753] = flip_d2_d4_d5_d6_d7()
flip_table[817] = flip_e2_e4_e5_e6_e7()
flip_table[881] = flip_f2_f4_f5_f6_f7()
flip_table[945] = flip_g2_g4_g5_g6_g7()
flip_table[1009] = flip_h2_h4_h5_h6_h7()
flip_table[1201] = flip_b2()
flip_table[1265] = flip_b3()
flip_table[1329] = flip_b4_d2()
flip_table[1393] = flip_b5_d3_e2()
flip_table[1457] = flip_b6_d4_e3_f2()
flip_table[1521] = flip_b7_d5_e4_f3_g2()
flip_table[1585] = flip_c7_e5_f4_g3()
flip_table[1649] = flip_d7_f5_g4()
flip_table[1713] = flip_e7_g5()
flip_table[1777] = flip_f7()
flip_table[1841] = flip_g7()
flip_table[2161] = flip_b7()
flip_table[2225] = flip_b6()
flip_table[2289] = flip_b5_d7()
flip_table[2353] = flip_b4_d6_e7()
flip_table[2417] = flip_b3_d5_e6_f7()
flip_table[2481] = flip_b2_d4_e5_f6_g7()
flip_table[2545] = flip_c2_e4_f5_g6()
flip_table[2609] = flip_d2_f4_g5()
flip_table[2673] = flip_e2_g4()
flip_table[2737] = flip_f2()
flip_table[2801] = flip_g2()
flip_table[50] = flip_c1_d1_e1_f1_g1()
flip_table[114] = flip_c2_d2_e2_f2_g2()
flip_table[178] = flip_c3_d3_e3_f3_g3()
flip_table[242] = flip_c4_d4_e4_f4_g4()
flip_table[306] = flip_c5_d5_e5_f5_g5()
flip_table[370] = flip_c6_d6_e6_f6_g6()
flip_table[434] = flip_c7_d7_e7_f7_g7()
flip_table[498] = flip_c8_d8_e8_f8_g8()
flip_table[562] = flip_a3_a4_a5_a6_a7()
flip_table[626] = flip_b3_b4_b5_b6_b7()
flip_table[690] = flip_c3_c4_c5_c6_c7()
flip_table[754] = flip_d3_d4_d5_d6_d7()
flip_table[818] = flip_e3_e4_e5_e6_e7()
flip_table[882] = flip_f3_f4_f5_f6_f7()
flip_table[946] = flip_g3_g4_g5_g6_g7()
flip_table[1010] = flip_h3_h4_h5_h6_h7()
flip_table[1266] = flip_c2()
flip_table[1330] = flip_c3_d2()
flip_table[1394] = flip_c4_d3_e2()
flip_table[1458] = flip_c5_d4_e3_f2()
flip_table[1522] = flip_c6_d5_e4_f3_g2()
flip_table[1586] = flip_d6_e5_f4_g3()
flip_table[1650] = flip_e6_f5_g4()
flip_table[1714] = flip_f6_g5()
flip_table[1778] = flip_g6()
flip_table[2226] = flip_c7()
flip_table[2290] = flip_c6_d7()
flip_table[2354] = flip_c5_d6_e7()
flip_table[2418] = flip_c4_d5_e6_f7()
flip_table[2482] = flip_c3_d4_e5_f6_g7()
flip_table[2546] = flip_d3_e4_f5_g6()
flip_table[2610] = flip_e3_f4_g5()
flip_table[2674] = flip_f3_g4()
flip_table[2738] = flip_g3()
flip_table[51] = flip_b1_c1_d1_e1_f1_g1()
flip_table[115] = flip_b2_c2_d2_e2_f2_g2()
flip_table[179] = flip_b3_c3_d3_e3_f3_g3()
flip_table[243] = flip_b4_c4_d4_e4_f4_g4()
flip_table[307] = flip_b5_c5_d5_e5_f5_g5()
flip_table[371] = flip_b6_c6_d6_e6_f6_g6()
flip_table[435] = flip_b7_c7_d7_e7_f7_g7()
flip_table[499] = flip_b8_c8_d8_e8_f8_g8()
flip_table[563] = flip_a2_a3_a4_a5_a6_a7()
flip_table[627] = flip_b2_b3_b4_b5_b6_b7()
flip_table[691] = flip_c2_c3_c4_c5_c6_c7()
flip_table[755] = flip_d2_d3_d4_d5_d6_d7()
flip_table[819] = flip_e2_e3_e4_e5_e6_e7()
flip_table[883] = flip_f2_f3_f4_f5_f6_f7()
flip_table[947] = flip_g2_g3_g4_g5_g6_g7()
flip_table[1011] = flip_h2_h3_h4_h5_h6_h7()
flip_table[1203] = flip_b2()
flip_table[1267] = flip_b3_c2()
flip_table[1331] = flip_b4_c3_d2()
flip_table[1395] = flip_b5_c4_d3_e2()
flip_table[1459] = flip_b6_c5_d4_e3_f2()
flip_table[1523] = flip_b7_c6_d5_e4_f3_g2()
flip_table[1587] = flip_c7_d6_e5_f4_g3()
flip_table[1651] = flip_d7_e6_f5_g4()
flip_table[1715] = flip_e7_f6_g5()
flip_table[1779] = flip_f7_g6()
flip_table[1843] = flip_g7()
flip_table[2163] = flip_b7()
flip_table[2227] = flip_b6_c7()
flip_table[2291] = flip_b5_c6_d7()
flip_table[2355] = flip_b4_c5_d6_e7()
flip_table[2419] = flip_b3_c4_d5_e6_f7()
flip_table[2483] = flip_b2_c3_d4_e5_f6_g7()
flip_table[2547] = flip_c2_d3_e4_f5_g6()
flip_table[2611] = flip_d2_e3_f4_g5()
flip_table[2675] = flip_e2_f3_g4()
flip_table[2739] = flip_f2_g3()
flip_table[2803] = flip_g2()
flip_table[52] = flip_b1_c1_d1_e1_f1_g1()
flip_table[116] = flip_b2_c2_d2_e2_f2_g2()
flip_table[180] = flip_b3_c3_d3_e3_f3_g3()
flip_table[244] = flip_b4_c4_d4_e4_f4_g4()
flip_table[308] = flip_b5_c5_d5_e5_f5_g5()
flip_table[372] = flip_b6_c6_d6_e6_f6_g6()
flip_table[436] = flip_b7_c7_d7_e7_f7_g7()
flip_table[500] = flip_b8_c8_d8_e8_f8_g8()
flip_table[564] = flip_a2_a3_a4_a5_a6_a7()
flip_table[628] = flip_b2_b3_b4_b5_b6_b7()
flip_table[692] = flip_c2_c3_c4_c5_c6_c7()
flip_table[756] = flip_d2_d3_d4_d5_d6_d7()
flip_table[820] = flip_e2_e3_e4_e5_e6_e7()
flip_table[884] = flip_f2_f3_f4_f5_f6_f7()
flip_table[948] = flip_g2_g3_g4_g5_g6_g7()
flip_table[1012] = flip_h2_h3_h4_h5_h6_h7()
flip_table[1204] = flip_b2()
flip_table[1268] = flip_b3_c2()
flip_table[1332] = flip_b4_c3_d2()
flip_table[1396] = flip_b5_c4_d3_e2()
flip_table[1460] = flip_b6_c5_d4_e3_f2()
flip_table[1524] = flip_b7_c6_d5_e4_f3_g2()
flip_table[1588] = flip_c7_d6_e5_f4_g3()
flip_table[1652] = flip_d7_e6_f5_g4()
flip_table[1716] = flip_e7_f6_g5()
flip_table[1780] = flip_f7_g6()
flip_table[1844] = flip_g7()
flip_table[2164] = flip_b7()
flip_table[2228] = flip_b6_c7()
flip_table[2292] = flip_b5_c6_d7()
flip_table[2356] = flip_b4_c5_d6_e7()
flip_table[2420] = flip_b3_c4_d5_e6_f7()
flip_table[2484] = flip_b2_c3_d4_e5_f6_g7()
flip_table[2548] = flip_c2_d3_e4_f5_g6()
flip_table[2612] = flip_d2_e3_f4_g5()
flip_table[2676] = flip_e2_f3_g4()
flip_table[2740] = flip_f2_g3()
flip_table[2804] = flip_g2()
flip_table[53] = flip_c1_d1_e1_f1_g1()
flip_table[117] = flip_c2_d2_e2_f2_g2()
flip_table[181] = flip_c3_d3_e3_f3_g3()
flip_table[245] = flip_c4_d4_e4_f4_g4()
flip_table[309] = flip_c5_d5_e5_f5_g5()
flip_table[373] = flip_c6_d6_e6_f6_g6()
flip_table[437] = flip_c7_d7_e7_f7_g7()
flip_table[501] = flip_c8_d8_e8_f8_g8()
flip_table[565] = flip_a3_a4_a5_a6_a7()
flip_table[629] = flip_b3_b4_b5_b6_b7()
flip_table[693] = flip_c3_c4_c5_c6_c7()
flip_table[757] = flip_d3_d4_d5_d6_d7()
flip_table[821] = flip_e3_e4_e5_e6_e7()
flip_table[885] = flip_f3_f4_f5_f6_f7()
flip_table[949] = flip_g3_g4_g5_g6_g7()
flip_table[1013] = flip_h3_h4_h5_h6_h7()
flip_table[1269] = flip_c2()
flip_table[1333] = flip_c3_d2()
flip_table[1397] = flip_c4_d3_e2()
flip_table[1461] = flip_c5_d4_e3_f2()
flip_table[1525] = flip_c6_d5_e4_f3_g2()
flip_table[1589] = flip_d6_e5_f4_g3()
flip_table[1653] = flip_e6_f5_g4()
flip_table[1717] = flip_f6_g5()
flip_table[1781] = flip_g6()
flip_table[2229] = flip_c7()
flip_table[2293] = flip_c6_d7()
flip_table[2357] = flip_c5_d6_e7()
flip_table[2421] = flip_c4_d5_e6_f7()
flip_table[2485] = flip_c3_d4_e5_f6_g7()
flip_table[2549] = flip_d3_e4_f5_g6()
flip_table[2613] = flip_e3_f4_g5()
flip_table[2677] = flip_f3_g4()
flip_table[2741] = flip_g3()
flip_table[54] = flip_d1_e1_f1_g1()
flip_table[118] = flip_d2_e2_f2_g2()
flip_table[182] = flip_d3_e3_f3_g3()
flip_table[246] = flip_d4_e4_f4_g4()
flip_table[310] = flip_d5_e5_f5_g5()
flip_table[374] = flip_d6_e6_f6_g6()
flip_table[438] = flip_d7_e7_f7_g7()
flip_table[502] = flip_d8_e8_f8_g8()
flip_table[566] = flip_a4_a5_a6_a7()
flip_table[630] = flip_b4_b5_b6_b7()
flip_table[694] = flip_c4_c5_c6_c7()
flip_table[758] = flip_d4_d5_d6_d7()
flip_table[822] = flip_e4_e5_e6_e7()
flip_table[886] = flip_f4_f5_f6_f7()
flip_table[950] = flip_g4_g5_g6_g7()
flip_table[1014] = flip_h4_h5_h6_h7()
flip_table[1334] = flip_d2()
flip_table[1398] = flip_d3_e2()
flip_table[1462] = flip_d4_e3_f2()
flip_table[1526] = flip_d5_e4_f3_g2()
flip_table[1590] = flip_e5_f4_g3()
flip_table[1654] = flip_f5_g4()
flip_table[1718] = flip_g5()
flip_table[2294] = flip_d7()
flip_table[2358] = flip_d6_e7()
flip_table[2422] = flip_d5_e6_f7()
flip_table[2486] = flip_d4_e5_f6_g7()
flip_table[2550] = flip_e4_f5_g6()
flip_table[2614] = flip_f4_g5()
flip_table[2678] = flip_g4()
flip_table[55] = flip_e1_f1_g1()
flip_table[119] = flip_e2_f2_g2()
flip_table[183] = flip_e3_f3_g3()
flip_table[247] = flip_e4_f4_g4()
flip_table[311] = flip_e5_f5_g5()
flip_table[375] = flip_e6_f6_g6()
flip_table[439] = flip_e7_f7_g7()
flip_table[503] = flip_e8_f8_g8()
flip_table[567] = flip_a5_a6_a7()
flip_table[631] = flip_b5_b6_b7()
flip_table[695] = flip_c5_c6_c7()
flip_table[759] = flip_d5_d6_d7()
flip_table[823] = flip_e5_e6_e7()
flip_table[887] = flip_f5_f6_f7()
flip_table[951] = flip_g5_g6_g7()
flip_table[1015] = flip_h5_h6_h7()
flip_table[1399] = flip_e2()
flip_table[1463] = flip_e3_f2()
flip_table[1527] = flip_e4_f3_g2()
flip_table[1591] = flip_f4_g3()
flip_table[1655] = flip_g4()
flip_table[2359] = flip_e7()
flip_table[2423] = flip_e6_f7()
flip_table[2487] = flip_e5_f6_g7()
flip_table[2551] = flip_f5_g6()
flip_table[2615] = flip_g5()
flip_table[56] = flip_f1_g1()
flip_table[120] = flip_f2_g2()
flip_table[184] = flip_f3_g3()
flip_table[248] = flip_f4_g4()
flip_table[312] = flip_f5_g5()
flip_table[376] = flip_f6_g6()
flip_table[440] = flip_f7_g7()
flip_table[504] = flip_f8_g8()
flip_table[568] = flip_a6_a7()
flip_table[632] = flip_b6_b7()
flip_table[696] = flip_c6_c7()
flip_table[760] = flip_d6_d7()
flip_table[824] = flip_e6_e7()
flip_table[888] = flip_f6_f7()
flip_table[952] = flip_g6_g7()
flip_table[1016] = flip_h6_h7()
flip_table[1464] = flip_f2()
flip_table[1528] = flip_f3_g2()
flip_table[1592] = flip_g3()
flip_table[2424] = flip_f7()
flip_table[2488] = flip_f6_g7()
flip_table[2552] = flip_g6()


if __name__ == '__main__':
    # italian line
    italian = 'F5D6C4D3E6F4E3F3C6F6G5G6E7F7C3G4D2C5H3H4E2F2G3C1C2E1D1B3F1G1F8D7C7G7A3B4B6B1H8B5A6A5A4B7A8G8H7H6H5G2H1H2A1D8E8C8B2A2B8A7'
    human_moves = [italian[i*2:(i+1)*2] for i in range(len(italian)//2)]
    moves = ['ABCDEFGH'.index(h[0]) + 8 * (int(h[1])-1) for h in human_moves]

    # setup initial board state
    t0 = time.time()

    p_d5 = put_d5()
    p_e4 = put_e4()
    p_d4 = put_d4()
    p_e5 = put_e5()

    for x in range(10**5):
        init_state()

        turn = BLACK
        p_d5.go()
        p_e4.go()
        turn = WHITE
        p_d4.go()
        p_e5.go()
        turn = BLACK

        for mv in moves:
            move_table[mv].go()
            turn = -turn

    t = 60 * 10**5 // (time.time()-t0)

    check_board()

    nx = sum(str_state(states()[l]).count('2') for l in range(8))
    no = sum(str_state(states()[l]).count('0') for l in range(8))

    print(f'{nx}-{no}')
    print()

    print('moves/sec: %d' % t)
