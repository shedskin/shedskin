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


def test_stat_times():
    path = 'shedskin_test_stat_times.txt'
    with open(path, 'w') as f:
        f.write('x')

    os.utime(path, (1000000000.5, 1234567890.25))
    for st in [os.stat(path), os.lstat(path)]:
        # float seconds, as in CPython (st_mtime used to be an int)
        assert st.st_atime == 1000000000.5
        assert st.st_mtime == 1234567890.25
        assert str(st.st_mtime) == '1234567890.25'
        assert st.st_atime_ns == 1000000000500000000
        assert st.st_mtime_ns == 1234567890250000000
        assert abs(st.st_ctime - st.st_ctime_ns / 1e9) < 1e-3
        # tuple items 7-9 are still integer seconds
        assert st[7] == 1000000000
        assert st[8] == 1234567890
        assert st[9] == st.st_ctime_ns // 1000000000
    assert os.path.getmtime(path) == 1234567890.25
    assert os.path.getatime(path) == 1000000000.5

    fd = os.open(path, os.O_RDONLY)
    st = os.fstat(fd)
    os.close(fd)
    assert st.st_mtime == 1234567890.25
    assert st.st_mtime_ns == 1234567890250000000
    assert st.st_ino == os.stat(path).st_ino
    assert st.st_dev == os.stat(path).st_dev

    os.remove(path)


def test_direntry_inode_junction():
    base = 'shedskin_test_direntry_inode'
    afile = os.path.join(base, 'afile.txt')
    subdir = os.path.join(base, 'subdir')

    os.mkdir(base)
    os.mkdir(subdir)
    with open(afile, 'w') as f:
        f.write('hi')

    inodes = []
    for entry in os.scandir(base):
        assert entry.inode() == os.lstat(entry.path).st_ino
        assert entry.inode() == entry.stat(follow_symlinks=False).st_ino
        assert not entry.is_junction()
        inodes.append(entry.inode())
    assert len(inodes) == 2
    assert inodes[0] != inodes[1]

    os.remove(afile)
    os.rmdir(subdir)
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


def test_nt():
    assert os.linesep == '\r\n'
    assert os.sep == '\\'


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
    except FileExistsError as e:
        assert e.errno == 17  # EEXIST
        assert e.filename == path

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

    # times_result: named fields, unpacking, slicing, tuple methods
    assert t2.user == t2[0]
    assert t2.system == t2[1]
    assert t2.children_user == t2[2]
    assert t2.children_system == t2[3]
    assert t2.elapsed == t2[4] == t2[-1]
    user, system, cuser, csystem, elapsed = t2
    assert user == t2.user and elapsed == t2.elapsed
    assert len(t2[:2]) == 2
    assert t2[1:3] == (t2.system, t2.children_user)
    assert t2.elapsed in t2

    tr = os.times_result((1.5, 2.0, 0.0, 0.0, 10.25))
    assert tr.user == 1.5
    assert tr.elapsed == 10.25
    assert tr[::2] == (1.5, 0.0, 10.25)
    assert tr.count(0.0) == 2
    assert tr.index(0.0) == 2
    assert tr.index(0.0, 3) == 3
    assert tr.index(0.0, 0, 3) == 2
    assert list(tr) == [1.5, 2.0, 0.0, 0.0, 10.25]
    assert repr(tr) == os.name + '.times_result(user=1.5, system=2.0, children_user=0.0, children_system=0.0, elapsed=10.25)'
    tr = os.times_result((1, 2, 3, 4, 5))
    assert tr.children_system == 4.0
    ok = False
    try:
        tr[5]
    except IndexError:
        ok = True
    assert ok
    ok = False
    try:
        tr.index(7.0)
    except ValueError:
        ok = True
    assert ok


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

