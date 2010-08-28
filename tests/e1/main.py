#Matrix4
import Matrix4
v = Matrix4.Vector4(1,2,3,4)
m = Matrix4.Matrix4([v,v,v,v])
w = Matrix4.hoppa(v)
print w.x, w.y, w.z, w.w
