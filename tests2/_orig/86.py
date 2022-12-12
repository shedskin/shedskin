
def row_perm_rec():
    hoppa_row = []                       # [list(str)]

    new_row = ['']                   # [list(str)]

    a = hoppa_row                        # [list(str)]

    new_row.extend(a)                # []
    hoppa_row = new_row[:]
    hoppa_row.append('u')                # []

    return hoppa_row

numbers = [1]                            # [list(int)]
numberscopy = numbers[:]                 # [list(int)]

s = row_perm_rec()                       # []

