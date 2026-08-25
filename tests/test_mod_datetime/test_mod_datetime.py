import datetime



def test_date():
    assert datetime.date(2007, 4, 3).replace(month=11) == datetime.date(2007, 11, 3)

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
        test_date_day_out_of_range()
        test_date_compare_year_boundary()
        test_datetime_compare_year_boundary()
        test_datetime_basic()
        test_datetime_custom_tzinfo()
        test_timedelta_total_seconds()
        test_timedelta_floordiv()
        test_timedelta_truediv()
        test_date_replace_keeps_unchanged_day_out_of_range()
        test_datetime_replace_keywords()
        test_time_replace_keywords()

if __name__ == "__main__":
    test_all()
