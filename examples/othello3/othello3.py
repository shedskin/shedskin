import collections
import time

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

# initial state (base-3 number, 0..3**8-1. digit value 0, 1, 2 -> white, empty, black)
state = [3280 for line in lines]

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
                    board[j][i] = {'1': '.', '0': 'o', '2': 'x'}[str_state(state[l])[idx]]
    return '\n'.join([''.join(row) for row in board])


def calc_pos(l, j):
    line = lines[l]
    return (line.start[0]+j*line.dx, line.start[1]+j*line.dy)


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
    return flips


# for each line state, idx and turn, determine flipped discs
flippers_x = {}
flippers_o = {}
for s in range(3**8):
    for idx in range(8):
        flippers_x[s, idx] = state_flips(s, idx, '2')
        flippers_o[s, idx] = state_flips(s, idx, '0')


def check_board():  # TODO remove
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
                print(f"        state[{l}] += turn * {3**idx}")
            print()

    print('move_table = [')
    for name in move_funcs:
        print(f'   {name}(),')
    print(']')
    print()

    # 830 flip patterns (831 including noop)
    patterns = set([tuple(v) for v in flippers_x.values()])
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
        for pos in flipfunc:
            line_idcs = collections.defaultdict(list)
            for (l, idx) in topology[pos]:
                line_idcs[l].append(idx)
            for (l, idcs) in line_idcs.items():
                value = sum(3**idx for idx in idcs)
                print(f"        state[{l}] += 2 * turn * {value}")
            print()

#gen_funcs()
#stop

class Put:
    pass

class Flip:
    pass

class put_a1(Put):
    def go(self):
        state[0] += turn * 1
        state[8] += turn * 1
        state[16] += turn * 1
        state[38] += turn * 1

class put_b1(Put):
    def go(self):
        state[0] += turn * 3
        state[9] += turn * 1
        state[17] += turn * 3
        state[39] += turn * 1

class put_c1(Put):
    def go(self):
        state[0] += turn * 9
        state[10] += turn * 1
        state[18] += turn * 9
        state[40] += turn * 1

class put_d1(Put):
    def go(self):
        state[0] += turn * 27
        state[11] += turn * 1
        state[19] += turn * 27
        state[41] += turn * 1

class put_e1(Put):
    def go(self):
        state[0] += turn * 81
        state[12] += turn * 1
        state[20] += turn * 81
        state[42] += turn * 1

class put_f1(Put):
    def go(self):
        state[0] += turn * 243
        state[13] += turn * 1
        state[21] += turn * 243
        state[43] += turn * 1

class put_g1(Put):
    def go(self):
        state[0] += turn * 729
        state[14] += turn * 1
        state[22] += turn * 729
        state[44] += turn * 1

class put_h1(Put):
    def go(self):
        state[0] += turn * 2187
        state[15] += turn * 1
        state[23] += turn * 2187
        state[45] += turn * 1

class put_a2(Put):
    def go(self):
        state[1] += turn * 1
        state[8] += turn * 3
        state[17] += turn * 1
        state[37] += turn * 1

class put_b2(Put):
    def go(self):
        state[1] += turn * 3
        state[9] += turn * 3
        state[18] += turn * 3
        state[38] += turn * 3

class put_c2(Put):
    def go(self):
        state[1] += turn * 9
        state[10] += turn * 3
        state[19] += turn * 9
        state[39] += turn * 3

class put_d2(Put):
    def go(self):
        state[1] += turn * 27
        state[11] += turn * 3
        state[20] += turn * 27
        state[40] += turn * 3

class put_e2(Put):
    def go(self):
        state[1] += turn * 81
        state[12] += turn * 3
        state[21] += turn * 81
        state[41] += turn * 3

class put_f2(Put):
    def go(self):
        state[1] += turn * 243
        state[13] += turn * 3
        state[22] += turn * 243
        state[42] += turn * 3

class put_g2(Put):
    def go(self):
        state[1] += turn * 729
        state[14] += turn * 3
        state[23] += turn * 729
        state[43] += turn * 3

class put_h2(Put):
    def go(self):
        state[1] += turn * 2187
        state[15] += turn * 3
        state[24] += turn * 729
        state[44] += turn * 3

class put_a3(Put):
    def go(self):
        state[2] += turn * 1
        state[8] += turn * 9
        state[18] += turn * 1
        state[36] += turn * 1

class put_b3(Put):
    def go(self):
        state[2] += turn * 3
        state[9] += turn * 9
        state[19] += turn * 3
        state[37] += turn * 3

class put_c3(Put):
    def go(self):
        state[2] += turn * 9
        state[10] += turn * 9
        state[20] += turn * 9
        state[38] += turn * 9

class put_d3(Put):
    def go(self):
        state[2] += turn * 27
        state[11] += turn * 9
        state[21] += turn * 27
        state[39] += turn * 9

class put_e3(Put):
    def go(self):
        state[2] += turn * 81
        state[12] += turn * 9
        state[22] += turn * 81
        state[40] += turn * 9

class put_f3(Put):
    def go(self):
        state[2] += turn * 243
        state[13] += turn * 9
        state[23] += turn * 243
        state[41] += turn * 9

class put_g3(Put):
    def go(self):
        state[2] += turn * 729
        state[14] += turn * 9
        state[24] += turn * 243
        state[42] += turn * 9

class put_h3(Put):
    def go(self):
        state[2] += turn * 2187
        state[15] += turn * 9
        state[25] += turn * 243
        state[43] += turn * 9

class put_a4(Put):
    def go(self):
        state[3] += turn * 1
        state[8] += turn * 27
        state[19] += turn * 1
        state[35] += turn * 1

class put_b4(Put):
    def go(self):
        state[3] += turn * 3
        state[9] += turn * 27
        state[20] += turn * 3
        state[36] += turn * 3

class put_c4(Put):
    def go(self):
        state[3] += turn * 9
        state[10] += turn * 27
        state[21] += turn * 9
        state[37] += turn * 9

