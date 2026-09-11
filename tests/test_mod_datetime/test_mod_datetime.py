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

def test_date_replace_keeps_unchanged_day_out_of_range():
    # replacing month/year only (day left alone) must still validate the
    # resulting day against the new month/year
    error = ''
    try:
        datetime.date(2024, 1, 31).replace(month=4)
    except ValueError as e:
        error = str(e)
    assert error == 'day is out of range for month'

    error = ''
    try:
        datetime.date(2024, 2, 29).replace(year=2023)
    except ValueError as e:
        error = str(e)
    assert error == 'day is out of range for month'

    # sanity: still works fine when the resulting day is valid
    assert datetime.date(2024, 1, 15).replace(month=4) == datetime.date(2024, 4, 15)


def test_datetime_replace_keywords():
    # each single keyword argument must actually update that field, and
    # leave every other field untouched
    dt = datetime.datetime(2024, 1, 15, 10, 30, 20, 123)

    assert dt.replace(year=2025) == datetime.datetime(2025, 1, 15, 10, 30, 20, 123)
    assert dt.replace(month=6) == datetime.datetime(2024, 6, 15, 10, 30, 20, 123)
    assert dt.replace(day=20) == datetime.datetime(2024, 1, 20, 10, 30, 20, 123)
    assert dt.replace(hour=5) == datetime.datetime(2024, 1, 15, 5, 30, 20, 123)
    assert dt.replace(minute=1) == datetime.datetime(2024, 1, 15, 10, 1, 20, 123)
    assert dt.replace(second=2) == datetime.datetime(2024, 1, 15, 10, 30, 2, 123)
    assert dt.replace(microsecond=9) == datetime.datetime(2024, 1, 15, 10, 30, 20, 9)

    # multiple keywords at once
    assert dt.replace(day=1, hour=0) == datetime.datetime(2024, 1, 1, 0, 30, 20, 123)

    # positional args still work
    assert dt.replace(2025, 6, 10) == datetime.datetime(2025, 6, 10, 10, 30, 20, 123)

    # resulting invalid day must still raise, even though day wasn't itself
    # a replace() keyword
    error = ''
    try:
        datetime.datetime(2024, 1, 31, 10, 30).replace(month=4)
    except ValueError as e:
        error = str(e)
    assert error == 'day is out of range for month'


def test_time_replace_keywords():
    t = datetime.time(10, 30, 20, 123)
    assert t.replace(hour=5) == datetime.time(5, 30, 20, 123)
    assert t.replace(minute=1) == datetime.time(10, 1, 20, 123)
    assert t.replace(second=2) == datetime.time(10, 30, 2, 123)
    assert t.replace(microsecond=9) == datetime.time(10, 30, 20, 9)
    assert t.replace(hour=1, second=2) == datetime.time(1, 30, 2, 123)


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

class UTC0(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)


def test_datetime_timestamp_aware():
    tol = 1e-6

    # offset-aware: result is independent of the platform/local timezone
    dt = datetime.datetime(2007, 4, 3, tzinfo=TZ2())
    assert abs(dt.timestamp() - 1175578740.0) < tol

    # a zero-offset ("UTC") tzinfo reproduces the epoch exactly
    assert datetime.datetime(1970, 1, 1, tzinfo=UTC0()).timestamp() == 0.0

    # fractional seconds and non-epoch dates
    dt2 = datetime.datetime(2024, 2, 29, 23, 59, 59, 500000, tzinfo=UTC0())
    assert abs(dt2.timestamp() - 1709251199.5) < tol


def test_datetime_timestamp_naive_roundtrip():
    # naive timestamp() interprets the wall-clock fields as local time,
    # so it should be the exact inverse of fromtimestamp() regardless of
    # which platform/timezone the test runs under. Pick a date well away
    # from any DST transition to keep the round trip unambiguous.
    dt = datetime.datetime(2023, 6, 15, 14, 30, 0)
    ts = dt.timestamp()
    assert datetime.datetime.fromtimestamp(ts) == dt


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


def test_date_arithmetic():
    # regression test: for __add__, both operands used to be converted to
    # the union of their types, so that element types get unified (e.g.
    # [1] + [1.0] -> list<double>). for unrelated operand classes such as
    # date and timedelta there is no such common type, so both sides were
    # cast to 'pyobj *' -- which has no __add__ at all (compile error).
    # __sub__ never went through that conversion, and always worked.
    d = datetime.date(2024, 1, 1)
    td = datetime.timedelta(days=30)

    assert d + td == datetime.date(2024, 1, 31)
    assert d - td == datetime.date(2023, 12, 2)

    # across a leap day
    assert datetime.date(2024, 2, 28) + datetime.timedelta(days=1) == \
        datetime.date(2024, 2, 29)
    # across a year boundary
    assert datetime.date(2023, 12, 31) + datetime.timedelta(days=1) == \
        datetime.date(2024, 1, 1)
    # negative timedelta
    assert d + datetime.timedelta(days=-1) == datetime.date(2023, 12, 31)

    # date - date still yields a timedelta
    assert (datetime.date(2024, 3, 1) - d).days == 60


