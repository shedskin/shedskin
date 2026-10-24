# Keys from the terminal, read without blocking once a frame. The game needs
# to know which keys are held down, and a terminal reports releases only
# under the kitty keyboard protocol; elsewhere a key counts as held while it
# keeps repeating.
from __future__ import annotations

import os
import sys
import termios
import tty

from .controls import DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_UP, Input

# Key codes: ASCII for the character keys, these above it for the arrows.
KEY_BACKSPACE = 8
KEY_ENTER = 13
KEY_ESCAPE = 27
KEY_SPACE = 32
KEY_UP = 0x101
KEY_DOWN = 0x102
KEY_RIGHT = 0x103
KEY_LEFT = 0x104

EVENT_PRESS = 1
EVENT_REPEAT = 2
EVENT_RELEASE = 3

# Without release events: a first press holds the key past the terminal's
# autorepeat delay, each repeat a little longer than the repeat interval.
# The terminal repeats only the key pressed last, so the keys held with it
# stay held as long as it does: arrow then space keeps running.
FIRST_HOLD_MS = 550
REPEAT_HOLD_MS = 120
HELD = 0x7FFFFFFF

# Kitty flags: disambiguate escapes (1), report releases (2), and report
# every key as an escape code (8), so letters and space get releases too.
KITTY_FLAGS = 11
# The longest XTVERSION reply taken; anything longer is not one.
MAX_REPLY = 64


