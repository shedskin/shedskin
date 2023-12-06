import sys
import time

'''
poppy - basic python othello player

-bitboard implementation
-alpha-beta pruning
-mobility/corner evaluation function
-nboard GUI support
-UGI support (cutegames engine tournament software)

copyright 2023 mark dufour

based on the following implementations/tutorials:

-https://www.hanshq.net/othello.html
-https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning

compiled with shedskin for a ~200-times speedup.

'''

BLACK, WHITE = 0, 1

MASKS = [
    0x7F7F7F7F7F7F7F7F, # Right
    0x007F7F7F7F7F7F7F, # Down-right
    0x00FFFFFFFFFFFFFF, # Down
    0x00FEFEFEFEFEFEFE, # Down-left
    0xFEFEFEFEFEFEFEFE, # Left
    0xFEFEFEFEFEFEFE00, # Up-left
    0xFFFFFFFFFFFFFFFF, # Up
    0x7F7F7F7F7F7F7F00  # Up-right
]

CORNER_MASK = 0x8100000000000081

WIN_BONUS = 1 << 20
ALPHA_MIN = -65 * WIN_BONUS
BETA_MAX = 65 * WIN_BONUS

SHIFTS = [1, 9, 8, 7, 1, 9, 8, 7] # 4 right- and 4 left-shifts


def shift(disks, direction, S, M):
    if direction < 4:
        return (disks >> S) & M
    else:
        return (disks << S) & M


def possible_moves(state, color):
    moves = 0

    my_disks = state[color]
    opp_disks = state[color^1]
    empties = ~(my_disks | opp_disks)

    for direction in range(8):
        S = SHIFTS[direction]
        M = MASKS[direction]

        # Get opponent disks adjacent to my disks in direction dir.
        x = shift(my_disks, direction, S, M) & opp_disks

        # Add opponent disks adjacent to those, and so on.
        x |= shift(x, direction, S, M) & opp_disks
        x |= shift(x, direction, S, M) & opp_disks
        x |= shift(x, direction, S, M) & opp_disks
        x |= shift(x, direction, S, M) & opp_disks
        x |= shift(x, direction, S, M) & opp_disks

        # Empty cells adjacent to those are valid moves.
        moves |= shift(x, direction, S, M) & empties

    return moves


def do_move(state, color, move):
    disk = 1 << move
    state[color] |= disk

    my_disks = state[color]
    opp_disks = state[color ^ 1]

    captured_disks = 0

    for direction in range(8):
        S = SHIFTS[direction]
        M = MASKS[direction]

        # Find opponent disk adjacent to the new disk.
        x = shift(disk, direction, S, M) & opp_disks
        if x == 0:
            continue

        # Add any adjacent opponent disk to that one, and so on.
        x |= shift(x, direction, S, M) & opp_disks
        if x == 0:
            continue
        x |= shift(x, direction, S, M) & opp_disks
        if x == 0:
            continue
        x |= shift(x, direction, S, M) & opp_disks
        if x == 0:
            continue
        x |= shift(x, direction, S, M) & opp_disks
        if x == 0:
            continue
        x |= shift(x, direction, S, M) & opp_disks
        if x == 0:
            continue

        # Determine whether the disks were captured.
        bounding_disk = shift(x, direction, S, M) & my_disks
        if bounding_disk:
            captured_disks |= x

    state[color] ^= captured_disks
    state[color ^ 1] ^= captured_disks


def print_board(state):
    for move in range(64):
        mask = 1 << move
        if state[BLACK] & mask:
            print('X', end='')
        elif state[WHITE] & mask:
            print('O', end='')
        else:
            print('.', end='')
        if move % 8 == 7:
            print()
    print(f'black: {int.bit_count(state[0])}, white: {int.bit_count(state[1])}')


def parse_state(board):
    state = [0, 0]

    for move in range(64):
        mask = 1 << move
        if board[move] == 'X':
            state[0] |= mask
        elif board[move] == 'O':
            state[1] |= mask

    return state


