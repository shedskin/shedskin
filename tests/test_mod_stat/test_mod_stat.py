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


def test_stat_indices():
    # indices into the tuple returned by os.stat(), fixed by cpython
    assert stat.ST_MODE == 0
    assert stat.ST_INO == 1
    assert stat.ST_DEV == 2
    assert stat.ST_NLINK == 3
    assert stat.ST_UID == 4
    assert stat.ST_GID == 5
    assert stat.ST_SIZE == 6
    assert stat.ST_ATIME == 7
    assert stat.ST_MTIME == 8
    assert stat.ST_CTIME == 9


def test_file_type_constants():
    # the S_IF* values are the same on every platform cpython runs on
    assert stat.S_IFDIR == 0o040000
    assert stat.S_IFCHR == 0o020000
    assert stat.S_IFBLK == 0o060000
    assert stat.S_IFREG == 0o100000
    assert stat.S_IFIFO == 0o010000
    assert stat.S_IFLNK == 0o120000
    assert stat.S_IFSOCK == 0o140000

    # all distinct, and all covered by the file type mask
    types = [stat.S_IFDIR, stat.S_IFCHR, stat.S_IFBLK, stat.S_IFREG,
             stat.S_IFIFO, stat.S_IFLNK, stat.S_IFSOCK]
    assert len(set(types)) == len(types)
    for t in types:
        assert t & 0o170000 == t
        assert stat.S_IFMT(t) == t
        assert stat.S_IMODE(t) == 0


def test_permission_constants():
    assert stat.S_ISUID == 0o4000
    assert stat.S_ISGID == 0o2000
    assert stat.S_ENFMT == 0o2000
    assert stat.S_ISVTX == 0o1000
    assert stat.S_IREAD == 0o0400
    assert stat.S_IWRITE == 0o0200
    assert stat.S_IEXEC == 0o0100
    assert stat.S_IRWXU == 0o0700
    assert stat.S_IRUSR == 0o0400
    assert stat.S_IWUSR == 0o0200
    assert stat.S_IXUSR == 0o0100
    assert stat.S_IRWXG == 0o0070
    assert stat.S_IRGRP == 0o0040
    assert stat.S_IWGRP == 0o0020
    assert stat.S_IXGRP == 0o0010
    assert stat.S_IRWXO == 0o0007
    assert stat.S_IROTH == 0o0004
    assert stat.S_IWOTH == 0o0002
    assert stat.S_IXOTH == 0o0001

    # the legacy names alias the owner bits, and S_ENFMT the setgid bit
    assert stat.S_IREAD == stat.S_IRUSR
    assert stat.S_IWRITE == stat.S_IWUSR
    assert stat.S_IEXEC == stat.S_IXUSR
    assert stat.S_ENFMT == stat.S_ISGID

    # the rwx masks are the union of their bits
    assert stat.S_IRWXU == stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
    assert stat.S_IRWXG == stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
    assert stat.S_IRWXO == stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
    assert stat.S_IRWXU & stat.S_IRWXG == 0
    assert stat.S_IRWXG & stat.S_IRWXO == 0

    # each permission bit is a single, distinct bit
    bits = [stat.S_ISUID, stat.S_ISGID, stat.S_ISVTX,
            stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR,
            stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP,
            stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH]
    assert len(set(bits)) == len(bits)
    total = 0
    for bit in bits:
        assert bit > 0
        assert bit & (bit - 1) == 0
        total |= bit
    assert total == 0o7777


def test_s_imode_s_ifmt():
    mode = stat.S_IFREG | stat.S_ISUID | stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH
    assert stat.S_IFMT(mode) == stat.S_IFREG
    assert stat.S_IMODE(mode) == 0o4744
    assert stat.S_IFMT(mode) | stat.S_IMODE(mode) == mode

    # S_IMODE strips the type bits, S_IFMT strips the permission bits
    assert stat.S_IMODE(stat.S_IFDIR | 0o1777) == 0o1777
    assert stat.S_IFMT(stat.S_IFDIR | 0o1777) == stat.S_IFDIR
    assert stat.S_IMODE(0) == 0
    assert stat.S_IFMT(0) == 0

    # the predicates agree with the mask
    assert stat.S_ISREG(mode) == (stat.S_IFMT(mode) == stat.S_IFREG)
    assert stat.S_ISDIR(mode) == (stat.S_IFMT(mode) == stat.S_IFDIR)


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
    test_stat_indices()
    test_file_type_constants()
    test_permission_constants()
    test_s_imode_s_ifmt()


test_all()
