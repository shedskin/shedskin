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


def test_s_isdoor_isport_iswht():
    # doors and event ports (solaris) and whiteouts (bsd/macos) are file
    # types that linux and windows don't model. cpython still defines the
    # constants and predicates on every platform, with the predicates
    # returning False for a type the platform doesn't know about, so
    # portable code can call them unconditionally
    file_mode = stat.S_IFREG | 0o644
    assert stat.S_ISDOOR(file_mode) == False
    assert stat.S_ISPORT(file_mode) == False
    assert stat.S_ISWHT(file_mode) == False
    assert stat.S_ISREG(file_mode) == True

    # S_IFDOOR/S_IFPORT are 0 off solaris; S_IFWHT is the real whiteout
    # bit on macos and 0 elsewhere, so don't pin it to one value
    assert stat.S_IFDOOR == 0
    assert stat.S_IFPORT == 0
    assert stat.S_IFWHT == 0 or stat.S_IFWHT == 0o160000


def test_file_flags():
    # the UF_*/SF_* values come from the system headers where those
    # exist (macos) and from cpython's fixed fallbacks otherwise, so
    # check the mask relations that hold either way rather than exact
    # numbers
    assert stat.UF_NODUMP & stat.UF_SETTABLE == stat.UF_NODUMP
    assert stat.UF_IMMUTABLE & stat.UF_SETTABLE == stat.UF_IMMUTABLE
    assert stat.UF_APPEND & stat.UF_SETTABLE == stat.UF_APPEND
    assert stat.UF_OPAQUE & stat.UF_SETTABLE == stat.UF_OPAQUE
    assert stat.UF_NOUNLINK & stat.UF_SETTABLE == stat.UF_NOUNLINK
    assert stat.UF_COMPRESSED & stat.UF_SETTABLE == stat.UF_COMPRESSED
    assert stat.UF_TRACKED & stat.UF_SETTABLE == stat.UF_TRACKED
    assert stat.UF_DATAVAULT & stat.UF_SETTABLE == stat.UF_DATAVAULT
    assert stat.UF_HIDDEN & stat.UF_SETTABLE == stat.UF_HIDDEN

    # SF_DATALESS is deliberately left out: it sits outside SF_SETTABLE
    # on macos, where cpython narrows the mask to 0x3fff0000
    assert stat.SF_ARCHIVED & stat.SF_SETTABLE == stat.SF_ARCHIVED
    assert stat.SF_IMMUTABLE & stat.SF_SETTABLE == stat.SF_IMMUTABLE
    assert stat.SF_APPEND & stat.SF_SETTABLE == stat.SF_APPEND
    assert stat.SF_RESTRICTED & stat.SF_SETTABLE == stat.SF_RESTRICTED
    assert stat.SF_NOUNLINK & stat.SF_SETTABLE == stat.SF_NOUNLINK
    assert stat.SF_SNAPSHOT & stat.SF_SETTABLE == stat.SF_SNAPSHOT
    assert stat.SF_FIRMLINK & stat.SF_SETTABLE == stat.SF_FIRMLINK

    # owner-settable and superuser-settable flags never overlap
    assert stat.UF_SETTABLE & stat.SF_SETTABLE == 0

    # each flag is a distinct single bit
    flags = [stat.UF_NODUMP, stat.UF_IMMUTABLE, stat.UF_APPEND,
             stat.UF_OPAQUE, stat.UF_NOUNLINK, stat.UF_COMPRESSED,
             stat.UF_TRACKED, stat.UF_DATAVAULT, stat.UF_HIDDEN,
             stat.SF_ARCHIVED, stat.SF_IMMUTABLE, stat.SF_APPEND,
             stat.SF_RESTRICTED, stat.SF_NOUNLINK, stat.SF_SNAPSHOT,
             stat.SF_FIRMLINK, stat.SF_DATALESS]
    assert len(set(flags)) == len(flags)
    for flag in flags:
        assert flag > 0
        assert flag & (flag - 1) == 0


def test_file_attributes():
    # st_file_attributes bits; these are fixed win32 values that cpython
    # hardcodes identically on every platform
    assert stat.FILE_ATTRIBUTE_READONLY == 1
    assert stat.FILE_ATTRIBUTE_HIDDEN == 2
    assert stat.FILE_ATTRIBUTE_SYSTEM == 4
    assert stat.FILE_ATTRIBUTE_DIRECTORY == 16
    assert stat.FILE_ATTRIBUTE_ARCHIVE == 32
    assert stat.FILE_ATTRIBUTE_DEVICE == 64
    assert stat.FILE_ATTRIBUTE_NORMAL == 128
    assert stat.FILE_ATTRIBUTE_TEMPORARY == 256
    assert stat.FILE_ATTRIBUTE_SPARSE_FILE == 512
    assert stat.FILE_ATTRIBUTE_REPARSE_POINT == 1024
    assert stat.FILE_ATTRIBUTE_COMPRESSED == 2048
    assert stat.FILE_ATTRIBUTE_OFFLINE == 4096
    assert stat.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED == 8192
    assert stat.FILE_ATTRIBUTE_ENCRYPTED == 16384
    assert stat.FILE_ATTRIBUTE_INTEGRITY_STREAM == 32768
    assert stat.FILE_ATTRIBUTE_VIRTUAL == 65536
    assert stat.FILE_ATTRIBUTE_NO_SCRUB_DATA == 131072


def test_statx_attributes():
    # stx_attributes bits, also fixed values in cpython's stat.py
    assert stat.STATX_ATTR_COMPRESSED == 0x00000004
    assert stat.STATX_ATTR_IMMUTABLE == 0x00000010
    assert stat.STATX_ATTR_APPEND == 0x00000020
    assert stat.STATX_ATTR_NODUMP == 0x00000040
    assert stat.STATX_ATTR_ENCRYPTED == 0x00000800
    assert stat.STATX_ATTR_AUTOMOUNT == 0x00001000
    assert stat.STATX_ATTR_MOUNT_ROOT == 0x00002000
    assert stat.STATX_ATTR_VERITY == 0x00100000
    assert stat.STATX_ATTR_DAX == 0x00200000
    assert stat.STATX_ATTR_WRITE_ATOMIC == 0x00400000


def test_filemode():
    assert stat.filemode(stat.S_IFREG | 0o644) == '-rw-r--r--'
    assert stat.filemode(stat.S_IFDIR | 0o755) == 'drwxr-xr-x'
    assert stat.filemode(stat.S_IFLNK | 0o777) == 'lrwxrwxrwx'
    assert stat.filemode(stat.S_IFREG | 0o4755) == '-rwsr-xr-x'
    assert stat.filemode(stat.S_IFDIR | 0o1777) == 'drwxrwxrwt'


def test_all():
    test_s_isdir()
    test_s_isreg()
    test_s_islnk()
    test_s_isfifo()
    test_s_ischr()
    test_s_isblk()
    test_s_issock()
    test_combine_with_bool_logic()
    test_s_isdoor_isport_iswht()
    test_file_flags()
    test_file_attributes()
    test_statx_attributes()
    test_filemode()


test_all()
