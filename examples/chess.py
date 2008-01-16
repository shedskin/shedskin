
# This is an extremely simple chess like speed test program written in Python
# This program can be distributed under GNU General Public License Version 2.
# (C) Jyrki Alakuijala 2005
#
# Despite its looks, this program was written in Python, not converted to it.
# This program is incomplete, castlings, enpassant situation etc. are not properly implemented
# game ending is not recognized. The evaluator as simple as it ever could be. 
#
# The board is an 160-element array of ints, Nones and Booleans,
# The board contains the real board in squares indexed in variable 'squares'
# The oversized board is to allow for "0x88" chess programming trick for move generation.
# Other board data:
# 4x castling flags, indices [10-13], queen side white, king side white, queen side black, king side white
# turn, enpassant [26, 27]

from copy import copy

iNone = -999
iTrue = 1
iFalse = 0

setup = (4, 2, 3, 5, 6, 3, 2, 4, iNone, iNone) + (True,)*4 + (iNone, iNone) +   (1,) * 8 + (iNone, iNone, True, iNone, iNone, iNone, iNone, iNone,) +   ((0, ) * 8 + (iNone,) * 8) * 4 +   (-1,) * 8 + (iNone,) * 8 +   (-4, -2, -3, -5, -6, -3, -2, -4) + (iNone,) * 40

squares = tuple([i for i in range(128) if not i & 8])
knightMoves = (-33, -31, -18, -14, 14, 18, 31, 33)
bishopLines = (tuple(range(17, 120, 17)), tuple(range(-17, -120, -17)), tuple(range(15, 106, 15)), tuple(range(-15, -106, -15)))
rookLines = (tuple(range(1, 8)), tuple(range(-1, -8, -1)), tuple(range(16, 128, 16)), tuple(range(-16, -128, -16)))
queenLines = bishopLines + rookLines
kingMoves = (-17, -16, -15, -1, 1, 15, 16, 17)

linePieces = ((), (), (), bishopLines, rookLines, queenLines, (), (), queenLines, rookLines, bishopLines, (), ())

clearCastlingOpportunities = [None] * 0x80
for (i, v) in ((0x0, (10,)), (0x4, (10, 11)), (0x7, (11,)), (0x70, (12,)), (0x74, (12, 13)), (0x77, (13,))):
  clearCastlingOpportunities[i] = v

pieces = ".pnbrqkKQRBNP"

def evaluate(board):
  evals = (0, 100, 300, 330, 510, 950, 100000, -100000, -950, -510, -330, -300, -100)
  return sum([evals[board[i]] for i in squares])

def printBoard(board):
  for i in range(7,-1,-1):
    for j in range(8):
      ix = i * 16 + j
      print pieces[board[ix]],
    print

def move(board, mv):
  ix = (mv >> 8) & 0xff
  board[mv & 0xff] = board[ix]
  board[ix] = 0
  if clearCastlingOpportunities[ix]:
    for i in clearCastlingOpportunities[ix]:
      board[i] = False

  board[26] = not board[26] # Turn
  if (mv & 0x7fff0000) == 0:
    return
  if (mv & 0x01000000): # double step
    board[27] = mv & 7
  else:
    board[27] = iNone # no enpassant
  if (mv & 0x04000000): # castling
    toix = mv & 0xff
    if toix == 0x02:
      board[0x00] = 0
      board[0x03] = 4
    elif toix == 0x06:
      board[0x07] = 0
      board[0x05] = 4
    elif toix == 0x72:
      board[0x70] = 0
      board[0x73] = -4
    elif toix == 0x76:
      board[0x77] = 0
      board[0x75] = -4
    else:
      raise "faulty castling"
  if mv & 0x08000000: # enpassant capture
    if board[26]: # turn after this move
      board[mv & 0x07 + 64] = 0
    else:
      board[mv & 0x07 + 48] = 0
  if mv & 0x10000000: # promotion
    a = (mv & 0xff0000) >> 16
    if (a >= 0x80):
      a = a - 0x100 
    board[mv & 0xff] = a

def toString(move):
  fr = (move >> 8) & 0xff
  to = move & 0xff
  letters = "abcdefgh"
  numbers = "12345678"
  mid = "-"
  if (move & 0x04000000):
    if (move & 0x7) == 0x02:
      return "O-O-O"
    else:
      return "O-O"
  if move & 0x02000000:
    mid = "x"
  retval = letters[fr & 7] + numbers[fr >> 4] + mid + letters[to & 7] + numbers[to >> 4]
  return retval

def moveStr(board, strMove):
  moves = pseudoLegalMoves(board)
  for m in moves:
    if strMove == toString(m):
      move(board, m)
      return
  for m in moves:
    print toString(m)
  raise "no move found", strMove

