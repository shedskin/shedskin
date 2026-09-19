# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)


argv = ['']

stdin, stdout, stderr = file('stdin'), file('stdout'), file('stderr')
__stdin__, __stdout__, __stderr__ = stdin, stdout, stderr

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

def getsizeof(obj, default=0):
    return 0

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

class __flags:
    def __init__(self):
        self.debug = 0
        self.inspect = 0
        self.interactive = 0
        self.optimize = 0
        self.dont_write_bytecode = 0
        self.no_user_site = 0
        self.no_site = 0
        self.ignore_environment = 0
        self.verbose = 0
        self.bytes_warning = 0
        self.quiet = 0
        self.hash_randomization = 0
        self.isolated = 0
        self.dev_mode = False
        self.utf8_mode = 0
        self.warn_default_encoding = 0
        self.safe_path = False
        self.int_max_str_digits = 0
        self.gil = 0
        self.thread_inherit_context = 0
        self.context_aware_warnings = 0

    def __repr__(self):
        return 'str'

flags = __flags()

class __int_info:
    def __init__(self):
        self.bits_per_digit = 0
        self.sizeof_digit = 0
        self.default_max_str_digits = 0
        self.str_digits_check_threshold = 0

    def __repr__(self):
        return 'str'

int_info = __int_info()

class __hash_info:
    def __init__(self):
        self.width = 0
        self.modulus = 0
        self.inf = 0
        self.nan = 0
        self.imag = 0
        self.algorithm = ''
        self.hash_bits = 0
        self.seed_bits = 0
        self.cutoff = 0

    def __repr__(self):
        return 'str'

hash_info = __hash_info()
