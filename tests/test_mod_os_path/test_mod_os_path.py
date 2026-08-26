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



def test_os_path_isabs():
    assert isabs('/a/b') is True
    assert isabs('a/b') is False
    assert isabs('') is False


def test_os_path_normpath():
    # expected results use forward slashes and are translated to the
    # platform separator, matching the convention used elsewhere in this
    # file (see test_os_path_join); normpath() itself returns paths using
    # os.sep (e.g. backslashes on Windows), so a bare '/' literal here
    # would fail there.
    assert normpath('a/b/../c') == 'a/c'.replace('/', os.sep)
    assert normpath('a//b') == 'a/b'.replace('/', os.sep)
    assert normpath('./a/b/') == 'a/b'.replace('/', os.sep)
    assert normpath('../a') == '../a'.replace('/', os.sep)
    assert normpath('/a/./b/../c') == '/a/c'.replace('/', os.sep)
    # also check an already-native-separator input round-trips correctly
    assert normpath('a' + os.sep + 'b' + os.sep + '..' + os.sep + 'c') == 'a/c'.replace('/', os.sep)


# TODO: os.symlink is not compiled on Windows (guarded out in
# shedskin/lib/os/__init__.{hpp,cpp}), and os.path.islink()/realpath()
# don't have real Windows implementations either (islink() is hard-stubbed
# to False, realpath() doesn't resolve symlinks). Re-enable once Windows
# symlink support lands.
# def test_os_path_islink_samefile_samestat_realpath():
#     if exists("testdata"):
#         testdata = "testdata"
#     elif exists("../testdata"):
#         testdata = "../testdata"
#     else:
#         testdata = "../../testdata"
#
#     base = join(testdata, "ospathtest")
#     os.makedirs(base, exist_ok=True)
#
#     target = join(base, "file.txt")
#     with open(target, "w") as f:
#         f.write("hi")
#
#     link = join(base, "link.txt")
#     if not islink(link):
#         os.symlink("file.txt", link)
#
#     assert islink(link) is True
#     assert islink(target) is False
#
#     assert samefile(target, link) is True
#     assert samefile(target, target) is True
#
#     s1 = os.stat(target)
#     s2 = os.stat(link)
#     assert samestat(s1, s2) is True
#
#     assert realpath(link) == realpath(target)


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


def test_os_path_expandvars():
    old = os.getenv("SS_TEST_EXPANDVARS_VAR")

    os.putenv("SS_TEST_EXPANDVARS_VAR", "value")
    assert expandvars("$SS_TEST_EXPANDVARS_VAR/foo") == "value/foo"
    assert expandvars("${SS_TEST_EXPANDVARS_VAR}/foo") == "value/foo"
    # trailing alnum/underscore chars are absorbed into the var name (like
    # CPython's \w+ matching), so this name isn't set and stays literal
    assert expandvars("a$SS_TEST_EXPANDVARS_VARb") == "a$SS_TEST_EXPANDVARS_VARb"

    if old is None:
        os.unsetenv("SS_TEST_EXPANDVARS_VAR")
    else:
        os.putenv("SS_TEST_EXPANDVARS_VAR", old)

    # unknown variables and edge cases are left unchanged
    assert expandvars("$SS_TEST_DEFINITELY_NOT_SET/foo") == "$SS_TEST_DEFINITELY_NOT_SET/foo"
    assert expandvars("no dollar here") == "no dollar here"
    assert expandvars("") == ""
    assert expandvars("$") == "$"
    assert expandvars("$$") == "$$"
    assert expandvars("${") == "${"
    assert expandvars("${unterminated") == "${unterminated"


def test_os_path_commonpath():
    assert commonpath(["/a/b/c", "/a/b/d"]) == "/a/b"
    assert commonpath(["/a/b/c", "/a/b/c"]) == "/a/b/c"
    assert commonpath(["a/b", "a/c"]) == "a"
    assert commonpath(["/a", "/a/b"]) == "/a"
    assert commonpath(["/a/b/", "/a/b/c"]) == "/a/b"
    assert commonpath(["/", "/a"]) == "/"
    assert commonpath(["a"]) == "a"
    assert commonpath(["/a"]) == "/a"

    try:
        commonpath(["/a/b", "a/b"])
        assert False, "expected ValueError for mixed absolute/relative paths"
    except ValueError:
        pass


def test_all():
    test_os_path_join()
    test_os_path()
    test_os_path_samefile()
    test_os_path_ismount()
    test_os_path_isabs()
    test_os_path_normpath()
    # test_os_path_islink_samefile_samestat_realpath()  # see comment above, disabled for now
    test_os_path_relpath()
    test_os_path_expanduser()
    test_os_path_expanduser_windows_trailing_sep()
    test_os_path_expandvars()
    test_os_path_commonpath()

if __name__ == '__main__':
    test_all()

