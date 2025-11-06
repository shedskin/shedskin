from matrix4 import Matrix4
from transform import Transform

class Camera:
    def __init__(self, projection):
        self.projection = projection
        self.transform = Transform()

    def get_view_projection(self):
        camera_rotation = self.transform.rot.conjugate().to_rotation_matrix()
        camera_pos = self.transform.pos.mul(-1)
        camera_translation = Matrix4().init_translation(camera_pos.x, camera_pos.y, camera_pos.z)

        return self.projection.mul(camera_rotation.mul(camera_translation))
