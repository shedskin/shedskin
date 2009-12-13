import re

class Error(Exception):
    def __init__(self, msg=''): pass
class NoSectionError(Error):
    def __init__(self, section): pass
class DuplicateSectionError(Error):
    def __init__(self, section): pass
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
    def __init__(self, defaults=None):
        self._sections = {'': ''}
        self._defaults = {'': ''}
    def defaults(self):
        return self._defaults
    def sections(self):
        return self._sections
    def add_section(self, section):
        pass
    def has_section(self, section):
        return True
    def options(self, section):
        return ['']
    def read(self, filenames):
        return ['']
    def readfp(self, fp, filename=None):
        pass
    def get(self, section, option, raw=False, vars=None): # XXX
        return ''
    def items(self, section):
        return {'':''}
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

class ConfigParser(RawConfigParser):
    def get(self, section, option, raw=False, vars=None):
        return ''
    def items(self, section, raw=False, vars=None):
        return {'':''}
    def _interpolate(self, section, option, rawval, vars):
        return ''
    #def _interpolation_replace(self, match):

