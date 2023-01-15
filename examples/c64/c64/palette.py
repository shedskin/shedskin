#!/usr/bin/env python2

colors = [
    [0, 0, 0, 0xFF],
    [255, 255, 255, 0xFF],
    [116, 67, 53, 0xFF],
    [124, 172, 186, 0xFF], 
    [123, 72, 144, 0xFF], 
    [100, 151, 79, 0xFF],
    [63, 50, 133, 0xFF],
    [191, 205, 122, 0xFF],
    [123, 91, 47, 0xFF],
    [79, 69, 0, 0xFF],
    [163, 114, 101, 0xFF],
    [80, 80, 80, 0xFF],
    [120, 120, 120, 0xFF],
    [164, 215, 142, 0xFF],
    [120, 106, 189, 0xFF],
    [159, 159, 159, 0xFF],
]

def get_RGBA32_pixel(index):
    item = colors[index]
    #return(item[3] | (item[2] << 8) | (item[1] << 16) | (item[0] << 24))
    return(item[0] | (item[1] << 8) | (item[2] << 16) | (item[3] << 24))
