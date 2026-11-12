# os functionality that is #ifndef WIN32 in lib/os (see CMakeLists.txt);
# portable os tests live in test_mod_os

import copy
import os
import stat
import sys


def test_kill():
    pid = os.getpid()
    # signal 0 only checks that the process exists
    os.kill(pid, 0)
    try:
        os.kill(2 ** 22 + 12345, 0)
        assert False, 'expected an error for a non-existent pid'
    except ProcessLookupError as e:
        assert e.errno == 3  # ESRCH
        assert e.filename is None
        assert str(e) == '[Errno 3] No such process'
    os.killpg(os.getpgrp(), 0)


def test_link_unlink_lstat_readlink():
    base = 'shedskin_test_link_dir'
    os.system('rm -rf ' + base)
    os.mkdir(base)
    target = os.path.join(base, 'target.txt')
    hard = os.path.join(base, 'hard.txt')
    soft = os.path.join(base, 'soft.txt')
    with open(target, 'w') as f:
        f.write('data')

    os.link(target, hard)
    assert os.stat(hard).st_ino == os.stat(target).st_ino
    assert os.stat(target).st_nlink == 2
    with open(hard) as f:
        assert f.read() == 'data'

    os.symlink('target.txt', soft)
    assert os.readlink(soft) == 'target.txt'
    # lstat looks at the link itself, stat follows it
    assert os.lstat(soft).st_ino != os.stat(soft).st_ino
    assert os.stat(soft).st_ino == os.stat(target).st_ino
    assert os.lstat(target).st_ino == os.stat(target).st_ino

    os.unlink(soft)
    assert not os.path.lexists(soft)
    os.unlink(hard)
    assert os.stat(target).st_nlink == 1
    try:
        os.unlink(hard)
        assert False
    except FileNotFoundError:
        pass

    os.unlink(target)
    os.rmdir(base)


def test_chmod():
    path = 'shedskin_test_chmod.txt'
    with open(path, 'w') as f:
        f.write('x')

    os.chmod(path, 0o600)
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    os.chmod(path, 0o644)
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o644
    assert os.chmod(path, 0o644) is None

    os.remove(path)


def test_fchmod():
    path = 'shedskin_test_fchmod.txt'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.fchmod(fd, 0o600)
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    os.fchmod(fd, mode=0o640)
    assert stat.S_IMODE(os.fstat(fd).st_mode) == 0o640
    os.close(fd)
    os.remove(path)


def test_blocking():
    r, w = os.pipe()
    assert os.get_blocking(r)
    os.set_blocking(r, False)
    assert not os.get_blocking(r)
    assert os.get_blocking(w)  # per-descriptor
    ok = False
    try:
        os.read(r, 1)  # nothing written yet
    except BlockingIOError:
        ok = True
    assert ok
    os.set_blocking(r, True)
    assert os.get_blocking(r)
    os.write(w, b'x')
    assert os.read(r, 1) == b'x'
    os.close(r)
    os.close(w)

    ok = False
    try:
        os.get_blocking(r)
    except OSError as e:
        ok = e.errno == 9  # EBADF
    assert ok
    ok = False
    try:
        os.set_blocking(r, True)
    except OSError as e:
        ok = e.errno == 9
    assert ok


def test_uname():
    u = os.uname()
    assert len(u) == 5
    assert u.sysname == u[0]
    assert u.nodename == u[1]
    assert u.release == u[2]
    assert u.version == u[3]
    assert u.machine == u[4] == u[-1]
    sysname, nodename, release, version, machine = u
    assert sysname == u.sysname and machine == u.machine
    assert [x for x in u] == [u.sysname, u.nodename, u.release, u.version, u.machine]
    assert u[:2] == (u.sysname, u.nodename)
    assert u.sysname in u

    # copies keep the attributes (1106-A5)
    for uc in (copy.copy(u), copy.deepcopy(u)):
        assert uc is not u and uc == u
        assert uc.sysname == u.sysname and uc.machine == u.machine
        assert repr(uc) == repr(u)

    if sys.platform.startswith('linux'):
        assert u.sysname == 'Linux'

    ur = os.uname_result(('A', 'b', 'c', 'b', 'e'))
    assert ur.version == 'b'
    assert ur.count('b') == 2
    assert ur.index('b') == 1
    assert ur.index('b', 2) == 3
    assert ur.index('b', -3, 5) == 3
    ok = False
    try:
        ur.index('b', 2, 3)
    except ValueError:
        ok = True
    assert ok
    assert ur[::-2] == ('e', 'c', 'A')
    assert repr(ur) == "posix.uname_result(sysname='A', nodename='b', release='c', version='b', machine='e')"
    ok = False
    try:
        ur[5]
    except IndexError:
        ok = True
    assert ok
    # a tuple, with the items also as attributes
    assert ur == ('A', 'b', 'c', 'b', 'e')
    assert hash(ur) == hash(('A', 'b', 'c', 'b', 'e'))
    assert '-'.join(ur) == 'A-b-c-b-e'
    assert ur + ('f',) == ('A', 'b', 'c', 'b', 'e', 'f')
    assert sorted(ur) == ['A', 'b', 'b', 'c', 'e']
    assert '%s/%s' % ur[:2] == 'A/b'


