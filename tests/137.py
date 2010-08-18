
class node:
    def __init__(self):
        self.input = [8]

def incoming(node):
    return [link for link in node.input]

print incoming(node())

