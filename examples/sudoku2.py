# (c) Peter Goodspeed
# --- coriolinus@gmail.com
#
# sudoku solver

from math import ceil
from time import time
import sys

class bmp(object):
        def __init__(self, vals=9*[True], n=-1):
                self.v = vals[0:9]
                if n>=0: self.v[n] = not self.v[n]
        def __and__(self, other):
                return bmp([self.v[i] and other.v[i] for i in xrange(9)])
        def cnt(self):
                return len([i for i in self.v if i])

class boardRep(object):
        def __init__(self, board):
                self.__fields = list(board.final)
        def fields(self):
                return self.__fields
        def __eq__(self, other):
                return self.__fields==other.fields()
        def __ne__(self, other):
                return self.__fields!=other.fields()
        def __hash__(self):
                rep=""
                for i in xrange(9):
                        for j in xrange(9):
                                rep += str(self.__fields[i][j])
                return hash(rep)

class board(object):
        notifyOnCompletion = True               #let the user know when you're done computing a game
        completeSearch = False                  #search past the first solution

        def __init__(self):
                #final numbers: a 9 by 9 grid
                self.final = [9 * [0] for i in xrange(9)]
                self.rows = 9 * [bmp()]
                self.cols = 9 * [bmp()]
                self.cels = [3 * [bmp()] for i in xrange(3)]

                #statistics
                self.__turns = 0
                self.__backtracks = 0
                self.__starttime = 0
                self.__endtime = 0
                self.__status = 0
                self.__maxdepth = 0
                self.__openspaces = 81

                #a set of all solved boards discovered so far
                self.solutions = set()
                #a set of all boards examined--should help reduce the amount of search duplication
                self.examined = set()

        def fread(self,fn=''):
                #self.__init__()
                if fn=='':
                        fn = raw_input("filename: ")
                f = file(fn, 'r')
                lines = f.readlines()
                for row in xrange(9):
                        for digit in xrange(1,10):
                                try:
                                        self.setval(row,lines[row].index(str(digit)),digit)
                                except ValueError:
                                        pass
                f.close()

        def setval(self, row, col, val):
                #add the number to the grid
                self.final[row][col] = val
                self.__openspaces -= 1

                #remove the number from the potential masks
                mask = bmp(n = val - 1)
                #rows and cols
                self.rows[row] = self.rows[row] & mask
                self.cols[col] = self.cols[col] & mask
                #cels
                cr = self.cell(row)
                cc = self.cell(col)
                self.cels[cr][cc] = self.cels[cr][cc] & mask

        def cell(self, num):
                return int(ceil((num + 1) / 3.0)) - 1

        def __str__(self):
                ret = ""
                for row in xrange(9):
                        if row == 3 or row == 6: ret += (((3 * "---") + "+") * 3)[:-1] + "\n"
                        for col in xrange(9):
                                if col == 3 or col == 6: ret += "|"
                                if self.final[row][col]: c = str(self.final[row][col])
                                else: c = " "
                                ret += " "+c+" "
                        ret += "\n"
                return ret

        def solve(self, notify=True, completeSearch=False):
                if self.__status == 0:
                        self.__status = 1
                        self.__starttime = time()
                        board.notifyOnCompletion = notify
                        board.completeSearch = completeSearch
                        self.__solve(self, 0)

        def openspaces(self):
                return self.__openspaces

        def __solve(self, _board, depth):
                global bekos
                bekos += 1
                if bekos == 5000:
                    self.onexit()
                    sys.exit()

                if boardRep(_board) not in self.examined:
                        self.examined.add(boardRep(_board))
            
                        #check for solution condition:
                        if _board.openspaces() <= 0:
                                self.solutions.add(boardRep(_board))
                                print 'sol', _board
                                if depth == 0: self.onexit()
                                if not board.completeSearch:
                                        self.onexit()

                        else:
                                #update the statistics
                                self.__turns += 1
                                if depth > self.__maxdepth: self.__maxdepth = depth

                                #figure out the mincount
                                mincnt, coords = _board.findmincounts()
                                if mincnt <= 0:
                                        self.__backtracks += 1
                                        if depth == 0: self.onexit()
                                else:
                                        #coords is a list of tuples of coordinates with equal, minimal counts
                                        # of possible values. Try each of them in turn.
                                        for row, col in coords:
                                                #now we iterate through possible values to put in there
                                                broken = False
                                                for val in [i for i in xrange(9) if _board.mergemask(row, col).v[i] == True]:
                                                        if not board.completeSearch and self.__status == 2: 
                                                            broken = True
                                                            break
                                                        val += 1
                                                        t = _board.clone()
                                                        t.setval(row, col, val)
                                                        self.__solve(t, depth + 1)
                                                #if we broke out of the previous loop, we also want to break out of
                                                # this one. unfortunately, "break 2" seems to be invalid syntax.
                                                if broken: break
                                                #else: didntBreak = True
                                                #if not didntBreak: break

        def clone(self):
                ret = board()
                for row in xrange(9):
                        for col in xrange(9):
                                if self.final[row][col]:
                                        ret.setval(row, col, self.final[row][col])
                return ret

        def mergemask(self, row, col):
                return self.rows[row] & self.cols[col] & self.cels[self.cell(row)][self.cell(col)]

        def findmincounts(self):
                #compute the list of lenghths of merged masks
                masks = []
                for row in xrange(9):
                        for col in xrange(9):
                                if self.final[row][col] == 0:
                                        numallowed = self.mergemask(row, col).cnt()
                                        masks.append((numallowed, row, col))
                #return the minimum number of allowed moves, and a list of cells which are
                # not currently occupied and which have that number of allowed moves
                return min(masks)[0], [(i[1],i[2]) for i in masks if i[0] == min(masks)[0]]

        def onexit(self):
                self.__endtime = time()
                self.__status = 2

                if board.notifyOnCompletion: print self.stats()['turns']

        def stats(self):
                if self.__status == 1: t = time() - self.__starttime
                else: t = self.__endtime - self.__starttime
                return {'max depth' : self.__maxdepth, 'turns' : self.__turns, 'backtracks' : self.__backtracks, 'elapsed time' : int(t), 'boards examined': len(self.examined), 'number of solutions' : len(self.solutions)}


bekos = 0
puzzle = board()
puzzle.fread('testdata/b6.pz')
#print puzzle
puzzle.solve()

