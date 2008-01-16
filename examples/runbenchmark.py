#!/usr/bin/env python
"""
runbenchmark.py

runbenchmark.py is a script to auto-benchmark CPython/CPython+psyco/ShedSkin speed.

according to your machine, this test may cost you 20mins to 1 hour+.

Excute this script in tools or ss-progs directory.
The script will output a benchmark.log file in ss-progs directory.

usage: python runbenchmark.py
(if you wanna keep all testing messages just redirect standard output)

This benchmark script is still in very alpha stage and not well tested.

Author: __tim__ <tim119@gmail.com>
License: Public Domain

"""
import sys, os
import time as _time

testfiles = ['amaze.py', 'brainfuck.py', 'chess.py', 'genetic.py', 'life.py', 'linalg.py', 'mandelbrot.py', 'mask_alg.py', 'nbody.py', 'neural1.py', 'neural2.py','oliva2.py', 'othello.py', 'pisang.py', 'pygmy.py', 'pystone.py', 'richards.py', 'sudoku1.py', 'sudoku2.py', 'sudoku3.py', 'tictactoe.py', 'voronoi.py', 'yopyra.py', 'sieve.py', 'dijkstra.py'] 

mods = {}
testlog = []
psycotestlog = []
sstestlog = []

def runsstest():
    for tf in testfiles:
        try:
            begin = _time.time()
            if tf in ['yopyra.py']:
                os.system("shedskin --infinite %s" % tf )
            else:
                os.system("shedskin %s" % tf )
            sscompile = _time.time() - begin 
            os.system("make")
            cccompile = _time.time() - begin - sscompile
            runfile = "./" + tf[:-3]
            runbgtime = _time.time()
            os.system(runfile)
            runtime = _time.time() - runbgtime
            logmsg = "%s ss-analysis: %f compiletime: %f runtime: %f\n" % (tf[:-3],sscompile,cccompile,runtime)
            sstestlog.append(logmsg)
        except:
            sstestlog.append("%s failed %s\n" % (tf[:-3],"".join(map(str,sys.exc_info()))))

if __name__ == "__main__": 
    if "ss-progs" not in os.getcwd():
        os.chdir("../ss-progs")
        sys.path.append(".")

    #runtest()
    for tf in testfiles:
        try:
            begin = _time.time()
            execfile(tf)
            runtime = _time.time() - begin
            testlog.append("%s runtime: %f\n" % (tf,runtime) )
        except SystemExit: #sudoku2.py need this
            runtime = _time.time() - begin
            testlog.append("%s runtime: %f\n" % (tf,runtime) )
        except:
            testlog.append("%s execute failed %s\n" % (tf,"".join(map(str,sys.exc_info()))))
            continue
    #endof runtest

    #runpsycotest()
    try:
        import psyco
        psyco.full()
        for tf in testfiles:
            try:
                begin = _time.time()
                execfile(tf)
                runtime = _time.time() - begin
                psycotestlog.append("%s runtime: %f\n" % (tf,runtime))
            except SystemExit: #sudoku2.py need this
                runtime = _time.time() - begin
                psycotestlog.append("%s runtime: %f\n" % (tf,runtime) )
            except:
                psycotestlog.append("%s execute failed %s\n" % (tf,"".join(map(str,sys.exc_info()))))
                continue
    except:
        psycotestlog.append("psyco not installed\n")
    #endof runpsycotest

    runsstest()

    #this will create a benchmark.log file in ss-progs.
    logfile=open("benchmark.log","w+")
    alllog = zip(testlog,psycotestlog,sstestlog)

    for ilog in alllog:
        logfile.write("CPython: %sCpython+psyco: %sShedskin: %s\n" % (ilog[0],ilog[1],ilog[2]) )
        
    #uncomment these for another logfile layout
    #logfile.write("\n\n*****CPython*****\n\n")
    #logfile.write("".join(testlog))
    #logfile.write("\n\n*****CPython+psyco*****\n\n")
    #logfile.write("".join(psycotestlog))
    #logfile.write("\n\n*****ShedSkin*****\n\n")
    #logfile.write("".join(sstestlog))

    logfile.close()

    logfile=open("benchmark.log","r")
    print "\n\n\n\n\n Benchmark result: \n\n"
    msg = logfile.read()
    print msg
    logfile.close()
    print "\n\n also check log in : ss-progs/benchmark.log \n\n"

    #if you wanna save pickle format, uncomment these
    #reallog = [testlog,psycotestlog,sstestlog]
    #import pickle
    #output = open('logpickle.pkl', 'wb')
    #pickle.dump(reallog, output)
    #output.close()
