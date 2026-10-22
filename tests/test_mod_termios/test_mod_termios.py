import copy
import os
import termios
import tty
from tty import CC, LFLAG


# in non-canonical mode, CPython returns cc[VMIN] and cc[VTIME] as ints, else
# as bytes (shedskin: always bytes). this reads them in a compatible way
def ccval(v):
    try:
        return ord(v)
    except TypeError:
        return int(v)


def test_cc_index():
    # attrs[6], attrs[CC] and attrs[tty.CC] hold the control characters
    master, slave = os.openpty()
    attrs = termios.tcgetattr(slave)
    attrs[3] &= ~(termios.ECHO | termios.ICANON)
    attrs[6][termios.VMIN] = 1
    attrs[CC][termios.VTIME] = 2
    attrs[tty.CC][0] = b'\x05'
    termios.tcsetattr(slave, termios.TCSANOW, attrs)

    cur = termios.tcgetattr(slave)
    assert cur[LFLAG] & termios.ICANON == 0
    assert cur[tty.LFLAG] & termios.ECHO == 0
    assert ccval(cur[6][termios.VMIN]) == 1
    assert ccval(cur[CC][termios.VTIME]) == 2
    assert cur[tty.CC][0] == b'\x05'
    assert cur == attrs
    assert len(cur) == 7
    assert len(cur[6]) == termios.NCCS
    os.close(slave)
    os.close(master)


def test_backup_restore():
    master, slave = os.openpty()
    old = termios.tcgetattr(slave)
    new = termios.tcgetattr(slave)
    new[tty.LFLAG] &= ~termios.ECHO
    termios.tcsetattr(slave, termios.TCSANOW, new)
    assert termios.tcgetattr(slave) != old
    termios.tcsetattr(slave, termios.TCSADRAIN, old)
    assert termios.tcgetattr(slave) == old
    assert termios.tcgetattr(slave)[LFLAG] & termios.ECHO != 0
    os.close(slave)
    os.close(master)


def test_cc_bytes():
    # control characters are ordinary bytes objects
    master, slave = os.openpty()
    cc = termios.tcgetattr(slave)[CC]
    chars = [cc[0], b'x']
    for c in cc:
        chars.append(c)
    assert len(chars) == termios.NCCS + 2
    assert chars[0] == cc[0]
    assert cc[-1] == cc[termios.NCCS - 1]
    os.close(slave)
    os.close(master)


def test_cc_set():
    master, slave = os.openpty()
    attrs = termios.tcgetattr(slave)
    attrs[CC][1] = 300  # like CPython, ints are truncated
    termios.tcsetattr(slave, termios.TCSANOW, attrs)
    cc = termios.tcgetattr(slave)[CC]
    assert cc[1] == b',' and ord(cc[1]) == 44
    attrs[CC][1] = b'\x07'
    termios.tcsetattr(slave, termios.TCSANOW, attrs)
    assert termios.tcgetattr(slave)[CC][1] == b'\x07'
    # CPython raises on tcsetattr, shedskin on assignment
    try:
        attrs[CC][1] = b'ab'
        termios.tcsetattr(slave, termios.TCSANOW, attrs)
        assert False
    except TypeError:
        pass
    try:
        cc[termios.NCCS] = 1
        assert False
    except IndexError:
        pass
    os.close(slave)
    os.close(master)


def test_copy():
    master, slave = os.openpty()
    attrs = termios.tcgetattr(slave)
    attrs[6][termios.VMIN] = 3

    # a shallow copy shares the control characters
    shallow = copy.copy(attrs)
    shallow[CC][termios.VMIN] = 7
    shallow[3] = 0
    assert ccval(attrs[CC][termios.VMIN]) == 7
    assert attrs[3] != 0

    # a deep copy does not
    deep = copy.deepcopy(attrs)
    deep[CC][termios.VMIN] = 9
    assert ccval(attrs[CC][termios.VMIN]) == 7
    assert deep != attrs
    deep[CC] = attrs[CC]
    assert deep == attrs
    os.close(slave)
    os.close(master)


