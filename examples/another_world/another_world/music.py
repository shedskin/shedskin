# The music sequencer: it steps through a module's patterns on the game
# clock, playing their notes on the mixer's music voices and passing on the
# marks the bytecode synchronizes with.
from __future__ import annotations

from .binary import be16
from .sound import MUSIC_VOICE, PAULA_CLOCK, Mixer, raw_sample
from .video import s16

MARK_NOTE = 0xFFFD
STOP_NOTE = 0xFFFE
INSTRUMENTS = 15
MAX_VOLUME = 0x3F
EFFECT_VOLUME_UP = 5
EFFECT_VOLUME_DOWN = 6


def _event_delay(delay: int) -> int:
    return (delay * 60 // 7050) & 0xFFFF


class Music:
    # module: bytes
    # The module's instruments: the sample of each, b"" for none, and its volume.
    # samples: list[bytes]
    # volumes: list[int]
    # playing: bool
    # delay: int
    # next_event: int
    # order: int
    # num_orders: int
    # pos: int
    # The last mark reached, for the VM to copy into its mark variable.
    # mark: int
    # mark_pending: bool

    def __init__(self) -> None:
        self.module = b""
        self.samples = []
        self.volumes = []
        self.playing = False
        self.delay = 0
        self.next_event = 0
        self.order = 0
        self.num_orders = 0
        self.pos = 0
        self.mark = 0
        self.mark_pending = False

    def load(self, module: bytes, delay: int, order: int,
             samples: list[bytes]) -> None:
        """Loads `module`; `samples` holds its instruments' samples, by the
        resource numbers its header lists (see instrument_numbers)."""
        self.module = module
        self.samples = samples
        self.volumes = []
        for i in range(INSTRUMENTS):
            self.volumes.append(be16(module, 4 + i * 4))
        self.order = order
        self.num_orders = be16(module, 0x3E)
        if delay == 0:
            delay = be16(module, 0)
        self.delay = _event_delay(delay)

    def start(self, now: int) -> None:
        self.pos = 0
        self.playing = True
        self.next_event = now + self.delay

    def set_delay(self, delay: int) -> None:
        self.delay = _event_delay(delay)

    def stop(self) -> None:
        self.playing = False

    def update(self, now: int, mixer: Mixer) -> None:
        """Runs every pattern row that has come due by `now`, the mixer
        rendered up to each row's time first."""
        while self.playing and self.next_event <= now:
            mixer.render_to(self.next_event)
            self._step(mixer)
            if self.delay == 0:
                self.playing = False
            self.next_event += self.delay

    def _step(self, mixer: Mixer) -> None:
        pattern = int(self.module[0x40 + self.order])
        p = 0xC0 + self.pos + pattern * 1024
        for channel in range(4):
            self._note(mixer, channel, be16(self.module, p), be16(self.module, p + 2))
            p += 4
        self.pos += 16
        if self.pos >= 1024:
            self.pos = 0
            self.order = (self.order + 1) & 0xFF
            if self.order == self.num_orders:
                self.playing = False

    def _note(self, mixer: Mixer, channel: int, note: int, arg: int) -> None:
        if note == MARK_NOTE:
            self.mark = s16(arg)
            self.mark_pending = True
            return
        voice = MUSIC_VOICE + channel
        instrument = (arg >> 12) & 0xF
        sample = b""
        if instrument != 0:
            sample = self.samples[instrument - 1]
        if len(sample) != 0:
            # An instrument sets the voice's volume even without a note, for
            # the one playing.
            volume = self.volumes[instrument - 1]
            effect = (arg >> 8) & 0xF
            if effect == EFFECT_VOLUME_UP:
                volume = min(volume + (arg & 0xFF), MAX_VOLUME)
            elif effect == EFFECT_VOLUME_DOWN:
                volume = max(volume - (arg & 0xFF), 0)
            mixer.set_volume(voice, volume)
        if note == STOP_NOTE:
            mixer.stop(voice)
        elif note != 0 and len(sample) != 0:
            # The note is an Amiga period.
            mixer.play(voice, raw_sample(sample), PAULA_CLOCK // (note * 2),
                       mixer.voices[voice].volume)


def instrument_numbers(module: bytes) -> list[int]:
    """The resource number of each of the module's instruments, 0 for none."""
    numbers = []
    for i in range(INSTRUMENTS):
        numbers.append(be16(module, 2 + i * 4))
    return numbers
