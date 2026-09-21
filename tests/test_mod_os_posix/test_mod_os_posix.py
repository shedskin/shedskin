# os functionality that is #ifndef WIN32 in lib/os (see CMakeLists.txt);
# portable os tests live in test_mod_os

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

    # P_NOWAIT: the return value is a pid, to be collected with waitpid
    pid = os.spawnv(os.P_NOWAIT, '/bin/sh', ['sh', '-c', 'exit 7'])
    assert pid > 0
    wpid, status = os.waitpid(pid, 0)
    assert wpid == pid
    assert os.WIFEXITED(status)
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
    # macOS only allows unprivileged mknod() for FIFOs (EPERM otherwise),
    # so there pass S_IFIFO explicitly and just check the permission bits.
    path = '/tmp/shedskin_test_mknod_default'
    if os.path.exists(path):
        os.remove(path)
    mask = os.umask(0o022)
    os.umask(mask)
    if sys.platform == 'darwin':
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


def test_all():
    test_kill()
    test_link_unlink_lstat_readlink()
    test_walk_followlinks()
    test_direntry_follow_symlinks()
    test_chmod()
    test_fchmod()
    test_blocking()
    test_uname()
    test_popen_spawn()
    test_times_children()
    test_misc_constants()
    test_oserror_subclasses()
    test_kwarg_names()
    test_direntry_inode_symlink()
    test_mknod_default_mode()
    test_waitstatus_signals()
    test_pty_terminal()


if __name__ == '__main__':
    test_all()
