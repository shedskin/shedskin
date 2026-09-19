import os.path
from os.path import *
import os
import sys

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


def test_os_path_splitroot():
    if os.name == "nt":
        assert splitroot("") == ("", "", "")
        assert splitroot("foo") == ("", "", "foo")
        assert splitroot("foo\\bar") == ("", "", "foo\\bar")
        assert splitroot("\\") == ("", "\\", "")
        assert splitroot("\\foo") == ("", "\\", "foo")
        assert splitroot("/foo") == ("", "/", "foo")
        assert splitroot("c:") == ("c:", "", "")
        assert splitroot("c:foo") == ("c:", "", "foo")
        assert splitroot("c:\\") == ("c:", "\\", "")
        assert splitroot("c:\\foo") == ("c:", "\\", "foo")
        assert splitroot("C:/foo") == ("C:", "/", "foo")
        # UNC and device paths
        assert splitroot("\\\\server\\share\\x") == ("\\\\server\\share", "\\", "x")
        assert splitroot("//server/share/x") == ("//server/share", "/", "x")
        assert splitroot("\\\\?\\UNC\\server\\share\\x") == ("\\\\?\\UNC\\server\\share", "\\", "x")
        assert splitroot("\\\\.\\dev") == ("\\\\.\\dev", "", "")
        assert splitroot("\\\\server") == ("\\\\server", "", "")
    else:
        assert splitroot("") == ("", "", "")
        assert splitroot("foo") == ("", "", "foo")
        assert splitroot("foo/bar") == ("", "", "foo/bar")
        assert splitroot("/") == ("", "/", "")
        assert splitroot("/foo") == ("", "/", "foo")
        assert splitroot("/foo/bar") == ("", "/", "foo/bar")
        # precisely two leading slashes are implementation-defined and
        # kept as the root; three or more are not
        assert splitroot("//") == ("", "//", "")
        assert splitroot("//foo") == ("", "//", "foo")
        assert splitroot("//foo/bar") == ("", "//", "foo/bar")
        assert splitroot("///") == ("", "/", "//")
        assert splitroot("///foo") == ("", "/", "//foo")
        assert splitroot("////foo") == ("", "/", "///foo")


def test_os_path_isjunction():
    # junctions are a Windows-only thing, and none of these are one, so
    # this is False everywhere
    assert not isjunction("")
    assert not isjunction(".")
    assert not isjunction("shedskin_no_such_path_here")

    if exists("testdata"):
        testdata = "testdata"
    elif exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"

    assert not isjunction(testdata)
    assert not isjunction(join(testdata, "abc.txt"))


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


def test_os_path_realpath_strict():
    if os.name == "nt":
        # "/tmp/..." isn't an absolute path on Windows (no drive letter),
        # and the os.system() "mkdir -p"/"rm -rf" calls below are POSIX
        # shell syntax that cmd.exe doesn't understand. The strict-mode
        # logic itself isn't platform-specific, so just skip here; it's
        # exercised by the POSIX run below.
        return

    # resolve the tmp root itself first: on macOS, /tmp is a symlink to
    # /private/tmp, so building test paths under the unresolved name
    # would make the equality checks below fail even when realpath() is
    # behaving correctly (it's supposed to follow that symlink).
    tmpdir = realpath("/tmp")

    missing = join(tmpdir, "shedskin_test_realpath_strict_missing", "foo")

    # non-strict (default): no error, just resolves as far as it can
    assert realpath(missing) == missing

    # strict=True: raise for a path that doesn't exist
    try:
        realpath(missing, strict=True)
        assert False, "expected FileNotFoundError for missing path"
    except FileNotFoundError:
        pass

    # strict=ALLOW_MISSING: missing components are explicitly tolerated
    assert realpath(missing, strict=os.path.ALLOW_MISSING) == missing

    # strict=True: no error for a path that does exist
    existing = join(tmpdir, "shedskin_test_realpath_strict_exists")
    os.system("mkdir -p " + existing)
    assert realpath(existing, strict=True) == existing
    assert realpath(existing, strict=os.path.ALLOW_MISSING) == existing
    os.system("rm -rf " + existing)


