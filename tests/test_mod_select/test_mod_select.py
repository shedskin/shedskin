import os
import select


def test_select_basic():
    r, w = os.pipe()
    os.write(w, b"hi")
    rl, wl, xl = select.select([r], [], [], 1.0)
    assert rl == [r]
    assert wl == []
    assert xl == []
    os.close(r)
    os.close(w)


def test_select_timeout_no_ready_fds():
    r, w = os.pipe()
    # nothing written, so r is not readable; should time out
    # quickly instead of blocking, and report nothing ready
    rl, wl, xl = select.select([r], [], [], 0.05)
    assert rl == []
    assert wl == []
    assert xl == []
    os.close(r)
    os.close(w)


def test_select_negative_fd_raises():
    # matches cpython: select.select() raises ValueError for a
    # negative file descriptor instead of silently ignoring it
    ok = False
    try:
        select.select([-5], [], [], 0.05)
    except ValueError:
        ok = True
    assert ok


def test_select_fd_out_of_range_raises():
    # matches cpython: select.select() raises ValueError for a file
    # descriptor >= FD_SETSIZE instead of writing past the end of the
    # underlying fd_set (this used to silently corrupt the stack and
    # could report a never-opened fd as "ready")
    ok = False
    try:
        select.select([2000], [], [], 0.05)
    except ValueError:
        ok = True
    assert ok


def test_select_negative_timeout_raises():
    # matches cpython: select.select() raises ValueError for a
    # negative timeout instead of silently blocking forever
    r, w = os.pipe()
    ok = False
    try:
        select.select([r], [], [], -5.0)
    except ValueError:
        ok = True
    os.close(r)
    os.close(w)
    assert ok


def test_select_explicit_negative_one_raises():
    # -1.0 used to double as the "no timeout given" sentinel, which let
    # this slip through and block forever; an explicit -1.0 must raise
    # ValueError just like any other negative timeout
    r, w = os.pipe()
    ok = False
    try:
        select.select([r], [], [], -1.0)
    except ValueError:
        ok = True
    os.close(r)
    os.close(w)
    assert ok


def test_select_omitted_timeout_still_works():
    # omitting timeout entirely must still behave correctly (here,
    # returning immediately since data is already ready) rather than
    # being confused with an explicit negative value
    r, w = os.pipe()
    os.write(w, b"hi")
    rl, wl, xl = select.select([r], [], [])
    assert rl == [r]
    os.close(r)
    os.close(w)


def test_all():
    test_select_basic()
    test_select_timeout_no_ready_fds()
    test_select_negative_fd_raises()
    test_select_fd_out_of_range_raises()
    test_select_negative_timeout_raises()
    test_select_explicit_negative_one_raises()
    test_select_omitted_timeout_still_works()


if __name__ == '__main__':
    test_all()
