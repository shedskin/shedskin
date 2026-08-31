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

def test_has_magic():
    assert glob.has_magic('*.txt') == True
    assert glob.has_magic('abc.txt') == False
    assert glob.has_magic('a[bc].txt') == True
    assert glob.has_magic('a?.txt') == True

def test_escape():
    assert glob.escape('a[bc]?*.txt') == 'a[[]bc][?][*].txt'
    assert glob.escape('plain.txt') == 'plain.txt'

def test_iglob():
    path = '/tmp/shedskin_test_iglob'
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path, 'x1.txt'), 'w').close()
    open(os.path.join(path, 'x2.txt'), 'w').close()

    res = sorted([os.path.basename(f) for f in glob.iglob(os.path.join(path, '*.txt'))])
    assert res == ['x1.txt', 'x2.txt']

    os.remove(os.path.join(path, 'x1.txt'))
    os.remove(os.path.join(path, 'x2.txt'))
    os.removedirs(path)

def test_all():
    test_glob()
    test_has_magic()
    test_escape()
    test_iglob()


if __name__ == "__main__":
    test_all()