def test_os_path_realpath_all_but_last():
    # (os.path.ALL_BUT_LAST is new in CPython 3.15, so running this file
    # under an older CPython fails here)
    if os.name == "nt":
        return  # see test_os_path_realpath_strict

    tmpdir = realpath("/tmp")
    existing = join(tmpdir, "shedskin_test_realpath_all_but_last")
    os.system("mkdir -p " + existing)

    # existing path: fine
    assert realpath(existing, strict=os.path.ALL_BUT_LAST) == existing

    # existing parent, missing last component: fine with ALL_BUT_LAST,
    # an error with strict=True
    missing_last = join(existing, "nope")
    assert realpath(missing_last, strict=os.path.ALL_BUT_LAST) == missing_last
    try:
        realpath(missing_last, strict=True)
        assert False, "expected FileNotFoundError for missing last component"
    except FileNotFoundError:
        pass

    # missing parent directory: an error, unlike ALLOW_MISSING
    missing = join(existing, "nope", "foo")
    assert realpath(missing, strict=os.path.ALLOW_MISSING) == missing
    try:
        realpath(missing, strict=os.path.ALL_BUT_LAST)
        assert False, "expected FileNotFoundError for missing parent"
    except FileNotFoundError:
        pass

    os.system("rm -rf " + existing)

    # the special values are all true, but distinct from each other
    assert os.path.ALLOW_MISSING
    assert os.path.ALL_BUT_LAST
    assert os.path.ALLOW_MISSING != os.path.ALL_BUT_LAST


def test_os_path_realpath_symlink_loop():
    if os.name == "nt":
        return  # posix shell syntax below, and no ln(1) on cmd.exe

    base = join(realpath("/tmp"), "shedskin_test_realpath_loop")
    link = join(base, "loop")

    os.system("rm -rf " + base)
    os.system("mkdir -p " + base)
    os.system("ln -s " + link + " " + link)

    # non-strict: a symlink loop is not an error, the path is just left
    # as unresolved as it can be
    realpath(link)

    # both strict modes report the loop: ALLOW_MISSING only tolerates
    # *missing* components, not other errors
    try:
        realpath(link, strict=True)
        assert False, "expected OSError for symlink loop"
    except OSError:
        pass

    try:
        realpath(link, strict=os.path.ALLOW_MISSING)
        assert False, "expected OSError for symlink loop"
    except OSError:
        pass

    os.system("rm -rf " + base)


def test_os_path_realpath_through_symlink():
    if os.name == "nt":
        return  # os.symlink often needs elevated privileges on Windows

    base = "/tmp/shedskin_test_realpath_symlink_base"
    target = join(base, "target")
    link = join(base, "link")

    os.system("rm -rf " + base)
    os.system("mkdir -p " + target)
    os.symlink(target, link)

    # realpath() must follow the symlink component, not just report the
    # path as its own (unresolved) name.
    assert realpath(link) == realpath(target)
    assert realpath(link) != link

    os.system("rm -rf " + base)


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


def test_os_path_expanduser_environ():
    # expanduser() must see changes made through os.environ
    if os.name == "nt":
        return

    old_home = os.getenv("HOME")

    os.environ["HOME"] = "/hömé/shedskin/"
    assert expanduser("~") == "/hömé/shedskin"
    assert expanduser("~/foo") == "/hömé/shedskin/foo"

    os.environ["HOME"] = "/"
    assert expanduser("~") == "/"
    assert expanduser("~/foo") == "/foo"

    # without $HOME, CPython falls back to the password database
    del os.environ["HOME"]
    user = os.getenv("USER") or os.getenv("LOGNAME")
    if user and expanduser("~" + user) != "~" + user:
        assert expanduser("~/foo") == expanduser("~" + user + "/foo")

    if old_home is not None:
        os.environ["HOME"] = old_home


