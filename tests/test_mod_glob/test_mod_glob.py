import os
import os.path
import glob
import re

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


def names(it, base):
    # strip the base directory and normalize separators, so results
    # are comparable regardless of where the tree was created.
    # normalization has to happen *before* the prefix is stripped: glob
    # assembles its results with os.path.join(), which inserts os.sep
    # ('\' on windows) even when the pattern itself used '/', so a
    # '/'-terminated base is not a literal prefix of the output there.
    base = base.replace(os.sep, '/')
    out = []
    for f in it:
        f = f.replace(os.sep, '/')
        assert f.startswith(base)
        out.append(f[len(base):])
    return sorted(out)


def test_recursive():
    base = '/tmp/shedskin_test_glob_rec'
    files = ['a.txt', 'b.py', '.hid.txt', 'sub/c.txt', 'sub/d.py',
             'sub/deep/e.txt', '.hsub/f.txt', 'sub2/g.txt']
    for f in files:
        d = os.path.dirname(os.path.join(base, f))
        os.makedirs(d, exist_ok=True)
        open(os.path.join(base, f), 'w').close()
    os.makedirs(os.path.join(base, 'emptydir'), exist_ok=True)
    B = base + '/'

    # without recursive=True, '**' behaves like '*'
    assert names(glob.glob(B + '**/*.txt'), B) == ['sub/c.txt', 'sub2/g.txt']
    assert names(glob.glob(B + '**'), B) == ['a.txt', 'b.py', 'emptydir', 'sub', 'sub2']

    # '**' matches zero or more directories
    assert names(glob.glob(B + '**/*.txt', recursive=True), B) == \
        ['a.txt', 'sub/c.txt', 'sub/deep/e.txt', 'sub2/g.txt']
    assert names(glob.glob(B + '**/*.py', recursive=True), B) == ['b.py', 'sub/d.py']
    assert names(glob.glob(B + '**/deep/*', recursive=True), B) == ['sub/deep/e.txt']

    # bare '**' includes the (trailing-slash) base directory itself
    assert names(glob.glob(B + '**', recursive=True), B) == \
        ['', 'a.txt', 'b.py', 'emptydir', 'sub', 'sub/c.txt', 'sub/d.py',
         'sub/deep', 'sub/deep/e.txt', 'sub2', 'sub2/g.txt']
    # whatever separator os.path.join() used, every result must be a
    # path that actually resolves
    for f in glob.glob(B + '**', recursive=True):
        assert os.path.exists(f)
    # trailing slash: directories only
    assert names(glob.glob(B + '**/', recursive=True), B) == \
        ['', 'emptydir/', 'sub/', 'sub/deep/', 'sub2/']
    # consecutive '**' segments do not collapse in glob() (unlike in
    # translate()): each '**' expands independently, so deeper matches
    # are reported multiple times -- this mirrors CPython exactly
    assert names(glob.glob(B + '**/**/*.txt', recursive=True), B) == \
        ['a.txt', 'sub/c.txt', 'sub/c.txt', 'sub/deep/e.txt', 'sub/deep/e.txt',
         'sub/deep/e.txt', 'sub2/g.txt', 'sub2/g.txt']
    # '**' in the middle, with a magic tail
    assert names(glob.glob(B + 'sub/**/*.txt', recursive=True), B) == \
        ['sub/c.txt', 'sub/deep/e.txt']
    # '**' with a non-magic tail
    assert names(glob.glob(B + '**/e.txt', recursive=True), B) == ['sub/deep/e.txt']
    # non-existent directory
    assert glob.glob(B + 'nope/**', recursive=True) == []

    # hidden files/dirs are skipped unless include_hidden=True
    assert names(glob.glob(B + '**/*.txt', recursive=True, include_hidden=True), B) == \
        ['.hid.txt', '.hsub/f.txt', 'a.txt', 'sub/c.txt', 'sub/deep/e.txt', 'sub2/g.txt']
    assert names(glob.glob(B + '**/.*', recursive=True), B) == ['.hid.txt', '.hsub']
    assert names(glob.glob(B + '.*', include_hidden=True), B) == ['.hid.txt', '.hsub']

    # iglob with recursive=True
    assert names(glob.iglob(B + '**/*.py', recursive=True), B) == ['b.py', 'sub/d.py']

    # relative patterns, evaluated from inside the tree
    cwd = os.getcwd()
    os.chdir(base)
    assert names(glob.glob('**/*.txt', recursive=True), '') == \
        ['a.txt', 'sub/c.txt', 'sub/deep/e.txt', 'sub2/g.txt']
    assert names(glob.glob('**', recursive=True), '') == \
        ['a.txt', 'b.py', 'emptydir', 'sub', 'sub/c.txt', 'sub/d.py',
         'sub/deep', 'sub/deep/e.txt', 'sub2', 'sub2/g.txt']
    assert names(glob.glob('sub/**', recursive=True), '') == \
        ['sub/', 'sub/c.txt', 'sub/d.py', 'sub/deep', 'sub/deep/e.txt']
    os.chdir(cwd)

    for f in files:
        os.remove(os.path.join(base, f))
    os.rmdir(os.path.join(base, 'emptydir'))
    os.removedirs(os.path.join(base, 'sub', 'deep'))
    os.removedirs(os.path.join(base, 'sub2'))
    os.removedirs(os.path.join(base, '.hsub'))


