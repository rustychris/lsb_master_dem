import numpy as np
import matplotlib.pyplot as plt

from stompy.spatial import field
from stompy.model.delft import dfm_grid
from stompy.plot import plot_utils


## 

# This one seems like it should just be the Alviso-only grid, but plots as the
# combined...
#g=dfm_grid.DFMGrid('/home/rusty/models/grids/mick_alviso_v4_net.nc/mick_alviso_v4_net.nc')

g=dfm_grid.DFMGrid('/media/hpc/opt/data/delft/lsb_combined/grids/alviso2012_net.nc')

g.add_cell_field('depth',g.interp_node_to_cell(g.nodes['depth']))

## 

dem=field.GdalGrid('tiles_5m_20170501/merged_5m.tif')


## 

clip=(576264.,597495.,4122205.,4154848.)

## 

plt.figure(1).clf()

fig,(ax,ax2)=plt.subplots(1,2,num=1,sharex=True,sharey=True)

img=dem.plot(ax=ax,interpolation='nearest',aspect='auto')

#coll=g.plot_cells(values=g.cells['depth'],lw=0,ax=ax2,clip=clip)
coll=g.contourf_node_values(g.nodes['depth'],np.linspace(-1.2,2.5,20),
                            extend='both')


cax=fig.add_axes([0.93,0.1,0.02,0.4])

cbar=plot_utils.cbar(img,cax=cax,extras=[coll],ax=ax2,label='Bed elev. (m NAVD88)')

plt.setp([coll,img], clim=[-1.2,2.5])

ax.axis('equal')

fig.subplots_adjust(left=0.05)
ax.axis( (587196.,592615.,4139820.,4146642.) )

# z01: used the full grid, already merged
# fig.savefig('compare_to_alviso_grid_z02.png')

## 

reload(unstructured_grid)
reload(dfm_grid)
