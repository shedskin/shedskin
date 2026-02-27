import heapq


def test_heapify():
    l = []
    heapq.heapify(l)
    assert l == []

    l = [42, 45, 35, 3]
    heapq.heapify(l)
    assert l == [3, 42, 35, 45]


def test_heapify_max():
    l = []
    heapq.heapify_max(l)
    assert l == []

    l = [42, 45, 35, 3]
    heapq.heapify_max(l)
    assert l == [45, 42, 35, 3]


def test_heappush_max():
    l = [30, 10, 20]
    heapq.heappush_max(l, 50)
    assert l == [50, 30, 20, 10]


def test_heappop():
    l = [2, 8, 16]
    assert heapq.heappop(l) == 2
    assert l == [8, 16]

    l = []
    error = None
    try:
        heapq.heappop(l)
    except IndexError as e:
        error = str(e)
    assert error == 'index out of range'


def test_heappop_max():
    l = [30, 10, 20]
    assert heapq.heappop_max(l) == 30
    assert l == [20, 10]


def test_heappushpop_max():
    l = []
    assert heapq.heappushpop_max(l, 10) == 10
    assert l == []

    l = [30, 10, 20]
    assert heapq.heappushpop_max(l, 35) == 35
    assert l == [30, 10, 20]

    l = [30, 10, 20]
    assert heapq.heappushpop_max(l, 25) == 30
    assert l == [25, 10, 20]


def test_heapreplace_max():
    l = []
    error = None
    try:
        assert heapq.heapreplace_max(l, 10) == 10
    except IndexError as e:
        error = str(e)
    assert error == 'index out of range'

    l = [30, 10, 20]
    assert heapq.heapreplace_max(l, 35) == 30
    assert l == [35, 10, 20]

    l = [30, 10, 20]
    assert heapq.heapreplace_max(l, 25) == 30
    assert l == [25, 10, 20]


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


def test_merge():
    assert list(heapq.merge()) == []
    assert list(heapq.merge([3, 7, 18])) == [3, 7, 18]
    assert list(heapq.merge([3, 7, 18], [5, 21, 44])) == [3, 5, 7, 18, 21, 44]
    assert list(heapq.merge([3, 7, 18], [5, 21, 44], [2, 33])) == [2, 3, 5, 7, 18, 21, 33, 44]

    # reverse
    assert list(heapq.merge()) == []
    assert list(heapq.merge([18, 7, 3], reverse=True)) == [18, 7, 3]
    assert list(heapq.merge([18, 7, 3], [44, 21, 5], reverse=True)) == [44, 21, 18, 7, 5, 3]
    assert list(heapq.merge([18, 7, 3], [44, 21, 5], [33, 2], reverse=True)) == [44, 33, 21, 18, 7, 5, 3, 2]

    # key
    assert list(heapq.merge(['aap', 'ans', 'Arie'], ['alaaf', 'ALAAF', 'ANSJOVIS'], key=lambda x:x.lower())) == ['aap', 'alaaf', 'ALAAF', 'ans', 'ANSJOVIS', 'Arie']

    # key & reverse
    assert list(heapq.merge(['Arie', 'ans', 'aap'], ['ANSJOVIS', 'ALAAF', 'alaaf'], key=lambda x:x.lower(), reverse=True)) == ['Arie', 'ANSJOVIS', 'ans', 'ALAAF', 'alaaf', 'aap']


def test_nlargest():
    assert list(heapq.nlargest(5, [3, 15, 56, 38, 49, 12, 41])) == [56, 49, 41, 38, 15]
    assert list(heapq.nlargest(5, [3, 15])) == [15, 3]

    assert list(heapq.nlargest(3, ['aap', 'Arie', 'ans', 'ANSJOVIS', 'alaaf', 'ALAAF'])) == ['ans', 'alaaf', 'aap']
    assert list(heapq.nlargest(3, [s.lower() for s in ['aap', 'Arie', 'ans', 'ANSJOVIS', 'alaaf', 'ALAAF']])) == ['arie', 'ansjovis', 'ans']
    assert list(heapq.nlargest(3, ['aap', 'Arie', 'ans', 'ANSJOVIS', 'alaaf', 'ALAAF'], key=lambda x:x.lower())) == ['Arie', 'ANSJOVIS', 'ans']


def test_nsmallest():
    assert list(heapq.nsmallest(5, [3, 15, 56, 38, 49, 12, 41])) == [3, 12, 15, 38, 41]
    assert list(heapq.nsmallest(5, [3, 15])) == [3, 15]


class Bert:
    def __init__(self, val):
        self.val = val

    def __lt__(self, other):
        return self.val < other.val


def get_list(berten):
    return [bert.val for bert in berten]


def test_custom_class():
    l = [Bert(42), Bert(45), Bert(35), Bert(3)]

    heapq.heapify(l)
    assert get_list(l) == [3, 42, 35, 45]

    assert heapq.heapreplace(l, Bert(36)).val == 3
    assert get_list(l) == [35, 42, 36, 45]

    assert heapq.heappop(l).val == 35
    assert get_list(l) == [36, 42, 45]
    assert heapq.heappop(l).val == 36
    assert get_list(l) == [42, 45]
    assert heapq.heappop(l).val == 42
    assert get_list(l) == [45]
    assert heapq.heappop(l).val == 45
    assert get_list(l) == []


def test_all():
    test_heapify()
    test_heapify_max()

    test_heappush_max()

    test_heappop()
    test_heappop_max()

    test_heappushpop_max()

    test_heapreplace_max()

    test_merge()

    test_nlargest()
    test_nsmallest()

    test_heapq_1()  # TODO split up/remove
    test_heapq_2()

    test_custom_class()


if __name__ == '__main__':
    test_all()
