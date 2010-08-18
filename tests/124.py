
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
                l.append(n/i)            # []
            else:
                factorize(n/i,l)         # []
            break

factors=[]                               # [list(int)]
n='2079283419'                             # [int]
#raw_input("Number to factorize:")      # [str]
factorize(int(n),factors)                # []
print factors                            # [list(int)]

