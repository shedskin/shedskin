#
#       C image processing example for shedskin.  This shows doing simple image processing
#       in C, and uses the __del__ method in the canvas class to automatically free a C
#       data scructure that points to the image data.
#
#       Please feel free to use this code in any way you want!
#
#       Paul Haeberli - 2013
#
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

# Point class

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return 'Point: ' + str(self.x) + ' ' + str(self.y)

    def __del__(self):
        print('del Point')

    def clone(self):
        return Point(self.x, self.y)

    def equal(self, p):
        if self.x != p.x:
            return False
        if self.y != p.y:
            return False
        return True

    def round(self):
        return Point(round(self.x), round(self.y))

    def translate(self, tx, ty):
        return Point(self.x+tx, self.y+ty)

    def scale(self, sx, sy=FLAGVAL):
        if sy == FLAGVAL:
            sy = sx
        return Point(self.x*sx, self.y*sy)

    def rotate(self, angle):
        angle = int(round(angle))
        while angle<0:
            angle += 360
        while angle>=360:
            angle -= 360
        if angle == 90:
            return Point(-self.y, self.x)
        if angle == 180:
            return Point(-self.x, self.y)
        if angle == 270:
            return Point(self.y, -self.x)
        return self.clone()

    def distance(self, p):
        dx = self.x-p.x
        dy = self.y-p.y
        return math.sqrt(dx*dx+dy*dy)

def pointlerp(p0, p1, param):
    return Point(lerp(p0.x,p1.x,param), lerp(p0.y,p1.y,param))

def size(x, y):
    return Point(x, y)

# Rectangle class

POS_LT = 0
POS_IN = 1
POS_GT = 2

class Rect:
    def __init__(self, orgx, orgy, sizex, sizey):
        self.orgx = orgx
        self.orgy = orgy
        self.sizex = sizex
        self.sizey = sizey

    def __str__(self):
        return 'Rect: org: ' + str(self.orgx) + ',' + str(self.orgy) + ' size: ' + str(self.sizex) + ',' + str(self.sizey)

    def __del__(self):
        print('del Rect')

    def clone(self):
        return Rect(self.orgx, self.orgy, self.sizex, self.sizey)

    def area(self):
        return self.sizex * self.sizey

    def diameter(self):
        return math.sqrt(self.sizex*self.sizex+self.sizey*self.sizey)

    def aspect(self):
        return self.sizex/float(self.sizey)

    def origin(self):
        return Point(self.orgx, self.orgy)

    def ll(self):
        return Point(self.orgx, self.orgy)

    def lr(self):
        return Point(self.orgx+self.sizex, self.orgy)

    def ur(self):
        return Point(self.orgx+self.sizex, self.orgy+self.sizey)

    def ul(self):
        return Point(self.orgx, self.orgy+self.sizey)

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
        return Point(self.orgx+self.sizex/2.0, self.orgy+self.sizey/2.0)

    def atzero(self):
        return rectsize(self.sizex, self.sizey)

    def inset(self, inx, iny):     
        return Rect(self.orgx+inx, self.orgy+iny, self.sizex-2*inx, self.sizey-2*iny)

    def expand(self, outx, outy): 
        return Rect(self.orgx-outx, self.orgy-outy, self.sizex+2*outx, self.sizey+2*outy)

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
        return Rect(self.orgx+offset.x, self.orgy+offset.y, self.sizex, self.sizey)

    def scale(self, center, scale):
        return Rect(center.x + (scale*(self.orgx-center.x)),
                    center.y + (scale*(self.orgy-center.y)),
                    scale*self.sizex,
                    scale*self.sizey)

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

    def round(self):
        minx = int(self.minx())
        miny = int(self.miny())
        maxx = int(self.maxx())
        maxy = int(self.maxy())
        return Rect(minx, miny, maxx-minx, maxy-miny)

def rectsize(sizex, sizey):
    return Rect(0, 0, sizex, sizey)

def rectnull():
    return Rect(FLAGVAL, FLAGVAL, FLAGVAL, FLAGVAL)

