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

O_APPEND = 0
O_CREAT = 0
O_EXCL = 0
O_RDONLY = 0
O_RDWR = 0
O_TRUNC = 0
O_WRONLY = 0

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

def execv(file, args):
    pass

def execvp(file, args):
    pass

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

