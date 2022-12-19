
from getopt import getopt, gnu_getopt

args = ["-ahoei", "--alpha=4", "meuk"]

def test_getopt():
    assert getopt(args, "a:b", ["alpha=", "beta"]) == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert getopt(args, "a:b", {"alpha=": 0, "beta": 0}) == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert gnu_getopt(args, "a:b", ["alpha=", "beta"]) == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert gnu_getopt(args, "a:b", {"alpha=": 0, "beta": 0}) == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert getopt(args, "a:b", "alpha=") == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])
    assert gnu_getopt(args, "a:b", "alpha=") == ([('-a', 'hoei'), ('--alpha', '4')], ['meuk'])

def test_all():
    test_getopt()

if __name__ == '__main__':
    test_all()