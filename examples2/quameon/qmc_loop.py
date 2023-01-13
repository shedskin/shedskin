#!/usr/bin/python

"""\
 qmc_loop.py - VMC loop
"""

# Copyright (C) 2006, Mark Dewing
# http://quameon.sourceforge.net/
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.

import math
import random
from stats import average
import wave_func
#import scipy.optimize

def construct_trial_move(box,p,delta):
  tr = []
  for i in range(0,len(p)):
    d = p[i] + delta*(random.random()-0.5)
    tr.append(d)
  return tr

def compute_wavefunction_ratio(wavef,box,epos,p,idx):
   #old_psi = wavef.compute_log_value(epos,epos[idx],idx)
   #new_psi = wavef.compute_log_value(epos,p,idx)
   #return new_psi - old_psi
   diff_psi = wavef.compute_log_ratio(epos,p,idx)
   return diff_psi

class qmc_loop:
  def __init__(self,nstep=10,nblock=10):
    self.nstep = 10
    self.nblock = 10
    self.delta = 2.0
    self.epos = []
    self.naccept = 0
    self.ntry = 0
    self.box = None
    self.wavef = None
    self.ave_e = None
    self.ave_kin_e = None
    self.ave_pot_e = None
    self.diff_e = None
    self.en_file = None
    self.save_samples = None
    self.observables = []
    self.do_num_loc_e = False

  def add_epos(self,pos):
    self.epos.append(pos)

  def add_observable(self,obs):
    self.observables.append(obs)

  def compute_energy(self):
    self.ave_e = average.averager()
    self.ave_kin_e = average.averager()
    self.ave_pot_e = average.averager()
    self.diff_e = average.averager()
    for nb in range(0,self.nblock):
      for ns in range(0,self.nstep):
        for j in range(0,len(self.epos)):
          tr = construct_trial_move(self.box,self.epos[j],self.delta)
          wave_ratio = compute_wavefunction_ratio(self.wavef,self.box,self.epos,tr,j)
          arg = 2*wave_ratio
          prob = 1.0
          if (arg < 0.0):
            prob = math.exp(arg)
          if prob > random.random():
            self.epos[j] = tr
            self.naccept += 1
      loc_e,kin_e,pot_e = self.wavef.local_energy(self.epos)
      if self.do_num_loc_e:
        num_loc_e,num_kin_e,num_pot_e = self.wavef.local_energy_num(self.epos)
        diff = abs(loc_e - num_loc_e)
        self.diff_e.add_value(diff)
      #if self.en_file:
      #  print >>self.en_file ,loc_e
      self.ave_e.add_value(loc_e)
      self.ave_kin_e.add_value(kin_e)
      self.ave_pot_e.add_value(pot_e)
      for obs in self.observables:
        obs.accumulate(self.epos,self.wavef,loc_e)
      #if self.save_samples != None:
      #  log_psi = self.wavef.compute_total_log_value(self.epos)
      #  copy_epos = []
      #  for p in self.epos:
      #    copy_epos.append(p)
      #  self.save_samples.append((copy_epos,loc_e,log_psi))
    self.ntry += self.nblock*self.nstep*len(self.epos)

  def accept_ratio(self):
    if (self.ntry > 0):
      return self.naccept/(1.0*self.ntry)
    else:
      return 0

#  def get_vp(self):
#    return self.wavef.get_vp()

#  def set_vp(self,vp):
#    return self.wavef.set_vp(vp)

#  def compute_reweight_variance(self,new_vp):
#    #print 'new_vp = ',new_vp
#    self.wavef.set_vp(new_vp)
#    ret = []
#    eave = average.averager()
#    eloc_list = []
#    for (pos,eloc,log_psi) in self.save_samples:
#      eloc_new = self.wavef.local_energy(pos)
#      eloc_list.append(eloc_new)
#      eave.add_value(eloc_new)
#    et = eave.average()
#    #for (pos,eloc,log_psi) in self.save_samples:
#    #  eloc_new = self.wavef.local_energy(pos)
#    #  #ret.append(eloc_new-self.etrial)
#    #  ret.append(eloc_new-et)
#    evar = average.averager()
#    for e in eloc_list:
#      evar.add_value((e-et)**2)
#      ret.append(e-et)
#    print 'var = ',evar.average()
#    return ret

#  def compute_reweight_variance2(self,new_vp):
#    vals = self.compute_reweight_variance(new_vp)
#    evar = average.averager()
#    for v in vals:
#      evar.add_value(v**2)
#    return evar.average()

#  def compute_reweight_energy(self,new_vp):
#    #print 'new_vp = ',new_vp
#    self.wavef.set_vp(new_vp)
#    ave = average.weighted_averager()
#    for (pos,eloc,psi_old) in self.save_samples:
#      eloc_new = self.wavef.local_energy(pos)[0]
#      psi_new = self.wavef.compute_total_log_value(pos)
#      wt = math.exp(2*(psi_new-psi_old))
#      ave.add_value(eloc_new,wt)
#    return ave

#  def derivative_vp(self,en):
#    vp = self.wavef.get_vp()
#    h = 0.001
#    deriv = []
#    for i in range(len(vp)):
#      new_vp = vp[:]
#      new_vp[i] += h
#      vph = self.compute_reweight_energy(new_vp).average()
#      val = (vph-en)/h
#      deriv.append(val)
#    self.wavef.set_vp(vp)
#    return deriv

#def var_func(new_vp,qmcl):
#  return qmcl.compute_reweight_variance(new_vp)
#
#def var_func2(new_vp,qmcl):
#  return qmcl.compute_reweight_variance2(new_vp)



#if __name__ == '__main__':
#  test_qmc_loop()

