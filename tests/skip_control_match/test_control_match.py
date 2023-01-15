

def http_error(status):
    # example
    # from: https://stackoverflow.com/questions/11479816/what-is-the-python-equivalent-for-a-case-switch-statement
    match status:
        case 400:
            return "Bad request"
        case 404:
            return "Not found"
        case 418:
            return "I'm a teapot"

        # If an exact match is not confirmed, this last case will be used if provided
        case _:
            return "Something's wrong with the internet"


def test_match():
    assert http_error(400) == "Bad request"
    assert http_error(404) == "Not found"
    assert http_error(418) == "I'm a teapot"
    assert http_error(500) == "Something's wrong with the internet"


def test_all():
    test_match()

if __name__ == '__main__':
    test_all() 
