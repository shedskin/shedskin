''' min-max othello player in 100 lines; copyleft Mark Dufour (GPL3 or later) '''

empty, black, white = 0, 1, -1
board = [[empty for x in range(8)] for y in range(8)]
board[3][3] = board[4][4] = white
board[3][4] = board[4][3] = black
player = {white: 'human', black: 'lalaoth'}
depth = 6
directions = [(1, 1), (-1, 1), (0, 1), (1, -1), (-1, -1), (0, -1), (1, 0), (-1, 0)]
corners = [(0, 0), (0, 7), (7, 0), (7, 7)]

def possible_move(board, x, y, color):
    if board[x][y] != empty:
        return False
    for direction in directions:
        if flip_in_direction(board, x, y, direction, color):
            return True
    return False
        
def flip_in_direction(board, x, y, direction, color):
    other_color = False
    while True:
        x, y = x+direction[0], y+direction[1]
        if x not in list(range(8)) or y not in list(range(8)):
            return False
        square = board[x][y]
        if square == empty: return False
        if square != color: other_color = True
        else: return other_color

def flip_stones(board, move, color):
    for direction in directions:
        if flip_in_direction(board, move[0], move[1], direction, color):
             x, y = move[0]+direction[0], move[1]+direction[1]
             while board[x][y] != color:
               board[x][y] = color
               x, y = x+direction[0], y+direction[1]
    board[move[0]][move[1]] = color

def print_board(board, turn):
    print('  '+' '.join('abcdefgh'))
    for nr, line in enumerate(board):
        print(nr+1, ' '.join([{white: 'O', black: 'X', empty: '.'}[square] for square in line]))
    print('turn:', player[turn])
    print('black:', stone_count(board, black), 'white:', stone_count(board, white))

def possible_moves(board, color):
    return [(x,y) for x in range(8) for y in range(8) if possible_move(board, x, y, color)]
def coordinates(move):
    return (int(move[1])-1, 'abcdefgh'.index(move[0]))
def human_move(move):
    return 'abcdefgh'[move[1]]+str(move[0]+1)
def stone_count(board, color):
    return sum([len([square for square in line if square == color]) for line in board])

def best_move(board, color, first, step=1):
    max_move, max_mobility, max_score = None, 0, 0
    for move in possible_moves(board, color):
        if move in corners:
            mobility, score = 64, 64
            if color != first:
                mobility = 64-mobility
        else:
            testboard = [[square for square in line] for line in board]
            flip_stones(testboard, move, color)
            if step < depth:
                next_move, mobility = best_move(testboard, -color, first, step+1)
            else:
                mobility = len(possible_moves(testboard, first))
            score = mobility
            if color != first:
                score = 64-score
        if score >= max_score:
            max_move, max_mobility, max_score = move, mobility, score
    return max_move, max_mobility
    
if __name__ == '__main__':
    turn = black
    while possible_moves(board, black) or possible_moves(board, white):
        if possible_moves(board, turn):
            print_board(board, turn)
            if turn == black:
                move, mobility = best_move(board, turn, turn)
                print('move:', human_move(move))
            else:
                try: 
                    move = coordinates(input('move? '))
                except ValueError: 
                    print('syntax error')
                    continue
            if not possible_move(board, move[0], move[1], turn):
                print('impossible!')
                continue
            else:
                flip_stones(board, move, turn)
                break # XXX shedskin; remove to play against computer
        turn = -turn
    print_board(board, turn)
    if stone_count(board, black) == stone_count(board, white):
        print('draw!')
    else:
        if stone_count(board, black) > stone_count(board, white): print(player[black], 'wins!')
        else: print(player[white], 'wins!')
