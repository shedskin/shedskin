import os

def test_horn():
    if os.path.exists("testdata"):
        testdata = "testdata"
    elif os.path.exists("testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"
    datafile = os.path.join(testdata, 'uuf250-010.cnf')
    argv = ["", datafile]  # [list(str)]

    cnf = [l.strip().split() for l in open(argv[1]) if l[0] not in "c%0\n"]
    clauses = [[int(x) for x in m[:-1]] for m in cnf if m[0] != "p"]
    nrofvars = [int(n[2]) for n in cnf if n[0] == "p"][0]
    vars = range(nrofvars + 1)
    occurrence = [
        [[c for c in clauses if -v in c], [c for c in clauses if v in c]] for v in vars
    ]
    fixedt = [-1 for var in vars]
    assert len(occurrence) == 251


def test_all():
    test_horn()

if __name__ == '__main__':
    test_all() 


