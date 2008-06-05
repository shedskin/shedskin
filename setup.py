#!/usr/bin/env python
import sys, os

# create compiler startup script

if sys.platform != 'win32':
    ss = file('shedskin','w')
    ss.write('#!/bin/bash\n')
    ss.write('SHEDSKIN_ROOT="%s"\n' % os.getcwd()) 
    ss.write('%s "$SHEDSKIN_ROOT/ss.py" $*\n' % sys.executable)
    ss.close()

    os.system('chmod a+wrx shedskin')

