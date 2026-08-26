import stat


def test_s_isdir():
    dir_mode = stat.S_IFDIR | 0o755
    file_mode = stat.S_IFREG | 0o644
    assert stat.S_ISDIR(dir_mode) == True
    assert stat.S_ISDIR(file_mode) == False


def test_s_isreg():
    dir_mode = stat.S_IFDIR | 0o755
    file_mode = stat.S_IFREG | 0o644
    assert stat.S_ISREG(file_mode) == True
    assert stat.S_ISREG(dir_mode) == False


def test_s_islnk():
    link_mode = stat.S_IFLNK | 0o777
    file_mode = stat.S_IFREG | 0o644
    assert stat.S_ISLNK(link_mode) == True
    assert stat.S_ISLNK(file_mode) == False


def test_s_isfifo():
    fifo_mode = stat.S_IFIFO | 0o644
    file_mode = stat.S_IFREG | 0o644
    assert stat.S_ISFIFO(fifo_mode) == True
    assert stat.S_ISFIFO(file_mode) == False


def test_s_ischr():
    chr_mode = stat.S_IFCHR | 0o644
    file_mode = stat.S_IFREG | 0o644
    assert stat.S_ISCHR(chr_mode) == True
    assert stat.S_ISCHR(file_mode) == False


def test_s_isblk():
    blk_mode = stat.S_IFBLK | 0o644
    file_mode = stat.S_IFREG | 0o644
    assert stat.S_ISBLK(blk_mode) == True
    assert stat.S_ISBLK(file_mode) == False


def test_s_issock():
    sock_mode = stat.S_IFSOCK | 0o644
    file_mode = stat.S_IFREG | 0o644
    assert stat.S_ISSOCK(sock_mode) == True
    assert stat.S_ISSOCK(file_mode) == False


def test_combine_with_bool_logic():
    # combining S_ISDIR with 'and'/'or' exercises its use as an actual
    # bool rather than an int (regression: used to be typed __ss_int
    # in the hand-written C++ backend, mismatching the bool-returning
    # Python stub, which broke compilation of code like this)
    mode = stat.S_IFDIR | 0o755
    result = stat.S_ISDIR(mode) and not stat.S_ISREG(mode)
    assert result == True


def test_all():
    test_s_isdir()
    test_s_isreg()
    test_s_islnk()
    test_s_isfifo()
    test_s_ischr()
    test_s_isblk()
    test_s_issock()
    test_combine_with_bool_logic()


test_all()
