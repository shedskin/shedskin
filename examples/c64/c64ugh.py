#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import sys
import os

#{
import psyco
psyco.full()
#}

import time

class Memory(object):
    def __init__(self):
        self.B_can_write = True # in the instance because of ShedSkin

    def read_memory(self, address, size = 1):
        return 0xFF

    def write_memory(self, address, value, size):
        pass

class TextView(object):
    def __init__(self, VIC, controls):
        self.VIC = VIC
        self.first_column = 0
        self.first_row = 0
        self.last_column = 0
        self.last_row = 0
        self.character_bitmaps_offset = 0 # FIXME correct that.
        self.video_offset = 0 # FIXME correct that.
        self.mode = "normal-text"
        self.border_color = 0 # FIXME default?
        self.old_VIC_bank = -1
        self.background_color_0 = 0 # FIXME default?

        self.viewport_column = 0 # FIXME
        self.viewport_row = 0  # FIXME
        self.VIC_bank = 0 # FIXME
        self.width = 40
        self.height = 25

    def unprepare(self):
        self.old_VIC_bank = -1
        print("unprepare...")

#    def get_border_color(self):
#        return self._border_color
#
#    def set_border_color(self, value):
#        self._border_color = value
#        # TODO update pixbuf etc.
#
#    border_color = property(get_border_color, set_border_color)

class CPUPort(Memory): # $0..$1
    def __init__(self, MMU):
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
        assert(size == 1)
        if address == 0:
            return self.data_direction
        elif address == 1:
            return self.port
        else:
            assert(False)
            return 0

    def write_memory(self, address, value, size):
        assert(isinstance(value, int))
        if address == 0:
            self.data_direction = value # FIXME protect?
        elif address == 1:
            self.set_port(value)
        else:
            assert(False)

    def set_port(self, value):
        if self.port == value:
            return

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
        if B_E000_RAM:
            sys.stderr.write("warning: KERNAL disabled!!!\n")
            time.sleep(5.0)

class C64:
    def __init__(self):
        self.interrupt_clock = 0
        self.CPU = CPU()
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
            print(ROM)
            assert(size == len(value))
            # TODO how to do this in a nicer way?
            if ROM == "kernal":
                hardware_vectors = value[-6:]
                value = value[:-6]
                for i in range(6):
                    self.CPU.MMU.write_memory(0xFFFA + i, ord(hardware_vectors[i]), 1)
            ROM_obj = self.CPU.MMU.map_ROM(ROM, range_1[0], value, ROM != "chargen")
            if ROM == "chargen":
                char_ROM = ROM_obj

        self.controls = {} #gmonitor.Controls(self)

        cia1 = CIA1()
        self.CIA1 = cia1
        cia2 = CIA2()
        vic = VIC_II(self.CPU.MMU, cia2, char_ROM)
        self.VIC = vic
        vic.text_view = TextView(vic, self.controls)
        self.CPU.MMU.map_IO("cia2", (0xDD00, 0xDE00), cia2)
        self.CPU.MMU.map_IO("vic", (0xD000, 0xD400), vic)
        self.CPU.MMU.map_IO("sid", (0xD400, 0xD800), SID())
        self.CPU.MMU.map_IO("cia1", (0xDC00, 0xDD00), cia1)
        self.CPU.MMU.map_IO("cpu", (0x0000, 0x0002), CPUPort(self.CPU.MMU))
        vic.unprepare() # memory is not initialized yet, so unprepare...
        MMU = self.CPU.MMU
        #MMU.write_memory(0xFFFA, b"\x43\xFE\xE2\xFC\x48\xFF") # FIXME endianness.
        self.CPU.write_register("PC", (MMU.read_memory(0xFFFC, 2)))
        self.count = 0

    def run(self):
        while True: # TODO terminate?
            self.cycle()

    def fire_timer(self):
        for n in range(2000):
            self.CPU.fetch_execute()
            self.interrupt_clock += 1
            if self.interrupt_clock >= 50: # FIXME remove
                self.interrupt_clock = 0
                self.cause_interrupt()
            self.VIC.increase_raster_position()
        self.VIC.repaint()

    def cause_interrupt(self):
        if "I" in self.CPU.flags: # interrupt DISABLE
            #print("not supposed to cause interrupts right now...")
            return True
        #print("at 0x0283: %r" % self.CPU.MMU.read_memory(0x0283, 2))
#        print("at 0x37: %r" % self.CPU.MMU.read_memory(0x37, 2))
#        print("at 0x2B: %r" % self.CPU.MMU.read_memory(0x2B, 2))
        #if not self.CIA1.B_interrupt_pending:
        if not self.CPU.B_in_interrupt:
            self.CIA1.B_interrupt_pending = True
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

# TODO DECIMAL MODE (CLD, SED)
# TODO interrupts

def err(message):
	print >>sys.stderr, "error: %s" % message
	sys.exit(1)
	return 42

def to_signed_byte(value):
	return value if value < 0x80 else -(256 - value)

class Registers(object):
	def __init__(self): # FIXME default values...
		self.PC = 0
		self.SP = 0
		self.X = 0
		self.Y = 0
		self.A = 0

class CPU(object):
	def __init__(self):
		self.B_disasm = False # True
		self.B_debug_stack = False
		assert(len(CPU.opcode_to_mnem) == 0x100)
		self.B_in_interrupt = False
		self.registers = Registers()
		self.MMU = MMU()
		self.flags = set() # of N, V, B, D, I, Z, C.
		#for mnem in set(CPU.opcode_to_mnem):
		#	if not hasattr(self, mnem) and mnem not in CPU.exotic_opcodes:
		#		raise NotImplementedError("warning: instruction %r not implemented")
