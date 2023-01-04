from spam import Spam


class Bar:
    """a bar class"""

    def __init__(self):
        self.spam = Spam()

    def name(self):
        return self.spam.name()
