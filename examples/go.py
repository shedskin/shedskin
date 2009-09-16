import random, math, sys

SIZE = 9
#GAMES = 15000
KOMI = 7.5
EMPTY, WHITE, BLACK = 0, 1, 2
SHOW = {EMPTY: '.', WHITE: 'o', BLACK: 'x'}
PASS = -1
MAXMOVES = SIZE*SIZE*3
TIMESTAMP = REMOVESTAMP = 0
MOVES = 0

def to_pos(x,y):
    return y * SIZE + x

def to_xy(pos):
    y, x = divmod(pos, SIZE)
    return x, y

class Square:
    def __init__(self, board, pos):
        self.board = board
        self.pos = pos
        self.liberties = 0
        self.timestamp = TIMESTAMP
        self.timestamp2 = TIMESTAMP
        self.findstamp = TIMESTAMP
        self.removestamp = REMOVESTAMP
        self.zobrist_strings = [random.randrange(sys.maxint) for i in range(3)]

    def set_neighbours(self): 
        x, y = self.pos % SIZE, self.pos / SIZE;
        self.neighbours = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            newx, newy = x + dx, y + dy
            if 0 <= newx < SIZE and 0 <= newy < SIZE:
                self.neighbours.append(self.board.squares[to_pos(newx, newy)])

    def count_liberties(self, reference=None):
        if not reference:
            reference = self
            self.liberties = 0
        self.timestamp = TIMESTAMP
        for neighbour in self.neighbours:
            if neighbour.timestamp != TIMESTAMP:
                neighbour.timestamp = TIMESTAMP
                if neighbour.color == EMPTY:
                    reference.liberties += 1
                elif neighbour.color == self.color:
                    neighbour.count_liberties(reference)

    def liberty(self):
        self.findstamp = TIMESTAMP
        for neighbour in self.neighbours:
            if neighbour.findstamp != TIMESTAMP:
                neighbour.findstamp = TIMESTAMP
                if neighbour.color == EMPTY:
                    return neighbour
                elif neighbour.color == self.color:
                    liberty = neighbour.liberty()
                    if liberty:
                        return liberty

    def move(self, color):
        global TIMESTAMP, MOVES
        TIMESTAMP += 1
        MOVES += 1
        self.board.zobrist.update(self, color)
        self.color = color
        self.reference = self
        self.members = 1
        self.used = True
        self.board.atari = None
        for neighbour in self.neighbours:
            if neighbour.color != EMPTY: 
                neighbour_ref = neighbour.find(update=True)
                if neighbour_ref.timestamp != TIMESTAMP:
                    neighbour_ref.timestamp = TIMESTAMP
                    if neighbour.color == color:
                        neighbour_ref.reference = self
                        self.members += neighbour_ref.members
                    else:
                        neighbour_ref.liberties -= 1
                        if neighbour_ref.liberties == 0:
                            neighbour_ref.remove(neighbour_ref, update=True)
                        elif neighbour_ref.liberties == 1:
                            self.board.atari = neighbour_ref
        TIMESTAMP += 1
        self.count_liberties()
        self.board.zobrist.add()

    def remove(self, reference, update=True):
        global REMOVESTAMP
        REMOVESTAMP += 1
        removestamp = REMOVESTAMP
        self.board.zobrist.update(self, EMPTY)
        self.timestamp2 = TIMESTAMP
        if update:
            self.color = EMPTY
            self.board.emptyset.add(self.pos)
#            if color == BLACK:
#                self.board.black_dead += 1
#            else:
#                self.board.white_dead += 1
        if update:
            for neighbour in self.neighbours:
                if neighbour.color != EMPTY:
                    neighbour_ref = neighbour.find(update)
                    if neighbour_ref.pos != self.pos and neighbour_ref.removestamp != removestamp:
                        neighbour_ref.removestamp = removestamp
                        neighbour_ref.liberties += 1
        for neighbour in self.neighbours:
            if neighbour.color != EMPTY:
                neighbour_ref = neighbour.find(update)
                if neighbour_ref.pos == reference.pos and neighbour.timestamp2 != TIMESTAMP:
                    neighbour.remove(reference, update)

    def find(self, update=False): 
       reference = self.reference
       if reference.pos != self.pos:
           reference = reference.find(update)
           if update:
               self.reference = reference
       return reference
    
    def __repr__(self):
        return repr(to_xy(self.pos))

