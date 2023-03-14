import os
import os.path
import glob

if os.path.exists("testdata"):
    testdata = "testdata"
elif os.path.exists("testdata"):
    testdata = "../testdata"
else:
    testdata = "../../testdata"

def test_glob():
    txts = os.path.join(testdata, 'globdir', '*.txt')
    assert sorted([os.path.basename(f) for f in glob.glob(txts)]) == ['a.txt', 'b.txt', 'c.txt']
    mods = os.path.join(testdata, 'globdir', '*.mod')
    assert sorted([os.path.basename(f) for f in glob.glob(mods)]) == ['d.mod']

def test_all():
    test_glob()


if __name__ == "__main__":
    test_all()