def test_statvfs():
    # a tuple, with the items also as attributes
    vf = os.statvfs('.')
    assert len(vf) == 10
    assert vf[0] == vf.f_bsize and vf[1] == vf.f_frsize and vf[-1] == vf.f_namemax
    bsize, frsize, blocks, bfree, bavail, files, ffree, favail, flag, namemax = vf
    assert (blocks, bfree, bavail) == (vf.f_blocks, vf.f_bfree, vf.f_bavail)
    assert (files, ffree, favail, flag) == (vf.f_files, vf.f_ffree, vf.f_favail, vf.f_flag)
    assert vf[2:4] == (vf.f_blocks, vf.f_bfree)
    assert vf.f_namemax > 0
    assert vf.f_fsid == os.statvfs('.').f_fsid
    assert repr(vf) == ('os.statvfs_result(f_bsize=%d, f_frsize=%d, f_blocks=%d, f_bfree=%d, f_bavail=%d, '
                        'f_files=%d, f_ffree=%d, f_favail=%d, f_flag=%d, f_namemax=%d)' % vf)
    fd = os.open('.', os.O_RDONLY)
    vf2 = os.fstatvfs(fd)
    os.close(fd)
    assert vf2.f_bsize == vf.f_bsize and len(vf2) == 10

    # copies keep the attributes (1106-A5)
    for vc in (copy.copy(vf), copy.deepcopy(vf)):
        assert vc is not vf and vc == vf
        assert vc.f_bsize == vf.f_bsize and vc.f_namemax == vf.f_namemax
        assert repr(vc) == repr(vf)


def test_popen_spawn():
    p = os.popen('echo hello popen')
    assert p.read() == 'hello popen\n'
    p.close()

    p = os.popen('printf "a\\nb\\n"', 'r')
    assert p.readlines() == ['a\n', 'b\n']
    p.close()

    assert os.P_WAIT == 0
    assert os.P_NOWAIT == 1
    assert os.P_NOWAITO == os.P_NOWAIT  # same thing on posix

    # P_WAIT: the return value is the exit status
    assert os.spawnv(os.P_WAIT, '/bin/sh', ['sh', '-c', 'exit 0']) == 0
    assert os.spawnv(os.P_WAIT, '/bin/sh', ['sh', '-c', 'exit 3']) == 3

    # argv may also be a tuple
    assert os.spawnv(os.P_WAIT, '/bin/sh', ('sh', '-c', 'exit 4')) == 4
    assert os.spawnvp(os.P_WAIT, 'sh', ('sh', '-c', 'exit 5')) == 5
    assert os.spawnve(os.P_WAIT, '/bin/sh', ('sh', '-c', 'exit $X'), {'X': '6'}) == 6
    assert os.spawnvpe(os.P_WAIT, 'sh', ('sh', '-c', 'exit $X'), {'X': '2', 'PATH': os.environ['PATH']}) == 2
    if os.environ.get('SHEDSKIN_NEVER_SET') == 'yes':  # compile-only
        os.execv('/bin/true', ('true',))
        os.execvp('true', ('true',))
        os.execve('/bin/true', ('true',), {'X': '1'})
        os.execvpe('true', ('true',), {'X': '1'})

    # P_NOWAIT: the return value is a pid, to be collected with waitpid
    pid = os.spawnv(os.P_NOWAIT, '/bin/sh', ['sh', '-c', 'exit 7'])
    assert pid > 0
    wpid, status = os.waitpid(pid, 0)
    assert wpid == pid
    assert os.WIFEXITED(status) is True
    assert os.WIFSIGNALED(status) is False
    assert os.WEXITSTATUS(status) == 7


def test_times_children():
    # user/system time of waited-for children is accounted in slots 2 and 3
    t = os.times()
    assert t[2] >= 0.0
    assert t[3] >= 0.0


def test_misc_constants():
    assert os.EX_OK == 0


def test_oserror_subclasses():
    ok = False
    try:
        os.waitpid(-1, 0)  # no children
    except ChildProcessError as e:
        ok = e.errno == 10  # ECHILD
    assert ok

    ok = False
    try:
        open('.')
    except IsADirectoryError as e:
        ok = e.filename == '.'
    assert ok

    path = 'shedskin_test_notadir.txt'
    with open(path, 'w') as f:
        f.write('x')
    ok = False
    try:
        os.listdir(path)
    except NotADirectoryError:
        ok = True
    assert ok
    ok = False
    try:
        os.chdir(path)
    except NotADirectoryError:
        ok = True
    assert ok
    ok = False
    try:
        open(path + '/x')
    except NotADirectoryError:
        ok = True
    assert ok
    os.remove(path)

    # remove/unlink must not delete (empty) directories
    # (IsADirectoryError on Linux, PermissionError on macOS)
    path = 'shedskin_test_emptydir'
    os.mkdir(path)
    ok = False
    try:
        os.remove(path)
    except OSError:
        ok = True
    assert ok and os.path.isdir(path)
    ok = False
    try:
        os.unlink(path)
    except OSError:
        ok = True
    assert ok and os.path.isdir(path)
    os.rmdir(path)


