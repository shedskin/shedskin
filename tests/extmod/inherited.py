# inherited instance attributes whose type comes only from the base class
# (1023-C4): the subclass getset/__setstate__ must use the field's type


class Node:
    def __init__(self):
        self.other = None
        self.label = 'node'


class Leaf(Node):  # inherits both attributes, assigns neither
    pass


class Twig(Leaf):  # two levels down
    def __init__(self):
        Node.__init__(self)
        self.depth = 2


def make():
    n = Node()
    n.other = Twig()
    return n


if __name__ == '__main__':
    # 'other' is only ever assigned through a Node, so for Leaf and Twig
    # (whose own Variables see just the None from __init__) the type is known
    # only in the base class context
    n = Node()
    n.other = Leaf()
    print(n.label, Twig().depth, make().other.depth)
