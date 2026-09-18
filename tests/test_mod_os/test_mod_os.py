# popen deprecated in favor of subprocess.. consider subprocess support?

import os
import stat

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
# (see test_mod_os_posix for functionality that is #ifndef WIN32 in lib/os:
# shedskin translates every called function unconditionally, so a runtime
# os.name check does not keep those calls out of the windows build)

def test_walk():
    base = 'shedskin_test_walk_dir'
    a = os.path.join(base, 'a')
    ab = os.path.join(a, 'b')
    c = os.path.join(base, 'c')
    paths = [os.path.join(base, 'f1'), os.path.join(a, 'f2'),
             os.path.join(ab, 'f3'), os.path.join(c, 'f4')]

    for d in (base, a, ab, c):
        os.mkdir(d)
    for p in paths:
        with open(p, 'w') as f:
            f.write('hi')

    # top-down: parent before children, dirnames/filenames per directory
    seen = []
    for root, dirs, files in os.walk(base):
        dirs.sort()
        seen.append((root, dirs[:], sorted(files)))
    assert seen == [
        (base, ['a', 'c'], ['f1']),
        (a, ['b'], ['f2']),
        (ab, [], ['f3']),
        (c, [], ['f4']),
    ]

    # pruning dirnames in place skips those subtrees
    roots = []
    for root, dirs, files in os.walk(base):
        dirs.sort()
        if 'a' in dirs:
            dirs.remove('a')
        roots.append(root)
    assert roots == [base, c]

    # bottom-up: children before parent
    roots2 = []
    for root, dirs, files in os.walk(base, topdown=False):
        roots2.append(root)
    assert roots2[-1] == base
    assert roots2.index(ab) < roots2.index(a)
    assert sorted(roots2) == sorted([base, a, ab, c])

    # unreadable/missing top yields nothing
    assert list(os.walk('shedskin_test_walk_nonexistent')) == []

    # count files via unpacking in a genexpr
    assert sum(len(files) for root, dirs, files in os.walk(base)) == 4

    for p in paths:
        os.remove(p)
    for d in (ab, a, c, base):
        os.rmdir(d)


def test_env():
    os.environ['bert'] = 'value'
    assert os.getenv('bert') == 'value'

    os.putenv('bert', 'value2') # does not change os.environ
    assert os.getenv('bert') == 'value'

    del os.environ['bert']
    assert os.getenv('bert') is None
    assert os.getenv('bert', 'dflt') == 'dflt'


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


def test_get_exec_path():
    # default: derived from os.environ['PATH']
    path = os.get_exec_path()
    assert path == os.environ['PATH'].split(os.pathsep)
    assert os.get_exec_path(None) == path

    # explicit env dict
    custom = {'PATH': os.pathsep.join(['/a', '/b/c', ''])}
    assert os.get_exec_path(custom) == ['/a', '/b/c', '']
    assert os.get_exec_path(env=custom) == ['/a', '/b/c', '']

    # no PATH in env: fall back to os.defpath
    assert os.get_exec_path({'HOME': '/x'}) == os.defpath.split(os.pathsep)


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


def test_makedirs_parent_mode():
    base = '/tmp/shedskin_test_makedirs_parent_mode'
    leaf = base + '/a/b/c'

    os.system('rm -rf ' + base)
    os.makedirs(leaf, mode=0o700, exist_ok=True, parent_mode=0o750)

    leaf_mode = stat.S_IMODE(os.stat(leaf).st_mode)
    parent_mode = stat.S_IMODE(os.stat(base + '/a').st_mode)
    assert leaf_mode == 0o700
    assert parent_mode == 0o750

    os.system('rm -rf ' + base)


def test_makedirs_default_parent_mode():
    # without parent_mode, intermediate directories should get the
    # default (umask-restricted) mode, not the leaf `mode` argument
    # (matching CPython's default behavior since 3.7, bpo-42367).
    base = '/tmp/shedskin_test_makedirs_default_parent_mode'
    leaf = base + '/a/b/c'

    os.system('rm -rf ' + base)
    old_umask = os.umask(0o022)
    os.makedirs(leaf, mode=0o700, exist_ok=True)
    os.umask(old_umask)

    parent_mode = stat.S_IMODE(os.stat(base + '/a').st_mode)
    assert parent_mode == 0o755  # 0o777 & ~0o022

    os.system('rm -rf ' + base)


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


