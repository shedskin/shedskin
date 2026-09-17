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


def test_root_dir():
    base = '/tmp/shedskin_test_glob_root'
    files = ['a.txt', '.h.txt', 'sub/b.txt', 'sub/deep/c.txt']
    for f in files:
        os.makedirs(os.path.dirname(os.path.join(base, f)), exist_ok=True)
        open(os.path.join(base, f), 'w').close()

    # results are relative to root_dir, the current directory is not used
    assert sorted(glob.glob('*.txt', root_dir=base)) == ['a.txt']
    assert sorted(glob.glob('*.txt', root_dir=base, include_hidden=True)) == ['.h.txt', 'a.txt']
    assert names(glob.glob('*/*.txt', root_dir=base), '') == ['sub/b.txt']
    assert names(glob.glob('s*/', root_dir=base), '') == ['sub/']
    assert names(glob.glob('**/*.txt', root_dir=base, recursive=True), '') == \
        ['a.txt', 'sub/b.txt', 'sub/deep/c.txt']
    assert names(glob.glob('**', root_dir=base, recursive=True), '') == \
        ['a.txt', 'sub', 'sub/b.txt', 'sub/deep', 'sub/deep/c.txt']
    assert names(glob.glob('sub/**/', root_dir=base, recursive=True), '') == \
        ['sub/', 'sub/deep/']

    # non-magic patterns are checked against root_dir as well
    assert glob.glob('a.txt', root_dir=base) == ['a.txt']
    assert glob.glob('sub/', root_dir=base) == ['sub/']
    assert glob.glob('nope.txt', root_dir=base) == []
    assert glob.glob('sub/nope/', root_dir=base) == []

    # an absolute pattern ignores root_dir
    B = base + '/'
    assert names(glob.glob(B + '*.txt', root_dir='/nonexistent'), B) == ['a.txt']

    # iglob, and a root_dir that does not exist
    assert names(glob.iglob('*/*/*.txt', root_dir=base), '') == ['sub/deep/c.txt']
    assert glob.glob('*', root_dir='/nonexistent') == []

    for f in files:
        os.remove(os.path.join(base, f))
    os.removedirs(os.path.join(base, 'sub', 'deep'))


