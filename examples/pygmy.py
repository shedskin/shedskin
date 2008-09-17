# (c) Dave Griffiths
# --- http://www.pawfal.org/index.php?page=PyGmy
#
# ray tracer :-) (see output test.ppm)

from math import sin, cos, sqrt
import random, sys

def sq(a):
    return a*a

def conv_value(col):
    if col >= 1.0:
        return "255"
    elif col <= 0.0:
        return "0"
    else:
        return str(int(col*255.0))

class Shaderinfo:
    pass

class vec:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self,other):
        return vec(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self,other):
        return vec(self.x-other.x, self.y-other.y, self.z-other.z)

    def __mul__(self,amount):
        return vec(self.x*amount, self.y*amount, self.z*amount)

    def __div__(self,amount):
        return vec(self.x/amount, self.y/amount, self.z/amount)

    def __neg__(self):
        return vec(-self.x, -self.y, -self.z)

    def dot(self,other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def dist(self,other):
        return sqrt((other.x-self.x)*(other.x-self.x)+
                    (other.y-self.y)*(other.y-self.y)+
                    (other.z-self.z)*(other.z-self.z))

    def sq(self):
        return sq(self.x) + sq(self.y) + sq(self.z)

    def mag(self):
        return self.dist(vec(0.0, 0.0, 0.0))

    def norm(self):
        mag = self.mag()
        if mag != 0:
            self.x = self.x/mag
            self.y = self.y/mag
            self.z = self.z/mag

    def reflect(self,normal):
        vdn = self.dot(normal)*2
        return self - normal*vdn

class line:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def vec(self):
        return self.end - self.start

class renderobject:
    def __init__(self, shader):
        self.shader = shader

class plane(renderobject):
    def __init__(self, plane, dist, shader):
        renderobject.__init__(self, shader)
        self.plane = plane
        self.dist = dist

    def intersect(self,l):
        vd = self.plane.dot(l.vec())
        if vd == 0:
            return "none",(vec(0.0, 0.0, 0.0),vec(0.0, 0.0, 0.0))
        v0 = -(self.plane.dot(l.start)+self.dist)
        t = v0/vd
        if t<0 or t>1:
            return "none",(vec(0.0, 0.0, 0.0),vec(0.0, 0.0, 0.0))
        return "one", (l.start+(l.vec()*t), self.plane)


class sphere(renderobject):
    def __init__(self, pos, radius, shader):
        renderobject.__init__(self, shader)
        self.pos = pos
        self.radius = radius

    def intersect(self,l):
        lvec = l.vec()
        a = sq(lvec.x) + sq(lvec.y) + sq(lvec.z)

        b = 2*(lvec.x*(l.start.x-self.pos.x)+                lvec.y*(l.start.y-self.pos.y)+                lvec.z*(l.start.z-self.pos.z))

        c = self.pos.sq()+l.start.sq() -             2*(self.pos.x*l.start.x+self.pos.y*l.start.y+self.pos.z*l.start.z)-sq(self.radius)

        i = b*b - 4*a*c

        intersectiontype = "none"
        pos = vec(0.0, 0.0, 0.0)
        norm = vec(0.0, 0.0, 0.0)
        t = 0.0

        if i > 0:
            if i == 0:
                intersectiontype="one"
                t = -b/(2*a)
            else:
                intersectiontype="two"
                t = (-b - sqrt( b*b - 4*a*c )) / (2*a)

            if t>0 and t<1:
                pos = l.start + lvec*t
                norm = pos - self.pos
                norm.norm()
            else:
                intersectiontype="none"

        return intersectiontype, (pos, norm)

class light:
    def checkshadow(self, obj, objects,l):
        for ob in objects:
            if ob is not obj:
                intersects,(pos, norm) = ob.intersect(l)
                if intersects is not "none":
                    return 1
        return 0

class parallellight(light):
    def __init__(self, direction, col):
        direction.norm()
        self.direction = direction
        self.col=  col

    def inshadow(self, obj, objects, pos):
        l = line(pos, pos+self.direction*1000.0)
        return self.checkshadow(obj, objects,l)

    def light(self, shaderinfo):
        if self.inshadow(shaderinfo.thisobj, shaderinfo.objects, shaderinfo.position):
            return vec(0.0, 0.0, 0.0)
        return self.col*self.direction.dot(shaderinfo.normal)

class pointlight(light):
    def __init__(self, position, col):
        self.position = position
        self.col = col

    def inshadow(self, obj, objects, pos):
        l = line(pos, self.position)
        return self.checkshadow(obj, objects,l)

    def light(self, shaderinfo):
        if self.inshadow(shaderinfo.thisobj, shaderinfo.objects, shaderinfo.position):
            return vec(0.0, 0.0, 0.0)
        direction = shaderinfo.position - self.position
        direction.norm()
        direction = -direction
        return self.col*direction.dot(shaderinfo.normal)

class shader:
    def getreflected(self, shaderinfo):
        depth = shaderinfo.depth
        col = vec(0.0, 0.0, 0.0)
        if depth > 0:
            lray = line(shaderinfo.ray.start, shaderinfo.ray.end) #copy.copy(shaderinfo.ray)
            ray = lray.vec()
            normal = vec(shaderinfo.normal.x, shaderinfo.normal.y, shaderinfo.normal.z) #copy.copy(shaderinfo.normal)

            ray = ray.reflect(normal)
            reflected = line(shaderinfo.position,shaderinfo.position+ray)
            obj = shaderinfo.thisobj
            objects = shaderinfo.objects

            newshaderinfo = Shaderinfo() #copy.copy(shaderinfo) # XXX
            newshaderinfo.thisobj = shaderinfo.thisobj
            newshaderinfo.objects = shaderinfo.objects
            newshaderinfo.lights = shaderinfo.lights
            newshaderinfo.position = shaderinfo.position
            newshaderinfo.normal = shaderinfo.normal

            newshaderinfo.ray = reflected
            newshaderinfo.depth = depth - 1

            # todo - depth test
            for ob in objects:
                if ob is not obj:
                    intersects,(position,normal) = ob.intersect(reflected)
                    if intersects is not "none":
                        newshaderinfo.thisobj = ob
                        newshaderinfo.position = position
                        newshaderinfo.normal = normal
                        col = col + ob.shader.shade(newshaderinfo)
        return col

    def isoccluded(self, ray, shaderinfo):
        dist = ray.mag()
        test = line(shaderinfo.position, shaderinfo.position+ray)
        obj = shaderinfo.thisobj
        objects = shaderinfo.objects
        # todo - depth test
        for ob in objects:
            if ob is not obj:
                intersects,(position,normal) = ob.intersect(test)
                if intersects is not "none":
                    return 1
        return 0

    def doocclusion(self, samples, shaderinfo):
        # not really very scientific, or good in any way...
        oc = 0.0
        for i in xrange(samples):
            ray = vec(float(random.randrange(-100,100)),float(random.randrange(-100,100)),float(random.randrange(-100,100)))
            ray.norm()
            ray = ray * 2.5
            if self.isoccluded(ray, shaderinfo):
                oc = oc + 1
        oc = oc / float(samples)
        return 1-oc

    def shade(self,shaderinfo):
        col = vec(0.0, 0.0, 0.0)
        for lite in shaderinfo.lights:
            col = col + lite.light(shaderinfo)
        return col

class world:
    def __init__(self,width,height):
        self.lights = []
        self.objects = []
        self.cameratype = "persp"
        self.width = width
        self.height = height
        self.backplane = 2000.0
        self.imageplane = 5.0
        self.aspect = self.width/float(self.height)

    def render(self, filename):
        out_file = file(filename, 'w')
        # PPM header
        print >>out_file, "P3"
        print >>out_file, self.width, self.height
        print >>out_file, "256"
        total = self.width * self.height
        count = 0

        for sy in xrange(self.height):
            pixel_line = []
            for sx in xrange(self.width):
                x = 2 * (0.5-sx/float(self.width)) * self.aspect
                y = 2 * (0.5-sy/float(self.height))
                if self.cameratype=="ortho":
                    ray = line(vec(x, y, 0.0),vec(x, y, self.backplane))
                else:
                    ray = line(vec(0.0, 0.0, 0.0),vec(x, y, self.imageplane))
                    ray.end=ray.end*self.backplane

                col = vec(0.0, 0.0, 0.0)
                depth = self.backplane
                shaderinfo = Shaderinfo() #{"ray":ray,"lights":self.lights,"objects":self.objects,"depth":2}
                shaderinfo.ray = ray
                shaderinfo.lights = self.lights
                shaderinfo.objects = self.objects
                shaderinfo.depth = 2

                for obj in self.objects:
                    intersects,(position,normal) = obj.intersect(ray)
                    if intersects is not "none":
                        if position.z<depth and position.z>0:
                            depth = position.z
                            shaderinfo.thisobj = obj
                            shaderinfo.position = position
                            shaderinfo.normal = normal
                            col = obj.shader.shade(shaderinfo)

                pixel_line.append( conv_value(col.x) )
                pixel_line.append( conv_value(col.y) )
                pixel_line.append( conv_value(col.z) )
                count = count + 1

            print >>out_file, " ".join(pixel_line)
            percentstr = str(int((count/float(total))*100))+"%"
            print "" + percentstr
        out_file.close()


class everythingshader(shader):
    def shade(self,shaderinfo):
        col = shader.shade(self,shaderinfo)
        ref = self.getreflected(shaderinfo)
        col = col*0.5+ref*0.5
        return col*self.doocclusion(10,shaderinfo)


class spotshader(shader):
    def shade(self,shaderinfo):
        col = shader.shade(self, shaderinfo)
        position = shaderinfo.position
        jitter = sin(position.x) + cos(position.z)
        if jitter > 0.5:
            col = col / 2
        ref = self.getreflected(shaderinfo)
        return ref*0.5 + col*0.5*self.doocclusion(10,shaderinfo)

# Main
# Give sixe x and y of the image
if len(sys.argv) == 3:
    nx, ny = int(sys.argv[1]), int(sys.argv[2])
else:
    nx, ny = 160, 120
w = world(nx, ny)
numballs = 10.0
offset = vec(0.0,-5.0,55.0)
rad = 12.0
radperball = (2 * 3.141592) / numballs

for i in xrange(int(numballs)):
    x = sin(0.3+radperball*float(i))*rad
    y = cos(0.3+radperball*float(i))*rad
    w.objects.append(sphere(vec(x,0.0,y)+offset,2.0,everythingshader()))

w.objects.append(sphere(vec(3.0,3.0,0.0)+offset,5.0,everythingshader()))
w.objects.append(plane(vec(0.0,1.0,0.0),7.0, spotshader()))
w.lights.append(parallellight(vec(1.0,1.0,-1.0), vec(0.3,0.9,0.1)))
w.lights.append(pointlight(vec(5.0,100.0,-5.0), vec(0.5,0.5,1.0)))

w.render('test.ppm')

