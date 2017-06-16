from __future__ import print_function
import matplotlib.pyplot as plt

from stompy.spatial import field
from stompy.plot import plot_utils, plot_wkb

import composite_field_v03

## 
reload(composite_field_v03)

## 


from shapely import geometry

class CompositeField(field.Field):
    """ 
    In the same vein as BlenderField, but following the model of raster
    editors like Photoshop or the Gimp.

    Individual sources are treated as an ordered "stack" of layers.
    
    Layers higher on the stack can overwrite the data provided by layers
    lower on the stack.

    A layer is typically defined by a raster data source and a polygon over
    which it is valid.  

    Each layer's contribution to the final dataset is both a data value and
    an alpha value.  This allows for blending/feathering between layers.

    The default "data_mode" is simply overlay.  Other data modes like "min" or 
    "max" are possible.  

    The default "alpha_mode" is "valid()" which is essentially opaque where there's
    valid data, and transparent where there isn't.  A second common option would 
    probably be "feather(<distance>)", which would take the valid areas of the layer,
    and feather <distance> in from the edges.

    The sources, data_mode, alpha_mode details are taken from a shapefile.

    Alternatively, if a factory is given, it should be callable and will take a single argument -
    a dict with the attributse for each source.  The factory should then return the corresponding
    Field.
    """
    def __init__(self,shp_fn=None,factory=None,
                 priority_field='priority',
                 data_mode='data_mode',
                 alpha_mode='alpha_mode',
                 shp_data=None):
        self.shp_fn = shp_fn
        if shp_fn is not None: # read from shapefile
            self.sources=wkb2shp.shp2geom(shp_fn)
        else:
            self.sources=shp_data

        if data_mode is not None:
            self.data_mode=self.sources[data_mode]
        else:
            self.data_mode=['overlay()']*len(self.sources)

        if alpha_mode is not None:
            self.alpha_mode=self.sources[alpha_mode]
        else:
            self.data_mode=['valid()']*len(self.sources)

        # Impose default values on those:
        for i in range(len(self.sources)):
            if self.alpha_mode[i]=='':
                self.alpha_mode[i]='valid()'
            if self.data_mode[i]=='':
                self.data_mode[i]='overlay()'

        super(CompositeField,self).__init__()

        self.factory = factory

        self.delegate_list=[None]*len(self.sources)

        self.src_priority=self.sources[priority_field]
        self.priorities=np.unique(self.src_priority)

    def bounds(self):
        raise Exception("For now, you have to specify the bounds when gridding a BlenderField")

    def load_source(self,i):
        if self.delegate_list[i] is None:
            self.delegate_list[i] = self.factory( self.sources[i] )
        return self.delegate_list[i]

    def to_grid(self,nx=None,ny=None,bounds=None,dx=None,dy=None):
        """ render the layers to a SimpleGrid tile.
        """
        # boil the arguments down to dimensions
        if bounds is None:
            xmin,xmax,ymin,ymax = self.bounds()
        else:
            if len(bounds) == 2:
                xmin,ymin = bounds[0]
                xmax,ymax = bounds[1]
            else:
                xmin,xmax,ymin,ymax = bounds
        if nx is None:
            nx=1+int(np.round((xmax-xmin)/dx))
            ny=1+int(np.round((ymax-ymin)/dy))

        # allocate the blank starting canvas
        result_F =np.ones((ny,nx),'f8')
        result_F[:]=-999
        result_data=field.SimpleGrid(extents=bounds,F=result_F)
        result_alpha=result_data.copy()
        result_alpha.F[:]=0.0

        # Which sources to use, and in what order?
        box=geometry.box(bounds[0],bounds[2],bounds[1],bounds[3])

        # Which sources are relevant?
        relevant_srcs=np.nonzero( [ box.intersects(geom)  
                                    for geom in self.sources['geom'] ])[0]
        # omit negative priorities
        relevant_srcs=relevant_srcs[ self.src_priority[relevant_srcs]>=0 ]

        # Starts with lowest, goes to highest
        order = np.argsort(self.src_priority[relevant_srcs])
        ordered_srcs=relevant_srcs[order]

        for src_i in ordered_srcs:
            print self.sources['src_name'][src_i]
            print "   data mode: %s  alpha mode: %s"%(self.data_mode[src_i],
                                                      self.alpha_mode[src_i])

            source=self.load_source(src_i)
            src_data = source.to_grid(bounds=bounds,dx=dx,dy=dy)
            src_alpha= field.SimpleGrid(extents=src_data.extents,
                                        F=np.ones(src_data.F.shape,'f8'))

            if 0: # slower
                src_alpha.mask_outside(self.sources['geom'][src_i],value=0.0)
            else: 
                mask=src_alpha.polygon_mask(self.sources['geom'][src_i])
                src_alpha.F[~mask] = 0.0

            # create an alpha tile. depending on alpha_mode, this may draw on the lower data,
            # the polygon and/or the data tile.
            # modify the data tile according to the data mode - so if the data mode is 
            # overlay, do nothing.  but if it's max, the resulting data tile is the max
            # of itself and the lower data.
            # composite the data tile, using its alpha to blend with lower data.

            # the various operations
            def min():
                """ new data will only decrease values
                """
                valid=result_alpha.F>0
                src_data.F[valid]=np.minimum( src_data.F[valid],result_data.F[valid] )
            def max():
                """ new data will only increase values
                """
                valid=result_alpha.F>0
                src_data.F[valid]=np.maximum( src_data.F[valid],result_data.F[valid] )
            def fill(dist):
                "fill in small missing areas"
                pixels=int(round(float(dist)/dx))
                niters=np.maximum( pixels//3, 2 )
                src_data.fill_by_convolution(iterations=niters)
            def overlay():
                pass 
            # alpha channel operations:
            def valid():
                # updates alpha channel to be zero where source data is missing.
                data_missing=np.isnan(src_data.F)
                src_alpha.F[data_missing]=0.0
            def gaussian(dist):
                "smooth with gaussian filter - this allows spreading beyond original poly!"
                pixels=int(round(float(dist)/dx))
                src_alpha.F=ndimage.gaussian_filter(src_alpha.F,pixels)
            def feather(dist):
                "linear feathering within original poly"
                pixels=int(round(float(dist)/dx))
                Fsoft=ndimage.distance_transform_bf(src_alpha.F)
                src_alpha.F = (Fsoft/pixels).clip(0,1)

            # dangerous! executing code from a shapefile!
            eval(self.data_mode[src_i])
            eval(self.alpha_mode[src_i])

            data_missing=np.isnan(src_data.F)
            src_alpha.F[data_missing]=0.0
            cleaned=src_data.F.copy()
            cleaned[data_missing]=-999 # avoid nan contamination.

            assert np.allclose( result_data.extents, src_data.extents )
            assert np.all( result_data.F.shape==src_data.F.shape )
            # before getting into fancy modes, just stack it all up:
            result_data.F   = result_data.F *(1-src_alpha.F) + cleaned*src_alpha.F
            result_alpha.F  = result_alpha.F*(1-src_alpha.F) + src_alpha.F

        # fudge it a bit, and allow semi-transparent data back out, but 
        # at least nan out the totally transparent stuff.
        result_data.F[ result_alpha.F==0 ] = np.nan
        return result_data

factory= composite_field_v03.factory

cf=CompositeField(shp_fn='sources_v03.shp',
                  factory=factory,
                  priority_field='priority',
                  data_mode='data_mode',
                  alpha_mode='alpha_mode')

bounds=[590000,591000,4142000,4143000]
dem=cf.to_grid(dx=2,dy=2,bounds=bounds)


## 

plt.figure(1).clf()
fig,ax=plt.subplots(num=1)

img=dem.plot(ax=ax,interpolation='nearest',vmin=-5,vmax=4)
plot_utils.cbar(img,ax=ax)

for src_i in range(len(cf.sources)):
    if cf.sources['priority'][src_i]<0:
        continue
    plot_wkb.plot_wkb( cf.sources['geom'][src_i], ax=ax, fc='none',ec='k',lw=0.5)

## 

# looking pretty good, about ready to scale it up...
# The test tile took 10.8s, with all the time in mask_outside.

# So far so good - last thing is to bring in the holey USGS 2m, so it can sit
# on top of the pond bathy.
