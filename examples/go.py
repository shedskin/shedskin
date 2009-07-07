import random
import math

SIZE = 7
GAMES = 1000
WHITE, BLACK, EMPTY = 0, 1, 2
SHOW = {EMPTY: '.', WHITE: 'o', BLACK: 'x'}
PASS = -1

def to_pos(x,y):
    return y*SIZE+x

def to_xy(pos):
    y, x = divmod(pos, SIZE)
    return x, y

class Square:
    def __init__(self, board, pos):
        self.board = board
        self.pos = pos
        self.color = EMPTY
        self.group = None
        self.fast_group = Group(board)

    def set_neighbours(self):
        x, y = to_xy(self.pos)
        self.neighbours = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            newx, newy = x+dx, y+dy
            if 0 <= newx < SIZE and 0 <= newy < SIZE:
                self.neighbours.append(self.board.squares[to_pos(newx, newy)])

class Board:
    def __init__(self):
        self.squares = [Square(self, pos) for pos in range(SIZE*SIZE)]
        for square in self.squares:
            square.set_neighbours()
        self.empties = [square.pos for square in self.squares]
        self.color = BLACK
        self.finished = False
        self.lastmove = -2
        self.history = []

    def legal_move(self, pos):
        """ determine if move is legal """
        square = self.squares[pos]
        if square.color != EMPTY:
            return False
        other = 1-self.color
        for neighbour in square.neighbours:
            ncolor = neighbour.color
            if ncolor == EMPTY:
                return True
            elif ncolor == self.color:
                liberties = len(neighbour.group.liberties)
                if liberties >= 2:
                    return True
            elif ncolor == other:
                members = len(neighbour.group.members)
                liberties = len(neighbour.group.liberties)
                if liberties == 1 and not (neighbour.pos == self.lastmove and members == 1):
                    return True
        return False

    def useful_move(self, pos):
        """ determine whether move can be useful """
        square = self.squares[pos]
        buddies = 0
        for neighbour in square.neighbours:
            if neighbour.color == self.color:
                if len(neighbour.group.liberties) == 1:
                    return True
                buddies += 1
        return buddies != len(square.neighbours)

    def random_move(self):
        """ return random, possibly useful move """
        choices = len(self.empties)
        while choices:  
            i = random.randrange(choices)
            pos = self.empties[i]
            if self.legal_move(pos) and self.useful_move(pos):
                last = len(self.empties)-1
                self.empties[i] = self.empties[last] 
                self.empties.pop(last)
                return pos
            choices -= 1
            self.empties[i] = self.empties[choices]
            self.empties[choices] = pos
        return PASS

    def new_group(self, square): # XXX to Group class
        group = square.group = square.fast_group
        group.color = square.color
        group.members.clear()
        group.members.add(square.pos)
        group.liberties.clear()
        for neighbour in square.neighbours:
            if neighbour.color == EMPTY:
                group.liberties.add(neighbour.pos)

    def score(self, color):
        """ score according to chinese rules """ # XXX lookup rules :)
        count = 0
        for square in self.squares:
            if square.color == color:
                count += 1
            elif square.color == EMPTY:
                surround = 0
                for neighbour in square.neighbours:
                    if neighbour.color == color:
                        surround += 1
                if surround == len(square.neighbours): 
                    count += 1
        return count

    def playout(self):
        """ play until finished """
        for x in range(1000): # XXX while not self.finished?
            if self.finished:
                break
            pos = self.random_move()
            self.play_move(pos)

    def play_move(self, pos):
        """ administer move or PASS """
        if pos != PASS:
            self._move(pos, self.color)
        elif self.lastmove == PASS:
            self.finished = True
        self.color = 1-self.color
        self.lastmove = pos
        self.history.append(pos)

    def _move(self, pos, color):
        """ actual move: update groups, empties """
        square = self.squares[pos]
        other = 1-color
        prev_group = None
        for neighbour in square.neighbours:
            group = neighbour.group
            if neighbour.color == color:
                if square.pos in group.liberties:
                    group.liberties.remove(square.pos)
                if prev_group:
                    if prev_group != group:
                        group.add_group(prev_group)
                else:
                    group.add_stone(square)
                prev_group = group
            if neighbour.color == other:
                group.take_liberty(square)
        square.color = color
        if not prev_group:
            self.new_group(square)
        self.empties = [e for e in self.empties if e != pos] # XXX set?

    def replay(self, history):
        """ replay steps """
        for pos in history:
            self.play_move(pos)

    def __repr__(self):
        result = []
        for y in range(SIZE):
            start = to_pos(0, y)
            result.append(''.join([SHOW[square.color]+' ' for square in self.squares[start:start+SIZE]]))
        result.append('W %d B %d (%s)' % (self.score(WHITE), self.score(BLACK), SHOW[self.color]))
        return '\n'.join(result)

