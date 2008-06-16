#!/usr/bin/env python
import sys, os

# create compiler startup script

ss = file('shedskin','w')
ss.write('#!/bin/sh\n')
ss.write('SHEDSKIN_ROOT="%s" %s "%s/ss.py" $*\n' % (os.getcwd(), sys.executable, os.getcwd()))
ss.close()

os.system('chmod a+wrx shedskin')
