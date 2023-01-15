#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

# public: calculate_pixbuf_data

import sys

SPRITE_COUNT = 8

#sprite = open(sys.argv[1], "rb").read()[2:]
WIDTH = 24
HEIGHT = 21

#def from_high_resolution_sprite(sprite, primary_color):
#    result = []
#    for cell in sprite:
#        for item in [
#            primary_color if (cell & (1 << (7 - column_i))) != 0
#            else [0,0,0,0] for column_i in range(8)]:
#            result += item
#    return(result)

#def from_multi_color_sprite(sprite, primary_color, multicolor_0, multicolor_1):
#    result = []
#    #for i in range(8):
#    #    result += [0xFF,0,0,0xFF]
#    masks = [0x03, 0x0C, 0x30, 0xC0]
#    colors = [
#        [0x00, 0x00, 0x00, 0x00],
#        multicolor_0, # $D025
#        primary_color, # $D027..$D02E
#        multicolor_1, # $D026
#    ]
#    for cell in sprite:
#        for item in reversed([colors[(cell & masks[column_i]) >> (column_i * 2)] for column_i in range(4)]):
#            result += item * 2
#    return(result)

#data = from_high_resolution_sprite(sprite)
#frame_size = 4 * 64 * 8 # WIDTH * 4 * HEIGHT + 4
#data = from_multi_color_sprite(sprite)

#def calculate_pixbuf_data(sprite_data, primary_color, B_multicolor, multicolor_0, multicolor_1):
#    if B_multicolor:
#        data = from_multi_color_sprite(map(ord, sprite_data), primary_color, multicolor_0, multicolor_1)
#    else:
#        data = from_high_resolution_sprite(map(ord, sprite_data), primary_color)
#    return("".join(map(chr, data)))