#		if False: # ShedSkin
#			value = self.load_value_unadvancing("Z")
#			value = self.load_value_advancing("Z")
#			self.update_flags_by_number(value)                 

	def write_register(self, name, value):
		assert(isinstance(value, int))
		if name == "PC":
			self.registers.PC = value
		elif name == "A":
			self.registers.A = value
		elif name == "X":
			self.registers.X = value
		elif name == "Y":
			self.registers.Y = value
		elif name == "SP":
			self.registers.SP = value
		else:
			assert(False)
		#print("registers", self.registers)

	def read_register(self, name):
		r = self.registers
		return r.PC if name == "PC" else \
		       r.A if name == "A" else \
		       r.X if name == "X" else \
		       r.Y if name == "Y" else \
		       r.SP if name == "SP" else \
		       err("unknown register")

	def disasm(self, PC):
		opcode = self.MMU.read_memory(PC)
		mnem = CPU.opcode_to_mnem[opcode]
		addressing_modes = CPU.LDX_addressing_modes if mnem == "LDX" else \
			CPU.LDY_addressing_modes if mnem == "LDY" else \
			CPU.LDA_addressing_modes if mnem == "LDA" else \
			CPU.CMP_addressing_modes if mnem == "CMP" else \
			CPU.CPX_addressing_modes if mnem == "CPX" else \
			CPU.CPY_addressing_modes if mnem == "CPY" else \
			CPU.ADC_addressing_modes if mnem == "ADC" else \
			CPU.SBC_addressing_modes if mnem == "SBC" else \
			CPU.BIT_addressing_modes if mnem == "BIT" else \
			CPU.AND_addressing_modes if mnem == "AND" else \
			CPU.EOR_addressing_modes if mnem == "EOR" else \
			CPU.ORA_addressing_modes if mnem == "ORA" else \
			CPU.INC_addressing_modes if mnem == "INC" else \
			CPU.ASL_addressing_modes if mnem == "ASL" else \
			CPU.LSR_addressing_modes if mnem == "LSR" else \
			CPU.ROL_addressing_modes if mnem == "ROL" else \
			CPU.ROR_addressing_modes if mnem == "ROR" else \
			CPU.STX_addressing_modes if mnem == "STX" else \
			CPU.STY_addressing_modes if mnem == "STY" else \
			CPU.STA_addressing_modes if mnem == "STA" else {42: "XXX"}
		addressing_mode = addressing_modes.get(opcode) or ""
		# EQ addressing_mode = getattr(self.__class__, mnem + "_addressing_modes")[opcode]

		args = ""
		if addressing_mode == "#":
			args = "#%r" % self.MMU.read_memory(PC + 1, 1)
		elif addressing_mode == "ABS+X":
			base = (self.MMU.read_memory(PC + 1, 2))
			args = "$%04X+X" % base
		elif addressing_mode == "ABS":
			base = (self.MMU.read_memory(PC + 1, 2))
			args = "$%04X ABS" % base
		elif addressing_mode == "ABS+Y":
			base = (self.MMU.read_memory(PC + 1, 2))
			args = "$%04X+Y" % base
		elif addressing_mode == "Z":
			base = (self.MMU.read_memory(PC + 1, 1))
			args = "[$%02X]" % base
		elif addressing_mode == "Z+X":
			base = (self.MMU.read_memory(PC + 1, 1))
			args = "[$%02X+X]" % base
		elif addressing_mode == "IND+X":
			base = (self.MMU.read_memory(PC + 1, 1))
			args = "[[$%02X]+X]" % base
		elif addressing_mode == "IND+Y":
			base = (self.MMU.read_memory(PC + 1, 1))
			args = "[[$%02X]+Y]" % base
		elif addressing_mode == "A":
			args = "A"
		elif addressing_mode != "":
			print(addressing_mode)
			assert(False)
		else:
			if mnem in ["BNE", "BEQ", "BVS", "BVC", "BCC", "BCS", "BPL", "BMI"]:
				offset = to_signed_byte(self.MMU.read_memory(PC + 1, 1))
				args = "%r ; $%X" % (offset, PC + offset + 2)
			elif mnem in ["JSR", "JMP"]:
				# FIXME other modes for JMP
				address = (self.MMU.read_memory(PC + 1, 2))
				args = "$%X" % address
				if opcode == 0x6C:
					args = "[%s]" % args

		print("%04X  %s %s" % (PC, mnem,  args))

	def fetch_execute(self):
		PC = self.read_register("PC")
		opcode = self.MMU.read_memory(PC)
		if PC == 0xE43D:  #FIXME
			self.B_disasm = False
		if self.B_disasm:
			self.disasm(PC)
		self.write_register("PC", PC + 1)
		#sys.stdout.write("\t" + mnem)
		#print(hex(opcode))
		if opcode == 0x0:
			return self.BRK(opcode)
		elif opcode == 0x1:
			return self.ORA(opcode)
		elif opcode == 0x2:
			return self.KIL(opcode)
		elif opcode == 0x3:
			return self.SLO(opcode)
		elif opcode == 0x4:
			return self.NOP(opcode)
		elif opcode == 0x5:
			return self.ORA(opcode)
		elif opcode == 0x6:
			return self.ASL(opcode)
		elif opcode == 0x7:
			return self.SLO(opcode)
		elif opcode == 0x8:
			return self.PHP(opcode)
		elif opcode == 0x9:
			return self.ORA(opcode)
		elif opcode == 0xA:
			return self.ASL(opcode)
		elif opcode == 0xB:
			return self.ANC(opcode)
		elif opcode == 0xC:
			return self.NOP(opcode)
		elif opcode == 0xD:
			return self.ORA(opcode)
		elif opcode == 0xE:
			return self.ASL(opcode)
		elif opcode == 0xF:
			return self.SLO(opcode)
		elif opcode == 0x10:
			return self.BPL(opcode)
		elif opcode == 0x11:
			return self.ORA(opcode)
		elif opcode == 0x12:
			return self.KIL(opcode)
		elif opcode == 0x13:
			return self.SLO(opcode)
		elif opcode == 0x14:
			return self.NOP(opcode)
		elif opcode == 0x15:
			return self.ORA(opcode)
		elif opcode == 0x16:
			return self.ASL(opcode)
		elif opcode == 0x17:
			return self.SLO(opcode)
		elif opcode == 0x18:
			return self.CLC(opcode)
		elif opcode == 0x19:
			return self.ORA(opcode)
		elif opcode == 0x1A:
			return self.NOP(opcode)
		elif opcode == 0x1B:
			return self.SLO(opcode)
		elif opcode == 0x1C:
			return self.NOP(opcode)
		elif opcode == 0x1D:
			return self.ORA(opcode)
		elif opcode == 0x1E:
			return self.ASL(opcode)
		elif opcode == 0x1F:
			return self.SLO(opcode)
		elif opcode == 0x20:
			return self.JSR(opcode)
		elif opcode == 0x21:
			return self.ANDX(opcode)
		elif opcode == 0x22:
			return self.KIL(opcode)
		elif opcode == 0x23:
			return self.RLA(opcode)
		elif opcode == 0x24:
			return self.BIT(opcode)
		elif opcode == 0x25:
			return self.ANDX(opcode)
		elif opcode == 0x26:
			return self.ROL(opcode)
		elif opcode == 0x27:
			return self.RLA(opcode)
		elif opcode == 0x28:
			return self.PLP(opcode)
		elif opcode == 0x29:
			return self.ANDX(opcode)
		elif opcode == 0x2A:
			return self.ROL(opcode)
		elif opcode == 0x2B:
			return self.ANC(opcode)
		elif opcode == 0x2C:
			return self.BIT(opcode)
		elif opcode == 0x2D:
			return self.ANDX(opcode)
		elif opcode == 0x2E:
			return self.ROL(opcode)
		elif opcode == 0x2F:
			return self.RLA(opcode)
		elif opcode == 0x30:
			return self.BMI(opcode)
		elif opcode == 0x31:
			return self.ANDX(opcode)
		elif opcode == 0x32:
			return self.KIL(opcode)
		elif opcode == 0x33:
			return self.RLA(opcode)
		elif opcode == 0x34:
			return self.NOP(opcode)
		elif opcode == 0x35:
			return self.ANDX(opcode)
		elif opcode == 0x36:
			return self.ROL(opcode)
		elif opcode == 0x37:
			return self.RLA(opcode)
		elif opcode == 0x38:
			return self.SEC(opcode)
		elif opcode == 0x39:
			return self.ANDX(opcode)
		elif opcode == 0x3A:
			return self.NOP(opcode)
		elif opcode == 0x3B:
			return self.RLA(opcode)
		elif opcode == 0x3C:
			return self.NOP(opcode)
		elif opcode == 0x3D:
			return self.ANDX(opcode)
		elif opcode == 0x3E:
			return self.ROL(opcode)
		elif opcode == 0x3F:
			return self.RLA(opcode)
		elif opcode == 0x40:
			return self.RTI(opcode)
		elif opcode == 0x41:
			return self.EOR(opcode)
		elif opcode == 0x42:
			return self.KIL(opcode)
		elif opcode == 0x43:
			return self.SRE(opcode)
		elif opcode == 0x44:
			return self.NOP(opcode)
		elif opcode == 0x45:
			return self.EOR(opcode)
		elif opcode == 0x46:
			return self.LSR(opcode)
		elif opcode == 0x47:
			return self.SRE(opcode)
		elif opcode == 0x48:
			return self.PHA(opcode)
		elif opcode == 0x49:
			return self.EOR(opcode)
		elif opcode == 0x4A:
			return self.LSR(opcode)
		elif opcode == 0x4B:
			return self.ALR(opcode)
		elif opcode == 0x4C:
			return self.JMP(opcode)
		elif opcode == 0x4D:
			return self.EOR(opcode)
		elif opcode == 0x4E:
			return self.LSR(opcode)
		elif opcode == 0x4F:
			return self.SRE(opcode)
		elif opcode == 0x50:
			return self.BVC(opcode)
		elif opcode == 0x51:
			return self.EOR(opcode)
		elif opcode == 0x52:
			return self.KIL(opcode)
		elif opcode == 0x53:
			return self.SRE(opcode)
		elif opcode == 0x54:
			return self.NOP(opcode)
		elif opcode == 0x55:
			return self.EOR(opcode)
		elif opcode == 0x56:
			return self.LSR(opcode)
		elif opcode == 0x57:
			return self.SRE(opcode)
		elif opcode == 0x58:
			return self.CLI(opcode)
		elif opcode == 0x59:
			return self.EOR(opcode)
		elif opcode == 0x5A:
			return self.NOP(opcode)
		elif opcode == 0x5B:
			return self.SRE(opcode)
		elif opcode == 0x5C:
			return self.NOP(opcode)
		elif opcode == 0x5D:
			return self.EOR(opcode)
		elif opcode == 0x5E:
			return self.LSR(opcode)
		elif opcode == 0x5F:
			return self.SRE(opcode)
		elif opcode == 0x60:
			return self.RTS(opcode)
		elif opcode == 0x61:
			return self.ADC(opcode)
		elif opcode == 0x62:
			return self.KIL(opcode)
		elif opcode == 0x63:
			return self.RRA(opcode)
		elif opcode == 0x64:
			return self.NOP(opcode)
		elif opcode == 0x65:
			return self.ADC(opcode)
		elif opcode == 0x66:
			return self.ROR(opcode)
		elif opcode == 0x67:
			return self.RRA(opcode)
		elif opcode == 0x68:
			return self.PLA(opcode)
		elif opcode == 0x69:
			return self.ADC(opcode)
		elif opcode == 0x6A:
			return self.ROR(opcode)
		elif opcode == 0x6B:
			return self.ARR(opcode)
		elif opcode == 0x6C:
			return self.JMP(opcode)
		elif opcode == 0x6D:
			return self.ADC(opcode)
		elif opcode == 0x6E:
			return self.ROR(opcode)
		elif opcode == 0x6F:
			return self.RRA(opcode)
		elif opcode == 0x70:
			return self.BVS(opcode)
		elif opcode == 0x71:
			return self.ADC(opcode)
		elif opcode == 0x72:
			return self.KIL(opcode)
		elif opcode == 0x73:
			return self.RRA(opcode)
		elif opcode == 0x74:
			return self.NOP(opcode)
		elif opcode == 0x75:
			return self.ADC(opcode)
		elif opcode == 0x76:
			return self.ROR(opcode)
		elif opcode == 0x77:
			return self.RRA(opcode)
		elif opcode == 0x78:
			return self.SEI(opcode)
		elif opcode == 0x79:
			return self.ADC(opcode)
		elif opcode == 0x7A:
			return self.NOP(opcode)
		elif opcode == 0x7B:
			return self.RRA(opcode)
		elif opcode == 0x7C:
			return self.NOP(opcode)
		elif opcode == 0x7D:
			return self.ADC(opcode)
		elif opcode == 0x7E:
			return self.ROR(opcode)
		elif opcode == 0x7F:
			return self.RRA(opcode)
		elif opcode == 0x80:
			return self.NOP(opcode)
		elif opcode == 0x81:
			return self.STA(opcode)
		elif opcode == 0x82:
			return self.NOP(opcode)
		elif opcode == 0x83:
			return self.SAX(opcode)
		elif opcode == 0x84:
			return self.STY(opcode)
		elif opcode == 0x85:
			return self.STA(opcode)
		elif opcode == 0x86:
			return self.STX(opcode)
		elif opcode == 0x87:
			return self.SAX(opcode)
		elif opcode == 0x88:
			return self.DEY(opcode)
		elif opcode == 0x89:
			return self.NOP(opcode)
		elif opcode == 0x8A:
			return self.TXA(opcode)
		elif opcode == 0x8B:
			return self.XAA(opcode)
		elif opcode == 0x8C:
			return self.STY(opcode)
		elif opcode == 0x8D:
			return self.STA(opcode)
		elif opcode == 0x8E:
			return self.STX(opcode)
		elif opcode == 0x8F:
			return self.SAX(opcode)
		elif opcode == 0x90:
			return self.BCC(opcode)
		elif opcode == 0x91:
			return self.STA(opcode)
		elif opcode == 0x92:
			return self.KIL(opcode)
		elif opcode == 0x93:
			return self.AHX(opcode)
		elif opcode == 0x94:
			return self.STY(opcode)
		elif opcode == 0x95:
			return self.STA(opcode)
		elif opcode == 0x96:
			return self.STX(opcode)
		elif opcode == 0x97:
			return self.SAX(opcode)
		elif opcode == 0x98:
			return self.TYA(opcode)
		elif opcode == 0x99:
			return self.STA(opcode)
		elif opcode == 0x9A:
			return self.TXS(opcode)
		elif opcode == 0x9B:
			return self.TAS(opcode)
		elif opcode == 0x9C:
			return self.SHY(opcode)
		elif opcode == 0x9D:
			return self.STA(opcode)
		elif opcode == 0x9E:
			return self.SHX(opcode)
		elif opcode == 0x9F:
			return self.AHX(opcode)
		elif opcode == 0xA0:
			return self.LDY(opcode)
		elif opcode == 0xA1:
			return self.LDA(opcode)
		elif opcode == 0xA2:
			return self.LDX(opcode)
		elif opcode == 0xA3:
			return self.LAX(opcode)
		elif opcode == 0xA4:
			return self.LDY(opcode)
		elif opcode == 0xA5:
			return self.LDA(opcode)
		elif opcode == 0xA6:
			return self.LDX(opcode)
		elif opcode == 0xA7:
			return self.LAX(opcode)
		elif opcode == 0xA8:
			return self.TAY(opcode)
		elif opcode == 0xA9:
			return self.LDA(opcode)
		elif opcode == 0xAA:
			return self.TAX(opcode)
		elif opcode == 0xAB:
			return self.LAX(opcode)
		elif opcode == 0xAC:
			return self.LDY(opcode)
		elif opcode == 0xAD:
			return self.LDA(opcode)
		elif opcode == 0xAE:
			return self.LDX(opcode)
		elif opcode == 0xAF:
			return self.LAX(opcode)
		elif opcode == 0xB0:
			return self.BCS(opcode)
		elif opcode == 0xB1:
			return self.LDA(opcode)
		elif opcode == 0xB2:
			return self.KIL(opcode)
		elif opcode == 0xB3:
			return self.LAX(opcode)
		elif opcode == 0xB4:
			return self.LDY(opcode)
		elif opcode == 0xB5:
			return self.LDA(opcode)
		elif opcode == 0xB6:
			return self.LDX(opcode)
		elif opcode == 0xB7:
			return self.LAX(opcode)
		elif opcode == 0xB8:
			return self.CLV(opcode)
		elif opcode == 0xB9:
			return self.LDA(opcode)
		elif opcode == 0xBA:
			return self.TSX(opcode)
		elif opcode == 0xBB:
			return self.LAS(opcode)
		elif opcode == 0xBC:
			return self.LDY(opcode)
		elif opcode == 0xBD:
			return self.LDA(opcode)
		elif opcode == 0xBE:
			return self.LDX(opcode)
		elif opcode == 0xBF:
			return self.LAX(opcode)
		elif opcode == 0xC0:
			return self.CPY(opcode)
		elif opcode == 0xC1:
			return self.CMP(opcode)
		elif opcode == 0xC2:
			return self.NOP(opcode)
		elif opcode == 0xC3:
			return self.DCP(opcode)
		elif opcode == 0xC4:
			return self.CPY(opcode)
		elif opcode == 0xC5:
			return self.CMP(opcode)
		elif opcode == 0xC6:
			return self.DEC(opcode)
		elif opcode == 0xC7:
			return self.DCP(opcode)
		elif opcode == 0xC8:
			return self.INY(opcode)
		elif opcode == 0xC9:
			return self.CMP(opcode)
		elif opcode == 0xCA:
			return self.DEX(opcode)
		elif opcode == 0xCB:
			return self.AXS(opcode)
		elif opcode == 0xCC:
			return self.CPY(opcode)
		elif opcode == 0xCD:
			return self.CMP(opcode)
		elif opcode == 0xCE:
			return self.DEC(opcode)
		elif opcode == 0xCF:
			return self.DCP(opcode)
		elif opcode == 0xD0:
			return self.BNE(opcode)
		elif opcode == 0xD1:
			return self.CMP(opcode)
		elif opcode == 0xD2:
			return self.KIL(opcode)
		elif opcode == 0xD3:
			return self.DCP(opcode)
		elif opcode == 0xD4:
			return self.NOP(opcode)
		elif opcode == 0xD5:
			return self.CMP(opcode)
		elif opcode == 0xD6:
			return self.DEC(opcode)
		elif opcode == 0xD7:
			return self.DCP(opcode)
		elif opcode == 0xD8:
			return self.CLD(opcode)
		elif opcode == 0xD9:
			return self.CMP(opcode)
		elif opcode == 0xDA:
			return self.NOP(opcode)
		elif opcode == 0xDB:
			return self.DCP(opcode)
		elif opcode == 0xDC:
			return self.NOP(opcode)
		elif opcode == 0xDD:
			return self.CMP(opcode)
		elif opcode == 0xDE:
			return self.DEC(opcode)
		elif opcode == 0xDF:
			return self.DCP(opcode)
		elif opcode == 0xE0:
			return self.CPX(opcode)
		elif opcode == 0xE1:
			return self.SBC(opcode)
		elif opcode == 0xE2:
			return self.NOP(opcode)
		elif opcode == 0xE3:
			return self.ISC(opcode)
		elif opcode == 0xE4:
			return self.CPX(opcode)
		elif opcode == 0xE5:
			return self.SBC(opcode)
		elif opcode == 0xE6:
			return self.INC(opcode)
		elif opcode == 0xE7:
			return self.ISC(opcode)
		elif opcode == 0xE8:
			return self.INX(opcode)
		elif opcode == 0xE9:
			return self.SBC(opcode)
		elif opcode == 0xEA:
			return self.NOP(opcode)
		elif opcode == 0xEB:
			return self.SBC(opcode)
		elif opcode == 0xEC:
			return self.CPX(opcode)
		elif opcode == 0xED:
			return self.SBC(opcode)
		elif opcode == 0xEE:
			return self.INC(opcode)
		elif opcode == 0xEF:
			return self.ISC(opcode)
		elif opcode == 0xF0:
			return self.BEQ(opcode)
		elif opcode == 0xF1:
			return self.SBC(opcode)
		elif opcode == 0xF2:
			return self.KIL(opcode)
		elif opcode == 0xF3:
			return self.ISC(opcode)
		elif opcode == 0xF4:
			return self.NOP(opcode)
		elif opcode == 0xF5:
			return self.SBC(opcode)
		elif opcode == 0xF6:
			return self.INC(opcode)
		elif opcode == 0xF7:
			return self.ISC(opcode)
		elif opcode == 0xF8:
			return self.SED(opcode)
		elif opcode == 0xF9:
			return self.SBC(opcode)
		elif opcode == 0xFA:
			return self.NOP(opcode)
		elif opcode == 0xFB:
			return self.ISC(opcode)
		elif opcode == 0xFC:
			return self.NOP(opcode)
		elif opcode == 0xFD:
			return self.SBC(opcode)
		elif opcode == 0xFE:
			return self.INC(opcode)
		elif opcode == 0xFF:
			return self.ISC(opcode)
		#fn = self.opcode_to_fn[opcode]
		#fn(self, opcode)
		#print("done")

	# TODO DCP {adr} = DEC {adr} + CMP {adr}

	def update_flags_by_number(self, value):
		""" assumes 8 bit number, be careful. """
		assert(isinstance(value, int))
		if value == 0:
			self.flags.add("Z")
		else:
			self.flags.discard("Z")
		if value < 0 or ((value & 128) != 0):
			self.flags.add("N")
		else:
			self.flags.discard("N")

	def consume_operand(self, size):
		PC = self.read_register("PC")
		value = self.MMU.read_memory(PC, size)
		self.write_register("PC", PC + size)
		return value

	def consume_unsigned_operand(self, size):
		""" returns the operand as an integer, not as a buffer """
		value = self.consume_operand(size)
		return value

	def consume_signed_operand(self, size):
		""" returns the operand as an integer, not as a buffer """
		value = to_signed_byte(self.consume_operand(size))
		#value = (endian.unpack_signed_16_bit if size == 2 else endian.unpack_signed if size == 1 else err("invalid operand size"))(value)
		#print(value)
		return value

	def store_value(self, addressing_mode, value, size = 1):
		#print("MODE", addressing_mode)
		if addressing_mode == "Z":
			self.MMU.write_memory(self.consume_unsigned_operand(1), value, size)
		elif addressing_mode == "Z+Y":
			# FIXME unsigned?
			self.MMU.write_memory(self.consume_unsigned_operand(1) + (self.read_register("Y")), value, size)
		elif addressing_mode == "Z+X":
			# FIXME unsigned?
			self.MMU.write_memory(self.consume_unsigned_operand(1) + (self.read_register("X")), value, size)
		elif addressing_mode == "ABS":
			self.MMU.write_memory(self.consume_unsigned_operand(2), value, size)
		elif addressing_mode == "ABS+Y":
			# FIXME unsigned.
			self.MMU.write_memory(self.consume_unsigned_operand(2) + (self.read_register("Y")), value, size)
		elif addressing_mode == "ABS+X":
			# FIXME unsigned.
			self.MMU.write_memory(self.consume_unsigned_operand(2) + (self.read_register("X")), value, size)
		elif addressing_mode == "IND+Y": # [[$a]+X]
			base = self.consume_unsigned_operand(1)
			#print("base would be $%X" % base)
			address = (self.MMU.read_memory(base, 2))
			offset = (self.read_register("Y"))
			#print("address would be $%X+$%X" % (address, offset))
			assert(address != 0)
			# FIXME unsigned
			#print("offset %r" % offset)
			address += offset
			self.MMU.write_memory(address, value, size)
		elif addressing_mode == "A":
			self.write_register("A", value)
		else:
			print("error", addressing_mode)
			assert(False)

	def load_value_unadvancing(self, addressing_mode): # mostly INC and shift instructions...
		old_PC = self.read_register("PC")
		result = self.load_value_advancing(addressing_mode)
		self.write_register("PC", old_PC)
		return result

	def load_value_advancing(self, addressing_mode):
		# mask_addressing_modes = ["#", "Z", "Z+X", "Z+Y", "ABS", "ABS+X", "ABS+Y", "IND+X", "IND+Y"]
		#sys.stdout.write({
		#	0: "#",
		#	0x1C: "ABS+Y",
		#}.get(addressing_mode) or str(addressing_mode))
		# FIXME is unsigned correct?
		#print(addressing_mode)
		return	self.read_register("A") if addressing_mode == "A" else \
		        self.consume_unsigned_operand(1) if addressing_mode == "#" else \
			self.MMU.read_zero_page(self.consume_unsigned_operand(1)) if addressing_mode == "Z" else \
			self.MMU.read_zero_page(self.consume_unsigned_operand(1) + self.read_register("X")) if addressing_mode == "Z+X" else \
			self.MMU.read_zero_page(self.consume_unsigned_operand(1) + self.read_register("Y")) if addressing_mode == "Z+Y" else \
			self.MMU.read_memory(self.consume_unsigned_operand(2)) if addressing_mode == "ABS" else \
			self.MMU.read_memory(self.consume_unsigned_operand(2) + self.read_register("X")) if addressing_mode == "ABS+X" else \
			self.MMU.read_memory(self.consume_unsigned_operand(2) + self.read_register("Y")) if addressing_mode == "ABS+Y" else \
			self.MMU.read_memory((self.MMU.read_memory(self.consume_unsigned_operand(1), 2)) + self.read_register("X")) if addressing_mode == "IND+X" else \
			self.MMU.read_memory((self.MMU.read_memory(self.consume_unsigned_operand(1), 2)) + self.read_register("Y")) if addressing_mode == "IND+Y" else \
			err("invalid addressing mode %r" % addressing_mode)

	LDX_addressing_modes = {
			0xA2: "#",
			0xA6: "Z",
			0xB6: "Z+Y",
			0xAE: "ABS",
			0xBE: "ABS+Y",
		}
	def LDX(self, opcode = 0xA2):
		# FIXME don't mix up addressing modes.
		addressing_mode = CPU.LDX_addressing_modes[opcode]
		value = self.load_value_advancing(addressing_mode)
		self.update_flags_by_number(value)
		self.write_register("X", value)

	LDY_addressing_modes = {
			0xA0: "#",
			0xA4: "Z",
			0xB4: "Z+X",
			0xAC: "ABS",
			0xBC: "ABS+X",
	}
	def LDY(self, opcode):
		# FIXME don't mix up addressing modes.
		addressing_mode = CPU.LDY_addressing_modes[opcode]
		value = self.load_value_advancing(addressing_mode)
		self.update_flags_by_number(value)
		self.write_register("Y", value)

	LDA_addressing_modes = {
			0xA9: "#",
			0xA5: "Z",
			0xB5: "Z+X",
			0xAD: "ABS",
			0xBD: "ABS+X",
			0xB9: "ABS+Y",
			0xA1: "IND+X",
			0xB1: "IND+Y",
	}
	def LDA(self, opcode):
		addressing_mode = CPU.LDA_addressing_modes[opcode]
		value = self.load_value_advancing(addressing_mode)
		#if value is None:
		#	print("ADR", CPU.LDA_addressing_modes[opcode])
		#print("LDA result is %r" % value)
		self.update_flags_by_number(value)
		self.write_register("A", value)

	def compare(self, addressing_mode, reference_value):
		value = self.load_value_advancing(addressing_mode)
		result = value - reference_value # FIXME direction.
		self.update_flags_by_number(result)
		#print("CMP RES", result)
		if reference_value >= value:
			self.flags.add("C")
		else:
			self.flags.discard("C")

	CMP_addressing_modes = {
			0xC9: "#",
			0xC5: "Z",
			0xD5: "Z+X",
			0xCD: "ABS",
			0xDD: "ABS+X",
			0xD9: "ABS+Y",
			0xC1: "IND+X",
			0xD1: "IND+Y",
		}
	def CMP(self, opcode):
		""" compare with A """
		# FIXME negative numbers?
		assert(opcode in [0xC1, 0xC5, 0xC9, 0xCD, 0xD1, 0xD5, 0xD9, 0xDD])
		reference_value = self.read_register("A")
		addressing_mode = CPU.CMP_addressing_modes[opcode]
		return self.compare(addressing_mode, reference_value)

	CPX_addressing_modes = {
			0xE0: "#",
			0xE4: "Z",
			0xEC: "ABS",
	}
	def CPX(self, opcode):
		""" compare with X """
		reference_value = self.read_register("X")
		addressing_mode = CPU.CPX_addressing_modes[opcode]
		return self.compare(addressing_mode, reference_value)

	CPY_addressing_modes = {
			0xC0: "#",
			0xC4: "Z",
			0xCC: "ABS",
	}
	def CPY(self, opcode):
		""" compare with Y """
		# FIXME negative numbers?
		reference_value = self.read_register("Y")
		addressing_mode = CPU.CPY_addressing_modes[opcode]
		return self.compare(addressing_mode, reference_value)

	ADC_addressing_modes = {
		0x69: "#",
		0x65: "Z",
		0x75: "Z+X",
		0x6D: "ABS",
		0x7D: "ABS+X",
		0x79: "ABS+Y",
		0x61: "IND+X",
		0x71: "IND+Y",
	}
	def ADC(self, opcode):
		""" add with carry """
		# FIXME BCD arithmetic.
		assert("D" not in self.flags)
		addressing_mode = CPU.ADC_addressing_modes[opcode]
		operand_1 = self.load_value_advancing(addressing_mode)
		carry = 1 if "C" in self.flags else 0
		operand_0 = self.read_register("A")
		value = (operand_1 + operand_0 + carry)
		if (value & 0xFF) != value:
			self.flags.add("C")
		else:
			self.flags.discard("C") # FIXME test
		value = value & 0xFF
		B_overflow = ((operand_0 ^ operand_1) & (operand_0 ^ (value & 0xFF)) & 0x80) != 0
		#B_overflow = ((operand_1 & 0x80) == 0 and (operand_0 & 0x80) == 0 and (value & 0x80) != 0) or \
		#             ((operand_1 & 0x80) != 0 and (operand_0 & 0x80) != 0 and (value & 0x80) == 0)
		if B_overflow:
			self.flags.add("V")
		else:
			self.flags.discard("V")
		#self.store_value(addressing_mode, value)
		self.write_register("A", value)
		self.update_flags_by_number(value)

	SBC_addressing_modes = {
		0xE9: "#",
		0xE5: "Z",
		0xF5: "Z+X",
		0xED: "ABS",
		0xFD: "ABS+X",
		0xF9: "ABS+Y",
		0xE1: "IND+X",
		0xF1: "IND+Y",
	}
	def SBC(self, opcode):
		""" subtract with carry """
		# FIXME BCD arithmetic.
		assert("D" not in self.flags)
		addressing_mode = CPU.SBC_addressing_modes[opcode]
		operand_1 = self.load_value_advancing(addressing_mode)
		carry = 0 if "C" in self.flags else 1
		operand_0 = self.read_register("A")
		result = operand_0 - operand_1 - carry
		B_overflow = ((operand_0 ^ operand_1) & (operand_0 ^ (result & 0xFF)) & 0x80) != 0
		if B_overflow:
			self.flags.add("V")
		else:
			self.flags.discard("V")
		if result < 0:
			self.flags.add("C")
		else:
			self.flags.discard("C") # FIXME test.
		result = result & 0xFF
		#self.store_value(addressing_mode, value)
		self.write_register("A", result)
		self.update_flags_by_number(result)

	def test_bits(self, addressing_mode):
		reference_value = self.read_register("A")
		value = self.load_value_advancing(addressing_mode)
		result = value & reference_value
		self.update_flags_by_number(result)
		return result, value

	BIT_addressing_modes = {
		0x24: "Z",
		0x2C: "ABS",
	}
	def BIT(self, opcode = 0x24):
		""" like AND, but does not store the result (but just the flags). """
		reference_value = self.read_register("A")
		result, operand = self.test_bits(CPU.BIT_addressing_modes[opcode])
		if (operand & 64) != 0:
			self.flags.add("V")
		else:
			self.flags.discard("V")
		if (operand & 128) != 0:
			self.flags.add("N")
		else:
			self.flags.discard("N")
		#return result

	AND_addressing_modes = {
			0x29: "#",
			0x25: "Z",
			0x35: "Z+X",
			0x2D: "ABS",
			0x3D: "ABS+X",
			0x39: "ABS+Y",
			0x21: "IND+X",
			0x31: "IND+Y",
		}
	def ANDX(self, opcode):
		""" AND with A """
		value, operand = self.test_bits(CPU.AND_addressing_modes[opcode])
		self.write_register("A", value)

	EOR_addressing_modes = {
			0x49: "#",
			0x45: "Z",
			0x55: "Z+X",
			0x4D: "ABS",
			0x5D: "ABS+X",
			0x59: "ABS+Y",
			0x41: "IND+X",
			0x51: "IND+Y",
	}

	def EOR(self, opcode):
		""" exclusive OR """
		reference_value = self.read_register("A")
		addressing_mode = CPU.EOR_addressing_modes[opcode]
		value = self.load_value_advancing(addressing_mode)
		result = value ^ reference_value
		self.update_flags_by_number(result)
		self.write_register("A", result)

	ORA_addressing_modes = {
			0x09: "#",
			0x05: "Z",
			0x15: "Z+X",
			0x0D: "ABS",
			0x1D: "ABS+X",
			0x19: "ABS+Y",
			0x01: "IND+X",
			0x11: "IND+Y",
	}
	def ORA(self, opcode = 0x1):
		""" ORA with A """
		reference_value = self.read_register("A")
		addressing_mode = CPU.ORA_addressing_modes[opcode]
		value = self.load_value_advancing(addressing_mode)
		result = value | reference_value
		self.update_flags_by_number(result)
		self.write_register("A", result)

	def TXS(self, opcode = 0x9A):
		""" transfer X to stack pointer """
		self.write_register("SP", self.read_register("X"))

	def TAY(self, opcode = 0xA8):
		""" transfer A to Y """
		self.write_register("Y", self.read_register("A"))

	def TYA(self, opcode = 0x98):
		""" transfer Y to A """
		self.write_register("A", self.read_register("Y"))

	def TAX(self, opcode = 0xAA):
		""" transfer A to X """
		self.write_register("X", self.read_register("A"))

	def TSX(self, opcode = 0xBA):
		""" transfer SP to X """
		self.write_register("X", self.read_register("SP"))

	def TXA(self, opcode = 0x8A):
		""" transfer X to A """
		self.write_register("A", self.read_register("X"))

	def CLD(self, opcode):
		""" Clear Decimal """
		self.flags.discard("D")

	def SED(self, opcode):
		""" Set Decimal """
		self.flags.add("D")

	def NOP(self, opcode):
		""" No operation """
		pass

	def DEX(self, opcode):
		result = (self.read_register("X") - 1) & 0xFF
		self.write_register("X", result)
		self.update_flags_by_number(result)

	def INX(self, opcode = 0xE8):
		result = ((self.read_register("X")) + 1) & 0xFF
		self.write_register("X", result)
		self.update_flags_by_number(result)

	def DEY(self, opcode = 0x88):
		result = (self.read_register("Y") - 1) & 0xFF
		self.write_register("Y", result)
		self.update_flags_by_number(result)

	def INY(self, opcode = 0xC8):
		result = ((self.read_register("Y")) + 1) & 0xFF
		self.write_register("Y", result)
		self.update_flags_by_number(result)

	def DEC(self, opcode = 0xC6):
		result = (self.read_register("A") - 1) & 0xFF
		self.write_register("A", result)
		self.update_flags_by_number(result)

	INC_addressing_modes = {
			0xE6: "Z",
			0xF6: "Z+X",
			0xEE: "ABS",
			0xFE: "ABS+X",
	}
	def INC(self, opcode):
		addressing_mode = CPU.INC_addressing_modes[opcode]
		value = self.load_value_unadvancing(addressing_mode)
		result = (value + 1) & 0xFF
		self.store_value(addressing_mode, result)
		self.update_flags_by_number(result)

	ASL_addressing_modes = {
			0x0A: "A",
			0x06: "Z",
			0x16: "Z+X",
			0x0E: "ABS",
			0x1E: "ABS+X",
	}
	def ASL(self, opcode):
		addressing_mode = CPU.ASL_addressing_modes[opcode]
		value = self.load_value_unadvancing(addressing_mode)
		if (value & 128) != 0:
			self.flags.add("C")
		else:
			self.flags.discard("C")
		result = (value << 1) & 0xFF
		self.store_value(addressing_mode, result)
		self.update_flags_by_number(result)

	LSR_addressing_modes = {
			0x4A: "A",
			0x46: "Z",
			0x56: "Z+X",
			0x4E: "ABS",
			0x5E: "ABS+X",
	}
	def LSR(self, opcode):
		addressing_mode = CPU.LSR_addressing_modes[opcode]
		value = self.load_value_unadvancing(addressing_mode)
		if (value & 1) != 0:
			self.flags.add("C")
		else:
			self.flags.discard("C")
		result = (value >> 1) & 0xFF
		self.store_value(addressing_mode, result)
		self.update_flags_by_number(result)

	ROL_addressing_modes = {
			0x2A: "A",
			0x26: "Z",
			0x36: "Z+X",
			0x2E: "ABS",
			0x3E: "ABS+X",
	}
	def ROL(self, opcode):
		addressing_mode = CPU.ROL_addressing_modes[opcode]
		value = self.load_value_unadvancing(addressing_mode)
		value = ((value << 1) | (1 if "C" in self.flags else 0))
		result = value & 0xFF
		if (value & 0x100) != 0:
			self.flags.add("C")
		else:
			self.flags.discard("C")
		self.store_value(addressing_mode, result)
		self.update_flags_by_number(result)
		
	ROR_addressing_modes = {
			0x6A: "A",
			0x66: "Z",
			0x76: "Z+X",
			0x6E: "ABS",
			0x7E: "ABS+X",
	}
	def ROR(self, opcode = 0x66):
		addressing_mode = CPU.ROR_addressing_modes[opcode]
		value = self.load_value_unadvancing(addressing_mode)
		result = ((value >> 1) | (128 if "C" in self.flags else 0))  & 0xFF
		if (value & 1) != 0:
			self.flags.add("C")
		else:
			self.flags.discard("C")
		#(self.flags.add if value & 1 else self.flags.discard)("C") # yes, the old value!
		self.store_value(addressing_mode, result)
		self.update_flags_by_number(result)
	
	status_positions = ["C", "Z", "I", "D", "B", "5", "V", "N"]

	def pop_status(self):
		flags_bin = self.stack_pop(1)
		self.flags = set([(flag_name if (flags_bin & (1 << flag_bit)) != 0 else "") for flag_bit, flag_name in enumerate(CPU.status_positions)])
		self.flags.discard("")

	def push_status(self):
		flags_bin = sum([((1 << flag_bit) if flag_name in self.flags else 0) for flag_bit, flag_name in enumerate(CPU.status_positions)])
		self.stack_push(flags_bin, 1)

	def stack_push(self, value, size):
		assert(isinstance(value, int))
		SP = self.read_register("SP")
		base = 0x100
		SP -= size
		self.write_register("SP", SP)
		address = base + SP + 1
		self.MMU.write_memory(address, value, size)
		if self.B_debug_stack:
			print("stack push %r at $%X" % (value, address))

	def stack_peek(self, size):
		SP = self.read_register("SP")
		base = 0x100
		value_bin = self.MMU.read_memory(base + SP + 1, size)
		return value_bin

	def stack_pop(self, size):
		""" returns a string """
		value_bin = self.stack_peek(size)
		SP = self.read_register("SP")
		self.write_register("SP", SP + size)
		base = 0x100
		if self.B_debug_stack:
			print("stack pop %r at $%X" % (value_bin, base + SP + 1))
		#print("stack peek %r" % self.stack_peek(2))
		return value_bin

	def BNE(self, opcode):
		assert(opcode == 0xD0)
		offset = self.consume_signed_operand(1)
		if "Z" not in self.flags:
			#print("OFFSET", offset)
			self.write_register("PC", (self.read_register("PC")) + offset)

	def BEQ(self, opcode):
		offset = self.consume_signed_operand(1)
		if "Z" in self.flags:
			#print("OFFSET", offset)
			self.write_register("PC", (self.read_register("PC")) + offset)

	def BPL(self, opcode = 0x10):
		offset = self.consume_signed_operand(1)
		if "N" not in self.flags:
			#print("OFFSET", offset)
			self.write_register("PC", (self.read_register("PC")) + offset)

	def BMI(self, opcode = 0x30):
		offset = self.consume_signed_operand(1)
		if "N" in self.flags:
			#print("OFFSET", offset)
			self.write_register("PC",(self.read_register("PC")) + offset)

	def BCS(self, opcode = 0xB0):
		offset = self.consume_signed_operand(1)
		if "C" in self.flags:
			#print("OFFSET", offset)
			self.write_register("PC",(self.read_register("PC")) + offset)

	def BCC(self, opcode):
		offset = self.consume_signed_operand(1)
		if "C" not in self.flags:
			#print("OFFSET", offset)
			self.write_register("PC",(self.read_register("PC")) + offset)

	def BVS(self, opcode):
		offset = self.consume_signed_operand(1)
		if "V" in self.flags:
			#print("OFFSET", offset)
			self.write_register("PC",(self.read_register("PC")) + offset)

	def BVC(self, opcode):
		offset = self.consume_signed_operand(1)
		if "V" not in self.flags:
			#print("OFFSET", offset)
			self.write_register("PC",(self.read_register("PC")) + offset)

	def JMP(self, opcode = 0x4C):
		address = self.consume_unsigned_operand(2)
		if opcode == 0x6C: # indirect jump
			address = self.MMU.read_memory(address, 2)
		self.write_register("PC", address)

	def JSR(self, opcode = 0x20):
		assert(opcode == 0x20)
		#self.push_status()
		new_PC = self.consume_unsigned_operand(2)
		self.stack_push(self.read_register("PC") - 1, 2)
		self.write_register("PC", new_PC)

	STX_addressing_modes = {
		0x86: "Z",
		0x96: "Z+Y",
		0x8E: "ABS",
	}
	def STX(self, opcode):
		""" store X into memory """
		self.store_value(CPU.STX_addressing_modes[opcode], self.read_register("X"))

	STY_addressing_modes = {
		0x84: "Z",
		0x94: "Z+X",
		0x8C: "ABS",
	}
	def STY(self, opcode):
		""" store Y into memory """
		self.store_value(CPU.STY_addressing_modes[opcode], self.read_register("Y"))

	STA_addressing_modes = {
		0x85: "Z",
		0x95: "Z+X",
		0x8D: "ABS",
		0x9D: "ABS+X",
		0x99: "ABS+Y",
		0x81: "IND+X",
		0x91: "IND+Y",
	}
	def STA(self, opcode = 0x81):
		""" store A into memory """
		self.store_value(CPU.STA_addressing_modes[opcode], self.read_register("A"))

	def RTS(self, opcode = 0x60):
		""" return from subroutine """
		PC = (self.stack_pop(2))
		self.write_register("PC", PC + 1)
		#self.pop_status()

	def RTI(self, opcode = 0x40):
		""" return from interrupt """
		self.pop_status()
		PC = (self.stack_pop(2))
		self.write_register("PC", PC)
		self.B_in_interrupt = False

	def SEI(self, opcode = 0x78):
		""" Set Interrupt Disable """
		self.flags.add("I")

	def CLI(self, opcode = 0x58):
		""" Clear Interrupt Disable """
		self.flags.discard("I")

	def CLC(self, opcode = 0x18):
		""" Clear Carry """
		self.flags.discard("C")

	def SEC(self, opcode = 0x38):
		""" Set Carry """
		self.flags.add("C")

	def CLV(self, opcode = 0xB8):
		""" Clear Overflow """
		self.flags.discard("V")

	def BRK(self, opcode):
		""" software debugging (NMI) """
		assert(False)
		self.consume_operand(1) # dummy so you can replace any 1-arg instruction's opcode by BRK.
		self.cause_interrupt(True)

	def cause_interrupt(self, B_BRK):  # IRQ and BRK.
		if self.B_in_interrupt:
			return
		address = 0xFFFE
		self.stack_push((self.read_register("PC")), 2)
		new_PC = (self.MMU.read_memory(address, 2))
		self.push_status()
		self.SEI(0x78)
		#print("NEW PC $%X" % new_PC)
		self.write_register("PC", new_PC)
		if B_BRK:
			self.flags.add("B")

	def PHP(self, opcode):
		""" push processor status """
		self.push_status()

	def PLP(self, opcode):
		""" pull processor status """
		self.pop_status()

	def PHA(self, opcode):
		""" push A """
		self.stack_push(self.read_register("A"), 1)

	def PLA(self, opcode):
		""" pull A """
		value = self.stack_pop(1)
		self.update_flags_by_number(value)
		self.write_register("A", value)

	opcode_to_mnem = [
		"BRK", 
		"ORA",
		"KIL", 
		"SLO",
		"NOP",
		"ORA",
		"ASL",
		"SLO",
		"PHP",
		"ORA",
		"ASL",
		"ANC",
		"NOP",
		"ORA",
		"ASL",
		"SLO",
		"BPL",
		"ORA",
		"KIL",
		"SLO",
		"NOP",
		"ORA",
		"ASL",
		"SLO",
		"CLC",
		"ORA",
		"NOP",
		"SLO",
		"NOP",
		"ORA",
		"ASL",
		"SLO",
		"JSR",
		"AND",
		"KIL",
		"RLA",
		"BIT",
		"AND",
		"ROL",
		"RLA",
		"PLP",
		"AND",
		"ROL",
		"ANC",
		"BIT",
		"AND",
		"ROL",
		"RLA",
		"BMI",
		"AND",
		"KIL",
		"RLA",
		"NOP",
		"AND",
		"ROL",
		"RLA",
		"SEC",
		"AND",
		"NOP",
		"RLA",
		"NOP",
		"AND",
		"ROL",
		"RLA",
		"RTI",
		"EOR",
		"KIL",
		"SRE",
		"NOP",
		"EOR",
		"LSR",
		"SRE",
		"PHA",
		"EOR",
		"LSR",
		"ALR",
		"JMP",
		"EOR",
		"LSR",
		"SRE",
		"BVC",
		"EOR",
		"KIL",
		"SRE",
		"NOP",
		"EOR",
		"LSR",
		"SRE",
		"CLI",
		"EOR",
		"NOP",
		"SRE",
		"NOP",
		"EOR",
		"LSR",
		"SRE",
		"RTS",
		"ADC",
		"KIL",
		"RRA", # ROR then ADC
		"NOP",
		"ADC",
		"ROR",
		"RRA",
		"PLA",
		"ADC",
		"ROR",
		"ARR",
		"JMP",
		"ADC",
		"ROR",
		"RRA",
		"BVS",
		"ADC",
		"KIL",
		"RRA",
		"NOP",
		"ADC",
		"ROR",
		"RRA",
		"SEI",
		"ADC",
		"NOP",
		"RRA",
		"NOP",
		"ADC",
		"ROR",
		"RRA",
		"NOP",
		"STA",
		"NOP",
		"SAX",
		"STY",
		"STA",
		"STX",
		"SAX",
		"DEY",
		"NOP",
		"TXA",
		"XAA",
		"STY",
		"STA",
		"STX",
		"SAX",
		"BCC",
		"STA",
		"KIL",
		"AHX",
		"STY",
		"STA",
		"STX",
		"SAX",
		"TYA",
		"STA",
		"TXS",
		"TAS", # unstable.
		"SHY",
		"STA",
		"SHX",
		"AHX",
		"LDY",
		"LDA",	
		"LDX",
		"LAX",
		"LDY",
		"LDA",
		"LDX",
		"LAX",
		"TAY",
		"LDA",
		"TAX",
		"LAX",
		"LDY",
		"LDA",
		"LDX",
		"LAX",
		"BCS",
		"LDA",
		"KIL",
		"LAX",
		"LDY",
		"LDA",
		"LDX",
		"LAX",
		"CLV",
		"LDA",
		"TSX",
		"LAS",
		"LDY",
		"LDA",
		"LDX",
		"LAX",
		"CPY",
		"CMP",
		"NOP",
		"DCP",
		"CPY",
		"CMP",
		"DEC",
		"DCP",
		"INY",
		"CMP",
		"DEX",
		"AXS",
		"CPY",
		"CMP",
		"DEC",
		"DCP",
		"BNE",
		"CMP",
		"KIL",
		"DCP",
		"NOP",
		"CMP",
		"DEC",
		"DCP",
		"CLD",
		"CMP",
		"NOP",
		"DCP",
		"NOP",
		"CMP",
		"DEC",
		"DCP",
		"CPX",
		"SBC",
		"NOP",
		"ISC",
		"CPX",
		"SBC",
		"INC",
		"ISC",
		"INX",
		"SBC",
		"NOP",
		"SBC",
		"CPX",
		"SBC",
		"INC",
		"ISC",
		"BEQ",
		"SBC",
		"KIL",
		"ISC",
		"NOP",
		"SBC",
		"INC",
		"ISC", # INC then SBC
		"SED",
		"SBC",
		"NOP",
		"ISC",
		"NOP",
		"SBC",
		"INC",
		"ISC",
	]

	def AHX(self, opcode):
		raise NotImplementedError("AHX not implemented")
		sys.exit(1)

	def ALR(self, opcode):
		raise NotImplementedError("ALR not implemented")
		sys.exit(1)

	def ANC(self, opcode):
		raise NotImplementedError("ANC not implemented")
		sys.exit(1)

	def ARR(self, opcode):
		raise NotImplementedError("ARR not implemented")
		sys.exit(1)

	def AXS(self, opcode = 0xCB):
		raise NotImplementedError("AXS not implemented")
		sys.exit(1)

	def DCP(self, opcode = 0xC3):
		raise NotImplementedError("AXS not implemented")
		sys.exit(1)

	def ISC(self, opcode):
		raise NotImplementedError("ISC not implemented")
		sys.exit(1)

	def KIL(self, opcode):
		raise NotImplementedError("KIL not implemented")
		sys.exit(1)

	def LAS(self, opcode):
		raise NotImplementedError("LAS not implemented")
		sys.exit(1)

	def LAX(self, opcode):
		raise NotImplementedError("LAX not implemented")
		sys.exit(1)

	def RLA(self, opcode):
		raise NotImplementedError("RLA not implemented")
		sys.exit(1)

	def RRA(self, opcode):
		raise NotImplementedError("RRA not implemented")
		sys.exit(1)

	def SAX(self, opcode):
		raise NotImplementedError("SAX not implemented")
		sys.exit(1)

	def SHX(self, opcode):
		raise NotImplementedError("SHX not implemented")
		sys.exit(1)

	def SHY(self, opcode):
		raise NotImplementedError("SHY not implemented")
		sys.exit(1)

	def SLO(self, opcode):
		raise NotImplementedError("SLO not implemented")
		sys.exit(1)

	def SRE(self, opcode):
		raise NotImplementedError("SRE not implemented")
		sys.exit(1)

	def TAS(self, opcode = 0x9B):
		raise NotImplementedError("TAS not implemented")
		sys.exit(1)

	def XAA(self, opcode):
		raise NotImplementedError("XAA not implemented")
		sys.exit(1)


	exotic_opcodes = set(["RRA", "TAS", "SRE", "SLO", "KIL", "SHX", "SHY", "SAX", "LAS", "XAS", "ALR", "RLA", "DCP", "AHX", "ARR", "LAX", "ANC", "ISC", "XAA", "AXS", ])

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