def test_oserror_filename():
    # only calls that take a path report it as the filename (like CPython)
    caught = 0
    try:
        os.getpgid(2 ** 22 + 12345)
    except ProcessLookupError as e:
        assert e.filename is None
        caught += 1
    try:
        os.ttyname(987)
    except OSError as e:
        assert e.filename is None
        caught += 1
    try:
        os.mkfifo('shedskin_no_such_dir/fifo')
    except FileNotFoundError as e:
        assert e.filename is None
        caught += 1
    try:
        os.execv('shedskin_no_such_dir/prog', ['prog'])
    except FileNotFoundError as e:
        assert e.filename is None
        caught += 1
    try:
        os.execve('shedskin_no_such_dir/prog', ['prog'], {'A': 'b'})
    except FileNotFoundError as e:
        assert e.filename == 'shedskin_no_such_dir/prog'
        assert str(e) == "[Errno 2] No such file or directory: 'shedskin_no_such_dir/prog'"
        caught += 1
    try:
        os.fstatvfs(987)
    except OSError as e:
        assert e.filename is None
        caught += 1
    assert caught == 6


def test_kwarg_names():
    # keyword argument names should match CPython
    base = '/tmp/shedskin_test_posix_kwarg_names'
    if os.path.exists(base):
        for name in os.listdir(base):
            os.remove(base + '/' + name)
        os.rmdir(base)
    os.mkdir(base)
    f = open(base + '/f', 'w')
    f.close()
    os.link(src=base + '/f', dst=base + '/hard')
    os.symlink(src=base + '/f', dst=base + '/soft')
    assert os.readlink(base + '/soft') == base + '/f'
    assert os.stat(base + '/hard').st_nlink == 2
    for name in os.listdir(base):
        os.remove(base + '/' + name)
    os.rmdir(base)


def test_mknod_default_mode():
    # CPython's default mode for os.mknod is 0o600 (a regular file).
    # macOS (EPERM) and FreeBSD (EINVAL) don't allow mknod() to create
    # regular files, so there pass S_IFIFO explicitly and just check the
    # permission bits.
    path = '/tmp/shedskin_test_mknod_default'
    if os.path.exists(path):
        os.remove(path)
    mask = os.umask(0o022)
    os.umask(mask)
    if not sys.platform.startswith('linux'):
        os.mknod(path=path, mode=stat.S_IFIFO | 0o600)
        assert stat.S_ISFIFO(os.stat(path).st_mode)
    else:
        os.mknod(path=path)
        assert stat.S_ISREG(os.stat(path).st_mode)
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600 & ~mask
    os.remove(path)


def test_direntry_inode_symlink():
    base = 'shedskin_test_direntry_inode_symlink'
    target = os.path.join(base, 'target.txt')
    link = os.path.join(base, 'link')

    os.mkdir(base)
    with open(target, 'w') as f:
        f.write('hi')
    os.symlink('target.txt', link)

    for entry in os.scandir(base):
        # inode() is that of the entry itself, so of the link, not its target
        assert entry.inode() == os.lstat(entry.path).st_ino
        assert not entry.is_junction()
        if entry.name == 'link':
            assert entry.inode() != os.stat(entry.path).st_ino

    os.remove(link)
    os.remove(target)
    os.rmdir(base)


def test_waitstatus_signals():
    assert os.waitstatus_to_exitcode(9) == -9  # killed by SIGKILL
    ok = False
    try:
        os.waitstatus_to_exitcode(0x137f)  # stopped by signal 19
    except ValueError:
        ok = True
    assert ok

    # a real child process
    pid = os.spawnv(os.P_NOWAIT, '/bin/sh', ['sh', '-c', 'exit 7'])
    pid2, status = os.waitpid(pid, 0)
    assert pid2 == pid
    assert os.waitstatus_to_exitcode(status) == 7

    # TODO os._exit in a forked child should not flush the parent's (inherited)
    # stdio buffers; check with fork + _exit while stdout is redirected to a file


def test_broken_pipe():
    # SIGPIPE is ignored, as in CPython, so writing to a pipe without a
    # reader raises BrokenPipeError instead of killing the process
    r, w = os.pipe()
    os.close(r)
    error = 0
    try:
        os.write(w, b'x')
    except BrokenPipeError as e:
        error = e.errno
    assert error == 32
    os.close(w)

    # the same for print() (e.g. when piped into 'head')
    r, w = os.pipe()
    os.close(r)
    sys.stdout.flush()
    pid = os.fork()
    if pid == 0:
        os.dup2(w, 1)
        code = 1
        try:
            for i in range(100000):
                print('x' * 100)
        except BrokenPipeError:
            code = 0
        os._exit(code)
    os.close(w)
    pid2, status = os.waitpid(pid, 0)
    assert os.WIFEXITED(status)
    assert os.WEXITSTATUS(status) == 0


def test_pty_terminal():
    master, slave = os.openpty()
    assert os.device_encoding(slave) == 'utf-8'
    ts = os.get_terminal_size(slave)
    assert ts.columns >= 0 and ts.lines >= 0
    columns, lines = ts
    assert columns == ts.columns
    assert list(ts) == [columns, lines]
    assert [x for x in ts] == [columns, lines]
    os.close(slave)
    os.close(master)

    ok = False
    fd = os.open(os.devnull, os.O_RDONLY)
    try:
        os.get_terminal_size(fd)
    except OSError:
        ok = True
    os.close(fd)
    assert ok


