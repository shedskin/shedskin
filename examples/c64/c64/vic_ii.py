#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

# TODO The 47 registers of the VIC are mapped in at $d000. Due to the incomplete address decoding, they are repeated every 64 bytes in the area $d000-$d3ff.


from . import memory
from .sprite import SPRITE_COUNT
from . import palette
from . import screens

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
A_INTERRUPT_STATUS = 0x19
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

class Settings(object):
    def __init__(self): #, VIC):
        #self.VIC = VIC
        self.raw_memory_pointers = 0
        self.first_column = 0
        self.mode = 0
        self.first_row = 0
        self.last_column = 0
        self.last_row = 0
        self.character_bitmaps_offset = 0 # that's wrong.
        self.old_VIC_bank = -1
        self.VIC_bank = 0
        self.border_color = 0
        self.background_color_0 = 0
        self.background_color_1 = 0
        self.background_color_2 = 0
        self.background_color_3 = 0
        self.video_offset = 0
        self.viewport_row = 0
        self.sprite_priority = 0 # the ones that have bit value= 1 are in the back.
        self.sprite_enabled = 0 # bitmask
        self.sprite_primary_color = SPRITE_COUNT * [0]
        self.sprite_multicolor_enabled = 0 # bitmask
        self.sprite_multicolor_0 = 0
        self.sprite_multicolor_1 = 0
        self.sprite_expand_horizontally = 0 #bitmask
        self.sprite_expand_vertically = 0 # bitmask
        self.sprite_X = SPRITE_COUNT * [0]
        self.sprite_Y = SPRITE_COUNT * [0]
        #self.controls = controls
        #self.controls.handle_key_press("foo")
        #self.controls.handle_key_release("bar")

    #def repaint(self):
    #    pass
    def unprepare(self):
        self.old_VIC_bank = -1

class VIC_II(memory.Memory):
    def __init__(self, C64, MMU, CIA2, char_ROM):
        self.B_can_write = True # in the instance because of ShedSkin
        self.MMU = MMU
        self.C64 = C64
        self.char_ROM = char_ROM
        self.CIA2 = CIA2
        self.B_active = True
        self.B_bitmap = False
        self.control_1 = 0
        self.control_2 = 0
        self.B_clip_address = False # FIXME default?
        self.B_MCM = False # FIXME default?
        self.props = Settings()
        self.MSB_X = 0
        #self.set_control_1(0) # FIXME default.
        #self.set_control_2(0) # FIXME default.
        palette.get_RGBA32_pixel(0)
        self.screen = screens.Screen(self, CIA2)
        self.screen.get_rendered_pixbuf() # ShedSkin
    def increase_raster_position(self):
        self.screen.increase_raster_position()
        if self.screen.raw_interrupt_status != 0 and self.screen.B_enable_raster_interrupt:
            self.C64.cause_interrupt()
        return True
    def unprepare(self):
        self.props.unprepare()
    def set_control_1(self, value):
        self.control_1 = value
        self.props.first_row = (0) + (51 if value & 8 else 55) # set: 25 lines.
        self.props.last_row = (0) + (250 if value & 8 else 246)
        self.props.viewport_row = value & 7
        value & 16 # DEN
        self.B_bitmap = (value & 32) != 0 # BMM
        self.B_clip_address = (value & 64) != 0 # ECM # bits 9 and 10 low.
        #value & 128 # RST8 # TODO this is also used for multicolor bitmap mode
        old_mode = self.props.mode
        self.props.mode = (self.props.mode & 4) | ((value >> 5) & 3)
        #self.props.bitmap_mode = (1 if self.B_bitmap else 0) + 2 * (1 if self.B_clip_address else 0)
        self.screen.breakpoint_raster_position = (self.screen.breakpoint_raster_position & 0xFF) | (value & 128)
