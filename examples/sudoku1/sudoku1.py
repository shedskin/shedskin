# (c) Jack Ha
# --- jack.ha@gmail.com
#
# sudoku solver


def validMove(puzzle, x, y, number):
    # see if the number is in any row, column or his own 3x3 square
    blnOK = True
    px = x // 3
    py = y // 3
    if puzzle[x][y] != 0:
        blnOK = False
    if blnOK:
        for i in range(9):
            if puzzle[i][y] == number:
                blnOK = False
    if blnOK:
        for j in range(9):
            if puzzle[x][j] == number:
                blnOK = False
    if blnOK:
        for i in range(3):
            for j in range(3):
                if puzzle[px * 3 + i][py * 3 + j] == number:
                    blnOK = False
    return blnOK


def findallMoves(puzzle, x, y):
    returnList = []
    for n in range(1, 10):
        if validMove(puzzle, x, y, n):
            returnList.append(n)
    return returnList


def solvePuzzleStep(puzzle):
    isChanged = False
    for y in range(9):
        for x in range(9):
            if puzzle[x][y] == 0:
                allMoves = findallMoves(puzzle, x, y)
                if len(allMoves) == 1:
                    puzzle[x][y] = allMoves[0]
                    isChanged = True
    return isChanged


# try to solve as much as possible without lookahead
def solvePuzzleSimple(puzzle):
    iterationCount = 0
    while solvePuzzleStep(puzzle) == True:
        iterationCount += 1


hashtable = {}


def calc_hash(puzzle):
    hashcode = 0
    for c in range(9):
        hashcode = hashcode * 17 + hash(tuple(puzzle[c]))
    return hashcode


def hash_add(puzzle):
    hashtable[calc_hash(puzzle)] = 1


def hash_lookup(puzzle):
    return calc_hash(puzzle) in hashtable


# solve with lookahead
# unit is 3x3, (i,j) is coords of unit. l is the list of all todo's
def perm(puzzle, i, j, l, u):
    global iterations
    iterations += 1
    # print(u,l)
    if (u == []) and (l == []):
        print("Solved!")
        printpuzzle(puzzle)
        print("iterations: ", iterations)
        return True
    else:
        if l == []:
            # here we have all permutations for one unit

            # some simple moves
            puzzlebackup = []
            for c in range(9):
                puzzlebackup.append(tuple(puzzle[c]))
            solvePuzzleSimple(puzzle)

            # next unit to fill
            for c in range(len(u)):
                if not hash_lookup(puzzle):
                    inew, jnew = u.pop(c)
                    l = genMoveList(puzzle, inew, jnew)
                    # printpuzzle(puzzle)
                    # print "iterations: ", iterations
                    if perm(puzzle, inew, jnew, l, u):
                        return True
                    else:
                        hash_add(puzzle)
                    u.insert(c, (inew, jnew))

            # undo simple moves
            for y in range(9):
                for x in range(9):
                    puzzle[x][y] = puzzlebackup[x][y]
            hash_add(puzzle)
            return False
        else:
            # try all possibilities of one unit
            ii = i * 3
            jj = j * 3
            for m in range(len(l)):
                # find first empty
                for y in range(3):
                    for x in range(3):
                        if validMove(puzzle, x + ii, y + jj, l[m]):
                            puzzle[x + ii][y + jj] = l[m]
                            backup = l.pop(m)
                            if perm(puzzle, i, j, l, u):
                                return True
                            else:
                                hash_add(puzzle)
                            l.insert(m, backup)
                            puzzle[x + ii][y + jj] = 0
            return False


# gen move list for unit (i,j)
def genMoveList(puzzle, i, j):
    l = list(range(1, 10))
    for y in range(3):
        for x in range(3):
            p = puzzle[i * 3 + x][j * 3 + y]
            if p != 0:
                l.remove(p)
    return l


def printpuzzle(puzzle):
    for x in range(9):
        s = " "
        for y in range(9):
            p = puzzle[x][y]
            if p == 0:
                s += "."
            else:
                s += str(puzzle[x][y])
            s += " "
        print(s)


def main():
    puzzle = [
        [0, 9, 3, 0, 8, 0, 4, 0, 0],
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
            lcount.append(len(genMoveList(puzzle, x, y)))

    # sort
    for j in range(0, 9):
        for i in range(j, 9):
            if i != j:
                if lcount[i] < lcount[j]:
                    u[i], u[j] = u[j], u[i]
                    lcount[i], lcount[j] = lcount[j], lcount[i]

    l = genMoveList(puzzle, 0, 0)
    perm(puzzle, 0, 0, l, u)


iterations = 0
for x in range(30):
    main()
