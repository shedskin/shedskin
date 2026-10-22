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


received = []


def handler(signum, frame):
    received.append(signum)


class Stop(Exception):
    pass


def stopper(signum, frame):
    raise Stop('stop %d' % signum)


def exiter(signum, frame):
    sys.exit(128 + signum)


def test_signal_handler():
    signal.signal(signal.SIGTERM, handler)
    signal.raise_signal(signal.SIGTERM)  # the handler runs right after
    assert received == [signal.SIGTERM]

    # an exception raised by the handler comes out where it runs
    signal.signal(signal.SIGTERM, stopper)
    try:
        signal.raise_signal(signal.SIGTERM)
        assert False
    except Stop as e:
        assert str(e) == 'stop %d' % signal.SIGTERM

    # sys.exit in a handler leaves through the finally blocks
    cleaned = []
    signal.signal(signal.SIGTERM, exiter)
    try:
        try:
            signal.raise_signal(signal.SIGTERM)
        finally:
            cleaned.append(True)
    except SystemExit as e:
        assert e.code == 128 + signal.SIGTERM
    assert cleaned == [True]

    signal.signal(signal.SIGTERM, handler)

    try:
        signal.signal(0, handler)
        assert False
    except ValueError as e:
        assert str(e) == 'signal number out of range'


def test_all():
    test_signal_constants()
    test_signal_handler()


if __name__ == '__main__':
    test_all()
