

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


def command(s):
    match s:
        case "start" | "go":
            return 1
        case "stop" | "quit" | "exit":
            return 2
        case "":
            return 3
    return 0


def test_match_str_or():
    assert command("start") == 1
    assert command("go") == 1
    assert command("quit") == 2
    assert command("exit") == 2
    assert command("") == 3
    assert command("bla") == 0


def sign(x):
    match x:
        case -1:
            return "neg"
        case 0:
            return "zero"
        case 1:
            return "pos"
    return "?"


def test_match_negative():
    assert sign(-1) == "neg"
    assert sign(0) == "zero"
    assert sign(1) == "pos"
    assert sign(2) == "?"


def test_match_float():
    x = 2.5
    match x:
        case 1.5:
            r = 1
        case 2.5:
            r = 2
        case _:
            r = 3
    assert r == 2


class Color:
    RED = 0
    GREEN = 1
    BLUE = 2


def color_name(c):
    match c:
        case Color.RED:
            return "red"
        case Color.GREEN | Color.BLUE:
            return "green or blue"
        case _:
            return "unknown"


def test_match_dotted():
    assert color_name(Color.RED) == "red"
    assert color_name(Color.GREEN) == "green or blue"
    assert color_name(Color.BLUE) == "green or blue"
    assert color_name(7) == "unknown"


def opt(s):
    match s:
        case None:
            return "none"
        case "":
            return "empty"
        case _:
            return s


def boolname(b):
    match b:
        case True:
            return "yes"
        case False:
            return "no"
    return "?"


def test_match_singleton():
    assert opt(None) == "none"
    assert opt("") == "empty"
    assert opt("x") == "x"
    assert boolname(True) == "yes"
    assert boolname(False) == "no"


def classify(n, strict):
    match n:
        case 0 | 1 if strict:
            return "small strict"
        case 0 | 1:
            return "small"
        case _ if n < 0:
            return "negative"
        case _:
            return "large"


def test_match_guard():
    assert classify(0, True) == "small strict"
    assert classify(1, False) == "small"
    assert classify(-5, True) == "negative"
    assert classify(5, True) == "large"


calls = []


def subject(x):
    calls.append(x)
    return x


def test_match_subject_once():
    match subject(3):
        case 1:
            r = 1
        case 2:
            r = 2
        case 3:
            r = 3
        case _:
            r = 4
    assert r == 3
    assert calls == [3]


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Points:
    UNIT = Point(1, 1)


def test_match_user_eq():
    match Point(1, 1):
        case Points.UNIT:
            r = "unit"
        case _:
            r = "other"
    assert r == "unit"


def test_match_loop():
    result = []
    for i in range(6):
        match i:
            case 1:
                continue
            case 4:
                break
            case _:
                result.append(i)
    assert result == [0, 2, 3]


def test_match_nested():
    result = []
    for a in range(3):
        for b in range(2):
            match a:
                case 0:
                    match b:
                        case 0:
                            result.append("00")
                        case _:
                            result.append("0x")
                case 2:
                    result.append("2")
    assert result == ["00", "0x", "2", "2"]


def test_match_only_wildcard():
    match 7:
        case _:
            r = 1
    assert r == 1


g = 0
match "b":
    case "a":
        g = 1
    case "b":
        g = 2


def test_match_global():
    assert g == 2


def test_all():
    test_match()
    test_match_str_or()
    test_match_negative()
    test_match_float()
    test_match_dotted()
    test_match_singleton()
    test_match_guard()
    test_match_subject_once()
    test_match_user_eq()
    test_match_loop()
    test_match_nested()
    test_match_only_wildcard()
    test_match_global()

if __name__ == '__main__':
    test_all()
