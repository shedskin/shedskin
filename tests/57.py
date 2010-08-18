
class bert:
    pass

class evert:
    pass

class node:                              # value: [bert(), evert()]*, next: [node(bert()), node(evert())]*
    pass

b = bert()                               # [bert]
e = evert()                              # [evert]

n = node()                               # [node(bert)]
n.next = n                               # [node(bert)]
n.value = b                              # [bert]

m = node()                               # [node(evert)]
m.next = m                               # [node(evert)]
m.value = e                              # [evert]

