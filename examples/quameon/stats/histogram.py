#!/usr/bin/python

import math
import sys

class histogram:
  def __init__(self,start,end,nbins=10):
    self.start = start
    self.end = end
    self.nbins = nbins
    self.inc = (end-start)/nbins
    self.bins = []
    self.norm = []
    self.npts = 0
    for i in range(0,nbins):
      self.bins.append(0.0)
      self.norm.append(0)

  def add_value(self,v):
    idx = -1
    if self.inc > 0.0:
      idx = int((v - self.start)/self.inc)
    if idx < 0 or idx >= self.nbins:
      return
    self.bins[idx] += 1
    self.npts += 1

#  def get_histogram(self):
#    hist = []
#    for i in range(0,self.nbins):
#      x = self.start + i*self.inc
#      if self.npts == 0:
#        val = 0
#      else:
#        val = self.bins[i]/(1.0*self.npts)
#      hist.append((x,val))
#    return hist

  def print_histogram(self,fname):
    out_hist = open(fname,"w")
    for i in range(0,self.nbins):
      x = self.start + i*self.inc
      val = self.bins[i]/(1.0*self.npts)
      print(x, val, file=out_hist)
    out_hist.close()


class auto_histogram:
  def __init__(self,nbins=10,nstart=100):
    self.nbins = nbins
    self.nstart = nstart
    self.start_pts = []
    self.hist = None

  def add_value(self,v):
    if len(self.start_pts) < self.nstart-1:
      self.start_pts.append(v)
    elif len(self.start_pts) == self.nstart-1:
      self.start_pts.append(v)
      self.init_hist()
    else:
      self.hist.add_value(v)

  def init_hist(self):
    if len(self.start_pts) == 0:
      max_v = 1.0
      min_v = 0.0
    else:
      max_v = self.start_pts[0]
      min_v = self.start_pts[0]
    for v in self.start_pts:
      if v > max_v:
        max_v = v
      if v < min_v:
        min_v = v
    dist = max_v - min_v
    min_v -= dist*.1
    max_v += dist*.1
    self.hist = histogram(min_v,max_v,self.nbins)
    for v in self.start_pts:
       self.hist.add_value(v)

#  def get_histogram(self):
#    if not(self.hist):
#       self.init_hist()
#    return self.hist.get_histogram()

  def print_histogram(self,fname):
    if not(self.hist):
       self.init_hist()
    self.hist.print_histogram(fname)


#class weighted_histogram:
#  def __init__(self,start,end,nbins=10):
#    self.start = start
#    self.end = end
#    self.nbins = nbins
#    self.inc = (end-start)/nbins
#    self.bins = []
#    self.npts = 0
#    self.total_weight = 0
#    for i in range(0,nbins):
#      self.bins.append(0.0)
#
#  def add_value(self,v,weight):
#    idx = int((v - self.start)/self.inc)
#    #print v,idx
#    if idx < 0 or idx >= self.nbins:
#      return
#    self.bins[idx] += weight
#    self.npts += 1
#    self.total_weight += weight
#
#  def print_histogram(self,fname):
#    out_hist = open(fname,"w")
#    for i in range(0,self.nbins):
#     x = self.start + i*self.inc
#     val = self.bins[i]/(1.0*self.total_weight)
#     print >>out_hist, x,val
#    out_hist.close()


#class auto_weighted_histogram:
#  def __init__(self,nbins=10,nstart=100):
#    self.nbins = nbins
#    self.nstart = nstart
#    self.start_pts = []
#    self.hist = None
#
#  def add_value(self,v,weight):
#    if len(self.start_pts) < self.nstart-1:
#      self.start_pts.append((v,weight))
#    elif len(self.start_pts) == self.nstart-1:
#      self.start_pts.append((v,weight))
#      self.init_hist()
#    else:
#      self.hist.add_value(v,weight)
#
#  def init_hist(self):
#    max_v = self.start_pts[0][0]
#    min_v = self.start_pts[0][0]
#    for (v,w) in self.start_pts:
#      if v > max_v:
#        max_v = v
#      if v < min_v:
#        min_v = v
#    dist = max_v - min_v
#    min_v -= dist*.1
#    max_v += dist*.1
#    self.hist = weighted_histogram(min_v,max_v,self.nbins)
#    for (v,w) in self.start_pts:
#       self.hist.add_value(v,w)
#
#  def print_histogram(self,fname):
#    if not(self.hist):
#       self.init_hist()
#    self.hist.print_histogram(fname)

