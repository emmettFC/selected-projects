'''
    Plot coverage of raster data against the max/min region of the labeled points
'''

# -- 
# Dependancies 

import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt 
import seaborn as sns
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.patches import Polygon

import pandas as pd 
import numpy as np 
import gdal
from osgeo import ogr
from osgeo import osr

# -- 
# IO 

df = pd.read_csv('./data/bart-ground-truth/cleaneddepths.csv') # BD depth readings

filepath = './data/reproject.tif' # Reprojected tif of raster WV2 data 
raster = gdal.Open(filepath)


# -- 
# Build raster window 

ulx, xres, xskew, uly, yskew, yres  = raster.GetGeoTransform() # corner points raster file
lrx = ulx + (raster.RasterXSize * xres)
lry = uly + (raster.RasterYSize * yres)


# -- 
# Build BD readings coverage window

xgrid = np.arange(np.min(df.x.values), np.max(df.x.values), xres * 100)
ygrid = np.arange(np.min(df.y.values), np.max(df.y.values), xres * 100)

x = xgrid.tolist() 
y = ygrid.tolist() 
y.reverse() 

listPoints = [] 
for val in x: 
    for r in y: 
        point = (r, val)
        listPoints.append(point)

latsBD = [i[0] for i in listPoints]
lonsBD = [i[1] for i in listPoints]

del xgrid, ygrid, listPoints, x, y


# --
# Plot coverage region over raster region and scatter readings

map = Basemap(projection='merc', lat_0 = 57, lon_0 = -135,
    resolution = 'h', area_thresh=.0000001,
    llcrnrlon=-88.55, llcrnrlat=16.3,
    urcrnrlon=-88, urcrnrlat=17.1)


map.drawcoastlines()
map.drawcountries()
map.drawmapboundary()


# -- 
# Plot the raster coverage 

x1,y1 = map(ulx,lry)
x2,y2 = map(ulx,uly)
x3,y3 = map(lrx,uly)
x4,y4 = map(lrx,lry)
poly = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)],facecolor='red',edgecolor='green',linewidth=3)
plt.gca().add_patch(poly)


# -- 
# Plot the labeled region

minx, maxx, miny, maxy = (np.min(df.x.values), np.max(df.x.values), np.min(df.y.values), np.max(df.y.values))
x1,y1 = map(minx,miny)
x2,y2 = map(minx,maxy)
x3,y3 = map(maxx,maxy)
x4,y4 = map(maxx, miny)
poly = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)],edgecolor='black',linewidth=3)
plt.gca().add_patch(poly)


# -- 
# View the plot

plt.show()


