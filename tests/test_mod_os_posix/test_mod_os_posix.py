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


def test_all():
    test_kill()
    test_link_unlink_lstat_readlink()
    test_chmod()
    test_popen_spawn()
    test_times_children()
    test_misc_constants()
    test_oserror_subclasses()
    test_kwarg_names()
    test_direntry_inode_symlink()
    test_mknod_default_mode()


if __name__ == '__main__':
    test_all()
