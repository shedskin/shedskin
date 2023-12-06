#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.


from . import cpu
from . import vic_ii
from . import sid
from . import cia
from . import tape

from . import memory
from .symbols import *

SPRITE_COUNT = 8


class CPUPort(memory.Memory): # $0..$1
    def __init__(self, MMU):
        memory.Memory.__init__(self)
        self.B_can_write = True # in the instance because of ShedSkin
        self.B_active = True
        self.MMU = MMU
        self.data_direction = 0x2F # RW for port below
        self.port = 0
        """
        port:
            bits 0..2: configuration for ROM memory:
                bx00: RAM visible in all areas.
                bx01: RAM visible at $A000..BFFF, $E000..$FFFF.
                bx10: RAM visible at $A000..BFFF, KERNAL ROM AT $E000..$FFFF.
                bx11: BASIC ROM visible at $A000..BFFF, KERNAL ROM AT $E000..$FFFF.
                b0xx: Character ROM visible at $D000..$DFFF except for b000.
                b1xx: IO area visible at $D000..$DFFF except for b100.
            bit 3: datasette output signal level
            bit 4: datasette button status (inverse).
            bit 5: motor control (inverse).
        """
        self.set_port(0x37)

    def read_memory(self, address, size = 1):
        assert size == 1, "CPUPort.read_memory size=1"
        if address == 0:
            return self.data_direction
        elif address == 1:
            return self.port
        else:
            assert False, "CPUPort.read_memory address is known"
            return 0

    def write_memory(self, address, value, size):
        assert isinstance(value, int), "CPUPort.write_memory value written is an integer"
        if address == 0:
            self.data_direction = value # FIXME protect?
        elif address == 1:
            self.set_port(value)
        else:
            assert False, "CPUPort.write_memory address is known"

    def set_port(self, value):
        if self.port == value:
            return
#        if value & 32:
#            print("cassette motor off")
#        else:
#            print("cassette motor on")
        self.port = value
        B_all_visible = (value & 3) == 0 # all RAM
        low = (value & 3)
        B_A000_RAM = low == 1 or low == 0x10 or B_all_visible
        B_E000_RAM = low == 1 or B_all_visible
        B_D000_Character = (value & 4) == 0 and not B_all_visible
        B_D000_IO = (value & 4) != 0 and not B_all_visible
        self.MMU.set_overlay_active("basic", not B_A000_RAM)
        self.MMU.set_overlay_active("chargen", B_D000_Character)
        self.MMU.set_overlay_active("vic", B_D000_IO)
        self.MMU.set_overlay_active("sid", B_D000_IO)
        self.MMU.set_overlay_active("cia1", B_D000_IO)
        self.MMU.set_overlay_active("cia2", B_D000_IO)
        self.MMU.set_overlay_active("kernal", not B_E000_RAM)
        #if B_E000_RAM:
        #    sys.stderr.write("warning: KERNAL disabled!!!\n")
            #time.sleep(5.0)

