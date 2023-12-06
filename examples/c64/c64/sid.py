#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

# http://www.waitingforfriday.com/index.php/Commodore_SID_6581_Datasheet

import sys

from . import memory

# write-only
A_VOICE_1_FREQUENCY_LOW=0x00 # write-only
A_VOICE_1_FREQUENCY_HIGH=0x01 # write-only
A_VOICE_1_PULSE_WIDTH_LOW = 0x02 # write-only
A_VOICE_1_PULSE_WIDTH_HIGH = 0x03 # just 4 bits used
A_VOICE_1_CONTROL = 0x04
A_VOICE_1_ATTACK_DECAY = 0x05
A_VOICE_1_SUSTAIN_RELEASE = 0x06
A_FILTER_CUTOFF_L = 0x15
A_FILTER_CUTOFF_H = 0x16
A_FILTER_CONTROL = 0x17
A_VOLUME_FILTER_MODES = 0x18
A_VOICE_3_WAVEFORM_OUTPUT = 0x1B
A_VOICE_3_ADSR_OUTPUT = 0x1C
# 0x19, 0x1A paddle read
attack_rates = [2, 8, 16, 24, 38, 56, 68, 80, 100, 250, 500, 800, 1000, 3000, 5000, 8000] # ms
release_rates = [6, 24, 48, 72, 114, 168, 204, 240, 300, 750, 1500, 2400, 3000, 9000, 15000, 24000] # ms
decay_rates = release_rates

F = 44100 # our output frequency.

'''
class Oscillator(object):
    def __init__(self, frequency, B_triangle, B_saw, B_rectangle):
        self.frequency = frequency
        self.in_stage_point = 0
        self.B_triangle = B_triangle
        self.B_saw = B_saw
        self.B_rectangle = B_rectangle
        self.frame_count = int(F / frequency)
        self.samples = frame_count * [0.0] # FIXME round up and introduce a correction thingie
    def next(self):
        if self.in_stage_point >= self.frame_count:
            self.in_stage_point = 0
        yield 1.0 # FIXME
        """def iter(self):
        while True:
            while self.in_stage_point < self.frame_count:
                yield 1.0 # FIXME
                self.in_stage_point += 1
            self.in_stage_point = 0"""
class EnvelopeGenerator(object):
    def __init__(self, attack_rate, decay_rate, sustain, release_rate):
        self.stage = 0 # attack
        self.in_stage_point = 0
        self.attack_frame_count = int(attack_rate * F / 1000) # FIXME round up etc
        self.decay_frame_count = int(decay_rate * F / 1000) # FIXME round up etc
        self.sustain = sustain
        self.release_frame_count = int(release_rate * F / 1000) # FIXME round up etc
        self.frame_counts = [self.attack_frame_count, self.decay_frame_count, self.release_frame_count, -1]
        self.amplification = 0.0
    def set_stage(self, value):
        self.stage = value
    def next(self):
        while self.frame_counts[self.stage] != -1 and self.in_stage_point >= self.frame_counts[self.stage]:
            self.in_stage_point = 0
            self.stage += 1
        yield 1.0 # FIXME
        self.in_stage_point += 1
        """def iter(self):
        while True:
            while self.frame_counts[self.stage] == -1 or self.in_stage_point < self.frame_counts[self.stage]:
                yield 1.0 # FIXME
                self.in_stage_point += 1
            self.in_stage_point = 0
            self.stage += 1"""
'''
class Voice(object):
    def __init__(self):
        self.raw_frequency = 0
        self.frequency = 0
        self.raw_control = 0
        self.attack_rate = 2 
        self.decay_rate = 6
        self.sustain = 0 # of 15
        self.release_rate = 6
        self.amplitude = 0 # current one
        self.raw_pulse_width = 0
        self.pulse_width = 0
    def set_raw_frequency(self, value):
        self.raw_frequency = value
        Fclk = 1000000.0
        Fout = (value * Fclk/16777216) # Hz 
        self.frequency = Fout
    def set_raw_pulse_width(self, value):
        self.raw_pulse_width = value
        PWout = (value/40.95) # % # for pulse only.
        self.pulse_width = PWout
    def set_raw_control(self, value):
        """
        Bit #0: 0 = Voice off, Release cycle; 1 = Voice on, Attack-Decay-Sustain cycle.
        Bit #1: 1 = Synchronization enabled (hard sync fundamental frequency voice 1 to fundamental frequency voice 3 or 2)
        Bit #2: 1 = Ring modulation enabled (ring instead of triangle, combine voices).
        Bit #3: 1 = Disable voice, reset noise generator.
        Bit #4: 1 = Triangle waveform enabled.
        Bit #5: 1 = Saw waveform enabled.
        Bit #6: 1 = Rectangle waveform enabled.
        Bit #7: 1 = Noise enabled.
        """
        self.raw_control = value
    def set_raw_attack(self, value):
        self.attack_rate = attack_rates[value]
    def set_raw_decay(self, value):
        self.decay_rate = decay_rates[value]
    def set_raw_sustain(self, value):
        self.sustain = value
    def set_raw_release(self, value):
        self.release_rate = release_rates[value]
