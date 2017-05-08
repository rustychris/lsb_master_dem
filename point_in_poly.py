import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from shapely import geometry

import matplotlib.tri as delaunay
from stompy.spatial import wkb2shp,field
from stompy.plot import plot_wkb
from stompy.grid import (unstructured_grid, exact_delaunay)


from stompy import utils
## 

#xyz=pd.read_csv('../../rma_bathy/SJSC-Bay-Delta_mNAVD88_6.xyz').values

xyz=field.XYZText('../../rma_bathy/SJSC-Bay-Delta_mNAVD88_6.xyz',sep=',')

sources=wkb2shp.shp2geom('sources_v01.shp')

## 

poly=sources['geom'][39]

buff=200
xyz_sub=xyz.clip_to_polygon(poly.buffer(buff))

## 
dem1=xyz_sub.to_grid(dx=5,dy=10,interp='linear')

## 


# That's okay, although not that great.
# 1st step: build a triangulation, embed the polygon as
# constrained edges, see how that looks.

cdt=exact_delaunay.Triangulation(extra_node_fields=[ ('value',np.float64) ])
cdt.bulk_init(xyz_sub.X)
cdt.nodes['value'] = xyz_sub.F


# Add in the nodes and edges of the polygon:
poly_pnts=np.array(poly.exterior)
if np.all( poly_pnts[-1] == poly_pnts[0] ):
    poly_pnts=poly_pnts[:-1]
new_values=xyz_sub.interpolate(poly_pnts,'nearest')

poly_nodes=[]
for pnt,value in zip( poly_pnts, new_values):
    poly_nodes.append( cdt.add_node(x=pnt,value=value) )

from stompy import utils
for a,b in utils.circular_pairs(poly_nodes):
    cdt.add_constraint(a,b)

## 

xyz_aug=field.XYZField(X=cdt.nodes['x'],
                       F=cdt.nodes['value'] )

aug_tri = delaunay.Triangulation(xyz_aug.X[:,0],xyz_aug.X[:,1],
                                 cdt.cells['nodes'][ ~cdt.cells['deleted'] ])
xyz_aug._tri = aug_tri

dem2=xyz_aug.to_grid(dx=5,dy=10,interp='linear')


## 

plt.figure(20).clf()
#fig,ax=plt.subplots(1,1,num=20,sharex=True,sharey=True)
fig,(ax,ax2)=plt.subplots(1,2,num=20,sharex=True,sharey=True)

plot_wkb.plot_polygon(poly,ax=ax,fc='none')

ax.scatter(xyz_sub.X[:,0],
           xyz_sub.X[:,1],30,
           xyz_sub.F,lw=1,edgecolor='m')

dem1.plot(ax=ax,interpolation='none',zorder=-2)

# cdt.plot_edges(ax=ax,edgecolor='k')
# Worse:
dem2.plot(ax=ax2,interpolation='none',zorder=-2)

plot_wkb.plot_polygon(poly,ax=ax2,fc='none')


ax.axis('equal')

## 

# What about grab nearest N, look for max/min direction
# of variance, and do anisotropic along that direction?

pnt=np.array( [580711., 4146341.] )

nearest=xyz_sub.within_r(pnt,200)

n_x=xyz_sub.X[nearest]
n_z=xyz_sub.F[nearest]

dxy=n_x - pnt

## 

# A little bit more futzing ...

# layout a grid which is going to have vectors for the gradient

grad=np.zeros( dem2.F.shape + (2,), 'f8')

## 

# Can I extract a medial axis, then buffer that out or similar
# to establish the local orientation?

cdt=exact_delaunay.Triangulation()

# Add in the nodes and edges of the polygon:
poly_pnts=np.array(poly.exterior)
if np.all( poly_pnts[-1] == poly_pnts[0] ):
    poly_pnts=poly_pnts[:-1]
    
poly_nodes= [ cdt.add_node(x=pnt)
              for pnt in poly_pnts]

poly_edges=[]
for a,b in utils.circular_pairs(poly_nodes):
    cdt.add_constraint(a,b)
    poly_edges.append( cdt.nodes_to_edge([a,b]) )

# loop through edges of the polygon, and refine until the 

check_edges=list(poly_edges)

def subdivide(j):
    assert cdt.edges['constrained'][j]
    ab=cdt.edges['nodes'][j]
    new_x=cdt.nodes['x'][ab].mean(axis=0)
    a,b=ab
    cdt.remove_constraint(a,b)
    mid=cdt.add_node(x=new_x)
    cdt.add_constraint(a,mid)
    cdt.add_constraint(mid,b)
    j1=cdt.nodes_to_edge(a,mid)
    j2=cdt.nodes_to_edge(mid,b)
    assert j1 is not None
    assert j2 is not None
    check_edges.append(j1)
    check_edges.append(j2)
    print "Subdivided edge %d to %d %d, nodes %d %d %d"%(j,
                                                         j1,j2,
                                                         ab[0],ab[1],mid)

l_min=5.0
l_max_frac=0.5


def maybe_refine_edge(j):
    centroids=cdt.cells_centroid()

    a,b=cdt.edges['nodes'][j]

    for cell in cdt.edges['cells'][j]:
        if poly.contains( geometry.Point(centroids[cell]) ):
            break
    else:
        assert False

    for n in cdt.cells['nodes'][cell]:
        if n not in [a,b]:
            c=n
            break
    else:
        assert False
    ab_len=utils.dist( cdt.nodes['x'][a]-cdt.nodes['x'][b] )

    circum=cdt.cells_center()[cell]
    ab_circum_len = utils.point_line_distance( circum, cdt.nodes['x'][ [a,b] ] )
    
    if (ab_len>l_min) and (ab_len>l_max_frac*ab_circum_len):
        subdivide(j)

## 
for count in range(100):
    j=check_edges.pop(0)
    maybe_refine_edge(j)

    print len(check_edges)
    if len(check_edges)==0:
        break


## 

# Extract a medial axis from that:


ma=unstructured_grid.UnstructuredGrid()

# some robustness issues are leading to the hack of checking
# both centroid and circumcenter.
cc=cdt.cells_center(refresh=True)

centroids=cdt.cells_centroid()
cell_sub = [ (~cdt.cells['deleted'][i]) 
             and poly.contains( geometry.Point(centroids[i]) )
             and poly.contains( geometry.Point(cc[i]) )
             for i in range(cdt.Ncells()) ]
cell_sub=np.array(cell_sub)


cell_to_node={}

for j in cdt.valid_edge_iter():
    c1,c2 = cdt.edges['cells'][j]
    if c1<0 or c2<0:
        continue
    if not (cell_sub[c1] and cell_sub[c2]):
        continue
    for c in [c1,c2]:
        if c not in cell_to_node:
            cell_to_node[c] = ma.add_node( x=cc[c] )
    ma.add_edge(nodes=[cell_to_node[c1],
                       cell_to_node[c2]] )

## 

# That gets to a reasonable MA - but still a lot of work to do...

## 

plt.figure(21).clf()
fig,ax=plt.subplots(num=21)

x,y=dem2.xy()
X,Y=np.meshgrid(x,y)

plot_wkb.plot_wkb(poly,ax=ax,fc='none')
ma.plot_edges(ax=ax,color='m',lw=2)

ax.axis('equal')
plt.pause(0.01)

## 

