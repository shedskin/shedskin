# slightly modified from
# https://stackoverflow.com/questions/2598437/how-to-implement-a-binary-tree

class Node:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value

class Tree:
    def __init__(self):
        self.root = None

    def get_root(self):
        return self.root

    def add(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self._add(value, self.root)

    def _add(self, value, node):
        if value < node.value:
            if node.left is not None:
                self._add(value, node.left)
            else:
                node.left = Node(value)
        else:
            if node.right is not None:
                self._add(value, node.right)
            else:
                node.right = Node(value)

    def find(self, value):
        if self.root is not None:
            return self._find(value, self.root)
        else:
            return None

    def _find(self, value, node):
        if value == node.value:
            return node
        elif (value < node.value and node.left is not None):
            return self._find(value, node.left)
        elif (value > node.value and node.right is not None):
            return self._find(value, node.right)

    def delete(self):
        self.__del__()

    def __del__(self):
        # garbage collector will do this for us. 
        self.root = None        

    def print(self):
        if self.root is not None:
            self._print(self.root)

    def _print(self, node):
        if node is not None:
            self._print(node.left)
            print(str(node.value) + ' ')
            self._print(node.right)


def test_tree():
    tree = Tree()
    tree.add(3)
    tree.add(4)
    tree.add(0)
    tree.add(8)
    tree.add(2)
    # tree.print()
    # print(tree.find(3).value)
    # print(tree.find(10))
    assert tree.find(3).value
    assert not tree.find(10)
    tree.delete()
    # tree.print()
    assert not tree.root

def test_all():
    test_tree()


if __name__ == "__main__":
    test_all()
