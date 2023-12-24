import os


def test_popen():
    # https://github.com/shedskin/shedskin/issues/191
    assert os.popen("echo Hello World").read() == 'Hello World\n'


def test_os():
    os.getcwd()


def test_os_exception():
    try:
        os.chdir("ontehunoe")
    except FileNotFoundError as e:
        assert e.errno == 2
        assert e.filename == "ontehunoe"


def test_all():
    test_os()
    # test_popen()  # TODO windows
    test_os_exception()


if __name__ == '__main__':
    test_all()
