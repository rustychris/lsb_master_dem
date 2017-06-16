"""
The in-pond data is very blocky - apply a bit of smoothing
before it gets used in the dem
"""
import matplotlib.pyplot as plt
from stompy.spatial import field

## 
fn='../../sbsprp/SbayPondBathy2005/merged_ponds.tif'
ponds_dem=field.GdalGrid(fn)

# limit it to the parts we're actually using
ponds_crop=ponds_dem.extract_tile(xxyy=(579160, 592550, 4141950, 4146580),
                                  res=2,interpolation='bilinear')
# expand a bit
ponds_crop.fill_by_convolution(iterations=5,kernel_size=5)
# Smooth it
ponds_crop.smooth_by_convolution(iterations=5)

## 
            
plt.figure(2).clf()
fig,ax=plt.subplots(num=2)
ponds_crop.plot(ax=ax,interpolation='nearest')

## 

# And looks like we need to convert to m, too.
ponds_crop.F *= 0.3048

## 
ponds_crop.write_gdal('../sources/merged_ponds_2m_smoothed.tif')