def test_datetime_arithmetic():
    dt = datetime.datetime(2024, 1, 1, 10, 30, 0)

    assert dt + datetime.timedelta(days=1) == datetime.datetime(2024, 1, 2, 10, 30, 0)
    assert dt + datetime.timedelta(hours=2) == datetime.datetime(2024, 1, 1, 12, 30, 0)
    # carry over midnight
    assert dt + datetime.timedelta(hours=14) == datetime.datetime(2024, 1, 2, 0, 30, 0)
    assert dt - datetime.timedelta(minutes=45) == datetime.datetime(2024, 1, 1, 9, 45, 0)

    # datetime - datetime still yields a timedelta
    delta = datetime.datetime(2024, 1, 2, 10, 30, 0) - dt
    assert delta.days == 1
    assert delta.seconds == 0


def test_timedelta_arithmetic():
    a = datetime.timedelta(days=1, seconds=30)
    b = datetime.timedelta(hours=12)

    assert a + b == datetime.timedelta(days=1, seconds=43230)
    assert a - b == datetime.timedelta(seconds=43230)
    assert a + a == datetime.timedelta(days=2, seconds=60)
    assert a - a == datetime.timedelta()


def test_datetime_isoformat():
    # regression test: isoformat()'s 'sep' parameter used to be given a
    # non-empty string default ('T'), which the code generator could not
    # resolve for this module (compile error: 'default_N' is not a member
    # of '__datetime__') when the call site omitted the argument.
    dt = datetime.datetime(2023, 5, 17, 10, 30, 0)
    assert dt.isoformat() == '2023-05-17T10:30:00'
    assert dt.isoformat(' ') == '2023-05-17 10:30:00'
    assert dt.isoformat(sep='|') == '2023-05-17|10:30:00'

    dt2 = datetime.datetime(2023, 5, 17, 10, 30, 0, 123456)
    assert dt2.isoformat() == '2023-05-17T10:30:00.123456'

    error = ''
    try:
        dt.isoformat('too long')
    except TypeError:
        error = 'TypeError'
    assert error == 'TypeError'


def test_date_repr():
    assert repr(datetime.date(2024, 3, 1)) == 'datetime.date(2024, 3, 1)'
    assert repr(datetime.date(1, 1, 1)) == 'datetime.date(1, 1, 1)'


def test_time_repr():
    # trailing zero second/microsecond are omitted, same as cpython
    assert repr(datetime.time(10, 30)) == 'datetime.time(10, 30)'
    assert repr(datetime.time(0, 0)) == 'datetime.time(0, 0)'
    assert repr(datetime.time(1, 2, 3)) == 'datetime.time(1, 2, 3)'
    assert repr(datetime.time(1, 2, 0, 4)) == 'datetime.time(1, 2, 0, 4)'
    assert repr(datetime.time(1, 2, 3, 4)) == 'datetime.time(1, 2, 3, 4)'


def test_datetime_repr():
    assert repr(datetime.datetime(2024, 1, 2)) == 'datetime.datetime(2024, 1, 2, 0, 0)'
    assert repr(datetime.datetime(2024, 1, 1, 10, 30)) == 'datetime.datetime(2024, 1, 1, 10, 30)'
    assert repr(datetime.datetime(2024, 1, 2, 3, 4, 5)) == 'datetime.datetime(2024, 1, 2, 3, 4, 5)'
    assert repr(datetime.datetime(2024, 1, 2, 3, 4, 0, 6)) == 'datetime.datetime(2024, 1, 2, 3, 4, 0, 6)'


def test_timedelta_repr():
    # keyword form with zero fields omitted (cpython >= 3.7)
    assert repr(datetime.timedelta()) == 'datetime.timedelta(0)'
    assert repr(datetime.timedelta(days=1)) == 'datetime.timedelta(days=1)'
    assert repr(datetime.timedelta(seconds=30, microseconds=5)) == \
        'datetime.timedelta(seconds=30, microseconds=5)'
    # normalized representation, not the constructor arguments
    assert repr(datetime.timedelta(days=-1, hours=1)) == 'datetime.timedelta(days=-1, seconds=3600)'
    assert repr(datetime.timedelta(hours=25)) == 'datetime.timedelta(days=1, seconds=3600)'


def test_date_hash():
    # regression test: date/datetime/time/timedelta used to inherit pyobj's
    # pointer-identity __hash__, so equal values were distinct set members
    # and dict keys
    d1 = datetime.date(2024, 3, 1)
    d2 = datetime.date(2024, 3, 1)
    d3 = datetime.date(2023, 1, 1)
    assert hash(d1) == hash(d2)
    assert hash(d1) != hash(d3)
    assert len(set([d1, d2, d3])) == 2
    assert d2 in {d1: 1}
    assert {d1: 1, d2: 2}[d1] == 2


def test_datetime_hash():
    a = datetime.datetime(2024, 1, 1, 10, 30)
    b = datetime.datetime(2024, 1, 1, 10, 30)
    c = datetime.datetime(2024, 1, 1, 10, 30, 0, 1)
    assert hash(a) == hash(b)
    assert hash(a) != hash(c)
    assert len(set([a, b, c])) == 2
    assert b in {a: 1}


