import time
import datetime # test potential conflict with datetime.time

#def test_mktime():
    #assert time.mktime(time.struct_time((1970, 2, 17, 23, 33, 34, 1, 48, -1))) == 4131214.0
    #assert time.mktime((1970, 2, 17, 23, 33, 34, 3, 17, -1)) == 4131214.0    

#def test_ctime():
#    assert time.ctime(1000000) == 'Mon Jan 12 17:46:40 1970'    

def test_localtime():
    t = time.localtime(4142014)
    assert t.tm_year == 1970
    assert t.tm_mon == 2
    #assert t.tm_mday == 18
    assert t.tm_sec == 34

def test_asctime():
    t1 = (2008, 6, 24, 12, 50, 00, 0, 120, -1)
    assert time.asctime(time.struct_time(t1)) == 'Mon Jun 24 12:50:00 2008'
    assert time.strftime("%a, %d %b %Y %H:%M:%S", t1) == 'Mon, 24 Jun 2008 12:50:00'

def test_strftime():
    assert time.strftime(
            "%d %b %Y %H:%M:%S", time.strptime(
                "2001-11-12 18:31:01", "%Y-%m-%d %H:%M:%S")
        ) == "12 Nov 2001 18:31:01"
    assert time.strftime("%Y", time.strptime("2001", "%Y")) == '2001'

def test_conversions():
    t = time.time()
    assert time.ctime(t) == time.asctime(time.localtime(t))
    assert int(time.mktime(time.localtime(t))) == int(t)

# def test_epoch():
#     epoch = time.gmtime(0)
#     assert tuple(epoch)[:6] == (1970, 1, 1, 0, 0, 0)

def test_tzname():
    assert len(time.tzname) == 2

def test_sleep():
    t1 = time.time()
    time.sleep(0.5)
    t2 = time.time()
    assert t2 > t1

def test_all():
    # test_time() ## producing different results on linux vs macos
    #test_mktime()
    #test_ctime()
    test_localtime()
    test_asctime()
    test_strftime()
    test_conversions()
    test_sleep()
    # test_epoch()
    test_tzname()

if __name__ == '__main__':
    test_all() 