class ROM(Memory):
    def __init__(self, value, B_active = True):
        self.B_active = B_active
        self.memory = []
        for i in range(len(value)):
            c = value[i]
            print(c)
            v = ord(c)
            self.memory.append(v)

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
    assert(len(part) <= 4)
    f = 0
    v = 0
    for c in part:
        v = v | (c << f)
        f += 8
    return v

class MMU:
    def __init__(self):
        self.overlays = {}
        self.memory = 65536 * [0]

    def read_memory(self, address, size = 1):
        value = self.xread_memory(address, size)
        #if value is None:
        #   print("memory at address $%X broken" % address)
        #   assert(size == 1)
        #   return 0xFF
        #assert(value is not None)
        #print("memory at $%X is %r=$%X" % (address, value, value))
        return value

    def read_zero_page(self, address, size = 1):
        return self.read_memory(address, size)

    def xread_memory(self, address, size = 1):
        if address >= minimal_overlay_address or address < 2:
            for range_1, controller in self.overlays.values():
                if address >= range_1[0] and address < range_1[1] and controller.B_active:
                    return controller.read_memory(address - range_1[0], size)
        if size == 1:
            return (self.memory[address])
        assert(size >= 0)
        v = one_big_value(self.memory[address : address + size])
        return v

    def write_memory(self, address, value, size):
        a = address
        if address >= minimal_overlay_address or address < 2:
            for range_1, controller in self.overlays.values():
                if address >= range_1[0] and address < range_1[1] and controller.B_active and controller.B_can_write: # FIXME and hasattr(controller, "write_memory"):
                    assert(address != 0x1FC and address != 0x1FD)
                    #print(address, range_1, controller)
                    return controller.write_memory(address - range_1[0], value, size)

        assert(isinstance(value, int))
        for i in range(size):
            self.memory[address + i] = value & 0xFF
            value >>= 8

    def map_ROM(self, name, address, value, B_active):
        assert(address >= minimal_overlay_address) # ??  or range_1[1] == 2)
        ROM_1 = ROM(value, B_active)
        self.overlays[name] = (((address, address + len(value)), ROM_1))
        return ROM_1

    def map_IO(self, name, range_1, IO):
        assert(range_1[0] >= minimal_overlay_address or range_1[1] == 2)
        self.overlays[name] = (((range_1[0], range_1[1]), IO))

    def set_overlay_active(self, name, value):
        print("setting overlay %r to %r" % (name, value))
        self.overlays[name][1].B_active = value
        if value == False:
            for s in range(0xD1, 0xD1 + 4):
                sys.stdout.write("%02X " % (self.read_memory(s)))

