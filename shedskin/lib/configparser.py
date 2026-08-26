# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

import re
import io

DEFAULTSECT = "DEFAULT"
MAX_INTERPOLATION_DEPTH = 10

class Error(Exception):
    def __init__(self, msg=''): pass
class NoSectionError(Error):
    def __init__(self, section): pass
class DuplicateSectionError(Error):
    def __init__(self, section, source=None, lineno=-1): pass
class DuplicateOptionError(Error):
    def __init__(self, section, option, source=None, lineno=-1): pass
class NoOptionError(Error):
    def __init__(self, option, section): pass
class InterpolationError(Error):
    def __init__(self, option, section, msg): pass
class InterpolationMissingOptionError(InterpolationError):
    def __init__(self, option, section, rawval, reference): pass
class InterpolationSyntaxError(InterpolationError):
    pass
class InterpolationDepthError(InterpolationError):
    def __init__(self, option, section, rawval): pass
class ParsingError(Error):
    def __init__(self, filename): pass
class MissingSectionHeaderError(ParsingError):
    def __init__(self, filename, lineno, line): pass

class RawConfigParser:
    def __init__(self, defaults=None, default_section=None):
        self._sections = {'': ''}
        self._defaults = {'': ''}
        self.default_section = ''
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
        return [('', SectionProxy(self, ''))]
    def getint(self, section, option):
        return 1
    def getfloat(self, section, option):
        return 1.0
    def getboolean(self, section, option):
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
