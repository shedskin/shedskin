import time

'''
poppy - basic python othello player

-bitboard implementation (~30M moves/second on my system)
-alpha-beta pruning
-greedy evaluation function (for now)

copyright 2023 mark dufour

based on the following implementations/tutorials:

-https://www.hanshq.net/othello.html
-https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning

compiled with shedskin for a 150-times speedup.

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

    captured_disks = 0;

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


MOVES = 0

def search(state, color, depth, path, max_depth):
    global MOVES

    # end depth reached
    if depth == max_depth:
        return

    moves = possible_moves(state, color)

    # passing
    if moves == 0:
        color = color ^ 1
        moves = possible_moves(state, color)
        if moves == 0:
            return

    # try all possible moves and recurse
    orig_black = state[0]
    orig_white = state[1]

    for move in range(64):
        if moves & (1 << move):

#            path.append(move)
            do_move(state, color, move)
            MOVES += 1
#            print('path', ''.join(path))

            search(state, color ^ 1, depth+1, path, max_depth)

#            path.pop()
            state[0] = orig_black
            state[1] = orig_white


def evaluate(state, color):
    return int.bit_count(state[color]) - int.bit_count(state[color ^ 1])


def minimax_ab(state, color, depth, max_depth, is_max_player, alpha=-65, beta=65):
    if depth == max_depth:
        return evaluate(state, color)

    moves = possible_moves(state, color)

    # TODO passing?

    # try all possible moves and recurse
    orig_black = state[0]
    orig_white = state[1]

    if is_max_player: # TODO similar code for min player..
        best = -65

        for move in range(64):
            if moves & (1 << move):
                do_move(state, color, move)

                val = minimax_ab(state, color ^ 1, depth+1, max_depth, False, alpha, beta)

                state[0] = orig_black
                state[1] = orig_white

                best = max(best, val)
                alpha = max(alpha, best)

                if beta <= alpha:
                    break
    else:
        best = 65

        for move in range(64):
            if moves & (1 << move):
                do_move(state, color, move)

                val = minimax_ab(state, color ^ 1, depth+1, max_depth, True, alpha, beta)

                state[0] = orig_black
                state[1] = orig_white

                best = min(best, val)
                beta = min(beta, best)

                if beta <= alpha:
                    break

    return best


def main():
    board = (
        '........'
        '........'
        '........'
        '...OX...'
        '...XO...'
        '........'
        '........'
        '........'
    )
#    board = (
#        '..XXXXXO'
#        'XOXXXXO.'
#        'XOXOOOXO'
#        'XOXOOOXO'
#        'XOXOOOOO'
#        'XXOOOOOO'
#        'XOO..O.O'
#        '.OX.....'
#    )
    color = BLACK

    state = parse_state(board)
    print_board(state)

    max_depth = 11

    t0 = time.time()
    search(state, color, 0, [], max_depth)
    t1 = (time.time()-t0)
    print('%d moves in %.2fs seconds (%.2f/second)' % (MOVES, t1, MOVES/t1))

#    move = minimax_ab(state, color, 0, max_depth, -65, 65)
#    print(f'best move: {human_move(move)}')


if __name__ == '__main__':
    main()