def test_time_hash():
    a = datetime.time(10, 30)
    b = datetime.time(10, 30)
    c = datetime.time(10, 31)
    assert hash(a) == hash(b)
    assert hash(a) != hash(c)
    assert len(set([a, b, c])) == 2
    assert b in {a: 1}


def test_timedelta_hash():
    a = datetime.timedelta(days=1)
    b = datetime.timedelta(hours=24)
    c = datetime.timedelta(days=2)
    assert hash(a) == hash(b)
    assert hash(a) != hash(c)
    assert len(set([a, b, c])) == 2
    assert b in {a: 1}


def test_datetime_hash_aware():
    # aware datetimes compare by their utc equivalent, so equal instants
    # with different offsets must hash the same (consistent with __eq__)
    a = datetime.datetime(2007, 4, 3, 0, 0, tzinfo=UTC0())
    b = datetime.datetime(2007, 4, 2, 18, 21, tzinfo=TZ2())  # utc-5:39
    assert a == b
    assert hash(a) == hash(b)
    assert len(set([a, b])) == 1


def test_date_sorting():
    d1 = datetime.date(2024, 3, 1)
    d2 = datetime.date(2023, 1, 1)
    d3 = datetime.date(2024, 2, 29)
    assert sorted([d1, d2, d3]) == [d2, d3, d1]
    assert min([d1, d2, d3]) == d2
    assert max([d1, d2, d3]) == d1
    assert d2 < d3 < d1
    assert d1 >= d3 >= d2
    assert d1 <= datetime.date(2024, 3, 1)
    assert d1 != d3


def test_datetime_sorting():
    a = datetime.datetime(2024, 1, 1, 10, 30)
    b = datetime.datetime(2024, 1, 1, 10, 31)
    c = datetime.datetime(2024, 1, 2)
    assert sorted([c, b, a]) == [a, b, c]
    assert min([c, b, a]) == a
    assert max([c, b, a]) == c


def test_time_sorting():
    a = datetime.time(1, 2, 3)
    b = datetime.time(1, 2, 3, 4)
    c = datetime.time(10, 0)
    assert sorted([c, b, a]) == [a, b, c]
    assert a < b < c
    assert c > b > a
    assert a <= datetime.time(1, 2, 3) <= a


def test_timedelta_sorting():
    a = datetime.timedelta(seconds=1)
    b = datetime.timedelta(days=1)
    c = datetime.timedelta(days=1, microseconds=1)
    assert sorted([c, b, a]) == [a, b, c]
    assert a < b < c
    assert c >= b >= a
    assert datetime.timedelta(hours=24) == b


def test_class_attributes():
    assert datetime.date.min == datetime.date(datetime.MINYEAR, 1, 1)
    assert datetime.date.max == datetime.date(datetime.MAXYEAR, 12, 31)
    assert datetime.date.resolution == datetime.timedelta(days=1)

    assert datetime.datetime.min == datetime.datetime(datetime.MINYEAR, 1, 1)
    assert datetime.datetime.max == datetime.datetime(datetime.MAXYEAR, 12, 31, 23, 59, 59, 999999)
    assert datetime.datetime.resolution == datetime.timedelta(microseconds=1)

    assert datetime.time.min == datetime.time(0, 0)
    assert datetime.time.max == datetime.time(23, 59, 59, 999999)
    assert datetime.time.resolution == datetime.timedelta(microseconds=1)

    assert datetime.timedelta.min == datetime.timedelta(days=-999999999)
    assert datetime.timedelta.max == datetime.timedelta(days=999999999, hours=23, minutes=59, seconds=59, microseconds=999999)
    assert datetime.timedelta.resolution == datetime.timedelta(microseconds=1)

    assert str(datetime.date.min) == '0001-01-01'
    assert str(datetime.datetime.max) == '9999-12-31 23:59:59.999999'
    assert repr(datetime.timedelta.max) == \
        'datetime.timedelta(days=999999999, seconds=86399, microseconds=999999)'

    # bounds are actually usable as bounds
    assert datetime.date.min <= datetime.date(2024, 1, 1) <= datetime.date.max
    assert datetime.timedelta.min < datetime.timedelta() < datetime.timedelta.max


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
        test_datetime_timestamp_aware()
        test_datetime_timestamp_naive_roundtrip()
        test_datetime_isoformat()
        test_date_arithmetic()
        test_datetime_arithmetic()
        test_timedelta_arithmetic()
        test_timedelta_total_seconds()
        test_timedelta_floordiv()
        test_timedelta_truediv()
        test_date_replace_keeps_unchanged_day_out_of_range()
        test_datetime_replace_keywords()
        test_time_replace_keywords()
        test_date_repr()
        test_time_repr()
        test_datetime_repr()
        test_timedelta_repr()
        test_date_hash()
        test_datetime_hash()
        test_time_hash()
        test_timedelta_hash()
        test_datetime_hash_aware()
        test_date_sorting()
        test_datetime_sorting()
        test_time_sorting()
        test_timedelta_sorting()
        test_class_attributes()

if __name__ == "__main__":
    test_all()
