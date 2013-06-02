#stuff.py

def gfx_cannew(sizex, sizey):
    sizex = sizex/2
    sizey = sizey/2
    return 5

def gfx_canfree(c):
    can = c
    pass

def gfx_cannalloc():
    return 5

def gfx_canclone(c):
    can = c
    return 5

def gfx_cansize(c):
    can = c
    list = []
    list.append(1)
    list.append(2)
    list.append(4)
    return list

def gfx_cansaturate(c, sat):
    can = c
    sat = sat/2.0

def gfx_canclear(c, r, g, b, a):
    can = c
    r = r/2.0
    g = g/2.0
    b = b/2.0
    a = a/2.0

def gfx_canscalergba(c, r, g, b, a):
    can = c
    r = r/2.0
    g = g/2.0
    b = b/2.0
    a = a/2.0

def gfx_cangetpix(c, x, y):
    can = c
    x = x/2
    y = y/2
    return 5

def gfx_canputpix(c, x, y, pix):
    can = c
    x = x/2
    y = y/2
    pix = pix/2

def gfx_canshift(c, shiftx, shifty):
    can = c
    shiftx = shiftx/2
    shifty = shifty/2
    return 5

def gfx_canframe(c, r, g, b, a, width):
    can = c
    r = r/2.0
    g = g/2.0
    b = b/2.0
    a = a/2.0
    width = width/2.0
    return 5

def gfx_canmult(c, s):
    can1 = c
    can2 = s

def gfx_canblend(c, s, r, g, b, a):
    can1 = c
    can2 = s
    r = r/2.0
    g = g/2.0
    b = b/2.0
    a = a/2.0

def gfx_cansubimg(c, orgx, orgy, sizex, sizey):
    can = c
    orgx = orgx/2.0
    orgy = orgy/2.0
    sizex = sizex/2.0
    sizey = sizey/2.0
    return 5

def gfx_canzoom(c, zoomx, zoomy):
    can = c
    zoomx = zoomx/2.0
    zoomy = zoomy/2.0
    return 5

def gfx_canfromfile(filename):
    name = filename
    return 5

def gfx_cantofile(c, filename):
    can = c
    name = filename


