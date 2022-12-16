import os.path
from os.path import *
import os

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

    if not exists("testdata"):
        testdata = "../testdata"
    else:
        testdata = "testdata"

    assert exists(testdata)
    assert lexists(testdata)
    assert isdir(testdata)
    assert not isfile(testdata)

    if not exists("test_hello.py"):
        test_hello = "../test_hello.py"
    else:
        test_hello = "test_hello.py"

    assert getsize(test_hello) == 23
    assert getatime(test_hello) > 1 # dummy: cannot test for time
    assert getctime(test_hello) > 1 # dummy: cannot test for time
    assert getmtime(test_hello) > 1 # dummy: cannot test for time



if __name__ == '__main__':
    test_os_path_join()
    test_os_path()