def rectunion(a, b):
    if a.isnull():
        return b
    if b.isnull():
        return a
    minx = min(a.orgx, b.orgx)
    maxx = max(a.maxx(), b.maxx())
    miny = min(a.orgy, b.orgy)
    maxy = max(a.maxy(), b.maxy())
    return Rect(minx, miny, maxx-minx, maxy-miny)

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
    return Rect(minx, miny, maxx-minx, maxy-miny)

# Canvas class

class Canvas():
    def __init__(self):
        self.name = ''

    def init(self):
        self.rect = rectsize(self.sizex, self.sizey)
        self.name = ''
        self.readonly = False
        self.diagsize = float(math.sqrt(self.sizex*self.sizex+self.sizey*self.sizey))
        self.units = float(max(self.sizex, self.sizey))
        self.origin = Point(0.0,0.0)

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
        return 'Canvas: size: ' + str(self.rect.sizex) + ',' + str(self.rect.sizey) + ' nchans: ' + str(self.nchans)

    def __del__(self):
        if self.can != 0:
	    print('del Canvas')
            libgfx.gfx_canfree(self.can)
            self.can = 0

    def setreadonly(self, ro):
        self.readonly = ro

    def touched(self):
        if self.readonly:
            print('Error: Canvas is readonly')
            print(self)

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
	c = Canvas()
  	c.initpointer(libgfx.gfx_canshift(self.can, int(shiftx), int(shifty)))
        c.origin.x = self.origin.x - shiftx
        c.origin.y = self.origin.y - shifty
        return c

    def frame(self, r, g, b, a, width): # pix dim
	c = Canvas()
        c.initpointer(libgfx.gfx_canframe(self.can, r, g, b, a, width))
        c.origin.x = self.origin.x + width
        c.origin.y = self.origin.y + width
        return c

    def subimage(self, r):              # pix dim
	c = Canvas()
        c.initpointer(libgfx.gfx_cansubimg(self.can, int(r.orgx), int(r.orgy), int(r.sizex), int(r.sizey)))
        c.origin.x = self.origin.x - int(r.orgx)
        c.origin.y = self.origin.y - int(r.orgy)
        return c

    def zoom(self, zoomx, zoomy):
	c = Canvas()
  	c.initpointer(libgfx.gfx_canzoom(self.can, zoomx, zoomy))
        c.origin.x = c.origin.x * zoomx
        c.origin.y = c.origin.y * zoomy
        return c

    def clone(self):
	c = Canvas()
        c.initpointer(libgfx.gfx_canclone(self.can))
        c.origin = self.origin
        return c

    def new(self):
	c = Canvas()
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

def gccollect():
    libgfx.gfx_gccollect()

def canvasfromfile(filename):
    can = Canvas()
    ptr = libgfx.gfx_canfromfile(filename)
    can.initpointer(ptr)
    return can

def canvasnew(sizex, sizey):
    can = Canvas()
    can.initsize(sizex, sizey)
    return can

def canvasnalloc():
    return libgfx.gfx_cannalloc()

def dotest(name, value):
    print('TEST ' + name + ': ' + str(value))
    if not value:
        print('FATAL ERROR!')
	exit()


# test misc functions

print('')
print('Test misc funcs')
print('')
dotest('lerp', lerp(1.0,2.0,0.5) == 1.5)
dotest('fmod', fmod(-23,5) == 2)
dotest('limit', limit(-3.0,0.0,1.0) == 0)
dotest('delta', delta(12,10) == 2)

# test the Point functions

print('')
print('Test Point')
print('')
p = Point(1,2)
print(p)
dotest('Point equal', p.equal(Point(1,2)))
dotest('Point clone', p.equal(p.clone()))
dotest('Point scale', p.scale(3).equal(Point(3,6)))
dotest('Point round', Point(1.1,2.1).round().equal(Point(1,2)))
dotest('Point translate', p.translate(4,4).equal(Point(5,6)))
print p.rotate(90)
dotest('Point rotate', p.rotate(90).equal(Point(-2,1)))
dotest('Point distance', p.distance(Point(2,2)) == 1.0)
dotest('pointlerp', pointlerp(Point(0,0), Point(2,0), 0.5).equal(Point(1,0)))
dotest('size', size(1,2).equal(Point(1,2)))

# test the Rect functions