class EmptySet:
    def __init__(self, board):
        self.board = board
        self.empties = range(SIZE*SIZE)
        self.empty_pos = range(SIZE*SIZE)

    def random_choice(self):
        choices = len(self.empties)
        while choices:  
            i = int(random.random()*choices)
            pos = self.empties[i]
            if self.board.useful(pos):
                return pos
            choices -= 1
            self.set(i, self.empties[choices])
            self.set(choices, pos)
        return PASS

    def add(self, pos):
        self.empty_pos[pos] = len(self.empties)
        self.empties.append(pos)

    def remove(self, pos):
        self.set(self.empty_pos[pos], self.empties[len(self.empties)-1])
        self.empties.pop()

    def set(self, i, pos): 
        self.empties[i] = pos
        self.empty_pos[pos] = i

class ZobristHash:
    def __init__(self, board):
        self.board = board
        self.hash_set = set()
        self.hash = 0
        for square in self.board.squares:
            self.hash ^= square.zobrist_strings[EMPTY]
        self.hash_set.clear()
        self.hash_set.add(self.hash)

    def update(self, square, color):
        self.hash ^= square.zobrist_strings[square.color]
        self.hash ^= square.zobrist_strings[color]

    def add(self):
        self.hash_set.add(self.hash)
    
    def dupe(self):
        return self.hash in self.hash_set

class Board:
    def __init__(self):
        self.squares = [Square(self, pos) for pos in range(SIZE*SIZE)]
        for square in self.squares:
            square.set_neighbours()
        self.reset()

    def reset(self):
        for square in self.squares:
            square.color = EMPTY
            square.used = False
        self.emptyset = EmptySet(self)
        self.zobrist = ZobristHash(self)
        self.color = BLACK
        self.finished = False
        self.lastmove = -2
        self.history = []
        self.atari = None
        self.white_dead = 0
        self.black_dead = 0

    def move(self, pos):
        square = self.squares[pos]
        if pos != PASS:
            square.move(self.color)
            self.emptyset.remove(square.pos)
        elif self.lastmove == PASS:
            self.finished = True
        if self.color == BLACK: self.color = WHITE
        else: self.color = BLACK
        self.lastmove = pos
        self.history.append(pos)

    def random_move(self):
        return self.emptyset.random_choice()

    def useful_fast(self, square):
        if not square.used:
            for neighbour in square.neighbours:
                if neighbour.color == EMPTY:
                    return True
        return False

    def useful(self, pos): 
        global TIMESTAMP
        TIMESTAMP += 1
        square = self.squares[pos]
        if self.useful_fast(square):
            return True
        old_hash = self.zobrist.hash
        self.zobrist.update(square, self.color)
        empties = strong_opps = weak_opps = strong_neighs = weak_neighs = 0
        for neighbour in square.neighbours:
            if neighbour.color == EMPTY:
                empties += 1
            else:
                neighbour_ref = neighbour.find()
                if neighbour_ref.timestamp != TIMESTAMP:
                    neighbour_ref.timestamp = TIMESTAMP
                    weak = (neighbour_ref.liberties == 1)
                    if neighbour.color == self.color:  
                        if weak: 
                            weak_neighs += 1
                        else: 
                            strong_neighs += 1
                    else: 
                        if weak: 
                            weak_opps += 1
                            neighbour_ref.remove(neighbour_ref, update=False)
                        else: 
                            strong_opps += 1
        dupe = self.zobrist.dupe()
        self.zobrist.hash = old_hash
        return not dupe and \
               bool(empties or weak_opps or (strong_neighs and (strong_opps or weak_neighs)))

    def useful_moves(self):
        return [pos for pos in self.emptyset.empties if self.useful(pos)]

    def replay(self, history):
        for pos in history:
            self.move(pos)

    def score(self, color):
        if color == WHITE:
            count = KOMI + self.black_dead
        else:
            count = self.white_dead
        for square in self.squares:
            squarecolor = square.color
            if squarecolor == color:
                count += 1
            elif squarecolor == EMPTY:
                surround = 0
                for neighbour in square.neighbours:
                    if neighbour.color == color:
                        surround += 1
                if surround == len(square.neighbours): 
                    count += 1
        return count

    def check(self):
       for square in self.squares:
           if square.color == EMPTY:
               continue

           members1 = set([square])
           changed = True
           while changed:
               changed = False
               for member in members1.copy():
                   for neighbour in member.neighbours:
                       if neighbour.color == square.color and neighbour not in members1:
                           changed = True
                           members1.add(neighbour)
           liberties1 = set()
           for member in members1:
               for neighbour in member.neighbours:
                   if neighbour.color == EMPTY:
                       liberties1.add(neighbour.pos)

           root = square.find()

           #print 'members1', square, root, members1
           #print 'ledges1', square, ledges1

           members2 = set()
           for square2 in self.squares:
               if square2.color != EMPTY and square2.find() == root:
                   members2.add(square2)

           liberties2 = root.liberties
           #print 'members2', square, root, members1
           #print 'ledges2', square, ledges2

           assert members1 == members2
           assert len(liberties1) == liberties2, ('liberties differ at %r: %d %d' % (root, len(liberties1), liberties2))

           empties1 = set(self.emptyset.empties)

           empties2 = set()
           for square in self.squares:
               if square.color == EMPTY:
                   empties2.add(square.pos)

           assert empties1 == empties2

    def __repr__(self):
        result = []
        for y in range(SIZE):
            start = to_pos(0, y)
            result.append(''.join([SHOW[square.color]+' ' for square in self.squares[start:start+SIZE]]))
        return '\n'.join(result)

