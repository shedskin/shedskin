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


def test_os_path_samefile():
    if exists("testdata"):
        testdata = "testdata"
    elif exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"

    abc = join(testdata, "abc.txt")

    assert samefile(abc, abc)
    assert samefile(abc, join(testdata, ".", "abc.txt"))
    assert not samefile(abc, testdata)

    try:
        samefile(join(testdata, "does_not_exist.txt"), abc)
        assert False, "expected an error for a missing file"
    except OSError:
        pass


def test_os_path_ismount():
    if exists("testdata"):
        testdata = "testdata"
    elif exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"

    if os.name == "nt":
        # the drive root is always a mount point on Windows
        drive = os.environ.get("SYSTEMDRIVE", "C:") + "\\"
        assert ismount(drive)
    else:
        # the filesystem root is always a mount point on POSIX
        assert ismount("/")

    assert not ismount(testdata)
    assert not ismount(join(testdata, "abc.txt"))



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


def test_os_path_realpath_strict():
    missing = "/tmp/shedskin_test_realpath_strict_missing/foo"

    # non-strict (default): no error, just resolves as far as it can
    assert realpath(missing) == missing

    # strict=True: raise for a path that doesn't exist
    try:
        realpath(missing, strict=True)
        assert False, "expected FileNotFoundError for missing path"
    except FileNotFoundError:
        pass

    # strict=True: no error for a path that does exist
    existing = "/tmp/shedskin_test_realpath_strict_exists"
    os.system("mkdir -p " + existing)
    assert realpath(existing, strict=True) == existing
    os.system("rm -rf " + existing)


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
        # posixpath now resolves ~user via a getpwnam()-based lookup
        user = os.getenv("USER", "") or os.getenv("LOGNAME", "")
        if user:
            assert expanduser("~" + user + "/bar") == home + "/bar"
        # on typical Linux systems, root's home is /root; guard this so the
        # test stays portable on POSIX variants where that isn't true (e.g. macOS)
        if os.path.isdir("/root"):
            assert expanduser("~root/bar") == "/root/bar"
        # unknown users are left alone
        assert expanduser("~definitelynotarealuser12345/bar") == "~definitelynotarealuser12345/bar"


def test_os_path_expanduser_windows_trailing_sep():
    # Regression test: os.path.expanduser() on Windows must not strip a
    # trailing separator from USERPROFILE, matching ntpath.expanduser.
    # (A previous version accidentally reused the POSIX rstrip() call,
    # which turned e.g. a drive root "C:\\" into the different path "C:".)
    if os.name != "nt":
        return

    old_userprofile = os.getenv("USERPROFILE")

    os.putenv("USERPROFILE", "C:\\Users\\shedskin\\")
    assert expanduser("~") == "C:\\Users\\shedskin\\"
    assert expanduser("~/foo") == "C:\\Users\\shedskin\\/foo"

    os.putenv("USERPROFILE", "C:\\")
    assert expanduser("~") == "C:\\"

    if old_userprofile is None:
        os.unsetenv("USERPROFILE")
    else:
        os.putenv("USERPROFILE", old_userprofile)


def test_all():
    test_os_path_join()
    test_os_path()
    test_os_path_samefile()
    test_os_path_ismount()
    test_os_path_relpath()
    test_os_path_realpath_strict()
    test_os_path_expanduser()
    test_os_path_expanduser_windows_trailing_sep()

if __name__ == '__main__':
    test_all()

