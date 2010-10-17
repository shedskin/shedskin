#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

# TODO The 47 registers of the VIC are mapped in at $d000. Due to the incomplete address decoding, they are repeated every 64 bytes in the area $d000-$d3ff.

import sys
import time
import timer
import memory

A_X_SPRITE_0 = 0x00
A_Y_SPRITE_0 = 0x01
A_X_SPRITE_1 = 0x02
A_Y_SPRITE_1 = 0x03
A_X_SPRITE_2 = 0x04
A_Y_SPRITE_2 = 0x05
A_X_SPRITE_3 = 0x06
A_Y_SPRITE_3 = 0x07
A_X_SPRITE_4 = 0x08
A_Y_SPRITE_4 = 0x09
A_X_SPRITE_5 = 0x0A
A_Y_SPRITE_5 = 0x0B
A_X_SPRITE_6 = 0x0C
A_Y_SPRITE_6 = 0x0D
A_X_SPRITE_7 = 0x0E
A_Y_SPRITE_7 = 0x0F
A_MSB_X = 0x10
A_CONTROL_1 = 0x11
A_RASTER_COUNTER = 0x12
A_LIGHT_PEN_X = 0x13
A_LIGHT_PEN_Y = 0x14
A_SPRITE_ENABLED = 0x15 # bits
A_CONTROL_2 = 0x16
A_SPRITE_Y_EXPANSION = 0x17
A_MEMORY_POINTERS = 0x18 # VM13..CB11, dummy bit (bits).
A_INTERRUPT_REGISTER = 0x19
A_INTERRUPT_ENABLED = 0x1A
A_SPRITE_DATA_PRIORITY = 0x1B
A_SPRITE_MULTICOLOR = 0x1C
A_SPRITE_X_EXPANSION = 0x1D
A_SPRITE_SPRITE_COLLISION = 0x1E
A_SPRITE_DATA_COLLISION = 0x1F
A_BORDER_COLOR = 0x20
A_BACKGROUND_COLOR_0 = 0x21
A_BACKGROUND_COLOR_1 = 0x22
A_BACKGROUND_COLOR_2 = 0x23
A_BACKGROUND_COLOR_3 = 0x24
A_SPRITE_MULTICOLOR_0 = 0x25
A_SPRITE_MULTICOLOR_1 = 0x26
A_COLOR_SPRITE_0 = 0x27
A_COLOR_SPRITE_1 = 0x28
A_COLOR_SPRITE_2 = 0x29
A_COLOR_SPRITE_3 = 0x2A
A_COLOR_SPRITE_4 = 0x2B
A_COLOR_SPRITE_5 = 0x2C
A_COLOR_SPRITE_6 = 0x2D
A_COLOR_SPRITE_7 = 0x2E

class VIC_II(memory.Memory):
    def __init__(self, MMU, CIA2, char_ROM):
        self.B_can_write = True # in the instance because of ShedSkin
        self.raster_counter = 0
        self.MMU = MMU
        self.char_ROM = char_ROM
        self.CIA2 = CIA2
        self.B_active = True
        self.B_bitmap = False
        self.B_clip_address = False # FIXME default?
        self.B_MCM = False # FIXME default?
        self.text_view = None
        #self.set_control_1(0) # FIXME default.
        #self.set_control_2(0) # FIXME default.

    def increase_raster_position(self):
        self.raster_counter += 5 # 1
        if self.raster_counter >= 255: # FIXME how could this get > 255?
            self.raster_counter = 0
        return True

    def unprepare(self):
        self.text_view.unprepare()

    def set_control_1(self, value):
        self.text_view.first_row = 51 if value & 8 else 55
        self.text_view.last_row = 250 if value & 8 else 246
        self.text_view.viewport_row = value & 7
        value & 16 # DEN
        self.B_bitmap = (value & 32) != 0 # BMM
        self.B_clip_address = (value & 64) != 0 # ECM # bits 9 and 10 low.
        value & 128 # RST8
        self.text_view

    def set_control_2(self, value):
        self.text_view.first_column = 24 if value & 8 else 31
        self.text_view.last_column = 343 if value & 8 else 334
        self.text_view.viewport_column = value & 7
        self.B_MCM = (value & 16) != 0

    def set_memory_pointers(self, value):
        value >>= 1
        CB_13_12_11 = value & 0x7 # character bitmaps.
        # TODO in bitmap mode, CB_13 only! (thus 2KiB/8KiB steps).
        VM_13_12_11_10 = value >> 3 # video matrix (movable in 1KiB steps).
        self.text_view.character_bitmaps_offset = (1 << 11) * CB_13_12_11
        self.text_view.video_offset = (1 << 10) * VM_13_12_11_10
        self.text_view.unprepare()
        code_color = self.VIC_read_memory(0, 1) # ShedSkin
        character_data = self.load_chunk(0, 8 * 256) # ShedSkin

    def load_chunk(self, offset, size):
        #address = VIC_bank_offset + offset
        return [self.VIC_read_memory(offset + i, 1) for i in range(size)]

    def repaint(self):
        self.text_view.VIC_bank = self.CIA2.VIC_bank
        self.text_view.mode = {
            (False, False, False): "normal-text",
            (False, False, True): "multicolor-text",
            (False, True, False): "normal-bitmap",
            (False, True, True): "multicolor-bitmap",
            (True, False, False): "ECM-text",
            (True, False, True): "invalid-1",
            (True, True, False): "invalid-2",
            (True, True, True): "invalid-3",
        }[self.B_clip_address, self.B_bitmap, self.B_MCM]

