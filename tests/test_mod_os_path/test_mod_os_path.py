import os.path
from os.path import *
import os

def test_os_path_join():
    assert os.path.join("heuk") == 'heuk'
    assert os.path.join("heuk", "emeuk") == 'heuk/emeuk'.replace('/', os.sep)
    assert os.path.join("heuk", "emeuk", "meuk") == 'heuk/emeuk/meuk'.replace('/', os.sep)
    assert os.path.join("a", "b", "c") == 'a/b/c'.replace('/', os.sep)

def test_os_path():
    assert commonprefix(["xxx", "xxxx"]) == 'xxx'
    assert normcase("hoei") == 'hoei'
    assert splitext("hoei/woei") == ('hoei/woei', '')
    assert splitdrive("hoei/woei") == ('', 'hoei/woei')
    assert basename("hoei/woei") == 'woei'
    assert dirname("hoei/woei") == 'hoei'

    if exists("testdata"):
        testdata = "testdata"
    elif exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"

    assert exists(testdata)
    assert lexists(testdata)
    assert isdir(testdata)
    assert not isfile(testdata)

    abc = join(testdata, "abc.txt")

    assert getsize(abc) in (5, 7)

    assert getatime(abc) > 1 # dummy: cannot test for time
    assert getctime(abc) > 1 # dummy: cannot test for time
    assert getmtime(abc) > 1 # dummy: cannot test for time



def test_all():
    test_os_path_join()
    test_os_path()

if __name__ == '__main__':
    test_all()

