#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 Francesco Frassinelli <fraph24@gmail.com>
#
#    pylife is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Implementation of: http://en.wikipedia.org/wiki/Conway's_Game_of_Life 
        Tested on Python 2.6.4 and Python 3.1.1 """

from collections import defaultdict
from itertools import product
from sys import argv

def add(board, pos):
    """ Adds eight cells near current cell """
    row, column = pos
    return \
        board[row-1, column-1] +\
        board[row-1, column] +\
        board[row-1, column+1] +\
        board[row, column-1] +\
        board[row, column+1] +\
        board[row+1, column-1] +\
        board[row+1, column] +\
        board[row+1, column+1]

def snext(board):
    """ Calculates the next stage """
    new = defaultdict(int, board)
    for pos in list(board.keys()):
        near = add(board, pos)
        item = board[pos]
        if near not in (2, 3) and item:
            new[pos] = 0
        elif near == 3 and not item:
            new[pos] = 1
    return new

def process(board):
    """ Finds if this board repeats itself """
    history = [defaultdict(None, board)]
    while 1:
        board = snext(board)
        if board in history:
            if board == history[0]:
                return board
            return None
        history.append(defaultdict(None, board))

def generator(rows, columns):
    """ Generates a board """
    ppos = [(row, column) for row in range(rows)
                          for column in range(columns)]
    possibilities = product((0, 1), repeat=rows*columns)
    for case in possibilities:
        board = defaultdict(int)
        for pos, value in zip(ppos, case):
            board[pos] = value
        yield board

def bruteforce(rows, columns):
    global count
    count = 0
    for board in map(process, generator(rows, columns)):
        if board is not None:
            count += 1
            #print board

if __name__ == "__main__":
    rows, columns = 4, 3
    bruteforce(rows, columns)
    print(count)
#    try:
#        rows, columns = int(argv[1]), int(argv[2])
#    except IndexError:
#        print("Usage: %s [rows] [columns]" % argv[0])
#    except ValueError:
#        print("Usage: %s [rows] [columns]" % argv[0])
#    else:
#        bruteforce(rows, columns)
