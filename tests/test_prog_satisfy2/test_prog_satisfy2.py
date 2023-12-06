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


hoppa = 0xFFFFFFFF


def _reduce(f, l, i=-1):
    if not l:
        if i != -1:
            return i
        print(
            "*** ERROR! *** reduce() called with empty sequence and no initial value"
        )  # [str]

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
            l.strip().split() for l in open(self.argv[1]) if l[0] not in "c0%\n"
        ]
        clauses = [
            [int(x) for x in l[:-1] if x != ""] for l in cnf if l[0] != "p"
        ]
        self.nrofvars = [int(l[2]) for l in cnf if l[0] == "p"][0]
        vars = list(range(self.nrofvars + 1))
        self.occurrence = [[] for l in 2 * vars]
        for clause in clauses:
            for lit in clause:
                self.occurrence[lit].append(clause)
        self.fixedt = [-1 for var in vars]

        self.nodecount = 0
        self.propcount = 0
        self.lit_mask = []
        self.part_mask = 0
        self.global_mask = 0
        self.some_failure = 0

    def solve_rec(self):
        self.nodecount += 1
        if self.nodecount == 100:
            return 1

        if -1 not in self.fixedt[1:]:
            print(
                "v",
                " ".join([str((2 * self.fixedt[i] - 1) * i) for i in range(1, self.nrofvars + 1)]),
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
            self.backtrack(prop_mods)

        return self.backtrack(la_mods)


    def propagate(self, lit, mods, failed_literal=0):
        current = len(mods)
        mods.append(lit)
        # print 'prop', lit

        while 1:
            if self.fixedt[abs(lit)] == -1:
                self.fixedt[abs(lit)] = int(lit > 0)
                self.propcount += 1  # []
                self.mask_propagate(lit)  # []

                for clause in self.occurrence[-lit]:
                    length, unfixed = self.info(clause)

                    if length == 0:
                        # print 'dead', lit
                        return 0
                    elif length == 1:
                        mods.append(unfixed)
                    elif length == 2:
                        self.bincount += 1  # []
                        if failed_literal:
                            self.mask_binclause(self.unfixed_lits(clause))

            elif self.fixedt[abs(lit)] != int(lit > 0):
                return 0

            current += 1  # []
            if current == len(mods):
                break
            lit = mods[current]

        return 1


    def mask_propagate(self, lit):
        self.lit_mask[lit] |= self.part_mask


    def mask_binclause(self, lits):
        for lit in lits:
            self.global_mask |= self.lit_mask[-lit]

    def lookahead(self, mods):

        self.global_mask = hoppa
        self.lit_mask = [0 for var in range(2 * (self.nrofvars + 1))]
        u = self.unfixed_vars()

        parts = [
            u[(i * len(u)) >> 5 : ((i + 1) * len(u)) >> 5] for i in range(32)
        ]
        masks = [1 << i for i in range(32)]

        self.some_failure = 0
        dif = [-1 for var in range(self.nrofvars + 1)]

        while self.global_mask != 0:
            # print 'next iteration'
            # print binstr(global_mask)

            self.lit_mask = [m & (hoppa - self.global_mask) for m in self.lit_mask]

            for i in range(32):
                part, self.part_mask = parts[i], masks[i]

                if self.global_mask & self.part_mask == 0:
                    # print 'skip', part_mask  # [str], [int]
                    continue
                self.global_mask &= (hoppa) ^ self.part_mask
                for var in part:
                    if self.fixedt[var] == -1 and not self.lookahead_variable(var, mods, dif):
                        return 0

        if self.some_failure:
            # print 'final iteration'          # [str]
            dif = [-1 for var in range(self.nrofvars + 1)]  # [list(int)]
            for var in self.unfixed_vars():
                if not self.lookahead_variable(var, mods, dif):
                    print("error")  # [str]
        return dif.index(max(dif))


    def lookahead_variable(self, var, mods, dif):
        score = []

        for choice in [var, -var]:
            prop_mods = []
            self.bincount = 0
            prop = self.propagate(choice, prop_mods)
            self.backtrack(prop_mods)
            if not prop:
                #            print 'failed literal', choice
                self.some_failure = 1
                if not self.propagate(-choice, mods, 1):
                    return 0
                break
            score.append(self.bincount)

        dif[var] = _reduce(lambda x, y: 1024 * x * y + x + y, score, 0)
        return 1


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
        return [var for var in range(1, self.nrofvars + 1) if self.fixedt[var] == -1]


    def unfixed_lits(self, clause):
        result = []
        for lit in clause:
            if self.fixedt[abs(lit)] == -1:
                result.append(lit)
        return result

    def run(self):
        if not self.solve_rec():
            print("unsatisfiable")
        print("nodes", nodecount, "propagations", propcount)
        return True

def test_satisfy():
    solver = Satisfier()
    assert solver.solve_rec()

def test_all():
    test_satisfy()
    

if __name__ == '__main__':
    test_all()    

