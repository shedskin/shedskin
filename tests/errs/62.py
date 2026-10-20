class Point:
    def __init__(self, x):
        self.x = x

match Point(0):
    case Point(x=0):
        pass
#*ERROR* 62.py:6: class patterns are not supported
