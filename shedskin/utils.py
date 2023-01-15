

MOVE = '\x1b[1G'
BOLD = '\x1b[1m'

WHITE = "\x1b[97;20m"
GREY = "\x1b[38;20m"
GREEN = "\x1b[32;20m"
CYAN = "\x1b[36;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
RED_BOLD = "\x1b[31;1m"

RESET = "\x1b[0m"

def bold(txt):
    return f'{BOLD}{txt}{RESET}'