def test_oserror_subclasses():
    # failed calls raise the OSError subclass matching errno, like CPython
    ok = False
    try:
        os.mkdir('.')
    except FileExistsError:
        ok = True
    assert ok

    ok = False
    try:
        os.rmdir('shedskin_no_such_dir')
    except FileNotFoundError as e:
        ok = e.filename == 'shedskin_no_such_dir'
    assert ok

    ok = False
    try:
        os.listdir('shedskin_no_such_dir')
    except FileNotFoundError as e:
        ok = e.errno == 2 and e.filename == 'shedskin_no_such_dir'
    assert ok

    ok = False
    try:
        os.scandir('shedskin_no_such_dir')
    except FileNotFoundError:
        ok = True
    assert ok

    ok = False
    try:
        os.chdir('shedskin_no_such_dir')
    except FileNotFoundError:
        ok = True
    assert ok

    ok = False
    try:
        os.open('shedskin_no_such_dir/x', os.O_RDONLY)
    except FileNotFoundError as e:
        ok = e.filename == 'shedskin_no_such_dir/x'
    assert ok


def test_kwarg_names():
    # keyword argument names should match CPython
    base = 'shedskin_test_kwarg_names'
    os.mkdir(path=base, mode=0o755)
    cwd = os.getcwd()
    os.chdir(path=base)
    os.chdir(cwd)
    fd = os.open(path=base + '/f', flags=os.O_CREAT | os.O_WRONLY, mode=0o644)
    assert os.fstat(fd=fd).st_size == 0
    os.close(fd)
    os.chmod(path=base + '/f', mode=0o600)
    error = False
    try:
        os.chmod(base + '/no_such_file', 0o600)
    except OSError:
        error = True
    assert error
    os.rename(src=base + '/f', dst=base + '/g')
    os.replace(src=base + '/g', dst=base + '/h')
    assert os.listdir(base) == ['h']
    os.remove(base + '/h')
    os.rmdir(path=base)
    assert not os.path.exists(base)


def test_kwarg_names_posix():
    assert os.getenv(key='SHEDSKIN_NO_SUCH_VAR', default='dflt') == 'dflt'
    assert os.system(command='true') == 0
    p = os.popen(cmd='echo hi', mode='r', buffering=-1)
    assert p.read() == 'hi\n'
    p.close()


def test_getcwdb():
    b = os.getcwdb()
    assert b.__class__.__name__ == 'bytes'
    assert b == os.fsencode(os.getcwd())
    assert os.fsdecode(b) == os.getcwd()


def test_fsencode_fsdecode():
    assert os.fsencode('abc') == b'abc'
    assert os.fsencode(b'abc') == b'abc'
    assert os.fsdecode(b'abc') == 'abc'
    assert os.fsdecode('abc') == 'abc'
    assert os.fsencode('caf\u00e9') == b'caf\xc3\xa9'
    assert os.fsdecode(b'caf\xc3\xa9') == 'caf\u00e9'
    # surrogateescape: undecodable bytes survive a round trip
    s = os.fsdecode(b'a\xffb')
    assert s == 'a\udcffb'
    assert os.fsencode(s) == b'a\xffb'


def test_process_cpu_count():
    n = os.process_cpu_count()
    assert 1 <= n <= os.cpu_count()


def test_truncate():
    path = 'shedskin_test_truncate.txt'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.write(fd, b'0123456789')
    os.close(fd)
    os.truncate(path, 4)
    assert os.stat(path).st_size == 4
    os.truncate(path, 7)
    assert os.stat(path).st_size == 7
    fd = os.open(path, os.O_RDONLY)
    assert os.read(fd, 10) == b'0123\0\0\0'
    os.close(fd)
    os.remove(path)

    ok = False
    try:
        os.truncate('shedskin_no_such_file.txt', 0)
    except FileNotFoundError as e:
        ok = e.filename == 'shedskin_no_such_file.txt'
    assert ok


def test_closerange():
    # place descriptors at known numbers, so no unrelated ones get closed
    fd = os.open(os.devnull, os.O_RDONLY)
    fds = [200, 201, 202]
    for n in fds:
        os.dup2(fd, n)
    os.close(fd)
    os.closerange(200, 202)
    for n in fds[:2]:
        ok = False
        try:
            os.fstat(n)
        except OSError:
            ok = True
        assert ok
    os.fstat(202)  # fd_high is exclusive
    os.close(202)
    os.closerange(300, 310)  # errors are ignored


