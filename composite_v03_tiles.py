from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
from stompy.spatial import field

import os
opj=os.path.join

from composite_field_v03 import mbf

def fill_holes(dem):
    dem.fill_by_convolution(iterations='adaptive',smoothing=2,kernel_size=7)

def f(args):
    fn,xxyy,res = args

    bleed=150 # pad out the tile by this much to avoid edge effects

    # # temporary code to set projection info:
    # if os.path.exists(fn):
    #     dem=field.GdalGrid(fn)
    #     if dem.projection() == '':
    #         dem.assign_projection('EPSG:26910')
    #         os.unlink(fn)
    #         dem.write_gdal(fn)

    if True: # DBG not os.path.exists(fn):
        try:
            xxyy_pad=[ xxyy[0]-bleed,
                       xxyy[1]+bleed,
                       xxyy[2]-bleed,
                       xxyy[3]+bleed ]
            dem=mbf.to_grid(dx=res,dy=res,bounds=xxyy_pad)
            # not great, since we're not padding the borders, but
            # there is very little filling now that the 2m dataset
            # is so pervasive.
            fill_holes(dem)

            if bleed!=0:
                dem=dem.crop(xxyy)
            dem.write_gdal(fn)
        except Exception as exc:
            print "Failed with exception"
            print repr(exc)

if __name__ == '__main__':
    dem_dir="tiles_2m_20171024"
    os.path.exists(dem_dir) or os.mkdir(dem_dir)

    res=2.0
    total_bounds=[576000., 596000., 4137000., 4153000.]
    tile_x=tile_y=1000.0
    
    total_bounds[0] = np.floor(total_bounds[0]/tile_x) * tile_x
    total_bounds[1] = np.ceil(total_bounds[1]/tile_x) * tile_x
    total_bounds[2] = np.floor(total_bounds[2]/tile_y) * tile_y
    total_bounds[3] = np.ceil(total_bounds[3]/tile_y) * tile_y

    calls=[]
    for x0 in np.arange(total_bounds[0],total_bounds[1],tile_x):
        for y0 in np.arange(total_bounds[2],total_bounds[3],tile_y):
            xxyy=(x0,x0+tile_x,y0,y0+tile_y)
            fn=os.path.join(dem_dir,"%.0f_%.0f.tif"%(x0,y0))
            calls.append( [fn,xxyy,res] )

    if 0: 
        p = Pool(4)
        p.map(f, calls )
    else:
        [f(call) for call in calls]