def matches(regex, s):
    # the exact regex text differs slightly between implementations
    # (escaping conventions, \Z vs \z anchor), so tests are behavioral:
    # compile the result and check what it matches
    return re.match(regex, s) != None


def test_translate():
    # literal pattern: matches exactly, anchored at both ends
    t = glob.translate('foo.txt')
    assert matches(t, 'foo.txt')
    assert not matches(t, 'foo_txt')       # '.' must be literal
    assert not matches(t, 'foo.txt.bak')   # anchored at end
    assert not matches(t, 'foo.txt\n')     # strict end-of-string anchor

    # empty pattern matches only the empty string
    t = glob.translate('')
    assert matches(t, '')
    assert not matches(t, 'a')

    # '*' within a segment: any run of non-separator chars, but not hidden
    t = glob.translate('*.txt')
    assert matches(t, 'a.txt')
    assert matches(t, 'a.b.txt')
    assert not matches(t, 'dir/a.txt')     # must not cross '/'
    assert not matches(t, '.hidden.txt')   # leading-dot names excluded

    # ...unless include_hidden is set
    t = glob.translate('*.txt', include_hidden=True)
    assert matches(t, '.hidden.txt')
    assert not matches(t, 'dir/a.txt')     # still segment-local

    # '?' is exactly one non-separator character
    t = glob.translate('a?c')
    assert matches(t, 'abc')
    assert not matches(t, 'ac')
    assert not matches(t, 'a/c')

    # bare '*' segments
    t = glob.translate('a/*')
    assert matches(t, 'a/b')
    assert not matches(t, 'a/.b')
    assert not matches(t, 'a/b/c')

    # character classes still work per segment
    t = glob.translate('a[bc]d')
    assert matches(t, 'abd')
    assert matches(t, 'acd')
    assert not matches(t, 'aed')

    # trailing separator is significant
    t = glob.translate('a/')
    assert matches(t, 'a/')
    assert not matches(t, 'a')

    # non-recursive '**' behaves like '*' (collapsed, segment-local)
    t = glob.translate('**')
    assert matches(t, 'ab')
    assert not matches(t, 'a/b')

    # recursive '**' spans any number of segments
    t = glob.translate('a/**', recursive=True)
    assert matches(t, 'a/')
    assert matches(t, 'a/b')
    assert matches(t, 'a/b/c')
    assert not matches(t, 'a/.b')          # hidden still excluded by default

    t = glob.translate('**/b', recursive=True)
    assert matches(t, 'b')
    assert matches(t, 'x/b')
    assert matches(t, 'x/y/b')
    assert not matches(t, 'x/y/c')

    # consecutive '**' segments collapse
    t = glob.translate('a/**/**/b', recursive=True)
    assert matches(t, 'a/b')
    assert matches(t, 'a/x/b')
    assert matches(t, 'a/x/y/b')

    # recursive + include_hidden
    t = glob.translate('a/**', recursive=True, include_hidden=True)
    assert matches(t, 'a/.b/c')

    # custom separator: ';' splits segments, '/' becomes an ordinary char
    t = glob.translate('*;x', seps=';')
    assert matches(t, 'foo;x')
    assert matches(t, 'a/b;x')
    assert not matches(t, 'a;b;x')

    # multiple separator characters
    t = glob.translate('*', seps='/;')
    assert matches(t, 'ab')
    assert not matches(t, 'a/b')
    assert not matches(t, 'a;b')


def test_all():
    test_glob()
    test_has_magic()
    test_escape()
    test_iglob()
    test_recursive()
    test_translate()


if __name__ == "__main__":
    test_all()
