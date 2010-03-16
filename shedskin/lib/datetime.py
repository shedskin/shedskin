from time import struct_time
import string

MINYEAR = 1
MAXYEAR = 9999

class date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def today():
        return date(0, 0, 0)

    def fromtimestamp(timestamp):
        return date(0, 0, 0)

    def fromordinal(ordinal):
        return date(0, 0, 0)

    today         = staticmethod(today)
    fromtimestamp = staticmethod(fromtimestamp)
    fromordinal   = staticmethod(fromordinal)

    def __add__(self, other):
        return self

    def __sub__(self, other):
        return other.subfromdate()

    def subfromdate(self):
        return timedelta()

    def replace(self, year=0, month=0, day=0):
        return self

    def timetuple(self):
        return struct_time((1,))

    def toordinal(self):
        return 1

    def weekday(self):
        return 1

    def isoweekday(self):
        return 1

    def isocalendar(self):
        return (1, 1, 1)

    def isoformat(self):
        return ''

    def ctime(self):
        return ''

    def strftime(self, format):
        return ''

    def __str__(self):
        return ''

class datetime(date):
    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        date.__init__(self, year, month, day)

        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond

        self.tzinfo = tzinfo

        tzinfo.utcoffset(self)
        tzinfo.dst(self)
        tzinfo.tzname(self)

    def today():
        return datetime(0, 0, 0)

    def now(tz=None):
        tz.utcoffset(self)
        return datetime(0, 0, 0)

    def utcnow():
        return datetime(0, 0, 0)

    def fromtimestamp(timestamp, tz=None):
        tz.fromutc(self)
        return datetime(0, 0, 0)

    def utcfromtimestamp(timestamp):
        return datetime(0, 0, 0)

    def fromordinal(ordinal):
        return datetime(0, 0, 0)

    def combine(date, time):
        return datetime(0, 0, 0)

    def strptime(date_string, format):
        return datetime(0, 0, 0)

    today = staticmethod(today)
    now = staticmethod(now)
    utcnow = staticmethod(utcnow)
    fromtimestamp = staticmethod(fromtimestamp)
    utcfromtimestamp = staticmethod(utcfromtimestamp)
    fromordinal = staticmethod(fromordinal)
    combine = staticmethod(combine)
    strptime = staticmethod(strptime)

    def __add__(self, delta):
        return self

    def __sub__(self, other):
        return other.subfromdatetime()

    def subfromdatetime(self):
        return timedelta()

    def date(self):
        return date(self.year, self.month, self.day)

    def time(self):
        return time(self.hour, self.minute, self.second, self.microsecond, 0)

    def timetz(self):
        return time(self.hour, self.minute, self.second, self.microsecond, self.tzinfo)

    def replace(self, year=0, month=0, day=0, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        return self

    def astimezone(self, tz):
        tz.fromutc(self)
        return self

    def utcoffset(self):
        return timedelta()

    def dst(self):
        return timedelta()

    def tzname(self):
        return ''

    def timetuple(self):
        return struct_time((1,))

    def utctimetuple(self):
        return struct_time((1,))

    def toordinal(self):
        return 1

    def weekday(self):
        return 1

    def isoweekday(self):
        return 1

    def isocalendar(self):
        return (1, 1, 1)

    def isoformat(self, sep='T'):
        return ''

    def ctime(self):
        return ''

    def strftime(self, format):
        return ''

    def __str__(self):
        return ''

class time:
    def __init__(self, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond

        self.tzinfo = tzinfo

        dt = datetime(0,0,0)
        tzinfo.utcoffset(dt)
        tzinfo.dst(dt)
        tzinfo.tzname(dt)

    def replace(self, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        return self

    def isoformat(self):
        return ''

    def strftime(self, format):
        return ''

    def utcoffset(self):
        return timedelta()

    def dst(self):
        return timedelta()

    def tzname(self):
        return ''

    def __str__(self):
        return ''

class timedelta:
    def __init__(self, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        self.days = 1
        self.seconds = 1
        self.microseconds = 1

    def __add__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __mul__(self, n):
        return self

    def __div__(self, n):
        return self

    def __neg__(self):
        return self

    def __floordiv__(self, n):
        return self

    def __abs__(self):
        return self

    def subfromdate(self):
        return date(1, 1, 1)

    def subfromdatetime(self):
        return datetime(1, 1, 1)

    def __str__(self):
        return ''

class tzinfo:
    def __init__(self):
        pass
    def utcoffset(self, dt):
        return timedelta()
    def dst(self, dt):
        return timedelta()
    def tzname(self, dt):
        return ''
    def fromutc(self, dt):
        self.utcoffset(dt)
        self.dst(dt)
        return datetime(0,0,0)

date.min = date (MINYEAR, 1, 1)
date.max = date (MAXYEAR, 12, 31)
date.resolution = timedelta(days=1)

datetime.min = datetime(MINYEAR, 1, 1, tzinfo=None)
datetime.max = datetime(MAXYEAR, 12, 31, 23, 59, 59, 999999, tzinfo=None)
datetime.resolution = timedelta(microseconds=1)

time.min = time(0, 0, 0, 0)
time.max = time(23, 59, 59, 999999)
time.resolution = timedelta(microseconds=1)

timedelta.min = timedelta(-999999999)
timedelta.max = timedelta(days=999999999, hours=23, minutes=59, seconds=59, microseconds=999999)
timedelta.resolution = timedelta(microseconds=1)
