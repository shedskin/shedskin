"""
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2023 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)
"""

import logging

from . import utils


class ShedskinFormatter(logging.Formatter):
    def __init__(self, datefmt=None):
        self._info_formatter = logging.Formatter(
            utils.MOVE + "%(message)s", datefmt=datefmt
        )
        self._other_formatter = logging.Formatter(
            (utils.MOVE + utils.bold("*%(levelname)s*") + " %(message)s"),
            datefmt=datefmt,
        )

    def format(self, record):
        if record.levelname == "INFO":
            return self._info_formatter.format(record)
        return self._other_formatter.format(record)



class CustomFormatter(logging.Formatter):
    """custom formatter class to add colors to logging"""

    white = "\x1b[97;20m"
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    CYAN = "\x1b[36;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    RED_BOLD = "\x1b[31;1m"
    RESET = "\x1b[0m"

    fmt = "{}%(levelname)s{} - %(message)s"
    # fmt = "{}%(levelname)s{} %(module)s.%(funcName)-8s %(message)s"
    # fmt = "{}%(levelname)-5s{} %(lineno)-4d %(module)s.%(funcName)-8s: %(message)s"

    FORMATS = {
        logging.DEBUG: fmt.format(GREEN, RESET),
        logging.INFO: fmt.format(white, RESET),
        logging.WARNING: fmt.format(YELLOW, RESET),
        logging.ERROR: fmt.format(RED, RESET),
        logging.CRITICAL: fmt.format(RED_BOLD, RESET),
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def config_log(debug=True):
    __handler = logging.StreamHandler()
    __handler.setFormatter(CustomFormatter())
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO, handlers=[__handler]
    )
