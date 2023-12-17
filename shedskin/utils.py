"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2023 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)
"""

# terminal codes
MOVE = "\x1b[1G"
BOLD = "\x1b[1m"
WHITE = "\x1b[97;20m"
GREY = "\x1b[38;20m"
GREEN = "\x1b[32;20m"
CYAN = "\x1b[36;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
RED_BOLD = "\x1b[31;1m"
RESET = "\x1b[0m"


def bold(txt):
    return f"{BOLD}{txt}{RESET}"


class ProgressBar:
    """Displays or updates a console progress bar in-place.

    Improved on original in https://stackoverflow.com/a/15860757/1391441

    >>> pbar = ProgressBar(done_sym='█', left_sym='░')
    >>> for i in range(101):
    >>>     pbar.update(i)
    """

    def __init__(
        self, total=100, prefix="processing", bar_length=33, done_sym="#", left_sym="-"
    ):
        self.total = total
        self.prefix = prefix
        self.bar_length = bar_length
        self.done_sym = done_sym
        self.left_sym = left_sym
        self.progress = 0.0
        self.done = False

    def update(self, n):
        if self.done:
            return

        self.progress = float(n) / float(self.total)
        if self.progress >= 1.0:
            self.progress = 1
            self.done = True

        block = int(round(self.bar_length * self.progress))
        text = "\r>> {} [{}] {:.0f}% ".format(
            self.prefix,
            self.done_sym * block + self.left_sym * (self.bar_length - block),
            round(self.progress * 100, 0),
        )
        print(text, end="\r", flush=True)
        if self.done:
            print(flush=True)
