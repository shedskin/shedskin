import signal


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


def test_all():
    test_signal_constants()


if __name__ == '__main__':
    test_all()