print('')
print('Test Rect')
print('')
r1 = Rect(0,0,100,100)
r2 = Rect(50,50,100,100)
print(r1)
dotest('Rect equal', r1.equal(Rect(0,0,100,100)))
dotest('Rect clone', r1.equal(r1.clone()))
dotest('Rect area', r1.area() == 10000)
dotest('Rect diameter', delta(r1.diameter(),141.42135623730950488000)<0.000001)
dotest('Rect aspect', r1.aspect() == 1.0)
dotest('Rect origin', r1.origin().equal(Point(0,0)))
dotest('Rect ll', r1.ll().equal(Point(0,0)))
dotest('Rect lr', r1.lr().equal(Point(100,0)))
dotest('Rect ur', r1.ur().equal(Point(100,100)))
dotest('Rect ul', r1.ul().equal(Point(0,100)))
dotest('Rect midx', r1.midx() == 50)
dotest('Rect midy', r1.midy() == 50)
dotest('Rect minx', r1.minx() == 0)
dotest('Rect miny', r1.miny() == 0)
dotest('Rect maxx', r1.maxx() == 100)
dotest('Rect maxy', r1.maxy() == 100)
dotest('Rect center', r1.center().equal(Point(50,50)))
dotest('Rect atzero', r2.atzero().equal(r1))
dotest('Rect inset', r1.inset(1,1).equal(Rect(1,1,98,98)))
dotest('Rect expand', r1.expand(1,1).equal(Rect(-1,-1,102,102)))
dotest('Rect isnull', rectnull().isnull())
dotest('Rect translate', r1.translate(Point(1,1)).equal(Rect(1,1,100,100)))
dotest('Rect scale', r1.scale(Point(0,0), 0.5).equal(Rect(0,0,50,50)))
dotest('Rect round', Rect(0.1,0.1,50,50).round().equal(Rect(0,0,50,50)))
dotest('Rect size', rectsize(20,20).equal(Rect(0,0,20,20)))
dotest('Rect union', rectunion(r1,r2).equal(Rect(0,0,150,150)))
dotest('Rect intersect', rectintersect(r1,r2).equal(Rect(50,50,50,50)))

# test a few of the Canvas functions

print('')
print('Test Canvas')
print('')

c1 = canvasnew(256, 256)
c1.clear(255, 0, 0, 255)
print(c1)
c1.setreadonly(True)
c2 = c1.new()
c2.clear(0, 255, 0, 255)
c1.blend(c2, 255, 128, 128, 128)
c1.mult(c2)
print(str(c1.getpix(10,10)))
c1 = None
c2 = None

# test image processing with C

print('')
print('N CANVASES ALLOCATED: ' + str(canvasnalloc()))

def testcanvases():
    # read in an image
    c = canvasfromfile('smallpic.tga')
    print('smallpic: ' + str(c))

    # get a sub image
    d = c.subimage(Rect(150,150,200,200))
    d.tofile('small.tga')

    # zoom the sub image by 1.3x and saturate it
    z = d.zoom(1.3,1.3)
    z.saturate(3.0)
    z.tofile('saturate.tga')

    # set a pixel
    c.putpix(20,20,45)

    # shift the sub image iand write it out
    sh = d.shift(20,20)
    sh.tofile('shift.tga')

    # add a frame and write it out
    sh = sh.frame(0.5, 0.5, 0.5, 1.0, 20)
    sh.tofile('frame.tga')

    # clone it and write it out
    c = sh.clone()
    c.scalergba(1.0, 0.0, 0.0, 1.0)
    c.tofile('red.tga')

for i in range(10):	# make this 50000, everything ok
    print('')
    print('start test canvases Pass: ' + str(i))
    testcanvases()

    # comment this in to make garbage collection happen on demand
    #gccollect()		 

    print('')
    print('In Loop')
    print('N CANVASES STILL ALLOCATED: ' + str(canvasnalloc()))

print('')
print('At end')
print('N CANVASES STILL ALLOCATED: ' + str(canvasnalloc()))
print('')

print('Before final garbage collection')
gccollect()		 
print('After garbage collection')
print('N CANVASES STILL ALLOCATED: ' + str(canvasnalloc()))
print('')
