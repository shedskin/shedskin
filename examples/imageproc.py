# C image processing example for shedskin. This shows doing simple image 
# processing in C, and uses the __del__ method in the canvas class to 
# automatically free a C data scructure that points to the image data.
#
# Only a few of the methods in the point and rect classes are used.
#
# Please feel free to use this code in any way you want!
#
# Paul Haeberli - 2013

import sys
import math
import libgfx

# misc utils

FLAGVAL	= 3-(256*256*128)

def lerp(v0, v1, p):
    return v0*(1.0-p)+v1*p

def fmod(x, y):
    return float(x - y*math.floor(x/float(y)))

def limit(val, min, max):
    if val < min:
        return min
    if val > max:
        return max
    return val

def delta(a, b):
    d = a-b
    if d > 0:
        return d
    else:
        return -d

# point class

class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "point: " + str(self.x) + " " + str(self.y)

    def clone(self):
        return point(self.x, self.y)

    def equal(self, p):
        if self.x != p.x:
            return False
        if self.y != p.y:
            return False
        return True

    def round(self):
        return point(round(self.x), round(self.y))

    def translate(self, tx, ty):
        return point(self.x+tx, self.y+ty)

    def scale(self, sx, sy=FLAGVAL):
        if sy == FLAGVAL:
            sy = sx
        return point(self.x*sx, self.y*sy)

    def rotate(self, angle):
        angle = int(round(angle))
        while angle<0:
            angle += 360
        while angle>=360:
            angle -= 360
        if angle == 90:
            return point(-self.y, self.x)
        if angle == 180:
            return point(-self.x, self.y)
        if angle == 270:
            return point(self.y, -self.x)
        return self.clone()

    def distance(self, p):
        dx = self.x-p.x
        dy = self.y-p.y
        return math.sqrt(dx*dx+dy*dy)


def pointlerp(p0, p1, param):
    return point(lerp(p0.x,p1.x,param), lerp(p0.y,p1.y,param))

def pointdistance(p0, p1):
    dx = p1.x-p0.x
    dy = p1.y-p0.y
    return math.sqrt(dx*dx+dy*dy)

def vector(p1, p0=False):
    if p0 == False:
        return p1.clone()
    else:
        return point(p1.x-p0.x, p1.y-p0.y)

def pointsequal(p0, p1):
    return p0.equal(p1)

def size(x, y):
    return point(x, y)


# rectangle class

POS_LT = 0
POS_IN = 1
POS_GT = 2

