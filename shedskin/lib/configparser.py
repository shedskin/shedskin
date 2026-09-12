# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

import re
import io

DEFAULTSECT = "DEFAULT"
MAX_INTERPOLATION_DEPTH = 10

__void = 0  # 'no fallback given' sentinel for the typed getters

class Error(Exception):
    def __init__(self, msg=''):
        self.message = msg
class NoSectionError(Error):
    def __init__(self, section):
        self.message = ''
        self.section = section
class DuplicateSectionError(Error):
    def __init__(self, section, source=None, lineno=-1):
        self.message = ''
        self.section = section
        self.source = source
        self.lineno = lineno
class DuplicateOptionError(Error):
    def __init__(self, section, option, source=None, lineno=-1):
        self.message = ''
        self.section = section
        self.option = option
        self.source = source
        self.lineno = lineno
class NoOptionError(Error):
    def __init__(self, option, section):
        self.message = ''
        self.option = option
        self.section = section
class InterpolationError(Error):
    def __init__(self, option, section, msg):
        self.message = msg
        self.option = option
        self.section = section
class InterpolationMissingOptionError(InterpolationError):
    def __init__(self, option, section, rawval, reference):
        self.message = ''
        self.option = option
        self.section = section
        self.reference = reference
class InterpolationSyntaxError(InterpolationError):
    pass
class InterpolationDepthError(InterpolationError):
    def __init__(self, option, section, rawval):
        self.message = ''
        self.option = option
        self.section = section
class ParsingError(Error):
    def __init__(self, filename):
        self.message = ''
        self.filename = filename
        self.errors = [(0, '')]
    def append(self, lineno, line):
        pass
    def combine(self, others):
        return self
class MissingSectionHeaderError(ParsingError):
    def __init__(self, filename, lineno, line):
        self.message = ''
        self.filename = filename
        self.errors = [(0, '')]
        self.lineno = lineno
        self.line = line

class Interpolation:
    """Dummy interpolation that passes the value through with no changes."""
    def before_get(self, parser, section, option, value, defaults):
        return value
    def before_set(self, parser, section, option, value):
        return value
    def before_read(self, parser, section, option, value):
        return value
    def before_write(self, parser, section, option, value):
        return value

class BasicInterpolation(Interpolation):
    """%(name)s interpolation, as used by ConfigParser by default."""
    pass

class ExtendedInterpolation(Interpolation):
    """${section:option} interpolation, in the style of zc.buildout."""
    pass

# seed attribute types: these exceptions are only ever raised from the C++
# implementation, so without a construction here their attributes stay untyped
__cperror0 = Error('')
__cperror1 = NoSectionError('')
__cperror2 = DuplicateSectionError('', '', 0)
__cperror3 = DuplicateOptionError('', '', '', 0)
__cperror4 = NoOptionError('', '')
__cperror5 = InterpolationError('', '', '')
__cperror6 = InterpolationMissingOptionError('', '', '', '')
__cperror7 = InterpolationSyntaxError('', '', '')
__cperror8 = InterpolationDepthError('', '', '')
__cperror9 = ParsingError('')
__cperror10 = MissingSectionHeaderError('', 0, '')

class RawConfigParser:
    def __init__(self, defaults=None, default_section=None, interpolation=None):
        self._sections = {'': ''}
        self._defaults = {'': ''}
        self.default_section = ''
        if interpolation is None:
            self._interpolation = Interpolation()
        else:
            self._interpolation = interpolation
    def defaults(self):
        return self._defaults
    def sections(self):
        return ['']
    def add_section(self, section):
        pass
    def has_section(self, section):
        return True
    def options(self, section):
        return ['']
    def read(self, filenames):
        return ['']
    def read_string(self, string, source=None):
        pass
    def read_dict(self, dictionary, source=None):
        pass
    def read_file(self, f, source=None):
        pass
    def get(self, section, option, raw=False, vars=None, fallback=None): # XXX
        return ''
    def items(self, section, __kw_raw=False, __kw_vars=None):
        return [('', '')]
    def __items0(self, __kw_raw=False, __kw_vars=None):
        # not SectionProxy(self, ''): for a zero-arg items() call the
        # compiler misaligns the __kw_ defaults after the arity redirect and
        # lets 'False' flow into 'self' here, which would then surface as
        # {ConfigParser, bool} on SectionProxy.parser (see 'claude bugs')
        return [('', SectionProxy(RawConfigParser(), ''))]
    def getint(self, section, option, raw=False, vars=None, fallback=__void):
        return 1
    def getfloat(self, section, option, raw=False, vars=None, fallback=__void):
        return 1.0
    def getboolean(self, section, option, raw=False, vars=None, fallback=__void):
        return True
    def optionxform(self, optionstr):
        return ''
    def has_option(self, section, option):
        return True
    def set(self, section, option, value):
        pass
    def write(self, fp):
        pass
    def remove_option(self, section, option):
        return True
    def remove_section(self, section):
        return True
    def _read(self, fp, fpname):
        pass
    def popitem(self):
        return ('', SectionProxy(self, ''))
    def __getitem__(self, section):
        return SectionProxy(self, section)
    def __setitem__(self, section, value):
        pass
    def __delitem__(self, section):
        pass
    def __contains__(self, section):
        return True
    def __len__(self):
        return 1
    def __iter__(self):
        return iter([''])

class SectionProxy:
    def __init__(self, parser, name):
        self._parser = parser
        self._name = name
    def getname(self):
        return self._name
    def getparser(self):
        return self._parser
    name = property(getname)
    parser = property(getparser)
    def __repr__(self):
        return ''
    def get(self, option, fallback=None, raw=False, vars=None):
        return ''
    def getint(self, option, fallback=__void, raw=False, vars=None):
        return 1
    def getfloat(self, option, fallback=__void, raw=False, vars=None):
        return 1.0
    def getboolean(self, option, fallback=__void, raw=False, vars=None):
        return True
    def __getitem__(self, key):
        return ''
    def __setitem__(self, key, value):
        pass
    def __delitem__(self, key):
        pass
    def __contains__(self, key):
        return True
    def __len__(self):
        return 1
    def __iter__(self):
        return iter([''])

class ConfigParser(RawConfigParser):
    pass
