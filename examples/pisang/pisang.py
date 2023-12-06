from functools import reduce
# pisang - a simple sat solver in Python
# (c) mark.dufour@gmail.com

argv = ['','testdata/uuf250-010.cnf']

cnf = [l.strip().split() for l in open(argv[1]) if l[0] not in 'c%0\n']
clauses = [[int(x) for x in m[:-1]] for m in cnf if m[0] != 'p']
nrofvars = [int(n[2]) for n in cnf if n[0] == 'p'][0]
vars = list(range(nrofvars+1))
occurrence = [[] for l in vars+list(range(-nrofvars,0))]
for clause in clauses:
    for lit in clause: occurrence[lit].append(clause)
fixedt = [-1 for var in vars]

def solve_rec():
    global nodecount
    nodecount += 1

    if -1 not in fixedt[1:]:
        print('v', ' '.join([str((2*fixedt[i]-1)*i) for i in vars[1:]]))
        return 1

    la_mods = []
    var = lookahead(la_mods)
    if not var:
        return backtrack(la_mods)
    for choice in [var, -var]:
        prop_mods = []
        if propagate(choice, prop_mods) and solve_rec():
            return 1
        backtrack(prop_mods)
    return backtrack(la_mods)

def propagate(lit, mods):
    global bincount

    current = len(mods)
    mods.append(lit)

    while 1:
        if fixedt[abs(lit)] == -1:
            fixedt[abs(lit)] = int(lit>0)
            for clause in occurrence[-lit]:
                cl_len = length(clause)
                if cl_len == 0:
                    return 0
                elif cl_len == 1:
                    mods.append(unfixed(clause))
                elif cl_len == 2:
                    bincount += 1

        elif fixedt[abs(lit)] != int(lit>0):
            return 0

        current += 1
        if current == len(mods):
            break
        lit = mods[current]

    return 1

def lookahead(mods):
    global bincount

    dif = [-1 for var in vars]
    for var in unfixed_vars():
        score = []
        for choice in [var, -var]:
            prop_mods = []
            bincount = 0
            prop = propagate(choice, prop_mods)
            backtrack(prop_mods)
            if not prop:
                if not propagate(-choice, mods):
                    return 0
                break
            score.append(bincount)
        dif[var] = reduce(lambda x, y: 1024*x*y+x+y, score, 0)

    return dif.index(max(dif))

def backtrack(mods):
    for lit in mods:
        fixedt[abs(lit)] = -1
    return 0

def length(clause):
    len = 0
    for lit in clause:
        fixed = fixedt[abs(lit)]
        if fixed == int(lit>0):
            return -1
        if fixed == -1:
            len += 1
    return len

def unfixed(clause):
    for lit in clause:
        fixed = fixedt[abs(lit)]
        if fixed == -1:
            return lit

def unfixed_vars():
    return [var for var in vars[1:] if fixedt[var] == -1]

nodecount = 0
if not solve_rec():
    print('unsatisfiable', nodecount)
