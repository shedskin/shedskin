# Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE)

import path

name = ''

linesep = ''
environ = {'': ''}

curdir = ''
pardir = ''
extsep = ''
sep = ''
pathsep = ''
defpath = ''
altsep = ''
devnull = ''

EX_CANTCREAT = 0
EX_CONFIG = 0
EX_DATAERR = 0
EX_IOERR = 0
EX_NOHOST = 0
EX_NOINPUT = 0
EX_NOPERM = 0
EX_NOUSER = 0
EX_OK = 0
EX_OSERR = 0
EX_OSFILE = 0
EX_PROTOCOL = 0
EX_SOFTWARE = 0
EX_TEMPFAIL = 0
EX_UNAVAILABLE = 0
EX_USAGE = 0
F_OK = 0
NGROUPS_MAX = 0
O_APPEND = 0
O_BINARY = 0  # (windows only)
O_CREAT = 0
O_DIRECT = 0
O_DIRECTORY = 0
O_DSYNC = 0
O_EXCL = 0
O_LARGEFILE = 0
O_NDELAY = 0
O_NOCTTY = 0
O_NOFOLLOW = 0
O_NONBLOCK = 0
O_RDONLY = 0
O_RDWR = 0
O_RSYNC = 0
O_SYNC = 0
O_TEXT = 0  # (windows only)
O_TRUNC = 0
O_WRONLY = 0
P_NOWAIT = 0
P_NOWAITO = 0
P_WAIT = 0
R_OK = 0
SEEK_CUR = 0
SEEK_END = 0
SEEK_DATA = 0
SEEK_HOLE = 0
SEEK_SET = 0
TMP_MAX = 0
WCONTINUED = 0
WNOHANG = 0
WUNTRACED = 0
W_OK = 0
X_OK = 0

__void = 0  # 'argument not given' sentinel (e.g. tuple-style index(x, start, stop))

pathconf_names = {'': 1}
sysconf_names = {'': 1}
confstr_names = {'': 1}

class error(OSError):
    pass

# struct sequences: subclasses of tuple, with the items also as attributes.
# (__slice__/__mul__: the tuple versions return self, so a subclass)
class stat_result(tuple):
    def __init__(self):
        self.unit = 1
        self.st_mode = 1
        self.st_size = 1
        self.st_ino = 1
        self.st_dev = 1
        self.st_rdev = 1
        self.st_nlink = 1
        self.st_mtime = 1.0
        self.st_atime = 1.0
        self.st_ctime = 1.0
        self.st_atime_ns = 1
        self.st_mtime_ns = 1
        self.st_ctime_ns = 1
        self.st_uid = 1
        self.st_gid = 1

        self.st_blksize = 1
        self.st_blocks = 1
    def __slice__(self, x, l, u, s):
        return (self.unit,)
    def __mul__(self, n):
        return (self.unit,)
    def __repr__(self):
        return ''

class statvfs_result(tuple):
    def __init__(self):
        self.unit = 1
        self.f_bsize = 1
        self.f_frsize = 1
        self.f_blocks = 1
        self.f_bfree = 1
        self.f_bavail = 1
        self.f_files = 1
        self.f_ffree = 1
        self.f_favail = 1
        self.f_flag = 1
        self.f_namemax = 1
        self.f_fsid = 1
    def __slice__(self, x, l, u, s):
        return (self.unit,)
    def __mul__(self, n):
        return (self.unit,)
    def __repr__(self):
        return ''

def statvfs(path):
    return statvfs_result()

def fstatvfs(fd):
    return statvfs_result()

class popen_pipe(file):
    def close(self):
        return 0

def listdir(path=None):
    return [path.__or_x__('')]

class DirEntry:
    def __init__(self):
        self.name = ''
        self.path = ''
    def is_dir(self, follow_symlinks=True):
        return True
    def is_file(self, follow_symlinks=True):
        return True
    def is_symlink(self):
        return True
    def is_junction(self):
        return True
    def inode(self):
        return 1
    def stat(self, follow_symlinks=True):
        return stat_result()
    def __repr__(self):
        return ''
    def __fspath__(self):
        return self.path