class rect:
    def __init__(self, orgx, orgy, sizex, sizey):
        self.orgx = orgx
        self.orgy = orgy
        self.sizex = sizex
        self.sizey = sizey

    def __str__(self):
        return "rect: org: " + str(self.orgx) + "," + str(self.orgy) + " size: " + str(self.sizex) + "," + str(self.sizey)

    def clone(self):
        return rect(self.orgx, self.orgy, self.sizex, self.sizey)

    def area(self):
        return self.sizex * self.sizey

    def diameter(self):
        return math.sqrt(self.sizex*self.sizex+self.sizey*self.sizey)

    def aspect(self):
        return self.sizex/float(self.sizey)

    def origin(self):
        return point(self.orgx, self.orgy)

    def ll(self):
        return point(self.orgx, self.orgy)

    def lr(self):
        return point(self.orgx+self.sizex, self.orgy)

    def ur(self):
        return point(self.orgx+self.sizex, self.orgy+self.sizey)

    def ul(self):
        return point(self.orgx, self.orgy+self.sizey)

    def midx(self):
        return self.orgx+self.sizex/2.0

    def midy(self):
        return self.orgy+self.sizey/2.0

    def minx(self):
        return self.orgx

    def miny(self):
        return self.orgy

    def maxx(self):
        return self.orgx+self.sizex

    def maxy(self):
        return self.orgy+self.sizey

    def center(self):
        return point(self.orgx+self.sizex/2.0, self.orgy+self.sizey/2.0)

    def atzero(self):
        return rectsize(self.sizex, self.sizey)

    def difference(self, r):
        return max(pointdistance(self.ll(), r.ll()), pointdistance(self.ur(), r.ur()))

    def inset(self, inx, iny):     
        return rect(self.orgx+inx, self.orgy+iny, self.sizex-2*inx, self.sizey-2*iny)

    def expand(self, outx, outy): 
        return rect(self.orgx-outx, self.orgy-outy, self.sizex+2*outx, self.sizey+2*outy)

    def flip(self):
        return rect(self.orgx, self.orgy+self.sizey, self.sizex, -self.sizey)

    def setorg(self, x, y):
        r = self.clone()
        r.orgx = x
        r.orgy = y
        return r

    def isnull(self):
        if self.orgx != FLAGVAL:
            return False
        if self.orgy != FLAGVAL:
            return False
        if self.sizex != FLAGVAL:
            return False
        if self.sizey != FLAGVAL:
            return False
        return True

    def translate(self, offset):
        return rect(self.orgx+offset.x, self.orgy+offset.y, self.sizex, self.sizey)

    def scale(self, center, scale):
        return rect(center.x + (scale*(self.orgx-center.x)),
                    center.y + (scale*(self.orgy-center.y)),
                    scale*self.sizex,
                    scale*self.sizey)

    def centerscale(self, scale):
        return self.scale(self.center(), scale)

    def fitinrect(self, r):
        return rectfitinrect(r, self)

    def containspoint(self, p):
        if p.x < self.minx():
            return False
        if p.y < self.miny():
            return False
        if p.x > self.maxx():
            return False
        if p.y > self.maxy():
            return False
        return True

    def equal(self, r):
        if r.sizex != self.sizex:
            return False
        if r.sizey != self.sizey:
            return False
        if r.orgx != self.orgx:
            return False
        if r.orgy != self.orgy:
            return False
        return True

    def sizeequal(self, r):
        if r.sizex != self.sizex:
            return False
        if r.sizey != self.sizey:
            return False
        return True

    def containsrect(self, r):
        return rectunion(self,r).equal(self)

    def pointdistance(self, p):
        cx = POS_IN
        if p.x < self.minx():
           cx = POS_LT
        if p.x > self.maxx():
           cx = POS_GT
        cy = POS_IN
        if p.y < self.miny():
            cy = POS_LT
        if p.y > self.maxy():
            cy = POS_GT
        if cx == POS_LT:
            if cy == POS_LT:
                return pointdistance(p,self.ll())
            if cy == POS_IN:
                return delta(self.minx(),p.x)
            if cy == POS_GT:
                return pointdistance(p,self.ul())
        if cx == POS_IN:
            if cy == POS_LT:
                return delta(self.miny(),p.y)
            if cy == POS_IN:
                return 0.0
            if cy == POS_GT:
                return delta(self.maxy(),p.y)
        if cx == POS_GT:
            if cy == POS_LT:
                return pointdistance(p,self.lr())
            if cy == POS_IN:
                return delta(self.maxx(),p.x)
            if cy == POS_GT:
                return pointdistance(p,self.ur())
            return 0.0

    def pointtoparam(self, p):
        return point((p.x-self.minx())/float(self.sizex), (p.y-self.miny())/float(self.sizey))

    def pointfromparam(self, p):
        return point(lerp(self.minx(),self.maxx(),p.x), lerp(self.miny(),self.maxy(),p.y)) 

    def recttoparam(self, r):
        return rect(r.orgx/float(self.sizex), r.orgy/float(self.sizey), 
                    r.sizex/float(self.sizex), r.sizey/float(self.sizey))

    def rectfromparam(self, r):
        return rect(lerp(self.minx(),self.maxx(),r.orgx),
                    lerp(self.miny(),self.maxy(),r.orgy),
                    self.sizex*r.sizex, self.sizey*r.sizey)

    def roundout(self):
        minx = int(math.floor(self.minx()))
        miny = int(math.floor(self.miny()))
        maxx = int(math.ceil(self.maxx()))
        maxy = int(math.ceil(self.maxy()))
        return rect(minx, miny, maxx-minx, maxy-miny)

    def round(self):
        minx = int(self.minx())
        miny = int(self.miny())
        maxx = int(self.maxx())
        maxy = int(self.maxy())
        return rect(minx, miny, maxx-minx, maxy-miny)

def rectsize(sizex, sizey):
    return rect(0, 0, sizex, sizey)

