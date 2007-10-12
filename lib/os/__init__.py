
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

def system(c):
    return 1

class __cstat:
    def __init__(self, path):
        self.st_mode = 1
    def __repr__(self):
        return '(%d, ..)' % self.st_mode

def stat(path):
    return __cstat(path)

def lstat(path):
    return __cstat(path)
