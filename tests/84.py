
def solve_rec():
    la_mods = [1]                        # [list(int)]
    for var in la_mods:                  # [list(int)]
        lookahead_variable(var, la_mods)      # []
        propagate(var, la_mods)          # []

def propagate(lit, mods, bla=0):         # lit: [int], mods: [list(int)], bla: [int]
    pass

def lookahead_variable(var, mods):       # var: [int], mods: [list(int)]
    propagate(10, mods)                  # []

solve_rec()                              # []

