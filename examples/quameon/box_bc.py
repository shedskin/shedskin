
"""\
 box_bc.py  - compute distances in a periodic box (minimum image convention),
              or in free space

"""

# Copyright (C) 2006, Mark Dewing
# http://quameon.sourceforge.net/
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of the distribution.

import math

class box_nopbc:
  def __init__(self):
    self.ndim = 3
  def dist(self,pos1,pos2):
    r2 = 0.0
    for i in range(len(pos1)):
      d = pos2[i] - pos1[i]
      r2 += d*d
    return math.sqrt(r2)
    #r2 = 0.0
    #for (d1,d2) in zip(pos1,pos2):
    #  d = d2-d1
    #  r2 += d*d
    #return math.sqrt(r2)

  def dist_v(self,vpos1,vpos2):
    diff = []
    r2 = 0.0
    for j in range(len(vpos1)):
      d = vpos1[j] - vpos2[j]
      diff.append(d)
      r2 += d*d
    return (diff,math.sqrt(r2))
    #diff =  [v1 - v2 for (v1,v2) in zip(vpos1,vpos2)]
    #r2 = 0.0
    #for d in diff:
    #  r2 += d*d
    #return (diff,math.sqrt(r2))
#  def move(self,pos):
#    return pos

#class box_pbc:
#  def __init__(self,box_len):
#    self.box_len = box_len
#    self.inv_box_len = 1.0/box_len
#    self.ndim = 3
#  def dist(self,pos1,pos2):
#    r2 = 0.0
#    for i in range(len(pos1)):
#      d = pos2[i] - pos1[i]
#      if d > 0.0:
#        d = d - self.box_len*int(d*self.inv_box_len+0.5)
#      else:
#        d = d - self.box_len*int(d*self.inv_box_len-0.5)
#      r2 += d*d
#    return math.sqrt(r2)
#  def dist_v(self,vpos1,vpos2):
#    for j in range(len(vpos1)):
#      r2 = 0.0
#  def move(self,pos):
#    p = []
#    for i in range(len(pos)):
#      if pos[i] > 0.0:
#        d = pos[i] - self.box_len*int(pos[i]*self.inv_box_len)
#      else:
#        d = pos[i] - self.box_len*int(pos[i]*self.inv_box_len-1.0)
#      p.append(d)
#    return p

if (__name__ == '__main__'):
  pass
  #def test_pot(r):
  #  return r
  #pos = [[1,2],[2,1]]
  #print len(pos)
  #box1  = box_nopbc()
  #print box1.dist(pos[0],pos[1])
  #print energy(box1,pos,test_pot)
  #print energy_one(box1,pos,test_pot,0)
  #box2 = box_pbc(2.0)
  #for i in range(0,120):
  #  p = .1*i - 3
  #  print p,box2.dist([0],[p]),box2.move([p])[0]