class SID(memory.Memory):
    def __init__(self):
        self.B_active = True
        self.B_can_write = True # in the instance because of ShedSkin
        self.voices = [Voice(), Voice(), Voice()]
        self.raw_filter_cutoff = 0
        self.raw_filter_control = 0
        self.raw_filter_mode = 0
        self.raw_volume = 0
    def set_raw_volume(self, value):
        self.raw_volume = value
    def set_raw_filter_cutoff(self, value):
        self.raw_filter_cutoff = value
    def set_raw_filter_control(self, value):
        """
      Bit #0: 1 = Voice #1 filtered.
      Bit #1: 1 = Voice #2 filtered.
      Bit #2: 1 = Voice #3 filtered.
      Bit #3: 1 = External voice filtered.
      Bits #4-#7: Filter resonance.
        """
        self.raw_filter_control = value
    def set_raw_filter_mode(self, value):
        """
      Bit #0: 1 = Low pass filter enabled.
      Bit #1: 1 = Band pass filter enabled.
      Bit #2: 1 = High pass filter enabled.
      Bit #3: 1 = Voice #3 disabled.
        """
        self.raw_filter_mode = value
    #@takes(int, int)
    def read_memory(self, address, size):
        address = address & 0x1F
        # TODO A_VOICE_3_WAVEFORM_OUTPUT, A_VOICE_3_ADSR_OUTPUT
        sys.stderr.write("error: SID: cannot read register $%X.\n" % address)
        return 0xFF
    #@takes(int, int)
    def write_memory(self, address, value, size):
        assert size == 1, "SID.write_memory: size is 1"
        address = address & 0x1F
        if address < 0x15:
            voice_index = address // 7
            voice = self.voices[voice_index]
            if address == 0:
                voice.set_raw_frequency((voice.raw_frequency & 0xFF00) | value)
            elif address == 1:
                voice.set_raw_frequency((voice.raw_frequency & 0xFF) | (value << 8))
            elif address == 2:
                voice.set_raw_pulse_width((voice.raw_pulse_width & 0xFF00) | value)
            elif address == 3:
                voice.set_raw_pulse_width((voice.raw_pulse_width & 0xFF) | ((value & 0xF) << 8))
            elif address == 4:
                voice.set_raw_control(value)
            elif address == 5:
                voice.set_raw_attack(value >> 4)
                voice.set_raw_decay(value & 0xF)
            elif address == 6:
                voice.set_raw_sustain(value >> 4)
                voice.set_raw_release(value & 0xF)
        elif address == A_FILTER_CUTOFF_L:
            self.set_raw_filter_cutoff((self.raw_filter_cutoff & 0xFF8) | (value & 0x7))
        elif address == A_FILTER_CUTOFF_H:
            self.set_raw_filter_cutoff((self.raw_filter_cutoff & 0x7) | (value << 3))
        elif address == A_FILTER_CONTROL:
            self.set_raw_filter_control(value)
        elif address == A_VOLUME_FILTER_MODES:
            self.set_raw_volume(value & 0xF)
            self.set_raw_filter_mode(value >> 4)
        #print("SID $%X := %r" % (address, value))