def rectnull():
    return rect(FLAGVAL, FLAGVAL, FLAGVAL, FLAGVAL)

def rectsequal(r0, r1):
    if r0.sizex != r1.sizex:
        return False
    if r0.sizey != r1.sizey:
        return False
    if r0.orgx != r1.orgx:
        return False
    if r0.orgy != r1.orgy:
        return False
    return True

def rectunion(a, b):
    if a.isnull():
        return b
    if b.isnull():
        return a
    minx = min(a.orgx, b.orgx)
    maxx = max(a.maxx(), b.maxx())
    miny = min(a.orgy, b.orgy)
    maxy = max(a.maxy(), b.maxy())
    return rect(minx, miny, maxx-minx, maxy-miny)

def rectintersect(a, b):
    if a.isnull():
        return rectnull()
    if b.isnull():
        return rectnull()
    bmaxx = b.orgx + b.sizex
    bmaxy = b.orgy + b.sizey
    amaxx = a.orgx + a.sizex
    amaxy = a.orgy + a.sizey
    if a.orgx > bmaxx:
        return rectnull()
    if a.orgy > bmaxy:
        return rectnull()
    if b.orgx > amaxx:
        return rectnull()
    if b.orgy > amaxy:
        return rectnull()
    minx = max(a.orgx, b.orgx)
    maxx = min(amaxx, bmaxx)
    miny = max(a.orgy, b.orgy)
    maxy = min(amaxy, bmaxy)
    return rect(minx, miny, maxx-minx, maxy-miny)

def rectdifference(r0, r1):
    return max(pointdistance(r0.ll(), r1.ll()), pointdistance(r0.ur(), r1.ur()))

def rectlerp(r0, r1, param):
    ll = pointlerp(r0.ll(), r1.ll(), param)
    ur = pointlerp(r0.ur(), r1.ur(), param)
    return rect(ll.x, ll.y, ur.x-ll.x, ur.y-ll.y)

def rectcenterinrect(outr, inr):
    center = outr.center()
    r = inr.clone()
    r.orgx = round(center.x-inr.sizex/2.0)
    r.orgy = round(center.y-inr.sizey/2.0)
    return r

def rectfitinrect(outr, inr):
    iaspect = inr.aspect()
    waspect = outr.aspect()
    if iaspect > waspect:
        sizex = outr.sizex
        sizey = round(sizex/iaspect)
    else:
        sizey = outr.sizey
        sizex = round(sizey*iaspect)
    return rectcenterinrect(outr, rectsize(sizex, sizey))

def rectonpoint(p, delta):
    return rect(p.x-delta/2.0, p.y-delta/2.0, delta, delta)

# canvas class

class canvas():
    def __init__(self):
        self.name = ""

    def init(self):
        self.rect = rectsize(self.sizex, self.sizey)
        self.name = ""
        self.readonly = False
        self.diagsize = float(math.sqrt(self.sizex*self.sizex+self.sizey*self.sizey))
        self.units = float(max(self.sizex, self.sizey))
        self.origin = point(0.0,0.0)

    def initsize(self, sizex, sizey):
        self.can = libgfx.gfx_cannew(sizex, sizey)
        self.sizex = sizex
        self.sizey = sizey
        self.nchans = 4
        self.init()

    def initpointer(self, ptr):
	self.can = ptr
	size = libgfx.gfx_cansize(self.can)
	self.sizex = size[0]
	self.sizey = size[1]
	self.nchans = size[2]
        self.init()

    def __str__(self):
        return "canvas: size: " + str(self.rect.sizex) + "," + str(self.rect.sizey) + " nchans: " + str(self.nchans)

    def __del__(self):
