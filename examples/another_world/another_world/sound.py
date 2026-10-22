# The mixer: eight voices of samples, the four the bytecode plays
# sound effects on and the four the music plays its notes on, as the Amiga's
# Paula chip played them, without interpolation. It renders on the game
# clock, so a headless run sounds the same every time.
from __future__ import annotations

from .binary import be16

RATE = 44100
VOICES = 8
MUSIC_VOICE = 4
# The Amiga's clock, which turns a period into a playback rate.
PAULA_CLOCK = 7159092
# The periods a sound effect is played at, by the index the bytecode gives.
PERIODS = [
    1076, 1016, 960, 906, 856, 808, 762, 720, 678, 640,
    604, 570, 538, 508, 480, 453, 428, 404, 381, 360,
    339, 320, 302, 285, 269, 254, 240, 226, 214, 202,
    190, 180, 170, 160, 151, 143, 135, 127, 120, 113,
]
FRAC_BITS = 16
SAMPLE_HEADER = 8

# How a sample's bytes hold its values.
SIGNED_8 = 0
UNSIGNED_8 = 1
SIGNED_16 = 2
# The rate the original samples were made for: a WAV at another rate is
# played faster in proportion, so it keeps its pitch.
NATIVE_RATE = 9943
SCALED_WAV_RATES = [22050, 44100, 48000]


def period_rate(period: int) -> int:
    return PAULA_CLOCK // (period * 2)


def _le16(data: bytes, pos: int) -> int:
    return int(data[pos]) | (int(data[pos + 1]) << 8)


def _le32(data: bytes, pos: int) -> int:
    """An unsigned little-endian long."""
    return int(_le16(data, pos)) | (int(_le16(data, pos + 2)) << 16)


