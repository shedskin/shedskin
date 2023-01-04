# slightly modified from
# https://stackoverflow.com/questions/2598437/how-to-implement-a-binary-tree

from collections import deque

class BinaryTreeNode:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right

    def __repr__(self):
        return "%s l: (%s) r: (%s)" % (self.key, self.left, self.right)

    def __eq__(self, other):
        if self.key == other.key and \
            self.right == other.right and \
                self.left == other.left:
            return True
        else:
            return False

class BinaryTree:
    def __init__(self, root_key=None):
        # maps from BinaryTreeNode key to BinaryTreeNode instance.
        # Thus, BinaryTreeNode keys must be unique.
        self.nodes = {}
        if root_key is not None:
            # create a root BinaryTreeNode
            self.root = BinaryTreeNode(root_key)
            self.nodes[root_key] = self.root

    def add(self, key, left_key=None, right_key=None):
        if key not in self.nodes:
            # BinaryTreeNode with given key does not exist, create it
            self.nodes[key] = BinaryTreeNode(key)
        # invariant: self.nodes[key] exists

        # handle left child
        if left_key is None:
            self.nodes[key].left = None
        else:
            if left_key not in self.nodes:
                self.nodes[left_key] = BinaryTreeNode(left_key)
            # invariant: self.nodes[left_key] exists
            self.nodes[key].left = self.nodes[left_key]

        # handle right child
        if right_key == None:
            self.nodes[key].right = None
        else:
            if right_key not in self.nodes:
                self.nodes[right_key] = BinaryTreeNode(right_key)
            # invariant: self.nodes[right_key] exists
            self.nodes[key].right = self.nodes[right_key]

    def remove(self, key):
        if key not in self.nodes:
            raise ValueError('%s not in tree' % key)
        # remove key from the list of nodes
        del self.nodes[key]
        # if node removed is left/right child, update parent node
        for k in self.nodes:
            if self.nodes[k].left and self.nodes[k].left.key == key:
                self.nodes[k].left = None
            if self.nodes[k].right and self.nodes[k].right.key == key:
                self.nodes[k].right = None
        return True

    def _height(self, node):
        if node is None:
            return 0
        else:
            return 1 + max(self._height(node.left), self._height(node.right))

    def height(self):
        return self._height(self.root)

    def size(self):
        return len(self.nodes)

    def __repr__(self):
        return str(self.traverse_inorder(self.root))

    def bfs(self, node):
        if not node or node not in self.nodes:
            return
        reachable = []    
        q = deque()
        # add starting node to queue
        q.append(node)
        while len(q):
            visit = q.popleft()
            # add currently visited BinaryTreeNode to list
            reachable.append(visit)
            # add left/right children as needed
            if visit.left:
                q.append(visit.left)
            if visit.right:
                q.append(visit.right)
        return reachable

    # visit left child, root, then right child
    def traverse_inorder(self, node, reachable=None):
        if not node or node.key not in self.nodes:
            return
        if reachable is None:
            reachable = []
        self.traverse_inorder(node.left, reachable)
        reachable.append(node.key)
        self.traverse_inorder(node.right, reachable)
        return reachable

    # visit left and right children, then root
    # root of tree is always last to be visited
    def traverse_postorder(self, node, reachable=None):
        if not node or node.key not in self.nodes:
            return
        if reachable is None:
            reachable = []
        self.traverse_postorder(node.left, reachable)
        self.traverse_postorder(node.right, reachable)
        reachable.append(node.key)
        return reachable

    # visit root, left, then right children
    # root is always visited first
    def traverse_preorder(self, node, reachable=None):
        if not node or node.key not in self.nodes:
            return
        if reachable is None:
            reachable = []
        reachable.append(node.key)
        self.traverse_preorder(node.left, reachable)
        self.traverse_preorder(node.right, reachable)
        return reachable


def test_tree():
    t = BinaryTree('root')
    t.add('root', left_key='a', right_key='b')
    t.add('a', left_key='c', right_key='d')
    t.add('b', left_key='e', right_key='f')
    assert t.height() == 3
    assert t.size() == 7

def test_all():
    test_tree()


if __name__ == "__main__":
    test_all()