#        print "canvas: DESTRUCT"
#        print self
        if self.can != 0:
            libgfx.gfx_canfree(self.can)
            self.can = 0

    def setreadonly(self, ro):
        self.readonly = ro

    def touched(self):
        if self.readonly:
            print "Error: Canvas is readonly"
            print self

    def tofile(self, filename):
        libgfx.gfx_cantofile(self.can, filename)
        return self

    # misc utils

    def putpix(self, x, y, pix):
        libgfx.gfx_canputpix(self.can, x, y, pix)

    def getpix(self, x, y):
        return libgfx.gfx_cangetpix(self.can, x, y)

    def saturate(self, sat):
        self.touched()
        libgfx.gfx_cansaturate(self.can, sat)
        return self

    def shift(self, shiftx, shifty):    # pix dim
	c = canvas()
  	c.initpointer(libgfx.gfx_canshift(self.can, int(shiftx), int(shifty)))
        c.origin.x = self.origin.x - shiftx
        c.origin.y = self.origin.y - shifty
        return c

    def frame(self, r, g, b, a, width): # pix dim
	c = canvas()
        c.initpointer(libgfx.gfx_canframe(self.can, r, g, b, a, width))
        c.origin.x = self.origin.x + width
        c.origin.y = self.origin.y + width
        return c

    def subimage(self, r):              # pix dim
	c = canvas()
        c.initpointer(libgfx.gfx_cansubimg(self.can, int(r.orgx), int(r.orgy), int(r.sizex), int(r.sizey)))
        c.origin.x = self.origin.x - int(r.orgx)
        c.origin.y = self.origin.y - int(r.orgy)
        return c

    def zoom(self, zoomx, zoomy):
	c = canvas()
  	c.initpointer(libgfx.gfx_canzoom(self.can, zoomx, zoomy))
        c.origin.x = c.origin.x * zoomx
        c.origin.y = c.origin.y * zoomy
        return c

    def clone(self):
	c = canvas()
        c.initpointer(libgfx.gfx_canclone(self.can))
        c.origin = self.origin
        return c

    def new(self):
	c = canvas()
        c.initpointer(libgfx.gfx_cannew(self.rect.sizex,self.rect.sizey))
        c.origin = self.origin
        return c

    def blend(self, c, r, g, b, a):
        self.touched()
        libgfx.gfx_canblend(self.can, c.can, r, g, b, a)
        return self

    def mult(self, c):
        self.touched()
        libgfx.gfx_canmult(self.can, c.can)
        return self

    def scalergba(self, r, g, b, a):
        self.touched()
        libgfx.gfx_canscalergba(self.can, r, g, b, a)
        return self

    def clear(self, r, g, b, a):
        self.touched()
        libgfx.gfx_canclear(self.can, r, g, b, a)
        return self

def canvasfromfile(filename):
    can = canvas()
    ptr = libgfx.gfx_canfromfile(filename)
    can.initpointer(ptr)
    return can

def canvasnew(sizex, sizey):
    can = canvas()
    can.initsize(sizex, sizey)
    return can

def canvasnalloc():
    return libgfx.gfx_cannalloc()

print "LERP: " + str(lerp(0.0,1.0,0.5))
print "FMOD: " + str(fmod(-23,5))
print "LIMIT: " + str(limit(-3.0,0.0,1.0))
print "DELTA: " + str(delta(4.5,4.6))

p = point(10.0,0.0)
b = point(0,20)
s = point(0,20).scale(3.0)
print s
g = point(0,20).scale(3.0, 0.0)
print g

p = p.clone()
print p
print b
if p.equal(b):
    print "SAME"
else:
    print "DIFFER"

r1 = rect(0,0,100,100)
r2 = rect(50,50,100,100)
r = rectintersect(r1,r2)
print r

print "N CANVASES ALLOCATED: " + str(canvasnalloc())

def testcanvases():
    c = canvasfromfile("smallpic.tga")
    print "smallpic: " + str(c)

    d = c.subimage(rect(150,150,300,150))
    d.tofile("small.tga")

    z = d.zoom(2.6,2.6)
    d.saturate(3.0)
    d.tofile("saturate.tga")
    c.putpix(20,20,45)
    print "GET PIX: " + str(c.getpix(20,20))

    sh = d.shift(10,10)
    sh.tofile("shift.tga")
    sh = d.frame(0.5, 0.5, 0.5, 1.0, 20)
    sh.tofile("frame.tga")

    c = sh.clone()
    sh.__del__()
    #libgfx.gfx_canfree(sh.can)
    c.scalergba(1.0, 0.0, 0.0, 1.0)
    c.tofile("red.tga")

for i in range(100):
    testcanvases()
    print "N CANVASES STILL ALLOCATED: " + str(canvasnalloc())
