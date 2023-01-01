"""
different implementations of quicksort (some in-place, some not):

from: 

- https://stackoverflow.com/questions/18262306/quicksort-with-python
- https://www.geeksforgeeks.org/python-program-for-quicksort/

"""
import copy


DATA = [1, 200, 50, 485, 22, 22, 3534, 22112]
SORTED = [1, 22, 22, 50, 200, 485, 3534, 22112]

def quicksort1(L):
        x = y = 0
        if L == []:
            return []
        pivot = L[0]
        return (
            quicksort1([x for x in L[1:] if x < pivot])
            + 
            [pivot]
            + 
            quicksort1([y for y in L[1:] if y >= pivot]))


def test_quicksort1():
    assert quicksort1(DATA) == SORTED


def quicksort2(array):
    """Sort the array by using quicksort."""

    less = []
    equal = []
    greater = []

    if len(array) > 1:
        pivot = array[0]
        for x in array:
            if x < pivot:
                less.append(x)
            elif x == pivot:
                equal.append(x)
            elif x > pivot:
                greater.append(x)
        return quicksort2(less) + equal + quicksort2(greater)
    else:
        return array

def test_quicksort2():
    assert quicksort2(DATA) == SORTED


def quicksort3(xs):
    return xs and (
        quicksort3([i for i in xs[1:] if i < xs[0]])
        + 
        [xs[0]] 
        + 
        quicksort3([i for i in xs[1:] if i >= xs[0]])
    )

def test_quicksort3():
    assert quicksort3(DATA) == SORTED


def test_sorted():
    assert sorted(DATA) == SORTED


def partition(array, low, high):
    pivot = array[high]
    i = low - 1
    for j in range(low, high):
        if array[j] <= pivot: 
            i = i + 1
            (array[i], array[j]) = (array[j], array[i])
    (array[i + 1], array[high]) = (array[high], array[i + 1]) 
    return i + 1
  
def quicksort4(array, low, high):
    if low < high: 
        pi = partition(array, low, high)
        quicksort4(array, low, pi - 1)
        quicksort4(array, pi + 1, high)
 
def test_quicksort4():
    # in-place
    data = copy.copy(DATA)
    size = len(data)     
    quicksort4(data, 0, size - 1)
    assert data == SORTED

def test_all():
    test_quicksort1()
    test_quicksort2()
    test_quicksort3()
    test_quicksort4()
    test_sorted()
    

if __name__ == '__main__':
    test_all() 