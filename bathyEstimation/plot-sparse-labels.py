
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
# Plot the labels to show distribution

plt.figure(figsize=(10,5))
plt.scatter(df.x, df.y, s=1, marker = ".")
plt.xlim(np.min(df.x.values), np.max(df.x.values))
plt.ylim(np.min(df.y.values), np.max(df.y.values))
# plt.xticks(np.arange(-1.5, 1.6, 0.1))
# plt.yticks(np.arange(0, 2.1, 0.1))
plt.grid(True)
plt.show()


# -- 
# Kernel density

lat = df.y.values
lon = df.x.values
ax = sns.kdeplot(lat, lon, cmap="Blues", shade=True, shade_lowest=False)

plt.show() 





