
import math


def fact1(n):
    res=1
    for i in range(1, n+1):
        res *= i
    return res



def fact2(n): 
    if (n == 0 or n == 1): 
        return 1
    else: 
        return n * fact2(n-1)



def test_factorial():
    assert fact1(5) == 120
    assert fact2(5) == 120
    assert math.factorial(5) == 120


if __name__ == '__main__':
    test_factorial()