def test_walk_followlinks():
    base = 'shedskin_test_walk_links'
    os.system('rm -rf ' + base)
    os.makedirs(os.path.join(base, 'real', 'sub'))
    with open(os.path.join(base, 'real', 'sub', 'f.txt'), 'w') as f:
        f.write('x')
    with open(os.path.join(base, 'file.txt'), 'w') as f:
        f.write('x')
    os.symlink('real', os.path.join(base, 'link'))

    # symlinked directories are listed in dirnames, but only descended
    # into with followlinks=True
    for followlinks in (False, True):
        seen = []
        for root, dirs, files in os.walk(base, followlinks=followlinks):
            seen.append((root, sorted(dirs), sorted(files)))
        seen.sort()
        expected = [(base, ['link', 'real'], ['file.txt'])]
        if followlinks:
            expected += [(base + '/link', ['sub'], []), (base + '/link/sub', [], ['f.txt'])]
        expected += [(base + '/real', ['sub'], []), (base + '/real/sub', [], ['f.txt'])]
        assert seen == expected

    roots = []
    for root, dirs, files in os.walk(base, topdown=False, followlinks=True):
        roots.append(root)
    assert roots[-1] == base
    assert sorted(roots) == [base, base + '/link', base + '/link/sub', base + '/real', base + '/real/sub']

    os.system('rm -rf ' + base)


def test_direntry_follow_symlinks():
    base = 'shedskin_test_direntry_links'
    os.system('rm -rf ' + base)
    os.mkdir(base)
    os.mkdir(os.path.join(base, 'real'))
    with open(os.path.join(base, 'file.txt'), 'w') as f:
        f.write('x')
    os.symlink('real', os.path.join(base, 'link'))
    os.symlink('file.txt', os.path.join(base, 'flink'))
    os.symlink('nowhere', os.path.join(base, 'dangling'))

    info = {}
    for entry in os.scandir(base):
        info[entry.name] = (entry.is_dir(), entry.is_dir(follow_symlinks=False),
                            entry.is_file(), entry.is_file(follow_symlinks=False),
                            entry.is_symlink())
        if entry.name != 'dangling':
            assert entry.stat().st_ino == os.stat(entry.path).st_ino
        assert entry.stat(follow_symlinks=False).st_ino == os.lstat(entry.path).st_ino

    assert info['real'] == (True, True, False, False, False)
    assert info['file.txt'] == (False, False, True, True, False)
    assert info['link'] == (True, False, False, False, True)
    assert info['flink'] == (False, False, True, False, True)
    assert info['dangling'] == (False, False, False, False, True)

    # following a dangling link fails
    for entry in os.scandir(base):
        if entry.name == 'dangling':
            ok = False
            try:
                entry.stat()
            except FileNotFoundError:
                ok = True
            assert ok

    os.system('rm -rf ' + base)


def test_inheritable():
    # like cpython (PEP 446): new file descriptors are non-inheritable
    path = 'tmp_inheritable.txt'
    f = open(path, 'w')
    assert not os.get_inheritable(f.fileno())
    f.write('x')
    f.close()
    g = open(path, 'rb')
    assert not os.get_inheritable(g.fileno())
    g.close()

    r, w = os.pipe()
    assert not os.get_inheritable(r)
    assert not os.get_inheritable(w)
    fd = os.open(path, os.O_RDONLY)
    assert not os.get_inheritable(fd)
    fd2 = os.dup(fd)
    assert not os.get_inheritable(fd2)
    m, sl = os.openpty()
    assert not os.get_inheritable(m)
    assert not os.get_inheritable(sl)

    # dup2 is the exception: inheritable unless asked otherwise
    assert os.dup2(fd, fd2) == fd2
    assert os.get_inheritable(fd2)
    os.dup2(fd, fd2, inheritable=False)
    assert not os.get_inheritable(fd2)

    # a child process only sees inheritable descriptors
    if fd < 10:  # sh redirections take a single digit
        cmd = 'true 2>/dev/null <&%d' % fd
        assert os.system(cmd) != 0
        os.set_inheritable(fd, True)
        assert os.get_inheritable(fd)
        assert os.system(cmd) == 0
        os.set_inheritable(fd, False)
        assert os.system(cmd) != 0

    for x in [r, w, fd, fd2, m, sl]:
        os.close(x)
    os.remove(path)


def test_close_after_failed_flush():
    # close() closes the file even when the final flush fails
    f = open('cftest.txt', 'w')
    f.write('abc')
    os.close(f.fileno())
    err = 0
    try:
        f.close()
    except OSError as e:
        err = e.errno
    assert err == 9
    assert f.closed
    f.close()  # no-op now

    g = open('cftest.txt', 'wb')
    g.write(b'abc')
    os.close(g.fileno())
    err = 0
    try:
        g.close()
    except OSError as e:
        err = e.errno
    assert err == 9
    assert g.closed
    g.close()
    os.remove('cftest.txt')


def test_pathconf_errors():
    assert os.pathconf('.', 'PC_NAME_MAX') > 0
    assert os.sysconf('SC_PAGE_SIZE') > 0
    assert os.confstr('CS_PATH') != ''
    try:
        os.pathconf('nope.txt', 'PC_NAME_MAX')
        assert False
    except OSError as e:
        assert str(e) == "[Errno 2] No such file or directory: 'nope.txt'"
        assert e.filename == 'nope.txt'
    try:  # EINVAL could be the name as well as the path: no filename
        os.pathconf('.', 99999)
        assert False
    except OSError as e:
        assert str(e) == '[Errno 22] Invalid argument'
        assert e.filename is None
    try:
        os.fpathconf(987, 'PC_NAME_MAX')
        assert False
    except OSError as e:
        assert str(e) == '[Errno 9] Bad file descriptor'
    try:
        os.sysconf(987654)
        assert False
    except OSError as e:
        assert e.errno == 22
    try:
        os.confstr(987654)
        assert False
    except OSError as e:
        assert e.errno == 22