def human_move(move):
    col = move & 0b111
    row = (move >>3) & 0b111
    return 'abcdefgh'[col]+str(row+1)


def parse_move(s):
    return 'abcdefgh'.index(s[0]) + 8 * (int(s[1])-1)


def evaluate(state, color, is_max_player, my_moves, opp_moves):
    value = 0

    # no moves left: greedy
    if my_moves | opp_moves == 0:
        value = int.bit_count(state[color]) - int.bit_count(state[color^1])
        value *= WIN_BONUS

    # else: value mobility and corners (wzebra)
    else:
        my_disks = state[color]
        opp_disks = state[color^1]

        my_corners = my_disks & CORNER_MASK
        opp_corners = opp_disks & CORNER_MASK

        value += (int.bit_count(my_corners) - int.bit_count(opp_corners)) * 16
        value += (int.bit_count(my_moves) - int.bit_count(opp_moves)) * 2

    if is_max_player:
        return value
    else:
        return -value


def minimax_ab(state, color, depth, max_depth, is_max_player, alpha=ALPHA_MIN, beta=BETA_MAX):
    global NODES
    NODES += 1

    moves = possible_moves(state, color)
    opp_moves = possible_moves(state, color^1)

    # max depth reached
    if depth == max_depth:
        return evaluate(state, color, is_max_player, moves, opp_moves)

    # player has to pass
    if moves == 0:
       if opp_moves == 0:
           return evaluate(state, color, is_max_player, moves, opp_moves)
       color = color ^ 1
       is_max_player = not is_max_player
       moves = opp_moves

    # try all possible moves and recurse
    orig_black = state[0]
    orig_white = state[1]

    if is_max_player:
        best_val = ALPHA_MIN
    else:
        best_val = BETA_MAX

    for move in range(64):
        if moves & (1 << move):
            do_move(state, color, move)

            val = minimax_ab(state, color ^ 1, depth+1, max_depth, not is_max_player, alpha, beta)

            state[0] = orig_black
            state[1] = orig_white

            if is_max_player:
                if val > best_val:
                    best_move = move
                    best_val = val

                alpha = max(alpha, best_val)

            else:
                if val < best_val:
                    best_move = move
                    best_val = val

                beta = min(beta, best_val)

            if beta <= alpha:
                break

    if depth > 0:
        return best_val
    else:
        return best_move


def empty_board():
    return (
        '........'
        '........'
        '........'
        '...OX...'
        '...XO...'
        '........'
        '........'
        '........'
    )


def vs_cpu_cli(max_depth):
    global NODES

    board = empty_board()
    state = parse_state(board)
    color = BLACK

    print_board(state)

    while True:
        NODES = 0
        passing = 0

        moves = possible_moves(state, color)
        if moves == 0:
            print('I pass')
            passing += 1
        else:
            print('(thinking)')
            t0 = time.time()
            move = minimax_ab(state, color, 0, max_depth, True)
            t1 = (time.time()-t0)
            print('%d nodes in %.2fs seconds (%.2f/second)' % (NODES, t1, NODES/t1))

            print(f'I move here: {human_move(move)}')
            do_move(state, color, move)
            print_board(state)

        color = color^1

        moves = possible_moves(state, color)
        if moves == 0:
            print('you pass')
            passing += 1
            if passing == 2:
                print_board(state)
                break
        else:
            while True:
                move = parse_move(input('your move? '))
                if moves & (1 << move):
                    break
            do_move(state, color, move)
            print_board(state)

        color = color^1


