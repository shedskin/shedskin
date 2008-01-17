import os.path

name = ''

linesep = ''
environ = {'':''}

curdir = ''
pardir = ''
extsep = ''
sep = ''
pathsep = ''
defpath = ''
altsep = ''
devnull = ''

def listdir(path):
    return ['']

def getenv(name, alternative=''):
    return ''

def getcwd():
    return ''

def chdir(d):
    pass

def rename(a, b):
    pass

def remove(path):
    pass

def unlink(path):
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

def abort():
    pass

def chown(path, uid, gid):
    pass

def system(c):
    return 1

def strerror(i):
    return ''

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

def getgid():
    return 1

def stat_float_times(n=False): 
    return True

class error(OSError): 
    pass

