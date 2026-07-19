# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)


argv = ['']

stdin, stdout, stderr = file('stdin'), file('stdout'), file('stderr')

version = ''
version_info = (0,)
copyright = ''
platform = ''
byteorder = ''
hexversion = 0
maxint = 0
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
