import datetime



def test_date():
    assert datetime.date(2007, 4, 3).replace(month=11) == datetime.date(2007, 11, 3)

def test_date_ctime():
    # regression test: date.ctime() passed bare C++ int literals (0, 0, 0)
    # for the hour/minute/second fields to the internal __mod6 formatting
    # helper. __mod6 only has real %d handling specialized for __ss_int
    # (long); a plain 'int' silently falls through to a no-op template
    # specialization, so the hour/minute/second fields vanished entirely
    # instead of printing as "00".
    assert datetime.date(2023, 5, 17).ctime() == 'Wed May 17 00:00:00 2023'

def test_date_day_out_of_range():
    # 2023 is not a leap year: Feb has 28 days, so day 29 must be rejected
    error = ''
    try:
        datetime.date(2023, 2, 29)
    except ValueError as e:
        error = str(e)
    assert error == 'day is out of range for month'

    # 2024 is a leap year: day 29 is valid, day 30 must still be rejected
    assert datetime.date(2024, 2, 29).day == 29

    error = ''
    try:
        datetime.date(2024, 2, 30)
    except ValueError as e:
        error = str(e)
    assert error == 'day is out of range for month'

    # day 31 must be rejected for a 30-day month
    error = ''
    try:
        datetime.date(2024, 4, 31)
    except ValueError as e:
        error = str(e)
    assert error == 'day is out of range for month'

def test_date_compare_year_boundary():
    # regression test: __cmp__ used to encode dates as year*366+month*31+day,
    # but month*31+day can reach 403, which is larger than the 366 weight
    # given to a single year -- so late-December dates could compare as
    # greater than early-January dates of the following year.
    a = datetime.date(2000, 12, 31)
    b = datetime.date(2001, 1, 1)
    assert a < b
    assert b > a
    assert not a > b
    assert not b < a
    assert a != b

def test_datetime_compare_year_boundary():
    a = datetime.datetime(2000, 12, 31, 23, 0, 0)
    b = datetime.datetime(2001, 1, 1, 0, 0, 0)
    assert a < b
    assert b > a
    assert not a > b
    assert not b < a
    assert a != b

def test_datetime_basic():
    assert datetime.MAXYEAR == 9999
    assert datetime.MINYEAR == 1

    a = datetime.datetime.now()
    b = datetime.datetime.now()
    assert a <= b

    assert datetime.datetime.utcnow().date().year > 2020


class TZ2(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0, 0, 0, 0, -339)


def test_datetime_custom_tzinfo():
    dt = datetime.datetime(2007, 4, 3, tzinfo=TZ2())
    assert dt.date() == datetime.date(2007, 4, 3)


def test_date_fromisoformat():
    assert datetime.date.fromisoformat('2020-01-01') == datetime.date(2020, 1, 1)

    error = ''
    try:
        datetime.date.fromisoformat('2020-1-1')  # not zero-padded
    except ValueError as e:
        error = str(e)
    assert error == "Invalid isoformat string: '2020-1-1'"

    error = ''
    try:
        datetime.date.fromisoformat('not-a-date')
    except ValueError as e:
        error = str(e)
    assert error == "Invalid isoformat string: 'not-a-date'"

    # still goes through the normal range validation
    error = ''
    try:
        datetime.date.fromisoformat('2020-02-30')
    except ValueError as e:
        error = str(e)
    assert error == 'day is out of range for month'


def test_time_fromisoformat():
    assert datetime.time.fromisoformat('12:30:15') == datetime.time(12, 30, 15)
    assert datetime.time.fromisoformat('12:30:15.5') == datetime.time(12, 30, 15, 500000)
    assert datetime.time.fromisoformat('12:30:15.123456') == datetime.time(12, 30, 15, 123456)

    # fractional part longer than 6 digits is truncated, same as cpython
    assert datetime.time.fromisoformat('12:30:15.1234567').microsecond == 123456

    error = ''
    try:
        datetime.time.fromisoformat('1:30:15')  # hour not zero-padded
    except ValueError as e:
        error = str(e)
    assert error == "Invalid isoformat string: '1:30:15'"

    error = ''
    try:
        datetime.time.fromisoformat('12:30:15.')  # dot with no digits
    except ValueError as e:
        error = str(e)
    assert error == "Invalid isoformat string: '12:30:15.'"