class Sample:
    """A sound to play: `length` values from `start` in `data`, then, when
    `loop_length` is not 0, the values from `loop_start` over and over. A
    stereo sample's value is a frame, its two channels together."""

    # data: bytes
    # form: int
    # channels: int
    # start: int
    # length: int
    # loop_start: int
    # loop_length: int
    # The rate the values were recorded at, NATIVE_RATE for the original's.
    # rate: int

    def __init__(self, data: bytes, form: int, channels: int, start: int, length: int,
                 loop_start: int, loop_length: int, rate: int) -> None:
        self.data = data
        self.form = form
        self.channels = channels
        self.start = start
        self.length = length
        self.loop_start = loop_start
        self.loop_length = loop_length
        self.rate = rate

    def playback_rate(self, rate: int) -> int:
        """The rate to play at for an original sample's `rate`."""
        if self.rate in SCALED_WAV_RATES:
            return int(int(rate) * int(self.rate) // int(NATIVE_RATE))
        return rate

    def empty(self) -> bool:
        """Whether there is no sound at all, as for a missing file."""
        return len(self.data) == 0

    def value(self, at: int) -> int:
        """The value at `at`, scaled to 16 bits; a stereo frame's channels
        mixed down to one."""
        if self.channels == 2:
            return (self._channel_value(at * 2) + self._channel_value(at * 2 + 1)) // 2
        return self._channel_value(at)

    def _channel_value(self, at: int) -> int:
        if self.form == SIGNED_16:
            v = _le16(self.data, self.start + at * 2)
            return v - 65536 if v >= 32768 else v
        v = int(self.data[self.start + at])
        if self.form == UNSIGNED_8:
            return (v - 128) * 256
        return (v - 256 if v >= 128 else v) * 256


def no_sample() -> Sample:
    return Sample(b"", SIGNED_8, 1, 0, 0, 0, 0, NATIVE_RATE)


def raw_sample(data: bytes) -> Sample:
    """A DOS or Amiga sample: its length and loop length in words, then
    the signed bytes; the loop part follows the part played once."""
    if len(data) < SAMPLE_HEADER:
        return no_sample()
    length = be16(data, 0) * 2
    loop_length = be16(data, 2) * 2
    loop_start = length if loop_length != 0 else 0
    # Damaged data would have the voice read past the end.
    length = min(length, len(data) - SAMPLE_HEADER)
    if loop_start + loop_length > len(data) - SAMPLE_HEADER:
        loop_length = 0
    return Sample(data, SIGNED_8, 1, SAMPLE_HEADER, length, loop_start, loop_length,
                  NATIVE_RATE)


def wav_sample(data: bytes, loop: bool) -> Sample:
    """A PCM WAV file, 8 or 16 bits, mono or stereo; `loop` repeats all of
    it. Anything else, or a damaged file, is no sample."""
    if len(data) < 12 or data[0:4] != b"RIFF" or data[8:12] != b"WAVE":
        return no_sample()
    pos = 12
    form = -1
    channels = 0
    rate = 0
    while pos + 8 <= len(data):
        tag = data[pos:pos + 4]
        body = pos + 8
        size64 = _le32(data, pos + 4)
        if size64 > int(len(data) - body):
            return no_sample()
        size = int(size64)
        if tag == b"fmt ":
            if size < 16:
                return no_sample()
            channels = _le16(data, body + 2)
            rate64 = _le32(data, body + 4)
            bits = _le16(data, body + 14)
            if _le16(data, body) != 1 or (channels != 1 and channels != 2) \
                    or rate64 > 0x7FFFFFFF:
                return no_sample()
            rate = int(rate64)
            if bits == 8:
                form = UNSIGNED_8
            elif bits == 16:
                form = SIGNED_16
        elif tag == b"data" and form >= 0:
            frame = channels * (2 if form == SIGNED_16 else 1)
            length = size // frame
            return Sample(data, form, channels, body, length, 0, length if loop else 0, rate)
        pos = body + size + (size & 1)
    return no_sample()


class Voice:
    # sample: Sample
    # playing: bool
    # Position in the sample and step per output sample, 16.16 fixed point.
    # pos: int
    # step: int
    # volume: int

    def __init__(self) -> None:
        self.sample = no_sample()
        self.playing = False
        self.pos = 0
        self.step = 0
        self.volume = 0

    def start(self, sample: Sample, rate: int, volume: int) -> None:
        """Plays `sample` at `rate` values a second."""
        self.sample = sample
        # A sample with only a loop part plays its loop.
        self.playing = self.sample.length > 0 or self.sample.loop_length > 0
        self.pos = 0
        self.step = (int(rate) << FRAC_BITS) // int(RATE)
        self.volume = volume

    def stop(self) -> None:
        self.playing = False

    def next(self) -> int:
        """The voice's next output sample, 0 once it has ended."""
        if not self.playing:
            return 0
        sample = self.sample
        at = int(self.pos >> FRAC_BITS)
        if sample.loop_length != 0:
            if at >= sample.loop_start + sample.loop_length:
                at = sample.loop_start
                self.pos = int(at) << FRAC_BITS
        elif at >= sample.length:
            self.playing = False
            return 0
        self.pos += self.step
        # Half scale: the Amiga put two voices on each side of its output.
        return sample.value(at) // 2 * self.volume // 64


class Mixer:
    # Off, nothing is mixed: without somewhere for the sound to go, the
    # voices only keep their state.
    # enabled: bool
    # voices: list[Voice]
    # Output samples rendered so far, and those not yet taken.
    # rendered: int
    # pending: bytearray
    # A music file to be played whole by the sound sink, "" for none, and
    # whether it changed since the sink last looked.
    # track: str
    # track_loop: bool
    # track_changed: bool

    def __init__(self) -> None:
        self.enabled = False
        self.voices = []
        for _ in range(VOICES):
            self.voices.append(Voice())
        self.rendered = 0
        self.pending = bytearray()
        self.track = ""
        self.track_loop = False
        self.track_changed = False

    def play(self, voice: int, sample: Sample, rate: int, volume: int) -> None:
        # A sound that is not there leaves the voice playing what it was,
        # as in rawgl.
        if sample.empty():
            return
        self.voices[voice].start(sample, rate, volume)

    def stop(self, voice: int) -> None:
        self.voices[voice].stop()

    def set_volume(self, voice: int, volume: int) -> None:
        self.voices[voice].volume = volume

    def stop_music(self) -> None:
        for i in range(MUSIC_VOICE, VOICES):
            self.voices[i].stop()

    def play_track(self, path: str, loop: bool) -> None:
        self.track = path
        self.track_loop = loop
        self.track_changed = True

    def stop_all(self) -> None:
        for v in self.voices:
            v.stop()
        if self.track != "":
            self.play_track("", False)

    def render_to(self, now: int) -> None:
        """Mixes the samples up to game time `now`, in milliseconds, as
        signed 16-bit little-endian mono."""
        end = int(now) * int(RATE) // 1000
        if not self.enabled:
            self.rendered = end
            return
        while self.rendered < end:
            total = 0
            for v in self.voices:
                total += v.next()
            if total > 32767:
                total = 32767
            elif total < -32768:
                total = -32768
            self.pending.append(int(total & 0xFF))
            self.pending.append(int((total >> 8) & 0xFF))
            self.rendered += 1

    def take(self) -> bytes:
        """The samples rendered since the last call."""
        out = bytes(self.pending)
        self.pending = bytearray()
        return out