class C64(object):
    def __init__(self):
        self.interrupt_clock = 0
        self.VIC_clock = 0
        self.CPU = cpu.CPU()
        MMU = self.CPU.MMU
        address = 0
        # power-up pattern:
        for i in range(512):
            for b in range(64):
                MMU.write_memory(address, 0, 1)
                address += 1
            for b in range(64):
                MMU.write_memory(address, 0xFF, 1)
                address += 1

        self.ROMs = [
            ("basic",   (0xA000, 0xC000)),
            ("chargen", (0xD000, 0xE000)),
            #("dos1541", (0xD000, 0xE000)),
            ("kernal",  (0xE000, 0x10000)),
        ]

        char_ROM = None
        for ROM, range_1 in self.ROMs:
            value = open("ROM/bin/C64/" + ROM, "rb").read()
            size = range_1[1] - range_1[0]
            #print(ROM)
            assert size == len(value), "C64 ROM is not truncated"
            # TODO how to do this in a nicer way?
            if ROM == "kernal":
                hardware_vectors = value[-6:]
                value = value[:-6]
                for i in range(6):
                    self.CPU.MMU.write_memory(0xFFFA + i, hardware_vectors[i], 1)
                # patch ROM so BRK instructions are at strategic places.
                xvalue = [c for c in value]
                for address in tape.get_hooks():
                    assert address >= 0xE000, "hooks are actually within the KERNAL"
                    xvalue[address - 0xE000] = 0 # BRK
                xvalue[0xE4E2 - 0xE000] = 0x60 # get rid of tape delay
                value = bytes(xvalue)
            ROM_obj = self.CPU.MMU.map_ROM(ROM, range_1[0], value, ROM != "chargen")
            if ROM == "chargen":
                char_ROM = ROM_obj


        cia1 = cia.CIA1()
        self.CIA1 = cia1
        cia2 = cia.CIA2()
        self.CIA2 = cia2
        vic = vic_ii.VIC_II(self, self.CPU.MMU, cia2, char_ROM)
        self.VIC = vic
        self.CPU.MMU.map_IO("cia2", (0xDD00, 0xDE00), cia2)
        self.CPU.MMU.map_IO("vic", (0xD000, 0xD400), vic)
        self.CPU.MMU.map_IO("sid", (0xD400, 0xD800), sid.SID())
        self.CPU.MMU.map_IO("cia1", (0xDC00, 0xDD00), cia1)
        self.CPU.MMU.map_IO("cpu", (0x0000, 0x0002), CPUPort(self.CPU.MMU))
        vic.repaint() # ShedSkin
        vic.unprepare() # memory is not initialized yet, so unprepare...
        MMU = self.CPU.MMU
        #MMU.write_memory(0xFFFA, b"\x43\xFE\xE2\xFC\x48\xFF") # FIXME endianness.
        #self.CPU.BRK(0)
        # done automatically on "BRK"?
        self.CPU.write_register(S_PC, (MMU.read_memory(0xFFFC, 2)))
        self.fire_timer() # ShedSkin
        #self.controls = gmonitor.Controls(self)
        #self.controls = {}

    def set_tape_image_name(self, name, format):
        tape.set_image_name(name, format)

    def run(self):
        while True: # TODO terminate?
            self.iterate()

    def fire_timer(self):
        for n in range(19800):
            self.iterate()
            self.interrupt_clock += 1
            self.VIC_clock += 1
            if self.VIC_clock >= 66: # 6:
                self.VIC_clock = 0
                self.VIC.increase_raster_position()
        if self.interrupt_clock >= 50: # FIXME remove
            self.interrupt_clock = 0
            self.cause_interrupt()
        self.VIC.repaint()
        if self.VIC_clock >= 1: # 6:
            self.VIC_clock = 0
            self.VIC.increase_raster_position()
        return
        self.iterate()
        self.interrupt_clock += 1
        if self.interrupt_clock >= 50: # FIXME remove
            self.interrupt_clock = 0
            self.cause_interrupt()
        return

    def iterate(self):
        self.CPU.step()
        return True

    def cause_interrupt(self):
        if "I" in self.CPU.flags: # interrupt DISABLE
            #print("not supposed to cause interrupts right now...")
            return True
        #print("at 0x0283: %r" % self.CPU.MMU.read_memory(0x0283, 2))
        #print("at 0x37: %r" % self.CPU.MMU.read_memory(0x37, 2))
        #print("at 0x2B: %r" % self.CPU.MMU.read_memory(0x2B, 2))
        #if not self.CIA1.B_interrupt_pending:
        if not self.CPU.B_in_interrupt:
            #self.CIA1.B_interrupt_pending = True
            self.CPU.cause_interrupt(False)
        return True


"""
$D000-$DFFF
53248-57343    

I/O Area (memory mapped chip registers), Character ROM or RAM area (4096 bytes); depends on the value of bits #0-#2 of the processor port at memory address $0001:

    *

      %x00: RAM area.
    *

      %0xx: Character ROM. (Except for the value %000, see above.)
    *

      %1xx: I/O Area. (Except for the value %100, see above.)
"""

if __name__ == "__main__":
    c64 = C64()
    c64.set_tape_image_name(b'', b'')
    c64.CIA1.handle_key_press('')
    c64.CIA1.handle_key_release('')
    c64.iterate()
