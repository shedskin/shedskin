# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

import stat

curdir = ''
pardir = ''
extsep = ''
sep = ''
pathsep = ''
defpath = ''
altsep = ''
devnull = ''

# special value for the 'strict' argument of realpath(): missing path
# components are tolerated, other errors are not. CPython models this as a
# singleton object with a true boolean value; shed skin models it as a bool
# with a value distinct from True/False (see ALLOW_MISSING in path.cpp).
ALLOW_MISSING = True

# special value for the 'strict' argument of realpath(): the last path
# component may be missing, all other errors are raised (see path.cpp).
ALL_BUT_LAST = True

# True if arbitrary Unicode strings can be used as file names (within
# limitations imposed by the file system).
supports_unicode_filenames = False

def isdir(s):
    return True

def exists(path):
    return True

def lexists(path):
    return True

def islink(path):
    return True

def isfile(path):
    return True

def isjunction(path):
    return True

def samefile(f1, f2):
    return True

def samestat(s1, s2):
    return True

def sameopenfile(fp1, fp2):
    return True

def isdevdrive(path):
    return True

def ismount(path):
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

def splitdrive(p):
    return ('', '')

def splitroot(path):
    return ('', '', '')

def basename(p):
    return p

def dirname(p):
    return p

def commonprefix(m):
    return ''

def abspath(path):
    return ''

def realpath(path, strict=False):
    return ''

def normpath(path):
    return ''

def relpath(path, start=None):
    return ''

def expanduser(path):
    return path

def expandvars(path):
    return path

def commonpath(paths):
    return ''

def getsize(filename):
    return 1

def getatime(filename):
    return 1.0

def getmtime(filename):
    return 1.0

def getctime(filename):
    return 1.0