class UCTNode:
    def __init__(self):
        self.bestchild = None
        self.pos = -1
        self.wins = 0
        self.losses = 0
        self.pos_child = [None for x in range(SIZE*SIZE)]
        self.amafvisits = 0
        self.pos_amaf_wins = [0 for x in range(SIZE*SIZE)]
        self.pos_amaf_losses = [0 for x in range(SIZE*SIZE)]
        self.parent = None

    def play(self, board):
        """ uct tree search """
        color = board.color
        node = self
        path = [node]
        histpos = len(board.history)
        while True:
            pos = node.select(board)
            if pos == PASS:
                break
            board.move(pos)
            child = node.pos_child[pos]
            if not child:
                child = node.pos_child[pos] = UCTNode()
                child.unexplored = board.useful_moves()
                child.pos = pos
                child.parent = node
                path.append(child)
                break
            path.append(child)
            node = child
        self.random_playout(board)
        self.update_path(board, histpos, color, path)

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
        for x in range(MAXMOVES): # XXX while not self.finished?
            if board.finished:
                break
            pos = PASS
            if board.atari:
                liberty = board.atari.liberty()
                if board.useful(liberty.pos):
                    pos = liberty.pos
            if pos == PASS:
                pos = board.random_move()
#            print 'pos color', to_xy(pos), SHOW[board.color]
            board.move(pos)
#            print board
#            board.check()
#        print 'WHITE:', board.score(WHITE)
#        print 'BLACK:', board.score(BLACK)

    def update_path(self, board, histpos, color, path):
        """ update win/loss count along path """
        wins = board.score(BLACK) >= board.score(WHITE)
        for node in path:
            if color == BLACK: color = WHITE
            else: color = BLACK
            if wins == (color == BLACK):
                node.wins += 1
            else:
                node.losses += 1
            if node.parent:
                for i in range(histpos+2, len(board.history), 2):
                    pos = board.history[i]
                    if pos == PASS:
                        break
                    if wins == (color == BLACK):
                        node.parent.pos_amaf_wins[pos] += 1
                    else:
                        node.parent.pos_amaf_losses[pos] += 1
                    node.parent.amafvisits += 1
                node.parent.bestchild = node.parent.best_child()

    def score(self):
        winrate = self.wins/float(self.wins+self.losses)
        parentvisits = self.parent.wins+self.parent.losses
        if not parentvisits:
            return winrate
        nodevisits = self.wins+self.losses
        uct_score = winrate + math.sqrt((math.log(parentvisits))/(5*nodevisits))

        amafvisits = self.parent.pos_amaf_wins[self.pos]+self.parent.pos_amaf_losses[self.pos] 
        if not amafvisits:
            return uct_score
        amafwinrate = self.parent.pos_amaf_wins[self.pos]/float(amafvisits)
        uct_amaf = amafwinrate + math.sqrt((math.log(self.parent.amafvisits))/(5*amafvisits))

        beta = math.sqrt(1000.0/(3*parentvisits+1000.0))
        return beta*uct_amaf + (1-beta)*uct_score

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
        if board.useful(pos): 
            return pos

def computer_move(board):
    global MOVES
    pos = board.random_move()
    if pos == PASS:
        return PASS
    tree = UCTNode()
    tree.unexplored = board.useful_moves()
    nboard = Board()
    GAMES = max(25000-(1000*len(board.history))/4, 4000)
#    GAMES = 100000
    for game in range(GAMES):
        node = tree
        nboard.reset()
        nboard.replay(board.history)
        node.play(nboard)
#    for pos in range(SIZE*SIZE):
#        print 'amaf', to_xy(pos), node.pos_child[pos].score() #node.pos_amaf_wins[pos]/float(node.pos_amaf_wins[pos]+node.pos_amaf_losses[pos])
#    print 'moves', MOVES
    return tree.best_visited().pos

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
        board.move(pos)
        #break
        #board.check()
        if board.finished:
            break
        if board.lastmove != PASS:
            print board
        pos = user_move(board)
        board.move(pos)
        #board.check()
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