def test_bad_fd():
    # an unused descriptor must give OSError(EBADF), not crash (msvc crt)
    fd = os.open(os.devnull, os.O_RDONLY)
    os.close(fd)
    count = 0
    try:
        os.fstat(fd)
    except OSError as e:
        count += (e.errno == 9)
    try:
        os.close(fd)
    except OSError as e:
        count += (e.errno == 9)
    try:
        os.dup(fd)
    except OSError as e:
        count += (e.errno == 9)
    try:
        os.dup2(fd, 250)
    except OSError as e:
        count += (e.errno == 9)
    try:
        os.read(fd, 1)
    except OSError as e:
        count += (e.errno == 9)
    try:
        os.write(fd, b'x')
    except OSError as e:
        count += (e.errno == 9)
    try:
        os.lseek(fd, 0, os.SEEK_SET)
    except OSError as e:
        count += (e.errno == 9)
    try:
        os.fsync(fd)
    except OSError as e:
        count += (e.errno == 9)
    assert count == 8
    assert not os.isatty(fd)


def test_waitstatus_to_exitcode():
    assert os.waitstatus_to_exitcode(0) == 0
    assert os.waitstatus_to_exitcode(3 << 8) == 3
    assert os.waitstatus_to_exitcode(255 << 8) == 255


def test_inheritable():
    path = 'shedskin_test_inheritable.txt'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.set_inheritable(fd, True)
    assert os.get_inheritable(fd) == True
    os.set_inheritable(fd, False)
    assert os.get_inheritable(fd) == False
    os.set_inheritable(fd, True)
    assert os.get_inheritable(fd) == True
    os.close(fd)
    os.remove(path)

    ok = False
    try:
        os.get_inheritable(fd)
    except OSError as e:
        ok = e.errno == 9  # EBADF
    assert ok


def test_fchmod():
    # portable: only the write bit (read-only attribute on windows)
    path = 'shedskin_test_fchmod.txt'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.fchmod(fd, stat.S_IREAD)
    assert not (os.stat(path).st_mode & stat.S_IWRITE)
    os.fchmod(fd, stat.S_IREAD | stat.S_IWRITE)
    assert os.stat(path).st_mode & stat.S_IWRITE
    os.close(fd)
    os.remove(path)

    ok = False
    try:
        os.fchmod(fd, 0o644)
    except OSError as e:
        ok = e.errno == 9  # EBADF
    assert ok


def test_device_encoding():
    fd = os.open(os.devnull, os.O_RDONLY)
    assert os.device_encoding(fd) is None
    os.close(fd)


def test_terminal_size():
    ts = os.terminal_size((80, 24))
    assert ts.columns == 80
    assert ts.lines == 24
    assert len(ts) == 2
    assert ts[0] == 80
    assert ts[1] == 24
    assert ts[-1] == 24
    assert ts[:] == (80, 24)
    assert repr(ts) == 'os.terminal_size(columns=80, lines=24)'
    ok = False
    try:
        ts[2]
    except IndexError:
        ok = True
    assert ok

    # stdout may or may not be a terminal while testing
    try:
        ts = os.get_terminal_size()
        assert ts.columns >= 0 and ts.lines >= 0
    except OSError:
        pass
    try:
        ts = os.get_terminal_size(1)
    except OSError:
        pass


walk_errors = []
walk_errnos = []

def walk_onerror(e):
    walk_errors.append(e.filename)

def walk_reraise(e):
    raise e

def test_walk_onerror():
    # onerror is called with the OSError for a directory that cannot be
    # scanned (here: a missing top, or a top that is a file)
    base = 'shedskin_test_walk_onerror'
    afile = os.path.join(base, 'afile.txt')
    os.mkdir(base)
    with open(afile, 'w') as f:
        f.write('hi')

    assert list(os.walk('shedskin_walk_missing', onerror=walk_onerror)) == []
    assert walk_errors == ['shedskin_walk_missing']
    assert list(os.walk(afile, onerror=walk_onerror)) == []
    assert walk_errors == ['shedskin_walk_missing', afile]

    # lazy: nothing happens before the first next()
    w = os.walk('shedskin_walk_missing2', onerror=walk_onerror)
    assert len(walk_errors) == 2
    assert list(w) == []
    assert len(walk_errors) == 3
    assert list(os.walk('shedskin_walk_missing3', topdown=False, onerror=walk_onerror)) == []
    assert walk_errors[3] == 'shedskin_walk_missing3'

    # readable directories do not trigger it
    assert len(list(os.walk(base, onerror=walk_onerror))) == 1
    assert len(walk_errors) == 4

    # explicit None, lambda, and a callback that re-raises
    assert list(os.walk('shedskin_walk_missing', onerror=None)) == []
    list(os.walk('shedskin_walk_missing', onerror=lambda err: walk_errnos.append(err.errno)))
    assert walk_errnos == [2]  # ENOENT
    ok = False
    try:
        list(os.walk('shedskin_walk_missing', False, walk_reraise))
    except OSError as e:  # TODO FileNotFoundError: 'raise e' loses the subclass
        ok = True
        assert e.errno == 2
        assert e.filename == 'shedskin_walk_missing'
    assert ok

    os.remove(afile)
    os.rmdir(base)



