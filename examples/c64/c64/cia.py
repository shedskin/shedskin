#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import time

from . import memory
from . import joysticks

A_KEYBOARD_MATRIX_JOYSTICK_2 = 0x00
A_KEYBOARD_KEY_JOYSTICK_1 = 0x01
A_TIMER_A = 0x0E
A_TIMER_B = 0x0F
A_TIME_OF_DAY_TS = 0x08 # in 1/10 s. BCD.
A_TIME_OF_DAY_S = 0x09 # seconds. BCD.
A_TIME_OF_DAY_M = 0x0A # minutes, BCD.
A_TIME_OF_DAY_H = 0x0B # hours, BCD (& AM/PM).
A_SERIAL_SHIFT_REGISTER = 0x0C
A_INTERRUPT_CONTROL_STATUS = 0x0D
B_PORT_A_SERIAL = 0
B_PORT_B_RS232 = 1
B_PORT_A_DATA_DIRECTION = 2
B_PORT_B_DATA_DIRECTION = 3
B_TIMER_A_LOW = 4
B_TIMER_A_HIGH = 5
B_TIMER_B_LOW = 6
B_TIMER_B_HIGH = 7
B_TIME_OF_DAY_TOS = 8
B_TIME_OF_DAY_SEC = 9
B_TIME_OF_DAY_MIN = 0xA
B_TIME_OF_DAY_HOUR = 0xB
B_SERIAL_SHIFT = 0xC
B_INTERRUPT_CONTROL = 0xD
B_TIMER_A_CONTROL = 0xE
B_TIMER_B_CONTROL = 0xF


class Timer(object):
    def __init__(self):
        self.B_active = False
        self.B_indicate_underflow = False
        self.B_underflow_generate_short_signal = 0
        self.B_stop_upon_underflow = False
        self.B_load_start_value = False
        self.B_count_CNT = False # as opposed to system cycles.
        self.B_serial_out = False
        self.B_PAL = False # 0=60Hz, 1=50Hz
    def get_control_mask(self):
        return (1 if self.B_active else 0) + \
               (2 if self.B_indicate_underflow else 0) + \
               (4 if self.B_underflow_generate_short_signal else 0) + \
               (8 if self.B_stop_upon_underflow else 0) + \
               (16 if self.B_load_start_value else 0) + \
               (32 if self.B_count_CNT else 0) + \
               (64 if self.B_serial_out else 0) + \
               (128 if self.B_PAL else 0)

# FIXME implement $DC02 data direction A bits
# FIXME implement $DC03 data direction B bits
class CIA1(memory.Memory):
    def __init__(self):
        memory.Memory.__init__(self)
        self.B_can_write = True # in the instance because of ShedSkin
        self.B_active = True
        self.keyboard_matrix_rows = 0 # FIXME
        self.timer_A = Timer()
        self.timer_B = Timer()
        self.pressed_keys = set("dummy")
        self.pressed_keys.discard("dummy") # Shedskin hint...
        self.joysticks = [joysticks.DigitalJoystick(), joysticks.DigitalJoystick()]
        self.B_interrupt_pending = False
        self.known_keys = set()
        self.A_data_direction = 0
        self.B_data_direction = 0
        for row in self.get_keyboard_matrix():
            for cell in row:
                self.known_keys.add(cell)

    matrix = [ # broken: 1 pound plus
        ["BackSpace", "Return", "Right",  "F7", "F1", "F3", "F5", "Down"],
        ["3", "W", "A", "4", "Z", "S", "E", "Shift_L"],
        ["5", "R", "D", "6", "C", "F", "T", "X"],
        ["7", "Y", "G", "8", "B", "H", "U", "V"],
        ["9", "I", "J", "0", "M", "K", "O", "N"],
        ["+", "P", "L", "-", ".", ":", "@", ","],
        ["pound", "*", ";", "Home", "Shift_R", "=", "grave", "/"], # FIXME should be "pound".
        ["1", "LeftArrow", "Control_L", "2", "space", "Meta_L", "Q", "Break"],
    ]
    def read_memory(self, address, size = 1):
        assert size == 1, "CIA.read_memory size is 1"
        if address == A_KEYBOARD_MATRIX_JOYSTICK_2:
            #if (self.A_data_direction & 31) == 0: # sets the joystick bits to "read". TODO could also be just one of them?
            joystick = self.joysticks[0]
            return (0 if joystick.B_up else 1) | \
                   (0 if joystick.B_down else 2) | \
                   (0 if joystick.B_right else 4) | \
                   (0 if joystick.B_left else 8) | \
                   (0 if joystick.B_fire_1 else 16)
        elif address == A_KEYBOARD_KEY_JOYSTICK_1:
            joystick = self.joysticks[0]
            if (self.A_data_direction & 31) == 0: # disabled keyboard
                return (0 if joystick.B_up else 1) | \
                       (0 if joystick.B_down else 2) | \
                       (0 if joystick.B_right else 4) | \
                       (0 if joystick.B_left else 8) | \
                       (0 if joystick.B_fire_1 else 16)
            # FIXME the other joystick.
            # TODO: artificially make Up and Left work.
            if self.keyboard_matrix_rows != 0: # is not None:
                #print("we think keys", self.pressed_keys)
                v = 0
                #matrix = self.__class__.matrix
                for row in range(0, 8):
                    if (self.keyboard_matrix_rows & (1 << row)) != 0: # client wants to know
                        columns = CIA1.matrix[row]
                        #print("possible", rows)
                        for column_i, cell in enumerate(columns):
                            if cell in self.pressed_keys: # or (isinstance(cell, int) and cell < 128 and (cell | 0x20) in self.pressed_keys):
                                #print("YESSS, matched", cell)
                                v |= (1 << column_i)
                #print("INVKEY", v)
                return 255 - v

            # return bits cleared in rows where a key is pressed in self.keyboard_matrix_column.
            return 0xFF # nothing.
        elif address == A_TIMER_A:
            return self.timer_A.get_control_mask()
        elif address == A_TIMER_B:
            return self.timer_B.get_control_mask()
        elif address == A_INTERRUPT_CONTROL_STATUS:
            if self.B_interrupt_pending:
                #print("yes, we had an interrupt")
                self.B_interrupt_pending = False
                return 1<<7 # FIXME the others
            return 0
        elif address == B_PORT_A_DATA_DIRECTION:
            return self.A_data_direction
        elif address == B_PORT_B_DATA_DIRECTION:
            return self.B_data_direction
        else:
            #print(hex(address))
            assert False, "CIA address is known"

    def get_keyboard_matrix(self):
        return CIA1.matrix

    def write_memory(self, address, value, size):
        #print("CIA#1 $%X := %r" % (address, value))
        # TODO address == A_TIMER_A bit 0: active or not.
        if address == A_KEYBOARD_MATRIX_JOYSTICK_2:
            self.keyboard_matrix_rows = ~(value & 0xFF)
            # other is paddle.
        elif address == B_PORT_A_DATA_DIRECTION:
            # POKE 56322,224 deactivated the keyboard
            self.A_data_direction = value
        elif address == B_PORT_B_DATA_DIRECTION:
            self.B_data_direction = value

    def handle_key_press(self, name):
        if name not in self.pressed_keys:
            if name == "Down":
                self.joysticks[0].B_down = True
            elif name == "Up":
                self.joysticks[0].B_up = True
            elif name == "Left":
                self.joysticks[0].B_left = True
            elif name == "Right":
                self.joysticks[0].B_right = True
            elif name == "Shift_R":
                self.joysticks[0].B_fire_1 = True
            self.B_interrupt_pending = True
            self.pressed_keys.add(name)
        return name in self.known_keys

    def handle_key_release(self, name):
        self.B_interrupt_pending = True
        if name in self.pressed_keys:
            if name == "Down":
                self.joysticks[0].B_down = False
            elif name == "Up":
                self.joysticks[0].B_up = False
            elif name == "Left":
                self.joysticks[0].B_left = False
            elif name == "Right":
                self.joysticks[0].B_right = False
            elif name == "Shift_R":
                self.joysticks[0].B_fire_1 = False
        self.pressed_keys.discard(name)
        return name in self.known_keys
