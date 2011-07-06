
s = 10000*'x'
sum = 0
for x in range(100000):
   sum += len(s[:x])
print sum