def test_getrandom():
    bts = os.getrandom(10)
    assert len(bts) == 10
    assert bts.__class__.__name__ == 'bytes'

    bts = os.getrandom(10, 0)
    assert len(bts) == 10


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



def test_access():
    assert os.F_OK == 0
    assert os.X_OK == 1
    assert os.W_OK == 2
    assert os.R_OK == 4

    path = 'shedskin_test_access.txt'
    with open(path, 'w') as f:
        f.write('x')
    assert os.access(path, os.F_OK)
    assert os.access(path, os.R_OK)
    assert os.access(path, os.W_OK)
    assert os.access(path, os.R_OK | os.W_OK)
    assert not os.access('shedskin_does_not_exist.txt', os.F_OK)
    assert not os.access('shedskin_does_not_exist.txt', os.R_OK)
    os.remove(path)


def test_open_flags():
    path = 'shedskin_test_open_flags.txt'
    if os.path.exists(path):
        os.remove(path)

    # O_CREAT|O_EXCL creates, and refuses to create twice
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    assert os.write(fd, b'abc') == 3
    os.close(fd)
    try:
        os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        assert False
    except OSError as e:  # FileExistsError
        assert e.errno == 17  # EEXIST

    # O_APPEND writes go to the end
    fd = os.open(path, os.O_WRONLY | os.O_APPEND)
    os.write(fd, b'def')
    os.close(fd)
    with open(path, 'rb') as f:
        assert f.read() == b'abcdef'

    # O_TRUNC empties the file first
    fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
    os.write(fd, b'z')
    os.close(fd)
    with open(path, 'rb') as f:
        assert f.read() == b'z'

    # O_WRONLY really is write-only
    fd = os.open(path, os.O_WRONLY)
    try:
        os.read(fd, 1)
        assert False
    except OSError:
        pass
    os.close(fd)

    os.remove(path)


def test_fd_ops():
    path = 'shedskin_test_fd_ops.txt'
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, 0o644)
    os.write(fd, b'0123456789')
    os.fsync(fd)
    assert os.fstat(fd).st_size == 10

    # dup: a second descriptor sharing the same open file (and offset)
    fd2 = os.dup(fd)
    assert fd2 != fd
    assert os.fstat(fd2).st_size == 10
    os.lseek(fd, 2, os.SEEK_SET)
    assert os.read(fd2, 3) == b'234'
    os.close(fd2)

    # dup2: reuse an explicit target descriptor number
    fd3 = os.open(os.devnull, os.O_RDONLY)
    assert os.dup2(fd, fd3) == fd3
    os.lseek(fd3, 0, os.SEEK_SET)
    assert os.read(fd3, 2) == b'01'
    os.close(fd3)

    # ftruncate shrinks and grows
    os.ftruncate(fd, 4)
    assert os.fstat(fd).st_size == 4
    os.ftruncate(fd, 6)
    assert os.fstat(fd).st_size == 6
    os.lseek(fd, 0, os.SEEK_SET)
    assert os.read(fd, 10) == b'0123\0\0'
    os.close(fd)

    assert os.stat(path).st_size == 6
    os.remove(path)


def test_pipe_fdopen():
    r, w = os.pipe()
    assert r != w
    assert os.write(w, b'through the pipe') == 16
    os.close(w)
    assert os.read(r, 100) == b'through the pipe'
    assert os.read(r, 100) == b''  # writer closed: EOF
    os.close(r)

    # fdopen wraps a descriptor in a file object
    path = 'shedskin_test_fdopen.txt'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    f = os.fdopen(fd, 'w')
    f.write('hello fdopen\n')
    f.close()
    fd = os.open(path, os.O_RDONLY)
    f = os.fdopen(fd, 'r')
    assert f.read() == 'hello fdopen\n'
    f.close()
    os.remove(path)


def test_pids():
    pid = os.getpid()
    ppid = os.getppid()
    assert pid > 0
    assert ppid > 0
    assert pid != ppid


