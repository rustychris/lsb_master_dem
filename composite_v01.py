import matplotlib.pyplot as plt
import numpy as np
from stompy.spatial import field

import os
opj=os.path.join

from stompy.spatial import interp_coverage
import composite_field_v01 
reload(interp_coverage)
reload(field)
reload(composite_field_v01)

from composite_field_v01 import mbf


# getting the breach out of Knapp Tract correct
tile3=(584931.40258328104,
       585945.29478035471,
       4145124.3747996395,
       4146167.1940208809)

blend=mbf.to_grid(dx=5.,dy=5.,bounds=tile3)

## 

plt.figure(1).clf()
fig,ax=plt.subplots(num=1)
blend.plot(interpolation='nearest',ax=ax,vmin=-10,vmax=5)

blend.plot_hillshade(ax=ax)


## 
#- # 
bounds = array([[589000.0,4145000],
                [590000.0,4146000]])
print "Blending"
blend = mbf.to_grid(dx=50.0,dy=50.0,bounds=bounds)

## 


dem_40=field.GdalGrid('/home/rusty/data/bathy_dwr/joined-40m.tif')

## 

fig,ax=plt.subplots(num=1)
dem_40.plot(interpolation='nearest',ax=ax,vmin=-10,vmax=5)

## 

tile=(581500,
      587000,
      4144000,
      4149000)
blend=mbf.to_grid(dx=20.,dy=20.,bounds=tile)
plt.figure(1).clf()
fig,ax=plt.subplots(num=1)
blend.plot(interpolation='nearest',ax=ax,vmin=-10,vmax=5)

blend.plot_hillshade(ax=ax)

## 

tile2=(582500.,
       586000.,
       4144400.,
       4148000.)

blend=mbf.to_grid(dx=5.,dy=5.,bounds=tile2)

## 

plt.figure(1).clf()
fig,ax=plt.subplots(num=1)
blend.plot(interpolation='nearest',ax=ax,vmin=-10,vmax=5)

blend.plot_hillshade(ax=ax)
## 

# getting the breach out of Knapp Tract correct
tile3=(584931.40258328104,
       585945.29478035471,
       4145124.3747996395,
       4146167.1940208809)

blend=mbf.to_grid(dx=5.,dy=5.,bounds=tile3)

## 

plt.figure(1).clf()
fig,ax=plt.subplots(num=1)
blend.plot(interpolation='nearest',ax=ax,vmin=-10,vmax=5)

blend.plot_hillshade(ax=ax)

## 
