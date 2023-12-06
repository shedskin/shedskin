#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.


from . import memory

# TODO actually the memory is separated into pages of 256 bytes each on a real C64.

# $0000-$00FF, 0-256 zero page (without $0 and $1).
# $0100-$01FF, 256-511 processor stack.
# $0200-$02FF, buffers.
# $0300-$03FF, 768-1023 IRQ vectors.
# $0400-$07FF, 1024-2047 default screen memory.
# $0800-$9FFF, 2048-40959 basic area.
# $A000-$BFFF, 40960-49151 BASIC ROM
# $C000-$CFFF, 49152-53247 upper RAM area.
# $D000-$DFFF, 53248-57343 I/O Area
# $D000-$DFFF, 53248-57343 character ROM
# $D000-$D3FF, 53248-54271 VIC II
# $D400-$D7FF, 54272-55295 SID
# $D800-$DBFF, 55296-56319 Color RAM (only 4 bits per byte)!
# $DC00-$DCFF, 56320-56575 CIA#1 inputs
# $DD00-$DDFF, 56576-56831 CIA#2 serial, NMI
# $DE00-$DEFF, 56832-57087 external device memory maps.
# $DF00-$DFFF, 57088-57343 external device memory maps.
# $E000-$FFFF, 57344-65535 kernal ROM!!!
# $FFFA-$FFFF, 65530-65535 hardware vectors.

class ROM(memory.Memory):
    def __init__(self, value, B_active = True):
        self.B_active = B_active
        self.memory = []
        for i in range(len(value)): # for some reason, in ShedSkin "for c in value: self.memory.append(ord(c))" doesn't work.
            c = value[i]
            self.memory.append(c)

        #self.memory = [ord(c) for c in value]
        self.B_can_write = False # in the instance because of ShedSkin

    def read_memory(self, address, size = 1):
        if size == 1:
            return self.memory[address]
        return one_big_value(self.memory[address : address + size])

    def write_memory(self, address, value, size):
        raise NotImplementedError("cannot write to ROM")

minimal_overlay_address = 0xA000

def one_big_value(part):
    assert len(part) <= 4, "mmu.one_big_value: len(part)<=4"
    f = 0
    v = 0
    for c in part:
        v = v | (c << f)
        f += 8
    return v

class MMU(memory.Memory):
    def __init__(self):
        self.overlays = {}
        self.overlay_values = []
        self.memory = 65536 * [0]

    def set_overlay(self, name, overlay):
        self.overlays[name] = overlay
        self.overlay_values = list(self.overlays.values())

    def read_memory(self, address, size = 1):
        value = self.xread_memory(address, size)
        #if value is None:
        #    print("memory at address $%X broken" % address)
        #    assert(size == 1)
        #    return 0xFF
        #assert(value is not None)
        #print("memory at $%X is %r=$%X" % (address, value, value))
        return value

    def read_zero_page(self, address, size = 1):
        return self.read_memory(address, size)

    def xread_memory(self, address, size = 1):
        if address >= minimal_overlay_address or address < 2:
            for range_1, controller in self.overlay_values:
                if address >= range_1[0] and address < range_1[1] and controller.B_active:
                    return controller.read_memory(address - range_1[0], size)
        if size == 1:
            return (self.memory[address])
        assert size >= 0, "MMU.read_memory: size>=0"
        v = one_big_value(self.memory[address : address + size])
        return v

    def write_memory(self, address, value, size):
        a = address
        if address >= minimal_overlay_address or address < 2:
            for range_1, controller in self.overlay_values:
                if address >= range_1[0] and address < range_1[1] and controller.B_active and controller.B_can_write: # FIXME and hasattr(controller, "write_memory"):
                    # WTF assert(address != 0x1FC and address != 0x1FD)
                    #print(address, range_1, controller)
                    return controller.write_memory(address - range_1[0], value, size)

        assert isinstance(value, int), "MMU.write_memory: value is an integer"
        for i in range(size):
            self.memory[address + i] = value & 0xFF
            value >>= 8

    def map_ROM(self, name, address, value, B_active):
        assert address >= minimal_overlay_address, "MMU.map_ROM address >= minimal_overlay_address" # ??  or range_1[1] == 2
        ROM_1 = ROM(value, B_active)
        self.set_overlay(name, (((address, address + len(value)), ROM_1)))
        return ROM_1

    def map_IO(self, name, range_1, IO):
        assert range_1[0] >= minimal_overlay_address or range_1[1] == 2, "MMU.map_IO"
        self.set_overlay(name, (((range_1[0], range_1[1]), IO)))

    def set_overlay_active(self, name, value):
        #print("setting overlay %r to %r" % (name, value))
        self.overlays[name][1].B_active = value
        #self.overlay_values = self.overlays.values()
        #if value == False:
        #    for s in range(0xD1, 0xD1 + 4):
        #        sys.stdout.write("%02X " % (self.read_memory(s)))


