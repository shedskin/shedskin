
def flatsie(iter):                       # iter: [pyiter(tuple2(A, B))]
    return [(bh,ah) for (ah,bh) in iter] # [tuple2(int, float)]

print flatsie([(1,2.1),(2,4.1)])         # [list(tuple2(float, int))]
print flatsie({(2,3.1): [1,2,3]})        # [list(tuple2(float, int))]
print flatsie({(1,4.1): None})           # [list(tuple2(float, int))]
print flatsie(((7.7,1),))                # [list(tuple2(int, float))]