class put_d4(Put):
    def go(self):
        state[3] += turn * 27
        state[11] += turn * 27
        state[22] += turn * 27
        state[38] += turn * 27

class put_e4(Put):
    def go(self):
        state[3] += turn * 81
        state[12] += turn * 27
        state[23] += turn * 81
        state[39] += turn * 27

class put_f4(Put):
    def go(self):
        state[3] += turn * 243
        state[13] += turn * 27
        state[24] += turn * 81
        state[40] += turn * 27

class put_g4(Put):
    def go(self):
        state[3] += turn * 729
        state[14] += turn * 27
        state[25] += turn * 81
        state[41] += turn * 27

class put_h4(Put):
    def go(self):
        state[3] += turn * 2187
        state[15] += turn * 27
        state[26] += turn * 81
        state[42] += turn * 27

class put_a5(Put):
    def go(self):
        state[4] += turn * 1
        state[8] += turn * 81
        state[20] += turn * 1
        state[34] += turn * 1

class put_b5(Put):
    def go(self):
        state[4] += turn * 3
        state[9] += turn * 81
        state[21] += turn * 3
        state[35] += turn * 3

class put_c5(Put):
    def go(self):
        state[4] += turn * 9
        state[10] += turn * 81
        state[22] += turn * 9
        state[36] += turn * 9

class put_d5(Put):
    def go(self):
        state[4] += turn * 27
        state[11] += turn * 81
        state[23] += turn * 27
        state[37] += turn * 27

class put_e5(Put):
    def go(self):
        state[4] += turn * 81
        state[12] += turn * 81
        state[24] += turn * 27
        state[38] += turn * 81

class put_f5(Put):
    def go(self):
        state[4] += turn * 243
        state[13] += turn * 81
        state[25] += turn * 27
        state[39] += turn * 81

class put_g5(Put):
    def go(self):
        state[4] += turn * 729
        state[14] += turn * 81
        state[26] += turn * 27
        state[40] += turn * 81

class put_h5(Put):
    def go(self):
        state[4] += turn * 2187
        state[15] += turn * 81
        state[27] += turn * 27
        state[41] += turn * 81

class put_a6(Put):
    def go(self):
        state[5] += turn * 1
        state[8] += turn * 243
        state[21] += turn * 1
        state[33] += turn * 1

class put_b6(Put):
    def go(self):
        state[5] += turn * 3
        state[9] += turn * 243
        state[22] += turn * 3
        state[34] += turn * 3

class put_c6(Put):
    def go(self):
        state[5] += turn * 9
        state[10] += turn * 243
        state[23] += turn * 9
        state[35] += turn * 9

class put_d6(Put):
    def go(self):
        state[5] += turn * 27
        state[11] += turn * 243
        state[24] += turn * 9
        state[36] += turn * 27

class put_e6(Put):
    def go(self):
        state[5] += turn * 81
        state[12] += turn * 243
        state[25] += turn * 9
        state[37] += turn * 81

class put_f6(Put):
    def go(self):
        state[5] += turn * 243
        state[13] += turn * 243
        state[26] += turn * 9
        state[38] += turn * 243

class put_g6(Put):
    def go(self):
        state[5] += turn * 729
        state[14] += turn * 243
        state[27] += turn * 9
        state[39] += turn * 243

class put_h6(Put):
    def go(self):
        state[5] += turn * 2187
        state[15] += turn * 243
        state[28] += turn * 9
        state[40] += turn * 243

class put_a7(Put):
    def go(self):
        state[6] += turn * 1
        state[8] += turn * 729
        state[22] += turn * 1
        state[32] += turn * 1

class put_b7(Put):
    def go(self):
        state[6] += turn * 3
        state[9] += turn * 729
        state[23] += turn * 3
        state[33] += turn * 3

class put_c7(Put):
    def go(self):
        state[6] += turn * 9
        state[10] += turn * 729
        state[24] += turn * 3
        state[34] += turn * 9

class put_d7(Put):
    def go(self):
        state[6] += turn * 27
        state[11] += turn * 729
        state[25] += turn * 3
        state[35] += turn * 27

class put_e7(Put):
    def go(self):
        state[6] += turn * 81
        state[12] += turn * 729
        state[26] += turn * 3
        state[36] += turn * 81

class put_f7(Put):
    def go(self):
        state[6] += turn * 243
        state[13] += turn * 729
        state[27] += turn * 3
        state[37] += turn * 243

class put_g7(Put):
    def go(self):
        state[6] += turn * 729
        state[14] += turn * 729
        state[28] += turn * 3
        state[38] += turn * 729

class put_h7(Put):
    def go(self):
        state[6] += turn * 2187
        state[15] += turn * 729
        state[29] += turn * 3
        state[39] += turn * 729

class put_a8(Put):
    def go(self):
        state[7] += turn * 1
        state[8] += turn * 2187
        state[23] += turn * 1
        state[31] += turn * 1

class put_b8(Put):
    def go(self):
        state[7] += turn * 3
        state[9] += turn * 2187
        state[24] += turn * 1
        state[32] += turn * 3

class put_c8(Put):
    def go(self):
        state[7] += turn * 9
        state[10] += turn * 2187
        state[25] += turn * 1
        state[33] += turn * 9

class put_d8(Put):
    def go(self):
        state[7] += turn * 27
        state[11] += turn * 2187
        state[26] += turn * 1
        state[34] += turn * 27

class put_e8(Put):
    def go(self):
        state[7] += turn * 81
        state[12] += turn * 2187
        state[27] += turn * 1
        state[35] += turn * 81

class put_f8(Put):
    def go(self):
        state[7] += turn * 243
        state[13] += turn * 2187
        state[28] += turn * 1
        state[36] += turn * 243

class put_g8(Put):
    def go(self):
        state[7] += turn * 729
        state[14] += turn * 2187
        state[29] += turn * 1
        state[37] += turn * 729

