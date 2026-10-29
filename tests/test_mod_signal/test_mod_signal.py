import signal
import sys


def test_signal_constants():
    # only the handful of signals guaranteed by the C standard on every
    # platform shedskin targets (linux, macos, windows); most POSIX
    # signals below this set don't exist on Windows
    assert signal.SIGABRT > 0
    assert signal.SIGFPE > 0
    assert signal.SIGILL > 0
    assert signal.SIGINT > 0
    assert signal.SIGSEGV > 0
    assert signal.SIGTERM > 0

    # they must all be distinct signal numbers
    vals = [signal.SIGABRT, signal.SIGFPE, signal.SIGILL,
            signal.SIGINT, signal.SIGSEGV, signal.SIGTERM]
    assert len(set(vals)) == len(vals)


def test_pthread_sigmask_overflow():
    # 'how' is a C int: no silent truncation to SIG_BLOCK
    for how in [2 ** 32 + signal.SIG_BLOCK, -2 ** 31 - 1]:
        try:
            signal.pthread_sigmask(how, [signal.SIGUSR1])
            assert False
        except OverflowError as e:
            assert str(e) == 'Python int too large to convert to C int'
    assert signal.SIGUSR1 not in signal.pthread_sigmask(signal.SIG_BLOCK, [])


def test_all():
    test_signal_constants()
    if sys.platform != 'win32':
        test_pthread_sigmask_overflow()


if __name__ == '__main__':
    test_all()