def test_include_hidden():
    base = '/tmp/shedskin_test_glob_hidden'
    files = ['a.txt', '.a.txt', '.hid.txt', 'sub/b.txt', 'sub/.hb.txt',
             '.hsub/f.txt', '.hsub/.g.txt', '.hsub/deep/h.txt']
    for f in files:
        os.makedirs(os.path.dirname(os.path.join(base, f)), exist_ok=True)
        open(os.path.join(base, f), 'w').close()
    B = base + '/'

    # '*' and '?' skip hidden names unless include_hidden=True
    assert names(glob.glob(B + '*.txt'), B) == ['a.txt']
    assert names(glob.glob(B + '*.txt', include_hidden=True), B) == \
        ['.a.txt', '.hid.txt', 'a.txt']
    assert names(glob.glob(B + '?a.txt'), B) == []
    assert names(glob.glob(B + '?a.txt', include_hidden=True), B) == ['.a.txt']
    assert names(glob.glob(B + 'sub/*'), B) == ['sub/b.txt']
    assert names(glob.glob(B + 'sub/*', include_hidden=True), B) == \
        ['sub/.hb.txt', 'sub/b.txt']

    # a pattern segment starting with '.' matches hidden names regardless
    assert names(glob.glob(B + '.*'), B) == ['.a.txt', '.hid.txt', '.hsub']
    assert names(glob.glob(B + '.*', include_hidden=True), B) == \
        ['.a.txt', '.hid.txt', '.hsub']
    assert names(glob.glob(B + 'sub/.*'), B) == ['sub/.hb.txt']
    assert names(glob.glob(B + '.h*.txt'), B) == ['.hid.txt']
    # ...but only a literal leading dot counts: a character class does not
    assert names(glob.glob(B + '[.]*'), B) == []
    assert names(glob.glob(B + '[.]*', include_hidden=True), B) == \
        ['.a.txt', '.hid.txt', '.hsub']
    # non-magic hidden paths are simply checked for existence
    assert names(glob.glob(B + '.hid.txt'), B) == ['.hid.txt']
    assert names(glob.glob(B + 'sub/.hb.txt'), B) == ['sub/.hb.txt']
    assert names(glob.glob(B + '.hsub/'), B) == ['.hsub/']
    # a literal hidden directory segment does not need include_hidden either
    assert names(glob.glob(B + '.hsub/*.txt'), B) == ['.hsub/f.txt']
    assert names(glob.glob(B + '.hsub/*.txt', include_hidden=True), B) == \
        ['.hsub/.g.txt', '.hsub/f.txt']

    # wildcard directory segments skip hidden directories
    assert names(glob.glob(B + '*/*.txt'), B) == ['sub/b.txt']
    assert names(glob.glob(B + '*/*.txt', include_hidden=True), B) == \
        ['.hsub/.g.txt', '.hsub/f.txt', 'sub/.hb.txt', 'sub/b.txt']
    assert names(glob.glob(B + '*/'), B) == ['sub/']
    assert names(glob.glob(B + '*/', include_hidden=True), B) == ['.hsub/', 'sub/']
    assert names(glob.glob(B + '*/f.txt'), B) == []
    assert names(glob.glob(B + '*/f.txt', include_hidden=True), B) == ['.hsub/f.txt']

    # recursive '**' neither reports nor descends into hidden directories
    assert names(glob.glob(B + '**/h.txt', recursive=True), B) == []
    assert names(glob.glob(B + '**/h.txt', recursive=True, include_hidden=True), B) == \
        ['.hsub/deep/h.txt']
    assert names(glob.glob(B + '**', recursive=True), B) == \
        ['', 'a.txt', 'sub', 'sub/b.txt']
    assert names(glob.glob(B + '**', recursive=True, include_hidden=True), B) == \
        ['', '.a.txt', '.hid.txt', '.hsub', '.hsub/.g.txt', '.hsub/deep',
         '.hsub/deep/h.txt', '.hsub/f.txt', 'a.txt', 'sub', 'sub/.hb.txt',
         'sub/b.txt']
    assert names(glob.glob(B + '**/', recursive=True), B) == ['', 'sub/']
    assert names(glob.glob(B + '**/', recursive=True, include_hidden=True), B) == \
        ['', '.hsub/', '.hsub/deep/', 'sub/']
    # (hidden *names* still match a '.*' segment; only the traversal skips them)
    assert names(glob.glob(B + '**/.*', recursive=True), B) == \
        ['.a.txt', '.hid.txt', '.hsub', 'sub/.hb.txt']
    assert names(glob.glob(B + '**/.*', recursive=True, include_hidden=True), B) == \
        ['.a.txt', '.hid.txt', '.hsub', '.hsub/.g.txt', 'sub/.hb.txt']

    # iglob honours it too
    assert names(glob.iglob(B + '*.txt', include_hidden=True), B) == \
        ['.a.txt', '.hid.txt', 'a.txt']
    assert names(glob.iglob(B + '**/*.txt', recursive=True, include_hidden=True), B) == \
        ['.a.txt', '.hid.txt', '.hsub/.g.txt', '.hsub/deep/h.txt', '.hsub/f.txt',
         'a.txt', 'sub/.hb.txt', 'sub/b.txt']

    # relative patterns
    cwd = os.getcwd()
    os.chdir(base)
    assert sorted(glob.glob('*.txt', include_hidden=True)) == ['.a.txt', '.hid.txt', 'a.txt']
    assert names(glob.glob('**/*.txt', recursive=True, include_hidden=True), '') == \
        ['.a.txt', '.hid.txt', '.hsub/.g.txt', '.hsub/deep/h.txt', '.hsub/f.txt',
         'a.txt', 'sub/.hb.txt', 'sub/b.txt']
    os.chdir(cwd)

    for f in files:
        os.remove(os.path.join(base, f))
    os.rmdir(os.path.join(base, 'sub'))
    os.removedirs(os.path.join(base, '.hsub', 'deep'))