def rowAttack(board, attackers, ix, dir):
  own = attackers[0]
  for k in [i + ix for i in dir]:
    if k & 0x88:
      return False
    if board[k]:
      return (board[k] * own < 0) and board[k] in attackers

def nonpawnAttacks(board, ix, color):
  return (max([board[ix + i] == color * 2 for i in knightMoves]) or 
          max([rowAttack(board, (color * 3, color * 5), ix, bishopLine) for bishopLine in bishopLines]) or
          max([rowAttack(board, (color * 4, color * 5), ix, rookLine) for rookLine in rookLines]))

nonpawnBlackAttacks = lambda board, ix: nonpawnAttacks(board, ix, -1)
nonpawnWhiteAttacks = lambda board, ix: nonpawnAttacks(board, ix, 1)

def pseudoLegalMovesWhite(board):
  retval = pseudoLegalCapturesWhite(board)
  for sq in squares:
    b = board[sq]
    if b >= 1:
      if b == 1 and not (sq + 16 & 0x88) and board[sq + 16] == 0:
        if sq >= 16 and sq < 32 and board[sq + 32] == 0:
          retval.append(sq * 0x101 + 32)
        retval.append(sq * 0x101 + 16)
      elif b == 2:
        for k in knightMoves:
          if board[k + sq] == 0:
            retval.append(sq * 0x101 + k)
      elif b == 3 or b == 5:
        for line in bishopLines:
          for k in line:
            if (k + sq & 0x88) or board[k + sq] != 0:
              break
            retval.append(sq * 0x101 + k)
      if b == 4 or b == 5:
        for line in rookLines:
          for k in line:
            if (k + sq & 0x88) or board[k + sq] != 0:
              break
            retval.append(sq * 0x101 + k)
      elif b == 6:
        for k in kingMoves:
          if not (k + sq & 0x88) and board[k + sq] == 0:
            retval.append(sq * 0x101 + k)
  if (board[10] and board[1] == 0 and board[2] == 0 and board[3] == 0 and
      not -1 in board[17:22] and
      not nonpawnBlackAttacks(board, 2) and not nonpawnBlackAttacks(board, 3) and not nonpawnBlackAttacks(board, 4)):
    retval.append(0x04000000 + 4 * 0x101 - 2)
  if (board[11] and board[5] == 0 and board[6] == 0 and
      not -1 in board[19:24] and
      not nonpawnBlackAttacks(board, 4) and not nonpawnBlackAttacks(board, 5) and not nonpawnBlackAttacks(board, 6)):
    retval.append(0x04000000 + 4 * 0x101 + 2)
  return retval

def pseudoLegalMovesBlack(board):
  retval = pseudoLegalCapturesBlack(board)
  for sq in squares:
    b = board[sq]
    if b < 0:
      if b == -1 and not (sq + 16 & 0x88) and board[sq - 16] == 0:
        if sq >= 96 and sq < 112 and board[sq - 32] == 0:
          retval.append(sq * 0x101 - 32)
        retval.append(sq * 0x101 - 16)
      elif b == -2:
        for k in knightMoves:
          if board[k + sq] == 0:
            retval.append(sq * 0x101 + k)
      elif b == -3 or b == -5: 
        for line in bishopLines:
          for k in line:
            if (k + sq & 0x88) or board[k + sq] != 0:
              break
            retval.append(sq * 0x101 + k)

      if b == -4 or b == -5:
        for line in rookLines:
          for k in line:
            if (k + sq & 0x88) or board[k + sq] != 0:
              break
            retval.append(sq * 0x101 + k)
      elif b == -6: 
        for k in kingMoves:
          if not (k + sq & 0x88) and board[k + sq] == 0:
            retval.append(sq * 0x101 + k)
  if (board[12] and board[0x71] == 0 and board[0x72] == 0 and board[0x73] == 0 and
      not 1 in board[0x61:0x65] and
      not nonpawnWhiteAttacks(board, 0x72) and not nonpawnWhiteAttacks(board, 0x73) and not nonpawnWhiteAttacks(board, 0x74)):
    retval.append(0x04000000 + 0x74 * 0x101 - 2)
  if (board[11] and board[0x75] == 0 and board[0x76] == 0 and
      not -1 in board[0x63:0x68] and
      not nonpawnWhiteAttacks(board, 0x74) and not nonpawnWhiteAttacks(board, 0x75) and not nonpawnWhiteAttacks(board, 0x76)):
    retval.append(0x04000000 + 0x74 * 0x101 + 2)
  return retval

def pseudoLegalMoves(board):
  if board[26]:
    return pseudoLegalMovesWhite(board)
  else:
    return pseudoLegalMovesBlack(board)

