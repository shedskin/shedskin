import random
import math

SIZE = 9
GAMES = 10000
KOMI = 7.5
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
        x, y = self.pos % SIZE, self.pos / SIZE;
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
        self.empties = range(SIZE*SIZE)
        self.empty_pos = range(SIZE*SIZE)
        self.color = BLACK
        self.finished = False
        self.lastmove = -2
        self.history = []
        self.white_dead = 0
        self.black_dead = 0

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
                return pos
            choices -= 1
            self.set_empty(i, self.empties[choices])
            self.set_empty(choices, pos)
        return PASS
  
    def possible_moves(self):
        """ legal and useful moves """
        return [pos for pos in self.empties if self.legal_move(pos) and self.useful_move(pos)]

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
        """ score according to chinese rules (area, instead of territory) """ 
        if color == WHITE:
            count = KOMI + self.black_dead
        else:
            count = self.white_dead
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
        """ actual move: update groups, empties, remove captives """
        square = self.squares[pos]
        other = 1-color
        # connect to surrounding stones
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

        # fill in square
        square.color = color
        self.remove_empty(pos)
        if not prev_group:
            self.new_group(square)

        # remove captives
        for neighbour in square.neighbours:
            if neighbour.color == other:
                neighbour.group.take_liberty(square)

    def add_empty(self, pos):
        self.empty_pos[pos] = len(self.empties)
        self.empties.append(pos)

    def remove_empty(self, pos):
        self.set_empty(self.empty_pos[pos], self.empties[len(self.empties)-1])
        self.empties.pop()

    def set_empty(self, i, pos): 
        self.empties[i] = pos
        self.empty_pos[pos] = i

    def replay(self, history):
        """ replay steps """
        for pos in history:
            self.play_move(pos)

    def __repr__(self):
        result = []
        for y in range(SIZE):
            start = to_pos(0, y)
            result.append(''.join([SHOW[square.color]+' ' for square in self.squares[start:start+SIZE]]))
        result.append('W %s B %s (%s)' % (self.score(WHITE), self.score(BLACK), SHOW[self.color]))
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
            for member in self.members:
                self.board.add_empty(member)
            if self.color == BLACK:
                self.board.black_dead += len(self.members)
            else:
                self.board.white_dead += len(self.members)
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

    def play(self, board, options=None):
        """ uct tree search """
        color = board.color
        node = self
        path = [node]
        while True:
            pos = node.select(board)
            if pos == PASS:
                break
            board.play_move(pos)

            child = node.pos_child[pos]
            if not child:
                child = node.pos_child[pos] = UCTNode()
                child.unexplored = board.possible_moves()
                child.pos = pos
                child.parent = node
                path.append(child)
                break

            path.append(child)
            node = child

        self.random_playout(board)
        self.update_path(board, color, path)

    def select(self, board):
        """ select move; unexplored children first, then according to uct value """
        if self.unexplored:
            i = random.randrange(len(self.unexplored))
            pos = self.unexplored[i]
            self.unexplored[i] = self.unexplored[len(self.unexplored)-1]
            self.unexplored.pop()
            return pos
        elif self.bestchild:
            return self.bestchild.pos
        else:
            return PASS

    def random_playout(self, board):
        """ random play until both players pass """
        for x in range(1000): # XXX while not self.finished?
            if board.finished:
                break
#            print 'checking'
#            for i, pos in enumerate(board.empties):
#                if board.empty_pos[pos] != i:
#                    print 'FOUT %d staat op %d, maar volgens empty_pos op %d' % (pos, i, board.empty_pos[pos])
#                    import sys
#                    sys.exit()
            pos = board.random_move()
            board.play_move(pos)

    def update_path(self, board, color, path):
        """ update win/loss count along path """
        global treedepth
        treedepth = max(treedepth, len(path))
        wins = board.score(BLACK) >= board.score(WHITE)
        for node in path:
            color = 1-color
            if wins == (color == BLACK):
                node.wins += 1
            else:
                node.losses += 1
            if node.parent:
                node.parent.bestchild = node.parent.best_child()

    def score(self):
        winrate = self.wins/float(self.wins+self.losses)
        parentvisits = self.parent.wins+self.parent.losses
        if not parentvisits:
            return winrate
        nodevisits = self.wins+self.losses
        return winrate + math.sqrt((math.log(parentvisits))/(5*nodevisits))

    def best_child(self):
        maxscore = -1
        maxchild = None
        for child in self.pos_child:
            if child and child.score() > maxscore:
                maxchild = child
                maxscore = child.score()
        return maxchild

    def best_visited(self):
        maxvisits = -1
        maxchild = None
        for child in self.pos_child:
#            if child:
#                print to_xy(child.pos), child.wins, child.losses, child.score()
            if child and (child.wins+child.losses) > maxvisits:
                maxvisits, maxchild = (child.wins+child.losses), child
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
    global treedepth
    treedepth = 0
    pos = board.random_move()
    if pos == PASS:
        return PASS
    history = board.history[:]
    tree = UCTNode()
    tree.unexplored = board.possible_moves()
    for game in range(GAMES):
        node = tree
        nboard = Board()
        nboard.replay(history)
        node.play(nboard)
    return tree.best_visited().pos

def pgo(history, options):
    tree = UCTNode()
    tree.unexplored = options
    for game in range(GAMES):
        node = tree
        nboard = Board()
        nboard.replay(history)
        node.play(nboard, options)
    best = tree.best_visited()
    return best.pos, (best.wins+best.losses)

def versus_cpu():
    board = Board()
    while True:
        if board.lastmove != PASS:
            print board
        print 'thinking..'
        pos = computer_move(board)
        print 'tree depth:', treedepth
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

if False: # type model for extmod
    pgo([1], [1])
    UCTNode().play(None, [1])

if __name__ == '__main__':
    random.seed(1)
    try:
        versus_cpu()
    except EOFError:
        pass
