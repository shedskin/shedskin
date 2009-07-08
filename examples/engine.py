#!/usr/bin/env python

import sys
import gtp
import pgo
import go

class Engine:
    name = 'Disco'

    def __init__(self):
        self.board = go.Board()

    def boardsize(self, size):
        if int(size) != 9:
            raise 'illegal board size'

    def clear_board(self):
        pass

    def komi(self, value):
        pass

    def play(self, color, vertex):
        vertex = gtp.parse_vertex(vertex)
        if vertex is None:
            return
        i, j = vertex
        pos = go.to_pos(i, j)
        self.board.play_move(pos)

#    def undo(self):
#        pass

    def genmove(self, color):
        options = [pos for pos in self.board.empties if self.board.legal_move(pos) and self.board.useful_move(pos)]
        if not options:
            return 'pass'
        pos = pgo.computer_move(self.board, options)
        self.board.play_move(pos)
        x,y = go.to_xy(pos)
        return gtp.make_vertex(x, y)

#    def showboard(self):
#        pass

def main():
    engine = Engine()
    gtp.run(engine)

if __name__ == '__main__':
    main()
