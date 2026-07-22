import time

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

def test_perf_counter():
    t1 = time.perf_counter()
    time.sleep(0.1)
    t2 = time.perf_counter()
    assert t2 > t1
    assert (t2 - t1) >= 0.09

def test_monotonic():
    t1 = time.monotonic()
    time.sleep(0.1)
    t2 = time.monotonic()
    assert t2 > t1
    assert (t2 - t1) >= 0.09

def test_process_time():
    p1 = time.process_time()
    x = 0
    for i in range(1000000):
        x += i * i
    p2 = time.process_time()
    # cpu time should never go backwards
    assert p2 >= p1
    print(x)

def test_isdst_attribute():
    t = time.localtime(0)
    # regression test: struct_time must expose tm_isdst (not "isdst")
    assert t.tm_isdst == -1 or t.tm_isdst == 0 or t.tm_isdst == 1

def test_len():
    # regression test: struct_time is a 9-sequence, len() must reflect that
    # (previously fell back to pyobj's default __len__, which is always 1)
    t = time.gmtime(1700000000)
    assert len(t) == 9

def test_eq_and_ordering():
    # regression test: struct_time must compare by value, not by identity
    # (previously fell back to pyobj's default __eq__/__cmp__)
    t1 = time.gmtime(1700000000)
    t2 = time.gmtime(1700000000)
    t3 = time.gmtime(1700000100)
    assert t1 == t2
    assert not (t1 == t3)
    assert t1 < t3
    assert not (t3 < t1)
    assert t3 > t1

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
    test_perf_counter()
    test_monotonic()
    test_process_time()
    test_isdst_attribute()
    test_len()
    test_eq_and_ordering()

if __name__ == '__main__':
    test_all() 