#class two_histogram:
#  def __init__(self,start,end,nbins=[10,10]):
#    self.start = start
#    self.end = end
#    self.nbins = nbins
#    self.inc = []
#    self.inc.append((end[0]-start[0])/nbins[0])
#    self.inc.append((end[1]-start[1])/nbins[1])
#    self.bins = []
#    self.norm = []
#    self.npts = 0
#    for i in range(0,self.nbins[0]):
#      self.bins.append([])
#      for j in range(0,self.nbins[1]):
#        self.bins[i].append(0.0)
#
#  def add_value(self,v):
#    idx1 = int((v[0] - self.start[0])/self.inc[0])
#    idx2 = int((v[1] - self.start[1])/self.inc[1])
#    idx = idx1*self.nbins[0] + idx2
#    if idx1 < 0 or idx1 >= self.nbins[0] or idx2 < 0 or idx2 > self.nbins[1]:
#      return
#    self.bins[idx1][idx2] += 1
#    self.npts += 1
#
#  def print_histogram(self,fname):
#    out_hist = open(fname,"w")
#    for i in range(0,self.nbins[0]):
#      for j in range(0,self.nbins[1]):
#        x = self.start[0] + i*self.inc[0]
#        y = self.start[1] + j*self.inc[1]
#	idx = i*self.nbins[0] + j
#        val = self.bins[i][j]/(1.0*self.npts)
#        print >>out_hist, x,y,val
#      print >>out_hist," "
#    out_hist.close()

#class auto_two_histogram:
#  def __init__(self,nbins=[10,10],nstart=100):
#    self.nbins = nbins
#    self.nstart = nstart
#    self.start_pts = []
#    self.hist = None
#
#  def add_value(self,v):
#    if len(self.start_pts) < self.nstart-1:
#      self.start_pts.append(v)
#    elif len(self.start_pts) == self.nstart-1:
#      self.start_pts.append(v)
#      self.init_hist()
#    else:
#      self.hist.add_value(v)
#
#  def init_hist(self):
#    max_v_x = self.start_pts[0][0]
#    min_v_x = self.start_pts[0][0]
#    max_v_y = self.start_pts[0][1]
#    min_v_y = self.start_pts[0][1]
#    for v in self.start_pts:
#      if v[0] > max_v_x:
#        max_v_x = v[0]
#      if v[0] < min_v_x:
#        min_v_x = v[0]
#      if v[1] > max_v_y:
#        max_v_y = v[1]
#      if v[1] < min_v_y:
#        min_v_y = v[1]
#    dist_x = max_v_x - min_v_x
#    min_v_x -= dist_x*.1
#    max_v_x += dist_x*.1
#    dist_y = max_v_y - min_v_y
#    min_v_y -= dist_y*.1
#    max_v_y += dist_y*.1
#    self.hist = two_histogram([min_v_x,min_v_y],[max_v_x,max_v_y],self.nbins)
#    for v in self.start_pts:
#       self.hist.add_value(v)
#
#  def print_histogram(self,fname):
#    if not(self.hist):
#       self.init_hist()
#    self.hist.print_histogram(fname)

def compute_hist(in_file,col):
  data = open(in_file,"r")
  hist = auto_histogram(40,5000)
  for line in data.readlines():
    s = line.split()
    val = float(s[col])
    hist.add_value(val)
  hist.print_histogram("hist.dat")



if __name__ == '__main__':
  if len(sys.argv) > 1:
    in_file = sys.argv[1]
    col = 0
    if len(sys.argv) > 2:
      col = int(sys.argv[2])
    compute_hist(in_file,col)
