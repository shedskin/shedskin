# Live sound: the mixed samples are piped into the first audio player on the
# system that works, which hands them to the sound server.
from __future__ import annotations

import os
import time
from .popen import DEVNULL, NO_STATUS, PIPE, Popen

from .sound import RATE

# Each reads signed 16-bit little-endian mono at RATE from stdin.
PLAYERS = [
    ["pw-play", f"--rate={RATE}", "--channels=1", "--format=s16", "-"],
    ["paplay", "--raw", f"--rate={RATE}", "--channels=1", "--format=s16le"],
    ["aplay", "-q", "-t", "raw", "-f", "S16_LE", "-r", f"{RATE}", "-c", "1"],
    # SoX, the one of them on macOS (brew install sox).
    ["play", "-q", "-t", "raw", "-r", f"{RATE}", "-e", "signed", "-b", "16", "-c", "1", "-"],
]


# Players that read a music file themselves (Ogg included), by its path. The
# recordings play at a quarter of full volume: rawgl plays them at half the
# volume of the sound effects, which the mixer puts at half scale. The sound
# server keeps a paplay stream's volume for the next one of the same client
# name, which would turn the live sound down too.
FILE_PLAYERS = [
    ["pw-play", "--volume=0.25"],
    ["paplay", "--client-name=Another World music", "--volume=16384"],
    ["play", "-q", "-v", "0.25"],
]

# A player that ends sooner than this after its start, in seconds, is taken
# for one that cannot play.
QUICK_EXIT = 1.0
# Silence the live player gets ahead of the samples when it starts and after
# a pause, 100 ms of it, so a frame that comes late does not leave it empty.
LEAD = bytes(RATE // 10 * 2)


class AudioOut:
    # player: Popen | None
    # False once the player has gone away or been stopped.
    # playing: bool
    # Every player was missing or ended at once.
    # unavailable: bool
    # The next of PLAYERS to try, each tried once; when the player first
    # took samples, negative before; and whether silence is due before the
    # next samples.
    # next_player: int
    # first_write: float
    # lead: bool
    # The player of the music file being played, which the sound server
    # mixes with the rest; it is FILE_PLAYERS[file_player], the first not
    # found unable to play.
    # track: Popen | None
    # track_playing: bool
    # file_player: int
    # track_started: float
    # The file it plays, and whether it starts over when it ends.
    # track_path: str
    # track_loop: bool

    def __init__(self) -> None:
        """Starts the first player that works; without one, sound stays off."""
        # pw-play reads --volume=0.25 with the locale's decimal point.
        os.environ["LC_ALL"] = "C"
        self.player = None
        self.playing = False
        self.unavailable = False
        self.next_player = 0
        self.first_write = -1.0
        self.lead = False
        self.track = None
        self.track_playing = False
        self.file_player = 0
        self.track_started = 0.0
        self.track_path = ""
        self.track_loop = False
        self._start_player()

    def active(self) -> bool:
        return self.playing

    def missing(self) -> bool:
        """Whether no player could play, so the game ran without sound."""
        return self.unavailable

    def write(self, samples: bytes) -> None:
        if len(samples) == 0:
            return
        while self.playing:
            if self._write(samples):
                return
            self._end_player()
            if self.first_write >= 0.0 and time.monotonic() - self.first_write >= QUICK_EXIT:
                # The player went away; the game goes on silently.
                self.playing = False
                return
            self._start_player()

    def resume(self) -> None:
        """After a pause, which has let the player run out of samples."""
        self.lead = True

    def play_track(self, path: str, loop: bool) -> None:
        """Plays the music file at `path` instead of the one playing, over
        and over when `loop`; "" stops it."""
        self._stop_track()
        self.track_path = path
        self.track_loop = loop
        self._start_track()

    def keep_track(self) -> None:
        """Starts a looping track over once its player has finished, and the
        track again with the next player if this one could not play it."""
        track = self.track
        if track is None or not self.track_playing:
            return
        code = track.poll()
        if code == NO_STATUS:
            return
        self.track_playing = False
        if time.monotonic() - self.track_started < QUICK_EXIT:
            if code != 0:
                self.file_player += 1
                self._start_track()
            # Otherwise the track is too short to start over every frame.
            return
        if self.track_loop:
            self._start_track()

    def close(self) -> None:
        self._stop_track()
        self._end_player()
        self.playing = False

    def _start_player(self) -> None:
        self.playing = False
        while self.next_player < len(PLAYERS):
            args = PLAYERS[self.next_player]
            self.next_player += 1
            try:
                self.player = Popen(args, stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)
            except OSError:
                continue
            self.playing = True
            self.first_write = -1.0
            self.lead = True
            return
        self.unavailable = True

    def _write(self, samples: bytes) -> bool:
        """Whether the player took `samples`."""
        player = self.player
        if player is None or player.poll() != NO_STATUS:
            return False
        stdin = player.stdin
        if stdin is None:
            return False
        try:
            if self.lead:
                stdin.write(LEAD)
                self.lead = False
            stdin.write(samples)
            stdin.flush()
        except OSError:
            return False
        if self.first_write < 0.0:
            self.first_write = time.monotonic()
        return True

    def _end_player(self) -> None:
        player = self.player
        if player is None:
            return
        # Stopped at once rather than left to drain what is buffered.
        player.kill()
        player.wait()

    def _start_track(self) -> None:
        if self.track_path == "" or not self.playing:
            return
        while self.file_player < len(FILE_PLAYERS):
            args = []
            for arg in FILE_PLAYERS[self.file_player]:
                args.append(arg)
            args.append(self.track_path)
            try:
                self.track = Popen(args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
            except OSError:
                self.file_player += 1
                continue
            self.track_playing = True
            self.track_started = time.monotonic()
            return

    def _stop_track(self) -> None:
        track = self.track
        if track is None or not self.track_playing:
            return
        track.kill()
        track.wait()
        self.track_playing = False
