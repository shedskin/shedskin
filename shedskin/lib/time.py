# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

timezone = 0
altzone = 0
daylight = 0
tzname = ("str", "str")

CLOCK_REALTIME = 0
CLOCK_MONOTONIC = 0
CLOCK_MONOTONIC_RAW = 0
CLOCK_PROCESS_CPUTIME_ID = 0
CLOCK_THREAD_CPUTIME_ID = 0
CLOCK_BOOTTIME = 0
CLOCK_TAI = 0
CLOCK_UPTIME_RAW = 0

def clock():
    return 1.0

def clock_gettime(clk_id):
    return 1.0

def clock_gettime_ns(clk_id):
    return 1

def clock_getres(clk_id):
    return 1.0

def thread_time():
    return 1.0

def thread_time_ns():
    return 1

def perf_counter():
    return 1.0

def monotonic():
    return 1.0

def process_time():
    return 1.0

def sleep(s):
    pass

def time():
    return 1.0

def time_ns():
    return 1

def perf_counter_ns():
    return 1

def monotonic_ns():
    return 1

def process_time_ns():
    return 1

class __clock_info:
    def __init__(self):
        self.implementation = ''
        self.monotonic = False
        self.adjustable = False
        self.resolution = 0.0

    def __repr__(self):
        return 'str'

def get_clock_info(name):
    return __clock_info()

# a tuple, with the items also as attributes (and tm_zone, tm_gmtoff)
class struct_time(tuple):
    def __init__(self, tuple):
        self.unit = 0
        self.tm_year = 0
        self.tm_mon = 0
        self.tm_mday = 0
        self.tm_hour = 0
        self.tm_min = 0
        self.tm_sec = 0
        self.tm_wday = 0
        self.tm_yday = 0
        self.tm_isdst = 0
        self.tm_zone = ''
        self.tm_gmtoff = 0
    def __slice__(self, x, l, u, s):
        return (self.unit,)
    def __mul__(self, n):
        return (self.unit,)
    def __repr__(self):
        return ''

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

