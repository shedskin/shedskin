# The checkpoint codes of the password screen, read out of its bytecode.
# Each code is four comparisons of the typed letters (vars 0x1E to 0x21,
# each held as letter - 55) against constants, each jumping to the next
# code's comparisons on a mismatch; then the checkpoint number put in var
# 0x00, then the request for the part it starts in. The chain starts where
# the enter key (var 0x06 == 99) sends the check. Every release encodes them
# this way; a code left in the bytecode off that chain is not accepted,
# and plain jumps along the chain are followed.
#
# The continue screen after a death shows the code of the checkpoint the
# game restarts at, picking the string to draw by var 0x00. The password
# screen draws each letter typed as a string too, which the 20th
# Anniversary Edition's text relabels: its codes are the same, spelled
# with the letters it shows.
from __future__ import annotations

from .binary import be16
from .controls import Input
from .video import s16

OP_SET = 0x00
OP_CALL = 0x04
OP_RETURN = 0x05
OP_JUMP = 0x07
OP_COND_JUMP = 0x0A
OP_DRAW_STRING = 0x12
OP_LOAD = 0x19
COND_EQUAL_BYTE = 0x00
COND_NOT_EQUAL_BYTE = 0x01
VAR_CHECKPOINT = 0x00
VAR_ENTRY = 0x06
ENTRY_ENTER = 99
LETTER_OFFSET = 55
BLOCK = 24
STRING_PRESS_BUTTON = 0x13D
STRING_ACCESS_CODE = 0x13C


def read_codes(code: bytes) -> dict[str, tuple[int, int]]:
    """Every code the password screen accepts, mapped to (part, checkpoint)."""
    found = {}
    at = _chain_start(code)
    steps = 0
    while at > 0 and at + BLOCK + 7 <= len(code) and steps < len(code) // BLOCK:
        steps += 1
        # The 20th Anniversary chain jumps over a code it no longer takes.
        if int(code[at]) == OP_JUMP:
            at = be16(code, at + 1)
            continue
        name = _letters(code, at)
        if name == "":
            break
        after = at + BLOCK
        if int(code[after]) == OP_SET and int(code[after + 1]) == VAR_CHECKPOINT \
                and int(code[after + 4]) == OP_LOAD and name not in found:
            found[name] = (be16(code, after + 5), be16(code, after + 2))
        at = be16(code, at + 4)
    return found


def _chain_start(code: bytes) -> int:
    """Where `if var[0x06] == 99` sends the check, or -1."""
    for at in range(len(code) - 5):
        if int(code[at]) == OP_COND_JUMP and int(code[at + 1]) == COND_EQUAL_BYTE \
                and int(code[at + 2]) == VAR_ENTRY and int(code[at + 3]) == ENTRY_ENTER:
            return be16(code, at + 4)
    return -1


def _letters(code: bytes, at: int) -> str:
    """The code tested by four comparisons at `at`, or "" if there are none."""
    chars = []
    for k in range(4):
        pos = at + k * 6
        if int(code[pos]) != OP_COND_JUMP or int(code[pos + 1]) != COND_NOT_EQUAL_BYTE \
                or int(code[pos + 2]) != 0x1E + k:
            return ""
        letter = int(code[pos + 3]) + LETTER_OFFSET
        if letter < 0x41 or letter > 0x5A:
            return ""
        chars.append(chr(letter))
    return "".join(chars)


def read_code_strings(code: bytes, part: int,
                      codes: dict[str, tuple[int, int]]) -> dict[int, str]:
    """The continue screens of `part`'s bytecode: the id of the string each
    of the part's codes is drawn with, mapped to the code."""
    found = {}
    for at in range(len(code) - 12):
        if not (_draws(code, at, STRING_PRESS_BUTTON)
                and _draws(code, at + 6, STRING_ACCESS_CODE)):
            continue
        for name in codes:
            start = codes[name]
            if start[0] != part:
                continue
            string_id = _code_string(code, at + 12, start[1])
            if string_id >= 0:
                found[string_id] = name
    return found


def continue_screen_string(code: bytes, checkpoint: int) -> int:
    """The string the continue screen in `code` shows the code with, for
    var 0x00 at `checkpoint`; -1 if the part has no continue screen."""
    for at in range(len(code) - 12):
        if _draws(code, at, STRING_PRESS_BUTTON) and _draws(code, at + 6, STRING_ACCESS_CODE):
            return _code_string(code, at + 12, checkpoint)
    return -1


