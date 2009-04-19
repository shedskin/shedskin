# (c) Alex P-B (chozabu@gmail.com) 
# license: http://creativecommons.org/licenses/by-nc-sa/2.5/

from math import sin, cos, pi, hypot
from random import random

def setup(w, h):
    global sw, sh
    sw, sh = w, h
   
class Point:
        def __init__(self):
                self.x=0
                self.y=0
                self.rad=3
                self.ox=self.x
                self.oy=self.y
                self.locked = 0

	def basicphys(self):
		self.x,self.ox = self.x+(self.x-self.ox)*0.98,self.x
		self.y,self.oy = self.y+(self.y-self.oy)*0.98,self.y
		self.y+=0.3
	
	def basiclimits(self):
		if self.y > sh:
			self.y = sh
			self.x = self.ox
		if self.x > sw:
			self.x = sw
			self.y = self.oy
		if self.x < 0:
			self.x = 0
			self.y = self.oy

def twopoint(p1,p2,destdist = 15,mult = 0.5):
	xd = p1.x-p2.x
	yd = p1.y-p2.y
	td = hypot(xd, yd)#+0.0000000001
	rads = p1.rad+p2.rad
	diffd = (destdist-td)*mult
	xd/=td
	yd/=td
	xd*=diffd
	yd*=diffd
	p1.x+=xd
	p1.y+=yd
	p2.x-=xd
	p2.y-=yd
	

class Link:
        def __init__(self):
                self.p1=None
                self.p2=None
                self.dist = 15
                self.strength = 0.5
                self.drawme = 1

	def applyme(self):
		twopoint(self.p1,self.p2,self.dist,self.strength)

points = []
links = []
wheels = []

drawlinks = 1

def addlinki(p1,p2, dist=30,strength=0.5):
	global drawlinks
	l= Link()
	l.p1 = points[p1]
	l.p2 = points[p2]
	l.dist = dist
	l.strength = strength
	l.drawme = drawlinks
	links.append(l)
	return l

def addlinkrr(p1,p2,strength=0.5):
	global drawlinks
	l= Link()
	l.p1 = p1
	l.p2 = p2
	xd = p1.x-p2.x
	yd = p1.y-p2.y
	dist = hypot(xd,yd)
	l.dist = dist
	l.strength = strength
	l.drawme = drawlinks
	links.append(l)
	return l

def addpoint(x,y):
	p= Point()
	p.x = x
	p.y = y
	p.ox = p.x
	p.oy = p.y
	points.append(p)
	return p 
	
class Wheel:
	def __init__(self,x,y,numspokes = 8, scale = 34):
		global drawlinks

		lastspoke = numspokes-1
		halfspoke = numspokes/2
		self.spokes = []
		drawlinks = 1
		self.mainpoint = addpoint(x,y)
		step = pi/numspokes*2
		angle = 0
		for i in range(numspokes):
			angle+=step
			self.spokes.append(addpoint(cos(angle)*scale+x,sin(angle)*scale+y))
		for i in range(0,numspokes):
			nextspoke = i+1
			if nextspoke > lastspoke:
				nextspoke = 0
			addlinkrr(self.spokes[i],self.mainpoint)
		
		for i in range(0,lastspoke):
			for r in range(i+1,lastspoke+1):
				addlinkrr(self.spokes[i],self.spokes[r])
		
		addlinkrr(self.spokes[0+halfspoke/2],self.spokes[halfspoke+halfspoke/2])
		addlinkrr(self.spokes[0],self.spokes[halfspoke])

	def addpower(self,power=1.0):
		mp = self.mainpoint
		for p in self.spokes:
			if p.y > mp.y:
				p.x-=power
			else:
				p.x+=power
			if p.x > mp.x:
				p.y+=power
			else:
				p.y-=power

for ir in range(18*2):
	addpoint(ir*15,10+cos(ir)*5)
for ir in range(11,18*2-1):
	addlinki(ir,ir+1)
drawlinks = 1
#neck
addlinki(0,1)
points[0].rad = 14

#body
addlinki(1,2,60)

#leg1
addlinki(2,3)
addlinki(3,4)

#leg2
addlinki(2,5)
addlinki(5,6)

#arm1
addlinki(1,7)
addlinki(7,8)

#arm2
addlinki(1,9)
addlinki(9,10)

drawlinks = 0
addlinki(0,2,90)

addlinki(7,9,70)
addlinki(3,5,40)

wheels.append(Wheel(300,300))

if __name__ == '__main__':
    setup(1,1)
    p, l, w = points[0], links[0], wheels[0] 
    p.basiclimits()
    p.basicphys()
    l.applyme()
    w.addpower()