class Group:
    def __init__(self, board):
        self.board = board
        self.color = -1
        self.members = set()
        self.liberties = set()

    def take_liberty(self, square):
        if square.pos in self.liberties:
            self.liberties.remove(square.pos)
        if not self.liberties: 
            other = 1-self.color
            self.board.empties.extend(self.members)
            for pos in self.members:
                square = self.board.squares[pos]
                square.color = EMPTY
                for neighbour in square.neighbours:
                    if neighbour.color == other:
                        neighbour.group.liberties.add(pos)

    def add_stone(self, square):
        self.members.add(square.pos)
        square.group = self
        for neighbour in square.neighbours:
            if neighbour.color == EMPTY:
                self.liberties.add(neighbour.pos)
        
    def add_group(self, group):
        for pos in group.members:
            self.board.squares[pos].group = self
        self.members.update(group.members)
        self.liberties.update(group.liberties)

class UCTNode:
    def __init__(self):
        self.bestchild = None
        self.pos = -1
        self.wins = 0
        self.losses = 0
        self.pos_child = [None for x in range(SIZE*SIZE)]
        self.parent = None

    def play(self, board):
        color = board.color

        steps = []
        node = self
        while True:
            if node.bestchild and random.random() < 0.2:
                pos = node.bestchild.pos
            else:
                pos = board.random_move() # XXX geen move mogelijk?
            board.play_move(pos)

            child = node.pos_child[pos]
            if not child:
                child = node.pos_child[pos] = UCTNode()
                child.pos = pos
                child.parent = self
                steps.append(child)
                break

            steps.append(child)
            node = child

        board.playout()

        wins = board.score(BLACK) >= board.score(WHITE)
        for child in steps:
            if wins:
                if color == BLACK:
                    child.wins += 1
                else:
                    child.losses += 1
            else:
                if color == WHITE:
                    child.wins += 1
                else:
                    child.losses += 1

            child.parent.bestchild = child.parent.best_child()
            color = 1-color

    def score(self):
        winrate = self.wins/float(self.wins+self.losses)
        parentvisits = self.parent.wins+self.parent.losses
        if not parentvisits:
            return winrate
        nodevisits = self.wins+self.losses
        return winrate + math.sqrt((math.log(parentvisits))/(nodevisits))/2

    def best_child(self, hoppa=False):
        maxscore = -1
        maxchild = None
        maxpos = -1
        for pos, child in enumerate(self.pos_child):
            if child: # and (child.wins or child.losses):
#                if hoppa:
#                    print 'child!', to_xy(pos), child.wins, child.losses, child.score()
                if child.score() > maxscore:
                    maxchild = child
                    maxscore = child.score()
                    maxpos = pos
        return maxchild

def user_move(board):
    while True:
        text = raw_input('?').strip()
        if text == 'p':
            return PASS
        if text == 'q':
            raise EOFError
        try:
            x, y = [int(i) for i in text.split()]
        except ValueError:
            continue
        if not (0 <= x < SIZE and 0 <= y < SIZE):
            continue
        pos = to_pos(x, y)
        if board.legal_move(pos):
            return pos

def computer_move(board):
    pos = board.random_move()
    if pos == PASS:
        return PASS
    history = board.history[:]
    tree = UCTNode()
    for game in range(GAMES):
        node = tree
        nboard = Board()
        nboard.replay(history)
        #print 'SET STATE:'
        #print nboard
        node.play(nboard)
    best = tree.best_child(hoppa=True)
#        print 'best one', best, best.wins, best.losses, best.score(), to_xy(best.pos)
    return best.pos

def versus_cpu():
    board = Board()
    while True:
        if board.lastmove != PASS:
            print board
        print 'thinking..'
        pos = computer_move(board)
        if pos == PASS:
            print 'I pass.'
        else:
            print 'I move here:', to_xy(pos)
        board.play_move(pos)
        if board.finished:
            break
        if board.lastmove != PASS:
            print board
        pos = user_move(board)
        board.play_move(pos)
        if board.finished:
            break
    print 'WHITE:', board.score(WHITE)
    print 'BLACK:', board.score(BLACK)

if __name__ == '__main__':
    random.seed(1)
    try:
        versus_cpu()
    except EOFError:
        pass