def test_os_path_expanduser_windows_trailing_sep():
    # Regression test: os.path.expanduser() on Windows must not strip a
    # trailing separator from USERPROFILE, matching ntpath.expanduser.
    # (A previous version accidentally reused the POSIX rstrip() call,
    # which turned e.g. a drive root "C:\\" into the different path "C:".)
    if os.name != "nt":
        return

    old_userprofile = os.getenv("USERPROFILE")

    # (os.path reads os.environ; os.putenv() does not update it)
    os.environ["USERPROFILE"] = "C:\\Users\\shedskin\\"
    assert expanduser("~") == "C:\\Users\\shedskin\\"
    assert expanduser("~/foo") == "C:\\Users\\shedskin\\/foo"

    os.environ["USERPROFILE"] = "C:\\"
    assert expanduser("~") == "C:\\"

    if old_userprofile is None:
        del os.environ["USERPROFILE"]
    else:
        os.environ["USERPROFILE"] = old_userprofile


def test_os_path_expandvars():
    old = os.getenv("SS_TEST_EXPANDVARS_VAR")

    # (os.path reads os.environ; os.putenv() does not update it)
    os.environ["SS_TEST_EXPANDVARS_VAR"] = "value"
    assert expandvars("$SS_TEST_EXPANDVARS_VAR/foo") == "value/foo"
    assert expandvars("${SS_TEST_EXPANDVARS_VAR}/foo") == "value/foo"
    # trailing alnum/underscore chars are absorbed into the var name (like
    # CPython's \w+ matching), so this name isn't set and stays literal
    assert expandvars("a$SS_TEST_EXPANDVARS_VARb") == "a$SS_TEST_EXPANDVARS_VARb"

    os.putenv("SS_TEST_EXPANDVARS_VAR", "other")
    assert expandvars("$SS_TEST_EXPANDVARS_VAR") == "value"

    os.environ["SS_TEST_EXPANDVARS_VAR"] = "välüe"
    assert expandvars("é${SS_TEST_EXPANDVARS_VAR}é") == "évälüeé"

    if old is None:
        del os.environ["SS_TEST_EXPANDVARS_VAR"]
        assert expandvars("$SS_TEST_EXPANDVARS_VAR") == "$SS_TEST_EXPANDVARS_VAR"
    else:
        os.environ["SS_TEST_EXPANDVARS_VAR"] = old

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



def test_os_path_constants():
    # os.path re-exports the separator constants of the os module
    assert os.path.sep == os.sep
    assert os.path.altsep == os.altsep
    assert os.path.curdir == os.curdir
    assert os.path.pardir == os.pardir
    assert os.path.extsep == os.extsep
    assert os.path.pathsep == os.pathsep
    assert os.path.defpath == os.defpath
    assert os.path.devnull == os.devnull

    if os.name == "nt":
        assert os.path.sep == "\\"
        assert os.path.altsep == "/"
        assert os.path.pathsep == ";"
    else:
        assert os.path.sep == "/"
        assert os.path.altsep is None
        assert os.path.pathsep == ":"
        assert os.path.devnull == "/dev/null"
    assert os.path.curdir == "."
    assert os.path.pardir == ".."
    assert os.path.extsep == "."
    assert len(os.path.defpath) > 0

    # ..and they are consistent with what the path functions do
    assert join("a", "b") == "a" + os.path.sep + "b"
    assert normpath(join("a", os.path.curdir, "b")) == "a" + os.path.sep + "b"
    assert normpath(join("a", os.path.pardir, "b")) == "b"
    assert exists(os.path.devnull)
    # ..exists as a device, not as a regular file or a directory
    assert not isfile(os.path.devnull)
    assert not isdir(os.path.devnull)
    assert os.path.pathsep in os.path.defpath


def test_os_path_split():
    assert split("a/b") == ("a", "b")
    assert split("a/b/") == ("a/b", "")
    assert split("a") == ("", "a")
    assert split("") == ("", "")
    assert split("/a") == ("/", "a")
    assert split("/") == ("/", "")
    assert split("//a") == ("//", "a")
    assert split("a/b/c.txt") == ("a/b", "c.txt")
    assert split("a//b") == ("a", "b")
    assert split("/a/b//") == ("/a/b", "")
    # head + sep + tail gives the path back, modulo duplicate separators
    # (join inserts os.sep, so on windows this is 'x/y\\z')
    head, tail = split("x/y/z")
    assert join(head, tail) == "x/y" + os.sep + "z"
    if os.name == "nt":
        assert split("c:\\a\\b") == ("c:\\a", "b")
        assert split("c:/a") == ("c:/", "a")


