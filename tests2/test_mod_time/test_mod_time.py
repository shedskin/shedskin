import time


def test_time():

    assert time.strftime(
        "%d %b %Y %H:%M:%S", time.strptime(
            "2001-11-12 18:31:01", "%Y-%m-%d %H:%M:%S")
    ) == "12 Nov 2001 18:31:01"

    assert time.strftime("%Y", time.strptime("2001", "%Y")) == '2001'



def test_all():
    test_time()

if __name__ == '__main__':
    test_all() 