def test_setsid():
    # in a forked child, so the session of the test runner is left alone
    sys.stdout.flush()
    pid = os.fork()
    if pid == 0:
        code = 1
        if os.setsid() is None and os.getsid(0) == os.getpid():
            code = 0
        os._exit(code)
    pid2, status = os.waitpid(pid, 0)
    assert os.WIFEXITED(status)
    assert os.WEXITSTATUS(status) == 0


def test_wait_status_macros():
    assert os.WIFEXITED(256) and os.WEXITSTATUS(256) == 1
    assert not os.WIFSIGNALED(256) and not os.WIFSTOPPED(256)
    assert os.WIFSIGNALED(9) and os.WTERMSIG(9) == 9
    assert os.WCOREDUMP(9 | 0x80) and not os.WCOREDUMP(9)
    assert os.WIFSTOPPED((5 << 8) | 0x7f) and os.WSTOPSIG((5 << 8) | 0x7f) == 5
    assert not os.WIFCONTINUED(256)
    # C int argument: an OverflowError instead of truncation to 256
    big = 2 ** 32 + 256
    errors = []
    try:
        os.WEXITSTATUS(big)
    except OverflowError as e:
        errors.append(str(e))
    try:
        os.WSTOPSIG(big)
    except OverflowError as e:
        errors.append(str(e))
    try:
        os.WTERMSIG(big)
    except OverflowError as e:
        errors.append(str(e))
    try:
        os.WCOREDUMP(big)
    except OverflowError as e:
        errors.append(str(e))
    try:
        os.WIFCONTINUED(big)
    except OverflowError as e:
        errors.append(str(e))
    try:
        os.WIFEXITED(big)
    except OverflowError as e:
        errors.append(str(e))
    try:
        os.WIFSIGNALED(big)
    except OverflowError as e:
        errors.append(str(e))
    try:
        os.WIFSTOPPED(big)
    except OverflowError as e:
        errors.append(str(e))
    assert errors == 8 * ['Python int too large to convert to C int']


def test_device_numbers():
    dev = os.makedev(8, 1)
    assert os.major(dev) == 8 and os.minor(dev) == 1
    if sys.platform == 'darwin':  # 8-bit major, 24-bit minor: NODEV is no fixpoint
        assert os.major(-1) == 255 and os.minor(-1) == 16777215
    else:
        assert os.major(-1) == -1 and os.minor(-1) == -1
    if sys.platform == 'linux':
        # dev_t is 64 bits: the major number is not truncated to 32 bits
        dev = os.makedev(5000, 70000)
        assert dev == 17592472537200
        assert os.major(dev) == 5000
        assert os.minor(dev) == 70000
        assert os.major(2 ** 32 + 1) == 0 and os.minor(2 ** 32 + 1) == 1048577
    errors = []
    for args in [(2 ** 32 + 1, 0), (0, 2 ** 32), (-2, 0)]:
        try:
            os.makedev(args[0], args[1])
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
    for v in [-2, -2 ** 40]:
        try:
            os.major(v)
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
        try:
            os.minor(v)
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
    try:
        os.mknod('shedskin_test_mknod', 0o600, -2)
        errors.append('none')
    except OverflowError as e:
        errors.append(str(e))
    if sys.platform == 'darwin':  # dev_t is a signed 32-bit int
        too_large = 'Python int too large to convert to C dev_t'
    else:
        too_large = 'Python int too large to convert to C unsigned int'
    assert errors == 2 * [too_large] + 6 * ["can't convert negative int to unsigned"]
    assert not os.path.exists('shedskin_test_mknod')


def test_uid_gid_overflow():
    # uid/gid arguments are not truncated (chown would give the file to the
    # wrong user); -1 and its unsigned equivalent mean 'unchanged'
    path = 'shedskin_test_chown.txt'
    open(path, 'w').close()
    st = os.stat(path)
    os.chown(path, -1, -1)
    os.chown(path, 2 ** 32 - 1, 2 ** 32 - 1)
    os.lchown(path, -1, 2 ** 32 - 1)
    os.setreuid(-1, -1)
    os.setregid(-1, -1)
    st2 = os.stat(path)
    assert (st2.st_uid, st2.st_gid) == (st.st_uid, st.st_gid)
    errors = []
    for v in [2 ** 32 + 1234, 2 ** 32, -2, 2 ** 63 - 1]:
        try:
            os.chown(path, v, -1)
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
        try:
            os.lchown(path, -1, v)
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
        try:
            os.setuid(v)
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
        try:
            os.setegid(v)
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
        try:
            os.setreuid(v, -1)
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
        try:
            os.setgroups([v])
            errors.append('none')
        except OverflowError as e:
            errors.append(str(e))
    assert errors == 4 * ['uid is less than minimum', 'gid is less than minimum', 'uid is less than minimum', 'gid is less than minimum', 'uid is less than minimum', 'gid is less than minimum']
    st2 = os.stat(path)
    assert (st2.st_uid, st2.st_gid) == (st.st_uid, st.st_gid)
    os.remove(path)


def _mode_at(path: str) -> int:
    return os.stat(path).st_mode & 0o777


