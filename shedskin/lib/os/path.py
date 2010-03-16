import stat

curdir = ''
pardir = ''
extsep = ''
sep = ''
pathsep = ''
defpath = ''
altsep = ''
devnull = ''

def isdir(path):
    return True

def exists(path):
    return True

def lexists(path):
    return True

def islink(path):
    return True

def isfile(path):
    return True

def samefile(a, b):
    return True

def samestat(a, b):
    return True

def split(p):
    return ('','')

def splitext(p):
    return ('','')

def join(*a):
    return ''

def normcase(s):
    return s

def isabs(s):
    return True

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

def walk(top, func, arg):
    func(arg, '', [''])
