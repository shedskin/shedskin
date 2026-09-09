class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


numbers = [1, 2, 3]
labels = {'a': 1}
origin = Point(0, 0)


def use():
    return numbers[0] + origin.x + labels['a']


print(use())