def pseudoLegalCapturesWhite(board):
  retval = []
  for sq in squares:
    b = board[sq]
    if b >= 1:
      if b == 1: 
        if not (sq + 17 & 0x88) and board[sq + 17] < 0:
          retval.append(0x02000000 + sq * 0x101 + 17)
        if not (sq + 15 & 0x88) and board[sq + 15] < 0:
          retval.append(0x02000000 + sq * 0x101 + 15)
        if sq >= 64 and sq < 72 and abs((sq & 7) - board[27]) == 1: # enpassant
          retval.append(0x02000000 + sq * 0x100 + (sq & 0x70) + 16 + board[27])
      elif b == 2:
        for k in knightMoves:
          if not (sq + k & 0x88) and board[k + sq] < 0:
            retval.append(0x02000000 + sq * 0x101 + k)
      elif b == 6:
        for k in kingMoves:
          if not(k + sq & 0x88) and board[k + sq] < 0:
            retval.append(0x02000000 + sq * 0x101 + k)
      else:
        for line in linePieces[b]:
          for k in line:
            if (sq + k & 0x88) or board[k + sq] >= 1:
              break
            if board[k + sq] < 0:
              retval.append(0x02000000 + sq * 0x101 + k)
              break
  return retval

def pseudoLegalCapturesBlack(board):
  retval = []
  for sq in squares:
    b = board[sq]
    if b < 0:
      if b == -1: 
        if board[sq - 17] >= 1:
          retval.append(0x02000000 + sq * 0x101 - 17)
        if board[sq - 15] >= 1:
          retval.append(0x02000000 + sq * 0x101 - 15)
        if sq >= 48 and sq < 56 and abs((sq & 7) - board[27]) == 1: # enpassant
          retval.append(0x0a000000 + sq * 0x100 + (sq & 0x70) - 16 + board[27])
      elif b == -2:
        for k in knightMoves:
          if not (sq + k & 0x88) and board[k + sq] >= 1:
            retval.append(0x02000000 + sq * 0x101 + k)
      elif b == -3:
        for line in bishopLines:
          for k in line:
            if board[k + sq] < 0:
              break
            if board[k + sq] >= 1:
              retval.append(0x02000000 + sq * 0x101 + k)
              break
      elif b == -4:
        for line in rookLines:
          for k in line:
            if board[k + sq] < 0:
              break
            if board[k + sq] >= 1:
              retval.append(0x02000000 + sq * 0x101 + k)
              break
      elif b == -5:
        for line in queenLines:
          for k in line:
            if board[k + sq] < 0:
              break
            if board[k + sq] >= 1:
              retval.append(0x02000000 + sq * 0x101 + k)
              break
      elif b == -6:
        for k in kingMoves:
          if board[k + sq] >= 1:
            retval.append(0x02000000 + sq * 0x101 + k)
  return retval

def pseudoLegalCaptures(board):
  if board[26]:
    return pseudoLegalCapturesWhite(board)
  else:
    return pseudoLegalCapturesBlack(board)

def legalMoves(board):
  allMoves = pseudoLegalMoves(board)
  retval = []
  #from copy import copy
  kingVal = 6
  if board[26]:
    kingVal = -kingVal
  for mv in allMoves:
    board2 = copy(board)
    move(board2, mv)
    #print "trying to reduce move", toString(mv)
    if not [i for i in pseudoLegalCaptures(board2) if board2[i & 0xff] == kingVal]:
      retval.append(mv)
  return retval

def alphaBetaQui(board, alpha, beta, n):
  e = evaluate(board)
  if not board[26]:
    e = -e
  if e >= beta:
    return (beta, iNone) # XXX
  if (e > alpha): 
    alpha = e
  bestMove = iNone # XXX
  if n >= -4:
    #from copy import copy
    for mv in pseudoLegalCaptures(board):
      newboard = copy(board)
      move(newboard, mv)
      value = alphaBetaQui(newboard, -beta, -alpha, n - 1)
      value = (-value[0], value[1])
      if value[0] >= beta:
        return (beta, mv)
      if (value[0] > alpha):
        alpha = value[0]
        bestMove = mv
  return (alpha, bestMove)

def alphaBeta(board, alpha, beta, n):
  if n == 0:
    return alphaBetaQui(board, alpha, beta, n)
#  from copy import copy
  bestMove = iNone # XXX

  for mv in legalMoves(board):
    newboard = copy(board)
    move(newboard, mv)
    value = alphaBeta(newboard, -beta, -alpha, n - 1)
    value = (-value[0], value[1])
    if value[0] >= beta:
      return (beta, mv)
    if (value[0] > alpha):
      alpha = value[0]
      bestMove = mv
  return (alpha, bestMove)

def speedTest():
  board = list(setup)
  moveStr(board, "c2-c4")
  moveStr(board, "e7-e5")
  moveStr(board, "d2-d4")

  res = alphaBeta(board, -99999999, 99999999, 4)
  print res
  moveStr(board, "d7-d6")
  res = alphaBeta(board, -99999999, 99999999, 4)
  print res

speedTest()