def test_fileno_object():
    master, slave = os.openpty()
    f = open(os.ttyname(slave), 'rb')
    assert termios.tcgetattr(f) == termios.tcgetattr(slave)
    f.close()
    os.close(slave)
    os.close(master)


class FilenoWrapper:
    def __init__(self, fd):
        self.fd = fd

    def fileno(self):
        return self.fd


def test_fileno_method():
    master, slave = os.openpty()
    assert termios.tcgetattr(FilenoWrapper(slave)) == termios.tcgetattr(slave)
    termios.tcdrain(FilenoWrapper(slave))
    os.close(slave)
    os.close(master)


def test_error():
    r, w = os.pipe()
    try:
        termios.tcgetattr(r)
        assert False
    except termios.error as e:
        assert str(e) == '(25, \'Inappropriate ioctl for device\')'
    try:
        termios.tcdrain(r)
        assert False
    except termios.error:
        pass
    os.close(r)
    os.close(w)

    try:
        termios.tcgetattr(-1)
        assert False
    except ValueError as e:
        assert str(e) == 'file descriptor cannot be a negative integer (-1)'
    try:
        termios.tcgetattr(FilenoWrapper(-2))
        assert False
    except ValueError:
        pass

    master, slave = os.openpty()
    try:
        termios.tcsetattr(slave, 99, termios.tcgetattr(slave))
        assert False
    except termios.error as e:
        assert str(e) == '(22, \'Invalid argument\')'
    os.close(slave)
    os.close(master)


def test_flush_drain_flow():
    master, slave = os.openpty()
    os.write(master, b'abc')
    termios.tcflush(slave, termios.TCIFLUSH)
    termios.tcflush(slave, termios.TCIOFLUSH)
    termios.tcdrain(slave)
    termios.tcflow(slave, termios.TCOOFF)
    termios.tcflow(slave, termios.TCOON)
    termios.tcsendbreak(slave, 0)
    os.close(slave)
    os.close(master)


def test_winsize():
    master, slave = os.openpty()
    termios.tcsetwinsize(slave, (24, 80))
    assert termios.tcgetwinsize(slave) == (24, 80)
    termios.tcsetwinsize(master, [50, 132])
    rows, cols = termios.tcgetwinsize(slave)
    assert rows == 50 and cols == 132
    try:
        termios.tcsetwinsize(slave, (1, 2, 3))
        assert False
    except TypeError as e:
        assert str(e) == 'tcsetwinsize, arg 2: must be a two-item sequence'
    try:
        termios.tcsetwinsize(slave, (70000, 80))
        assert False
    except OverflowError:
        pass
    os.close(slave)
    os.close(master)


def test_speed():
    master, slave = os.openpty()
    attrs = termios.tcgetattr(slave)
    attrs[4] = attrs[5] = termios.B115200
    termios.tcsetattr(slave, termios.TCSANOW, attrs)
    attrs = termios.tcgetattr(slave)
    assert attrs[4] == termios.B115200
    assert attrs[5] == termios.B115200
    os.close(slave)
    os.close(master)


def test_constants():
    assert termios.TCSANOW != termios.TCSADRAIN != termios.TCSAFLUSH
    assert termios.VMIN != termios.VTIME
    assert 0 <= termios.VMIN < termios.NCCS
    assert termios.ECHO & termios.ECHO == termios.ECHO
    assert termios.B9600 != termios.B38400
    assert termios.CS8 & termios.CSIZE == termios.CS8


def test_all():
    test_cc_index()
    test_backup_restore()
    test_cc_bytes()
    test_cc_set()
    test_copy()
    test_fileno_object()
    test_fileno_method()
    test_error()
    test_flush_drain_flow()
    test_winsize()
    test_speed()
    test_constants()


if __name__ == '__main__':
    test_all()
