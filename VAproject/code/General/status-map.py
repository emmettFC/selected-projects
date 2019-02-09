'''
    Build status Basemap for client reporting: 
'''

# -- 
# Dependancies

import numpy as np
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt 
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.colors import rgb2hex
from matplotlib.patches import Polygon
import urllib3
from threading import Thread
import time
from elasticsearch import Elasticsearch
import elasticsearch.helpers
from elasticsearch.helpers import scan, streaming_bulk
import json
import pandas as pd
from matplotlib.colors import rgb2hex, Normalize
from matplotlib.patches import Polygon
from matplotlib.colorbar import ColorbarBase


# -- 
# Basemap projection

fig, ax = plt.subplots()
# Lambert Conformal map of lower 48 states.
m = Basemap(llcrnrlon=-119,llcrnrlat=20,urcrnrlon=-64,urcrnrlat=49,
            projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
# Mercator projection, for Alaska and Hawaii
m_ = Basemap(llcrnrlon=-190,llcrnrlat=20,urcrnrlon=-143,urcrnrlat=46,
            projection='merc',lat_ts=20)  # do not change these numbers


# -- 
# Draw boundaries 

shp_info = m.readshapefile('/Users/culhane/VAProject/data/st99_d00/st99_d00','states',drawbounds=True,
                           linewidth=0.45,color='gray')
shp_info_ = m_.readshapefile('/Users/culhane/VAProject/data/st99_d00/st99_d00','states',drawbounds=False)


# -- 
# List of found offenders by state
 
popdensity = {
'New Jersey':  0,
'Rhode Island':   0,
'Massachusetts':   0,
'Connecticut':    0,
'Maryland':   0,
'New York':    16700,
'Delaware':    0,
'Florida':     69356,
'Ohio':  0,
'Pennsylvania':  28436,
'Illinois':    0,
'California':  55000,
'Hawaii':  0,
'Virginia':    0,
'Michigan':    0,
'Indiana':    0,
'North Carolina':  0,
'Georgia':     0,
'Tennessee':   0,
'New Hampshire':   0,
'South Carolina':  0,
'Louisiana':   0,
'Kentucky':   0,
'Wisconsin':  0,
'Washington':  0,
'Alabama':     0,
'Missouri':    0,
'Texas':   55000,
'West Virginia':   0,
'Vermont':     0,
'Minnesota':  0,
'Mississippi':   0,
'Iowa':  0,
'Arkansas':    0,
'Oklahoma':    0,
'Arizona':     0,
'Colorado':    0,
'Maine':  0,
'Oregon':  0,
'Kansas':  0,
'Utah':  0,
'Nebraska':    0,
'Nevada':  0,
'Idaho':   0,
'New Mexico':  0,
'South Dakota':  0,
'North Dakota':  0,
'Montana':     0,
'Wyoming':      0,
'Alaska':     4500}


# -- 
# Assign Colors based on offender population 

colors={}
statenames=[]
cmap = plt.cm.Blues

vmin = 0; vmax = 100000
norm = Normalize(vmin=vmin, vmax=vmax)
for shapedict in m.states_info:
    statename = shapedict['NAME']
    # skip DC and Puerto Rico.
    if statename not in ['District of Columbia','Puerto Rico']:
        pop = popdensity[statename]
        # calling colormap with value between 0 and 1 returns
        # rgba value.  Invert color range (hot colors are high
        # population), take sqrt root to spread out colors more.
        colors[statename] = cmap(np.sqrt((pop-vmin)/(vmax-vmin)))[:3]
    statenames.append(statename)

# -- 
# Assign colors based on dictionary and cmap range

for nshape,seg in enumerate(m.states):
    # skip DC and Puerto Rico.
    if statenames[nshape] not in ['Puerto Rico', 'District of Columbia']:
        color = rgb2hex(colors[statenames[nshape]])
        poly = Polygon(seg,facecolor=color,edgecolor=color)
        ax.add_patch(poly)

AREA_1 = 0.005  # exclude small Hawaiian islands that are smaller than AREA_1
AREA_2 = AREA_1 * 30.0  # exclude Alaskan islands that are smaller than AREA_2
AK_SCALE = 0.19  # scale down Alaska to show as a map inset
HI_OFFSET_X = -1900000  # X coordinate offset amount to move Hawaii "beneath" Texas
HI_OFFSET_Y = 250000    # similar to above: Y offset for Hawaii
AK_OFFSET_X = -250000   # X offset for Alaska (These four values are obtained
AK_OFFSET_Y = -750000   # via manual trial and error, thus changing them is not recommended.)

for nshape, shapedict in enumerate(m_.states_info):  # plot Alaska and Hawaii as map insets
    if shapedict['NAME'] in ['Alaska', 'Hawaii']:
        seg = m_.states[int(shapedict['SHAPENUM'] - 1)]
        if shapedict['NAME'] == 'Hawaii' and float(shapedict['AREA']) > AREA_1:
            seg = [(x + HI_OFFSET_X, y + HI_OFFSET_Y) for x, y in seg]
            color = rgb2hex(colors[statenames[nshape]])
        elif shapedict['NAME'] == 'Alaska' and float(shapedict['AREA']) > AREA_2:
            seg = [(x*AK_SCALE + AK_OFFSET_X, y*AK_SCALE + AK_OFFSET_Y)\
                   for x, y in seg]
            color = rgb2hex(colors[statenames[nshape]])
        poly = Polygon(seg, facecolor=color, edgecolor='gray', linewidth=.45)
        ax.add_patch(poly)

ax.set_title('Sex Offender Data Collection: Progress & Density')

# -- 
# Bounding boxes for non lower 48

light_gray = [0.8]*3  # define light gray color RGB
x1,y1 = m_([-190,-183,-180,-180,-175,-171,-171],[29,29,26,26,26,22,20])
x2,y2 = m_([-180,-180,-177],[26,23,20])  # these numbers are fine-tuned manually
m_.plot(x1,y1,color=light_gray,linewidth=0.8)  # do not change them drastically
m_.plot(x2,y2,color=light_gray,linewidth=0.8)


# -- 
# Add colorbar ledger and show plot

ax_c = fig.add_axes([0.9, 0.1, 0.03, 0.8])
cb = ColorbarBase(ax_c,cmap=cmap,norm=norm,orientation='vertical',
                  label=r'[population per $\mathregular{km^2}$]')


plotfile = '/Users/culhane/VAProject/admin/jan22-states-progress-map.png'
plt.savefig(plotfile)
plt.show()















