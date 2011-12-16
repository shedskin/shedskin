#!/usr/bin/env python

class IECMember(object):
    def __init__(self, IEC, bus_address):
        self.B_clock = False
        self.B_data = True
        self.B_ATN = False
        self.bus_address = bus_address
        self.IEC = IEC
        self.B_talker = False # effect not immediate
        self.B_switch_talker = False
        self.received_count = 0
        self.received_value = 0

    def get_data(self):
        return(self.B_data)

class IECBus(object):
    pass
