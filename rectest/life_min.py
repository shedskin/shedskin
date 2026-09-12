from collections import defaultdict

def snext(board):
    new = defaultdict(int)
    new[0, 0] = 0
    return new

board = defaultdict(int)
for pos, value in [((0, 0), 0)]:
    board[pos] = 0
board = snext(board)
