import time


def test_time():

    assert time.strftime(
        "%d %b %Y %H:%M:%S", time.strptime(
            "2001-11-12 18:31:01", "%Y-%m-%d %H:%M:%S")
    ) == "12 Nov 2001 18:31:01"

    assert time.strftime("%Y", time.strptime("2001", "%Y")) == '2001'
    assert time.mktime(time.struct_time((1970, 2, 17, 23, 33, 34, 1, 48, -1))) == 4131214.0
    assert time.mktime((1970, 2, 17, 23, 33, 34, 3, 17, -1)) == 4131214.0
    
    t = time.localtime(4142014)
    assert t.tm_year == 1970
    assert t.tm_mon == 2
    assert t.tm_mday == 18
    assert t.tm_sec == 34

    assert time.asctime(time.struct_time((2008, 6, 24, 12, 50, 00, 0, 120, -1))) == 'Mon Jun 24 12:50:00 2008'
    assert time.ctime(1000000) == 'Mon Jan 12 17:46:40 1970'
    assert time.strftime("%a, %d %b %Y %H:%M:%S", (2008, 6, 24, 12, 50, 00, 0, 120, -1)) == 'Mon, 24 Jun 2008 12:50:00'
    assert len(time.tzname) == 2

def test_all():
    test_time()

if __name__ == '__main__':
    test_all() 


