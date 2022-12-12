#https://github.com/shedskin/shedskin/issues/191

import os

print(os.popen("echo Hello World").read())
