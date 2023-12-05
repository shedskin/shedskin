#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import os
import struct

from . import entries
from .entries import Entry

class Loader(entries.Loader):
    def __init__(self):
        self.start_addr = 0
        self.end_addr = 0
        self.file_name = b""
        self.size = 0
        self.stream = None
        pass
    def parse(self, stream, file_name):
        beginning_pos = int(stream.tell())
        stream.seek(0, 2)
        end_pos = int(stream.tell())
        stream.seek(0)
        self.file_name = file_name
        self.size = end_pos - beginning_pos
        header_format = "<H"
        header_size = struct.calcsize(header_format)
        data = stream.read(header_size)
        assert(len(data) == header_size)
        # FIXME start_addr, = struct.unpack(header_format, data)
        start_addr = data[0] | (data[1] << 8)
        self.start_addr = start_addr
        self.end_addr = self.start_addr + end_pos - 1
        self.stream = stream
        return(self)
    def load_header(self, file_name):
        file_name = os.path.basename(self.file_name) # TODO mangle back to C64 format (16 char filename).
        file_type = 0x82 # PRG
        #type_, file_name, start_addr, stop_addr, data = tape_loader.load_header(file_name)
        print("loading header PRG")
        #return(file_type, file_name, self.start_addr, self.end_addr)
        tape_pos = 0
        return(Entry(B_used = True, file_type = file_type, start_addr = self.start_addr, end_addr = self.end_addr, reserved_a = 0, tape_pos = tape_pos, reserved_b = 0, file_name = file_name))
    def load_data(self, file_name):
        print("loading data PRG")
        self.stream.seek(0)
        data = self.stream.read(self.end_addr - self.start_addr + 1)
        return(data)
