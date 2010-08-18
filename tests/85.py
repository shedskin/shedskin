
def row_perm_rec():
    hoppa_row = 'impossible'         # [str]
    hoppa_row = []                   # [list(str)]

    a = hoppa_row                    # [pyobj]
    hoppa_row.extend(a)              # []
    hoppa_row.append('u')            # []

    return hoppa_row                 # [pyobj]

a = [[7]]                                # [list(list(int))]
s = row_perm_rec()                       # [pyobj]
puzzleboard = [['']]                     # [list(list(str))]
puzzleboard[1][1] = s[1]                 # [str]

