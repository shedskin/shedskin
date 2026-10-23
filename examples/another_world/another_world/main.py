# The command line and the engine loop.
from __future__ import annotations

import os
import signal
import sys
import time

from .audio import AudioOut
from .clock import Clock
from .cmdline import parse_args
from .codes import VAR_CHECKPOINT, CodeTyper, continue_screen_string
from .controls import Input
from .keyboard import Keyboard
from .resource import GAME_PART_FIRST, GAME_PART_LAST, PART_INTRO, RELEASE_20TH, Resources
from .screen import (H, MODE_COMPARE, MODE_DIGESTS, MODE_SUMMARY, MODE_TERMINAL, RENDER_NAMES,
                     RENDER_OCTANT, W, Cells, Screen)
from .sound import RATE
from .vm import VM
from .wav import WavWriter


def main() -> int:
    # A bare run shows the help, like --help.
    argv = []
    for arg in sys.argv[1:]:
        argv.append(arg)
    if len(argv) == 0:
        argv.append("--help")
    args = parse_args(argv)
    part = int(args.part)
    if part < GAME_PART_FIRST or part > GAME_PART_LAST:
        print(f"aw.py: error: --part must be between {GAME_PART_FIRST} and {GAME_PART_LAST}",
              file=sys.stderr)
        return 2

    # Headless runs use a virtual clock, so they finish at once and repeat.
    mode = MODE_TERMINAL
    if args.compare >= 0:
        mode = MODE_COMPARE
    elif args.digests:
        mode = MODE_DIGESTS
    elif not os.isatty(1):
        mode = MODE_SUMMARY
    clock = Clock(mode != MODE_TERMINAL)
    render = args.render
    picked = 0 if render == "" else 1
    for name, on in [("half", args.half), ("quad", args.quad),
                     ("sextant", args.sextant), ("octant", args.octant)]:
        if on:
            render = name
            picked += 1
    if picked > 1:
        print("aw.py: error: choose one of -2, -4, -6, -8 and -r", file=sys.stderr)
        return 2
    # The terminal's answers decide the default once it is opened.
    defaulted = render == ""
    if defaulted:
        render = "half"
    screen = Screen(mode, int(RENDER_NAMES.index(render)), int(args.compare))
    try:
        vm = VM(Resources(args.data), clock, screen, int(args.seed))
    except (OSError, ValueError) as e:
        print(f"aw.py: error: {e}", file=sys.stderr)
        return 1
    if args.remastered_audio:
        if vm.res.release != RELEASE_20TH:
            print("aw.py: error: --remastered-audio needs the 20th Anniversary Edition",
                  file=sys.stderr)
            return 2
        vm.res.remastered_audio = True
    if part == GAME_PART_FIRST and not vm.res.has_protection:
        print("aw.py: error: the 20th Anniversary Edition has no copy protection part (16000)",
              file=sys.stderr)
        return 2
    stop_part = part
    typer = CodeTyper("")
    typing = False
    if args.code != "":
        # Read once already, for the continue screen, so this cannot fail.
        codes = vm.res.checkpoint_codes()
        if args.code == "list":
            print_codes(codes)
            return 0
        name = args.code.upper()
        if name not in codes:
            print(f"aw.py: error: {args.code} is not a code of this release; it has "
                  + ", ".join(sorted(codes)), file=sys.stderr)
            return 2
        start = codes[name]
        stop_part = start[0]
        if vm.res.typed_codes:
            # Typed on the password screen, the code leaves the game in the
            # state a player gets, the screen's own variables included.
            part = GAME_PART_LAST
            typer = CodeTyper(name)
            typing = True
        else:
            # What the password screen does when it accepts a code.
            part = start[0]
            vm.vars[VAR_CHECKPOINT] = start[1]
    wav = None
    if args.wav != "":
        try:
            wav = WavWriter(args.wav, RATE)
        except OSError as e:
            print(f"aw.py: error: {args.wav}: {e.strerror}", file=sys.stderr)
            return 1
        vm.mixer.enabled = True
    audio = None
    if mode == MODE_TERMINAL and not args.mute:
        audio = AudioOut()
        if audio.active():
            vm.mixer.enabled = True
    keyboard = Keyboard(mode == MODE_TERMINAL)
    inp = Input()
    max_frames = int(args.frames)
    stop_after_part = mode != MODE_TERMINAL and max_frames == 0
    # Missing or damaged data can surface at any part start; the message is
    # printed once the terminal is restored.
    failure = ""
    # Blocked right before the try and taken at each frame, so a kill or a
    # closed terminal always ends through the cleanup below. Players
    # started later unblock them again (see popen.py).
    signal.pthread_sigmask(signal.SIG_BLOCK, [signal.SIGTERM, signal.SIGHUP])
    try:
        vm.screen.begin()
        keyboard.begin()
        if mode == MODE_TERMINAL:
            wait_for_answers(keyboard, inp, vm.clock)
            if defaulted and terminal_name(keyboard) in OCTANT_TERMINALS:
                vm.screen.set_render(RENDER_OCTANT)
        vm.init_for_part(part)
        while not vm.screen.done and not inp.quit:
            end_by_signal()
            if max_frames > 0 and vm.screen.frames >= max_frames:
                break
            if stop_after_part and vm.res.requested_part != 0 \
                    and vm.res.requested_part != stop_part:
                break
            vm.apply_requests()
            keyboard.poll(inp, vm.clock.now())
            if typing:
                typer.feed(inp)
            vm.update_input(inp)
            if inp.pause:
                inp.pause = False
                current = vm.res.current_part
                # The original ignores pause during the protection and the
                # intro; the password screen needs the letter p.
                if current != GAME_PART_FIRST and current != PART_INTRO \
                        and current != GAME_PART_LAST:
                    wait_for_unpause(keyboard, inp, vm.clock)
                    if audio is not None:
                        audio.resume()
            vm.run_frame()
            samples = vm.mixer.take()
            if wav is not None:
                wav.write(samples)
            if audio is not None:
                audio.write(samples)
                if vm.mixer.track_changed:
                    vm.mixer.track_changed = False
                    audio.play_track(vm.mixer.track, vm.mixer.track_loop)
                audio.keep_track()
    except (OSError, ValueError) as e:
        failure = str(e)
    except KeyboardInterrupt:
        # A SIGINT from outside the game quits it like Ctrl-C does.
        pass
    finally:
        # Each runs even if one before fails, so no player is left playing.
        try:
            keyboard.end()
        finally:
            try:
                vm.screen.end()
            finally:
                try:
                    if wav is not None:
                        wav.close()
                finally:
                    if audio is not None:
                        audio.close()
    if failure != "":
        print(f"aw.py: error: {failure}", file=sys.stderr)
        return 1
    if mode == MODE_TERMINAL:
        print(vm.video.string(CLOSING_STRING).strip())
        print()
        print("Thanks for playing Another World. If you liked it, get it on GOG.")
        name = checkpoint_code(vm)
        level = LEVELS.get(vm.res.current_part, "")
        if name != "" and level != "":
            print()
            print(f"Checkpoint code: {name} ({level}); start there with --code {name}")
        if audio is not None and audio.missing():
            print()
            print(no_sound())
        if keyboard.enabled:
            # The name again: a reply too late for the render mode still counts.
            tip = terminal_tip(keyboard.kitty, terminal_name(keyboard), defaulted, vm.screen)
            if tip != "":
                print()
                print(tip)
    return 0


