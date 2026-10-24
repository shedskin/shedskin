# What the engine reads of the controls each frame, whatever they come
# from: kept apart from the terminal keyboard so the engine core needs no
# terminal modules.
from __future__ import annotations

DIR_LEFT = 1
DIR_RIGHT = 2
DIR_UP = 4
DIR_DOWN = 8


class Input:
    # dir_mask: int
    # button: bool
    # The last character typed, 0 once the password screen has taken it.
    # last_char: int
    # Pressed since the engine last looked.
    # pause: bool
    # code: bool
    # quit: bool

    def __init__(self) -> None:
        self.dir_mask = 0
        self.button = False
        self.last_char = 0
        self.pause = False
        self.code = False
        self.quit = False
