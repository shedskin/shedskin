from __future__ import print_function

class meuk: pass

try:
    raise meuk()
    print('bad!')
except meuk:
    print('ok!')
except int:
    print('bad..')

try:
    assert 1 == 0
except AssertionError:
    print('crap!')

def crapfunction():
    a,b,c=1,2,3
    assert a > b < c, "the universe won't collapse"
try:
    crapfunction()
except AssertionError as msg:
    print('more crap!', msg)

class ueuk:
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        return 'ueukrepr!'

#try:
#    raise ueuk, 'aha! error.'
#except ueuk, x:
#    print x.msg

try:
    raise ueuk('aha! error.')
except ueuk as x:
    print(x)

try:
    hum = [1,2,3]
    print(hum.index(4))
except ValueError:
    print('exceptions are nice :D')

try:
    raise ValueError('exceptions are nice :D')
except ValueError as y:
    print(y)

try:
    {1:2}[3]
except KeyError as z:
    print('bah!', z)

try:
    [1].index(2)
except ValueError as v:
    print('hah')


