"""
import chain: Eggs <- Foo <- Bar <- Spam

"""


from foo import Foo


class Eggs:
    def __init__(self):
        self.foo = Foo()

    def name(self):
        return self.foo.name()


def test_imports():
    eggs = Eggs()
    # print(eggs.name())
    assert eggs.name() == "hello"


def test_all():
    test_imports()


if __name__ == "__main__":
    test_all()
