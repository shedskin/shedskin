#!/usr/bin/python

"""\
    ee_dist - e-e distance histograms
"""

# Copyright (C) 2008, Mark Dewing


from stats import histogram
from .observable_base import observable_base
import box_bc

class ee_dist(observable_base):
  def __init__(self):
    #self.dist_hist = histogram.auto_histogram()
    self.dist_hist = histogram.histogram(0.0,4.0,nbins=50)
    self.box = box_bc.box_nopbc()

#  def accumulate(self,epos,wavef,loc_e):
#    #for i in range(len(epos)):
#    #  for j in range(i):
#    #    r = self.box.dist(epos[i],epos[j])
#    #    self.dist_hist.add_value(r)
#    np = [0.0, 0.0, 0.0]
#    ep0 = epos[0]
#    ep1 = epos[1]
#    r1 = self.box.dist(np,ep0)
#    r2 = self.box.dist(np,ep1)
#    r = self.box.dist(ep1,ep0)
#    print r1,r2,r,loc_e


#  def output(self):
#    hist = self.dist_hist.get_histogram()
#    print '# e-e distance'
#    for x,val in hist:
#      print x,val


#if __name__ ==  '__main__':
#  import random
#  eed = ee_dist()
#  for n in range(1000000):
#    epos = []
#    for j in range(2):
#      p = [3*random.random() for i in range(3)]
#      epos.append(p)
#    eed.accumulate(epos,None,None)
#  eed.output()
    
  