class ScandirIterator:
    def __iter__(self):
        return self
    def __next__(self):
        return DirEntry()
    def __enter__(self):
        return self
    def __exit__(self):
        pass
    def close(self):
        pass
    def __repr__(self):
        return ''

def scandir(path=None):
    return ScandirIterator()

def walk(top, topdown=True, onerror=None, followlinks=False):
    onerror(OSError())
    return __iter((top, [top], [top]))

def getenv(key, default=None):
    return ''

def get_exec_path(env=None):
    return ['']

def getcwd():
    return ''

def getcwdb():
    return b''

def fsencode(filename):
    return b''

def fsdecode(filename):
    return ''

def getlogin():
    return ''

def chdir(path):
    pass

def rename(src, dst, __kw_src_dir_fd=None, __kw_dst_dir_fd=None):
    pass

def replace(src, dst, __kw_src_dir_fd=None, __kw_dst_dir_fd=None):
    pass

def cpu_count():
    return 1

def process_cpu_count():
    return 1

def fspath(path):
    return path.__fspath__()

def remove(path, __kw_dir_fd=None):
    pass

def rmdir(path, __kw_dir_fd=None):
    pass

def removedirs(name):
    pass

def mkdir(path, mode=0o0777, __kw_dir_fd=None):
    pass

def makedirs(name, mode=0o0777, exist_ok=False, parent_mode=-1):
    pass

def fork():
    return 1

def forkpty():
    return (1,)

def openpty():
    return (1,)

def abort():
    pass

def chown(path, uid, gid, __kw_dir_fd=None, __kw_follow_symlinks=True):
    pass

def system(command):
    return 1

def strerror(code):
    return ''

def stat(path, __kw_dir_fd=None, __kw_follow_symlinks=True):
    return stat_result()

def lstat(path, __kw_dir_fd=None):
    return stat_result()

def fstat(fd):
    return stat_result()

def readlink(path, __kw_dir_fd=None):
    return ''

def getuid():
    return 1

def setuid(uid):
    pass

def getgid():
    return 1

def setgid(gid):
    pass

def getegid():
    return 1

def setegid(egid):
    pass

def geteuid():
    return 1

def seteuid(euid):
    pass

def getgroups():
    return [1]

def setgroups(groups):
    pass

def getpgid(pid):
    return 1

def setpgid(pid, pgrp):
    pass

def getpgrp():
    return 1

def setpgrp():
    pass

def getppid():
    return 1

def getsid(pid):
    return 1

def setsid():
    pass

def getpid():
    return 1

def setreuid(ruid, euid):
    pass

def setregid(rgid, egid):
    pass

def tcgetpgrp(fd):
    return 1

def tcsetpgrp(fd, pgid):
    pass

def putenv(name, value):
    pass

def umask(mask):
    return 0

def chmod(path, mode, __kw_dir_fd=None, __kw_follow_symlinks=True):
    pass

def fchmod(fd, mode):
    pass

def unsetenv(name):
    pass

def renames(old, new):
    pass

def popen(cmd, mode=None, buffering=-1):
    return popen_pipe('')

def close(fd):
    pass

def execl(*path):
    pass
def execlp(*path):
    pass
def execle(*path):
    pass
def execlpe(*path):
    pass

def execv(path, argv):
    pass
def execvp(file, args):
    pass
def execve(path, argv, env):
    pass
def execvpe(file, args, env):
    pass

def spawnl(mode, *path):
    return 1
def spawnlp(mode, *path):
    return 1
def spawnle(mode, *path):
    return 1
def spawnlpe(mode, *path):
    return 1

def spawnv(mode, file, args):
    return 1
def spawnvp(mode, file, args):
    return 1
def spawnve(mode, file, args, env):
    return 1
def spawnvpe(mode, file, args, env):
    return 1

def open(path, flags, mode=0o777, __kw_dir_fd=None):
    return 1

def read(fd, length):
    return b''

def write(fd, data):
    return 1

def readinto(fd, buffer):
    return 1

def reload_environ():
    pass

