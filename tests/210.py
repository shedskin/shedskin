# -*- coding: utf-8 -*-
from __future__ import print_function

# unicode

# encode/decode
ss = u'\u91cf\u5b50\u529b\u5b66'
print(repr(ss), ss)
t = ss.encode('utf-8')
print(repr(t), t)
u = t.decode('utf-8')
print(repr(u), u)
l = [ss, u]
print(l)
print(repr(ss[1]))  #, s[1]
print(len(ss))

# char cache
initial = (
    '         \n'  #   0 -  9
    '         \n'  #  10 - 19
    ' rnbqkbnr\n'  #  20 - 29
    ' pppppppp\n'  #  30 - 39
    ' ........\n'  #  40 - 49
    ' ........\n'  #  50 - 59
    ' ........\n'  #  60 - 69
    ' ........\n'  #  70 - 79
    ' PPPPPPPP\n'  #  80 - 89
    ' RNBQKBNR\n'  #  90 - 99
    '         \n'  # 100 -109
    '         \n'  # 110 -119
)

def print_pos(board):
    print()
    uni_pieces = {'R':u'♜', 'N':u'♞', 'B':u'♝', 'Q':u'♛', 'K':u'♚', 'P':u'♟',
                  'r':u'♖', 'n':u'♘', 'b':u'♗', 'q':u'♕', 'k':u'♔', 'p':u'♙', '.':u'·'}

    for k in sorted(uni_pieces):
        print(k, uni_pieces[k])

print_pos(initial)