def test_os_path_islink_samestat():
    if os.name == "nt":
        return  # os.symlink needs elevated privileges on Windows

    base = "/tmp/shedskin_test_islink_samestat"
    os.system("rm -rf " + base)
    os.mkdir(base)
    target = join(base, "file.txt")
    link = join(base, "link.txt")
    with open(target, "w") as f:
        f.write("hi")
    os.symlink("file.txt", link)

    assert islink(link) is True
    assert islink(target) is False
    assert islink(base) is False
    assert islink(join(base, "missing")) is False

    s1 = os.stat(target)
    s2 = os.stat(link)  # follows the link
    s3 = os.lstat(link)  # does not
    s4 = os.stat(base)
    assert samestat(s1, s2) is True
    assert samestat(s1, s1) is True
    assert samestat(s1, s3) is False
    assert samestat(s1, s4) is False

    os.system("rm -rf " + base)

def test_os_path_sameopenfile():
    if exists("testdata"):
        testdata = "testdata"
    elif exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"

    abc = join(testdata, "abc.txt")
    fd1 = os.open(abc, os.O_RDONLY)
    fd2 = os.open(join(testdata, ".", "abc.txt"), os.O_RDONLY)
    fd3 = os.open(testdata, os.O_RDONLY)

    assert sameopenfile(fd1, fd1)
    assert sameopenfile(fd1, fd2)
    assert not sameopenfile(fd1, fd3)

    os.close(fd1)
    os.close(fd2)
    os.close(fd3)

    try:
        sameopenfile(fd1, fd2)
        assert False, "expected an error for a closed file descriptor"
    except OSError:
        pass


def test_os_path_isdevdrive():
    if os.name == "nt":
        # Dev Drives may or may not be in use, but it shouldn't raise
        assert isdevdrive(".") in (True, False)
        assert isdevdrive(os.getcwd()) in (True, False)
    else:
        assert isdevdrive(".") is False
        assert isdevdrive("/") is False
    # a non-existent path is never on a Dev Drive
    assert isdevdrive("shedskin_does_not_exist_isdevdrive") is False


def test_os_path_supports_unicode_filenames():
    assert os.path.supports_unicode_filenames in (True, False)
    if os.name == "nt" or sys.platform == "darwin":
        assert os.path.supports_unicode_filenames is True
    else:
        assert os.path.supports_unicode_filenames is False


def test_os_path_isdir_kwarg():
    # genericpath.isdir(s) in CPython: the parameter is called 's'
    assert isdir(s=".")
    assert not isdir(s="shedskin_does_not_exist_isdir")
    assert not exists(path="shedskin_does_not_exist_isdir")


def test_all():
    test_os_path_join()
    test_os_path()
    test_os_path_splitroot()
    test_os_path_isjunction()
    test_os_path_samefile()
    test_os_path_ismount()
    test_os_path_isabs()
    test_os_path_normpath()
    # test_os_path_islink_samefile_samestat_realpath()  # see comment above, disabled for now
    test_os_path_relpath()
    test_os_path_realpath_strict()
    test_os_path_realpath_all_but_last()
    test_os_path_realpath_symlink_loop()
    # test_os_path_realpath_through_symlink()  # os.symlink is #ifndef
    # WIN32'd out of __os__ in lib/os/__init__.hpp, and shedskin translates
    # this function's body to C++ unconditionally (the `os.name == "nt"`
    # check inside it is a runtime guard, not a compile-time one), so
    # calling it here breaks the Windows build even though it never runs
    # there. Same issue as test_setgroups_overflow() in test_mod_os.py.
    test_os_path_expanduser()
    test_os_path_expanduser_environ()
    test_os_path_expanduser_windows_trailing_sep()
    test_os_path_expandvars()
    test_os_path_commonpath()
    test_os_path_constants()
    test_os_path_split()
    test_os_path_islink_samestat()
    test_os_path_sameopenfile()
    test_os_path_isdevdrive()
    test_os_path_supports_unicode_filenames()
    test_os_path_isdir_kwarg()

if __name__ == '__main__':
    test_all()

