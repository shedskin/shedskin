import os.path
from os.path import *
import os

def test_os_path_join():
    assert os.path.join("heuk") == 'heuk'
    assert os.path.join("heuk", "emeuk") == 'heuk/emeuk'.replace('/', os.sep)
    assert os.path.join("heuk", "emeuk", "meuk") == 'heuk/emeuk/meuk'.replace('/', os.sep)
    assert os.path.join("a", "b", "c") == 'a/b/c'.replace('/', os.sep)

def test_os_path():
    assert commonprefix(["xxx", "xxxx"]) == 'xxx'
    assert normcase("hoei") == 'hoei'
    assert splitext("hoei/woei") == ('hoei/woei', '')
    assert splitext(".cshrc") == ('.cshrc', '')
    assert splitext(".gitignore") == ('.gitignore', '')
    assert splitext("..test") == ('..test', '')
    assert splitext(".a.b") == ('.a', '.b')
    assert splitext("/a/b/.hidden") == ('/a/b/.hidden', '')
    assert splitext("/a/b/.hidden.txt") == ('/a/b/.hidden', '.txt')
    assert splitext("foo.bar.baz") == ('foo.bar', '.baz')
    assert splitdrive("hoei/woei") == ('', 'hoei/woei')
    assert basename("hoei/woei") == 'woei'
    assert dirname("hoei/woei") == 'hoei'

    if exists("testdata"):
        testdata = "testdata"
    elif exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"

    assert exists(testdata)
    assert lexists(testdata)
    assert isdir(testdata)
    assert not isfile(testdata)

    abc = join(testdata, "abc.txt")

    assert getsize(abc) in (5, 7)

    assert getatime(abc) > 1 # dummy: cannot test for time
    assert getctime(abc) > 1 # dummy: cannot test for time
    assert getmtime(abc) > 1 # dummy: cannot test for time



def test_os_path_relpath():
    base = abspath(join("testdir_a", "b"))
    child = join(base, "c")

    assert relpath(child, base) == "c"
    assert relpath(base, child) == ".."
    assert relpath(base, base) == "."
    assert relpath("a/b/c", "a/b/c") == "."

    sibling = join(dirname(base), "d")
    assert relpath(child, sibling) == join("..", "b", "c")

    # relative to cwd by default
    assert relpath(join("x", "y")) == join("x", "y")

    try:
        relpath("")
        assert False, "expected ValueError for empty path"
    except ValueError:
        pass


def test_os_path_expanduser():
    assert expanduser("relative/path") == "relative/path"
    assert expanduser("") == ""

    if os.name == "nt":
        home_var, user_var = "USERPROFILE", "USERNAME"
    else:
        home_var, user_var = "HOME", None

    home = os.getenv(home_var)
    if not home:
        assert expanduser("~") == "~"
        return

    home = home.rstrip("/\\")
    assert expanduser("~") == home
    assert expanduser("~/foo") == home + "/foo"

    if user_var:
        # on Windows, ~<current user> resolves directly (no guessing needed)
        user = os.getenv(user_var)
        if user:
            assert expanduser("~" + user + "/bar") == home + "/bar"
    else:
        # posixpath has no pwd module here, so ~user forms are left alone
        assert expanduser("~otheruser/bar") == "~otheruser/bar"


def test_all():
    test_os_path_join()
    test_os_path()
    test_os_path_relpath()
    test_os_path_expanduser()

if __name__ == '__main__':
    test_all()

