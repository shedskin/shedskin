from __future__ import print_function

def yoyo(a):                             # a: [int]
   print('yoyo', a)                       # [str], [int]

def yoyoyo(b):                           # b: [int]
   print('yoyoyo', b)                     # [str], [int]


x = yoyo                                 # [yoyo]
x = yoyoyo                               # [lambda0]
x(1)                                     # []