def read_letter_labels(code: bytes, strings: dict[int, str]) -> dict[int, int]:
    """The letter the password screen in `code` shows for each letter it
    takes, where the two differ, as upper-case code points."""
    labels = {}
    for at in range(len(code) - 9):
        if int(code[at]) != OP_COND_JUMP or int(code[at + 1]) != COND_NOT_EQUAL_BYTE \
                or int(code[at + 2]) != VAR_ENTRY or int(code[at + 6]) != OP_DRAW_STRING:
            continue
        letter = int(code[at + 3]) + LETTER_OFFSET
        string_id = be16(code, at + 7)
        if letter < 0x41 or letter > 0x5A or string_id not in strings:
            continue
        shown = strings[string_id].strip()
        if len(shown) == 1 and 0x41 <= ord(shown) <= 0x5A and ord(shown) != letter:
            labels[letter] = ord(shown)
    return labels


def relabel(name: str, labels: dict[int, int]) -> str:
    out = []
    for ch in name:
        c = ord(ch)
        if c in labels:
            c = labels[c]
        out.append(chr(c))
    return "".join(out)


def _draws(code: bytes, at: int, string_id: int) -> bool:
    return int(code[at]) == OP_DRAW_STRING and be16(code, at + 1) == string_id


def _code_string(code: bytes, at: int, checkpoint: int) -> int:
    """The string the code at `at` draws first with var 0x00 at
    `checkpoint`, or -1 if it does anything else before."""
    returns = []
    pc = at
    steps = 0
    while pc + 7 <= len(code) and steps < 256:
        steps += 1
        op = int(code[pc])
        if op == OP_DRAW_STRING:
            return be16(code, pc + 1)
        if op == OP_CALL:
            returns.append(pc + 3)
            pc = be16(code, pc + 1)
        elif op == OP_RETURN:
            if len(returns) == 0:
                return -1
            pc = returns.pop()
        elif op == OP_JUMP:
            pc = be16(code, pc + 1)
        elif op == OP_COND_JUMP:
            cond = int(code[pc + 1])
            if int(code[pc + 2]) != VAR_CHECKPOINT or (cond & 0x80) != 0:
                return -1
            if (cond & 0x40) != 0:
                value = s16(be16(code, pc + 3))
                pc += 2
            else:
                value = int(code[pc + 3])
                pc += 1
            if condition_holds(cond, checkpoint, value):
                pc = be16(code, pc + 3)
            else:
                pc += 5
        else:
            return -1
    return -1


def condition_holds(cond: int, b: int, a: int) -> bool:
    """Whether a conditional jump of kind `cond` is taken for `b` against `a`."""
    match cond & 7:
        case 0:
            return b == a
        case 1:
            return b != a
        case 2:
            return b > a
        case 3:
            return b >= a
        case 4:
            return b < a
        case 5:
            return b <= a
        case _:  # 6 and 7 are not comparisons; the original never jumps on them
            return False


# When the typer presses its keys: the first after the password screen is
# up, then one every few frames, as a player types.
TYPE_START = 10
TYPE_GAP = 4
KEY_ENTER = 13


class CodeTyper:
    """Types a code on the password screen and presses enter, so the game
    starts the checkpoint as when a player types it quickly. The DOS screen
    adds to var 0x37 every frame and a few checkpoints read it, so there
    the typing speed shows, for the typer as for a player."""

    # keys: list[int]
    # frame: int

    def __init__(self, name: str) -> None:
        self.keys = []
        low = name.lower()
        for ch in low:
            self.keys.append(ord(ch))
        self.keys.append(KEY_ENTER)
        self.frame = 0

    def feed(self, inp: Input) -> None:
        """Sets this frame's key in `inp`, if one is due."""
        self.frame += 1
        k = self.frame - TYPE_START
        if k < 0 or k % TYPE_GAP != 0 or k // TYPE_GAP >= len(self.keys):
            return
        key = self.keys[k // TYPE_GAP]
        inp.last_char = key
        # The enter key is also the action key, as on the keyboard.
        if key == KEY_ENTER:
            inp.button = True
