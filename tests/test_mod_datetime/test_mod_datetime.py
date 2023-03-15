import datetime



def test_date():
    assert datetime.date(2007, 4, 3).replace(month=11) == datetime.date(2007, 11, 3)

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



def test_all():
        test_date()
        test_datetime_basic()
        test_datetime_custom_tzinfo()

if __name__ == "__main__":
    test_all()
