# (c) Mark Dufour, Haifang Ni, tweaked and converted to a class by shakfu
# --- mark.dufour@gmail.com

empty, black, white = 0, 1, -1

class BoardGame:
    def __init__(self, size):
        self.size = size
        self.board = self.get_board(self.size)
        self.player = {white: "human", black: "lalaoth"}
        self.depth = 3
        self.flips = 0
        self.DIRECTIONS = [
            (1, 1),
            (-1, 1),
            (0, 1),
            (1, -1),
            (-1, -1),
            (0, -1),
            (1, 0),
            (-1, 0),
        ]

    def get_board(self, n):
        board = [[empty for x in range(n)] for y in range(n)]
        c1 = (n // 2) - 1
        c2 = n // 2
        board[c1][c1] = board[c2][c2] = white
        board[c1][c2] = board[c2][c1] = black
        return board

    def possible_move(self, board, x, y, color):
        if board[x][y] != empty:
            return False
        for direction in self.DIRECTIONS:
            if self.flip_in_direction(board, x, y, direction, color):
                return True
        return False

    def flip_in_direction(self, board, x, y, direction, color):
        other_color = False
        while True:
            x, y = x + direction[0], y + direction[1]
            if x not in range(self.size) or y not in range(self.size):
                return False
            square = board[x][y]
            if square == empty:
                return False
            if square != color:
                other_color = True
            else:
                return other_color

    def flip_stones(self, board, move, color):
        self.flips += 1
        for direction in self.DIRECTIONS:
            if self.flip_in_direction(board, move[0], move[1], direction, color):
                x, y = move[0] + direction[0], move[1] + direction[1]
                while board[x][y] != color:
                    board[x][y] = color
                    x, y = x + direction[0], y + direction[1]
        board[move[0]][move[1]] = color

    def possible_moves(self, board, color):
        return [
            (x, y)
            for x in range(self.size)
            for y in range(self.size)
            if self.possible_move(board, x, y, color)
        ]

    def stone_count(self, board, color):
        return sum(
            [len([square for square in line if square == color]) for line in board]
        )

    def best_move(self, board, color, first, step=1):
        max_move, max_mobility, max_score = None, 0, 0

        for move in self.possible_moves(board, color):
            if move in [
                (0, 0),
                (0, self.size - 1),
                (self.size - 1, 0),
                (self.size - 1, self.size - 1),
            ]:
                mobility, score = self.size * self.size, self.size * self.size
                if color != first:
                    mobility = self.size * self.size - mobility
            else:
                testboard = [[square for square in line] for line in board]
                self.flip_stones(testboard, move, color)
                if step < self.depth:
                    next_move, mobility = self.best_move(testboard, -color, first, step + 1)
                else:
                    mobility = len(self.possible_moves(testboard, first))
                score = mobility
                if color != first:
                    score = self.size * self.size - score
            if score >= max_score:  # []
                max_move, max_mobility, max_score = (
                    move,
                    mobility,
                    score,
                )
        return max_move, max_mobility

    def play(self):
        self.flips = 0
        steps = 0
        turn = black
        while self.possible_moves(self.board, black) or self.possible_moves(self.board, white):
            if self.possible_moves(self.board, turn):
                move, mobility = self.best_move(self.board, turn, turn)
                if not self.possible_move(self.board, move[0], move[1], turn):
                    print("impossible!")
                    turn = -turn
                else:
                    self.flip_stones(self.board, move, turn)  # []
            turn = -turn
        return self.flips


def test_flip():
    # assert game() == 6689 # self.size = 6
    bg = BoardGame(size=4)
    assert bg.play() == 147  # self.size = 4


def test_all():
    test_flip()


if __name__ == "__main__":
    test_all()
