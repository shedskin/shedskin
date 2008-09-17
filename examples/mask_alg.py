# (c) Mark Dufour
# --- mark.dufour@gmail.com
#
# simple sat solver

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

argv = ['','testdata/uuf250-010.cnf']             # [list(str)]

# solver

cnf = [l.strip().split() for l in file(argv[1]) if l[0] not in 'c0%\n'] # [list(list(str))]
clauses = [[int(x) for x in l[:-1] if x != ''] for l in cnf if l[0] != 'p'] # [list(list(int))]
nrofvars = [int(l[2]) for l in cnf if l[0] == 'p'][0] # [int]
vars = range(nrofvars+1)                 # [list(int)]
occurrence = [[] for l in 2*vars] 
for clause in clauses:                   # [list(int)]
    for lit in clause: occurrence[lit].append(clause) # [int]
fixedt = [-1 for var in vars]            # [list(int)]

nodecount, propcount = 0, 0              # [int], [int]

def solve_rec():                         # la_mods: [list(int)], var: [int], prop_mods: [list(int)], choice: [int]*
    global nodecount
    nodecount += 1                       # []
    if nodecount == 100:
        return 1

    if not -1 in fixedt[1:]:             # [int]
        print 'v', ' '.join([str((2*fixedt[i]-1)*i) for i in range(1,nrofvars+1)]) # [list(str)]
        return 1                         # [int]

    la_mods = []                         # [list(int)]
    var = lookahead(la_mods)             # [int]
    #print 'select', var                  # [str], [int]
    if not var: return backtrack(la_mods) # [int]

    for choice in [var,-var]:            # [int]
        prop_mods = []                   # [list(int)]
        if propagate(choice, prop_mods) and solve_rec(): return 1 # [int]
        backtrack(prop_mods)             # [int]

    return backtrack(la_mods)            # [int]

def propagate(lit, mods, failed_literal=0): # lit_truth: [int], current: [int], unfixed: [int]*, mods: [list(int)], clause: [list(int)], lit: [int]*, length: [int], failed_literal: [int]
    global bincount, propcount
    current = len(mods)                  # [int]
    mods.append(lit)                     # [None]
    #print 'prop', lit                    # [str], [int]

    while 1:                             # [int]
        if fixedt[abs(lit)] == -1:       # [int]
            fixedt[abs(lit)] = (lit>0)   # [int]
            propcount += 1               # []
            mask_propagate(lit)          # []
                
            for clause in occurrence[-lit]: # [list(int)]
                length, unfixed = info(clause) # [tuple(int)]

                if length == 0:          # [int]
                    #print 'dead', lit    # [str], [int]
                    return 0             # [int]
                elif length == 1: mods.append(unfixed) # [None]
                elif length == 2:        # [int]
                    bincount += 1        # []
                    if failed_literal: mask_binclause(unfixed_lits(clause)) # []

        elif fixedt[abs(lit)] != (lit>0): return 0 # [int]

        current += 1                     # []
        if current == len(mods): break   # [int]
        lit = mods[current]              # [int]

    return 1                             # [int]

def mask_propagate(lit):                 # lit: [int]
    global lit_mask, part_mask # XXX 
    lit_mask[lit] |= part_mask           # []

def mask_binclause(lits):                # lit: [int], lits: [list(int)]
    global global_mask, lit_mask # XXX
    for lit in lits: global_mask |= lit_mask[-lit] # [int]

def lookahead(mods):                     # mods: [list(int)], i: [int], u: [list(int)], var: [int], part: [list(int)]
    global global_mask, lit_mask, part_mask, some_failure 

    global_mask = 2**32-1                # [int]
    lit_mask = [0 for var in range(2*(nrofvars+1))] # [list(int)]
    u = unfixed_vars()                   # [list(int)]

    parts = [u[(i*len(u))>>5:((i+1)*len(u))>>5] for i in range(32)] # [list(list(int))]
    masks = [1<<i for i in range(32)]    # [list(int)]

    some_failure = 0                     # [int]
    dif = [-1 for var in range(nrofvars+1)] # [list(int)]

    while global_mask != 0:              # [int]
        #print 'next iteration'           # [str]
        #print binstr(global_mask)        # [str]

        lit_mask = [m & (2**32-1-global_mask) for m in lit_mask] # [list(int)]
	
        for i in range(32):              # [int]
            part, part_mask = parts[i], masks[i] # [list(int)], [int]
            
            if global_mask & part_mask == 0: # [int]
                #print 'skip', part_mask  # [str], [int]
                continue
            global_mask &= (2**32-1) ^ part_mask # []
            for var in part:             # [int]
	            if fixedt[var] == -1 and not lookahead_variable(var, mods, dif): return 0 # [int]

    if some_failure:                     # [int]
        #print 'final iteration'          # [str]
        dif = [-1 for var in range(nrofvars+1)] # [list(int)]
        for var in unfixed_vars():       # [int]
            if not lookahead_variable(var, mods, dif): # [int]
                 print 'error'           # [str]
    return dif.index(max(dif))           # [int]

def lookahead_variable(var, mods, dif):  # mods: [list(int)], dif: [list(int)], choice: [int]*, var: [int], prop: [int]
    global bincount, some_failure
    score = []                           # [list(int)]
    
    for choice in [var,-var]:            # [int]
        prop_mods = []                   # [list(int)]
        bincount = 0                     # [int]
        prop = propagate(choice, prop_mods) # [int]
        backtrack(prop_mods)             # [int]
        if not prop:                     # [int]
#            print 'failed literal', choice
            some_failure = 1             # [int]
            if not propagate(-choice, mods, 1): return 0 # [int]
            break
        score.append(bincount)           # [None]
	    
    dif[var] = reduce(lambda x,y: 1024*x*y+x+y, score, 0) # [int]
    return 1                             # [int]

def backtrack(mods):                     # lit: [int], mods: [list(int)]
    for lit in mods: fixedt[abs(lit)] = -1 # [int]
    return 0                             # [int]

def info(clause):                        # lit: [int], clause: [list(int)], unfixed: [int], len: [int]
    len, unfixed = 0, 0                  # [int], [int]
    for lit in clause:                   # [int]
        if fixedt[abs(lit)] == -1: unfixed, len = lit, len+1 # [int], [int]
        elif fixedt[abs(lit)] == (lit>0): return -1, 0 # [tuple(int)]
    return len, unfixed                  # [tuple(int)]

def unfixed_vars(): 
    return [var for var in range(1,nrofvars+1) if fixedt[var] == -1] # [list(int)]

def unfixed_lits(clause):                # lit: [int]*, clause: [list(int)], result: [list(int)]r
    result = []                          # [list(int)]
    for lit in clause:                   # [int]
        if fixedt[abs(lit)] == -1: result.append(lit) # [None]
    return result                        # [list(int)]

if not solve_rec():                      # [int]
    print 'unsatisfiable'                # [str]
print 'nodes', nodecount, 'propagations', propcount # [str], [int], [str], [int]

