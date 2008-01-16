
# (c) Peter Goodspeed
# --- coriolinus@gmail.com

#import random
from math import exp
#from sets import Set
#set = Set

#functions
def sigmoid(x):
        return float(1)/(1 + exp(-x))

def sig(x, xshift=0, xcompress=1):
        return 0 + (1 * sigmoid(xcompress * (x - xshift)))

#exceptions
class SpaceNotEmpty(Exception):
        pass

class MultiVictory(Exception):
        def __init__(self, victorslist):
                self.victors = victorslist

#classes
class rectBoard(object):
        def __init__(self, edge=3):
                self.edge = edge
                self.__board = [edge * [0] for i in xrange(edge)]
                self.__empty = edge**2

        def assign(self, row, col, value):
                if(self.__board[row][col] == 0):
                        self.__board[row][col] = value
                        self.__empty -= 1
                else:
                        raise SpaceNotEmpty()

        def isfull(self):
                return self.__empty == 0

        #def valueof(self, row, col):
        #        return self.__board[row][col]

        def isvictory(self):
                victors = []
                #examine rows
                for row in self.__board:
                        if len(set(row)) == 1:
                                if row[0] != 0: victors.append(row[0])

                #examine cols
                for i in xrange(self.edge):
                        col = [row[i] for row in self.__board]
                        if len(set(col)) == 1:
                                if col[0] != 0: victors.append(col[0])

                #examine diagonals
                #left diagonal
                ld = []
                for i in xrange(self.edge): ld.append(self.__board[i][i])
                if len(set(ld)) == 1:
                        if ld[0] != 0: victors.append(ld[0])

                #right diagonal
                rd = []
                for i in xrange(self.edge): rd.append(self.__board[i][self.edge-(1+i)])
                if len(set(rd)) == 1:
                        if rd[0] != 0: victors.append(rd[0])

                #return
                if len(victors) == 0:
                        return 0
                if len(set(victors)) > 1:
                        raise MultiVictory(set(victors))
                return victors[0]

        def __str__(self):
                ret = ""
                for row in xrange(self.edge):
                        if row != 0:
                                ret += "\n"
                                for i in xrange(self.edge):
                                        if i != 0: ret += '+'
                                        ret += "---"
                                ret += "\n"
                        ret += " "
                        for col in xrange(self.edge):
                                if col != 0: ret += " | "
                                if self.__board[row][col] == 0: ret += ' '
                                else: ret += str(self.__board[row][col])
                return ret

        def doRow(self, fields, indices, player, scores):
                players = set(fields).difference(set([0]))

                if(len(players) == 1):
                        if list(players)[0] == player:
                                for rown, coln in indices:
                                        scores[rown][coln] += 15 * sig(fields.count(player) / float(self.edge), .5, 10)
                        else:
                                for rown, coln in indices:
                                        scores[rown][coln] += 15 * fields.count(list(players)[0]) / float(self.edge)

        def makeAImove(self, player):
                scores = [self.edge * [0] for i in xrange(self.edge)]

                for rown in xrange(self.edge):
                        row = self.__board[rown]
                        self.doRow(row, [(rown, i) for i in xrange(self.edge)], player, scores)

                for coln in xrange(self.edge):
                        col = [row[coln] for row in self.__board]
                        self.doRow(col, [(i, coln) for i in xrange(self.edge)], player, scores)

                indices = [(i, i) for i in xrange(self.edge)]
                ld = [self.__board[i][i] for i in xrange(self.edge)]
                self.doRow(ld, indices, player, scores)
                #also, because diagonals are just more useful
                for rown, coln in indices:
                        scores[rown][coln] += 1

                #now, we do the same for right diagonals
                indices = [(i, (self.edge - 1) - i) for i in xrange(self.edge)]
                rd = [self.__board[i][(self.edge - 1) - i] for i in xrange(self.edge)]
                self.doRow(rd, indices, player, scores)
                #also, because diagonals are just more useful
                for rown, coln in indices:
                        scores[rown][coln] += 1

                scorelist = []
                for rown in xrange(self.edge):
                        for coln in xrange(self.edge):
                                if(self.__board[rown][coln] == 0):
                                        scorelist.append((scores[rown][coln],(rown,coln)))
                scorelist.sort()
                scorelist.reverse()
                #print scorelist
                scorelist = [x for x in scorelist if x[0] == scorelist[0][0]]

                #return random.choice([(x[1], x[2]) for x in scorelist])

                #scorelist = [(random.random(), x[1],x[2]) for x in scorelist]
                #scorelist.sort()

                return (scorelist[0][1][0], scorelist[0][1][1])


def aigame(size=30, turn=1, players=2):
        b = rectBoard(size)

        while((not b.isfull()) and (b.isvictory() == 0)):
                if(turn==1):
                        #player turn
                        #print
                        #print b
                        r, c = b.makeAImove(turn)
                        b.assign(r,c,1)
                        turn = 2
                else:
                        #computer turn
                        r, c = b.makeAImove(turn)
                        b.assign(r,c,turn)
                        if(turn == players): turn = 1
                        else: turn += 1
        #print
        #print b.__str__()
        #print
        if(b.isvictory() == 0):
                print "Board is full! Draw!"
        else:
                print "Victory for player "+str(b.isvictory())+"!"

aigame()

