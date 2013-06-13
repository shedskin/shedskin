#
#       C image processing example
#
#       Paul Haeberli - 2013
#
#	This is the interface for calling C
#
def gfx_cannew(sizex, sizey):
    return 5

def gfx_canfree(c):
    pass

def gfx_cannalloc():
    return 5

def gfx_canclone(c):
    return 5

def gfx_cansize(c):
    list = []
    list.append(5)	# make this a list of integers!
    return list

def gfx_cansaturate(c, sat):
    pass

def gfx_canclear(c, r, g, b, a):
    pass

def gfx_canscalergba(c, r, g, b, a):
    pass

def gfx_cangetpix(c, x, y):
    return 5

def gfx_canputpix(c, x, y, pix):
    pass

def gfx_canshift(c, shiftx, shifty):
    return 5

def gfx_canframe(c, r, g, b, a, width):
    return 5

def gfx_canmult(c, s):
    pass

def gfx_canblend(c, s, r, g, b, a):
    pass

def gfx_cansubimg(c, orgx, orgy, sizex, sizey):
    return 5

def gfx_canzoom(c, zoomx, zoomy):
    return 5

def gfx_canfromfile(filename):
    return 5

def gfx_cantofile(c, filename):
    pass

def gfx_gccollect():
    pass
