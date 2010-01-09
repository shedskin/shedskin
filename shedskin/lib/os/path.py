import stat

curdir = ''
pardir = ''
extsep = ''
sep = ''
pathsep = ''
defpath = ''
altsep = ''
devnull = ''

def split(p):
    return ('','')

def splitext(p):
    return ('','')

def isdir(path):
    return False

def exists(path):
    return False

def lexists(path):
    return False

def islink(path):
    return False

def isfile(path):
    return False

def join(*a):
    return ''

def normcase(s):
    return s

def isabs(s):
    return 1

def splitdrive(s):
    return ('', '')

def basename(s):
    return s

def dirname(s):
    return s

def commonprefix(s):
    return ''

def abspath(s):
    return ''

def realpath(s):
    return ''

def normpath(s):
    return ''

def getsize(s):
    return 1
def getatime(s):
    return 1.0
def getmtime(s):
    return 1.0
def getctime(s):
    return 1.0
def samefile(a, b):
    return 1
def samestat(a, b):
    return 1

def walk(top, func, arg):
    func(arg, '', [''])