def vs_cpu_nboard(max_depth):
    board = empty_board()
    state = parse_state(board)
    color = BLACK

    sys.stdout.write('set myname Poppy\n')

    for line in sys.stdin:
        line = line.strip()

        if line == 'go':
            moves = possible_moves(state, color)
            if moves == 0:
                sys.stdout.write('=== PASS\n')
                color = color^1
            else:
                move = minimax_ab(state, color, 0, max_depth, True)
                sys.stdout.write('=== %s\n' % human_move(move).upper())

        elif line.startswith('ping '):
            sys.stdout.write('pong '+line[5:]+'\n')

        elif line.startswith('move '):
            b = line[5:7].lower()
            if b != 'pa':
                do_move(state, color, parse_move(b))
            color = color^1

        elif line.startswith('set game '):
            board = empty_board()
            state = parse_state(board)
            color = BLACK
            for l in line.split(']'):
                if '[' in l:
                    a, b = l.split('[')
                    b = b.lower()[:2]
                    if a == 'B':
                        if b != 'pa':
                            do_move(state, BLACK, parse_move(b))
                        color = WHITE
                    elif a == 'W':
                        if b != 'pa':
                            do_move(state, WHITE, parse_move(b))
                        color = BLACK

        elif line.startswith('set depth '):
            max_depth = int(line.split()[2])

        sys.stdout.flush()


def vs_cpu_ugi(max_depth):
    global NODES
    NODES = 0

    for line in sys.stdin:
        line = line.strip()

        if line == 'ugi':
            sys.stdout.write('ugiok\n')

        elif line == 'isready':
            sys.stdout.write('readyok\n')

        elif line == 'uginewgame':
            board = empty_board()
            state = parse_state(board)
            color = BLACK

        elif line == 'query p1turn':
            if color == BLACK:
                sys.stdout.write('response true\n')
            else:
                sys.stdout.write('response false\n')

        elif line == 'query result':
            blacks = int.bit_count(state[0])
            whites = int.bit_count(state[1])
            if blacks > whites:
                sys.stdout.write('response p1win\n')
            elif whites > blacks:
                sys.stdout.write('response p2win\n')
            else:
                sys.stdout.write('response draw\n')

        elif line == 'query gameover':
            moves = possible_moves(state, color)
            opp_moves = possible_moves(state, color^1)
            if moves | opp_moves == 0:
                sys.stdout.write('response true\n')
            else:
                sys.stdout.write('response false\n')

        elif line.startswith('go '):
            move = minimax_ab(state, color, 0, max_depth, True)
            sys.stdout.write('bestmove %s\n' % human_move(move))

        elif line.startswith('position'):
            segs = line.split()

            s = 1

            while s < len(segs):
                if segs[s] == 'fen':
                    s += 1

                    board = ''
                    for c in segs[s]:
                        if c.isdigit():
                           board += int(c) * '.'
                        elif c.lower() in 'ox':
                           board += c.upper()

                    assert len(board) == 64
                    state = parse_state(board)

                    s += 1
                    color = BLACK if segs[s].lower() == 'x' else WHITE

                elif segs[s] == 'startpos':
                    board = empty_board()
                    state = parse_state(board)
                    color = BLACK

                elif segs[s] == 'moves':
                    for hmove in segs[s + 1:]:
                        if hmove != 'moves':
                            do_move(state, color, parse_move(hmove.lower()))

                            if possible_moves(state, color^1) != 0:
                                color = color^1
                    break

                s += 1

        sys.stdout.flush()


def speed_test(max_depth):
    global NODES
    NODES = 0

    board = empty_board()
    state = parse_state(board)
    color = BLACK

    t0 = time.time()
    move = minimax_ab(state, color, 0, max_depth, True)
    t1 = (time.time()-t0)
    print('%d nodes in %.2f seconds (%.2f/second)' % (NODES, t1, NODES/t1))


if __name__ == '__main__':
    max_depth = 10
    mode = None

    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--depth':
            max_depth = int(sys.argv[i+2])
        elif arg == '--nboard':
            mode = 'nboard'
        elif arg == '--ugi':
            mode = 'ugi'
        elif arg == '--cli':
            mode = 'cli'

    if mode == 'nboard':
        vs_cpu_nboard(max_depth)
    elif mode == 'ugi':
        vs_cpu_ugi(max_depth)
    elif mode == 'cli':
        vs_cpu_cli(max_depth)
    else:
        speed_test(max_depth)
