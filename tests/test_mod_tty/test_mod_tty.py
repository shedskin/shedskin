import copy
import os
import termios
import tty


# in non-canonical mode, CPython returns cc[VMIN] and cc[VTIME] as ints, else
# as bytes (shedskin: always bytes). this reads them in a compatible way
def ccval(v):
    try:
        return ord(v)
    except TypeError:
        return int(v)


def test_indices():
    assert (tty.IFLAG, tty.OFLAG, tty.CFLAG, tty.LFLAG) == (0, 1, 2, 3)
    assert (tty.ISPEED, tty.OSPEED, tty.CC) == (4, 5, 6)


def test_reexport():
    # like CPython, tty re-exports everything from termios
    assert tty.ECHO == termios.ECHO
    assert tty.TCSAFLUSH == termios.TCSAFLUSH
    assert tty.VMIN == termios.VMIN
    master, slave = os.openpty()
    attrs = tty.tcgetattr(slave)
    assert attrs == termios.tcgetattr(slave)
    tty.tcsetattr(slave, tty.TCSANOW, attrs)
    r, w = os.pipe()
    try:
        tty.tcgetattr(r)
        assert False
    except tty.error:
        pass
    os.close(r)
    os.close(w)
    os.close(slave)
    os.close(master)


def test_setraw():
    master, slave = os.openpty()
    orig = termios.tcgetattr(slave)
    old = tty.setraw(slave)
    assert old == orig  # returns the original mode
    mode = termios.tcgetattr(slave)
    assert mode[tty.LFLAG] & (termios.ECHO | termios.ICANON | termios.ISIG) == 0
    assert mode[tty.IFLAG] & (termios.ICRNL | termios.IXON) == 0
    assert mode[tty.OFLAG] & termios.OPOST == 0
    assert mode[tty.CFLAG] & termios.CSIZE == termios.CS8
    assert ccval(mode[tty.CC][termios.VMIN]) == 1
    assert ccval(mode[tty.CC][termios.VTIME]) == 0

    # raw input: no line buffering or translation
    os.write(master, b'a\r')
    assert os.read(slave, 10) == b'a\r'

    termios.tcsetattr(slave, termios.TCSADRAIN, old)
    assert termios.tcgetattr(slave) == orig
    os.close(slave)
    os.close(master)


def test_setcbreak():
    master, slave = os.openpty()
    orig = termios.tcgetattr(slave)
    old = tty.setcbreak(slave, termios.TCSANOW)
    assert old == orig
    mode = termios.tcgetattr(slave)
    assert mode[tty.LFLAG] & (termios.ECHO | termios.ICANON) == 0
    assert mode[tty.LFLAG] & termios.ISIG == orig[tty.LFLAG] & termios.ISIG
    assert mode[tty.IFLAG] == orig[tty.IFLAG]
    assert ccval(mode[tty.CC][termios.VMIN]) == 1

    # no line buffering, but still CR -> NL translation (ICRNL)
    os.write(master, b'a\r')
    assert os.read(slave, 10) == b'a\n'

    termios.tcsetattr(slave, termios.TCSAFLUSH, old)
    assert termios.tcgetattr(slave) == orig
    os.close(slave)
    os.close(master)


def test_cfmakeraw():
    master, slave = os.openpty()
    mode = termios.tcgetattr(slave)
    new = copy.copy(mode)  # shares the control characters
    tty.cfmakeraw(new)
    assert new[tty.LFLAG] & termios.ICANON == 0
    assert mode[tty.LFLAG] & termios.ICANON != 0
    # cfmakeraw copies the control characters before changing them
    assert ccval(new[tty.CC][termios.VMIN]) == 1
    assert ccval(new[tty.CC][termios.VTIME]) == 0
    assert mode[tty.CC] == termios.tcgetattr(slave)[tty.CC]
    termios.tcsetattr(slave, termios.TCSANOW, new)
    assert termios.tcgetattr(slave)[tty.LFLAG] & termios.ICANON == 0
    os.close(slave)
    os.close(master)


def test_cfmakecbreak():
    master, slave = os.openpty()
    mode = termios.tcgetattr(slave)
    new = copy.deepcopy(mode)
    tty.cfmakecbreak(new)
    assert new[tty.LFLAG] & (termios.ECHO | termios.ICANON) == 0
    assert new[tty.IFLAG] == mode[tty.IFLAG]
    assert ccval(new[tty.CC][termios.VMIN]) == 1
    assert ccval(new[tty.CC][termios.VTIME]) == 0
    os.close(slave)
    os.close(master)


def test_all():
    test_indices()
    test_reexport()
    test_setraw()
    test_setcbreak()
    test_cfmakeraw()
    test_cfmakecbreak()


if __name__ == '__main__':
    test_all()
