#blah
import blah as test
import pickle

blah = test.Blah(7, 'eight')
s = pickle.dumps(blah)
obj = pickle.loads(s)
print obj.a, obj.b