# TODO The 47 registers of the VIC are mapped in at $d000. Due to the incomplete address decoding, they are repeated every 64 bytes in the area $d000-$d3ff.

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

class VIC_II(Memory):
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

class SID(Memory):
    def __init__(self):
        self.B_active = True
        self.B_can_write = True # in the instance because of ShedSkin
        pass

    #@takes(int, int)
    def read_memory(self, address, size):
        sys.stderr.write("error: SID: do you really think this works? No.\n")
        return 0xFF # FIXME

    #@takes(int, int)
    def write_memory(self, address, value, size):
        print("SID $%X := %r" % (address, value))

"""
$D400-$D401
54272-54273 

Voice #1 frequency.
Write-only.
$D402-$D403
54274-54275 

Voice #1 pulse width.
Write-only.
$D404
54276   

Voice #1 control register. Bits:

    *

      Bit #0: 0 = Voice off, Release cycle; 1 = Voice on, Attack-Decay-Sustain cycle.
    *

      Bit #1: 1 = Synchronization enabled.
    *

      Bit #2: 1 = Ring modulation enabled.
    *

      Bit #3: 1 = Disable voice, reset noise generator.
    *

      Bit #4: 1 = Triangle waveform enabled.
    *

      Bit #5: 1 = Saw waveform enabled.
    *

      Bit #6: 1 = Rectangle waveform enabled.
    *

      Bit #7: 1 = Noise enabled.

Write-only.
$D405
54277   

Voice #1 Attack and Decay length. Bits:

    *

      Bits #0-#3: Decay length. Values:
          o

            %0000, 0: 6 ms.
          o

            %0001, 1: 24 ms.
          o

            %0010, 2: 48 ms.
          o

            %0011, 3: 72 ms.
          o

            %0100, 4: 114 ms.
          o

            %0101, 5: 168 ms.
          o

            %0110, 6: 204 ms.
          o

            %0111, 7: 240 ms.
          o

            %1000, 8: 300 ms.
          o

            %1001, 9: 750 ms.
          o

            %1010, 10: 1.5 s.
          o

            %1011, 11: 2.4 s.
          o

            %1100, 12: 3 s.
          o

            %1101, 13: 9 s.
          o

            %1110, 14: 15 s.
          o

            %1111, 15: 24 s.
    *

      Bits #4-#7: Attack length. Values:
          o

            %0000, 0: 2 ms.
          o

            %0001, 1: 8 ms.
          o

            %0010, 2: 16 ms.
          o

            %0011, 3: 24 ms.
          o

            %0100, 4: 38 ms.
          o

            %0101, 5: 56 ms.
          o

            %0110, 6: 68 ms.
          o

            %0111, 7: 80 ms.
          o

            %1000, 8: 100 ms.
          o

            %1001, 9: 250 ms.
          o

            %1010, 10: 500 ms.
          o

            %1011, 11: 800 ms.
          o

            %1100, 12: 1 s.
          o

            %1101, 13: 3 s.
          o

            %1110, 14: 5 s.
          o

            %1111, 15: 8 s.

Write-only.
$D406
54278   

Voice #1 Sustain volume and Release length. Bits:

    *

      Bits #0-#3: Release length. Values:
          o

            %0000, 0: 6 ms.
          o

            %0001, 1: 24 ms.
          o

            %0010, 2: 48 ms.
          o

            %0011, 3: 72 ms.
          o

            %0100, 4: 114 ms.
          o

            %0101, 5: 168 ms.
          o

            %0110, 6: 204 ms.
          o

            %0111, 7: 240 ms.
          o

            %1000, 8: 300 ms.
          o

            %1001, 9: 750 ms.
          o

            %1010, 10: 1.5 s.
          o

            %1011, 11: 2.4 s.
          o

            %1100, 12: 3 s.
          o

            %1101, 13: 9 s.
          o

            %1110, 14: 15 s.
          o

            %1111, 15: 24 s.
    *

      Bits #4-#7: Sustain volume.

Write-only.
$D407-$D408
54279-54280 

Voice #2 frequency.
Write-only.
$D409-$D40A
54281-54282 

Voice #2 pulse width.
Write-only.
$D40B
54283   

Voice #2 control register.
Write-only.
$D40C
54284   

Voice #2 Attack and Decay length.
Write-only.
$D40D
54285   

Voice #2 Sustain volume and Release length.
Write-only.
$D40E-$D40F
54286-54287 

Voice #3 frequency.
Write-only.
$D410-$D411
54288-54289 

Voice #3 pulse width.
Write-only.
$D412
54290   

Voice #3 control register.
Write-only.
$D413
54291   

Voice #3 Attack and Decay length.
Write-only.
$D414
54292   

Voice #3 Sustain volume and Release length.
Write-only.
$D415
54293   

Filter cut off frequency (bits #0-#2).
Write-only.
$D416
54294   

Filter cut off frequency (bits #3-#10).
Write-only.
$D417
54295   

Filter control. Bits:

    *

      Bit #0: 1 = Voice #1 filtered.
    *

      Bit #1: 1 = Voice #2 filtered.
    *

      Bit #2: 1 = Voice #3 filtered.
    *

      Bit #3: 1 = External voice filtered.
    *

      Bits #4-#7: Filter resonance.

Write-only.
$D418
54296   

Volume and filter modes. Bits:

    *

      Bits #0-#3: Volume.
    *

      Bit #4: 1 = Low pass filter enabled.
    *

      Bit #5: 1 = Band pass filter enabled.
    *

      Bit #6: 1 = High pass filter enabled.
    *

      Bit #7: 1 = Voice #3 disabled.

Write-only.
$D419
54297   

X value of paddle selected at memory address $DD00. (Updates at every 512 system cycles.)
Read-only.
$D41A
54298   

Y value of paddle selected at memory address $DD00. (Updates at every 512 system cycles.)
Read-only.
$D41B
54299   

Voice #3 waveform output.
Read-only.
$D41C
54300   

Voice #3 ADSR output.
Read-only.
$D41D-$D41F
54301-54303 

Unusable (3 bytes).
$D420-$D7FF
54304-55295 

SID register images (repeated every $20, 32 bytes).
"""

