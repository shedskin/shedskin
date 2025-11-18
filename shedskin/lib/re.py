# Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE)


# TODO purge, match_object.__getitem__, fullmatch, re_object.groups attr,

I = IGNORECASE = 2
L = LOCALE = 4
M = MULTILINE = 8
S = DOTALL = 16
U = UNICODE = 32
X = VERBOSE = 64

class PatternError(Exception): pass

class error(Exception): pass  # deprecated alias for PatternError


class match_object:  # TODO __getitem__(g)
    def __init__(self):
        self.pos = 0
        self.endpos = 0
        self.lastindex = 0
        self.lastgroup = ''
        self.re = re_object()
        self.string = ''

    def expand(self, template):
        return ''

    def group(self, *args):
        return ('',)
    def __group0(self, arg):
        return ''
    def __group1(self, arg):
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

class re_object:  # TODO fullmatch
    def __init__(self):  # TODO .groups
        self.flags = 0
        self.groupindex = {'' : ''}
        self.pattern = ''

    def match(self, string, pos=0, endpos=-1):
        return match_object()

    def search(self, string, pos=0, endpos=-1):
        return match_object()

    def split(self, string, maxsplit=0):
        return ['']

    def sub(self, repl, string, count=0):
        repl(match_object())
        return ''

    def subn(self, repl, string, count=0):
        repl(match_object())
        return ('', 0)

    def finditer(self, string, pos=0, endpos=-1):
        return __iter(match_object())

    def findall(self, string, pos=0, endpos=-1):
        return ['']

    def __repr__(self):
        return ''

def compile(pattern, flags=0):
    return re_object()

def match(pattern, string, flags=0):  # TODO fullmatch
    return match_object()

def search(pattern, string, flags=0):
    return match_object()

def split(pattern, string, maxsplit=0, flags=0):
    return ['']

def sub(pattern, repl, string, count=0, flags=0):
    repl(match_object())
    return ''

def subn(pattern, repl, string, count=0, flags=0):
    repl(match_object())
    return ('', 0)

def finditer(pattern, string, flags=0):
    return __iter(match_object())

def findall(pattern, string, flags=0):
    return ['']

def escape(pattern):
    return ''
