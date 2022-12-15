import os.path
from os.path import *

def test_os_path_join():
    assert os.path.join("heuk") == 'heuk'
    assert os.path.join("heuk", "emeuk") == 'heuk/emeuk'
    assert os.path.join("heuk", "emeuk", "meuk") == 'heuk/emeuk/meuk'
    assert os.path.join("a", "b", "c") == 'a/b/c'

def test_os_path():
    assert commonprefix(["xxx", "xxxx"]) == 'xxx'
    assert normcase("hoei") == 'hoei'
    assert splitext("hoei/woei") == ('hoei/woei', '')
    assert splitdrive("hoei/woei") == ('', 'hoei/woei')
    assert basename("hoei/woei") == 'woei'
    assert dirname("hoei/woei") == 'hoei'
    assert exists("testdata")
    assert lexists("testdata")
    assert isdir("testdata")
    assert not isfile("testdata")
    # assert getsize('test_hello.py') == 23
    # assert getatime("test_hello.py") > 1 # dummy: cannot test for time
    # assert getctime("test_hello.py") > 1 # dummy: cannot test for time
    # assert getmtime("test_hello.py") > 1 # dummy: cannot test for time



if __name__ == '__main__':
    test_os_path_join()
    test_os_path()


