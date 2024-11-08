import time

# determine bitboard reference speed
# note this does not use SIMD, for a potential 8x speedup!

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

SHIFTS = [1, 9, 8, 7, 1, 9, 8, 7] # 4 right- and 4 left-shifts


def shift(disks, direction, S, M):
    if direction < 4:
        return (disks >> S) & M
    else:
        return (disks << S) & M


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


def parse_state(board):
    state = [0, 0]
    for move in range(64):
        mask = 1 << move
        if board[move] == 'X':
            state[0] |= mask
        elif board[move] == 'O':
            state[1] |= mask
    return state


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


if __name__ == '__main__':
    italian = 'F5D6C4D3E6F4E3F3C6F6G5G6E7F7C3G4D2C5H3H4E2F2G3C1C2E1D1B3F1G1F8D7C7G7A3B4B6B1H8B5A6A5A4B7A8G8H7H6H5G2H1H2A1D8E8C8B2A2B8A7'
    human_moves = [italian[i*2:(i+1)*2] for i in range(len(italian)//2)]
    moves = ['ABCDEFGH'.index(h[0]) + 8 * (int(h[1])-1) for h in human_moves]

    s0, s1 = parse_state(empty_board())

    t0 = time.time()
    for x in range(10**5):
        state = [s0, s1]
        color = BLACK
        for move in moves:
            do_move(state, color, move)
            color = 1 - color

    t = 60 * 10**5 // (time.time()-t0)
    print_board(state)
    print('moves/sec: %d' % t)
