import array
import copy
arr = array.array('i', [3,2,1])
c1 = copy.copy(arr)
c1.append(4)
c2 = copy.deepcopy(arr)
c2.append(5)
print c1, c2, arr
