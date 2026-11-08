# class variables, read and written from CPython (1016-D9); see README.md

class K:
    count = 3

    def __init__(self):
        self.x = K.count


class Base:
    count = 0
    label = 'base'

    def __init__(self):
        Base.count += 1

    def get(self):
        return Base.count, Base.label


class Sub(Base):
    scale = 1.5

    def __init__(self):
        Base.__init__(self)

    def scaled(self):
        return Sub.scale * 2


class Plain:
    def __init__(self):
        self.y = 1


if __name__ == '__main__':
    print(K().x)
    print(Base().get(), Sub().scaled(), Plain().y)
