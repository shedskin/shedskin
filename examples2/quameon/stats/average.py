#!/usr/bin/python

"""\
 average.py - compute statistics for regular and weighted data

"""

# Copyright 2006, Mark Dewing
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.


import math
import sys


class averager:
  """Compute average, variance, and standard error for a set of data"""
  def __init__(self):
    self.sum = 0.0
    self.sum_sq = 0.0
    self.norm = 0

  def add_value(self,v):
    self.sum += v
    self.sum_sq += v*v
    self.norm += 1

  def average(self):
    if (self.norm == 0):
      return 0.0
    else:
      return self.sum/self.norm

  def variance(self):
    var = 0.0
    if (self.norm != 0):
      var = (self.sum_sq - self.sum*self.sum/self.norm)/self.norm
    return var

#  def std_dev(self):
#    return math.sqrt(self.variance())

  def error(self):
    err = 0.0
    if (self.norm > 1):
      var = self.variance()
      err = math.sqrt(var/(self.norm-1))
    return err

# the definition of variance and error might be wrong
#class weighted_averager:
#  """Compute average of a weighted set of data"""
#  def __init__(self):
#    self.sum = 0.0
#    self.sum_sq = 0.0
#    self.norm = 0
#    self.weight_sum = 0.0
#    self.weight_sum_sq = 0.0
#
#  def add_value(self,v,w):
#    self.sum += w*v
#    self.sum_sq += w*w*v*v
#    self.norm += 1
#    self.weight_sum += w
#    self.weight_sum_sq += w*w
#
#  def average(self):
#    if (self.norm == 0):
#      return 0.0
#    else:
#      return self.sum/self.weight_sum
#
#  def variance(self):
#    var = 0.0
#    if (self.norm != 0):
#      var = (self.sum_sq - self.sum*self.sum/self.weight_sum)/self.weight_sum
#    return var
#
#  def error(self):
#    err = 0.0
#    if (self.norm > 1):
#      var = self.variance()
#      err = math.sqrt(var/(self.norm-1))
#    return err
#
#  def get_neff(self):
#     neff = self.weight_sum**2/self.weight_sum_sq
#     return neff

def compute_ave(filename,col):
  data = open(filename,"r")
  ave = averager()
  for line in data.readlines():
    s = line.split()
    val = float(s[col])
    ave.add_value(val)
  print("ave = ",ave.average()," err = ",ave.error())


if __name__ == '__main__':
  if len(sys.argv) > 1:
    in_file = sys.argv[1]
    col = 0
    if len(sys.argv) > 2:
      col = int(sys.argv[2])
    compute_ave(in_file,col)
