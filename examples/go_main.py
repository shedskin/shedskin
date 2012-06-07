import math
import random
import go

GAMES = 10000
PLAYOUTS = 1

class UCTNode:
    def __init__(self):
        self.bestchild = None
        self.pos = -1
        self.wins = 0
        self.losses = 0
        self.pos_child = [None for x in range(go.SIZE*go.SIZE)]
        self.parent = None

    def play(self, board):
        """ uct tree search """
        color = board.color
        node = self
        path = [node]
        while True:
            pos = node.select(board)
            if pos == go.PASS:
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
        black_wins = board.random_playout(PLAYOUTS)
        self.update_path(color, path, black_wins)

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
            return go.PASS

    def update_path(self, color, path, black_wins):
        """ update win/loss count along path """
        for node in path:
            if color == go.BLACK: color = go.WHITE
            else: color = go.BLACK
            if black_wins == (color == go.BLACK):
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
            if child and (child.wins+child.losses) > maxvisits:
                maxvisits, maxchild = (child.wins+child.losses), child
        return maxchild

def user_move(board):
    while True:
        text = raw_input('?').strip()
        if text == 'p':
            return go.PASS
        if text == 'q':
            raise EOFError
        try:
            x, y = [int(i) for i in text.split(',')]
        except ValueError:
            continue
        if not (0 <= x < go.SIZE and 0 <= y < go.SIZE):
            continue
        pos = go.to_pos(x, y)
        if board.useful(pos): 
            return pos

def computer_move(board):
    global MOVES
    pos = board.random_move()
    if pos == go.PASS:
        return go.PASS
    tree = UCTNode()
    tree.unexplored = board.useful_moves()
    nboard = go.Board()
    for game in range(GAMES):
        node = tree
        nboard.reset()
        nboard.replay(board.history)
        node.play(nboard)
    return tree.best_visited().pos

def versus_cpu():
    board = go.Board()
    while True:
        if board.lastmove != go.PASS:
            print board
        print 'thinking..'
        pos = computer_move(board)
        if pos == go.PASS:
            print 'I pass.'
        else:
            print 'I move here:', go.to_xy(pos)
        board.move(pos)
        if board.finished:
            break
        if board.lastmove != go.PASS:
            print board
        print 'x,y=move, p=pass, q=quit'
        pos = user_move(board)
        board.move(pos)
        if board.finished:
            break
    print 'WHITE:', board.score(go.WHITE)
    print 'BLACK:', board.score(go.BLACK)

if __name__ == '__main__':
    random.seed(1)
    try:
        versus_cpu()
    except EOFError:
        pass
