from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
from stompy.spatial import field

import os
opj=os.path.join

from stompy.spatial import interp_coverage
import composite_field_v01 

from composite_field_v01 import mbf



def f(args):
    fn,xxyy,res = args
    if not os.path.exists(fn):
        try:
            mbf.to_grid(dx=res,dy=res,bounds=xxyy).write_gdal(fn)
        except Exception as exc:
            print "Failed with exception"
            print exc

if __name__ == '__main__':
    dem_dir="tiles_2m_20170508"
    os.path.exists(dem_dir) or os.mkdir(dem_dir)

    res=2.0
    total_bounds=[576000., 596000., 4137000., 4152000.]
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

    p = Pool(4)
    p.map(f, calls )

