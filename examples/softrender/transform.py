from matrix4 import Matrix4
from quaternion import Quaternion
from vector4 import Vector4

class Transform:
    def __init__(self, pos=None, rot=None, scale=None):
        if pos is None:
            pos = Vector4(0.0, 0.0, 0.0, 0.0)
        self.pos = pos

        if rot is None:
            rot = Quaternion(0.0, 0.0, 0.0, 1.0)
        self.rot = rot

        if scale is None:
            scale = Vector4(1.0, 1.0, 1.0, 1.0)
        self.scale = scale

    def rotate(self, rotation):
        return Transform(self.pos, rotation.mul(self.rot).normalized(), self.scale)

    def get_transformation(self):
        translationMatrix = Matrix4().init_translation(self.pos.x , self.pos.y, self.pos.z)
        rotationMatrix = self.rot.to_rotation_matrix()
        scaleMatrix = Matrix4().init_scale(self.scale.x, self.scale.y, self.scale.z)

        return translationMatrix.mul(rotationMatrix.mul(scaleMatrix))
