
u = [' p  o', 'c o ']                    # [list(str)]
cnf = [x.strip().split() for x in u if not x.startswith('x')] # [list(list(str))]
cnf2 = [[3] for x in u]                  # [list(list(int))]