class Keyboard:
    # enabled: bool
    # The terminal opened again for reading: O_NONBLOCK on stdin would also
    # apply to stdout, which shares its open file, and cut frames short.
    # fd: int
    # kitty: bool
    # The device attributes reply came, so every answer before it is in.
    # answered: bool
    # The terminal's name from its XTVERSION reply, lower case; "" for none.
    # terminal: str
    # saved: 'termios.TermAttributes | None'
    # pending: bytearray
    # Held keys and the time each stops counting as held.
    # held_until: dict[int, int]

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled and os.isatty(0)
        self.fd = -1
        self.kitty = False
        self.answered = False
        self.terminal = ""
        self.pending = bytearray()
        self.held_until = {}
        self.saved = None

    def begin(self) -> None:
        if not self.enabled:
            return
        # Raw, not cbreak: Ctrl-C arrives as a key, so quitting can restore
        # the terminal.
        self.fd = os.open("/dev/tty", os.O_RDONLY)
        self.saved = tty.setraw(self.fd)
        os.set_blocking(self.fd, False)
        # Asks for the terminal's name (XTVERSION) and the kitty flags, then
        # for the device attributes, which every terminal answers: a reply
        # to the others comes before it or not at all.
        sys.stdout.write("\x1b[>q\x1b[?u\x1b[c")
        sys.stdout.flush()

    def end(self) -> None:
        # Also after a begin() that failed before the terminal was opened.
        if not self.enabled or self.fd < 0:
            return
        try:
            if self.kitty:
                sys.stdout.write("\x1b[<u")
                sys.stdout.flush()
            saved = self.saved
            if saved is not None:
                termios.tcsetattr(self.fd, termios.TCSAFLUSH, saved)
        except (OSError, termios.error):
            # The terminal hung up (SIGHUP): there is nothing left to restore.
            pass
        os.close(self.fd)
        self.fd = -1

    def poll(self, inp: Input, now: int) -> None:
        """Reads the keys that arrived since the last call into `inp`."""
        if not self.enabled:
            return
        while True:
            try:
                data = os.read(self.fd, 256)
            except BlockingIOError:
                break
            if len(data) == 0:
                break
            self.pending.extend(data)
        self._parse(inp, now)
        mask = 0
        button = False
        for key, until in self.held_until.items():
            if until <= now:
                continue
            if key == KEY_LEFT:
                mask |= DIR_LEFT
            elif key == KEY_RIGHT:
                mask |= DIR_RIGHT
            elif key == KEY_UP:
                mask |= DIR_UP
            elif key == KEY_DOWN:
                mask |= DIR_DOWN
            elif key == KEY_SPACE or key == KEY_ENTER:
                button = True
        inp.dir_mask = mask
        inp.button = button

    def _parse(self, inp: Input, now: int) -> None:
        i = 0
        n = len(self.pending)
        while i < n:
            b = int(self.pending[i])
            if b != 0x1B:
                self._key(inp, now, b, 0, EVENT_PRESS)
                i += 1
                continue
            if i + 1 >= n:
                # A lone escape with nothing after it is the Escape key.
                self._key(inp, now, KEY_ESCAPE, 0, EVENT_PRESS)
                i += 1
                continue
            intro = int(self.pending[i + 1])
            if intro == 0x4F:  # SS3: arrows in application cursor mode
                if i + 2 >= n:
                    break
                self._arrow(inp, now, int(self.pending[i + 2]), 0, EVENT_PRESS)
                i += 3
                continue
            # DCS: the XTVERSION reply, ESC P > | name ST. Replies come before
            # the device attributes one, so after it ESC P is a key again.
            if intro == 0x50 and not self.answered:
                if i + 2 >= n:
                    break
                if int(self.pending[i + 2]) == 0x3E:
                    end, skip = self._dcs_end(i + 3, n)
                    if end == -1:
                        break  # the rest of the reply has not arrived yet
                    if end >= 0:
                        self._dcs(self.pending[i + 3:end].decode())
                        i = end + skip
                        continue
            if intro != 0x5B:
                self._key(inp, now, KEY_ESCAPE, 0, EVENT_PRESS)
                i += 1
                continue
            end = i + 2
            while end < n and not (0x40 <= int(self.pending[end]) <= 0x7E):
                end += 1
            if end >= n:
                break  # the rest of the sequence has not arrived yet
            self._csi(inp, now, self.pending[i + 2:end].decode(), int(self.pending[end]))
            i = end + 1
        rest = bytearray()
        for k in range(i, n):
            rest.append(self.pending[k])
        self.pending = rest

    def _dcs_end(self, start: int, n: int) -> tuple[int, int]:
        """Where the reply from `start` ends and how long its terminator is;
        (-1, 0) when it has not all arrived, (-2, 0) when it is no reply,
        which then reads as keys: an unterminated one must not hold up the
        input after it."""
        end = start
        while end < n:
            b = int(self.pending[end])
            if b == 0x9C:  # the 8-bit string terminator
                return (end, 1)
            if b == 0x1B:
                if end + 1 >= n:
                    return (-1, 0)
                if int(self.pending[end + 1]) == 0x5C:
                    return (end, 2)
                return (-2, 0)
            if b < 0x20 or b >= 0x7F or end - start >= MAX_REPLY:
                return (-2, 0)
            end += 1
        return (-1, 0)

    def _dcs(self, text: str) -> None:
        if not text.startswith("|"):
            return
        # "ghostty 1.1.3", "kitty(0.32.2)", "XTerm(390)"
        name = text[1:]
        for sep in [" ", "("]:
            cut = name.find(sep)
            if cut >= 0:
                name = name[:cut]
        self.terminal = name.lower()

    def _csi(self, inp: Input, now: int, params: str, final: int) -> None:
        if params.startswith("?"):
            if final == 0x75 and not self.kitty:  # u: the kitty flags reply
                self.kitty = True
                sys.stdout.write(f"\x1b[>{KITTY_FLAGS}u")
                sys.stdout.flush()
            elif final == 0x63:  # c: the device attributes reply
                self.answered = True
            return
        fields = params.split(";")
        code = _number(fields[0].split(":")[0], 1)
        mods = 0
        event = EVENT_PRESS
        if len(fields) > 1:
            parts = fields[1].split(":")
            mods = _number(parts[0], 1) - 1
            if len(parts) > 1:
                event = _number(parts[1], EVENT_PRESS)
        if final == 0x75:  # u: a key by its code point
            self._key(inp, now, code, mods, event)
        else:
            self._arrow(inp, now, final, mods, event)

    def _arrow(self, inp: Input, now: int, final: int, mods: int, event: int) -> None:
        if 0x41 <= final <= 0x44:  # A B C D
            self._key(inp, now, KEY_UP + final - 0x41, mods, event)

    def _key(self, inp: Input, now: int, key: int, mods: int, event: int) -> None:
        if key == 127:
            key = KEY_BACKSPACE
        ctrl = (mods & 4) != 0
        if key == 3 or (ctrl and key == 0x63):  # Ctrl-C
            inp.quit = True
            return
        if event == EVENT_RELEASE:
            if key in self.held_until:
                del self.held_until[key]
            return
        if self.kitty:
            self.held_until[key] = HELD
        else:
            until = now + FIRST_HOLD_MS
            if key in self.held_until and self.held_until[key] > now:
                until = now + REPEAT_HOLD_MS
            for other in self.held_until:
                if self.held_until[other] > now and self.held_until[other] < until:
                    self.held_until[other] = until
            self.held_until[key] = until
        if event == EVENT_REPEAT:
            if 0x61 <= key <= 0x7A or key == KEY_BACKSPACE:
                inp.last_char = key
            return
        # Escape does nothing: it sits next to the keys the game is played
        # with, and quitting by accident loses the game.
        if key == 0x70:  # p
            inp.pause = True
        elif key == 0x63:  # c
            inp.code = True
        if 0x61 <= key <= 0x7A or key == KEY_BACKSPACE or key == KEY_ENTER:
            inp.last_char = key
        elif 0x41 <= key <= 0x5A:
            inp.last_char = key + 0x20


def _number(text: str, default: int) -> int:
    if text == "":
        return default
    return int(int(text))
