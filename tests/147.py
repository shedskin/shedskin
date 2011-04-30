
class meuk: pass

try:
    raise meuk()
    print 'bad!'
except meuk:
    print 'ok!'
except int:
    print 'bad..'

try:
    assert 1 == 0
except AssertionError:
    print 'crap!'

def crapfunction():
    a,b,c=1,2,3
    assert a > b < c, "the universe won't collapse"
try:
    crapfunction()
except AssertionError, msg:
    print 'more crap!', msg

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
except ueuk, x:
    print x

try:
    hum = [1,2,3]
    print hum.index(4)
except ValueError:
    print 'exceptions are stupid :D'

try:
    raise ValueError('exceptions are stupid :D')
except ValueError, y:
    print y

try:
    {1:2}[3]
except KeyError, z:
    print 'bah!', z

try:
    [1].index(2)
except ValueError, v:
    print 'hah'


