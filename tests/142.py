
class renderobject: pass
class plane(renderobject): pass
class sphere(renderobject): pass

class light:
    def hoei(self): print 'hoei!'

class parallellight(light): pass
class pointlight(light): pass

objects = []
objects.append(plane())
objects.append(sphere())

lights = []
lights.append(parallellight())
lights.append(pointlight())

lights[0].hoei()

