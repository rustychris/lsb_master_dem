import matplotlib.pyplot as plt
import numpy as np
from stompy.spatial import field
from stompy.plot import plot_utils

import os
opj=os.path.join

from stompy.spatial import interp_coverage
import composite_field_v01 

from composite_field_v01 import mbf

## 

# Load in RMA point data:
fn=opj('..','..','rma_bathy','SJSC-Bay-Delta_mNAVD88_6.xyz')
rma_xyz=np.loadtxt(fn,delimiter=',')

## 

# 30s.
comp_at_rma = mbf(rma_xyz[:,:2] )

## 

plt.figure(1).clf()
fig,(ax,ax_diff)=plt.subplots(2,1,num=1,sharex=True,sharey=True)

coll1=ax.scatter(rma_xyz[:,0], rma_xyz[:,1], 40, 
                 rma_xyz[:,2],
                 lw=0)
coll2=ax_diff.scatter(rma_xyz[:,0], rma_xyz[:,1], 40, 
                      comp_at_rma - rma_xyz[:,2],
                      lw=0)

ax.axis('equal')
ax.axis( (572834.,598820.,4131083.,4161534.))

coll1.set_clim([-10,5])
coll2.set_clim([-2,2])

plot_utils.cbar(coll1,ax=ax)
plot_utils.cbar(coll2,ax=ax_diff)



## 

# Similarly, bring in xyz points for LSB grid
from stompy.model.delft import dfm_grid

g=dfm_grid.DFMGrid()
