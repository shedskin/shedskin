#!/usr/bin/env python
# I, Danny Milosavljevic, hereby place this file into the public domain.

class DigitalJoystick(object):
    def __init__(self):
        self.B_left = False
        self.B_right = False
        self.B_up = False
        self.B_down = False
        self.B_fire_1 = False
        self.B_fire_2 = False
#address $DC00. column driver for the keyboard matrix, and is normally configured as outputs (by writing $FF to $DC02) in the keyboard scanning routine. 
#address $DC01. row inputs from the keyboard and is normally configured as input (by writing $00 to $DC03) in the kernal keyboard scanning routine. 