def test_chmod_chown_access_link_at():
    # dir_fd/follow_symlinks (and effective_ids for access), as CPython;
    # these used to be dropped, so e.g. the target of a symlink changed
    top = 'shedskin_test_at2'
    target = os.path.join(top, 'x.txt')
    os.mkdir(top)
    with open(target, 'w') as f:
        f.write('hi')
    os.symlink('x.txt', os.path.join(top, 'lnk'))
    os.symlink('nowhere', os.path.join(top, 'dang'))
    d = os.open(top, os.O_RDONLY)
    # chmod
    os.chmod('x.txt', 0o640, dir_fd=d)
    assert _mode_at(target) == 0o640
    os.chmod('lnk', 0o604, dir_fd=d)  # (follows)
    assert _mode_at(target) == 0o604
    os.chmod(target, 0o600, follow_symlinks=False)  # (a regular file)
    assert _mode_at(target) == 0o600
    fd = os.open(target, os.O_RDONLY)
    os.chmod(fd, 0o644)
    assert _mode_at(target) == 0o644
    try:
        os.chmod('nope', 0o600, dir_fd=d)
        assert False
    except FileNotFoundError as e:
        assert e.filename == 'nope'
    # chown (-1: unchanged)
    os.chown('lnk', -1, -1, dir_fd=d, follow_symlinks=False)
    os.chown(os.path.join(top, 'dang'), -1, -1, follow_symlinks=False)
    try:
        os.chown(os.path.join(top, 'dang'), -1, -1)
        assert False
    except FileNotFoundError:
        pass
    os.chown(fd, -1, -1)
    try:
        os.chown(fd, -1, -1, follow_symlinks=False)
        assert False
    except ValueError as e2:
        assert str(e2) == 'chown: cannot use fd and follow_symlinks together'
    try:
        os.chown(fd, -1, -1, dir_fd=d)
        assert False
    except ValueError as e3:
        assert str(e3) == "chown: can't specify both dir_fd and fd"
    os.close(fd)
    # access
    assert os.access('dang', os.F_OK, dir_fd=d, follow_symlinks=False)
    assert not os.access('dang', os.F_OK, dir_fd=d)
    assert os.access('x.txt', os.R_OK, dir_fd=d, effective_ids=True)
    assert not os.access('x.txt', os.R_OK, dir_fd=9999)
    # link: with a dir_fd, follow_symlinks=True follows (linkat)
    os.link('lnk', 'h1', src_dir_fd=d, dst_dir_fd=d)
    assert not os.path.islink(os.path.join(top, 'h1'))
    os.link('lnk', 'h2', src_dir_fd=d, dst_dir_fd=d, follow_symlinks=False)
    assert os.path.islink(os.path.join(top, 'h2'))
    os.link('x.txt', os.path.join(top, 'h3'), src_dir_fd=d)
    assert os.path.exists(os.path.join(top, 'h3'))
    try:
        os.link('nope', 'h4', src_dir_fd=d, dst_dir_fd=d)
        assert False
    except FileNotFoundError as e4:
        assert e4.filename == 'nope' and e4.filename2 == 'h4'
    os.close(d)
    for name in sorted(os.listdir(top)):
        os.remove(os.path.join(top, name))
    os.rmdir(top)


def test_fd_statvfs_pathconf():
    # statvfs and pathconf also take an fd, as CPython
    path = 'shedskin_test_fd_statvfs.txt'
    with open(path, 'w') as f:
        f.write('hello')
    fd = os.open(path, os.O_RDONLY)
    assert os.statvfs(fd).f_bsize > 0
    assert os.pathconf(fd, 'PC_NAME_MAX') == os.pathconf(path, 'PC_NAME_MAX')
    os.close(fd)
    os.remove(path)


def test_mkfifo_dir_fd():
    if sys.platform == 'darwin':  # (mkfifoat/mknodat: macOS 13+ only)
        return
    top = 'shedskin_test_mkfifo_dir_fd'
    os.mkdir(top)
    d = os.open(top, os.O_RDONLY)
    os.mkfifo('ff', dir_fd=d)
    assert os.listdir(top) == ['ff']
    assert stat.S_ISFIFO(os.stat(os.path.join(top, 'ff')).st_mode)
    os.unlink('ff', dir_fd=d)
    assert os.listdir(top) == []
    os.close(d)
    os.rmdir(top)


def test_long_cwd_and_os_names():
    # getcwd() of a path longer than 255 bytes (crashed)
    cwd = os.getcwd()
    base = 'shedskin_test_long_cwd'
    os.mkdir(base)
    os.chdir(base)
    for i in range(30):
        os.mkdir('directory_' + str(i))
        os.chdir('directory_' + str(i))
    long_cwd = os.getcwd()
    assert len(long_cwd) > 300
    assert os.path.basename(long_cwd) == 'directory_29'
    assert len(os.getcwdb()) == len(os.fsencode(long_cwd))
    os.chdir(cwd)
    for i in range(29, -1, -1):
        os.rmdir('/'.join([base] + ['directory_' + str(j) for j in range(i + 1)]))
    os.rmdir(base)

    # os-supplied names: an encoded surrogate gives three escapes, which
    # round-trip (not a lone surrogate)
    name = os.fsdecode(b'shedskin_\xed\xa0\x80')
    assert name == 'shedskin_\udced\udca0\udc80'
    if sys.platform != 'darwin':  # (macOS: EILSEQ, names must be valid utf-8)
        f = open(name, 'w')
        f.write('z')
        f.close()
        assert name in os.listdir('.')
        assert name in [e.name for e in os.scandir('.')]
        assert os.stat(name).st_size == 1
        os.symlink(name, 'shedskin_link')
        assert os.readlink('shedskin_link') == name
        os.remove('shedskin_link')
        os.remove(name)

    # os.popen text pipes are strict, as open()
    p = os.popen("printf 'a\\377'")
    err = ''
    try:
        p.read()
    except UnicodeDecodeError as e:
        err = e.reason
    p.close()
    assert err == 'invalid start byte'


