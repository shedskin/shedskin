import random

SIZE = 9
WHITE, BLACK, EMPTY = 0, 1, 2
SHOW = {EMPTY: '.', WHITE: 'o', BLACK: 'x'}

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
        self.lastmove = -1
        self.lastpass = False

    def acceptable(self, pos):
        square = self.squares[pos]
        other = 1-self.color
        legal = False
        buddies = 0
        need_help = False
        for neighbour in square.neighbours:
            ncolor = neighbour.color
            if neighbour.group:
                members = len(neighbour.group.members)
                liberties = len(neighbour.group.liberties)

            if ncolor == EMPTY:
                return True
            elif ncolor == other:
                if liberties == 1 and not (neighbour.pos == self.lastmove and members == 1):
                    return True
            elif ncolor == self.color:
                buddies += 1
                if liberties == 1:
                    need_help = True
                elif liberties >= 2:
                    legal = True

        return legal and (buddies != len(square.neighbours) or need_help)

    def move(self, pos, color):
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

    def new_group(self, square):
        group = square.group = square.fast_group
        group.color = square.color
        group.members.clear()
        group.members.add(square.pos)
        group.liberties.clear()
        for neighbour in square.neighbours:
            if neighbour.color == EMPTY:
                group.liberties.add(neighbour.pos)

    def random_move(self):
        choices = len(self.empties)
        while choices:  
            i = random.randrange(choices)
            trypos = board.empties[i]
            if self.acceptable(trypos):
                last = len(self.empties)-1
                self.empties[i] = self.empties[last] 
                self.empties.pop(last)
                return trypos
            choices -= 1
            self.empties[i] = self.empties[choices]
            self.empties[choices] = trypos
        return -1

    def score(self, color):
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

    def play(self):
        for x in range(1000):
            if self.play_random_move() == -2:
                break

    def play_random_move(self):
        pos = self.random_move()
        return self.play_move(pos)

    def play_move(self, pos):
        if pos == -1:
            if self.lastpass:
                return -2
            self.lastmove = -1
            self.lastpass = True
        else:
            self.move(pos, self.color)
            self.lastmove = pos
            self.lastpass = False
        self.color = 1-self.color
        return pos

    def get_state(self):
        return [square.color for square in self.squares], (self.color, self.lastmove, self.lastpass)

    def set_state(self, state):
        colors, (self.color, self.lastmove, self.lastpass) = state
        for pos, color in enumerate(colors):
            if color != EMPTY:
                self.move(pos, color)

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
        self.wins = 0
        self.losses = 0
        self.pos_child = [None for x in range(SIZE*SIZE)]

    def play(self, board):
        color = board.color
        pos = board.random_move()
        board.play_move(pos)
#        print 'SELECT', to_xy(pos)
#        print board
        board.play()
#        print board
#        print 'WHITE', board.score(WHITE)
#        print 'BLACK', board.score(BLACK)

        child = self.pos_child[pos]
        if not child:
#            print 'NEW NODE'
            child = self.pos_child[pos] = UCTNode()
       
        if color == BLACK:
            wins = board.score(BLACK) >= board.score(WHITE)
            if wins:
                child.wins += 1
            else:
                child.losses += 1

    def score(self):
        return self.wins/float(self.wins+self.losses)

if __name__ == '__main__':
    random.seed(1)
    board = Board()
#    for x in range(20):
#        board.play_random_move()
#    print 'START STATE:'
#    print board
    state = board.get_state()
    tree = UCTNode()
    for game in range(25000):
        node = tree
        board = Board()
        board.set_state(state)
        #print 'RESET STATE:'
        #print board
        node.play(board)
        #print 'FINAL:'
        #print board

    print 'visited', len([child for child in tree.pos_child if child])

    maxscore = -1
    maxchild = None
    maxpos = -1
    for pos, child in enumerate(node.pos_child):
        if child: # and (child.wins or child.losses):
            print 'child!', to_xy(pos), child.wins, child.losses, child.score()
            if child.score() > maxscore:
                maxchild = child
                maxscore = child.score()
                maxpos = pos
    print 'best one', maxchild, maxchild.wins, maxchild.losses, maxchild.score(), to_xy(maxpos)
