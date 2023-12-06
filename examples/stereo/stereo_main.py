# James M. Coughlan
# Simple Belief Propagation stereo implementation using Shed Skin.
# Use speed-up technique from: 
# J. Coughlan and H. Shen. "An Embarrassingly Simple Speed-Up of Belief Propagation with Robust Potentials." arXiv. 2010. http://arxiv.org/abs/1010.0012

import numpy as np
import pylab as pl

from scipy import interpolate
# above line must be imported *after* changing directory!
interp1d=interpolate.interp1d

from matplotlib.pyplot import imread

from stereo import do_sweepsSS2

##############
Lnam, Rnam='L.bmp','R.bmp'
nd=40 #number of disparities
dmin,dmax=0,19 #min, max disparities
Tu,Tb=15,3 #discontinuity thresholds (unary, binary potentials)
unBeta,binBeta=1/5., 0.75
num_sweeps = 5
##############
            
#from integer index to real-valued disparity:
disps=[dmin + k/(nd-1.)*(dmax-dmin)  for k in range(nd)]

pl.close('all')
pl.ion()

imL,imR=imread(Lnam)+0.,imread(Rnam)+0.
h,w=np.shape(imL)
print('h,w:',h,w)

rlo,rhi,clo,chi=0,h,0,w
h2,w2=h,w

print('h2,w2:',h2,w2)

#make unary potential:
print('calculating unPots')
unPots=np.zeros((h2,w2,nd),float) #unPots[i,j,d]


errors=np.zeros((h2,w2,nd),float)
x_sparse=np.arange(w)
for i in range(rlo,rhi):
    print('row:',i,)
    y_sparse=imL[i,:]
    for j in range(clo,chi):
        func=interp1d(x_sparse,y_sparse)
        x_dense=np.clip(np.array([j+d  for d in disps]),0.,w-1) #clip so that nothing is out of bounds
        y_dense=func(x_dense)
        errors[i-rlo,j-clo,:]=np.array([min(abs(y-imR[i,j]),Tu) for y in y_dense])
unPots=np.exp(-unBeta*errors)
print()

#make binary potential (homogeneous, and assume symmetric!):
print('calculating binPots')
binPots=np.ones((nd,nd),float) #binPots[d0,d1]
f0=np.exp(-binBeta*Tb)
for d0 in range(nd):
    for d1 in range(nd):
        binPots[d0,d1]=np.exp(-binBeta*min(abs(d0-d1),Tb))

#make messages (Left, Right, Up, Down) and initialize to all ones:
#convention: all message indices [i,j] label ***source*** (not destination) of message
msgs={'L':np.ones((h2,w2,nd),float), 'R':np.ones((h2,w2,nd),float),
      'U':np.ones((h2,w2,nd),float), 'D':np.ones((h2,w2,nd),float)}

def getbeliefs(unPots,msgs):
    h,w,jnk=np.shape(unPots)
    unBels=unPots+0.
    for i0 in range(h):
        for j0 in range(w):
            incoming_nodes=[(i0-1,j0,'D'), (i0+1,j0,'U'), (i0,j0-1,'R'), (i0,j0+1,'L')]
            for (i,j,direc) in incoming_nodes:
                if i>=0 and i<h and j>=0 and j<w:
                    unBels[i0,j0,:] *= msgs[direc][i,j,:]
            unBels[i0,j0,:] /= np.sum(unBels[i0,j0,:]) #normalize beliefs
    return unBels #unBels[i,j,d]

def getwinners(unBels):
    #at each pixel, what is the winning disparity?
    h,w,nd=np.shape(unBels)
    winners=np.ones((h,w),int)
    for i in range(h):
        for j in range(w):
            winners[i,j]=np.argmax(unBels[i,j,:])
    return winners

#(row,col) pixel ranges for each update direction, for use with range() function:
ranges={'L':[(0,h2,1),(w2-1,0,-1)],'R':[(0,h2,1),(0,w2-1,1)],'U':[(h2-1,0,-1),(0,w2,1)],'D':[(0,h2-1,1),(0,w2,1)]}
#note that range should go from right column to left column for 'L' update, etc.


#note: must be compatible with the SS version, which will work on messages padded on each side to eliminate special border cases
def do_sweeps(unPots, binPots, msgs, nsweeps):
    h,w,nd=np.shape(msgs['L'])
    h2,w2=h+2,w+2
    msgs2={}
    for dir in ['L','R','U','D']:
        msgs2[dir]=np.ones((h2,w2,nd),float)
        msgs2[dir][1:(h2-1),1:(w2-1),:]=msgs[dir]+0.

    msgs2['L'],msgs2['R'],msgs2['U'],msgs2['D']=do_sweepsSS2(unPots.tolist(), binPots.tolist(), msgs2['L'].tolist(),msgs2['R'].tolist(),msgs2['U'].tolist(),msgs2['D'].tolist(), nsweeps, h2,w2,nd, Tb, f0)

    for dir in ['L','R','U','D']:
        msgs2[dir]=np.array(msgs2[dir]) #convert from lists:
        msgs2[dir]=msgs2[dir][1:(h2-1),1:(w2-1)][:]+0
    return msgs2
    
	
#do BP sweeps:
msgs=do_sweeps(unPots, binPots, msgs, num_sweeps)
unBels=getbeliefs(unPots,msgs)
winners=getwinners(unBels)
pl.figure();pl.imshow(winners,interpolation='nearest');pl.title('winners');pl.colorbar()
pl.show()
input('<press enter>')
