#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/


from .triangle import TOLERANCE
from .vector3f import Vector3f_seq, Vector3f_scalar, MAX

MAX_LEVELS = 44
MAX_ITEMS  =  8

class SpatialIndex(object):

    def __init__(self, vect, bound, items, level=0):
        if vect:
            for item in items:
                item.bound = item.get_bound()
            bound = vect.as_list() * 2
            for item in items:
                for j in range(6):
                    if (bound[j] > item.bound[j]) ^ (j > 2):
                        bound[j] = item.bound[j]
            size = max((Vector3f_seq(bound[3:6]) - Vector3f_seq(bound[0:3])).as_list())
            self.bound = bound[0:3] + (Vector3f_seq(bound[3:6]).clamped(Vector3f_seq(bound[0:3]) + Vector3f_scalar(size), MAX)).as_list()
        else:
            self.bound = bound
        self.is_branch = len(items) > MAX_ITEMS and level < MAX_LEVELS - 1
        if self.is_branch:
            q1 = 0
            self.vector = [None] * 8
            for s in range(8):
                sub_bound = []
                for j in range(6):
                    m = j % 3
                    if (((s >> m) & 1) != 0) ^ (j > 2):
                        sub_bound.append((self.bound[m] + self.bound[m + 3]) * 0.5)
                    else:
                        sub_bound.append(self.bound[j])
                sub_items = []
                for item in items:
                    if item.bound[3] >= sub_bound[0] and item.bound[0] < sub_bound[3] and \
                       item.bound[4] >= sub_bound[1] and item.bound[1] < sub_bound[4] and \
                       item.bound[5] >= sub_bound[2] and item.bound[2] < sub_bound[5]:
                           sub_items.append(item)
                q1 += 1 if len(sub_items) == len(items) else 0
                q2 = (sub_bound[3] - sub_bound[0]) < (TOLERANCE * 4.0)
                if len(sub_items) > 0:
                    self.vector[s] = SpatialIndex(None, sub_bound, sub_items, MAX_LEVELS if q1 > 1 or q2 else level + 1)
        else:
            self.items = items

    def get_intersection(self, ray_origin, ray_direction, last_hit, start=None):
        start = start if start else ray_origin
        hit_object = hit_position = None
        b0, b1, b2, b3, b4, b5 = self.bound
        if self.is_branch:
            sub_cell = 1 if start.x >= (b0+b3) * 0.5 else 0
            if start.y >= (b1+b4) * 0.5:
                sub_cell |= 2
            if start.z >= (b2+b5) * 0.5:
                sub_cell |= 4
            cell_position = start
            while True:
                if self.vector[sub_cell] != None:
                    hit_object, hit_position = self.vector[sub_cell].get_intersection(ray_origin, ray_direction, last_hit, cell_position)
                    if hit_object != None:
                        break
                step = 1.797e308
                axis = 0
                for i in range(3):
                    high = (sub_cell >> i) & 1
                    face = self.bound[i + high * 3] if (ray_direction[i] < 0.0) ^ (0 != high) else (self.bound[i] + self.bound[i + 3]) * 0.5
                    assert (isinstance((face - ray_origin[i]), float) and isinstance(ray_direction[i], float))
                    try:                        
                        distance = (face - ray_origin[i]) / ray_direction[i] ## truediv
                    except:
                        distance = float(1e30000)
                    if distance <= step:
                        step = distance
                        axis = i
                if (((sub_cell >> axis) & 1) == 1) ^ (ray_direction[axis] < 0.0):
                    break
                cell_position = ray_origin + ray_direction * step
                sub_cell = sub_cell ^ (1 << axis)
        else:
            nearest_distance = 1.797e308
            for item in self.items:
                if item != last_hit:
                    distance = item.get_intersection(ray_origin, ray_direction)
                    if 0.0 <= distance < nearest_distance:
                        hit = ray_origin + ray_direction * distance
                        if (b0 - hit.x <= TOLERANCE) and \
                           (hit.x - b3 <= TOLERANCE) and \
                           (b1 - hit.y <= TOLERANCE) and \
                           (hit.y - b4 <= TOLERANCE) and \
                           (b2 - hit.z <= TOLERANCE) and \
                           (hit.z - b5 <= TOLERANCE):
                               hit_object = item
                               hit_position = hit
                               nearest_distance = distance
        return hit_object, hit_position