# The terminals that draw the octants of -8 themselves, whatever the font.
OCTANT_TERMINALS = ["ghostty"]
# Terminal multiplexers, which answer XTVERSION for the terminal they run in.
MULTIPLEXERS = ["tmux", "screen"]

RENDER_OPTIONS = {"half": "-2", "quad": "-4", "sextant": "-6", "octant": "-8",
                                  "braille": "-r braille"}


def end_by_signal() -> None:
    """A pending SIGTERM / SIGHUP: leave through main's cleanup, which
    restores the terminal and stops the players, with the shell's status
    for the signal."""
    pending = signal.sigpending()
    for signum in (signal.SIGTERM, signal.SIGHUP):
        if signum in pending:
            sys.exit(128 + signum)


def wait_for_answers(keyboard: Keyboard, inp: Input, clock: Clock) -> None:
    """Waits for the terminal to answer keyboard.begin(), since the default
    render mode depends on it; keys typed meanwhile are read as usual. A
    terminal that answers nothing is given up on soon. A quit waits too, so
    the answers are not left for the shell to echo."""
    give_up = time.monotonic() + 0.3
    while keyboard.enabled:
        keyboard.poll(inp, clock.now())
        if keyboard.answered or time.monotonic() >= give_up:
            return
        time.sleep(0.005)