def test_utime_extended():
    path = 'shedskin_test_utime2.txt'
    with open(path, 'w') as f:
        f.write('x')

    # nanosecond precision (multiples of 100ns, the windows resolution)
    os.utime(path, ns=(1000000000123456700, 1234567890987654300))
    st = os.stat(path)
    assert st.st_atime_ns == 1000000000123456700
    assert st.st_mtime_ns == 1234567890987654300
    os.utime(path, None, ns=(2000000000000000000, 2000000000500000000))
    assert os.stat(path).st_mtime_ns == 2000000000500000000

    # no times: set both to the current time
    os.utime(path, (1000000000, 1000000000))
    os.utime(path)
    assert os.stat(path).st_mtime > 1600000000
    os.utime(path, (1000000000, 1000000000))
    os.utime(path, None)
    assert os.stat(path).st_mtime > 1600000000

    try:
        os.utime(path, (1, 2), ns=(1, 2))
        assert False
    except ValueError as e:
        assert str(e) == "utime: you may specify either 'times' or 'ns' but not both"
    try:
        os.utime(path, (1.0, 2.0, 3.0))
        assert False
    except TypeError:
        pass
    try:
        os.utime(path, ns=(1, 2, 3))
        assert False
    except TypeError:
        pass
    try:
        os.utime('shedskin_no_such_file_utime', None)
        assert False
    except FileNotFoundError:
        pass

    os.remove(path)


def test_stat_follow_symlinks():
    path = 'shedskin_test_stat_follow.txt'
    with open(path, 'w') as f:
        f.write('abc')
    st = os.stat(path, follow_symlinks=False)
    assert st.st_size == 3
    assert st.st_ino == os.lstat(path).st_ino
    assert os.stat(path, follow_symlinks=True).st_size == 3

    # stat_result attributes
    st = os.stat(path)
    assert st.st_nlink >= 1
    assert st.st_uid >= 0
    assert st.st_gid >= 0
    os.remove(path)


def test_links():
    base = 'shedskin_test_links'
    os.mkdir(base)
    target = os.path.join(base, 'target.txt')
    hard = os.path.join(base, 'hard.txt')
    with open(target, 'w') as f:
        f.write('data')

    os.link(target, hard)
    if os.name != 'nt':  # (st_nlink is always 1 on windows yet)
        assert os.stat(target).st_nlink == 2
    with open(hard) as f:
        assert f.read() == 'data'
    try:
        os.link(target, hard)
        assert False
    except FileExistsError:
        pass

    # symlinks may need extra privileges on windows
    soft = os.path.join(base, 'soft.txt')
    softdir = os.path.join(base, 'softdir')
    made = False
    try:
        os.symlink('target.txt', soft)
        made = True
    except OSError:
        pass
    if made:
        assert os.readlink(soft) == 'target.txt'
        if os.name != 'nt':  # (no st_ino/lstat distinction on windows yet)
            assert os.stat(soft, follow_symlinks=False).st_ino != os.stat(soft).st_ino
        os.symlink('.', softdir, target_is_directory=True)
        assert os.path.isdir(softdir)
        assert os.readlink(softdir) == '.'
        os.unlink(soft)
        if os.name == 'nt':
            os.rmdir(softdir)
        else:
            os.unlink(softdir)
    try:
        os.readlink(target)
        assert False
    except OSError:
        pass

    os.unlink(hard)
    assert os.stat(target).st_nlink == 1
    os.unlink(target)
    os.rmdir(base)