#        self.text_view.repaint()

    def read_color_RAM(self, address):
        return self.MMU.read_memory(0xD800 + (address & 0x3FF))

    def VIC_read_memory(self, address, size = 1):
        assert(size == 1)
        if (self.CIA2.VIC_bank & 1) == 0: # have Char ROM
            if address >= 0x1000 and address < 0x2000:
                return self.char_ROM.read_memory(address - 0x1000, size) #| (self.read_color_RAM(address) << 8)

        # Video_Matrix|Chargen|Sprite_Data_Pointers|Sprite_Data.

        if self.B_clip_address:
            address = address &~ (1 << 9) &~ (1 << 10) # FIXME does that also mappen with char_ROM?

        # FIXME return self. | (self.read_color_RAM(address) << 8)
        VIC_bank_offset = self.CIA2.VIC_bank * 4096
        return self.MMU.read_memory(address + VIC_bank_offset, size) | (self.read_color_RAM(address) << 8)

    def set_background_color_0(self, value):
        self.text_view.background_color_0 = value & 15

    def set_border_color(self, value):
        self.text_view.border_color = value & 15

    def read_memory(self, address, size = 1):
        assert(size == 1)
        address = address & 0x3F
        # TODO The registers $d01e and $d01f are automatically cleared on reading.
        slots = {
            A_BORDER_COLOR: self.text_view.border_color,
            A_BACKGROUND_COLOR_0: self.text_view.background_color_0,
            A_RASTER_COUNTER: self.raster_counter,
        }
        return slots[address] if address in slots else 0xFF

    def write_memory(self, address, value, size):
        assert(isinstance(value, int))
        # TODO The registers $d01e and $d01f cannot be written.
        address = address & 0x3F
        value = (value)
        # TODO 47 control registers.
        # 34 for sprite control.
        print("VIC-II $%X := %r" % (address, value))
        #time.sleep(5)
        if address == A_CONTROL_1:
            return self.set_control_1(value)
        elif address == A_CONTROL_2:
            return self.set_control_2(value)
        elif address == A_MEMORY_POINTERS:
            return self.set_memory_pointers(value)
        elif address == A_BORDER_COLOR:
            return self.set_border_color(value)
        elif address == A_BACKGROUND_COLOR_0:
            return self.set_background_color_0(value)
        #}.get(address) or ignore)(value)

"""
[$11]=$1B, [$16]=$8: hires text mode (global bg in $21).
[$11]=$1B, [$16]=216: multicolor text mode.
[$11]=$3B, [$16]=8: hires bitmap mode.
[$11]=$3B, [$16]=216: multicolor bitmap mode.
[$11]=$5B, [$16]=8: extended (background color) text mode.
[$16]=5: !!! 
http://codebase64.org/doku.php?id=base:built_in_screen_modes
"""
# memory address $D02F (extra keys). Try to set to something else than $FF. If it works, it's a C128.
