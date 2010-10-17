#!/usr/bin/env python

class Memory(object):
    def __init__(self):
        self.B_can_write = True # in the instance because of ShedSkin

    def read_memory(self, address, size = 1):
        return 0xFF

    def write_memory(self, address, value, size):
        pass

