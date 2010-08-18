
argv = ['','testdata/uuf250-010.cnf']             # [list(str)]

cnf = [l.strip().split() for l in file(argv[1]) if l[0] not in 'c%0\n']
clauses = [[int(x) for x in m[:-1]] for m in cnf if m[0] != 'p']
nrofvars = [int(n[2]) for n in cnf if n[0] == 'p'][0]
vars = range(nrofvars+1)
occurrence = [[[c for c in clauses if -v in c],[c for c in clauses if v in c]] for v in vars]
fixedt = [-1 for var in vars]

