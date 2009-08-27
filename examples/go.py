import random, math

SIZE = 9
GAMES = 100000
WHITE, BLACK, EMPTY = 0, 1, 2
SHOW = {EMPTY: '.', WHITE: 'o', BLACK: 'x'}
PASS = -1
MOVES = 0
TIMESTAMP = 0

def to_pos(x,y):
    return y * SIZE + x

def to_xy(pos):
    y, x = divmod(pos, SIZE)
    return x, y

class Square:
    def __init__(self, board, pos):
        self.board = board
        self.pos = pos
        self.color = EMPTY
        self.timestamp = TIMESTAMP

    def set_neighbours(self): 
        x, y = self.pos % SIZE, self.pos / SIZE;
        self.neighbours = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            newx, newy = x + dx, y + dy
            if 0 <= newx < SIZE and 0 <= newy < SIZE:
                self.neighbours.append(self.board.squares[to_pos(newx, newy)])

    def move(self, color):
        global MOVES
        MOVES += 1
        self.color = color
        self.reference = self
        self.ledges = 0
        for neighbour in self.neighbours:
            if neighbour.color == EMPTY: 
                self.ledges += 1
            else:
                neighbour_ref = neighbour.find()
                if neighbour.color == color:
                    if neighbour_ref.reference != self:
                        self.ledges += neighbour_ref.ledges 
                        neighbour_ref.reference = self
                    self.ledges -= 1
                else:
                    neighbour_ref.ledges -= 1
                    if neighbour_ref.ledges == 0:
                        neighbour.remove(neighbour_ref)

    def remove(self, reference):
        self.color = EMPTY
        self.board.emptyset.add(self.pos)
        for neighbour in self.neighbours:
            if neighbour.color != EMPTY:
                neighbour_ref = neighbour.find()
                if neighbour_ref == reference:
                    neighbour.remove(reference)
                else:
                    neighbour_ref.ledges += 1

    def find(self): 
        if self.reference.pos != self.pos:
            self.reference = self.reference.find()
        return self.reference

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
            if self.board.useful_move(pos):
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

class Board:
    def __init__(self):
        self.squares = [Square(self, pos) for pos in range(SIZE*SIZE)]
        for square in self.squares:
            square.set_neighbours()
        self.reset()

    def reset(self):
        for square in self.squares:
            square.color = EMPTY
        self.emptyset = EmptySet(self)
        self.color = BLACK
        self.finished = False
        self.lastmove = -2

    def random_move(self):
        return self.emptyset.random_choice()

    def useful_move(self, pos): 
        global TIMESTAMP
        TIMESTAMP += 1
        square = self.squares[pos]
        opps = weak_opps = neighs = weak_neighs = 0
        for neighbour in square.neighbours:
            if neighbour.color == EMPTY:
                return True
            neighbour_ref = neighbour.find()
            if neighbour_ref.timestamp != TIMESTAMP:
                if neighbour.color == self.color:  
                    neighs += 1
                else: 
                    opps += 1
                neighbour_ref.timestamp = TIMESTAMP
                neighbour_ref.temp_ledges = neighbour_ref.ledges
            neighbour_ref.temp_ledges -= 1
            if neighbour_ref.temp_ledges == 0:
                if neighbour.color == self.color:  
                    weak_neighs += 1
                else:
                    weak_opps += 1
        strong_neighs = neighs-weak_neighs
        strong_opps = opps-weak_opps
        return weak_opps or (strong_neighs and (strong_opps or weak_neighs))

    def play_move(self, pos):
        square = self.squares[pos]
        if pos != PASS:
            self.move(square)
        elif self.lastmove == PASS:
            self.finished = True
        self.color = 1 - self.color
        self.lastmove = pos

    def move(self, square):
        square.move(self.color)
        self.emptyset.remove(square.pos)

    def __repr__(self):
        result = []
        for y in range(SIZE):
            start = to_pos(0, y)
            result.append(''.join([SHOW[square.color]+' ' for square in self.squares[start:start+SIZE]]))
        return '\n'.join(result)

def check(board):
   for square in board.squares:
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

   #    print 'members1', square, members1
   #    print 'ledges1', ledges1

       members2 = set()
       root = square.find()
       for square2 in board.squares:
           if square2.color != EMPTY and square2.find() == root:
               members2.add(square2)

       ledges2 = root.ledges
   #    print 'members2', square, members1
   #    print 'ledges2', ledges2

       assert ledges1 == ledges2
       assert members1 == members2

   empties1 = set(board.emptyset.empties)
#    print 'empties1', empties1

   empties2 = set()
   for square in board.squares:
       if square.color == EMPTY:
           empties2.add(square.pos)

#    print 'empties2', empties2

   assert empties1 == empties2

def main():
    random.seed(1)
    board = Board()
    for game in range(GAMES):
#        print 'GAME'
        board.reset()
        for x in range(1000): 
            if board.finished:
                break
            pos = board.random_move()
#            print 'TURN', SHOW[board.color]
#            if pos == PASS:
#                print 'PASS'
#            else:
#                print 'SELECT', to_xy(pos)
            board.play_move(pos)
#            print x
#            print board
#            print
#            check(board)
    print 'MOVES', MOVES

if __name__ == '__main__':
    main()
