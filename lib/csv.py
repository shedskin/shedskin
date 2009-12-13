START_RECORD = START_FIELD = ESCAPED_CHAR = IN_FIELD = IN_QUOTED_FIELD = ESCAPE_IN_QUOTED_FIELD = QUOTE_IN_QUOTED_FIELD = EAT_CRNL = 0
QUOTE_MINIMAL = QUOTE_ALL = QUOTE_NONNUMERIC = QUOTE_NONE = 0

class Error(Exception):
    pass

def list_dialects():
    return ['excel', 'excel-tab']

def field_size_limit(new_limit=-1):
    return new_limit

class reader:
    def __init__(self, input_iter, dialect=None, delimiter=None, quotechar=None, doublequote=-1, skipinitialspace=-1, lineterminator=None, quoting=-1, escapechar=None, strict=-1):
        pass

    def __iter__(self):
        return __iter([''])

    def next(self):
        return ['']

class writer:
    def __init__(self, output_file, dialect=None, delimiter=None, quotechar=None, doublequote=-1, skipinitialspace=-1, lineterminator=None, quoting=-1, escapechar=None, strict=-1):
        pass

    def writerow(self, seq):
        pass

    def writerows(self, seqs):
        pass
