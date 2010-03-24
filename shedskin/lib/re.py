
I = IGNORECASE = 2
L = LOCALE = 4
M = MULTILINE = 8
S = DOTALL = 16
U = UNICODE = 32
X = VERBOSE = 64

class error(Exception): pass

class match_object:
    def __init__(self):
        self.pos = 0
        self.endpos = 0
        self.lastindex = 0
        self.lastgroup = ''
        self.re = re_object()
        self.string = ''

    def expand(self, tpl):
        return ''

    def group(self, *args):
        return ('',)
    def __group0(self, arg):
        return ''
    def __group1(self, arg):
        return ''

    def start(self, i = 0):
        return 1

    def end(self, i = 0):
        return 1

    def groups(self, defval = 0):
        return ('',)

    def groupdict(self, defval = 0):
        return {'' : ''}

    def __repr__(self):
        return ''

class re_object:
    def __init__(self):
        self.flags = 0
        self.groupindex = {'' : ''}
        self.pattern = ''

    def match(self, s, pos=0, endpos=-1):
        return match_object()

    def search(self, s, pos=0, endpos=-1):
        return match_object()

    def split(self, s, maxn=0):
        return ['']

    def sub(self, tpl, s, maxn=0):
        tpl(match_object())
        return ''

    def subn(self, tpl, s, maxn=0):
        tpl(match_object())
        return ('', 0)

    def finditer(self, s, pos=0, endpos=-1):
        return __iter(match_object())

    def findall(self, s, flags=0):
        return ['']

    def __repr__(self):
        return ''

def compile(pat, flgs=0):
    return re_object()

def match(pat, s, flags=0):
    return match_object()

def search(pat, s, flags=0):
    return match_object()

def split(pat, s, maxn=0):
    return ['']

def sub(pat, tpl, s, maxn=0):
    tpl(match_object())
    return ''

def subn(pat, tpl, s, maxn=0):
    tpl(match_object())
    return ('', 0)

def finditer(pat, s, pos=0, endpos=-1):
    return __iter(match_object())

def findall(pat, s, flags=0):
    return ['']

def escape(s):
    return ''
