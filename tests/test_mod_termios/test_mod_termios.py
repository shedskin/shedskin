import os
import sys
import termios
import tty


def test_constants():
    assert termios.ECHO > 0
    assert termios.ICANON > 0
    assert termios.TCSANOW != termios.TCSAFLUSH
    assert termios.VMIN != termios.VTIME
    assert termios.NCCS > termios.VMIN
    assert tty.LFLAG == 3
    assert tty.CC == 6


def test_attributes():
    master, slave = os.openpty()
    try:
        mode = termios.tcgetattr(slave)
        assert len(mode) == 7
        assert mode[tty.LFLAG] & termios.ICANON

        new = termios.tcgetattr(slave)
        new[tty.LFLAG] = new[tty.LFLAG] & ~termios.ECHO
        termios.tcsetattr(slave, termios.TCSANOW, new)
        assert not termios.tcgetattr(slave)[tty.LFLAG] & termios.ECHO
        assert termios.tcgetattr(slave)[tty.LFLAG] & termios.ICANON
        termios.tcsetattr(slave, termios.TCSANOW, mode)
        assert termios.tcgetattr(slave) == mode

        # setraw returns the attributes before
        saved = tty.setraw(slave)
        assert saved == mode
        raw = termios.tcgetattr(slave)
        assert not raw[tty.LFLAG] & (termios.ECHO | termios.ICANON | termios.ISIG)
        assert not raw[tty.OFLAG] & termios.OPOST
        assert raw[tty.CFLAG] & termios.CSIZE == termios.CS8
        termios.tcsetattr(slave, termios.TCSAFLUSH, saved)
        assert termios.tcgetattr(slave) == mode

        saved = tty.setcbreak(slave, termios.TCSANOW)
        cbreak = termios.tcgetattr(slave)
        assert not cbreak[tty.LFLAG] & (termios.ECHO | termios.ICANON)
        assert cbreak[tty.LFLAG] & termios.ISIG
        termios.tcsetattr(slave, termios.TCSANOW, saved)

        termios.tcdrain(slave)
        termios.tcflush(slave, termios.TCIOFLUSH)
        termios.tcsetwinsize(slave, (24, 80))
        assert termios.tcgetwinsize(slave) == (24, 80)
    finally:
        os.close(master)
        os.close(slave)


def test_error():
    fd = os.open(os.devnull, os.O_RDONLY)
    try:
        termios.tcgetattr(fd)
        assert False
    except termios.error as e:
        assert str(e) == "(25, 'Inappropriate ioctl for device')", str(e)
    finally:
        os.close(fd)


def test_all():
    if sys.platform == 'win32':
        return
    test_constants()
    test_attributes()
    test_error()


if __name__ == '__main__':
    test_all()
