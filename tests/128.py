
def main():
   ws = open("testdata/hoppa","r").read().split()
   d = {}
   for i, w in enumerate(ws):
       s = "".join(sorted(list(w.lower())))
       d.setdefault(s, []).append(i)
   for l in d.values():
       if len(l) > 1:
           print [ws[i] for i in l]

main()

def subsets(sequence):
   result = [[]] * (2**len(sequence))
   for i,e in enumerate(sequence):
       i2, el = 2**i, [e]
       for j in xrange(i2):
           result[j+i2] = result[j] + el
   return result

print subsets(range(4))


