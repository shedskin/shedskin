# (c) Mladen Bestvina
#
# linear algebra..

import copy

def inner_prod(v1, v2):
     'inner production of two vectors.'
     sum = 0
     for i in xrange(len(v1)):
            sum += v1[i] * v2[i]
     return sum

def matmulttransp(M, N):
     'M*N^t.'
     return [[inner_prod(v, w) for w in N] for v in M]

def col(M,j):
     v=[]
     rows=len(M)
     for i in xrange(rows):
          v.append(M[i][j])
     return v

def Transpose(M):
     N=[]
     cols=len(M[0])
     for i in xrange(cols):
          N.append(col(M,i))
     return N

def Minor(M,i,j):
     M1=copy.deepcopy(M)
     N=[v.pop(j) for v in M1]
     M1.pop(i)
     return M1

def sign(n):
     return 1-2*(n-2*(n/2))

def determinant(M):
     size=len(M)
     if size==1: return M[0][0]
     if size==2: return M[0][0]*M[1][1]-M[0][1]*M[1][0] # 1x1 Minors don't work
     det=0
     for i in xrange(size):
                    
          det += sign(i)*M[0][i]*determinant(Minor(M,0,i))
     return det
     
def inverse(M):
     size=len(M)
     det=determinant(M)
     if abs(det) != 1: print "error, determinant is not 1 or -1"
     N=[]
     for i in xrange(size):
          v=[]
          for j in xrange(size):
               v.append(det*sign(i+j)*determinant(Minor(M,j,i)))
          N.append(v)
     return N
     
def iterate_sort(list1,A,B,C,D,E,F):
    n=len(list1)
    for i in range(n):
        z=matmulttransp(list1[i],A)
        list1.append(z)
        z=matmulttransp(list1[i],B)

        list1.append(z)
        z=matmulttransp(list1[i],C)

        list1.append(z)
        z=matmulttransp(list1[i],D)

        list1.append(z)
        z=matmulttransp(list1[i],E)

        list1.append(z)
        z=matmulttransp(list1[i],F)

        list1.append(z)

    list1.sort()
    n=len(list1)
    last = list1[0]
    lasti = i = 1
    while i < n:
        if list1[i] != last:
            list1[lasti] = last = list1[i]
            lasti += 1
        i += 1
    list1.__delslice__(lasti,n)
        
def gen(n,list1,A,B,C,D,E,F):
    for i in range(n): iterate_sort(list1,A,B,C,D,E,F)

def inward(U):
    b01=(abs(U[0][0])<abs(U[0][1])) or     ((abs(U[0][0])==abs(U[0][1]) and abs(U[1][0])<abs(U[1][1]))) or     ((abs(U[0][0])==abs(U[0][1]) and abs(U[1][0])==abs(U[1][1]) and      abs(U[2][0])<abs(U[2][1])))

    b12=(abs(U[0][1])<abs(U[0][2])) or     ((abs(U[0][1])==abs(U[0][2]) and abs(U[1][1])<abs(U[1][2]))) or     ((abs(U[0][1])==abs(U[0][2]) and abs(U[1][1])==abs(U[1][2]) and      abs(U[2][1])<abs(U[2][2])))

    return b01 and b12

def examine(U,i,j):
    row1=abs(i)-1
    row2=j-1
    s=1
    if i<0: s=-1
    diff=abs(U[0][row1]+s*U[0][row2])-abs(U[0][row2])
    if diff<0: return -1
    if diff>0: return 1
    else:
        diff=abs(U[1][row1]+s*U[1][row2])-abs(U[1][row2])
        if diff<0: return -1
        if diff>0: return 1
        else:
            diff=abs(U[2][row1]+s*U[2][row2])-abs(U[2][row2])
            if diff<0: return -1
            if diff>0: return 1
            else: return 0

def examine3(U,i,j,k):
    row1=abs(i)-1
    row2=abs(j)-1
    row3=k-1
    s1=1
    s2=1
    if i<0: s1=-1
    if j<0: s2=-1
    diff=abs(s1*U[0][row1]+s2*U[0][row2]+U[0][row3])-abs(U[0][row3])
    if diff<0: return -1
    if diff>0: return 1
    else:
        diff=abs(s1*U[1][row1]+s2*U[1][row2]+U[1][row3])-abs(U[1][row3])
        if diff<0: return -1
        if diff>0: return 1
        else:
            diff=abs(s1*U[2][row1]+s2*U[2][row2]+U[2][row3])-abs(U[2][row3])
            if diff<0: return -1
            if diff>0: return 1
            else: return 0

def binary(n):
    if n==0: return 0
    if n==1: return 1
    m=n/2
    if 2*m==n: return 10*binary(m)
    else: return 10*binary(m)+1 
     
length=6 # wordlength

b=[[0,0,1],[0,1,0],[1,0,0]] 

A=[[1,1,0],[0,1,0],[0,0,1]]
B=inverse(A)
C=[[1,0,0],[0,1,1],[0,0,1]]
D=inverse(B)
E=[[1,0,0],[0,1,0],[1,0,1]]
F=inverse(E)

At=Transpose(A)
Bt=Transpose(B)
Ct=Transpose(C)
Dt=Transpose(D)
Et=Transpose(E)
Ft=Transpose(F)

bt=Transpose(b)

def descending(U):
    type=0

    r=examine(U,1,2)
    if r==0: return 1024
    if r==-1: type=type+1

    r=examine(U,-1,2)
    if r==0: return 1024
    if r==-1: type=type+2

    r=examine(U,1,3)
    if r==0: return 1024
    if r==-1: type=type+4

    r=examine(U,-1,3)
    if r==0: return 1024
    if r==-1: type=type+8

    r=examine(U,2,3)
    if r==0: return 1024
    if r==-1: type=type+16

    r=examine(U,-2,3)
    if r==0: return 1024
    if r==-1: type=type+32

    r=examine3(U,1,2,3)
    if r==0: return 1024
    if r==-1: type=type+64

    r=examine3(U,-1,-2,3)
    if r==0: return 1024
    if r==-1: type=type+128

    r=examine3(U,-1,2,3)
    if r==0: return 1024
    if r==-1: type=type+256

    r=examine3(U,1,-2,3)
    if r==0: return 1024
    if r==-1: type=type+512

    return type

def main2():
    list1=[bt]
    gen(length,list1,A,B,C,D,E,F)
    inlist=[x for x in list1 if inward(x)]
    types=[0]*1025
    for U in inlist:
        t=descending(U)
        types[t]+=1
        if t in [22,25,37,42,6,9,73,262]:
            pass #print t,U
    #print
    for t in reversed(range(1025)):
        if types[t]>0:
            print t, binary(t), types[t]
            break
            #print(' %03i   %012i   %i  ' %(t,binary(t),types[t]))

for x in range(10):
    main2()

