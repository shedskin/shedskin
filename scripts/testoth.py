import os

os.system('rm othello.so')
os.system('shedskin -e othello && make')

import othello
assert othello.__file__.split('/')[-1] == 'othello.so'

board = othello.board
white, black = othello.white, othello.black

assert len(board) == 8

assert othello.stone_count(board, black) == 2
assert othello.stone_count(board, white) == 2

assert set(othello.possible_moves(board, black)) == set([(2,3),(3,2),(4,5),(5,4)])
assert set(othello.possible_moves(board, white)) == set([(2,4),(4,2),(3,5),(5,3)])

print othello.best_move(board, black, black)

assert othello.possible_move(board, 5, 4, black)
print othello.flip_stones(board, (5,4), black)

