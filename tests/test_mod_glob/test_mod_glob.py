import os
import os.path
import glob

testdir = os.curdir
while not os.path.exists(os.path.join(testdir, "testdata")) and os.path.exists(os.pardir):
    testdir = os.path.join(testdir, os.pardir)
testdata = os.path.join(testdir, "testdata")
assert os.path.exists(testdata)

def test_glob():
    txts = os.path.join(testdata, 'globdir', '*.txt')
    assert sorted([os.path.basename(f) for f in glob.glob(txts)]) == ['a.txt', 'b.txt', 'c.txt']
    mods = os.path.join(testdata, 'globdir', '*.mod')
    assert sorted([os.path.basename(f) for f in glob.glob(mods)]) == ['d.mod']

def test_all():
    test_glob()


if __name__ == "__main__":
    test_all()
