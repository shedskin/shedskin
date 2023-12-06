# (c) Mark Dufour
# --- mark.dufour@gmail.com

import os

if os.path.exists("testdata"):
    testdata = "testdata"
elif os.path.exists("../testdata"):
    testdata = "../testdata"
else:
    testdata = "../../testdata"

datafile = os.path.join(testdata, 'uuf250-010.cnf')

def _reduce(f, l, i=-1):
    if not l:
        if i != -1:
            return i
        print(
            "*** ERROR! *** reduce() called with empty sequence and no initial value"
        )

    if i != -1:
        r = f(i, l[0])
    else:
        r = l[0]

    for i in range(len(l) - 1):
        r = f(r, l[i + 1])

    return r

class Satisfier:
    def __init__(self, argv=None):
        self.argv = argv or ["", datafile]
        cnf = [
            l.strip().split() for l in open(self.argv[1]) if l[0] not in "c%0\n"
        ]
        clauses = [[int(x) for x in m[:-1]] for m in cnf if m[0] != "p"]
        nrofvars = [int(n[2]) for n in cnf if n[0] == "p"][0]
        self.vars = list(range(nrofvars + 1))
        self.occurrence = [[] for l in self.vars + list(range(-nrofvars, 0))]
        for clause in clauses:
            for lit in clause:
                self.occurrence[lit].append(clause)
        self.fixedt = [-1 for var in self.vars]
        self.nodecount = 0
        self.bincount = 0


    def solve_rec(self):
        self.nodecount += 1  # []
        if self.nodecount == 100:
            return 1
        if -1 not in self.fixedt[1:]:  # [int]
            print(
                "v", " ".join([str((2 * self.fixedt[i] - 1) * i) for i in self.vars[1:]])
            )
            return 1

        la_mods = []
        var = self.lookahead(la_mods)
        # print 'select', var
        if not var:
            return self.backtrack(la_mods)

        for choice in [var, -var]:
            prop_mods = []
            if self.propagate(choice, prop_mods) and self.solve_rec():
                return 1
            self.backtrack(prop_mods)  # [int]

        return self.backtrack(la_mods)  # [int]


    def propagate(self, lit, mods):
        current = len(mods)  # [int]
        mods.append(lit)  # []

        while 1:  # [int]
            if self.fixedt[abs(lit)] == -1:  # [int]
                self.fixedt[abs(lit)] = int(lit > 0)  # [int]
                for clause in self.occurrence[-lit]:  # [list(int)]
                    length, unfixed = self.info(clause)  # [tuple(int)]

                    if length == 0:
                        return 0  # [int]
                    elif length == 1:
                        mods.append(unfixed)  # []
                    elif length == 2:
                        self.bincount += 1  # []

            elif self.fixedt[abs(lit)] != int(lit > 0):
                return 0  # [int]

            current += 1  # []
            if current == len(mods):
                break  # [int]
            lit = mods[current]  # [int]

        return 1  # [int]


    def lookahead(self, mods):

        dif = [-1 for var in self.vars]
        for var in self.unfixed_vars():
            score = []
            for choice in [var, -var]:
                prop_mods = []
                self.bincount = 0
                prop = self.propagate(choice, prop_mods)
                self.backtrack(prop_mods)
                if not prop:
                    if not self.propagate(-choice, mods):
                        return 0
                    break
                score.append(self.bincount)
            dif[var] = _reduce(lambda x, y: 1024 * x * y + x + y, score, 0)

        return dif.index(max(dif))


    def backtrack(self, mods):
        for lit in mods:
            self.fixedt[abs(lit)] = -1
        return 0


    def info(self, clause):
        len, unfixed = 0, 0
        for lit in clause:
            if self.fixedt[abs(lit)] == -1:
                unfixed, len = lit, len + 1
            elif self.fixedt[abs(lit)] == int(lit > 0):
                return -1, 0
        return len, unfixed


    def unfixed_vars(self):
        return [var for var in self.vars[1:] if self.fixedt[var] == -1]

    def run(self):
        self.nodecount = 0
        if not self.solve_rec():
            return "unsatisfiable", self.nodecount
        else:
            return "satisfiable", self.nodecount


def test_satisfy():
    game = Satisfier()
    assert game.run() == ("satisfiable", 100)


def test_all():
    test_satisfy()
    

if __name__ == '__main__':
    test_all() 

