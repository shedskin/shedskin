

# A simple program to find the prime factors of a given number.
# (c) Rohit Krishna Kumar
# --- http://www.geocities.com/rohitkkumar

import math

def prime(n):                            # n: [int]
    if(n==1):                            # [int]
        return False                     # [int]
    if(n==2):                            # [int]
        return True                      # [int]
    if(not n%2):                         # [int]
        return False                     # [int]
    for i in range(3,int(math.sqrt(n))+1,2): # [list(int)]
        if(not n%i):                     # [int]
            return False                 # [int]
    return True                          # [int]

def factorize(n,l):                      # n: [int], l: [list(int)]
    for i in range(2,int(math.sqrt(n))+1): # [list(int)]
        if(not n%i):                     # [int]
            if(prime(i)):                # [int]
                l.append(i)              # []
            else:
                factorize(i,l)           # []
            if(prime(n/i)):              # [int]
                l.append(n//i)            # []
            else:
                factorize(n//i,l)         # []
            break


def test_prime_factors():
    factors=[]
    n='2079283419'
    #raw_input("Number to factorize:")
    factorize(int(n),factors)
    # print(factors)
    assert factors == [3, 3, 3, 1097, 70201]


def test_all():
    test_prime_factors()

if __name__ == '__main__':
    test_all()


