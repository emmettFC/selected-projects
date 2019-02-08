
'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: Subset social media data
        II: Subset by polygons
        III: Subset by annotaions
'''

# -- 
# dependancies

import csv
import pandas as pd
import numpy as np 
import pickle
from pprint import pprint

import json 
import geojson
import matplotlib.pyplot as plt 
from descartes import PolygonPatch
from shapely.geometry import shape, Point

from matplotlib.path import Path
import matplotlib.patches as patches

import sqlite3


# -- 
# io

data = [] 
excpt = [] 
with open('../data/angel_de.txt') as f:
    for line in f:
        try: 
            out = line.split(',')
            row = out[0:4]
            data.append(row)
        except:
            excpt.append(line)

with open("../data/beijing.geojson") as json_file:
    json_data = geojson.load(json_file)


# -- 
# user defined functions 

def subsetPoints(poly, df): 
    bounds = poly.bounds
    df.loc[(df['lat'] >= bounds[1]) & (df['lat'] <= bounds[3]) \
        & (df['lon'] >= bounds[0]) & (df['lon'] <= bounds[2])]
    return df

def getInPolyPoints(poly, df): 
    bounds = poly.bounds
    d = df.loc[(df['lat'] >= bounds[1]) & (df['lat'] <= bounds[3]) \
        & (df['lon'] >= bounds[0]) & (df['lon'] <= bounds[2])]
    d['labelInPoly'] = d.apply(lambda row: labelInPoly(row), axis=1)
    return d.loc[d['labelInPoly'] == 'in']

def labelInPoly(row): 
    point = Point(row['lon'], row['lat'])
    out = 'out'
    if poly.contains(point):
            out = 'in'
    return out


# -- 
# reduce columns to eliminate text data

wbDat = pd.DataFrame(data)
wbDat.columns = ['unID', 'lon', 'lat', 'timestamp']
wbDat.reset_index(inplace=True)


# -- 
# convert string lat lons to float

wbDat['lon'] = wbDat.apply(lambda row: np.float(row['lon']), axis=1)
wbDat['lat'] = wbDat.apply(lambda row: np.float(row['lat']), axis=1)


# -- 
# reduce weibo data to beijing geojson file

inpolys = [] 
i = 0 
for f in json_data['features']:
    print(i)
    i += 1
    poly = shape(f['geometry']) 
    polydf = getInPolyPoints(poly, wbDat)
    inpolys.append(polydf)

weibo_subset = pd.concat(inpolys)


# -- 
# identify all points inside the area with baidu labels (aproximatley 6th ring road)

con = sqlite3.connect('/Users/culhane/Downloads/google.db')
cursor = con.cursor()

cursor.execute("SELECT * FROM google_result;")
dat = cursor.fetchall() 
dfg = pd.DataFrame(dat)
dfpoints = dfg[[1, 2]]
dfpoints.columns = ['lon','lat']

maxLon, minLon = np.max(dfpoints['lon']), np.min(dfpoints['lon'])
maxLat, minLat = np.max(dfpoints['lat']), np.min(dfpoints['lat'])

wbSub = weibo_subset.loc[(weibo_subset['lon'] >= minLon) & (weibo_subset['lon'] <= maxLon)]
wbSub = wbSub.loc[(wbSub['lat'] >= minLat) & (wbSub['lat'] <= maxLat)]


# -- 
# make plot to show both regions and explain script

'''plot beijing geojson file'''
fig = plt.figure() 
feats = json_data['features']
for i in range(0, len(feats)): 
    try: 
        test = feats[i]
        poly = test['geometry']
        coords = poly['coordinates']
        x = [i for i,j in coords[0]]
        y = [j for i,j in coords[0]]
        ax = fig.gca() 
        # ax.plot(x,y)
        ax.plot(x, y, color='black')
        ax.axis('scaled')
    except: 
        print('failed to add polygon with index ' + str(i))

'''Plot all weibo points'''
xa, ya = wbDat[['lon']], wbDat[['lat']]
ax.scatter(xa, ya, color='red', s=0.02)

'''Plot rectangle of annotated region'''
verts = [(minLon, maxLat), (maxLon, maxLat), (maxLon, minLat), (minLon, minLat), (minLon, maxLat),]
codes = [Path.MOVETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         Path.CLOSEPOLY,
         ]

path = Path(verts, codes)
patch = patches.PathPatch(path, facecolor='none', lw=2)
ax.add_patch(patch)

'''Plot all annotations'''
xd, yd = dfpoints[['lon']], dfpoints[['lat']]
ax.scatter(xd, yd, color='blue', s=0.009)

'''Save and show plot of annotations, weibo and boundary'''
plt.savefig('../assets/weibo-baidu-scatter-beijing.png')
plt.show()


# -- 
# save out reduced data for segmentation and clustering

wbSub.to_csv('../data/inLabelRegionPoints.csv')
