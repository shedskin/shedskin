

# modified version that only works with 1x1 matrices

import orbital
import math
#import scipy.linalg
#import Numeric

class fermion:
  def __init__(self,orb):
    self.orb = orb
    self.m_up = None
    self.m_down = None
    self.m_inv_up = None
    self.m_inv_down = None
  def set_orbital(self,orb):
    self.orb = orb

  def fill_matrix(self,epos):
    n = len(epos)
    e_up = epos[:(n+1)/2]
    e_down = epos[(n+1)/2:]
    self.m_up = []
    for p in e_up:
      vals = self.orb.compute_value(p,len(e_up))
      self.m_up.append(vals)

    self.m_down = []
    for p in e_down:
      vals = self.orb.compute_value(p,len(e_down))
      self.m_down.append(vals)

  def invert(self):

    if len(self.m_up) > 0:
      #self.m_inv_up = scipy.linalg.inv(self.m_up)
      self.m_inv_up = [[1.0/self.m_up[0][0]]]
    else:
      self.m_inv_up = []
    if len(self.m_down) > 0:
      #self.m_inv_down = scipy.linalg.inv(self.m_down)
      self.m_inv_down = [[1.0/self.m_down[0][0]]]
    else:
      self.m_inv_down = []

  def compute_log_ratio(self,epos,p,idx):
    log_det_old = self.compute_log_value(epos)
    old_p = epos[idx]
    epos[idx] = p
    log_det_new =  self.compute_log_value(epos)
    epos[idx] = old_p
    diff = log_det_new - log_det_old
    return diff

  def compute_log_value(self,epos):
    self.fill_matrix(epos)
    det_up = 1.0
    if len(self.m_up) == 1:
      det_up = self.m_up[0][0]
    elif len(self.m_up) > 1:
      #det_up = scipy.linalg.det(self.m_up)
      det_up = self.m_up[0][0]

    det_down = 1.0
    if len(self.m_down) == 1:
      det_down = self.m_down[0][0]
    elif len(self.m_down) > 1:
      #det_down = scipy.linalg.det(self.m_down)
      det_down = self.m_down[0][0]

    log_det =  0.0
    try:
      log_det +=  math.log(abs(det_up))
    except OverflowError:
      pass
    try:
      log_det +=  math.log(abs(det_down))
    except OverflowError:
      pass

      #log_det =  math.log(abs(det_up)) + math.log(abs(det_down))

    return log_det

  def compute_value(self,epos):
    self.fill_matrix(epos)
    det_up = 1.0
    if len(self.m_up) > 0:
      #det_up = scipy.linalg.det(self.m_up)
      det_up = self.m_up[0][0]
    det_down = 1.0
    if len(self.m_down) > 0:
      #det_down = scipy.linalg.det(self.m_down)
      det_down = self.m_down[0][0]
    return det_up*det_down

  def compute_del(self,epos,k):
    self.fill_matrix(epos)
    self.invert()
    n = len(epos)
    n_orb = len(self.m_up)
    if k > n/2:
      n_orb = len(self.m_down)

    p = epos[k]
    vals = self.orb.compute_del(p,n_orb)
    sum = []
    for i in range(len(vals[0])):
      sum.append(0.0)
    if k < (n+1)/2:
      for i in range(len(vals)):
        for j in range(len(vals[i])):
          sum[j] += vals[i][j]*self.m_inv_up[i][k]
    else:
      for i in range(len(vals)):
        for j in range(len(vals[i])):
          sum[j] += vals[i][j]*self.m_inv_down[i][k-(n+1)/2]
    return sum

  def compute_del_sq(self,epos,k):
    self.fill_matrix(epos)
    self.invert()
    n = len(epos)
    p = epos[k]
    n_orb = len(self.m_up)
    if k > n/2:
      n_orb = len(self.m_down)
    vals = self.orb.compute_del_sq(p,n_orb)
    sum = 0.0
    if k < (n+1)/2:
      for i in range(len(vals)):
        sum += vals[i]*self.m_inv_up[i][k]
    else:
      for i in range(len(vals)):
        sum += vals[i]*self.m_inv_down[i][k-(n+1)/2]
    return sum
