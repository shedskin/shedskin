

def hoppa(node, a, b):                   # node: [int], a: [int, float], b: [int, float]r
    print a, b                           # [int, float], [int, float]
    return b                             # [int, float]

def visit(node, *args):                  # node: [int], args: [tuple(float,int)]
    print node, args                     # [int], [tuple(float,int)]

    return hoppa(node, *args)            # [int, float]


visit(1,2,2)                           # [int, float]
visit(2,2,3,4,4,5)                       # [int, float]

