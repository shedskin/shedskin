# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

START_RECORD = START_FIELD = ESCAPED_CHAR = IN_FIELD = IN_QUOTED_FIELD = ESCAPE_IN_QUOTED_FIELD = QUOTE_IN_QUOTED_FIELD = EAT_CRNL = 0
QUOTE_MINIMAL = QUOTE_ALL = QUOTE_NONNUMERIC = QUOTE_NONE = 0

class Error(Exception):
    pass

class Dialect:
    def __init__(self):
        self.delimiter = ''
        self.doublequote = True
        self.escapechar = ''
        self.lineterminator = ''
        self.quotechar = ''
        self.quoting = 0
        self.skipinitialspace = False
        self.strict = False

class reader:
    def __init__(self, input_iter, dialect=None, delimiter=None, quotechar=None, doublequote=-1, skipinitialspace=-1, lineterminator=None, quoting=-1, escapechar=None, strict=-1):
        self.dialect = Dialect()
        self.line_num = 0

    def __iter__(self):
        return __iter([''])

    def __next__(self):
        return ['']

class writer:
    def __init__(self, output_file, dialect=None, delimiter=None, quotechar=None, doublequote=-1, skipinitialspace=-1, lineterminator=None, quoting=-1, escapechar=None, strict=-1):
        self.dialect = Dialect()

    def writerow(self, seq):
        pass

    def writerows(self, seqs):
        pass

class DictReader:
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, dialect=None, delimiter=None, quotechar=None, doublequote=-1, skipinitialspace=-1, lineterminator=None, quoting=-1, escapechar=None, strict=-1):
        self.dialect = '' # TODO not Dialect()?
        self.reader = reader(f)
        self._fieldnames = ['']
        self.restval = ''
        self.line_num = 0

    def __iter__(self):
        return __iter({'': ''})

    def getfieldnames(self):
        return self._fieldnames
    def setfieldnames(self, value):
        pass
    fieldnames = property(getfieldnames, setfieldnames)

    def __next__(self):
        return {'': ''}

class DictWriter:
    def __init__(self, f, fieldnames, restval="", extrasaction="raise", dialect="excel", delimiter=None, quotechar=None, doublequote=-1, skipinitialspace=-1, lineterminator=None, quoting=-1, escapechar=None, strict=-1):
        self.dialect = Dialect()
        self.writer = writer(f)
        self.fieldnames = ['']
        self.restval = ''
        self.extrasaction = ''

    def writeheader(self):
        pass

    def writerow(self, rowdict):
        pass

    def writerows(self, rowdicts):
        pass

def list_dialects():
    return ['']

def get_dialect(name):
    return Dialect()

def register_dialect(name, dialect="excel", delimiter=None, quotechar=None, doublequote=-1, skipinitialspace=-1, lineterminator=None, quoting=-1, escapechar=None, strict=-1):
    pass

def unregister_dialect(name):
    pass

def field_size_limit(new_limit=-1):
    return new_limit
