# os functionality that is #ifndef WIN32 in lib/os (see CMakeLists.txt);
# portable os tests live in test_mod_os

import os
import stat


def test_kill():
    pid = os.getpid()
    # signal 0 only checks that the process exists
    os.kill(pid, 0)
    try:
        os.kill(2 ** 22 + 12345, 0)
        assert False, 'expected an error for a non-existent pid'
    except OSError as e:  # ProcessLookupError
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


def test_all():
    test_kill()
    test_link_unlink_lstat_readlink()
    test_chmod()
    test_popen_spawn()
    test_times_children()
    test_misc_constants()


if __name__ == '__main__':
    test_all()
