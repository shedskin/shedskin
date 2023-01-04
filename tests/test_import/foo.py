from bar import Bar


class Foo:
    """a foo class"""

    def __init__(self):
        self.bar = Bar()

    def name(self):
        return self.bar.name()
