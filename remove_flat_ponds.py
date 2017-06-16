from scipy import ndimage as ndi
from stompy.spatial import field
import numpy as np
import matplotlib.pyplot as plt
import os
opj=os.path.join

IDRIVE='/media/idrive'


## 

fn='../../sbsprp/SbayPondBathy2005/merged_ponds.tif'
ponds_dem=field.GdalGrid(fn)


zoom=ponds_dem.extents

if 1:
    fn=opj(IDRIVE,
           'BASELAYERS/Elevation_DerivedProducts/LiDAR 2005-2012 entire Bay Area from AECOM',
           'USGS_TopoBathy/San_Francisco_TopoBathy_Elevation_2m.tif') 

    geo_bounds=ponds_dem.extents # [550000,560000,4.14e6,4.14e6+10e3]
    dem=field.GdalGrid(fn,geo_bounds=geo_bounds)
else:
    dem=field.GdalGrid('tiles_2m_20170508/merged_2m.tif',geo_bounds=zoom)


## 

plt.figure(1).clf()
fig,ax=plt.subplots(num=1)
img=dem.plot(interpolation='nearest',vmin=-5,vmax=3,aspect='auto')
ax.axis('equal')
plt.colorbar(img)

## 

# What are some pixel values which are very common?
# first bin by cm, in the range that could be filled in
min_val=-0.5 # ignore flat areas below this elevation
max_val=2.0  # ignore flat areas above this elevation
min_feat_area=10000 # ignore flat areas smaller than this (m^2)
#  4000 grabbed a few questionable spots..
bottom_bin_width=1e-6

## 
feat_size_thresh=min_feat_area/(dem.dx*dem.dy) # min size in pixels
values_to_test=[]

bin_count=100

F=dem.F.copy() # copy so we can nan stuff out.

## 
def mark_range(bin_low,bin_high):
    """
    nan out contiguous areas in F which fall within the given range,
    and satisfy the feature area requirement.
    alters F, from above
    """
    in_bin= (dem.F>=bin_low)&(dem.F<=bin_high) 

    marks=field.SimpleGrid( F=in_bin,
                            extents=dem.extents)

    # find contiguous areas of this value:
    label,num_features=ndi.label(marks.F)

    labels=field.SimpleGrid(F=label,extents=dem.extents)

    feat_sizes=np.bincount(labels.F.ravel())

    # Good features
    success=False

    for feat_i,feat_size in enumerate(feat_sizes):
        if feat_i==0:
            continue
        if feat_size > feat_size_thresh:
            success=True
            sel=(labels.F==feat_i)
            # mask[ sel ] = True
            F[sel] = np.nan

    return success

def test_recursive(min_val,max_val):
    """
    scan F for value within the given range which occur
    a lot, i.e. probably a constant-value fill.

    if it finds a reasonable feature, nan it out and return True.
    otherwise return False.
    """
    bins=np.linspace(min_val,max_val,bin_count+1)
    
    valid=np.isfinite(F)
    hist,_=np.histogram(F[valid],bins=bins)

    # will have to play around to get a good criterion, for
    # the moment choose the largest bin
    sel_bin=np.argmax(hist)

    bin_low,bin_high=bins[sel_bin:sel_bin+2]

    in_bin= (dem.F>=bin_low) &(dem.F<=bin_high) 

    if np.sum(in_bin)<feat_size_thresh:
        return False

    assert bottom_bin_width>0 # may someday allow bin width of 0

    if bin_high-bin_low<=bottom_bin_width:
        print "Found good value: %.6f -- %.6f"%(bin_low,bin_high)
        return mark_range(bin_low,bin_high)
    else:
        return test_recursive(bin_low,bin_high)

    # # not right, just stowing some code here.
    # mr=scipy.stats.mode(dem.F[in_bin]) # slow!
    # bin_high=bin_low=mr.mode[0]


# This is pretty slow --     
while test_recursive(min_val,max_val):
    pass

## 

out=field.SimpleGrid(F=F,extents=dem.extents)

plt.figure(2).clf()
fig,ax=plt.subplots(num=2)
out.plot(ax=ax,interpolation='nearest',vmin=-2,vmax=4)

fig.set_size_inches((6,8),forward=True)
ax.xaxis.set_visible(0)
ax.yaxis.set_visible(0)
fig.tight_layout()

fig.savefig('remove_flat_ponds-v00.png')
## 

out.write_gdal('../sources/usgs_2m_remove_flat_ponds_v00.tif')

# -0.37 might not have been a good one...
# not sure about 1.13.
# the others look good.
