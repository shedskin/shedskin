# (c) Jack Ha
# --- jack.ha@gmail.com
#
# sudoku solver

def validMove(puzzle, x, y, number):     # puzzle: [list(list(int))], x: [int], y: [int], number: [int]
        #see if the number is in any row, column or his own 3x3 square
        blnOK = True                     # [int]
        px = x / 3                       # [int]
        py = y / 3                       # [int]
        if puzzle[x][y] != 0:            # [int]
                blnOK = False            # [int]
        if blnOK:                        # []
                for i in range(9):       # [list(int)]
                        if puzzle[i][y] == number: # [int]
                                blnOK = False # [int]
        if blnOK:                        # []
                for j in range(9):       # [list(int)]
                        if puzzle[x][j] == number: # [int]
                                blnOK = False # [int]
        if blnOK:                        # []
                for i in range(3):       # [list(int)]
                        for j in range(3): # [list(int)]
                                if puzzle[px*3+i][py*3+j] == number: # [int]
                                        blnOK = False # [int]
        return blnOK                     # [int]

def findallMoves(puzzle,x,y):            # puzzle: [list(list(int))], x: [int], y: [int]
        returnList = []                  # [list(int)]
        for n in range(1,10):            # [list(int)]
                if validMove(puzzle, x, y, n): # [int]
                        returnList.append(n) # []
        return returnList                # [list(int)]

def solvePuzzleStep(puzzle):             # puzzle: [list(list(int))]
        isChanged = False                # [int]
        for y in range(9):               # [list(int)]
                for x in range(9):       # [list(int)]
                        if puzzle[x][y] == 0: # [int]
                                allMoves = findallMoves(puzzle, x, y) # [list(int)]
                                if len(allMoves) == 1: # [int]
                                        puzzle[x][y] = allMoves[0] # [int]
                                        isChanged = True # [int]
        return isChanged                 # [int]

#try to solve as much as possible without lookahead
def solvePuzzleSimple(puzzle):           # puzzle: [list(list(int))]
        iterationCount = 0               # [int]
        while solvePuzzleStep(puzzle) == True: # [int]
                iterationCount += 1      # [int]

hashtable = {}                           # [dict(int, int)]

def calc_hash(puzzle):                   # puzzle: [list(list(int))]
        hashcode = 0                     # [int]
        for c in range(9):               # [list(int)]
                hashcode = hashcode * 17 + hash(tuple(puzzle[c])) # [int]
        return hashcode                  # [int]

def hash_add(puzzle):                    # puzzle: [list(list(int))]
        hashtable[calc_hash(puzzle)] = 1 # [int]

def hash_lookup(puzzle):                 # puzzle: [list(list(int))]
        return hashtable.has_key(calc_hash(puzzle)) # [int]

