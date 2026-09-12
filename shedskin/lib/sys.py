# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)


argv = ['']

stdin, stdout, stderr = file('stdin'), file('stdout'), file('stderr')

version = ''
version_info = (0,)
copyright = ''
platform = ''
byteorder = ''
hexversion = 0
maxsize = 0
maxunicode = 0
executable = ''

def setrecursionlimit(limit):
    pass

def getrecursionlimit():
    return 0

def intern(s):
    return s

def is_finalizing():
    return False

def getdefaultencoding():
    return ''

def getfilesystemencoding():
    return ''

def exit(code=0):
    pass

def getfilesystemencodeerrors():
    return ''

float_repr_style = ''
orig_argv = ['']

class __float_info:
    def __init__(self):
        self.max = 1.0
        self.max_exp = 0
        self.max_10_exp = 0
        self.min = 1.0
        self.min_exp = 0
        self.min_10_exp = 0
        self.dig = 0
        self.mant_dig = 0
        self.epsilon = 1.0
        self.radix = 0
        self.rounds = 0

    def __repr__(self):
        return 'str'

float_info = __float_info()

class __implementation:
    def __init__(self):
        self.name = ''
        self.version = version_info
        self.hexversion = 0

    def __repr__(self):
        return 'str'

implementation = __implementation()
