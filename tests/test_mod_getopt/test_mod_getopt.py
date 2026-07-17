
import os
from getopt import getopt, gnu_getopt, GetoptError, error

args = ["-ahoei", "--alpha=4", "meuk"]

def test_getopt():
    assert getopt(args, "a:b", ["alpha=", "beta"]) == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert getopt(args, "a:b", {"alpha=": 0, "beta": 0}) == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert gnu_getopt(args, "a:b", ["alpha=", "beta"]) == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert gnu_getopt(args, "a:b", {"alpha=": 0, "beta": 0}) == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert getopt(args, "a:b", "alpha=") == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert gnu_getopt(args, "a:b", "alpha=") == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])


def test_getopt_stops_at_first_nonoption():
    # plain getopt() should stop scanning as soon as it hits a
    # non-option argument, leaving the rest (including a bare '-')
    # untouched in the returned args list.
    opts, rest = getopt(["-a", "foo", "-b"], "ab")
    assert opts == [('-a', '')]
    assert rest == ["foo", "-b"]

    opts, rest = getopt(["-", "foo"], "a")
    assert opts == []
    assert rest == ["-", "foo"]


def test_gnu_getopt_lone_dash_is_not_an_option():
    # a bare '-' is a conventional placeholder (e.g. "read from stdin")
    # and must be preserved as a positional argument, not consumed as
    # a short option.
    opts, rest = gnu_getopt(["-", "foo", "-a"], "a")
    assert opts == [('-a', '')]
    assert rest == ["-", "foo"]

    # it should also be preserved in isolation
    opts, rest = gnu_getopt(["-"], "a")
    assert opts == []
    assert rest == ["-"]

    # ... and when it's the only thing on the command line alongside
    # real options on both sides
    opts, rest = gnu_getopt(["-a", "-", "-a"], "a")
    assert opts == [('-a', ''), ('-a', '')]
    assert rest == ["-"]


def test_gnu_getopt_intermixed():
    opts, rest = gnu_getopt(["foo", "-a", "bar", "-b"], "ab")
    assert opts == [('-a', ''), ('-b', '')]
    assert rest == ["foo", "bar"]


def test_gnu_getopt_plus_stops_at_first_nonoption():
    opts, rest = gnu_getopt(["foo", "-a", "bar"], "+a")
    assert opts == []
    assert rest == ["foo", "-a", "bar"]


def test_double_dash_terminator():
    opts, rest = getopt(["-a", "--", "-b", "foo"], "ab")
    assert opts == [('-a', '')]
    assert rest == ["-b", "foo"]

    opts, rest = gnu_getopt(["-a", "--", "-b", "foo"], "ab")
    assert opts == [('-a', '')]
    assert rest == ["-b", "foo"]


def test_short_option_clusters():
    # required-arg option in the middle of a cluster consumes the
    # remainder of the cluster as its argument
    opts, rest = getopt(["-xab"], "x:y")
    assert opts == [('-x', 'ab')]
    assert rest == []

    # required-arg option at the end pulls its value from the next arg
    opts, rest = getopt(["-a", "value"], "a:")
    assert opts == [('-a', 'value')]
    assert rest == []

    # a cluster of plain flags
    opts, rest = getopt(["-abc"], "abc")
    assert opts == [('-a', ''), ('-b', ''), ('-c', '')]
    assert rest == []


def test_long_option_prefix_matching():
    opts, rest = getopt(["--foo"], "", ["foo", "foobar"])
    assert opts == [('--foo', '')]
    assert rest == []

    error_msg = None
    error_opt = None
    try:
        getopt(["--fo"], "", ["foo", "foobar"])
    except GetoptError as e:
        error_msg = e.msg
        error_opt = e.opt
    assert error_msg == "option --fo not a unique prefix"
    assert error_opt == "fo"


def test_getopt_error_messages():
    error_msg = None
    error_opt = None
    try:
        getopt(["-a"], "a:")
    except GetoptError as e:
        error_msg = e.msg
        error_opt = e.opt
    assert error_msg == "option -a requires argument"
    assert error_opt == "a"

    error_msg = None
    error_opt = None
    try:
        getopt(["-z"], "a")
    except GetoptError as e:
        error_msg = e.msg
        error_opt = e.opt
    assert error_msg == "option -z not recognized"
    assert error_opt == "z"


def test_long_option_error_messages():
    error_msg = None
    try:
        getopt(["--foo"], "", ["foo="])
    except GetoptError as e:
        error_msg = e.msg
    assert error_msg == "option --foo requires argument"

    error_msg = None
    try:
        getopt(["--foo=1"], "", ["foo"])
    except GetoptError as e:
        error_msg = e.msg
    assert error_msg == "option --foo must not have an argument"

    error_msg = None
    try:
        getopt(["--zzz"], "", ["foo"])
    except GetoptError as e:
        error_msg = e.msg
    assert error_msg == "option --zzz not recognized"


def test_error_alias_catches_getopterror():
    # 'error' is an alias for GetoptError and should be catchable
    # the same way real getopt.error is in CPython.
    caught = False
    try:
        getopt(["-z"], "a")
    except error as e:
        caught = True
        assert e.msg == "option -z not recognized"
    assert caught


def test_posixly_correct_env():
    os.environ["POSIXLY_CORRECT"] = "1"
    opts, rest = gnu_getopt(["foo", "-a", "bar"], "a")
    assert opts == []
    assert rest == ["foo", "-a", "bar"]
    del os.environ["POSIXLY_CORRECT"]


def test_all():
    test_getopt()
    test_getopt_stops_at_first_nonoption()
    test_gnu_getopt_lone_dash_is_not_an_option()
    test_gnu_getopt_intermixed()
    test_gnu_getopt_plus_stops_at_first_nonoption()
    test_double_dash_terminator()
    test_short_option_clusters()
    test_long_option_prefix_matching()
    test_getopt_error_messages()
    test_long_option_error_messages()
    test_error_alias_catches_getopterror()
    test_posixly_correct_env()

if __name__ == '__main__':
    test_all()
