#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

class Entry(object):
    def __init__(self, B_used, file_type, start_addr, end_addr, reserved_a, tape_pos, reserved_b, file_name):
        self.file_type = file_type
        self.start_addr = start_addr
        self.end_addr = end_addr # unreliable.
        self.reserved_a = reserved_a
        self.tape_pos = tape_pos
        self.reserved_b = reserved_b
        self.file_name = file_name
    #def __str__(self):
    #    return(self.file_name)
    #def __repr__(self):
    #    return("Entry(**%r)" % self.__dict__)
class Loader(object):
    def __init__(self):
        pass
#    def parse(self, stream, file_name):
#        pass
#    def load_header(self, file_name):
#        pass
#    def load_data(self, file_name):
#        pass
