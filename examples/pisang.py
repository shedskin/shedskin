# (c) Mark Dufour 
# --- mark.dufour@gmail.com
# 
# pisang - a simple sat solver in Python

def reduce(f, l, i=-1):                  # f: [lambda0], i: [int], l: [list(int)], r: [int]
    if not l:                            # [list(int)]
        if i != -1: return i             # [int]
        print '*** ERROR! *** reduce() called with empty sequence and no initial value' # [str]

    if i != -1:                          # [int]
        r = f(i, l[0])                   # [int]
    else:
        r = l[0]                         # [int]

    for i in range(len(l)-1):            # [int]
        r = f(r, l[i+1])                 # [int]

    return r                             # [int]

# prelims

argv = ['','testdata/uuf250-010.cnf']             # [list(str)]

cnf = [l.strip().split() for l in file(argv[1]) if l[0] not in 'c%0\n'] # [list(list(str))]
clauses = [[int(x) for x in m[:-1]] for m in cnf if m[0] != 'p'] # [list(list(int))]
nrofvars = [int(n[2]) for n in cnf if n[0] == 'p'][0] # [int]
vars = range(nrofvars+1)                 # [list(int)]
occurrence = [[] for l in vars+range(-nrofvars,0)] # [list(list(list(int)))]
for clause in clauses:                   # [list(int)]
    for lit in clause: occurrence[lit].append(clause) # [int]
fixedt = [-1 for var in vars]            # [list(int)]

def solve_rec():                         # la_mods: [list(int)], var: [int], prop_mods: [list(int)], choice: [int]
    global nodecount
    nodecount += 1                       # []
    if not -1 in fixedt[1:]:             # [int]
        print 'v', ' '.join([str((2*fixedt[i]-1)*i) for i in vars[1:]]) # [str], [str]
        return 1                         # [int]

    la_mods = []                         # [list(int)]
    var = lookahead(la_mods)             # [int]
    #print 'select', var                  # [str], [int]
    if not var: return backtrack(la_mods) # [int]

    for choice in [var, -var]:           # [int]
        prop_mods = []                   # [list(int)]
        if propagate(choice, prop_mods) and solve_rec(): return 1 # [int]
        backtrack(prop_mods)             # [int]

    return backtrack(la_mods)            # [int]

def propagate(lit, mods):                # current: [int], unfixed: [int], mods: [list(int)], clause: [list(int)], lit: [int], length: [int]
    global bincount

    current = len(mods)                  # [int]
    mods.append(lit)                     # []

    while 1:                             # [int]
        if fixedt[abs(lit)] == -1:       # [int]
            fixedt[abs(lit)] = (lit>0)   # [int]
            for clause in occurrence[-lit]: # [list(int)]
                length, unfixed = info(clause) # [tuple(int)]
                
                if length == 0: return 0 # [int]
                elif length == 1: mods.append(unfixed) # []
                elif length == 2: bincount += 1 # []

        elif fixedt[abs(lit)] != (lit>0): return 0 # [int]

        current += 1                     # []
        if current == len(mods): break   # [int]
        lit = mods[current]              # [int]

    return 1                             # [int]

def lookahead(mods):                     # mods: [list(int)], dif: [list(int)], choice: [int], score: [list(int)], prop_mods: [list(int)], var: [int], prop: [int]
    global bincount

    dif = [-1 for var in vars]           # [list(int)]
    for var in unfixed_vars():           # [int]
        score = []                       # [list(int)]
        for choice in [var, -var]:       # [int]
            prop_mods = []               # [list(int)]
            bincount = 0                 # [int]
            prop = propagate(choice, prop_mods) # [int]
            backtrack(prop_mods)         # [int]
            if not prop:                 # [int]
                if not propagate(-choice, mods): return 0 # [int]
                break
            score.append(bincount)       # []
        dif[var] = reduce(lambda x, y: 1024*x*y+x+y, score, 0) # [int]
 
    return dif.index(max(dif))           # [int]

def backtrack(mods):                     # lit: [int], mods: [list(int)]
    for lit in mods: fixedt[abs(lit)] = -1 # [int]
    return 0                             # [int]

def info(clause):                        # lit: [int], clause: [list(int)], unfixed: [int], len: [int]
    len, unfixed = 0, 0                  # [int], [int]
    for lit in clause:                   # [int]
        if fixedt[abs(lit)] == -1: unfixed, len = lit, len+1 # [int], [int]
        elif fixedt[abs(lit)] == (lit>0): return -1, 0 # [tuple(int)]
    return len, unfixed                  # [tuple(int)]

def unfixed_vars(): return [var for var in vars[1:] if fixedt[var] == -1] # [list(int)]
    
nodecount = 0                            # [int]
if not solve_rec():                      # [int]
    print 'unsatisfiable', nodecount     # [str], [int]

