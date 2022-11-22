#!/usr/bin/env python2

# tape emulation

from .symbols import *
from .loaders import t64, prg

tape_loader = t64.Loader() # public. set this from the main emu GUI.

T_EOF = 0x40
WRITE_LEADER = 0x0A
WRITE_BLOCK = 0x08
READ_BLOCK = 0x0E
# SCAN_KEY = 0x0C
err = 0

def get_tape_buffer(memory):
    return(memory.read_memory(0xB2, 1) | (memory.read_memory(0xB3, 1) << 8))

def get_file_name_length(memory):
    return(memory.read_memory(0xB7, 1))

def get_file_name_address(memory):
    return(memory.read_memory(0xBB, 1) | (memory.read_memory(0xBC) << 8))

def get_stop_location(memory):
    return(memory.read_memory(0xAE, 1) | (memory.read_memory(0xAF) << 8))

#def get_status(memory):
#    return(memory.read_memory(0x90, 1))

def set_status(memory, value):
    return(memory.write_memory(0x90, value, 1))

#def get_VERCKK(memory):
#    return(memory.read_memory(0x93, 1))

def set_VERCKK(memory, value):
    return(memory.write_memory(0x93, value, 1))

def set_IRQTMP(memory, value): # if = [$315] then end IO
    return(memory.write_memory(0x2A0, value, 1))

def get_start_location(memory):
    return(memory.read_memory(0xC1, 1) | (memory.read_memory(0xC2) << 8))

OFFSET_TYPE = 0
OFFSET_NAME = 5
OFFSET_START_ADDR = 1
OFFSET_STOP_ADDR = 3

def setup_tape_header(type, file_name, start_addr, stop_addr, memory):
    buffer_addr = get_tape_buffer(memory)
    file_name = (file_name + (b" "*16))[:16]
    for i in range(16):
        memory.write_memory(buffer_addr + OFFSET_NAME + i, file_name[i], 1)
    memory.write_memory(buffer_addr + OFFSET_TYPE, type, 1)
    memory.write_memory(buffer_addr + OFFSET_START_ADDR, start_addr, 2)
    memory.write_memory(buffer_addr + OFFSET_STOP_ADDR, stop_addr, 2)

def get_file_name(memory):
    file_name_length = 0 # ShedSkin
    file_name_addr = 0 # ShedSkin
    file_name_addr = get_file_name_address(memory)
    file_name_length = get_file_name_length(memory)
    # TODO replace invalid (not in "0-9A-Za-z._") by "."
    return bytes([memory.read_memory(file_name_addr + i, 1) for i in range(min(16, file_name_length))])

def find_header(CPU, memory): # read a block from tape
    """ trap 0xF72F, originally was [0x20, 0x41, 0xF8]. """
    file_name = get_file_name(memory)
    start_addr = 0 # ShedSkin
    stop_addr = 0 # ShedSkin
    type_ = 3 # 1 relocatable program; 2 SEQ data block; 3 non-relocatable program; 4 SEQ file header; 5 End-of-tape
    file_name = b"" # ShedSkin
    #type_, file_name, start_addr, stop_addr
    header = tape_loader.load_header(file_name)
    if header is None:
        print("umm... no file on tape?")
        set_status(memory, 0x30) # Checksum error and pass2 error.
        err = -1
    else:
        setup_tape_header(type_, header.file_name, header.start_addr, header.end_addr, memory)
        set_status(memory, 0)
        err = 0
    set_VERCKK(memory, 0) # FIXME do we have to set this?
    set_IRQTMP(memory, 0)
    if err == 0:
        CPU.CLC()
    else:
        CPU.SEC()
    CPU.clear_Z() # FIXME
    CPU.set_PC(0xF732)

def write_header(CPU, memory):
    """ trap 0xF7BE, originally was [0x20, 0x6B, 0xF8]. """
    CPU.set_PC(0xF7C1)
    return

def transfer(CPU, memory):
    """ trap 0xF8A1, originally was [0x20, 0xBD, 0xFC]. """
    err = 0
    st = 0
    X = CPU.read_register(S_X)
    if X == WRITE_LEADER:
        pass
    elif X == WRITE_BLOCK:
        pass
    elif X == READ_BLOCK:
        start = get_start_location(memory)
        end = get_stop_location(memory)
        size = end - start # !!!!!
        file_name = get_file_name(memory)
        data = b"" # ShedSkin
        data = tape_loader.load_data(file_name)
        for i in range(size):
            memory.write_memory(start + i, data[i], 1)
        st |= T_EOF
    else:
        err = -1
    set_IRQTMP(memory, 0)
    set_status(memory, st) # get_status(memory) | st)
    if err == 0:
        CPU.CLC()
    else:
        CPU.SEC()
    CPU.set_PC(0xFC93)

def get_hooks():
    return [0xF8A1, 0xF7BE, 0xF72F]
    """{0xF8A1: transfer,
            0xF7BE: write_header,
            0xF72F: find_header}.keys()"""

def call_hook(CPU, memory, PC):
    #PC = CPU.read_register(S_PC)
    if PC == 0xF8A1:
        return(transfer(CPU, memory))
    elif PC == 0xF7BE:
        return(write_header(CPU, memory))
    elif PC == 0xF72F:
        return(find_header(CPU, memory))
    else:
        pass

def set_image_name(name, format):
    global tape_loader
    if format == b"PRG":
        tape_loader = prg.Loader().parse(open(name, "rb"), name)
    else:
        tape_loader = t64.Loader().parse(open(name, "rb"), name)