#solve with lookahead
#unit is 3x3, (i,j) is coords of unit. l is the list of all todo's
def perm(puzzle, i, j, l, u):            # puzzle: [list(list(int))], i: [int], j: [int], l: [list(int)], u: [list(tuple(int))]
        global iterations
        iterations += 1                  # [int]
        if (u == []) and (l == []):      # [int]
                print "Solved!"          # [str]
                #printpuzzle(puzzle)      # []
                print "iterations: ", iterations # [str], [int]
                return True              # [int]
        else:
                if l == []:              # [int]
                        #here we have all permutations for one unit

                        #some simple moves
                        puzzlebackup = [] # [list(tuple(int))]
                        for c in range(9): # [list(int)]
                                puzzlebackup.append(tuple(puzzle[c])) # []
                        solvePuzzleSimple(puzzle) # []

                        #next unit to fill
                        for c in range(len(u)): # [list(int)]
                                if not hash_lookup(puzzle): # [int]
                                        inew, jnew = u.pop(c) # [tuple(int)]
                                        l = genMoveList(puzzle, inew, jnew) # [list(int)]
                                        #only print new situations
                                        #print "inew, jnew, l, u:", inew, jnew, l, u # [str], [int], [int], [list(int)], [list(tuple(int))]
                                        #printpuzzle(puzzle) # []
                                        #print "iterations: ", iterations # [str], [int]
                                        if perm (puzzle, inew, jnew, l, u): # [int]
                                                return True # [int]
                                        else:
                                                hash_add(puzzle) # []
                                        u.insert(c, (inew, jnew)) # []

                        #undo simple moves
                        for y in range(9): # [list(int)]
                                for x in range(9): # [list(int)]
                                        puzzle[x][y] = puzzlebackup[x][y] # [int]
                        hash_add(puzzle) # []
                        return False     # [int]
                else:
                        #try all possibilities of one unit
                        ii = i * 3       # [int]
                        jj = j * 3       # [int]
                        for m in range(len(l)): # [list(int)]
                                #find first empty
                                for y in range(3): # [list(int)]
                                        for x in range(3): # [list(int)]
                                                if validMove(puzzle, x+ii, y+jj, l[m]): # [int]
                                                        puzzle[x+ii][y+jj] = l[m] # [int]
                                                        backup = l.pop(m) # [int]
                                                        if (perm(puzzle, i, j, l, u)): # [int]
                                                                return True # [int]
                                                        else:
                                                                hash_add(puzzle) # []
                                                        l.insert(m, backup) # []
                                                        puzzle[x+ii][y+jj] = 0 # [int]
                        return False     # [int]

#gen move list for unit (i,j)
def genMoveList(puzzle, i, j):           # puzzle: [list(list(int))], i: [int], j: [int]
        l = range(1,10)                  # [list(int)]
        for y in range(3):               # [list(int)]
                for x in range(3):       # [list(int)]
                        p = puzzle[i*3+x][j*3+y] # [int]
                        if p != 0:       # [int]
                                l.remove(p) # []
        return l                         # [list(int)]

def printpuzzle(puzzle):                 # puzzle: [list(list(int))]
        for x in range(9):               # [list(int)]
                s = ' '                  # [str]
                for y in range(9):       # [list(int)]
                        p = puzzle[x][y] # [int]
                        if p == 0:       # [int]
                                s += '.' # [str]
                        else:
                                s += str(puzzle[x][y]) # [str]
                        s += ' '         # [str]
                print s                  # [str]

def main():
        puzzle = [[0, 9, 3, 0, 8, 0, 4, 0, 0], # [list(list(int))]
                          [0, 4, 0, 0, 3, 0, 0, 0, 0], # [list(int)]
                          [6, 0, 0, 0, 0, 9, 2, 0, 5], # [list(int)]
                          [3, 0, 0, 0, 0, 0, 0, 9, 0], # [list(int)]
                          [0, 2, 7, 0, 0, 0, 5, 1, 0], # [list(int)]
                          [0, 8, 0, 0, 0, 0, 0, 0, 4], # [list(int)]
                          [7, 0, 1, 6, 0, 0, 0, 0, 2], # [list(int)]
                          [0, 0, 0, 0, 7, 0, 0, 6, 0], # [list(int)]
                          [0, 0, 4, 0, 1, 0, 8, 5, 0]] # [list(int)]

        #create todo unit(each 3x3) list (this is also the order that they will be tried!)
        u = []                           # [list(tuple(int))]
        lcount = []                      # [list(int)]
        for y in range(3):               # [list(int)]
                for x in range(3):       # [list(int)]
                        u.append((x,y))  # []
                        lcount.append(len(genMoveList(puzzle, x, y))) # []

        #sort
        for j in range(0,9):             # [list(int)]
                for i in range(j,9):     # [list(int)]
                        if i != j:       # [int]
                                if lcount[i] < lcount[j]: # [int]
                                        u[i], u[j] = u[j], u[i]
                                        lcount[i], lcount[j] = lcount[j], lcount[i]

        l = genMoveList(puzzle, 0, 0)    # [list(int)]
        perm (puzzle, 0, 0, l, u)        # [int]

iterations = 0                           # [int]
for x in range(30):
    main()                                   # []

