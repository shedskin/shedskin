


def test_key_error():
    error = False
    try:
        try:
            {1: 2}[3]
        except KeyError as e:
            raise e
    except KeyError as m:
        error = True
    assert error


def test_type_error():
    error = False
    try:
        1 + 'a'
    except TypeError as m:
        error = True
    assert error


def test_all():
    test_key_error()
    # test_type_error()


if __name__ == '__main__':
    test_all() 
