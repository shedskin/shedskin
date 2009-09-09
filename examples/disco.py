#!/usr/bin/env python

import sys
import gtp
import go

class Engine:
    name = 'Disco'

    def __init__(self):
        self.board = go.Board()

    def boardsize(self, size):
        if int(size) != go.SIZE:
            raise 'illegal board size'

    def clear_board(self):
        self.board = go.Board()

    def komi(self, value):
        pass

    def play(self, color, vertex):
        vertex = gtp.parse_vertex(vertex)
        if vertex is None:
            self.board.move(go.PASS)
        else:
            i, j = vertex
            pos = go.to_pos(i, j)
            self.board.move(pos)

#    def undo(self):
#        pass

    def genmove(self, color):
        pos = go.computer_move(self.board)
        self.board.move(pos)
        if pos == go.PASS:
            return 'pass'
        x, y = go.to_xy(pos)
        return gtp.make_vertex(x, y)

    def final_score(self):
        black = self.board.score(go.BLACK)
        white = self.board.score(go.WHITE)
        if black >= white:
            return 'B+%.1f' % (black-white)
        else:
            return 'W+%.1f' % (white-black)

#    def showboard(self):
#        pass

def main():
    engine = Engine()
    gtp.run(engine)

if __name__ == '__main__':
    main()
