# The bytecode VM: 64 cooperative threads over 256 int16 variables. Each
# frame runs every live thread until it yields; a thread's video opcodes draw
# into the pages and a blit shows one.
from __future__ import annotations

from .clock import Clock
from .codes import condition_holds
from .controls import DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_UP, Input
from .music import Music, instrument_numbers
from .releases.anniversary import MUSIC_LOOP, MUSIC_NONE, MUSIC_STOP
from .releases.memlist import RT_MUSIC
from .resource import GAME_PART_FIRST, GAME_PART_LAST, PART_INTRO, Resources
from .screen import Screen
from .sound import PERIODS, Mixer, period_rate
from .video import Video, s16

NUM_THREADS = 64
INACTIVE = 0xFFFF
NO_REQUEST = 0xFFFF
KILL_REQUEST = 0xFFFE

VAR_RANDOM_SEED = 0x3C
VAR_LAST_KEYCHAR = 0xDA
VAR_HERO_POS_UP_DOWN = 0xE5
VAR_MUS_MARK = 0xF4
VAR_SCROLL_Y = 0xF9
VAR_HERO_ACTION = 0xFA
VAR_HERO_POS_JUMP_DOWN = 0xFB
VAR_HERO_POS_LEFT_RIGHT = 0xFC
VAR_HERO_POS_MASK = 0xFD
VAR_HERO_ACTION_POS_MASK = 0xFE
VAR_PAUSE_SLICES = 0xFF


def _s8(v: int) -> int:
    return ((v & 0xFF) ^ 0x80) - 0x80


