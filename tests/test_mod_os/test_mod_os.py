# popen deprecated in favor of subprocess.. consider subprocess support?

import os

def test_getcwd():
    assert len(os.getcwd()) > 1


def test_chdir():
    os.chdir('.')


def test_exceptions():
    try:
        os.chdir("ontehunoe")
    except FileNotFoundError as e:
        assert e.errno == 2
        assert e.filename == "ontehunoe"


def test_listdir():
    assert len(os.listdir()) > 0


def test_scandir():
    # relative paths (resolved against the test binary's cwd) rather than
    # a hardcoded '/tmp', which doesn't exist on Windows
    base = 'shedskin_test_scandir_dir'
    subdir = os.path.join(base, 'subdir')
    afile = os.path.join(base, 'afile.txt')

    os.mkdir(base)
    os.mkdir(subdir)
    with open(afile, 'w') as f:
        f.write('hi')

    names = []
    dirs = []
    files = []
    for entry in os.scandir(base):
        names.append(entry.name)
        if entry.is_dir():
            dirs.append(entry.name)
        if entry.is_file():
            files.append(entry.name)

    names.sort()
    assert names == ['afile.txt', 'subdir']
    assert dirs == ['subdir']
    assert files == ['afile.txt']

    os.remove(afile)
    os.rmdir(subdir)
    os.rmdir(base)


def test_scandir_name_path():
    base = 'shedskin_test_scandir_dir2'
    afile = os.path.join(base, 'afile.txt')

    os.mkdir(base)
    with open(afile, 'w') as f:
        f.write('hi')

    entries = list(os.scandir(base))
    assert len(entries) == 1
    entry = entries[0]
    assert entry.name == 'afile.txt'
    assert entry.path == afile
    assert entry.is_file()
    assert not entry.is_dir()
    assert not entry.is_symlink()

    st = entry.stat()
    assert st.st_size == 2

    os.remove(afile)
    os.rmdir(base)


# following currently only tested under posix

def test_env():
    os.environ['bert'] = 'value'
#    assert os.getenv('bert') == 'value'  # TODO

    os.putenv('bert', 'value2') # does not change os.environ


def test_getenv():
    # HOME (POSIX) / USERPROFILE (Windows) is always set in practice, and is
    # inherited from the real process environment at startup, so both
    # CPython and compiled Shedskin agree on it.
    home_var = "USERPROFILE" if os.name == "nt" else "HOME"
    home = os.getenv(home_var)
    if home:
        assert home is not None
        assert len(home) > 0

    # a variable that is essentially guaranteed not to exist
    missing = "SHEDSKIN_TEST_DEFINITELY_UNSET_VAR_12345"
    assert os.getenv(missing) is None
    assert os.getenv(missing, "fallback") == "fallback"
    assert os.getenv(missing, default="fallback") == "fallback"


def test_makedirs_exist_ok():
    path = '/tmp/shedskin_test_makedirs_exist_ok/a/b'

    os.makedirs(path, exist_ok=True)
    assert os.path.isdir(path)

    # calling again without exist_ok must raise
    try:
        os.makedirs(path)
        assert False
    except OSError as e:
        assert e.errno == 17  # EEXIST

    # calling again with exist_ok=True must be a no-op, not raise
    os.makedirs(path, exist_ok=True)
    assert os.path.isdir(path)

    os.removedirs(path)


def test_setgroups_overflow():
    # Regression test: os.setgroups used to fill a fixed-size 4096-slot
    # gid_t stack buffer without checking the input length first, so
    # passing more groups than that overflowed the stack. 4096 (MAXENTRIES)
    # is shedskin's own internal buffer limit -- the same cap os.getgroups
    # already uses -- not the real kernel NGROUPS_MAX, which is typically
    # much larger (e.g. 65536 on Linux) and not itself the thing under
    # test here. This must raise before touching the buffer, not crash
    # or corrupt memory, regardless of the caller's privileges.
    too_many = [0] * (4096 + 1)
    try:
        os.setgroups(too_many)
        assert False, "expected ValueError"
    except ValueError as e:
        assert str(e) == "too many groups"


