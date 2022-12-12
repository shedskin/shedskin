
argv = ['','testdata/uuf250-010.cnf']             # [list(str)]

def ffile(name):                          # name: [str]
    return [1]                           # [list(int)]

x = argv[0]                              # [str]
cnf = [y for y in ffile(x)]               # [list(int)]