A_KEYBOARD_MATRIX_JOYSTICK_2 = 0x00
A_KEYBOARD_KEY_JOYSTICK_1 = 0x01
A_DATA_DIRECTION = 0x02
A_TIMER_A = 0x0E
A_TIMER_B = 0x0F
A_TIME_OF_DAY_TS = 0x08 # in 1/10 s. BCD.
A_TIME_OF_DAY_S = 0x09 # seconds. BCD.
A_TIME_OF_DAY_M = 0x0A # minutes, BCD.
A_TIME_OF_DAY_H = 0x0B # hours, BCD (& AM/PM).
A_SERIAL_SHIFT_REGISTER = 0x0C
A_INTERRUPT_CONTROL_STATUS = 0x0D

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
class CIA1(Memory):
    def __init__(self):
        self.B_can_write = True # in the instance because of ShedSkin
        self.B_active = True
        self.keyboard_matrix_rows = 0 # FIXME
        self.timer_A = Timer()
        self.timer_B = Timer()
        self.pressed_keys = set()
        self.B_interrupt_pending = False

    matrix = [
        ["Delete", "Return", "Right",  "F7",     "F1",     "F3",     "F5"],
        ["3", "W", "A", "4", "Z", "S", "E", "Shift_L"],
        ["5", "R", "D", "6", "C", "F", "T", "X"],
        ["7", "Y", "G", "8", "B", "H", "U", "V"],
        ["9", "I", "J", "0", "M", "K", "O", "N"],
        ["+", "P", "L", "-", ".", ":", "@", ","],
        ["dollar", "*", ";", "Home", "Shift_R", "=", "grave", "/"], # FIXME should be "pound".
        ["1", "BackSpace", "Control_L", "2", "Space", "Meta_L", "Break"],
    ]
    def read_memory(self, address, size = 1):
        assert(size == 1)
        if address == A_KEYBOARD_KEY_JOYSTICK_1:
            if self.keyboard_matrix_rows != 0: # is not None:
