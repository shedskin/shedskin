
import heapq

heap = [21]
print heap

heapq.heappush(heap, 42)
print heap

heapq.heappush(heap, 12)
print heap

print heapq.heappop(heap)
print heap
print heapq.heappushpop(heap, 63)
print heap
print heapq.heappop(heap)
print heap
print heapq.heappop(heap)
print heap

heapq.heappush(heap, 12)
print heap

heapq.heappush(heap, 52)
print heap

heapq.heappush(heap, 112)
print heap

heapq.heappush(heap, 1)
print heap

heapq.heappush(heap, 12)
print heap

print heapq.heappop(heap)
print heap
print heapq.heappushpop(heap, 63)
print heap
print heapq.heappop(heap)
print heap
print heapq.heappop(heap)
print heap

print '--------------'

l = [42, 45, 35, 3]
print l

heapq.heapify(l)
print l

print heapq.heapreplace(l, 36)
print l

print heapq.heappop(l)
print l
print heapq.heappop(l)
print l
print heapq.heappop(l)
print l
print heapq.heappop(l)
print l

print '--------------'


for i in heapq.merge():
   print i

print list(heapq.merge())

print '-'

for j in heapq.merge([3, 7, 18]):
    print j

print '-'

for k in heapq.merge([3, 7, 18], [5, 21, 44]):
    print k

print '-'

for m in heapq.merge([3, 7, 18], [5, 21, 44], [2, 33]):
    print m

print '------'

for n in heapq.nlargest(5, [3, 15, 56, 38, 49, 12, 41]):
    print n
print '-'
for np in heapq.nlargest(5, [3, 15]):
    print np

print '---'

for o in heapq.nsmallest(5, [3, 15, 56, 38, 49, 12, 41]):
    print o
print '-'
for op in heapq.nsmallest(5, [3, 15]):
    print op



