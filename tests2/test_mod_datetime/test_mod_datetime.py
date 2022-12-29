import datetime

def test_datetime_basic():
    assert datetime.MAXYEAR == 9999
    assert datetime.MINYEAR == 1

    a = datetime.datetime.now()
    b = datetime.datetime.now()
    assert a < b

    assert datetime.datetime.utcnow().date().year > 2020


def test_all():
    test_datetime_basic()


if __name__ == "__main__":
    test_all()
