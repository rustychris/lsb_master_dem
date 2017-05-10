# lsb_master_dem
Scripts for generating Lower South Bay, San Francisco Bay, composite DEM

The scripts merge topography and bathymetry data from a range of sources, notably:
  1. USGS 2m seamless topobathy of the Bay
  2. Manually interpolated slough cross-sections (Ed Gross, Rusty Holleman)
  3. A small number of manually inserted levees breaches
  4. USGS Alviso Slough data
  5. NOAA Multibeam surveys of subtidal areas.
  
 The resulting 2m, stitched dataset is available via 
 <a href="http://sfbaynutrients.sfei.org/erddap/griddap/bathy_sfei_lsb_v001.graph">SFEI ERDDAP</a>
 
<img src="docs/bathy_sfei_lsb_v001.png"/>
