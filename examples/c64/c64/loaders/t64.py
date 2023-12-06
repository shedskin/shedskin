#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

"""
TODO: the file pointer should move to the next file after the one that was loaded.
TODO: The .t64 file demands that filenames be padded at the end with spaces.
TODO: seek to the end of the filename entry, and replace all consecutive $20 with $A0 internally.
"""

import struct

from . import entries
from .entries import Entry

def find_distances(items):
    h, t = items[0], items[1:]
    if len(t) == 0:
        return []
    else:
        hh, tt = t[0], t[1:]
        return [(hh[0] - h[0], h[1])] + find_distances(t)
class Loader(entries.Loader):
    def __init__(self):
        entries.Loader.__init__(self)
        self.entries = []
        self.offsets = []
    def parse(self, stream, file_name):
        beginning_pos = int(stream.tell())
        stream.seek(0, 2)
        end_pos = int(stream.tell())
        stream.seek(0)
        header_format = "<32s2BHHH24s"
        header_size = struct.calcsize(header_format)
        data = stream.read(header_size)
        version = [0, 0]
        reserved = 0
        assert(len(data) == header_size)
        #(magic, 0, 1, 1, 0, 1, 0, 0, 0, "->ZYRON'S PD<-          ")
        magic, version[0], version[1], max_files, cur_files, reserved, user_description = struct.unpack(header_format, data)
        # assert(version[0] == 0) # whatever
        assert(version[1] == 1)
        # first string = "C64 tape image file", padded with $00.
        magic = magic.rstrip(b"\0")
        assert(magic == b"C64 tape image file" or magic.startswith(b"C64S tape file") or magic.find(b"TAPE") > -1 or magic.find(b"tape") > -1)
        user_description = user_description.rstrip(b"\0") #.decode("petascii") # they can't decide.
        self.entries = []
        # usually 30 entries.
        self.entries = [self.parse_entry(stream) for i in range(cur_files)]
        self.offsets = sorted(map(lambda entry: (entry.tape_pos, entry), self.entries))
        self.offsets.append((end_pos, None))
        for size, entry in find_distances(self.offsets):
            entry.end_addr = entry.start_addr + size
        self.current_entry_index = -1
        self.stream = stream
        return(self)
    def parse_entry(self, stream):
        format = "<BBHHHII16s"
        size = struct.calcsize(format)
        data = stream.read(size)
        assert(len(data) == size)
        B_used, file_type, start_addr, end_addr, reserved_a, tape_pos, reserved_b, file_name = struct.unpack(format, data)
        # B_used > 1: memory snapshot
        #file_type = { # 1541 file type
        #    0x82: "PRG",
        #    0x81: "SEQ",
        #    # etc. # !=0 => PRG
        #}.get(file_type) or file_type
        # end_addr == 0xc3c6 is by a faulty tool; TODO loading all entries, sort by ascending order of offset into T64 (+2 for load addr which is part of the file). 
        B_used, file_type, start_addr, end_addr, reserved_a, tape_pos, reserved_b, file_name = struct.unpack(format, data)
        assert(B_used in [0,1])
        file_name = file_name.rstrip(b"\x20") # b"\0")
        # 0x53
        #file_name = file_name.decode("petascii")
        return(Entry(B_used = B_used > 0,
                     file_type = file_type,
                     start_addr = start_addr,
                     end_addr = 0, # unreliable
                     reserved_a = reserved_a,
                     tape_pos = tape_pos,
                     reserved_b = reserved_b,
                     file_name = file_name))
    def find_next_entry(self, file_name):
        file_name = file_name.rstrip(b"\xA0")
        while self.current_entry_index < len(self.entries):
            entry = self.entries[self.current_entry_index]
            if file_name == b"" or entry.file_name == file_name:
                return(entry)
            self.current_entry_index += 1
        return(None)
    def load_header(self, file_name):
        #type_, file_name, start_addr, stop_addr, data = tape_loader.load_header(file_name)
        self.current_entry_index += 1
        entry = self.find_next_entry(file_name)
        return(entry)
        #return(entry.file_type, entry.file_name, entry.start_addr, entry.end_addr)
    def load_data(self, file_name):
        entry = self.find_next_entry(file_name)
        self.stream.seek(entry.tape_pos)
        data = self.stream.read(entry.end_addr - entry.start_addr)
        #data = tape_loader.load_data(file_name)
        return(data)
