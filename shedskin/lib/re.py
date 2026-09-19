# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)


# NOTE: Pattern/Match are shedskin's type-inference stubs for compiled
# patterns and match results; the real logic lives in re.cpp.

NOFLAG = 0
I = IGNORECASE = 2
L = LOCALE = 4
M = MULTILINE = 8
S = DOTALL = 16
U = UNICODE = 32
X = VERBOSE = 64
DEBUG = 128
A = ASCII = 256

class PatternError(Exception):
    def __init__(self, msg, pattern=None, pos=-1):
        self.msg = msg
        self.pattern = pattern
        self.pos = pos
        self.lineno = 0
        self.colno = 0

class error(PatternError): pass  # deprecated alias for PatternError (C++: using)


class Match:
    def __init__(self):
        self.pos = 0
        self.endpos = 0
        self.lastindex = 0
        self.lastgroup = ''
        self.re = Pattern()
        self.string = ''

    def expand(self, template):
        return ''

    def group(self, *args):
        return ('',)
    def __group0(self):
        return ''
    def __group1(self, arg):
        return ''

    def __getitem__(self, g):
        return ''

    def start(self, group=0):
        return 1

    def end(self, group=0):
        return 1

    def span(self, group=0):
        return (1,)

    def groups(self, default=None):
        return ('',)

    def groupdict(self, default=None):
        return {'' : ''}

    def __repr__(self):
        return ''

class Pattern:
    def __init__(self):
        self.flags = 0
        self.groups = 0
        self.groupindex = {'' : ''}
        self.pattern = ''

    def prefixmatch(self, string, pos=0, endpos=-1):
        return Match()

    def match(self, string, pos=0, endpos=-1):
        return Match()

    def fullmatch(self, string, pos=0, endpos=-1):
        return Match()

    def search(self, string, pos=0, endpos=-1):
        return Match()

    def split(self, string, maxsplit=0):
        return ['']

    def sub(self, repl, string, count=0):
        repl(Match())
        return ''

    def subn(self, repl, string, count=0):
        repl(Match())
        return ('', 0)

    def finditer(self, string, pos=0, endpos=-1):
        return __iter(Match())

    def findall(self, string, pos=0, endpos=-1):
        return ['']

    def __repr__(self):
        return ''

def compile(pattern, flags=0):
    return Pattern()

def match(pattern, string, flags=0):
    return Match()

def prefixmatch(pattern, string, flags=0):
    return Match()

def fullmatch(pattern, string, flags=0):
    return Match()

def search(pattern, string, flags=0):
    return Match()

def split(pattern, string, maxsplit=0, flags=0):
    return ['']

def sub(pattern, repl, string, count=0, flags=0):
    repl(Match())
    return ''

def subn(pattern, repl, string, count=0, flags=0):
    repl(Match())
    return ('', 0)

def finditer(pattern, string, flags=0):
    return __iter(Match())

def findall(pattern, string, flags=0):
    return ['']

def escape(pattern):
    return ''

def purge():
    pass
