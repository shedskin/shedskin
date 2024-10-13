# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.__main__: commandline entrypoint

Provides the command-line interface to the shedskin compiler.
"""

from . import Shedskin


def run() -> None:
    """Run the shedskin compiler from the command line"""
    Shedskin.commandline()


if __name__ == "__main__":
    run()
