timezone = 0
tzname = ("str", "str")

def clock():
    return 1.0

def sleep(s):
    pass

def time():
    return 1.0

class struct_time:
    def __init__(self, tuple):
        self.tm_year = 0
        self.tm_mon = 0
        self.tm_mday = 0
        self.tm_hour = 0
        self.tm_min = 0
        self.tm_sec = 0
        self.tm_wday = 0
        self.tm_yday = 0
        self.isdst = 0
    def __getitem__(self, n):
        return 1
    def __repr__(self):
        return "str"

def mktime(tuple):
    return 1.0

def localtime(timep=None):
    return struct_time((1,2,3))

def gmtime(seconds=None):
    return struct_time((1,2,3))

def asctime(tuple=None):
    return "str"

def ctime(seconds=None):
    return "str"

def strftime(format, tuple=None):
    return "str"

def strptime(string, format):
    return struct_time((1,2,3))