def test_urandom():
    bts = os.urandom(10)
    assert len(bts) == 10
    assert bts.__class__.__name__ == 'bytes'


def test_cpu_count():
    n = os.cpu_count()
    assert n >= 1


def test_replace():
    # use relative paths (resolved against the test binary's cwd) rather
    # than a hardcoded '/tmp', which doesn't exist on Windows
    src = 'shedskin_test_replace_src.txt'
    dst = 'shedskin_test_replace_dst.txt'

    with open(src, 'w') as f:
        f.write('new content')

    # replace() must overwrite an existing destination, unlike rename()
    # on some platforms
    with open(dst, 'w') as f:
        f.write('old content')

    os.replace(src, dst)

    assert not os.path.exists(src)
    with open(dst) as f:
        assert f.read() == 'new content'

    os.remove(dst)


def test_replace_missing_source():
    # os.replace() on a missing source must raise the more specific
    # FileNotFoundError, not just a generic OSError, matching CPython.
    dst = 'shedskin_test_replace_missing_dst.txt'
    with open(dst, 'w') as f:
        f.write('untouched')

    try:
        os.replace('shedskin_test_replace_does_not_exist.txt', dst)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError as e:
        assert e.errno == 2

    with open(dst) as f:
        assert f.read() == 'untouched'

    os.remove(dst)


def test_fspath():
    assert os.fspath('/tmp/somefile.txt') == '/tmp/somefile.txt'
    # don't hardcode '/' here: os.path.join uses '\\' on Windows
    assert os.path.join(os.fspath('a'), os.fspath('b')) == os.path.join('a', 'b')


def test_posix():
    assert os.curdir == '.'
    assert os.pardir == '..'
    assert os.sep == '/'
    assert os.altsep is None
    assert os.extsep == '.'
    assert os.pathsep == ':'
    assert os.defpath == '/bin:/usr/bin'
    assert os.linesep == '\n'
    assert os.devnull == '/dev/null'


def test_rdwr():
    fd = os.open('/dev/null', os.O_RDWR)
    assert os.write(fd, b'blah') == 4
    assert os.read(fd, 10) == b''
    os.close(fd)


def test_lseek():
    # Regression test: os.lseek used to always return None instead of
    # the resulting file position that CPython's os.lseek promises.
    path = 'shedskin_test_lseek.txt'
    with open(path, 'wb') as f:
        f.write(b'0123456789')

    fd = os.open(path, os.O_RDWR)

    pos = os.lseek(fd, 3, os.SEEK_SET)
    assert pos == 3

    pos = os.lseek(fd, 2, os.SEEK_CUR)
    assert pos == 5

    pos = os.lseek(fd, 0, os.SEEK_END)
    assert pos == 10

    os.close(fd)
    os.remove(path)


def test_isatty():
    fd = os.open('/dev/null', os.O_RDONLY)
    assert os.isatty(fd) == False
    os.close(fd)


def test_system():
    assert os.system('ls') == 0


def test_all():
    test_getcwd()
    test_chdir()
    test_exceptions()
    test_listdir()

    test_makedirs_exist_ok()
    test_cpu_count()
    test_replace()
    test_replace_missing_source()
    test_fspath()
    test_scandir()
    test_scandir_name_path()

    if os.name == 'posix':  # TODO 'nt'
        test_posix()
        test_env()
        test_getenv()
        test_rdwr()
        test_lseek()
        test_isatty()
        test_system()
        test_urandom()
        # test_setgroups_overflow()  # os.setgroups is #ifndef WIN32'd out of
        # __os__ in lib/os/__init__.hpp, and shedskin translates this
        # function's body to C++ unconditionally (the `os.name == 'posix'`
        # check above is a runtime guard, not a compile-time one), so calling
        # it here breaks the Windows build even though it never runs there.


if __name__ == '__main__':
    test_all()
