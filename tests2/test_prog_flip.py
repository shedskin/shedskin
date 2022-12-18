# (c) Mark Dufour, Haifang Ni, tweaks by shakfu
# --- mark.dufour@gmail.com

empty, black, white = 0, 1, -1

SIZE=4

def get_board(n):
    board = [[empty for x in range(n)] for y in range(n)]
    c1 = (n // 2) - 1
    c2 = (n // 2)
    board[c1][c1] = board[c2][c2] = white
    board[c1][c2] = board[c2][c1] = black
    return board

board = get_board(SIZE)

player, depth = {white: "human", black: "lalaoth"}, 3


def possible_move(board, x, y, color):
    if board[x][y] != empty:
        return False
    for direction in [
        (1, 1),
        (-1, 1),
        (0, 1),
        (1, -1),
        (-1, -1),
        (0, -1),
        (1, 0),
        (-1, 0),
    ]:
        if flip_in_direction(board, x, y, direction, color):
            return True
    return False


def flip_in_direction(board, x, y, direction, color):
    other_color = False
    while True:
        x, y = x + direction[0], y + direction[1]
        if x not in range(SIZE) or y not in range(SIZE):
            return False
        square = board[x][y]
        if square == empty:
            return False
        if square != color:
            other_color = True
        else:
            return other_color


def flip_stones(board, move, color):
    global flips
    flips += 1
    for direction in [
        (1, 1),
        (-1, 1),
        (0, 1),
        (1, -1),
        (-1, -1),
        (0, -1),
        (1, 0),
        (-1, 0),
    ]:
        if flip_in_direction(board, move[0], move[1], direction, color):
            x, y = move[0] + direction[0], move[1] + direction[1]
            while board[x][y] != color:
                board[x][y] = color
                x, y = x + direction[0], y + direction[1]
    board[move[0]][move[1]] = color


# def print_board(board, turn):            # board: [], turn: []
#    for line in board:                   # []
#        print ' '.join([{white: 'O', black: 'X', empty: '.'}[square] for square in line]) # []
#    print 'turn:', player[turn]          # [], []
#    print 'black:', stone_count(board, black), 'white:', stone_count(board, white) # [], [], [], []


def possible_moves(board, color):
    return [
        (x, y) for x in range(SIZE) for y in range(SIZE) if possible_move(board, x, y, color)
    ]


# def coordinates(move):                   # move: []
#    return (int(move[1])-1, 'abcdefgh'.index(move[0])) # []
#
def stone_count(board, color):
    return sum([len([square for square in line if square == color]) for line in board])


# def human_move(move):                    # move: []
#    return 'abcdefgh'[move[0]]+str(move[1]+1) # []


def best_move(board, color, first, step=1):
    max_move, max_mobility, max_score = None, 0, 0
    # print 'possible', possible_moves(board, color) # [str], [list(tuple2(int, int))]

    for move in possible_moves(board, color):
        # print 'board before'
        # print_board(board, color)

        # print 'move', move
        if move in [(0, 0), (0, SIZE-1), (SIZE-1, 0), (SIZE-1, SIZE-1)]:
            mobility, score = SIZE*SIZE, SIZE*SIZE
            if color != first:
                mobility = SIZE*SIZE - mobility
        else:
            testboard = [
                [square for square in line] for line in board
            ]  # [list(list(int))]
            flip_stones(testboard, move, color)  # []
            # print_board(testboard, color) # []

            if step < depth:  # [int]
                # print 'deeper'           # [str]
                next_move, mobility = best_move(
                    testboard, -color, first, step + 1
                )  # [tuple2(tuple2(int, int), int)]
            else:
                # print 'mobility'         # [str]
                mobility = len(possible_moves(testboard, first))  # [int]
            score = mobility  # [int]
            if color != first:  # [int]
                score = SIZE*SIZE - score  # [int]
        if score >= max_score:  # []
            max_move, max_mobility, max_score = (
                move,
                mobility,
                score,
            )

    # print 'done'
    return max_move, max_mobility


def game():
    global flips
    flips = 0
    steps = 0
    turn = black
    while possible_moves(board, black) or possible_moves(board, white):
        if possible_moves(board, turn):
            # print_board(board, turn)
            # print 'flips', flips
            #        steps += 1
            #        if steps > 5:
            #            break

            # if turn == black:
            move, mobility = best_move(board, turn, turn)
            # else:
            #    move = coordinates(input())
            if not possible_move(board, move[0], move[1], turn):
                print("impossible!")
                turn = -turn
            else:
                flip_stones(board, move, turn)  # []
        turn = -turn

    # print_board(board, turn)
    # print("flips", flips)  # [str], [int]

    # if stone_count(board, black) == stone_count(board, white):  # [int]
    #     print("draw!")  # [str]
    # else:
    #     if stone_count(board, black) > stone_count(board, white):
    #         print(player[black], "wins!")  # [str], [str]
    #     else:
    #         print(player[white], "wins!")  # [str], [str]
    return flips


def test_flip():
    # assert game() == 6689 # SIZE = 6 
    assert game() == 147 # SIZE = 4


def test_all():
    test_flip()

if __name__ == '__main__':
    test_all() 


