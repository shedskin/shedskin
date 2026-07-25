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


def test_all():
        test_date()
        test_date_day_out_of_range()
        test_datetime_basic()
        test_datetime_custom_tzinfo()
        test_timedelta_total_seconds()

if __name__ == "__main__":
    test_all()