class put_h8(Put):
    def go(self):
        state[7] += turn * 2187
        state[15] += turn * 2187
        state[30] += turn * 1
        state[38] += turn * 2187

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
        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_d2_e2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_c5_d5_e5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_c2_d3_f5_g6(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_b1_c1_e1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_a4_a5_a7(Flip):
    def go(self):
        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_d3_e3(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_c2_c3_c5_c6_c7(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_c3_d3_e3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_b6_c6_d6_e6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_d4_d5_d6_d7(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_b3_c4_d5(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_e2_e3_e4_e5_e6_e7(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_g2_g3_g4(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_a2_a4_a5_a6_a7(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_d7_e7(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_f7_g6(Flip):
    def go(self):
        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_a3_a4(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

class flip_e3_e4_e6(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_c2_c3_c4_c5(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_c3_c4_c5_c6(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_h6_h7(Flip):
    def go(self):
        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_d4_d5(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_b7_d7_e7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_h3_h4_h6_h7(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_b3_c4(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

class flip_c3_d4_f6_g7(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e5_e7(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_f4_g5(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_d2_f4(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_c1_d1_e1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b8_c8_d8_e8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_c8_e8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_e4_e5_e7(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_a4_a6_a7(Flip):
    def go(self):
        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_c3_d3_e3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_b2_c2_d2_e2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_e5_e6_e7(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_b2_d2_e2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_d5_f7(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_a3_a5_a6_a7(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_b2_c3_e5_f6(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b8_c8_e8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_g2_g4_g5(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b8_d8_e8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_h5_h6(Flip):
    def go(self):
        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_c3_d3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_c4_e4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_e3_e5_e6_e7(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_d2_d3_d4_d6(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_b6_c6_d6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_e6_e7(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b4_c4_e4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_d2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_e4_e6_e7(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_f2_f3_f4_f5_f6_f7(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c4_d3(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_d5(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_c3_d3_e3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b5_b6(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_c3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

class flip_b4_c4_e4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_c2_c4_c5_c6(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_b3_c2(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

class flip_b7_c6_d5(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_g4_g6_g7(Flip):
    def go(self):
        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b2_b3(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

class flip_d3_d4_d5_d6_d7(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_a2_a4(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

class flip_g2_g3_g5_g6(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_e2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_b6_c5_d4_e3_f2(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_c4_c5_c6_c7(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_d2_d4_d5_d6(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_d4_e4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_a3_a5_a6(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_e8(Flip):
    def go(self):
        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

class flip_a2_a3_a5_a6_a7(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_d2_d3_d5_d6(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_f2_f3_f4_f6_f7(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_f3_f4_f5(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_c4_d5_e6(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b7_c6_d5_e4_f3(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b3_c4_d5_e6_f7(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c4_e6(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_d8_e8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_f3_f4_f5_f6_f7(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c8_d8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_h4_h6(Flip):
    def go(self):
        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_d3_f5_g6(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_e2_e3_e5_e6(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_f3_f4_f6_f7(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_b3_d3_e3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_b5_c5_d5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_h3_h5(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

class flip_b2_c3_d4_e5_f6(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b1_c1_e1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_c6_d5_f3_g2(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_c4_d4_e4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_c5_d5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_b4_b6(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_e5_f6(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_c8_e8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_a4_a5_a6_a7(Flip):
    def go(self):
        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_f4_f5_f6_f7(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_b2_c2_d2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_c3_e3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_b2_c2_d2_e2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_c6_e6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_e2_e3_e5(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_b1_c1_d1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_d4_f2(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_d3_e3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_d3_d4_d6(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_d5_d7(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_e1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_c4_e4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_g2_g3_g4_g5_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b7_c6_d5_e4_f3_g2(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_a2_a3_a4_a5_a6(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_f4_f5_f6(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_e6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_g2_g3_g4_g6(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_b4_b6_b7(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_d7_e6_f5(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_h4_h6_h7(Flip):
    def go(self):
        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_c2_d2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

class flip_d7(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_b3_b4_b5_b6_b7(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_c6_d6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_c6_d5_e4_f3(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b4_c4_d4_e4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_b1_c1_d1_e1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_b2_c2_e2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_a7(Flip):
    def go(self):
        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_b2_c3_e5_f6_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b2_d4_e5_f6_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e2_g4(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_e2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_d2_e3_f4(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b3_b5_b6_b7(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_e5_f4_g3(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_g3_g4_g5_g7(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e3_f2(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_d6_e6(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b2_b4_b5_b6_b7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_c7_d7_e7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c3_d2(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

class flip_e7_f6_g5(Flip):
    def go(self):
        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_c4_c5(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_h2_h4_h5_h6(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_f4_g3(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_c1_d1_e1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b8_c8_e8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_h4_h5_h6(Flip):
    def go(self):
        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_b7_d5(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_h7(Flip):
    def go(self):
        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_b7_c6_e4_f3(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c2_d3_e4_f5_g6(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_d2_d4(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_f3_f5_f6_f7(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c6_e4_f3_g2(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_a3_a4_a5(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

class flip_c7_e7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_c3_e5(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_a2_a3_a5_a6(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_b4_c5(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_b4_d2(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

class flip_c6_d6_e6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b8_d8_e8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

class flip_c5_d5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_c6_d6_e6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b2_b4_b5(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

class flip_a5_a6_a7(Flip):
    def go(self):
        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_b5_c5_e5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_d7_e7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_f2_f3_f4_f5(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_f3_g2(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_e4_f5(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_g2_g3(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_a2_a3_a5(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

class flip_c7_e7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_d3_d4(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_h2_h3(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

class flip_b8_c8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

class flip_e4_f3_g2(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_d4_e3(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_c4_d5_f7(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c4_d5(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_c1_d1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_a3(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

class flip_d4_f6(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_c3_d4_f6(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b3_c3_d3_e3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_b3_b4_b5(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

class flip_e4_e6(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_g4_g5_g6(Flip):
    def go(self):
        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_e8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_b6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_f2_f3_f5_f6_f7(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c6_e4_f3(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c6_d6_e6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_c8_d8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

class flip_h2_h3_h4_h6(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_b1_c1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

class flip_b1_c1_d1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

class flip_b8_c8_d8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

class flip_c7_d6_e5_f4(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_c6_d5_e4_f3_g2(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_c2_c4(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

class flip_e3_e5_e6(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_e2_e3(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_h3(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

class flip_e4_f3(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b7_d7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_e1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_d3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_b8_d8_e8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_d3_e3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_e3(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_b5_c4(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

class flip_b3_c3_d3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c2_c3_c4_c6_c7(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_c7_d6_f4_g3(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_d6_e6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_b7_c7_d7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_d4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_g5_g6(Flip):
    def go(self):
        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_h2_h3_h5_h6(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_g2_g3_g4_g5_g6_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_d4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_d5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_d3_e3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c7_e5_f4(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

class flip_c3_c4(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

class flip_e2_e4_e5_e6_e7(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_f4_f5(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_d7_f5_g4(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_b2_c2_d2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_b4_d4_e4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_c1_d1_e1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_c3_d4_e5_f6(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_d2_e2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_b2_b3_b4_b5_b7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_e5_g3(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_f3_g4(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_b1_d1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

class flip_f2_f3_f4_f5_f6(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b5_b6_b7(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_f6_g5(Flip):
    def go(self):
        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_d4_e5(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_c3_d4_e5(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_h5_h6_h7(Flip):
    def go(self):
        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_b7_c7_d7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b6_c6_e6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_c7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_b4_b5_b6(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_c6_e6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_d2_d3_d5(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_h2_h3_h5(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

class flip_a5(Flip):
    def go(self):
        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

class flip_e2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_b2_d2_e2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_c7_d7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

class flip_b5_c4_e2(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_d4_e5_f6_g7(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c2_e4_f5(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_c2_c3_c4_c5_c6_c7(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_g2_g3_g4_g6_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e3_f4(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_e2_f3_g4(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_c1_d1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_d5_e5(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_d2(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

class flip_c3_d4(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_c2_e2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_c5_d4_f2(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_g4_g6(Flip):
    def go(self):
        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_c4_d5_e6_f7(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c3_c5_c6_c7(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_b2_b4(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

class flip_e3_e5(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_c7_e5(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_d5_e4_f3_g2(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_b5_c5_d5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_e5(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_b7_c6_d5_f3_g2(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_e5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_c6_e4(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_d3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b6_c5_e3_f2(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_c3_d3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b4_d4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_b6_c6_d6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b6_c5_d4_e3(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_e7_f6(Flip):
    def go(self):
        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_c2_c3_c4_c5_c6(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_a2_a3_a4_a5(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

class flip_d3_e4_f5_g6(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_d7_e7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b2_c2_e2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_f3_f4_f5_f6(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_c7_e5_f4_g3(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_c5_e3_f2(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_e3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_g3_g4_g5(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b8_c8_d8_e8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

class flip_h3_h4_h5(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

class flip_h3_h4_h5_h6(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_c3_c4_c5_c6_c7(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_b2_c3_d4_e5_f6_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_g2_g4_g5_g6_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c6_d6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_d3_e4(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_d1_e1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b2_b3_b5_b6_b7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_b7_d5_e4_f3_g2(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_d2_d3_d5_d6_d7(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_d6_d7(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_e8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_b2_b3_b4(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

class flip_d7_f5(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_b4_c5_d6_e7(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_d4_d6(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_c5_d5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b3_c3_d3_e3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b6_c7(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_e6_f5_g4(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_b2_c3_d4_e5_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

class flip_c7_d7_e7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_e4_g2(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_a4_a5_a6(Flip):
    def go(self):
        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_e5_g7(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_d7_e6_g4(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_b8_c8_e8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

class flip_b6_c5_d4(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_f6_f7(Flip):
    def go(self):
        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_d7_e6(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b3_d5_e6(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b4_c3_d2(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

class flip_b3_b4_b5_b7(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_b6_c6_e6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_h5(Flip):
    def go(self):
        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

class flip_b6_c5(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_d3_d4_d5(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_d5_d6(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_b3_b5(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

class flip_b7_c7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_e1(Flip):
    def go(self):
        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

class flip_g6_g7(Flip):
    def go(self):
        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b2_c2_d2_e2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_e5_e6(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_h5_h7(Flip):
    def go(self):
        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_a2_a3_a4_a5_a6_a7(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_b3_c3_d3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_e4_e5_e6(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_d5_e4_f3(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c3_c4_c5(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_f2_f3_f5(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_e3_e4_e5(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_c5_d4_e3(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_c7_d6(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_c5_c7(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_b1_c1_d1_e1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

class flip_e6_f5(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_h2_h3_h5_h6_h7(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_b7_c7_d7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_b3_d5_e6_f7(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_d6(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_c6_d5(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_b8_c8_d8_e8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_e7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c8_d8_e8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

class flip_a5_a7(Flip):
    def go(self):
        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_e5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_f3_f4(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b2_b4_b5_b6(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_c2_d3_e4_f5(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_c4_d4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_d2_e3_g5(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_d5_f3_g2(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_b5_c5_d5_e5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_d6_e5_f4(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_g2_g3_g5(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_d3_d5_d6_d7(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_f3_f4_f6(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_c3_e3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_g5_g6_g7(Flip):
    def go(self):
        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c7_d6_e5_f4_g3(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_c4_d4_e4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_c7_d7_e7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_d2_d3_d4_d5_d6_d7(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_b3_d3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_h2_h4_h5(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

class flip_c5_d5_e5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b2_c3_d4_f6(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_f5_f7(Flip):
    def go(self):
        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_e4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_a6_a7(Flip):
    def go(self):
        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_c7_e7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b2_b3_b4_b5(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

class flip_b2_b3_b4_b6_b7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_d6_e6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_h3_h5_h6_h7(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_d4(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_b1_d1_e1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_h2_h4(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

class flip_c2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

class flip_d3_e4_f5(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_b4_c4_d4_e4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_d2_e2(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_b7_d5_e4_f3(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b2_c3_d4_f6_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b6_c5_e3(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_b5_c5_d5_e5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b3_d3_e3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_e2_e3_e4_e6(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_e7(Flip):
    def go(self):
        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_d4_e5_f6(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b2_d2_e2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_a3_a4_a5_a7(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_f2_f4_f5_f6_f7(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_f2_f4(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b5_c5_d5_e5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_g2_g4_g5_g6(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_b3_c4_e6_f7(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_h3_h4(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

class flip_c6_d7(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_d2_d4_d5(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_d4_d5_d7(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_c6_e6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_d3_e2(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_c1_d1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

class flip_b7_d7_e7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_e2_e3_e4_e5_e7(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_d1_e1(Flip):
    def go(self):
        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

class flip_b7_c6_d5_e4_g2(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_b5_c6(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_b4_c4_d4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_a4_a6(Flip):
    def go(self):
        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_b3_c3_e3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c2_c4_c5(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_b7_c7_e7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_a3_a4_a6_a7(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_b5_c5_d5_e5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_c4_c5_c7(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_c5_d5_e5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_h2_h3_h4_h5(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

class flip_b2_c3_d4_e5(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_d7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_e5_f6_g7(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b4_c5_e7(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_c2_e2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_h4_h5_h7(Flip):
    def go(self):
        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_g2_g3_g4_g5_g6(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_e4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_b1_d1_e1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

class flip_f6_g7(Flip):
    def go(self):
        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e2_e3_e4_e6_e7(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_b7_d5_e4(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_b3_c3_d3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_b6_c5_d4_f2(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_d6_f4(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_a2_a4_a5_a6(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_b3_b5_b6(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_d5_e4_g2(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_d8_e8(Flip):
    def go(self):
        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

class flip_b1_d1_e1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b6_d4(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_b2_c2_e2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_c2_e4_f5_g6(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_f5_g4(Flip):
    def go(self):
        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_a3_a4_a5_a6_a7(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_g3_g4_g5_g6(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_c3_e5_f6_g7(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b3_c3_d3_e3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_d2_d3(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_g2_g4(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_d6_e5(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_f4_f5_f7(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_e6_f7(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_d4_e4(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_b5_c5_d5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_b8_c8_d8_e8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_c3_c4_c5_c7(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_c6_d5_e4_g2(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_d8(Flip):
    def go(self):
        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

class flip_c2_d2_e2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_a4(Flip):
    def go(self):
        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

class flip_d5_e5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_d5_f3(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c5_d4_e3_f2(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_d2_d3_d4_d5_d7(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_a2_a3_a4_a6(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_d5_d6_d7(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_h2_h3_h4_h5_h7(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_c2_e2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_e2_f3(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_d6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_b7_c7_d7_e7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_d3_f5(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_b7_d7_e7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_b4_d6(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_e3_g5(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_e3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b4_c4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

class flip_e2_e4_e5(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_c3_e3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c5_d4(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_c7_d7_e7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_a2_a3_a4_a6_a7(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_b5_b7(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_b3_d5(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_h2_h3_h4_h5_h6_h7(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_b3_c3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

class flip_d5_e4(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_c8_d8_e8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_c2_c3_c4_c5_c7(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_c1_e1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_b5_d5_e5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_g3_g5(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_e2_e4(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_c4_d3_e2(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_e4_g6(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_c5_d6_e7(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_b3_c3_d3_e3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_e4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_c6_d6_e6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_c4_d4_e4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_d1_e1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_e3_e4(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_c5_e7(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_c1_d1_e1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

class flip_d3_d4_d5_d7(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_c4_d4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_b6_c6_e6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_c1_e1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b4_c4_d4_e4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_f2_g3(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_e7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e3_e4_e5_e6(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b1_c1_d1_e1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b4_b5_b6_b7(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_e4_e5(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_b4_d6_e7(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_d2_d3_d4_d5(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_f4_f6(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b2_c2_d2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

class flip_b5_c5_e5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_b8_c8_d8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_b6_d6_e6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_c5_e5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_c2_c3_c5_c6(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_f2_f4_f5(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_c6_c7(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_a2_a3(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

class flip_h2(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

class flip_b3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

class flip_c1_e1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

class flip_f2_f4_f5_f6(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_f5_f6(Flip):
    def go(self):
        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b5_d5_e5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_d7_e7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_h4_h5(Flip):
    def go(self):
        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

class flip_a3_a5(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

class flip_c7_d6_e5_g3(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_d5_e5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_c2_c3_c4_c6(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_b2_d2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

class flip_f3_f5(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_g4_g5_g6_g7(Flip):
    def go(self):
        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_d7_e6_f5_g4(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_c2_c3_c4(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

class flip_h3_h5_h6(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_e6_g4(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_e7_g5(Flip):
    def go(self):
        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_c2_d3(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_c6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_h2_h4_h5_h6_h7(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_g2_g3_g5_g6_g7(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b4_b5(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

class flip_c8_e8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

class flip_d4_d6_d7(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_b1_c1_e1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

class flip_b2_b3_b4_b5_b6(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_c5_e3(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_a2_a3_a4_a5_a7(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[6] += 2 * turn * 1
        state[8] += 2 * turn * 729
        state[22] += 2 * turn * 1
        state[32] += 2 * turn * 1

class flip_b2_c3_e5(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_h4_h5_h6_h7(Flip):
    def go(self):
        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_b5_c4_d3(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_b7_c7_d7_e7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_b5_d3(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_b8_c8_d8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_c2_d3_f5(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_b5_d5_e5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_d2_d3_d4(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_e2_e3_e4(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_h2_h3_h4(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

class flip_b3_b4_b6_b7(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_b6_d6_e6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_g3_g5_g6(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_g3_g4_g6_g7(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c3_d3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_b1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

class flip_d4_e4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_c5_d5_e5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_f5_g6(Flip):
    def go(self):
        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_d8_e8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_g3_g4_g6(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_h3_h4_h5_h7(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_h3_h4_h6(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_c4_e4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_d5_e5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_g2_g3_g4_g5(Flip):
    def go(self):
        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_e4_f5_g6(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_d6_e7(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_f5_f6_f7(Flip):
    def go(self):
        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_f3_f5_f6(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_d6_e6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_a3_a4_a6(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_c4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

class flip_f2_f3_f4_f5_f7(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_d3_d5_d6(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_a2(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

class flip_c3_d4_e5_f6_g7(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b7_c7_d7_e7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c2_e4(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_c4_e6_f7(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c3_c5_c6(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_e3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_b2_b3_b4_b5_b6_b7(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_e4_e5_e6_e7(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_b7_c6_e4_f3_g2(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_c8_d8_e8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_d3_d5(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_c3_e5_f6(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b7_c7_e7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c4_d4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_b1_c1_d1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_a2_a4_a5(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

class flip_c3_c4_c6_c7(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_d6_f4_g3(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_c2_d3_e4(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_h6(Flip):
    def go(self):
        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_b6_c6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_c5_e5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_g4_g5_g7(Flip):
    def go(self):
        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_b4_c5_d6(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_e2(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_b4_d4_e4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_d2_d3_d4_d6_d7(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_c4_d4_e4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_e2_e4_e5_e6(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_h3_h4_h5_h6_h7(Flip):
    def go(self):
        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_c8_d8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_b7_c7_e7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_c2_d2_e2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_d4_e5_g7(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_c3_c4_c6(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_f2_f3(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_c7_d7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_e7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_b4_c4_d4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b3_c4_d5_e6(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b2_c3(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

class flip_f3_f4_f5_f7(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_b7_c7_d7_e7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_d5_e6_f7(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_g3_g4_g5_g6_g7(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_d4_d5_d6(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_d2_e3_f4_g5(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_a2_a3_a4(Flip):
    def go(self):
        state[1] += 2 * turn * 1
        state[8] += 2 * turn * 3
        state[17] += 2 * turn * 1
        state[37] += 2 * turn * 1

        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

class flip_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b2_d4_e5_f6(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b7_c6(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_b2_d4_e5(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_e5_f4(Flip):
    def go(self):
        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b5_c5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_d6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_d1_e1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_d1_f1_g1(Flip):
    def go(self):
        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

        state[0] += 2 * turn * 729
        state[14] += 2 * turn * 1
        state[22] += 2 * turn * 729
        state[44] += 2 * turn * 1

class flip_b4_d4_e4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_b6_c6_d6_e6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_g5_g7(Flip):
    def go(self):
        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_e3_f4_g5(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b3_b4_b5_b6(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_c5_c6(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_b6_d6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_b3_c3_e3_f3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_h4(Flip):
    def go(self):
        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

class flip_d2_f4_g5(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b3_c4_e6(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

class flip_b3_b4(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

class flip_c3_c5(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_a5_a6(Flip):
    def go(self):
        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_g3_g4(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_d2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_f4_f6_f7(Flip):
    def go(self):
        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_b2_b3_b4_b6(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_e6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_f2_f3_f5_f6(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_b2_c3_d4(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_c4_c6_c7(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_f2_f3_f4(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b2_d4(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_b2_c2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

class flip_c4_c6(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_c8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

class flip_b4_b5_b7(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_c2_c3(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

class flip_d6_e5_f4_g3(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_e6_f6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_c6_d6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_a6(Flip):
    def go(self):
        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_d5_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_c2_d3_e4_g6(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_d4_e3_f2(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_b5_d5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

class flip_b5_c5_e5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_c2_d2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_c2_d2_e2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_b4_c4_d4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

class flip_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b6_b7(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

class flip_b2_b3_b5_b6(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_b3_d3_e3_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_f5(Flip):
    def go(self):
        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

class flip_d1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_c5_d6(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_d5_e6(Flip):
    def go(self):
        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_c3_d3_e3_g3(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_d3(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

class flip_c1(Flip):
    def go(self):
        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

class flip_d8_e8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_f2_f3_f4_f6(Flip):
    def go(self):
        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_c6_d5_f3(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_d2_e2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_c5_c6_c7(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_c3_d4_e5_g7(Flip):
    def go(self):
        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b5_c4_d3_e2(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_d2_d3_d4_d5_d6(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_e8_f8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_c2_c4_c5_c6_c7(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

class flip_d6_e5_g3(Flip):
    def go(self):
        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

class flip_h2_h3_h4_h5_h6(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[4] += 2 * turn * 2187
        state[15] += 2 * turn * 81
        state[27] += 2 * turn * 27
        state[41] += 2 * turn * 81

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

class flip_e6(Flip):
    def go(self):
        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_g3_g5_g6_g7(Flip):
    def go(self):
        state[2] += 2 * turn * 729
        state[14] += 2 * turn * 9
        state[24] += 2 * turn * 243
        state[42] += 2 * turn * 9

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_b7_c6_d5_f3(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_d4_f6_g7(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_a3_a4_a5_a6(Flip):
    def go(self):
        state[2] += 2 * turn * 1
        state[8] += 2 * turn * 9
        state[18] += 2 * turn * 1
        state[36] += 2 * turn * 1

        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

        state[5] += 2 * turn * 1
        state[8] += 2 * turn * 243
        state[21] += 2 * turn * 1
        state[33] += 2 * turn * 1

class flip_d4_e4_f4(Flip):
    def go(self):
        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b6_c6_d6_e6_f6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 243
        state[13] += 2 * turn * 243
        state[26] += 2 * turn * 9
        state[38] += 2 * turn * 243

class flip_d3_e4_g6(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_b4_c4_d4_e4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_b4_c3(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

class flip_c6_d5_e4(Flip):
    def go(self):
        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_b5_c6_d7(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_b2_c2_d2_e2(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_c5_e5_f5_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[4] += 2 * turn * 243
        state[13] += 2 * turn * 81
        state[25] += 2 * turn * 27
        state[39] += 2 * turn * 81

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b3_b4_b6(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

class flip_b1_c1_d1_e1_f1(Flip):
    def go(self):
        state[0] += 2 * turn * 3
        state[9] += 2 * turn * 1
        state[17] += 2 * turn * 3
        state[39] += 2 * turn * 1

        state[0] += 2 * turn * 9
        state[10] += 2 * turn * 1
        state[18] += 2 * turn * 9
        state[40] += 2 * turn * 1

        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

        state[0] += 2 * turn * 81
        state[12] += 2 * turn * 1
        state[20] += 2 * turn * 81
        state[42] += 2 * turn * 1

        state[0] += 2 * turn * 243
        state[13] += 2 * turn * 1
        state[21] += 2 * turn * 243
        state[43] += 2 * turn * 1

class flip_b5_d3_e2(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_h2_h3_h4_h6_h7(Flip):
    def go(self):
        state[1] += 2 * turn * 2187
        state[15] += 2 * turn * 3
        state[24] += 2 * turn * 729
        state[44] += 2 * turn * 3

        state[2] += 2 * turn * 2187
        state[15] += 2 * turn * 9
        state[25] += 2 * turn * 243
        state[43] += 2 * turn * 9

        state[3] += 2 * turn * 2187
        state[15] += 2 * turn * 27
        state[26] += 2 * turn * 81
        state[42] += 2 * turn * 27

        state[5] += 2 * turn * 2187
        state[15] += 2 * turn * 243
        state[28] += 2 * turn * 9
        state[40] += 2 * turn * 243

        state[6] += 2 * turn * 2187
        state[15] += 2 * turn * 729
        state[29] += 2 * turn * 3
        state[39] += 2 * turn * 729

class flip_b4_c4_e4_f4_g4(Flip):
    def go(self):
        state[3] += 2 * turn * 3
        state[9] += 2 * turn * 27
        state[20] += 2 * turn * 3
        state[36] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

class flip_c8_d8_e8_g8(Flip):
    def go(self):
        state[7] += 2 * turn * 9
        state[10] += 2 * turn * 2187
        state[25] += 2 * turn * 1
        state[33] += 2 * turn * 9

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 81
        state[12] += 2 * turn * 2187
        state[27] += 2 * turn * 1
        state[35] += 2 * turn * 81

        state[7] += 2 * turn * 729
        state[14] += 2 * turn * 2187
        state[29] += 2 * turn * 1
        state[37] += 2 * turn * 729

class flip_b3_c3_e3(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_d8_f8(Flip):
    def go(self):
        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

        state[7] += 2 * turn * 243
        state[13] += 2 * turn * 2187
        state[28] += 2 * turn * 1
        state[36] += 2 * turn * 243

class flip_e2_e3_e4_e5(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_e3_e4_e5_e7(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_b7_c6_d5_e4(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_b6_c6_d6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_c2_d2_e2_f2_g2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

        state[1] += 2 * turn * 729
        state[14] += 2 * turn * 3
        state[23] += 2 * turn * 729
        state[43] += 2 * turn * 3

class flip_g5(Flip):
    def go(self):
        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_c7_d7_f7(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_f3(Flip):
    def go(self):
        state[2] += 2 * turn * 243
        state[13] += 2 * turn * 9
        state[23] += 2 * turn * 243
        state[41] += 2 * turn * 9

class flip_b6_d6_e6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_e2_e3_e5_e6_e7(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_e2_e3_e4_e5_e6(Flip):
    def go(self):
        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

class flip_b6_d4_e3(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_d1(Flip):
    def go(self):
        state[0] += 2 * turn * 27
        state[11] += 2 * turn * 1
        state[19] += 2 * turn * 27
        state[41] += 2 * turn * 1

class flip_b8_d8(Flip):
    def go(self):
        state[7] += 2 * turn * 3
        state[9] += 2 * turn * 2187
        state[24] += 2 * turn * 1
        state[32] += 2 * turn * 3

        state[7] += 2 * turn * 27
        state[11] += 2 * turn * 2187
        state[26] += 2 * turn * 1
        state[34] += 2 * turn * 27

class flip_c7_d6_f4(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[3] += 2 * turn * 243
        state[13] += 2 * turn * 27
        state[24] += 2 * turn * 81
        state[40] += 2 * turn * 27

class flip_b6_d4_e3_f2(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_d3_d4_d5_d6(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

class flip_c4_c5_c6(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

class flip_g4_g5(Flip):
    def go(self):
        state[3] += 2 * turn * 729
        state[14] += 2 * turn * 27
        state[25] += 2 * turn * 81
        state[41] += 2 * turn * 27

        state[4] += 2 * turn * 729
        state[14] += 2 * turn * 81
        state[26] += 2 * turn * 27
        state[40] += 2 * turn * 81

class flip_b2_b3_b5(Flip):
    def go(self):
        state[1] += 2 * turn * 3
        state[9] += 2 * turn * 3
        state[18] += 2 * turn * 3
        state[38] += 2 * turn * 3

        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

class flip_d7_f7_g7(Flip):
    def go(self):
        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

        state[6] += 2 * turn * 729
        state[14] += 2 * turn * 729
        state[28] += 2 * turn * 3
        state[38] += 2 * turn * 729

class flip_d2_d4_d5_d6_d7(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_b3_c4_d5_f7(Flip):
    def go(self):
        state[2] += 2 * turn * 3
        state[9] += 2 * turn * 9
        state[19] += 2 * turn * 3
        state[37] += 2 * turn * 3

        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[4] += 2 * turn * 27
        state[11] += 2 * turn * 81
        state[23] += 2 * turn * 27
        state[37] += 2 * turn * 27

        state[6] += 2 * turn * 243
        state[13] += 2 * turn * 729
        state[27] += 2 * turn * 3
        state[37] += 2 * turn * 243

class flip_c2_c3_c5(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[2] += 2 * turn * 9
        state[10] += 2 * turn * 9
        state[20] += 2 * turn * 9
        state[38] += 2 * turn * 9

        state[4] += 2 * turn * 9
        state[10] += 2 * turn * 81
        state[22] += 2 * turn * 9
        state[36] += 2 * turn * 9

class flip_d2_e3(Flip):
    def go(self):
        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

class flip_b5_d7(Flip):
    def go(self):
        state[4] += 2 * turn * 3
        state[9] += 2 * turn * 81
        state[21] += 2 * turn * 3
        state[35] += 2 * turn * 3

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_c4_e2(Flip):
    def go(self):
        state[3] += 2 * turn * 9
        state[10] += 2 * turn * 27
        state[21] += 2 * turn * 9
        state[37] += 2 * turn * 9

        state[1] += 2 * turn * 81
        state[12] += 2 * turn * 3
        state[21] += 2 * turn * 81
        state[41] += 2 * turn * 3

class flip_e4(Flip):
    def go(self):
        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

class flip_c2_d2_f2(Flip):
    def go(self):
        state[1] += 2 * turn * 9
        state[10] += 2 * turn * 3
        state[19] += 2 * turn * 9
        state[39] += 2 * turn * 3

        state[1] += 2 * turn * 27
        state[11] += 2 * turn * 3
        state[20] += 2 * turn * 27
        state[40] += 2 * turn * 3

        state[1] += 2 * turn * 243
        state[13] += 2 * turn * 3
        state[22] += 2 * turn * 243
        state[42] += 2 * turn * 3

class flip_d3_d4_d6_d7(Flip):
    def go(self):
        state[2] += 2 * turn * 27
        state[11] += 2 * turn * 9
        state[21] += 2 * turn * 27
        state[39] += 2 * turn * 9

        state[3] += 2 * turn * 27
        state[11] += 2 * turn * 27
        state[22] += 2 * turn * 27
        state[38] += 2 * turn * 27

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[6] += 2 * turn * 27
        state[11] += 2 * turn * 729
        state[25] += 2 * turn * 3
        state[35] += 2 * turn * 27

class flip_a4_a5(Flip):
    def go(self):
        state[3] += 2 * turn * 1
        state[8] += 2 * turn * 27
        state[19] += 2 * turn * 1
        state[35] += 2 * turn * 1

        state[4] += 2 * turn * 1
        state[8] += 2 * turn * 81
        state[20] += 2 * turn * 1
        state[34] += 2 * turn * 1

class flip_e3_e4_e6_e7(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_e3_e4_e5_e6_e7(Flip):
    def go(self):
        state[2] += 2 * turn * 81
        state[12] += 2 * turn * 9
        state[22] += 2 * turn * 81
        state[40] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[6] += 2 * turn * 81
        state[12] += 2 * turn * 729
        state[26] += 2 * turn * 3
        state[36] += 2 * turn * 81

class flip_c7_d6_e5(Flip):
    def go(self):
        state[6] += 2 * turn * 9
        state[10] += 2 * turn * 729
        state[24] += 2 * turn * 3
        state[34] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[4] += 2 * turn * 81
        state[12] += 2 * turn * 81
        state[24] += 2 * turn * 27
        state[38] += 2 * turn * 81

class flip_b6_c6_d6_e6_g6(Flip):
    def go(self):
        state[5] += 2 * turn * 3
        state[9] += 2 * turn * 243
        state[22] += 2 * turn * 3
        state[34] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[5] += 2 * turn * 27
        state[11] += 2 * turn * 243
        state[24] += 2 * turn * 9
        state[36] += 2 * turn * 27

        state[5] += 2 * turn * 81
        state[12] += 2 * turn * 243
        state[25] += 2 * turn * 9
        state[37] += 2 * turn * 81

        state[5] += 2 * turn * 729
        state[14] += 2 * turn * 243
        state[27] += 2 * turn * 9
        state[39] += 2 * turn * 243

class flip_b7_c6_e4(Flip):
    def go(self):
        state[6] += 2 * turn * 3
        state[9] += 2 * turn * 729
        state[23] += 2 * turn * 3
        state[33] += 2 * turn * 3

        state[5] += 2 * turn * 9
        state[10] += 2 * turn * 243
        state[23] += 2 * turn * 9
        state[35] += 2 * turn * 9

        state[3] += 2 * turn * 81
        state[12] += 2 * turn * 27
        state[23] += 2 * turn * 81
        state[39] += 2 * turn * 27

#gen_funcs()
#stop

# init board state
turn = BLACK
put_d5().go()
put_e4().go()
turn = -turn
put_d4().go()
put_e5().go()
check_board()

turn = -turn

italian = 'F5D6C4D3E6F4E3F3C6F6G5G6E7F7C3G4D2C5H3H4E2F2G3C1C2E1D1B3F1G1F8D7C7G7A3B4B6B1H8B5A6A5A4B7A8G8H7H6H5G2H1H2A1D8E8C8B2A2B8A7'
human_moves = [italian[i*2:(i+1)*2] for i in range(60)]
moves = ['ABCDEFGH'.index(h[0]) + 8 * (int(h[1])-1) for h in human_moves]

for mv in moves:
    move_table[mv].go()
#    check_board()
    turn = -turn

check_board()

nx = sum(str_state(state[l]).count('2') for l in range(8))
no = sum(str_state(state[l]).count('0') for l in range(8))
print(f'{nx}-{no}')
print()
