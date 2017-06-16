"""
Importable field, for multiprocessing while producing tiles
"""
import numpy as np
from stompy.spatial import field
from stompy.spatial import interp_coverage

import os
opj=os.path.join

IDRIVE='/media/idrive'

class PointsInPoly(field.XYZField):
    """
    Test-driving a field which subsets a point dataset, and performs
    basic interpolation 
    """

def factory(attrs):
    geo_bounds=attrs['geom'].bounds

    if attrs['src_name']=='usgs_topobathy_2m':
        # A nice seamless 2m DEM from USGS.  A bit blurred, so maybe more like 4m resolution, but
        # still quite nice.
        fn=opj(IDRIVE,
               'BASELAYERS/Elevation_DerivedProducts/LiDAR 2005-2012 entire Bay Area from AECOM',
               'USGS_TopoBathy/San_Francisco_TopoBathy_Elevation_2m.tif') 
        return field.GdalGrid(fn,geo_bounds=geo_bounds)
    if attrs['src_name']=='usgs_topobathy_2m_remove_flat_ponds':
        # a postprocessing of a subset of the above, where broad areas of constant
        # elevation are removed.
        fn='../sources/usgs_2m_remove_flat_ponds_v00.tif'
        return field.GdalGrid(fn,geo_bounds=geo_bounds)
    if attrs['src_name']=='merged_ponds_25m':
        #fn='../../sbsprp/SbayPondBathy2005/merged_ponds.tif'
        fn='../sources/merged_ponds_2m_smoothed.tif'
        return field.GdalGrid(fn,geo_bounds=geo_bounds)
    if attrs['src_name']=='USGS Alviso 2010':
        # The 2010 data from USGS Open File Report 2011-1315, Amy Foxgrover et al Alviso data.
        fn='../../usgs/bathymetry/alviso_ofr2011_1315/2010/2010_DEM_UTM_NAVD88.tif'
        return field.GdalGrid(fn,geo_bounds=geo_bounds)
    if attrs['src_name']=='NOAA Sidescan SBB02_1m':
        # Recent NOAA sidescan for subtidal portions of LSB
        fn='../../noaa/bathy/sf_bay_sidescan/Area B -SSS Bathymetry/BAG/SBB02_1m.bag'
        dem=field.GdalGrid(fn,geo_bounds=geo_bounds)
        dem.F=dem.F[:,:,0] # Drop the second channel
        return dem
    if attrs['src_name']=='interp_lines':
        fn='../sources/interp_lines.tif'
        return field.GdalGrid(fn,geo_bounds=geo_bounds)
    if attrs['src_name']=='all_sloughs_061610':
        fn='../sources/all_sloughs_061610.tif'
        return field.GdalGrid(fn,geo_bounds=geo_bounds)
    if attrs['src_name']=='alviso_sections':
        fn='../sources/rma20170609/alviso_sections.tif'
        return field.GdalGrid(fn,geo_bounds=geo_bounds)
    if attrs['src_name']=='guadalupe_sections_remove_local_minima':
        fn='../sources/guadalupe_sections_remove_local_minima.tif'
        return field.GdalGrid(fn,geo_bounds=geo_bounds)
    if attrs['src_name'].startswith('py:'):
        expr=attrs['src_name'][3:]
        # something like 'ConstantField(-1.0)'
        # a little sneaky... make it look like it's running
        # after a "from stompy.spatial.field import *"
        # and also it gets fields of the shapefile
        field_hash=dict(field.__dict__)
        field_hash['PointsInPoly']=PointsInPoly
        # convert the attrs into a dict suitable for passing to eval
        attrs_dict={}
        for name in attrs.dtype.names:
            attrs_dict[name]=attrs[name]

        return eval(expr,field_hash,attrs_dict)
        
    assert False

src_shp='sources_v03.shp'

# mbf=field.MultiBlender(src_shp,factory=factory,buffer_field='buffer')
mbf=field.CompositeField(shp_fn=src_shp,
                         factory=factory,
                         priority_field='priority',
                         data_mode='data_mode',
                         alpha_mode='alpha_mode')