def test_dup2_inheritable():
    path = 'shedskin_test_dup2_inh.txt'
    fd = os.open(path, os.O_CREAT | os.O_WRONLY, 0o644)
    fd2 = os.dup(fd)
    assert os.dup2(fd, fd2) == fd2
    assert os.get_inheritable(fd2)
    assert os.dup2(fd, fd2, False) == fd2
    assert not os.get_inheritable(fd2)
    assert os.dup2(fd, fd2, inheritable=True) == fd2
    assert os.get_inheritable(fd2)
    os.close(fd2)
    os.close(fd)
    os.remove(path)


def test_readinto():
    path = 'shedskin_test_readinto.txt'
    with open(path, 'wb') as f:
        f.write(b'abcdefg')
    fd = os.open(path, os.O_RDONLY)
    buf = bytearray(4)
    assert os.readinto(fd, buf) == 4
    assert buf == bytearray(b'abcd')
    assert os.readinto(fd, buf) == 3
    assert buf == bytearray(b'efgd')
    assert os.readinto(fd, buf) == 0
    assert os.readinto(fd, bytearray()) == 0
    try:
        os.readinto(fd, b'xyz')
        assert False
    except TypeError:
        pass
    os.close(fd)
    try:
        os.readinto(fd, buf)
        assert False
    except OSError:
        pass
    os.remove(path)


def test_reload_environ():
    name = 'SHEDSKIN_RELOAD_ENVIRON_TEST'
    env = os.environ
    os.putenv(name, 'first')
    assert name not in os.environ
    os.reload_environ()
    assert env[name] == 'first'  # updated in place
    assert os.getenv(name) == 'first'
    os.putenv(name, 'second')
    os.reload_environ()
    assert os.environ[name] == 'second'
    os.unsetenv(name)
    os.reload_environ()
    assert name not in env
    try:
        os.putenv('A=B', 'x')
        assert False
    except ValueError:
        pass


def test_getlogin():
    # fails without a controlling terminal on posix (as in cpython)
    try:
        name = os.getlogin()
        assert len(name) > 0
    except OSError:
        pass


def test_fdopen_buffering():
    path = 'shedskin_test_fdopen_buf.txt'
    fd = os.open(path, os.O_CREAT | os.O_WRONLY, 0o644)
    f = os.fdopen(fd, 'w', 1)
    f.write('line\n')
    f.close()
    fd = os.open(path, os.O_RDONLY)
    f = os.fdopen(fd, 'r', buffering=-1)
    assert f.read() == 'line\n'
    f.close()
    os.remove(path)


def test_process_constants():
    assert os.P_WAIT == 0
    assert os.P_NOWAIT == 1
    if os.name == 'nt':
        assert os.P_NOWAITO == 3
        assert os.P_DETACH == 4


def test_process_compile_only():
    # process creation/termination: compiled on all platforms, but not run
    # (see test_mod_os_posix for runtime tests)
    if os.getenv('SHEDSKIN_TEST_NEVER_SET_ABC') is None:
        return
    env = {'A': 'B'}
    prog = 'shedskin_no_such_program'
    pid = os.spawnv(os.P_NOWAIT, prog, [prog, 'x'])
    pid = os.spawnve(os.P_NOWAIT, prog, [prog, 'x'], env)
    pid = os.spawnvp(os.P_NOWAIT, prog, [prog, 'x'])
    pid = os.spawnvpe(os.P_NOWAIT, prog, [prog, 'x'], env)
    pid = os.spawnl(os.P_WAIT, prog, prog, 'x')
    pid, status = os.waitpid(pid, 0)
    os.kill(pid, 0)
    os.execv(prog, [prog, 'x'])
    os.execve(prog, [prog, 'x'], env)
    os.execvp(prog, [prog, 'x'])
    os.execvpe(prog, [prog, 'x'], env)
    os.execl(prog, prog, 'x')
    os.execlp(prog, prog, 'x')
    os.abort()
    os._exit(1)


