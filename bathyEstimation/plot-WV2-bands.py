'''
    Read raster tif and plot bands: 
        I: WV2 2009 Satelite Raw
'''

# -- 
# Dependancies 
'''What you would likely run'''
from matplotlib import pyplot as plt
'''What I have to run because of disorganization'''
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt 
'''Generic'''
from osgeo import gdal 

# -- 
# Load tif into raster variable run from project/scripts directory
filepath = '../data/test-convert.tif'
raster = gdal.Open(filepath)

# -- 
# Plot bands along 2 by 4 subplot matrix
fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(16,16))
counter = 1
for ax in axes.flat:
    ax.set_title('WV2 Raster Basemap: Band ' + str(counter))
    # - specify band / make array / plot
    band = raster.GetRasterBand(counter)
    img = band.ReadAsArray() 
    im = ax.imshow(img, interpolation='nearest', vmin=0, cmap=plt.cm.terrain)
    counter += 1

# -- 
# Add colorbar and save plot to project/figures 
fig.colorbar(im, ax=axes.ravel().tolist())
plotfile= '../figures/wv2-all-bands-separated.png'
plt.savefig(plotfile)
plt.close('all')