def test_exec_spawn_failures():
    # a failed exec in a spawned child: exit code 127, the child stops
    assert os.spawnv(os.P_WAIT, '/nonexistent/x', ['x']) == 127
    assert os.spawnvp(os.P_WAIT, 'shedskin_no_such_cmd', ['x']) == 127
    # argv checks, before anything is executed
    a = ['x']
    a.pop()
    msg = ''
    try:
        os.execv('/bin/true', a)
    except ValueError as e:
        msg = str(e)
    assert msg == 'execv() arg 2 must not be empty'
    msg = ''
    try:
        os.execv('/bin/true', [''])
    except ValueError as e:
        msg = str(e)
    assert msg == 'execv() arg 2 first element cannot be empty'
    msg = ''
    try:
        os.spawnv(os.P_WAIT, '/bin/true', a)
    except ValueError as e:
        msg = str(e)
    assert msg == 'argv first element cannot be empty'
    # execvp continues past a PATH entry that cannot be executed
    d = 'shedskin_test_path'
    os.mkdir(d)
    f = open(os.path.join(d, 'sh'), 'w')
    f.write('')
    f.close()
    os.chmod(os.path.join(d, 'sh'), 0o644)
    env = {'PATH': os.path.abspath(d) + ':/bin:/usr/bin'}
    assert os.spawnvpe(os.P_WAIT, 'sh', ['sh', '-c', 'exit 3'], env) == 3
    os.remove(os.path.join(d, 'sh'))
    os.rmdir(d)


def test_wait_exec_utime_edges():
    # WNOHANG with no child ready: status 0
    pid = os.fork()
    if pid == 0:
        r, w = os.pipe()
        os.read(r, 1)  # (blocks until killed)
        os._exit(0)
    assert os.waitpid(pid, os.WNOHANG) == (0, 0)
    os.kill(pid, 9)
    os.waitpid(pid, 0)

    # a failed execvp keeps its OSError subclass
    caught = ''
    try:
        os.execvp('shedskin-no-such-prog', ['x'])
    except FileNotFoundError:
        caught = 'fnf'
    assert caught == 'fnf'

    # execve wording, and environment names
    a = ['x']
    a.pop()
    msg = ''
    try:
        os.execve('/bin/true', a, {'A': 'b'})
    except ValueError as e:
        msg = str(e)
    assert msg == 'execve: argv must not be empty'
    msg = ''
    try:
        os.execve('/bin/true', [''], {'A': 'b'})
    except ValueError as e:
        msg = str(e)
    assert msg == 'execve: argv first element cannot be empty'
    for env in [{'A=B': 'x'}, {'': 'x'}]:
        msg = ''
        try:
            os.execve('/bin/true', ['true'], env)
        except ValueError as e:
            msg = str(e)
        assert msg == 'illegal environment variable name'

    # utime with a float that does not fit
    name = 'shedskin_test_utime_range'
    f = open(name, 'w')
    f.close()
    for t in [1e30, float('inf'), -9.3e18]:
        msg = ''
        try:
            os.utime(name, (t, 5.0))
        except OverflowError as e:
            msg = str(e)
        assert msg == 'timestamp out of range for platform time_t'
    msg = ''
    try:
        os.utime(name, (float('nan'), 5.0))
    except ValueError as e:
        msg = str(e)
    assert msg == 'Invalid value NaN (not a number)'
    os.utime(name, (1.5, 2.25))
    assert os.stat(name).st_mtime == 2.25
    os.remove(name)


def test_spawn_variants():
    # spawnle/spawnlpe: env after mode and file
    assert os.spawnle(os.P_WAIT, '/bin/sh', 'sh', '-c', 'exit $X', {'X': '11'}) == 11
    assert os.spawnlpe(os.P_WAIT, 'sh', 'sh', '-c', 'exit $X', {'X': '12', 'PATH': '/bin:/usr/bin'}) == 12
    # only P_NOWAIT returns the pid; other modes wait (as CPython)
    assert os.spawnv(2, '/bin/sh', ['sh', '-c', 'exit 4']) == 4


def test_std_streams_nice_tty_fdopen():
    # closing sys.stdout/stdin/stderr leaves fds 0/1/2 open (in a child)
    pid = os.fork()
    if pid == 0:
        code = 0
        try:
            sys.stdout.flush()
            sys.stdout.close()
            sys.stderr.close()
            sys.stdin.close()
            os.fstat(0)
            os.fstat(1)
            os.fstat(2)
        except OSError:
            code = 1
        os._exit(code)
    assert os.waitpid(pid, 0)[1] == 0

    # nice(): -1 is a valid niceness (root only, in a child)
    if os.getuid() == 0:
        pid = os.fork()
        if pid == 0:
            code = 0
            try:
                if os.nice(-1) != -1:
                    code = 2
            except OSError:
                code = 1
            os._exit(code)
        assert os.waitpid(pid, 0)[1] == 0

    # a text file on a terminal is line buffered ('\r' flushes too)
    m, s = os.openpty()
    f = os.fdopen(s, 'w')
    assert f.line_buffering
    f.write('10%\r')
    assert os.read(m, 100) == b'10%\r'
    f.close()
    os.close(m)

    # os.fdopen(.., closefd=False)
    name = 'shedskin_test_fdopen_closefd'
    fd = os.open(name, os.O_RDWR | os.O_CREAT, 0o644)
    os.write(fd, b'ab')
    os.lseek(fd, 0, 0)
    g = os.fdopen(fd, 'rb', closefd=False)
    assert g.read() == b'ab'
    g.close()
    assert os.lseek(fd, 0, os.SEEK_CUR) == 2
    os.close(fd)
    os.remove(name)


