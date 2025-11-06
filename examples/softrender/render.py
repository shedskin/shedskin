from bitmap import Bitmap
from camera import Camera
from matrix4 import Matrix4
from mesh import Mesh
from quaternion import Quaternion
from rendercontext import RenderContext
from transform import Transform
from vector4 import Vector4


if __name__ == '__main__':
    mesh = Mesh("buddha2.obj")
    texture = Bitmap("buddha2.jpg")
    transform = Transform(Vector4(0.0, 0.3, 3.0))
    transform = transform.rotate(Quaternion.from_axis_angle(Vector4(1, 0, 0), 80))
    target = RenderContext(0, 0)
    target.clear(0)
    target.clear_zbuffer()
    camera = Camera(Matrix4().init_perspective(1.0, 1.0, 0.1, 1000.0))
    lightDir = Vector4(0, 0, -1)
    mesh.draw(target, camera.get_view_projection(), transform.get_transformation(), texture, lightDir)