def test_datetime_fromisoformat():
    assert datetime.datetime.fromisoformat('2020-01-01T12:30:15.500000') == \
        datetime.datetime(2020, 1, 1, 12, 30, 15, 500000)
    assert datetime.datetime.fromisoformat('2020-01-01 12:30:15') == \
        datetime.datetime(2020, 1, 1, 12, 30, 15)
    # any single character is accepted as date/time separator, same as
    # cpython (>= 3.11)
    assert datetime.datetime.fromisoformat('2020-01-01t12:30:15') == \
        datetime.datetime(2020, 1, 1, 12, 30, 15)
    assert datetime.datetime.fromisoformat('2020-01-01X12:30:15') == \
        datetime.datetime(2020, 1, 1, 12, 30, 15)
    # date-only is accepted, time defaults to midnight
    assert datetime.datetime.fromisoformat('2020-01-01') == datetime.datetime(2020, 1, 1)

    error = ''
    try:
        datetime.datetime.fromisoformat('2020-01-01  12:30:15')  # 2-char separator
    except ValueError as e:
        error = str(e)
    assert error != ''

    # range-check errors from the underlying constructor must still surface
    # with their own specific message, not get overwritten
    error = ''
    try:
        datetime.datetime.fromisoformat('2020-01-01T25:00:00')
    except ValueError as e:
        error = str(e)
    assert error == 'hour must be in 0..23'


def test_timedelta_total_seconds():
    tol = 1e-3  # generous enough to also pass under --float32

    td = datetime.timedelta(days=2, hours=3, minutes=30, seconds=15, microseconds=500000)
    assert abs(td.total_seconds() - 185415.5) < tol

    td = datetime.timedelta(seconds=-5, microseconds=-500000)
    assert abs(td.total_seconds() - (-5.5)) < tol

    td = datetime.timedelta()
    assert abs(td.total_seconds() - 0.0) < tol

    td = datetime.timedelta(weeks=1)
    assert abs(td.total_seconds() - 604800.0) < tol

    # negative days, positive seconds/microseconds (internal normalization)
    td = datetime.timedelta(days=-1, seconds=1, microseconds=1)
    assert abs(td.total_seconds() - (-86398.999999)) < tol


def test_timedelta_floordiv():
    # regression test: __floordiv__ used to compute days/seconds/microseconds
    # independently as (double)/n, which is not equivalent to exact integer
    # floor division of the total duration and produced off-by-one
    # microsecond/second results for most non-trivial inputs.
    td = datetime.timedelta(days=-5, seconds=1, microseconds=1)
    r = td // 3
    assert (r.days, r.seconds, r.microseconds) == (-2, 28800, 333333)

    td = datetime.timedelta(days=-1)
    r = td // 2
    assert (r.days, r.seconds, r.microseconds) == (-1, 43200, 0)

    td = datetime.timedelta(days=7, seconds=100)
    r = td // 3
    assert (r.days, r.seconds, r.microseconds) == (2, 28833, 333333)

    # large day counts used to overflow the (day*86400+seconds)*1e6 style
    # intermediate value when computed as a double
    td = datetime.timedelta(days=999999999, seconds=86399, microseconds=999999)
    r = td // 7
    assert (r.days, r.seconds, r.microseconds) == (142857142, 74057, 142857)


def test_timedelta_truediv():
    # regression test: __truediv__ had the same floating-point precision
    # issue as __floordiv__ (see test_timedelta_floordiv)
    td = datetime.timedelta(days=-5, seconds=1, microseconds=1)
    r = td / 3
    assert (r.days, r.seconds, r.microseconds) == (-2, 28800, 333334)

    # round-half-to-even tie-breaking, matching cpython
    assert (datetime.timedelta(microseconds=1) / 2).microseconds == 0
    assert (datetime.timedelta(microseconds=3) / 2).microseconds == 2
    assert (datetime.timedelta(microseconds=5) / 2).microseconds == 2
    assert (datetime.timedelta(microseconds=7) / 2).microseconds == 4


def test_all():
        test_date()
        test_date_ctime()
        test_date_day_out_of_range()
        test_date_compare_year_boundary()
        test_date_fromisoformat()
        test_datetime_compare_year_boundary()
        test_datetime_basic()
        test_datetime_custom_tzinfo()
        test_time_fromisoformat()
        test_datetime_fromisoformat()
        test_timedelta_total_seconds()
        test_timedelta_floordiv()
        test_timedelta_truediv()

if __name__ == "__main__":
    test_all()
