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
    test_translate()


if __name__ == "__main__":
    test_all()
