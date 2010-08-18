
class renderobject:
        def __init__(self, shader):
                self.shader=shader

class plane(renderobject):
        def __init__(self,plane,dist,shader):
                renderobject.__init__(self,shader)
                self.plane=plane
                self.dist=dist

class sphere(renderobject):
        def __init__(self, pos, radius, shader):
                renderobject.__init__(self,shader)
                self.pos=pos
                self.radius=radius

class world:
    def __init__(self):
        self.objects = []

w = world()
w.objects.append(plane(6,7,8))
w.objects.append(sphere(6,7,8))

