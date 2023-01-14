

MOVE = '\x1b[1G'
BOLD = '\x1b[1m'
RESET = "\x1b[0m"

def bold(txt):
    return f'{BOLD}{txt}{RESET}'