def test_rename_renames():
    src = 'shedskin_test_rename_src.txt'
    dst = 'shedskin_test_rename_dst.txt'
    with open(src, 'w') as f:
        f.write('moved')
    os.rename(src, dst)
    assert not os.path.exists(src)
    with open(dst) as f:
        assert f.read() == 'moved'

    # renames creates missing intermediate directories..
    deep = os.path.join('shedskin_test_renames_dir', 'a', 'b', 'file.txt')
    os.renames(dst, deep)
    assert not os.path.exists(dst)
    assert os.path.isfile(deep)
    # ..and prunes directories left empty by the move
    os.renames(deep, dst)
    assert not os.path.exists('shedskin_test_renames_dir')
    assert os.path.isfile(dst)
    os.remove(dst)

    try:
        os.rename('shedskin_does_not_exist.txt', dst)
        assert False
    except FileNotFoundError:
        pass


def test_utime():
    path = 'shedskin_test_utime.txt'
    with open(path, 'w') as f:
        f.write('x')

    os.utime(path, (1000000000, 1234567890))
    st = os.stat(path)
    assert int(st.st_atime) == 1000000000
    assert int(st.st_mtime) == 1234567890
    os.utime(path, (1000000000.5, 1234567890.25))
    assert int(os.stat(path).st_mtime) == 1234567890

    os.remove(path)


def test_strerror_error():
    assert len(os.strerror(2)) > 0
    assert os.strerror(2) != os.strerror(13)
    # matches what OSError carries for the same errno
    try:
        os.stat('shedskin_does_not_exist.txt')
        assert False
    except FileNotFoundError as e:
        assert os.strerror(e.errno) == e.strerror

    # os.error is OSError
    caught = False
    try:
        os.stat('shedskin_does_not_exist.txt')
    except os.error:
        caught = True
    assert caught


def test_times():
    t = os.times()
    assert len(t) == 5
    for x in t:
        assert x >= 0.0
    # burn a little cpu, so user time can only have gone up
    total = 0
    for i in range(200000):
        total += i * i
    assert total > 0
    t2 = os.times()
    assert t2[0] >= t[0]
    assert t2[4] >= t[4]


def test_misc_constants():
    assert os.TMP_MAX > 0


def test_unsetenv():
    os.putenv('SHEDSKIN_UNSETENV_TEST', 'set')
    os.unsetenv('SHEDSKIN_UNSETENV_TEST')
    # the process environment no longer has it, so a child does not see it
    if os.name != 'nt':
        p = os.popen('echo "[$SHEDSKIN_UNSETENV_TEST]"')
        assert p.read() == '[]\n'
        p.close()
    else:
        # cmd.exe echoes unset %VAR% literally, so just check popen works
        p = os.popen('echo hi')
        assert p.read().strip() == 'hi'
        p.close()
    # os.environ is a separate mapping in shedskin, so keep it in step by hand
    os.environ['SHEDSKIN_UNSETENV_TEST'] = 'set'
    del os.environ['SHEDSKIN_UNSETENV_TEST']
    assert os.getenv('SHEDSKIN_UNSETENV_TEST') is None

def test_all():
    test_getcwd()
    test_chdir()
    test_exceptions()
    test_listdir()
    test_access()
    test_open_flags()
    test_fd_ops()
    test_pipe_fdopen()
    test_pids()
    test_rename_renames()
    test_utime()
    test_strerror_error()
    test_times()
    test_misc_constants()
    test_unsetenv()

    test_makedirs_exist_ok()
    test_cpu_count()
    test_replace()
    test_replace_missing_source()
    test_fspath()
    test_scandir()
    test_scandir_name_path()
    test_walk()

    if os.name == 'posix':  # TODO 'nt'
        test_posix()
        test_env()
        test_getenv()
        test_get_exec_path()
        test_rdwr()
        test_lseek()
        test_isatty()
        test_system()
        test_urandom()
        test_getrandom()
        test_makedirs_parent_mode()
        test_makedirs_default_parent_mode()
        # test_setgroups_overflow()  # os.setgroups is #ifndef WIN32'd out of
        # __os__ in lib/os/__init__.hpp, and shedskin translates this
        # function's body to C++ unconditionally (the `os.name == 'posix'`
        # check above is a runtime guard, not a compile-time one), so calling
        # it here breaks the Windows build even though it never runs there.


if __name__ == '__main__':
    test_all()