def test_direntry_errors_keyboardinterrupt():
    # DirEntry.is_dir()/is_file() only treat a missing target as False
    os.mkdir('shedskin_test_de')
    os.symlink('loop2', 'shedskin_test_de/loop1')
    os.symlink('loop1', 'shedskin_test_de/loop2')
    os.symlink('nowhere', 'shedskin_test_de/dangling')
    for e in os.scandir('shedskin_test_de'):
        if e.name == 'dangling':
            assert not e.is_dir()
            assert not e.is_file()
        else:
            code = 0
            try:
                e.is_dir()
            except OSError as err:
                code = err.errno
            assert code in (40, 62), e.name  # ELOOP (linux, macOS/BSD)
    for n in ['loop1', 'loop2', 'dangling']:
        os.remove('shedskin_test_de/' + n)
    os.rmdir('shedskin_test_de')

    # an uncaught KeyboardInterrupt ends the process by SIGINT
    pid = os.fork()
    if pid == 0:
        r = os.open('/dev/null', os.O_WRONLY)
        os.dup2(r, 1)  # (the message)
        os.dup2(r, 2)
        raise KeyboardInterrupt
    assert os.waitstatus_to_exitcode(os.waitpid(pid, 0)[1]) == -2


def test_getrandom_conf_names():
    code = 0
    try:
        os.getrandom(-1)
    except OSError as e:
        code = e.errno
    assert code == 22
    if sys.platform == 'linux':
        assert os.confstr('CS_GNU_LIBC_VERSION') is not None
        assert os.pathconf('/', 'PC_SYMLINK_MAX') is not None
        assert 'PC_ALLOC_SIZE_MIN' in os.pathconf_names


def test_getrandom_flags():
    assert len(os.urandom(100)) == 100
    if sys.platform == 'linux':
        assert len(os.getrandom(16, os.GRND_NONBLOCK)) == 16
        assert len(os.getrandom(0)) == 0
        code = 0
        try:
            os.getrandom(5, 12345)
        except OSError as e:
            code = e.errno
        assert code == 22


def test_negative_fd_unsetenv_pipe_walk():
    msg = ''
    try:
        os.fsync(-1)
    except ValueError as e:
        msg = str(e)
    assert msg == 'file descriptor cannot be a negative integer (-1)'
    msg = ''
    try:
        os.fchdir(-1)
    except ValueError as e:
        msg = str(e)
    assert msg == 'file descriptor cannot be a negative integer (-1)'
    msg = ''
    try:
        os.fpathconf(-1, 'PC_NAME_MAX')
    except ValueError as e:
        msg = str(e)
    assert msg == 'file descriptor cannot be a negative integer (-1)'
    msg = ''
    try:
        os.times_result((1.0, 2.0))
    except TypeError as e:
        msg = str(e)
    assert msg == 'posix.times_result() takes a 5-sequence (2-sequence given)'
    # invalid names
    code = 0
    try:
        os.unsetenv('a=b')
    except OSError as e:
        code = e.errno
    assert code == 22
    # walk: a backslash is not a separator here
    os.makedirs('shedskin_test_walk\\/sub')
    roots = []
    for root, dirs, files in os.walk('shedskin_test_walk\\'):
        roots.append(root)
    assert roots == ['shedskin_test_walk\\', 'shedskin_test_walk\\/sub']
    os.rmdir('shedskin_test_walk\\/sub')
    os.rmdir('shedskin_test_walk\\')


def test_all():
    test_kill()
    test_link_unlink_lstat_readlink()
    test_walk_followlinks()
    test_direntry_follow_symlinks()
    test_chmod()
    test_fchmod()
    test_blocking()
    test_uname()
    test_statvfs()
    test_popen_spawn()
    test_times_children()
    test_misc_constants()
    test_oserror_subclasses()
    test_oserror_filename()
    test_kwarg_names()
    test_direntry_inode_symlink()
    test_mknod_default_mode()
    test_waitstatus_signals()
    test_broken_pipe()
    test_pty_terminal()
    test_inheritable()
    test_close_after_failed_flush()
    test_pathconf_errors()
    test_setsid()
    test_wait_status_macros()
    test_device_numbers()
    test_uid_gid_overflow()
    test_chmod_chown_access_link_at()
    test_fd_statvfs_pathconf()
    test_mkfifo_dir_fd()
    test_long_cwd_and_os_names()
    test_exec_spawn_failures()
    test_wait_exec_utime_edges()
    test_spawn_variants()
    test_std_streams_nice_tty_fdopen()
    test_direntry_errors_keyboardinterrupt()
    test_getrandom_conf_names()
    test_getrandom_flags()
    test_negative_fd_unsetenv_pipe_walk()

if __name__ == '__main__':
    test_all()