def terminal_name(keyboard: Keyboard) -> str:
    if keyboard.terminal != "":
        return keyboard.terminal
    # Without a reply, Ghostty is told by its own TERM: TERM_PROGRAM is
    # inherited by any terminal started from a Ghostty shell.
    if os.environ.get("TERM") == "xterm-ghostty":
        return "ghostty"
    return ""


def terminal_tip(kitty: bool, terminal: str, defaulted: bool, screen: Screen) -> str:
    """A tip for a better game, when the terminal or its window held this
    one back; "" when nothing did."""
    cells = screen.cells
    render = RENDER_NAMES[cells.render]
    ghostty = terminal == "ghostty"
    option = RENDER_OPTIONS[render]
    width = cells.cols * cells.cw
    height = cells.rows * cells.ch
    # The most this mode shows, in a window of any size.
    full = Cells(cells.render)
    full.fit(W, H)
    full_width = full.cols * full.cw
    full_height = full.rows * full.ch
    drawn = cells.cols > 0
    lower = drawn and defaulted and render != "octant" and (width < W or height < H)
    small = drawn and not lower and (width < full_width or height < full_height)
    text = ""
    if not kitty:
        text = "This terminal does not report key releases, so a tap counts as held " \
            "for about half a second"
    if lower:
        text += ", and showed" if text != "" else "This terminal showed"
        text += f" the picture with {option} at {width}x{height}"
    elif small:
        text += ", and the window" if text != "" else "The window"
        text += f" was too small for the full {full_width}x{full_height} picture with " \
            f"{option}, which needs {full.cols} columns by {full.rows} rows"
    if text == "":
        return ""
    text += "."
    lines = []
    line = ""
    for word in text.split(" "):
        if line == "":
            line = word
        elif len(line) + 1 + len(word) > 72:
            lines.append(line)
            line = word
        else:
            line += " " + word
    lines.append(line)
    if terminal in MULTIPLEXERS:
        # It answers for itself, so the terminal behind it is unknown.
        lines.append(f"Inside {terminal} the game cannot tell the terminal; in Ghostty, use -8.")
    elif not ghostty:
        lines.append("For the best experience, play in Ghostty.")
    return "\n".join(lines)


def no_sound() -> str:
    """The quit message when no player worked, naming this system's."""
    if sys.platform == "darwin":
        return "The game played without sound: it needs SoX's play, which did not\n" \
            "work. Install it with: brew install sox"
    return "The game played without sound: it needs pw-play, paplay, aplay or\n" \
        "SoX's play, and none of them worked."


# The line the game ends with.
CLOSING_STRING = 0x265


def checkpoint_code(vm: VM) -> str:
    """The code of the checkpoint the game was at: the one the continue
    screen would show, or where the part has none for it, the part's code
    of the latest checkpoint reached; "" for none."""
    checkpoint = vm.vars[VAR_CHECKPOINT]
    name = vm.video.string(continue_screen_string(vm.code, checkpoint))
    if name != "":
        return name
    best = -1
    codes = vm.res.checkpoint_codes()
    for code in codes:
        start = codes[code]
        if start[0] == vm.res.current_part and best < start[1] <= checkpoint:
            best = start[1]
            name = code
    return name


LEVELS = {16002: "water", 16003: "jail", 16004: "city", 16005: "arena",
                             16006: "baths", 16007: "final"}


def print_codes(codes: dict[str, tuple[int, int]]) -> None:
    """The codes by level, each level's in checkpoint order."""
    order = []
    for name in codes:
        start = codes[name]
        order.append((start[0], start[1], name))
    order.sort()
    part = int(0)
    line = []
    for entry in order:
        if entry[0] != part:
            if len(line) > 0:
                print(" ".join(line))
            part = entry[0]
            line = [f"{LEVELS.get(part, '?'):6} ({part})"]
        line.append(entry[2])
    if len(line) > 0:
        print(" ".join(line))


def wait_for_unpause(keyboard: Keyboard, inp: Input, clock: Clock) -> None:
    clock.pause()
    while not inp.pause and not inp.quit:
        time.sleep(0.05)
        end_by_signal()
        keyboard.poll(inp, clock.now())
    inp.pause = False
    clock.resume()
