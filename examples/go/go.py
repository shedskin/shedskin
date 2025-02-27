#! /usr/bin/python3

''' 
UCT go player in python, by mark.dufour@gmail.com.

techniques used:

-http://en.wikipedia.org/wiki/Disjoint-set_data_structure (to maintain groups)
-http://senseis.xmp.net/?UCT (UCT monte carlo search)
-http://en.wikipedia.org/wiki/Zobrist_hashing (incremental hash values)
-timestamps, to be able to invalidate things with a single increment

GTP code by Folkert van Heusden <mail@vanheusden.com>
'''

import random, math, sys, time

SIZE = 9
GAMES = 15000
KOMI = 7.5
EMPTY, WHITE, BLACK = 0, 1, 2
SHOW = {EMPTY: '.', WHITE: 'o', BLACK: 'x'}
PASS = -1
MAXMOVES = SIZE*SIZE*3
TIMESTAMP = 0
MOVES = 0

# def to_pos(x,y):
#     return y * SIZE + x

def to_pos(x,y):
    return int(y) * SIZE + int(x)

def to_xy(pos):
    y, x = divmod(pos, SIZE)
    return x, y

class Square:
    def __init__(self, board, pos):
        self.board = board
        self.pos = pos
        self.timestamp = TIMESTAMP
        self.removestamp = TIMESTAMP
        self.zobrist_strings = [random.randrange(sys.maxsize) for i in range(3)]

    def set_neighbours(self): 
        x, y = self.pos % SIZE, self.pos / SIZE
        self.neighbours = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            newx, newy = x + dx, y + dy
            if 0 <= newx < SIZE and 0 <= newy < SIZE:
                #print(newx, newy, '->', round(newy))
                self.neighbours.append(self.board.squares[to_pos(newx, newy)])

    def move(self, color):
        global TIMESTAMP, MOVES
        TIMESTAMP += 1
        MOVES += 1
        self.board.zobrist.update(self, color)
        self.color = color
        self.reference = self
        self.ledges = 0
        self.used = True
        for neighbour in self.neighbours:
            neighcolor = neighbour.color
            if neighcolor == EMPTY: 
                self.ledges += 1
            else:
                neighbour_ref = neighbour.find(update=True)
                if neighcolor == color:
                    if neighbour_ref.reference.pos != self.pos:
                        self.ledges += neighbour_ref.ledges 
                        neighbour_ref.reference = self
                    self.ledges -= 1
                else:
                    neighbour_ref.ledges -= 1
                    if neighbour_ref.ledges == 0:
                        neighbour.remove(neighbour_ref)
        self.board.zobrist.add()

    def remove(self, reference, update=True):
        self.board.zobrist.update(self, EMPTY)
        self.removestamp = TIMESTAMP
        if update:
            self.color = EMPTY
            self.board.emptyset.add(self.pos)
#            if color == BLACK:
#                self.board.black_dead += 1
#            else:
#                self.board.white_dead += 1
        for neighbour in self.neighbours:
            if neighbour.color != EMPTY and neighbour.removestamp != TIMESTAMP:
                neighbour_ref = neighbour.find(update)
                if neighbour_ref.pos == reference.pos:
                    neighbour.remove(reference, update)
                else:
                    if update:
                        neighbour_ref.ledges += 1

    def find(self, update=False): 
       reference = self.reference
       if reference.pos != self.pos:
           reference = reference.find(update)
           if update:
               self.reference = reference
       return reference

#    def __repr__(self):
#        return repr(to_xy(self.pos))

class EmptySet:
    def __init__(self, board):
        self.board = board
        self.empties = list(range(SIZE*SIZE))
        self.empty_pos = list(range(SIZE*SIZE))

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
        empties = opps = weak_opps = neighs = weak_neighs = 0
        for neighbour in square.neighbours:
            neighcolor = neighbour.color
            if neighcolor == EMPTY:
                empties += 1
                continue
            neighbour_ref = neighbour.find()
            if neighbour_ref.timestamp != TIMESTAMP:
                if neighcolor == self.color:  
                    neighs += 1
                else: 
                    opps += 1
                neighbour_ref.timestamp = TIMESTAMP
                neighbour_ref.temp_ledges = neighbour_ref.ledges
            neighbour_ref.temp_ledges -= 1
            if neighbour_ref.temp_ledges == 0:
                if neighcolor == self.color:  
                    weak_neighs += 1
                else:
                    weak_opps += 1
                    neighbour_ref.remove(neighbour_ref, update=False)
        dupe = self.zobrist.dupe()
        self.zobrist.hash = old_hash
        strong_neighs = neighs-weak_neighs
        strong_opps = opps-weak_opps
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

    '''
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
           ledges1 = 0
           for member in members1:
               for neighbour in member.neighbours:
                   if neighbour.color == EMPTY:
                       ledges1 += 1

           root = square.find()

           #print 'members1', square, root, members1
           #print 'ledges1', square, ledges1

           members2 = set()
           for square2 in self.squares:
               if square2.color != EMPTY and square2.find() == root:
                   members2.add(square2)

           ledges2 = root.ledges
           #print 'members2', square, root, members1
           #print 'ledges2', square, ledges2

           assert members1 == members2
           assert ledges1 == ledges2, ('ledges differ at %r: %d %d' % (square, ledges1, ledges2))

           empties1 = set(self.emptyset.empties)

           empties2 = set()
           for square in self.squares:
               if square.color == EMPTY:
                   empties2.add(square.pos)
    '''

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
        self.parent = None

    def play(self, board):
        """ uct tree search """
        color = board.color
        node = self
        path = [node]
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
        for x in range(MAXMOVES): # XXX while not self.finished?
            if board.finished:
                break
            board.move(board.random_move())

    def update_path(self, board, color, path):
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
        text = input('?').strip()
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
    for game in range(GAMES):
        node = tree
        nboard.reset()
        nboard.replay(board.history)
        node.play(nboard)
