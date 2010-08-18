
class renderobject:
        def intersect(self,l):
                return "none", (l, l)

class plane(renderobject):
        def intersect(self,l):
                return "one", (l, l)

class sphere(renderobject):
    def intersect(self,l):
        return "none", (l, l)

p = plane()
s = sphere()

print p.intersect(1)
print s.intersect(2)

meuk = [p, s]
for obj in meuk:
    print obj.intersect(1)