def test_unicode_names():
    d = 'tmp_\xfcn\xef'
    fn = os.path.join(d, 'caf\xe9_\u20ac_\U0001f600.txt')
    os.mkdir(d)
    with open(fn, 'w') as f:
        f.write('h\xe9llo')
    os.mkdir(os.path.join(d, 'sub_\xdf'))
    assert sorted(os.listdir(d)) == ['caf\xe9_\u20ac_\U0001f600.txt', 'sub_\xdf']
    assert sorted([e.name for e in os.scandir(d)]) == sorted(os.listdir(d))
    assert sorted([e.path for e in os.scandir(d)]) == sorted([os.path.join(d, n) for n in os.listdir(d)])
    walked = [(r, sorted(ds), sorted(fs)) for r, ds, fs in os.walk(d)]
    assert walked == [(d, ['sub_\xdf'], ['caf\xe9_\u20ac_\U0001f600.txt']), (os.path.join(d, 'sub_\xdf'), [], [])]
    assert os.path.isfile(fn) and os.stat(fn).st_size == 6
    fn2 = os.path.join(d, 'na\xefve.txt')
    os.rename(fn, fn2)
    with open(fn2) as f:  # (closed: Windows cannot remove an open file)
        assert f.read() == 'h\xe9llo'
    os.chdir(d)
    assert os.path.basename(os.getcwd()) == d
    os.chdir('..')
    os.remove(fn2)
    os.rmdir(os.path.join(d, 'sub_\xdf'))
    os.rmdir(d)
    assert not os.path.exists(d)


def test_undecodable_names():
    # names that are not valid utf-8 come back with surrogateescape (PEP 383)
    # and must work again as paths. (skipped where the file system refuses
    # such names, e.g. APFS)
    d = 'tmp_bad'
    os.mkdir(d)
    sub = os.path.join(d, 'd\udcfe')
    try:
        os.mkdir(sub)
    except OSError:
        os.rmdir(d)
        return
    with open(os.path.join(sub, 'f\udcff'), 'w') as f:
        f.write('abc')
    assert os.listdir(d) == ['d\udcfe']
    assert os.fsencode(os.listdir(d)[0]) == b'd\xfe'
    assert [e.name for e in os.scandir(sub)] == ['f\udcff']
    walked = [(r, fs) for r, ds, fs in os.walk(d)]
    assert walked == [(d, []), (sub, ['f\udcff'])]
    for e in os.scandir(sub):
        assert e.is_file() and e.stat().st_size == 3
    os.remove(os.path.join(sub, 'f\udcff'))
    os.rmdir(sub)
    os.rmdir(d)


def test_all():
    test_unicode_names()
    test_undecodable_names()
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
    test_stat_times()
    test_direntry_inode_junction()
    test_walk()
    test_walk_onerror()
    test_oserror_subclasses()
    test_kwarg_names()
    test_getcwdb()
    test_fsencode_fsdecode()
    test_process_cpu_count()
    test_truncate()
    test_closerange()
    test_bad_fd()
    test_waitstatus_to_exitcode()
    test_inheritable()
    test_fchmod()
    test_device_encoding()
    test_terminal_size()

    test_utime_extended()
    test_stat_follow_symlinks()
    test_links()
    test_dup2_inheritable()
    test_readinto()
    test_reload_environ()
    test_getlogin()
    test_fdopen_buffering()
    test_process_constants()
    test_process_compile_only()
    test_urandom()
    test_getrandom()

    if os.name == 'nt':
        test_nt()

    if os.name == 'posix':  # TODO 'nt'
        test_posix()
        test_env()
        test_getenv()
        test_get_exec_path()
        test_rdwr()
        test_lseek()
        test_isatty()
        test_system()
        test_makedirs_parent_mode()
        test_makedirs_default_parent_mode()
        test_kwarg_names_posix()
        # test_setgroups_overflow()  # os.setgroups is #ifndef WIN32'd out of
        # __os__ in lib/os/__init__.hpp, and shedskin translates this
        # function's body to C++ unconditionally (the `os.name == 'posix'`
        # check above is a runtime guard, not a compile-time one), so calling
        # it here breaks the Windows build even though it never runs there.


if __name__ == '__main__':
    test_all()
