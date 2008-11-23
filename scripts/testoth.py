import os
import sys

if sys.platform == 'win32': ext = '.pyd'
else: ext = '.so'

os.system('rm othello'+ext)
os.system('shedskin -e othello && make')

import othello
print othello.__file__
assert othello.__file__.split(os.sep)[-1] == 'othello'+ext

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

