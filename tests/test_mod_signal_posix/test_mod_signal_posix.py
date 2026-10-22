import os
import signal
import time

# posix-only: os.fork


received = []


def handler(signum, frame):
    received.append(signum)


class Stop(Exception):
    pass


def stopper(signum, frame):
    raise Stop('stop %d' % signum)


def test_signal_kill():
    del received[:]
    signal.signal(signal.SIGUSR1, handler)
    os.kill(os.getpid(), signal.SIGUSR1)
    assert received == [signal.SIGUSR1]

    # a signal from another process interrupts a sleep
    signal.signal(signal.SIGUSR2, stopper)
    pid = os.fork()
    if pid == 0:
        time.sleep(0.05)
        os.kill(os.getppid(), signal.SIGUSR2)
        os._exit(0)
    start = time.monotonic()
    try:
        time.sleep(10)
        assert False
    except Stop:
        pass
    assert time.monotonic() - start < 5
    os.waitpid(pid, 0)

    assert signal.strsignal(signal.SIGTERM).startswith('Terminated')  # macOS adds ': 15'


def test_all():
    test_signal_kill()


if __name__ == '__main__':
    test_all()
