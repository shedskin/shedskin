
# --- import problem
from testdata.bert177 import *
z = zeug()

# --- '_' renaming mangle
import testdata.bert177

class hello:
    def hello(self):
        testdata.bert177.hello(1)

s=hello().hello()


