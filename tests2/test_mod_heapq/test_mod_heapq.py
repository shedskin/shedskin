import heapq



def test_heapq_1():
    heap = [21]

    heapq.heappush(heap, 42)
    assert heap == [21, 42]

    heapq.heappush(heap, 12)
    assert heap == [12, 42, 21]

    assert heapq.heappop(heap) == 12
    assert heap == [21, 42]

    assert heapq.heappushpop(heap, 63) == 21
    assert heap == [42, 63]

    assert heapq.heappop(heap) == 42
    assert heap == [63]

    assert heapq.heappop(heap) == 63
    assert heap == []

    heapq.heappush(heap, 12)
    heapq.heappush(heap, 52)
    heapq.heappush(heap, 112)
    heapq.heappush(heap, 1)
    heapq.heappush(heap, 12)
    assert heap == [1, 12, 112, 52, 12]

    assert heapq.heappop(heap) == 1
    assert heap == [12, 12, 112, 52]

    assert heapq.heappushpop(heap, 63) == 12
    assert heap == [12, 52, 112, 63]

    assert heapq.heappop(heap) == 12
    assert heap == [52, 63, 112]

    assert heapq.heappop(heap) == 52
    assert heap == [63, 112]

def test_heapq_2():

    l = [42, 45, 35, 3]

    heapq.heapify(l)
    assert l == [3, 42, 35, 45]

    assert heapq.heapreplace(l, 36) == 3
    assert l == [35, 42, 36, 45]

    assert heapq.heappop(l) == 35
    assert l == [36, 42, 45]
    assert heapq.heappop(l) == 36
    assert l == [42, 45]
    assert heapq.heappop(l) == 42
    assert l == [45]
    assert heapq.heappop(l) == 45
    assert l == []

def test_heapq_3():

    assert list(heapq.merge()) == []
    assert list(heapq.merge([3, 7, 18])) == [3, 7, 18]
    assert list(heapq.merge([3, 7, 18], [5, 21, 44])) == [3, 5, 7, 18, 21, 44]
    assert list(heapq.merge([3, 7, 18], [5, 21, 44], [2, 33])) == [2, 3, 5, 7, 18, 21, 33, 44]

    assert list(heapq.nlargest(5, [3, 15, 56, 38, 49, 12, 41])) == [56, 49, 41, 38, 15]
    assert list(heapq.nlargest(5, [3, 15])) == [15, 3]

    assert list(heapq.nsmallest(5, [3, 15, 56, 38, 49, 12, 41])) == [3, 12, 15, 38, 41]
    assert list(heapq.nsmallest(5, [3, 15])) == [3, 15]

def test_all():
    test_heapq_1()
    test_heapq_2()
    test_heapq_3()

if __name__ == '__main__':
    test_all() 

