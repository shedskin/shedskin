import os
import os.path
import fnmatch


def test_fnmatch():
    if os.path.exists("testdata"):
        testdata = "testdata"
    elif os.path.exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"
    fs = os.listdir(os.path.join(testdata, 'globdir'))

    assert fnmatch.fnmatch("run.py", "run.[py]y")
    assert sorted([f for f in fs if fnmatch.fnmatch(f, '*.txt')]) == ['a.txt', 'b.txt', 'c.txt']
    assert sorted([f for f in fs if fnmatch.fnmatch(f, '*.mod')]) == ['d.mod']

def test_all():
    test_fnmatch()


if __name__ == "__main__":
    test_all()



