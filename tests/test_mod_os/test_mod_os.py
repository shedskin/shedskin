# popen deprecated in favor of subprocess.. consider subprocess support?

import os

def test_getcwd():
    assert len(os.getcwd()) > 1


def test_chdir():
    os.chdir('.')


def test_exceptions():
    try:
        os.chdir("ontehunoe")
    except FileNotFoundError as e:
        assert e.errno == 2
        assert e.filename == "ontehunoe"


def test_listdir():
    assert len(os.listdir()) > 0


# following currently only tested under posix

def test_env():
    os.environ['bert'] = 'value'
#    assert os.getenv('bert') == 'value'  # TODO

    os.putenv('bert', 'value2') # does not change os.environ


def test_makedirs_exist_ok():
    path = '/tmp/shedskin_test_makedirs_exist_ok/a/b'

    os.makedirs(path, exist_ok=True)
    assert os.path.isdir(path)

    # calling again without exist_ok must raise
    try:
        os.makedirs(path)
        assert False
    except OSError as e:
        assert e.errno == 17  # EEXIST

    # calling again with exist_ok=True must be a no-op, not raise
    os.makedirs(path, exist_ok=True)
    assert os.path.isdir(path)

    os.removedirs(path)


def test_setgroups_overflow():
    # Regression test: os.setgroups used to fill a fixed-size 4096-slot
    # gid_t stack buffer without checking the input length first, so
    # passing more groups than that overflowed the stack. 4096 (MAXENTRIES)
    # is shedskin's own internal buffer limit -- the same cap os.getgroups
    # already uses -- not the real kernel NGROUPS_MAX, which is typically
    # much larger (e.g. 65536 on Linux) and not itself the thing under
    # test here. This must raise before touching the buffer, not crash
    # or corrupt memory, regardless of the caller's privileges.
    too_many = [0] * (4096 + 1)
    try:
        os.setgroups(too_many)
        assert False, "expected ValueError"
    except ValueError as e:
        assert str(e) == "too many groups"


def test_urandom():
    bts = os.urandom(10)
    assert len(bts) == 10
    assert bts.__class__.__name__ == 'bytes'


def test_posix():
    assert os.curdir == '.'
    assert os.pardir == '..'
    assert os.sep == '/'
    assert os.altsep is None
    assert os.extsep == '.'
    assert os.pathsep == ':'
    assert os.defpath == '/bin:/usr/bin'
    assert os.linesep == '\n'
    assert os.devnull == '/dev/null'


def test_rdwr():
    fd = os.open('/dev/null', os.O_RDWR)
    assert os.write(fd, b'blah') == 4
    assert os.read(fd, 10) == b''
    os.close(fd)


def test_isatty():
    fd = os.open('/dev/null', os.O_RDONLY)
    assert os.isatty(fd) == False
    os.close(fd)


def test_system():
    assert os.system('ls') == 0


def test_all():
    test_getcwd()
    test_chdir()
    test_exceptions()
    test_listdir()

    test_makedirs_exist_ok()

    if os.name == 'posix':  # TODO 'nt'
        test_posix()
        test_env()
        test_rdwr()
        test_isatty()
        test_system()
        test_urandom()
        # test_setgroups_overflow()  # os.setgroups is #ifndef WIN32'd out of
        # __os__ in lib/os/__init__.hpp, and shedskin translates this
        # function's body to C++ unconditionally (the `os.name == 'posix'`
        # check above is a runtime guard, not a compile-time one), so calling
        # it here breaks the Windows build even though it never runs there.


if __name__ == '__main__':
    test_all()
