
n = 8                                    # [int]
count = 0                                # [int]

f = 1                                    # [int]
s = 1                                    # [int]
nums = []                                # [list(tuple2(int, int))]
while n > 0:                             # [int]
   count += 1                            # [int]
   nums.append((count, f))               # []
   temp = f                              # [int]
   f = s                                 # [int]
   s = temp + s                          # [int]
   n -= 1                                # [int]
print nums                               # [list(tuple2(int, int))]

