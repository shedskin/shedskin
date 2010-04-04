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
O_TRUNC = 0
O_WRONLY = 0
P_NOWAIT = 0
P_NOWAITO = 0
P_WAIT = 0
R_OK = 0
SEEK_CUR = 0
SEEK_END = 0
SEEK_SET = 0
TMP_MAX = 0
WCONTINUED = 0
WNOHANG = 0
WUNTRACED = 0
W_OK = 0
X_OK = 0

pathconf_names = {'': 1}
sysconf_names = {'': 1}
confstr_names = {'': 1}

class error(OSError):
    pass

class __cstat:
    def __init__(self):
        self.st_mode = 1
        self.st_size = 1
        self.st_ino = 1
        self.st_dev = 1
        self.st_rdev = 1
        self.st_nlink = 1
        self.st_mtime = 1
        self.st_atime = 1
        self.st_ctime = 1
        self.st_uid = 1
        self.st_gid = 1

        self.st_blksize = 1
        self.st_blocks = 1
    def __len__(self):
        return 1
    def __getitem__(self, i):
        return 1
    def __slice__(self, x, l, u, s):
        return (1,)
    def __repr__(self):
        return ''

class __vfsstat:
    def __init__(self):
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

    def __len__(self):
        return 1
    def __getitem__(self, i):
        return 1
    def __slice__(self, x, l, u, s):
        return (1,)
    def __repr__(self):
        return ''

def statvfs(path):
    return __vfsstat()

def fstatvfs(fd):
    return __vfsstat()

class popen_pipe(file):
    pass

def listdir(path):
    return ['']

def getenv(name, alternative=''):
    return ''

def getcwd():
    return ''

def getlogin():
    return ''

def chdir(d):
    pass

def rename(a, b):
    pass

def remove(path):
    pass

def rmdir(a):
    pass

def removedirs(name):
    pass

def mkdir(a, mode=0777):
    pass

def makedirs(name, mode=0777):
    pass

def fork():
    return 1

def forkpty():
    return (1,)

def openpty():
    return (1,)

def abort():
    pass

def chown(path, uid, gid):
    pass

def system(c):
    return 1

def strerror(i):
    return ''

def stat(path):
    return __cstat()

def lstat(path):
    return __cstat()

def fstat(file):
    return __cstat()

def readlink(path):
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
    return 1

def getpid():
    return 1

def setreuid(ruid, euid):
    pass

def setregid(guid, egid):
    pass

def tcgetpgrp(fd):
    return 1

def tcsetpgrp(fd, pg):
    pass

def stat_float_times(n=False):
    return True

def putenv(variable, value):
    pass

def umask(newmask):
    return 0

def chmod(path, val):
    return 0

def unsetenv(var):
    pass

def renames(old, new):
    pass

def popen(cmd, mode='r', bufsize=-1):
    return popen_pipe()

def popen2(cmd, mode='r', bufsize=-1):
    return ( file('/bin/sh'), file('/bin/sh') )

def popen3(cmd, mode='r', bufsize=-1):
    return ( file('/bin/sh'), file('/bin/sh'), file('/bin/sh') )

def popen4(cmd, mode='r', bufsize=-1):
    return ( file('/bin/sh'), file('/bin/sh') )

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

def execv(path, args):
    pass
def execvp(path, args):
    pass
def execve(path, args, env):
    pass
def execvpe(path, args, env):
    pass

def spawnl(mode, *path):
    return 1
def spawnlp(mode, *path):
    return 1
def spawnle(mode, *path):
    return 1
def spawnlpe(mode, *path):
    return 1

def spawnv(mode, path, args):
    return 1
def spawnvp(mode, path, args):
    return 1
def spawnve(mode, path, args, env):
    return 1
def spawnvpe(mode, path, args, env):
    return 1

def open(name, flags):
    return 1

def read(fd, n):
    return ''

def write(fd, s):
    return 1

def fdopen(fd, mode='r', bufsize=-1):
    return file('/bin/sh')

def pipe():
    return (0,0)

def dup(f1):
    return 1

def dup2(f1,f2):
    pass

def fchdir(f1):
    pass

def fdatasync(f1):
    pass

def chroot(dir):
    pass

def ctermid():
    return ''

def isatty(fd):
    return True

def ttyname(fd):
    return ''

def uname():
    return ('',)

def lchown(p, u, g):
    pass

def link(a, b):
    pass

def symlink(a, b):
    pass

def nice(n):
    return 1

def wait():
    return (1,)

def waitpid(pid, options):
    return (1,)

def kill(pid, sig):
    pass

def killpg(pgid, sig):
    pass

def pathconf(path, name):
    return 1

def fpathconf(fd, name):
    return 1

def confstr(name):
    return ''

def sysconf(name):
    return 1

def ftruncate(fd, n):
    pass

def getloadavg():
    return (1.0,)

def mkfifo(path, mode=438):
    pass

def unlink(path):
    pass

def lseek(fd, pos, how):
    pass

def fsync(fd):
    pass

def urandom(n):
    return ''

def utime(path, times):
    pass

def access(path, mode):
    return True

def times():
    return (1.0,)

def tmpnam():
    return ''

def tempnam(dir, prefix=None):
    return ''

def tmpfile():
    return file()

def makedev(major, minor):
    return 1

def major(dev):
    return 1

def minor(dev):
    return 1

def mknod(filename, mode=438, device=0):
    pass

def WCOREDUMP(status):
    return 1
def WEXITSTATUS(status):
    return 1
def WIFCONTINUED(status):
    return 1
def WIFEXITED(status):
    return 1
def WIFSIGNALED(status):
    return 1
def WIFSTOPPED(status):
    return 1
def WSTOPSIG(status):
    return 1
def WTERMSIG(status):
    return 1

def _exit(code):
    pass