#                print("we think keys", self.pressed_keys)
                v = 0
                for row in range(0, 8):
                    if (self.keyboard_matrix_rows & (1 << row)) != 0: # client wants to know
#                        print 'wants', row
                        columns = CIA1.matrix[row]
##                        print("possible", columns)
                        for column_i, cell in enumerate(columns):
                            if cell in self.pressed_keys or cell.lower() in self.pressed_keys:
#                                print("YESSS, matched", cell)
                                v |= (1 << column_i)
#                print("INVKEY", v)
                return 255 - v

            # return bits cleared in rows where a key is pressed in self.keyboard_matrix_column.
            return 0xFF # nothing.
        if address == A_TIMER_A:
            return self.timer_A.get_control_mask()
        elif address == A_TIMER_B:
            return self.timer_B.get_control_mask()
        elif address == A_INTERRUPT_CONTROL_STATUS:
            if self.B_interrupt_pending:
#               print("yes, we had an interrupt")
                self.B_interrupt_pending = False
                return 1<<7 # FIXME the others
            return 0
        else:
            print(hex(address))
            assert(False)

    def write_memory(self, address, value, size):
#       print("CIA#1 $%X := %r" % (address, value))
        # TODO address == A_TIMER_A bit 0: active or not.
        if address == A_KEYBOARD_MATRIX_JOYSTICK_2:
            self.keyboard_matrix_rows = ~(value & 63)
            # other is paddle.
        elif address == A_DATA_DIRECTION:
            # TODO POKE 56322,224 deactivated the keyboard, because the pointer of the CIA 1 is changed. This POKE is using for the joystickscans.
            pass

    def handle_key_press(self, keycode):
        self.pressed_keys.add(keycode)

    def handle_key_release(self, keycode):
        self.pressed_keys.discard(keycode)

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

class CIA2(Memory):
    def __init__(self):
        self.B_can_write = True # in the instance because of ShedSkin
        self.VIC_bank = 0
        self.B_active = True
        self.serial = SerialLine()
        self.RS232 = RS232Line()

    def read_memory(self, address, size = 1):
        """ returns a string """
        assert(size == 1)
        if address == 0:
            return (3 - self.VIC_bank) + self.serial.get_control_mask()
        elif address == 1:
            return self.RS232.get_control_mask()
        else:
            assert(False)
            return 0

    def write_memory(self, address, value, size):
        print("CIA#2 $%X := %r" % (address, value))
        if address == 0:
            self.VIC_bank = 3 - (value & 3) # TODO emit notification?
            # TODO map Char ROM into VIC in banks 0 and 2 at $1000.
            # TODO serial

if __name__ == '__main__':
    c64 = C64()
    c64.VIC.load_chunk(0,0)
    while True:
        c64.fire_timer()
