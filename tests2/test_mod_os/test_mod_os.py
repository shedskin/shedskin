import os


def test_os():
    os.getcwd()

def test_os_exception():
    try:
        os.chdir("ontehunoe")
    except FileNotFoundError as e:
        assert e.errno == 2
        assert e.filename == "ontehunoe"


if __name__ == '__main__':
    test_os()
    # test_os_exception()
