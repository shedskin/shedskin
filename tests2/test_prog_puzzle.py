# (c) Jack Ha
# --- jack.ha@gmail.com
# tweaked and converted to class by shakfu


class PuzzlGame:
    def __init__(self):
        self.iterations = 0
        self.hashtable = {}

    def validMove(self, puzzle, x, y, number):
        # see if the number is in any row, column or his own 3x3 square
        blnOK = True
        px = x // 3
        py = y // 3
        if puzzle[x][y] != 0:
            blnOK = False
        if blnOK:  # []
            for i in range(9):
                if puzzle[i][y] == number:
                    blnOK = False
        if blnOK:  # []
            for j in range(9):
                if puzzle[x][j] == number:
                    blnOK = False
        if blnOK:  # []
            for i in range(3):
                for j in range(3):
                    if puzzle[px * 3 + i][py * 3 + j] == number:
                        blnOK = False
        return blnOK


    def findallMoves(self, puzzle, x, y):
        returnList = []
        for n in range(1, 10):
            if self.validMove(puzzle, x, y, n):
                returnList.append(n)  # []
        return returnList


    def solvePuzzleStep(self, puzzle):
        isChanged = False
        for y in range(9):
            for x in range(9):
                if puzzle[x][y] == 0:
                    allMoves = self.findallMoves(puzzle, x, y)
                    if len(allMoves) == 1:
                        puzzle[x][y] = allMoves[0]
                        isChanged = True
        return isChanged


    # try to solve as much as possible without lookahead
    def solvePuzzleSimple(self, puzzle):
        iterationCount = 0
        while self.solvePuzzleStep(puzzle) == True:
            iterationCount += 1




    def calc_hash(self, puzzle):
        hashcode = 0
        for c in range(9):
            hashcode = hashcode * 17 + hash(tuple(puzzle[c]))
        return hashcode


    def hash_add(self, puzzle):
        self.hashtable[self.calc_hash(puzzle)] = 1


    def hash_lookup(self, puzzle):
        return self.calc_hash(puzzle) in self.hashtable


    # solve with lookahead
    # unit is 3x3, (i,j) is coords of unit. l is the list of all todo's
    def perm(self, puzzle, i, j, l, u):
        self.iterations += 1
        if (u == []) and (l == []):
            print("Solved!")  # [str]
            # printpuzzle(puzzle)      # []
            print("iterations: ", self.iterations)  # [str], [int]
            return True
        else:
            if l == []:
                # here we have all permutations for one unit

                # some simple moves
                puzzlebackup = []
                for c in range(9):
                    puzzlebackup.append(tuple(puzzle[c]))  # []
                self.solvePuzzleSimple(puzzle)  # []

                # next unit to fill
                for c in range(len(u)):
                    if not self.hash_lookup(puzzle):
                        inew, jnew = u.pop(c)  # [tuple(int)]
                        l = self.genMoveList(puzzle, inew, jnew)
                        # only print new situations
                        # print "inew, jnew, l, u:", inew, jnew, l, u # [str], [int], [int], [list(int)], [list(tuple(int))]
                        # printpuzzle(puzzle) # []
                        # print "self.iterations: ", self.iterations # [str], [int]
                        if self.perm(puzzle, inew, jnew, l, u):
                            return True
                        else:
                            self.hash_add(puzzle)  # []
                        u.insert(c, (inew, jnew))  # []

                # undo simple moves
                for y in range(9):
                    for x in range(9):
                        puzzle[x][y] = puzzlebackup[x][y]
                self.hash_add(puzzle)  # []
                return False
            else:
                # try all possibilities of one unit
                ii = i * 3
                jj = j * 3
                for m in range(len(l)):
                    # find first empty
                    for y in range(3):
                        for x in range(3):
                            if self.validMove(puzzle, x + ii, y + jj, l[m]):
                                puzzle[x + ii][y + jj] = l[m]
                                backup = l.pop(m)
                                if self.perm(puzzle, i, j, l, u):
                                    return True
                                else:
                                    self.hash_add(puzzle)  # []
                                l.insert(m, backup)  # []
                                puzzle[x + ii][y + jj] = 0
                return False


    # gen move list for unit (i,j)
    def genMoveList(self, puzzle, i, j):
        l = list(range(1, 10))
        for y in range(3):
            for x in range(3):
                p = puzzle[i * 3 + x][j * 3 + y]
                if p != 0:
                    l.remove(p)  # []
        return l


    def printpuzzle(self, puzzle):
        for x in range(9):
            s = " "  # [str]
            for y in range(9):
                p = puzzle[x][y]
                if p == 0:
                    s += "."  # [str]
                else:
                    s += str(puzzle[x][y])  # [str]
                s += " "  # [str]
            print(s)  # [str]


    def play(self):
        puzzle = [
            [0, 9, 3, 0, 8, 0, 4, 0, 0],  # [list(list(int))]
            [0, 4, 0, 0, 3, 0, 0, 0, 0],
            [6, 0, 0, 0, 0, 9, 2, 0, 5],
            [3, 0, 0, 0, 0, 0, 0, 9, 0],
            [0, 2, 7, 0, 0, 0, 5, 1, 0],
            [0, 8, 0, 0, 0, 0, 0, 0, 4],
            [7, 0, 1, 6, 0, 0, 0, 0, 2],
            [0, 0, 0, 0, 7, 0, 0, 6, 0],
            [0, 0, 4, 0, 1, 0, 8, 5, 0],
        ]

        # create todo unit(each 3x3) list (this is also the order that they will be tried!)
        u = []
        lcount = []
        for y in range(3):
            for x in range(3):
                u.append((x, y))
                lcount.append(len(self.genMoveList(puzzle, x, y)))

        # sort
        for j in range(0, 9):
            for i in range(j, 9):
                if i != j:
                    if lcount[i] < lcount[j]:
                        u[i], u[j] = u[j], u[i]
                        lcount[i], lcount[j] = lcount[j], lcount[i]

        l = self.genMoveList(puzzle, 0, 0)
        self.perm(puzzle, 0, 0, l, u)
        return self.iterations



def test_puzzle():
  
    # for x in range(30):
    #     main()  # []
    game = PuzzlGame()
    assert game.play() == 184


def test_all():
    test_puzzle()
    

if __name__ == '__main__':
    test_all() 