def fdopen(fd, mode=None, buffering=-1, encoding=None, errors=None, newline=None, closefd=1):
    return file('/bin/sh')

def fdopen_binary(fd, mode=None, buffering=-1, encoding=None, errors=None, newline=None, closefd=1):  # fdopen(fd, 'rb'), see graph.py
    return file_binary('/bin/sh')

def pipe():
    return (0,0)

def dup(fd):
    return 1

def dup2(fd, fd2, inheritable=True):
    return 1

def fchdir(fd):
    pass

def fdatasync(fd):
    pass

def chroot(path):
    pass

def ctermid():
    return ''

def isatty(fd):
    return True

def ttyname(fd):
    return ''

class uname_result(tuple):
    def __init__(self, t):
        self.unit = ''
        self.sysname = ''
        self.nodename = ''
        self.release = ''
        self.version = ''
        self.machine = ''
    def __slice__(self, x, l, u, s):
        return (self.unit,)
    def __mul__(self, n):
        return (self.unit,)
    def __repr__(self):
        return ''

def uname():
    return uname_result(('',))

def lchown(path, uid, gid):
    pass

def link(src, dst, __kw_src_dir_fd=None, __kw_dst_dir_fd=None, __kw_follow_symlinks=True):
    pass

def symlink(src, dst, target_is_directory=False, __kw_dir_fd=None):
    pass

def nice(increment):
    return 1

def wait():
    return (1,)

def waitpid(pid, options):
    return (1,)

def kill(pid, signal):
    pass

def killpg(pgid, signal):
    pass

def pathconf(path, name):
    return 1

def fpathconf(fd, name):
    return 1

def confstr(name):
    return ''

def sysconf(name):
    return 1

def ftruncate(fd, length):
    pass

def truncate(path, length):
    pass

def closerange(fd_low, fd_high):
    pass

def waitstatus_to_exitcode(status):
    return 1

def get_inheritable(fd):
    return True

def set_inheritable(fd, inheritable):
    pass

def get_blocking(fd):
    return True

def set_blocking(fd, blocking):
    pass

def device_encoding(fd):
    return ''

class terminal_size(tuple):
    def __init__(self, t):
        self.unit = 1
        self.columns = 1
        self.lines = 1
    def __slice__(self, x, l, u, s):
        return (self.unit,)
    def __mul__(self, n):
        return (self.unit,)
    def __repr__(self):
        return ''

def get_terminal_size(fd=1):
    return terminal_size((1, 1))

def getloadavg():
    return (1.0,)

def mkfifo(path, mode=438, __kw_dir_fd=None):
    pass

def unlink(path, __kw_dir_fd=None):
    pass

def lseek(fd, position, whence):
    return 1

def fsync(fd):
    pass

def urandom(size):
    return b''

def getrandom(size, flags=0):
    return b''

def utime(path, times=None, __kw_ns=None, __kw_dir_fd=None, __kw_follow_symlinks=True):
    pass

def access(path, mode, __kw_dir_fd=None, __kw_effective_ids=False, __kw_follow_symlinks=True):
    return True

class times_result(tuple):
    def __init__(self, t):
        self.unit = 1.0
        self.user = 1.0
        self.system = 1.0
        self.children_user = 1.0
        self.children_system = 1.0
        self.elapsed = 1.0
    def __slice__(self, x, l, u, s):
        return (self.unit,)
    def __mul__(self, n):
        return (self.unit,)
    def __repr__(self):
        return ''

def times():
    return times_result((1.0,))

def makedev(major, minor):
    return 1

def major(device):
    return 1

def minor(device):
    return 1

def mknod(path, mode=0o600, device=0, __kw_dir_fd=None):
    pass

def WCOREDUMP(status):
    return True
def WEXITSTATUS(status):
    return 1
def WIFCONTINUED(status):
    return True
def WIFEXITED(status):
    return True
def WIFSIGNALED(status):
    return True
def WIFSTOPPED(status):
    return True
def WSTOPSIG(status):
    return 1
def WTERMSIG(status):
    return 1

def _exit(status):
    pass