def test_dir_fd():
    base = '/tmp/shedskin_test_glob_dirfd'
    files = ['a.txt', '.h.txt', 'sub/b.txt', 'sub/.hb.txt', 'sub/deep/c.txt',
             'other/d.txt']
    for f in files:
        os.makedirs(os.path.dirname(os.path.join(base, f)), exist_ok=True)
        open(os.path.join(base, f), 'w').close()
    os.makedirs(os.path.join(base, 'emptydir'), exist_ok=True)
    B = base + '/'

    fd = os.open(base, os.O_RDONLY)
    # run from an unrelated directory (containing a .txt of its own), so
    # that any use of the current directory would show up in the results
    cwd = os.getcwd()
    os.chdir(os.path.join(base, 'other'))

    # relative patterns are resolved against dir_fd, not the current directory
    assert sorted(glob.glob('*.txt', dir_fd=fd)) == ['a.txt']
    assert sorted(glob.glob('*.txt', dir_fd=fd, include_hidden=True)) == ['.h.txt', 'a.txt']
    assert glob.glob('.*', dir_fd=fd) == ['.h.txt']
    assert names(glob.glob('*/*.txt', dir_fd=fd), '') == ['other/d.txt', 'sub/b.txt']
    assert names(glob.glob('*/*.txt', dir_fd=fd, include_hidden=True), '') == \
        ['other/d.txt', 'sub/.hb.txt', 'sub/b.txt']
    assert names(glob.glob('s*/', dir_fd=fd), '') == ['sub/']
    assert names(glob.glob('*/', dir_fd=fd), '') == ['emptydir/', 'other/', 'sub/']
    assert names(glob.glob('*/*/', dir_fd=fd), '') == ['sub/deep/']
    assert names(glob.glob('**/*.txt', dir_fd=fd, recursive=True), '') == \
        ['a.txt', 'other/d.txt', 'sub/b.txt', 'sub/deep/c.txt']
    assert names(glob.glob('**/*.txt', dir_fd=fd, recursive=True, include_hidden=True), '') == \
        ['.h.txt', 'a.txt', 'other/d.txt', 'sub/.hb.txt', 'sub/b.txt', 'sub/deep/c.txt']
    assert names(glob.glob('**', dir_fd=fd, recursive=True), '') == \
        ['a.txt', 'emptydir', 'other', 'other/d.txt', 'sub', 'sub/b.txt',
         'sub/deep', 'sub/deep/c.txt']
    assert names(glob.glob('**/', dir_fd=fd, recursive=True), '') == \
        ['emptydir/', 'other/', 'sub/', 'sub/deep/']
    assert names(glob.glob('sub/**/', dir_fd=fd, recursive=True), '') == \
        ['sub/', 'sub/deep/']
    assert names(glob.glob('sub/**/*.txt', dir_fd=fd, recursive=True), '') == \
        ['sub/b.txt', 'sub/deep/c.txt']

    # non-magic patterns are checked relative to dir_fd as well
    assert glob.glob('a.txt', dir_fd=fd) == ['a.txt']
    assert glob.glob('sub', dir_fd=fd) == ['sub']
    assert glob.glob('sub/', dir_fd=fd) == ['sub/']
    assert glob.glob('sub/deep/c.txt', dir_fd=fd) == ['sub/deep/c.txt']
    assert glob.glob('a.txt/', dir_fd=fd) == []
    assert glob.glob('nope.txt', dir_fd=fd) == []
    assert glob.glob('sub/nope/', dir_fd=fd) == []
    assert glob.glob('d.txt', dir_fd=fd) == []  # exists in cwd, not under dir_fd

    # an absolute pattern ignores dir_fd
    assert names(glob.glob(B + 'other/*.txt', dir_fd=fd), B) == ['other/d.txt']
    assert names(glob.glob(B + 'sub/', dir_fd=fd), B) == ['sub/']

    # root_dir is itself relative to dir_fd
    assert glob.glob('*.txt', root_dir='sub', dir_fd=fd) == ['b.txt']
    assert sorted(glob.glob('*.txt', root_dir='sub', dir_fd=fd, include_hidden=True)) == \
        ['.hb.txt', 'b.txt']
    assert names(glob.glob('**/*.txt', root_dir='sub', dir_fd=fd, recursive=True), '') == \
        ['b.txt', 'deep/c.txt']
    assert names(glob.glob('*/', root_dir='sub', dir_fd=fd), '') == ['deep/']
    assert glob.glob('b.txt', root_dir='sub', dir_fd=fd) == ['b.txt']
    assert glob.glob('*', root_dir='nope', dir_fd=fd) == []
    assert glob.glob('*', root_dir='a.txt', dir_fd=fd) == []

    # iglob
    assert names(glob.iglob('*/*/*.txt', dir_fd=fd), '') == ['sub/deep/c.txt']
    assert names(glob.iglob('**/c.txt', dir_fd=fd, recursive=True), '') == ['sub/deep/c.txt']

    # dir_fd=None means the current directory, as when it is omitted
    assert glob.glob('*.txt', dir_fd=None) == ['d.txt']
    assert glob.glob('*.txt') == ['d.txt']

    # the descriptor stays usable across calls
    assert sorted(glob.glob('*.txt', dir_fd=fd)) == ['a.txt']
    assert sorted(glob.glob('*.txt', dir_fd=fd)) == ['a.txt']
    os.close(fd)
    os.chdir(cwd)

    for f in files:
        os.remove(os.path.join(base, f))
    os.rmdir(os.path.join(base, 'emptydir'))
    os.rmdir(os.path.join(base, 'other'))
    os.removedirs(os.path.join(base, 'sub', 'deep'))


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
    t = glob.translate('**/b', recursive=True)
    assert not matches(t, '.x/b')
    t = glob.translate('**/b', recursive=True, include_hidden=True)
    assert matches(t, '.x/b')
    assert matches(t, 'x/.y/b')

    # '?' and character classes vs hidden names
    t = glob.translate('?a')
    assert not matches(t, '.a')
    t = glob.translate('?a', include_hidden=True)
    assert matches(t, '.a')
    # (unlike glob(), translate() only guards patterns starting with '*' or
    # '?' -- a character class matching a leading dot is left alone)
    t = glob.translate('[.]a')
    assert matches(t, '.a')
    t = glob.translate('[.]a', include_hidden=True)
    assert matches(t, '.a')
    # a literal leading dot in the pattern always matches a hidden name
    t = glob.translate('.a*')
    assert matches(t, '.abc')
    t = glob.translate('.h/*')
    assert matches(t, '.h/x')
    assert not matches(t, '.h/.x')

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
    test_root_dir()
    test_include_hidden()
    test_translate()
    if os.name == 'posix':  # dir_fd is not supported on windows (as in cpython)
        test_dir_fd()


if __name__ == "__main__":
    test_all()
