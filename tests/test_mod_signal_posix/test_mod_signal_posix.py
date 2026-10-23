import os
import signal

# posix-only: pthread_sigmask, sigpending, sigwait


def test_sigmask():
    usr1, usr2 = signal.SIGUSR1, signal.SIGUSR2

    # a blocked signal stays pending, instead of killing the process
    old = signal.pthread_sigmask(signal.SIG_BLOCK, [usr1, usr2])
    assert usr1 not in old and usr2 not in old
    assert usr1 not in signal.sigpending()
    os.kill(os.getpid(), usr1)
    pending = signal.sigpending()
    assert usr1 in pending and usr2 not in pending

    # sigwait takes it
    assert signal.sigwait({usr1, usr2}) == usr1
    assert usr1 not in signal.sigpending()

    # the previous mask comes back; any iterable gives the signals
    old = signal.pthread_sigmask(signal.SIG_UNBLOCK, (usr2,))
    assert usr1 in old and usr2 in old
    old = signal.pthread_sigmask(signal.SIG_SETMASK, {usr2})
    assert usr1 in old and usr2 not in old
    old = signal.pthread_sigmask(signal.SIG_UNBLOCK, [usr2])
    assert usr2 in old and usr1 not in old
    assert usr2 not in signal.pthread_sigmask(signal.SIG_BLOCK, [usr1])
    signal.pthread_sigmask(signal.SIG_UNBLOCK, [usr1])

    for bad in [0, -1, 100000]:
        try:
            signal.pthread_sigmask(signal.SIG_BLOCK, [bad])
            assert False
        except ValueError as e:
            assert str(e).startswith('signal number %d out of range [1; ' % bad)

    try:
        signal.pthread_sigmask(12345, [usr1])
        assert False
    except OSError as e:
        assert e.errno == 22  # EINVAL


def test_all():
    test_sigmask()


if __name__ == '__main__':
    test_all()
