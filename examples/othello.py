# (c) Mark Dufour, Haifang Ni
# --- mark.dufour@gmail.com
#
# min-max othello player 

empty, black, white = 0, 1, -1           # [int], [int], [int]

board = [[empty for x in range(8)] for y in range(8)] # [list(list(int))]
board[3][3] = board[4][4] = white        # [int]
board[3][4] = board[4][3] = black        # [int]

player, depth = {white: 'human', black: 'lalaoth'}, 3 # [dict(int, str)], [int]

def possible_move(board, x, y, color):   # board: [list(list(int))], x: [int], y: [int], color: [int]
    if board[x][y] != empty:             # [int]
        return False                     # [int]
    for direction in [(1, 1), (-1, 1), (0, 1), (1, -1), (-1, -1), (0, -1), (1, 0), (-1, 0)]: # [list(tuple2(int, int))]
        if flip_in_direction(board, x, y, direction, color): # [int]
            return True                  # [int]
    return False                         # [int]
        
def flip_in_direction(board, x, y, direction, color): # board: [list(list(int))], x: [int], y: [int], direction: [tuple2(int, int)], color: [int]
    other_color = False                  # [int]
    while True:                          # [int]
        x, y = x+direction[0], y+direction[1] # [int], [int]
        if x not in range(8) or y not in range(8): # [int]
            return False                 # [int]
        square = board[x][y]             # [int]
        if square == empty: return False # [int]
        if square != color: other_color = True # [int]
        else: return other_color         # [int]

def flip_stones(board, move, color):     # board: [list(list(int))], move: [tuple2(int, int)], color: [int]*
    global flips
    flips += 1                           # [int]
    for direction in [(1, 1), (-1, 1), (0, 1), (1, -1), (-1, -1), (0, -1), (1, 0), (-1, 0)]: # [list(tuple2(int, int))]
        if flip_in_direction(board, move[0], move[1], direction, color): # [int]
             x, y = move[0]+direction[0], move[1]+direction[1] # [int], [int]
             while board[x][y] != color: # [int]
               board[x][y] = color       # [int]
               x, y = x+direction[0], y+direction[1] # [int], [int]
    board[move[0]][move[1]] = color      # [int]

#def print_board(board, turn):            # board: [], turn: []
#    for line in board:                   # []
#        print ' '.join([{white: 'O', black: 'X', empty: '.'}[square] for square in line]) # []
#    print 'turn:', player[turn]          # [], []
#    print 'black:', stone_count(board, black), 'white:', stone_count(board, white) # [], [], [], []

def possible_moves(board, color):        # board: [list(list(int))], color: [int]
    return [(x,y) for x in range(8) for y in range(8) if possible_move(board, x, y, color)] # [list(tuple2(int, int))]
#def coordinates(move):                   # move: []
#    return (int(move[1])-1, 'abcdefgh'.index(move[0])) # []
def stone_count(board, color):           # board: [list(list(int))], color: [int]
    return sum([len([square for square in line if square == color]) for line in board]) # [list(int)]
#def human_move(move):                    # move: []
#    return 'abcdefgh'[move[0]]+str(move[1]+1) # []

def best_move(board, color, first, step=1): # board: [list(list(int))], color: [int]*, first: [int], step: [int]
    max_move, max_mobility, max_score = None, 0, 0 # [none], [int], [int]
    #print 'possible', possible_moves(board, color) # [str], [list(tuple2(int, int))]

    for move in possible_moves(board, color): # [list(tuple2(int, int))]
        #print 'board before'             # [str]
        #print_board(board, color)        # []

        #print 'move', move               # [str], [tuple2(int, int)]
        if move in [(0,0),(0,7),(7,0),(7,7)]:      # [list(tuple2(int, int))]
            mobility, score = 64, 64     # [int], [int]
            if color != first:           # [int]
                mobility = 64-mobility   # [int]
        else:
            testboard = [[square for square in line] for line in board] # [list(list(int))]
            flip_stones(testboard, move, color) # []
            #print_board(testboard, color) # []

            if step < depth:             # [int]
                #print 'deeper'           # [str]
                next_move, mobility = best_move(testboard, -color, first, step+1) # [tuple2(tuple2(int, int), int)]
            else:
                #print 'mobility'         # [str]
                mobility = len(possible_moves(testboard, first)) # [int]
            score = mobility             # [int]
            if color != first:           # [int]
                score = 64-score         # [int]
        if score >= max_score:           # []
            max_move, max_mobility, max_score = move, mobility, score # [tuple2(int, int)], [int], [int]

    #print 'done'                         # [str]
    return max_move, max_mobility        # [tuple2(tuple2(int, int), int)]
    
flips = 0                                # [int]
steps = 0                                # [int]
turn = black                             # [int]
while possible_moves(board, black) or possible_moves(board, white): # [list(tuple2(int, int))]
    if possible_moves(board, turn):      # [list(tuple2(int, int))]
        #print_board(board, turn)         # []
        #print 'flips', flips             # [str], [int]
#        steps += 1                       # [int]
#        if steps > 5:                    # [int]
#            break

        #if turn == black:                # [int]
        move, mobility = best_move(board, turn, turn) # [tuple2(tuple2(int, int), int)]
        #else:
        #    move = coordinates(raw_input()) # [tuple2(int, int)]
        if not possible_move(board, move[0], move[1], turn): # [int]
            print 'impossible!'          # [str]
            turn = -turn                 # [int]
        else:
            flip_stones(board, move, turn) # []
    turn = -turn                         # [int]

#print_board(board, turn)
print 'flips', flips                     # [str], [int]

if stone_count(board, black) == stone_count(board, white): # [int]
    print 'draw!'                        # [str]
else:
    if stone_count(board, black) > stone_count(board, white): print player[black], 'wins!' # [str], [str]
    else: print player[white], 'wins!'   # [str], [str]

