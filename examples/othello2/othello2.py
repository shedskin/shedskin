import time

'''
othello bitboard implementation

copyright 2023 mark dufour

based on the following C implementation (with nice explanation):

https://www.hanshq.net/othello.html

speedup of using shedskin is about 100 times.

(from ~100K to ~10M moves/second on my system)

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


def shift(disks, direction):
    if direction < 4:
        return (disks >> SHIFTS[direction]) & MASKS[direction]
    else:
        return (disks << SHIFTS[direction]) & MASKS[direction]


def possible_moves(state, color):
    moves = 0

    my_disks = state[color]
    opp_disks = state[color^1]
    empties = ~(my_disks | opp_disks)

    for direction in range(8):
        # Get opponent disks adjacent to my disks in direction dir.
        x = shift(my_disks, direction) & opp_disks

        # Add opponent disks adjacent to those, and so on.
        x |= shift(x, direction) & opp_disks
        x |= shift(x, direction) & opp_disks
        x |= shift(x, direction) & opp_disks
        x |= shift(x, direction) & opp_disks
        x |= shift(x, direction) & opp_disks

        # Empty cells adjacent to those are valid moves.
        moves |= shift(x, direction) & empties

    return moves


def do_move(state, color, move):
    disk = 1 << move
    state[color] |= disk

    my_disks = state[color]
    opp_disks = state[color ^ 1]

    captured_disks = 0;

    for direction in range(8):
        # Find opponent disk adjacent to the new disk.
        x = shift(disk, direction) & opp_disks

        # Add any adjacent opponent disk to that one, and so on.
        x |= shift(x, direction) & opp_disks
        x |= shift(x, direction) & opp_disks
        x |= shift(x, direction) & opp_disks
        x |= shift(x, direction) & opp_disks
        x |= shift(x, direction) & opp_disks

        # Determine whether the disks were captured.
        bounding_disk = shift(x, direction) & my_disks
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
    print()


def parse_state(board):
    state = [0, 0]

    for move in range(64):
        mask = 1 << move
        if board[move] == 'X':
            state[0] |= mask
        elif board[move] == 'O':
            state[1] |= mask

    return state


#def human_move(row, col):
#    return 'abcdefgh'[col]+str(row+1)

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

    for move in range(63):
        if moves & (1 << move):

#            path.append(human_move(row, col))
            do_move(state, color, move)
            MOVES += 1
#            print('path', ''.join(path))

            search(state, color ^ 1, depth+1, path, max_depth)

#            path.pop()
            state[0] = orig_black
            state[1] = orig_white


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
    color = BLACK

    state = parse_state(board)
    print_board(state)

    max_depth = 12

    t0 = time.time()
    search(state, color, 4, [], max_depth)
    t1 = (time.time()-t0)

    print('%d moves in %.2fs seconds (%.2f/second)' % (MOVES, t1, MOVES/t1))


if __name__ == '__main__':
    main()