#        if old_mode != self.props.mode:
#            print("new mode is $%X" % self.props.mode)
            #time.sleep(10)

    def set_control_2(self, value):
        self.control_2 = value
        self.props.first_column = 24 if value & 8 else 31
        self.props.last_column = 343 if value & 8 else 334
        self.props.viewport_column = value & 7
        self.B_MCM = (value & 16) != 0
        old_mode = self.props.mode
        self.props.mode = (self.props.mode & 3) | (4 if self.B_MCM else 0)
#        if old_mode != self.props.mode:
#            print("new mode is $%X" % self.props.mode)
            #time.sleep(10)
        # TODO 32, 64, 128

    def set_memory_pointers(self, value):
        self.raw_memory_pointers = value
        value >>= 1
        CB_13_12_11 = value & 0x7 # character bitmaps or bitmaps.
        # TODO in bitmap mode, CB_13 only! (thus 2KiB/8KiB steps).
        VM_13_12_11_10 = value >> 3 # video matrix (movable in 1KiB steps).
        self.props.character_bitmaps_offset = (1 << 11) * CB_13_12_11
        self.props.video_offset = (1 << 10) * VM_13_12_11_10
        self.props.unprepare()
        if False: # ShedSkin
            code_color = self.VIC_read_memory(0, 1) # ShedSkin
            character_data = self.load_chunk(0, 8 * 256) # ShedSkin
            character_data = self.load_12_chunk(0, 8 * 256) # ShedSkin

    def load_chunk(self, offset, size):
        #address = VIC_bank_offset + offset
        return [self.VIC_read_memory(offset + i, 1) for i in range(size)]

    def load_12_chunk(self, offset, size):
        #address = VIC_bank_offset + offset
        return [self.VIC_read_memory(offset + i, 2) for i in range(size)]

    def repaint(self):
        self.props.VIC_bank = self.CIA2.VIC_bank
        #self.props.repaint()

    def read_color_RAM(self, address):
        return self.MMU.read_memory(0xD800 + (address & 0x3FF))

    def VIC_read_memory(self, address, size = 1):
        if (self.CIA2.VIC_bank & 1) == 0: # have Char ROM
            if address >= 0x1000 and address < 0x2000:
                assert size == 1, "VIC_II.VIC_read_memory: address within char ROM"
                return self.char_ROM.read_memory(address & 0xFFF, size) #| (self.read_color_RAM(address) << 8)

        # Video_Matrix|Chargen|Sprite_Data_Pointers|Sprite_Data.

        if self.B_clip_address:
            address = address &~ (1 << 9) &~ (1 << 10) # FIXME does that also mappen with char_ROM?

        # FIXME return self. | (self.read_color_RAM(address) << 8)
        VIC_bank_offset = self.CIA2.VIC_bank * 16384 # TODO invalidate all the sprites once this changes.
        #assert(size == 2)
        return self.MMU.read_memory((address & 0x3FFF) | VIC_bank_offset, 1) | (((self.read_color_RAM(address) & 0xFF) << 8) if size > 1 else 0)

    def set_background_color_0(self, value):
        self.props.background_color_0 = value & 15

    def set_background_color_1(self, value):
        self.props.background_color_1 = value & 15

    def set_background_color_2(self, value):
        self.props.background_color_2 = value & 15

    def set_background_color_3(self, value):
        self.props.background_color_3 = value & 15

    def set_sprite_priority(self, value):
        self.props.sprite_priority = value

    def set_sprite_enabled(self, value):
        self.props.sprite_enabled = value

    def set_sprite_multicolor_0(self, value):
        self.props.sprite_multicolor_0 = value

    def set_sprite_multicolor_1(self, value):
        self.props.sprite_multicolor_1 = value

    def set_border_color(self, value):
        self.props.border_color = value & 15

    def set_sprite_primary_color(self, index, value):
        self.props.sprite_primary_color[index] = value

    def set_sprite_multicolor_enabled(self, value):
        mask = self.props.sprite_multicolor_enabled ^ value
        self.props.sprite_multicolor_enabled = value

    def set_sprite_expand_horizontally(self, value):
        mask = self.props.sprite_expand_horizontally ^ value
        self.props.sprite_expand_horizontally = value

    def set_sprite_expand_vertically(self, value):
        mask = self.props.sprite_expand_vertically ^ value
        self.props.sprite_expand_vertically = value

    def set_sprite_X(self, index, value):
        self.props.sprite_X[index] = value | (256 * ((self.MSB_X & (1 << index)) and 1))

    def set_MSB_X(self, value):
        self.MSB_X = value
        for index in range(8):
            self.props.sprite_X[index] = (self.props.sprite_X[index] & 0xFF) | (256 * ((self.MSB_X & (1 << index)) and 1))

    def set_sprite_Y(self, index, value):
        self.props.sprite_Y[index] = value

    def read_memory(self, address, size = 1):
        assert size == 1, "VIC_II.read_memory: size==1"
        address = address & 0x3F
        # TODO The registers $d01e and $d01f are automatically cleared on reading.
        self.control_1 = (self.control_1 & 127) | ((self.screen.client_raster_position & 0x100) >> 1)
        slots = {
            A_BORDER_COLOR: self.props.border_color,
            A_BACKGROUND_COLOR_0: self.props.background_color_0,
            A_BACKGROUND_COLOR_1: self.props.background_color_1,
            A_BACKGROUND_COLOR_2: self.props.background_color_2,
            A_BACKGROUND_COLOR_3: self.props.background_color_3,
            A_RASTER_COUNTER: self.screen.client_raster_position & 0xFF,
            A_X_SPRITE_0: self.props.sprite_X[0] & 0xFF,
            A_Y_SPRITE_0: self.props.sprite_Y[0],
            A_X_SPRITE_1: self.props.sprite_X[1] & 0xFF,
            A_Y_SPRITE_1: self.props.sprite_Y[1],
            A_X_SPRITE_2: self.props.sprite_X[2] & 0xFF,
            A_Y_SPRITE_2: self.props.sprite_Y[2],
            A_X_SPRITE_3: self.props.sprite_X[3] & 0xFF,
            A_Y_SPRITE_3: self.props.sprite_Y[3],
            A_X_SPRITE_4: self.props.sprite_X[4] & 0xFF,
            A_Y_SPRITE_4: self.props.sprite_Y[4],
            A_X_SPRITE_5: self.props.sprite_X[5] & 0xFF,
            A_Y_SPRITE_5: self.props.sprite_Y[5],
            A_X_SPRITE_6: self.props.sprite_X[6] & 0xFF,
            A_Y_SPRITE_6: self.props.sprite_Y[6],
            A_X_SPRITE_7: self.props.sprite_X[7] & 0xFF,
            A_Y_SPRITE_7: self.props.sprite_Y[7],
            A_MSB_X: self.MSB_X,
            A_CONTROL_1: self.control_1,
            #A_LIGHT_PEN_X = 0x13
            #A_LIGHT_PEN_Y = 0x14
            A_SPRITE_ENABLED: self.props.sprite_enabled,
            A_CONTROL_2: self.control_2,
            A_SPRITE_Y_EXPANSION: self.props.sprite_expand_vertically,
            A_MEMORY_POINTERS: self.raw_memory_pointers,
            A_INTERRUPT_STATUS: self.screen.raw_interrupt_status,
            A_INTERRUPT_ENABLED: (1 if self.screen.B_enable_raster_interrupt else 0) |
            (2 if self.screen.B_enable_sprite_background_collision_interrupt else 0) |
            (4 if self.screen.B_enable_sprite_sprite_collision_interrupt else 0),
            A_SPRITE_DATA_PRIORITY: self.props.sprite_priority,
            A_SPRITE_MULTICOLOR: self.props.sprite_multicolor_enabled,
            A_SPRITE_X_EXPANSION: self.props.sprite_expand_horizontally,
            #A_SPRITE_SPRITE_COLLISION = 0x1E
            #A_SPRITE_DATA_COLLISION = 0x1F
            #A_BACKGROUND_COLOR_1 = 0x22
            #A_BACKGROUND_COLOR_2 = 0x23
            #A_BACKGROUND_COLOR_3 = 0x24
            A_SPRITE_MULTICOLOR_0: self.props.sprite_multicolor_0,
            A_SPRITE_MULTICOLOR_1: self.props.sprite_multicolor_1,
            A_COLOR_SPRITE_0: self.props.sprite_primary_color[0],
            A_COLOR_SPRITE_1: self.props.sprite_primary_color[1],
            A_COLOR_SPRITE_2: self.props.sprite_primary_color[2],
            A_COLOR_SPRITE_3: self.props.sprite_primary_color[3],
            A_COLOR_SPRITE_4: self.props.sprite_primary_color[4],
            A_COLOR_SPRITE_5: self.props.sprite_primary_color[5],
            A_COLOR_SPRITE_6: self.props.sprite_primary_color[6],
            A_COLOR_SPRITE_7: self.props.sprite_primary_color[7],
        }
        return slots[address] if address in slots else 0xFF

    def write_memory(self, address, value, size):
        assert isinstance(value, int), "VIC_II.write_memory: value is an integer"
        # TODO The registers $d01e and $d01f cannot be written.
        address = address & 0x3F
        value = (value)
        # TODO 47 control registers.
        # 34 for sprite control.
        #print("VIC-II $%X := %r" % (address, value))
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
        elif address == A_BACKGROUND_COLOR_1:
            return self.set_background_color_1(value)
        elif address == A_BACKGROUND_COLOR_2:
            return self.set_background_color_2(value)
        elif address == A_BACKGROUND_COLOR_3:
            return self.set_background_color_3(value)
        elif address == A_SPRITE_DATA_PRIORITY:
            return self.set_sprite_priority(value)
        elif address == A_SPRITE_ENABLED:
            return self.set_sprite_enabled(value)
        elif address == A_COLOR_SPRITE_0:
            return self.set_sprite_primary_color(0, value)
        elif address == A_COLOR_SPRITE_1:
            return self.set_sprite_primary_color(1, value)
        elif address == A_COLOR_SPRITE_2:
            return self.set_sprite_primary_color(2, value)
        elif address == A_COLOR_SPRITE_3:
            return self.set_sprite_primary_color(3, value)
        elif address == A_COLOR_SPRITE_4:
            return self.set_sprite_primary_color(4, value)
        elif address == A_COLOR_SPRITE_5:
            return self.set_sprite_primary_color(5, value)
        elif address == A_COLOR_SPRITE_6:
            return self.set_sprite_primary_color(6, value)
        elif address == A_COLOR_SPRITE_7:
            return self.set_sprite_primary_color(7, value)
        elif address == A_SPRITE_MULTICOLOR:
            return self.set_sprite_multicolor_enabled(value)
        elif address == A_SPRITE_MULTICOLOR_0:
            return self.set_sprite_multicolor_0(value)
        elif address == A_SPRITE_MULTICOLOR_1:
            return self.set_sprite_multicolor_1(value)
        elif address == A_SPRITE_X_EXPANSION:
            return self.set_sprite_expand_horizontally(value)
        elif address == A_SPRITE_Y_EXPANSION:
            return self.set_sprite_expand_vertically(value)
        elif address == A_RASTER_COUNTER:
            self.screen.breakpoint_raster_position = (self.screen.breakpoint_raster_position & 0x100) | value
        elif address == A_INTERRUPT_STATUS:
            self.screen.raw_interrupt_status = self.screen.raw_interrupt_status & (value ^ 0xFF)
        elif address == A_INTERRUPT_ENABLED:
            self.screen.B_enable_raster_interrupt = (value & 1) != 0
            self.screen.B_enable_sprite_background_collision_interrupt = (value & 2) != 0
            self.screen.B_enable_sprite_sprite_collision_interrupt = (value & 4) != 0
            # TODO light pen
        elif address < 0x10: # coordinates
            if address & 1:
                return self.set_sprite_Y(address >> 1, value)
            else:
                return self.set_sprite_X(address >> 1, value)
        elif address == A_MSB_X:
            return self.set_MSB_X(value)
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
if __name__ == "__main__":
    pass
