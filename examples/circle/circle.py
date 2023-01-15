import sys
print(sys.version)

import math

def setup(width, height):
    global SCREEN_WIDTH_2, SCREEN_HEIGHT_2

    SCREEN_WIDTH_2 = width // 2
    SCREEN_HEIGHT_2 = height // 2

def sqr_distance(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    return dx*dx + dy*dy

class Circle(object):
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    @property
    def offset(self):
        return sqr_distance(self.x, self.y, SCREEN_WIDTH_2, SCREEN_HEIGHT_2)

    def contains(self, x, y):
        return sqr_distance(self.x, self.y, x, y) <= (self.radius * self.radius)

    def intersects(self, other):
        d = sqr_distance(self.x, self.y, other.x, other.y)
        radii = self.radius + other.radius
        return d < (radii * radii)

def pack(circles, damping=0.1, padding=2, exclude=None):
    circles.sort(key=lambda c: c.offset)

    len_circles = len(circles)
    # repulsive force: move away from intersecting circles.
    for i in range(len_circles):
        circle1 = circles[i]
        circle1_x = circle1.x
        circle1_y = circle1.y
        circle1_radius_padded = circle1.radius + padding
        for j in range(i+1, len_circles):
            circle2 = circles[j]

            #inlined for speed
            #d_d = sqr_distance(circle1_x, circle1_y, circle2.x, circle2.y)
            dx = circle2.x - circle1_x
            dy = circle2.y - circle1_y
            d_d = dx*dx + dy*dy

            r = circle1_radius_padded + circle2.radius
            if d_d < (r * r - 0.01):
                dx = circle2.x - circle1_x
                dy = circle2.y - circle1_y
                d = math.sqrt(d_d) # slow
                aux = (r - d) * 0.5
                vx = (dx / d) * aux
                vy = (dy / d) * aux

                if circle1 is not exclude:
                    circle1.x -= vx
                    circle1.y -= vy
                if circle2 is not exclude:
                    circle2.x += vx
                    circle2.y += vy

    # attractive force: all circles move to center
    for circle in circles:
        if circle is not exclude:
            vx = (circle.x - SCREEN_WIDTH_2) * damping
            vy = (circle.y - SCREEN_HEIGHT_2) * damping
            circle.x -= vx
            circle.y -= vy

if __name__ == '__main__':
    setup(1,1)
    c = Circle(1.0, 1.0, 1.0, (1,))
    c.contains(1.0, 1.0)
    c.intersects(c)
    pack([c], exclude=c)