#    print 'moves', MOVES
    return tree.best_visited().pos

def timed_computer_move(board, end_ts):
    pos = board.random_move()
    if pos == PASS:
        return PASS
    tree = UCTNode()
    tree.unexplored = board.useful_moves()
    nboard = Board()
    while time.time() < end_ts:
        node = tree
        nboard.reset()
        nboard.replay(board.history)
        node.play(nboard)
    best = tree.best_visited()
    if best == None:
        return PASS
    return best.pos

def versus_cpu():
    board = Board()
    while True:
        if board.lastmove != PASS:
            print(board)
        print('thinking..')
        pos = computer_move(board)
        if pos == PASS:
            print('I pass.')
        else:
            print('I move here:', to_xy(pos))
        board.move(pos)
        #board.check()
        if board.finished:
            break
        if board.lastmove != PASS:
            print(board)
        break # XXX remove this break for interactive play!!
        pos = user_move(board)
        board.move(pos)
        #board.check()
        if board.finished:
            break
    print('WHITE:', board.score(WHITE))
    print('BLACK:', board.score(BLACK))

def pos_to_gtp(pos):
    x = pos % SIZE
    y = pos // SIZE

    if x >= 8:  # 'i'
        x += 1

    return '%c%d' % (ord('A') + x, y + 1)

def gtp_to_color(name):
    if name in ('b', 'B', 'black', 'BLACK'):
        return BLACK

    return WHITE

def gtp():
    global KOMI
    global SIZE

    assert gtp_to_color('b') == BLACK
    assert pos_to_gtp(0) == 'A1'
    assert pos_to_gtp(9 * 9 - 1) == 'J9'

    board = Board()

    time_left_w = 30.
    time_left_b = 30.

    while True:
        line = sys.stdin.readline().rstrip('\n').rstrip('\r').lower()
        parts = line.split()

        if len(parts) == 0:
            print('?')

        elif parts[0] == 'clear_board':
            board = Board()
            KOMI = 7.5
            print('=')

        elif parts[0] == 'protocol_version':
            print('= 2')

        elif parts[0] == 'name':
            print('= Go by Mark Dufour')

        elif parts[0] == 'komi':
            KOMI = float(parts[1])
            print('=')

        elif parts[0] == 'boardsize':
            SIZE = int(parts[1])
            KOMI = 7.5
            board = Board()
            print('=')

        elif parts[0] == 'play':
            board.color = gtp_to_color(parts[1])
            if parts[2] == 'pass':
                board.move(PASS)
            else:
                vertex_str = parts[2]
                x = ord(vertex_str[0]) - ord('a')
                if vertex_str[0] >= 'i':
                    x -= 1
                y = int(vertex_str[1:]) - 1
                pos = y * SIZE + x
                if not board.useful(pos):
                    print('Invalid move?')
                board.move(pos)
                print(board)
            print('=')

        elif parts[0] == 'final_score':
            s = board.score(BLACK)

            if s == 0:
                print('= 0')
            elif s < 0:
                print('= W+%f' % abs(s))
            else:
                print('= B+%f' % s)

        elif parts[0] == 'time_settings':
            # TODO
            print('=')

        elif parts[0] == 'time_left':
            board.color = gtp_to_color(parts[1])
            if board.color == BLACK:
                time_left_b = float(parts[2])
            else:
                time_left_w = float(parts[2])
            print('=')

        elif parts[0] == 'genmove':
            board.color = gtp_to_color(parts[1])
            umoves = board.useful_moves()
            n_useful_moves = 0 if board.finished else len(umoves)
            if n_useful_moves == 0:
                print('= pass')
                board.move(PASS)
            else:
                print('moves: %s' % ', '.join([pos_to_gtp(x) for x in umoves]))
                time_to_use = (time_left_b if board.color == BLACK else time_left_w) / n_useful_moves
                pos = timed_computer_move(board, time.time() + time_to_use)
                board.move(pos)
                print(board)
                if pos == PASS:
                    print('= pass')
                else:
                    print('= %s' % pos_to_gtp(pos))

        elif parts[0] == 'list_commands':
            print('= clear_board')
            print('protocol_version')
            print('name')
            print('komi')
            print('boardsize')
            print('play')
            print('final_score')
            print('time_settings')
            print('time_left')
            print('genmove')
            print('quit')

        elif parts[0] == 'quit':
            break

        else:
            print('?')

        print('')

        sys.stdout.flush()

if __name__ == '__main__':
    random.seed(1)

    try:
        if len(sys.argv) == 2 and sys.argv[1] == '--gtp':
            gtp()
        else:
            versus_cpu()
    except EOFError:
        pass