class SerialLine(object): # TODO defaults.
    def __init__(self):
        self.B_clock_IN = False
        self.B_data_IN = False
    def get_control_mask(self):
        return \
               (4 if "TXD OUT" == "False" else 0) + \
               (8 if "ATN OUT" == "False" else 0) + \
               (16 if "CLOCK OUT" == "False" else 0) + \
               (32 if "DATA OUT" == "False" else 0) + \
               (64 if self.B_clock_IN else 0) + \
               (128 if self.B_data_IN else 0)
class RS232Line(object):
    def get_control_mask(self):
        return 0 # FIXME
class CIA2(memory.Memory):
    def __init__(self):
        memory.Memory.__init__(self)
        self.B_can_write = True # in the instance because of ShedSkin
        self.VIC_bank = 0
        self.B_active = True
        self.serial = SerialLine()
        self.RS232 = RS232Line()
    def read_memory(self, address, size = 1):
        assert size == 1, "CIA2.read_memory size is 1"
        address = address & 0xF
        if address >= B_TIME_OF_DAY_TOS and address < 0xC:
            t = time.time()
            gregorian_time = time.localtime(t) # FIXME setable?
            if address == B_TIME_OF_DAY_SEC:
                return gregorian_time.tm_sec
            if address == B_TIME_OF_DAY_MIN:
                return gregorian_time.tm_min
            if address == B_TIME_OF_DAY_HOUR:
                return gregorian_time.tm_hour
        return {
            B_PORT_A_SERIAL: (3 - self.VIC_bank) + self.serial.get_control_mask(),
            B_PORT_B_RS232: self.RS232.get_control_mask(),
            B_PORT_A_DATA_DIRECTION: 0, # FIXME
            B_PORT_B_DATA_DIRECTION: 0, # FIXME
            B_TIMER_A_LOW: 0, # FIXME
            B_TIMER_A_HIGH: 0, # FIXME
            B_TIMER_B_LOW: 0, # FIXME
            B_TIMER_B_HIGH: 0, # FIXME
            B_TIME_OF_DAY_TOS: 0, # FIXME
            #B_TIME_OF_DAY_SEC: gregorian_time.tm_sec,
            #B_TIME_OF_DAY_MIN: gregorian_time.tm_min,
            #B_TIME_OF_DAY_HOUR: gregorian_time.tm_hour,
            B_SERIAL_SHIFT: 0, # FIXME
            B_INTERRUPT_CONTROL: 0, # FIXME
            B_TIMER_A_CONTROL: 0, # FIXME
            B_TIMER_B_CONTROL: 0, # FIXME
        }[address]
        #assert False, "CIA2.read_memory address is known"
    def write_memory(self, address, value, size):
        #print("CIA#2 $%X := %r" % (address, value))
        if address == 0:
            self.VIC_bank = 3 - (value & 3) # TODO emit notification?
            # TODO map Char ROM into VIC in banks 0 and 2 at $1000.
            # TODO serial