class VM:
    # res: Resources
    # video: Video
    # music: Music
    # mixer: Mixer
    # clock: Clock
    # screen: Screen
    # vars: list[int]
    # pc: list[int]
    # requested_pc: list[int]
    # paused: list[int]
    # requested_paused: list[int]
    # stack: list[int]
    # sp: int
    # The current part's segments, copied out of Resources.
    # code: bytes
    # palettes: bytes
    # cinematic: bytes
    # shapes: bytes
    # ip: int
    # yielded: bool
    # last_blit: int

    def __init__(self, res: Resources, clock: Clock,
                 screen: Screen, seed: int) -> None:
        self.res = res
        self.video = Video()
        self.music = Music()
        self.mixer = Mixer()
        self.clock = clock
        self.screen = screen
        self.vars = [0] * 256
        self.pc = [INACTIVE] * NUM_THREADS
        self.requested_pc = [NO_REQUEST] * NUM_THREADS
        self.paused = [0] * NUM_THREADS
        self.requested_paused = [0] * NUM_THREADS
        self.stack = [0] * 256
        self.sp = 0
        self.code = b""
        self.palettes = b""
        self.cinematic = b""
        self.shapes = b""
        self.ip = 0
        self.yielded = False
        self.last_blit = 0
        self.vars[0x54] = 0x81
        self.vars[VAR_RANDOM_SEED] = s16(seed)
        self.res.start_vars(self.vars)
        self.video.use_strings(self.res.strings())

    def init_for_part(self, part: int) -> None:
        self._render_before_change()
        self.music.stop()
        self.mixer.stop_all()
        self.res.part_vars(self.vars)
        self.res.setup_part(part)
        self.code = self.res.segment(0)
        self.palettes = self.res.segment(1)
        self.cinematic = self.res.segment(2)
        self.shapes = self.res.segment(3)
        for t in range(NUM_THREADS):
            self.pc[t] = INACTIVE
            self.requested_pc[t] = NO_REQUEST
            self.paused[t] = 0
            self.requested_paused[t] = 0
        self.pc[0] = 0

    def apply_requests(self) -> None:
        """Starts a requested game part, then applies the pauses and jumps
        threads asked for during the previous frame."""
        if self.res.requested_part != 0:
            self.init_for_part(self.res.requested_part)
            self.res.requested_part = 0
        for t in range(NUM_THREADS):
            self.paused[t] = self.requested_paused[t]
            n = self.requested_pc[t]
            if n != NO_REQUEST:
                self.pc[t] = INACTIVE if n == KILL_REQUEST else n
                self.requested_pc[t] = NO_REQUEST

    def update_input(self, inp: Input) -> None:
        """Hands the keys to the bytecode, once a frame as the original."""
        self.clock.tick()
        self._update_music()
        part = self.res.current_part
        if part == GAME_PART_LAST:
            # The password screen reads letters and backspace, upper case,
            # and Enter to check the code. rawgl leaves Enter out, so a code
            # could only be confirmed from the on-screen grid there.
            c = self.res.taken_key(inp.last_char)
            if c == 8 or c == 13 or c == 0 or 0x61 <= c <= 0x7A:
                self.vars[VAR_LAST_KEYCHAR] = c & ~0x20
                inp.last_char = 0
        lr = 0
        ud = 0
        mask = 0
        if inp.dir_mask & DIR_RIGHT:
            lr = 1
            mask |= 1
        if inp.dir_mask & DIR_LEFT:
            lr = -1
            mask |= 2
        if inp.dir_mask & DIR_DOWN:
            ud = 1
            mask |= 4
        if inp.dir_mask & DIR_UP:
            ud = -1
            mask |= 8
        if self.res.writes_up_down:
            self.vars[VAR_HERO_POS_UP_DOWN] = ud
        self.vars[VAR_HERO_POS_JUMP_DOWN] = ud
        self.vars[VAR_HERO_POS_LEFT_RIGHT] = lr
        self.vars[VAR_HERO_POS_MASK] = mask
        button = 0
        if inp.button:
            button = 1
            mask |= 0x80
        self.vars[VAR_HERO_ACTION] = button
        self.vars[VAR_HERO_ACTION_POS_MASK] = mask
        if inp.code:
            # The code key opens the password screen from inside the game.
            inp.code = False
            if part != GAME_PART_FIRST and part != GAME_PART_LAST:
                self.res.requested_part = GAME_PART_LAST
        if inp.button and part == PART_INTRO and self.res.intro_skip \
                and self.res.requested_part == 0:
            self.res.requested_part = PART_INTRO + 1

    def run_frame(self) -> None:
        for t in range(NUM_THREADS):
            if self.paused[t] != 0 or self.pc[t] == INACTIVE:
                continue
            self.ip = self.pc[t]
            self.sp = 0
            self.yielded = False
            self._run_thread()
            self.pc[t] = self.ip & 0xFFFF

    def _update_music(self) -> None:
        self._render_sound()
        if self.music.mark_pending:
            self.vars[VAR_MUS_MARK] = self.music.mark
            self.music.mark_pending = False

    def _render_sound(self) -> None:
        now = self.clock.now()
        self.music.update(now, self.mixer)
        self.mixer.render_to(now)

    def _render_before_change(self) -> None:
        """Mixes the sound up to now, but not past a music row still due:
        the music steps only where it always has, so its marks reach the
        bytecode at the same moments."""
        now = self.clock.now()
        if self.music.playing and self.music.next_event < now:
            now = self.music.next_event
        self.mixer.render_to(now)

    def _fetch8(self) -> int:
        b = int(self.code[self.ip])
        self.ip += 1
        return b

    def _fetch16(self) -> int:
        hi = self._fetch8()
        lo = self._fetch8()
        return (hi << 8) | lo

    def _run_thread(self) -> None:
        while not self.yielded:
            op = self._fetch8()
            if op & 0x80:
                self._op_draw_cinematic(op)
            elif op & 0x40:
                self._op_draw_shape(op)
            else:
                self._op(op)

    def _op_draw_cinematic(self, op: int) -> None:
        lo = self._fetch8()
        off = (((op << 8) | lo) * 2) & 0xFFFF
        x = self._fetch8()
        y = self._fetch8()
        h = y - 199
        if h > 0:
            y = 199
            x += h
        self.video.draw_shape(self.cinematic, off, 0xFF, 0x40, x, y)

    def _op_draw_shape(self, op: int) -> None:
        off = (self._fetch16() * 2) & 0xFFFF
        x = self._fetch8()
        if not op & 0x20:
            if not op & 0x10:
                lo = self._fetch8()
                x = s16((x << 8) | lo)
            else:
                x = self.vars[x]
        elif op & 0x10:
            x += 0x100
        y = self._fetch8()
        if not op & 8:
            if not op & 4:
                lo = self._fetch8()
                y = s16((y << 8) | lo)
            else:
                y = self.vars[y]
        zoom = self._fetch8()
        use_shapes = False
        if not op & 2:
            if not op & 1:
                self.ip -= 1
                zoom = 0x40
            else:
                zoom = self.vars[zoom] & 0xFFFF
        elif op & 1:
            use_shapes = True
            self.ip -= 1
            zoom = 0x40
        if use_shapes:
            self.video.draw_shape(self.shapes, off, 0xFF, zoom, x, y)
        else:
            self.video.draw_shape(self.cinematic, off, 0xFF, zoom, x, y)

    def _op(self, op: int) -> None:
        v = self.vars
        match op:
            case 0x00:  # mov var, const
                d = self._fetch8()
                v[d] = s16(self._fetch16())
            case 0x01:  # mov var, var
                d = self._fetch8()
                v[d] = v[self._fetch8()]
            case 0x02:  # add var, var
                d = self._fetch8()
                v[d] = s16(v[d] + v[self._fetch8()])
            case 0x03:  # add var, const
                d = self._fetch8()
                v[d] = s16(v[d] + s16(self._fetch16()))
            case 0x04:  # call
                target = self._fetch16()
                self.stack[self.sp] = self.ip
                self.sp += 1
                self.ip = target
            case 0x05:  # ret
                self.sp -= 1
                self.ip = self.stack[self.sp]
            case 0x06:  # yield until the next frame
                self.yielded = True
            case 0x07:  # jmp
                self.ip = self._fetch16()
            case 0x08:  # set another thread's pc for the next frame
                t = self._fetch8()
                self.requested_pc[t] = self._fetch16()
            case 0x09:  # decrement, jump if not zero
                d = self._fetch8()
                v[d] = s16(v[d] - 1)
                target = self._fetch16()
                if v[d] != 0:
                    self.ip = target
            case 0x0A:
                self._op_cond_jump()
            case 0x0B:  # palette for the next blit
                self.video.palette_requested = self._fetch16() >> 8
            case 0x0C:
                self._op_reset_threads()
            case 0x0D:
                self.video.select_page(self._fetch8())
            case 0x0E:
                page = self._fetch8()
                self.video.fill_page(page, self._fetch8())
            case 0x0F:
                src = self._fetch8()
                self.video.copy_page(src, self._fetch8(), v[VAR_SCROLL_Y])
            case 0x10:
                self._op_blit(self._fetch8())
            case 0x11:  # kill the running thread
                self.ip = 0xFFFF
                self.yielded = True
            case 0x12:  # draw string
                string_id = self._fetch16()
                x = self._fetch8()
                y = self._fetch8()
                self.video.draw_string(string_id, x, y, self._fetch8())
            case 0x13:  # sub var, var
                d = self._fetch8()
                v[d] = s16(v[d] - v[self._fetch8()])
            case 0x14:  # and var, const
                d = self._fetch8()
                v[d] = s16(v[d] & self._fetch16())
            case 0x15:  # or var, const
                d = self._fetch8()
                v[d] = s16((v[d] & 0xFFFF) | self._fetch16())
            case 0x16:  # shl var, const
                d = self._fetch8()
                n = self._fetch16() & 31
                v[d] = 0 if n >= 16 else s16((v[d] & 0xFFFF) << n)
            case 0x17:  # shr var, const
                d = self._fetch8()
                n = self._fetch16() & 31
                v[d] = 0 if n >= 16 else s16((v[d] & 0xFFFF) >> n)
            case 0x18:
                self._op_sound()
            case 0x19:
                self._op_load(self._fetch16())
            case 0x1A:
                self._op_music()
            case _:
                raise ValueError(f"invalid opcode {op:#04x} at {self.ip - 1:#06x}")

    def _op_cond_jump(self) -> None:
        cond = self._fetch8()
        b = self.vars[self._fetch8()]
        a = 0
        if cond & 0x80:
            a = self.vars[self._fetch8()]
        elif cond & 0x40:
            a = s16(self._fetch16())
        else:
            a = self._fetch8()
        target = self._fetch16()
        if condition_holds(cond, b, a):
            self.ip = target

    def _op_reset_threads(self) -> None:
        first = self._fetch8()
        last = self._fetch8() & (NUM_THREADS - 1)
        n = _s8(last - first)
        if n < 0:
            return
        action = self._fetch8()
        for t in range(first, first + n + 1):
            if action == 2:
                self.requested_pc[t] = KILL_REQUEST
            elif action < 2:
                self.requested_paused[t] = action

    def _op_blit(self, page: int) -> None:
        # The bytecode sets how long a frame stays up, in 20 ms slices.
        wait = self.vars[VAR_PAUSE_SLICES] * 20 - (self.clock.now() - self.last_blit)
        if wait > 0:
            self.clock.sleep(wait)
            self._update_music()
        self.last_blit = self.clock.now()
        self.vars[0xF7] = 0
        self.video.flip(page, self.palettes)
        self.video.show(self.screen, self.clock.now())

    def _op_load(self, index: int) -> None:
        if index == 0:
            self._render_before_change()
            self.music.stop()
            self.mixer.stop_all()
            self.res.invalidate_media()
            return
        for bitmap in self.res.request(index):
            self.video.copy_bitmap(bitmap)

    def _op_sound(self) -> None:
        index = self._fetch16()
        period = self.res.sound_period(min(self._fetch8(), len(PERIODS) - 1))
        volume = min(self._fetch8(), 63)
        voice = self._fetch8() & 3
        self._render_before_change()
        if volume == 0:
            self.mixer.stop(voice)
        else:
            sample = self.res.sound(index)
            rate = sample.playback_rate(period_rate(PERIODS[period]))
            self.mixer.play(voice, sample, rate, volume)

    def _op_music(self) -> None:
        index = self._fetch16()
        delay = self._fetch16()
        order = self._fetch8()
        self._render_before_change()
        if index != 0:
            action, track = self.res.music_request(index)
            if action == MUSIC_STOP:
                self.mixer.play_track("", False)
            elif action != MUSIC_NONE:
                self.mixer.play_track(track, action == MUSIC_LOOP)
            elif self.res.is_loaded(index) and self.res.entries[index].kind == RT_MUSIC:
                module = self.res.entry(index)
                samples = []
                for n in instrument_numbers(module):
                    if n != 0 and self.res.is_loaded(n):
                        samples.append(self.res.entry(n))
                    else:
                        samples.append(b"")
                self.music.load(module, delay, order, samples)
                self.mixer.stop_music()
                self.music.start(self.clock.now())
        elif delay != 0:
            self.music.set_delay(delay)
        else:
            # A recording plays on, as in rawgl, which ignores this request in
            # the 20th Anniversary Edition.
            self.music.stop()
            self.mixer.stop_music()
