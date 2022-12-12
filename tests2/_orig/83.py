
def propagate(lit):                      # lit: [int]
    global lit_mask # XXX
    lit_mask[lit] |= 1                   # [int]

def lookahead():                     # mods: [list(int)]
    global lit_mask
    lit_mask = [1]

lookahead()
propagate(0)

