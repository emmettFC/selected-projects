
'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: Subset social media data
        II: Subset by polygons
        III: Subset by annotaions
'''

# -- 
# Dependancies

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
# Load file line by line (1,785,565)

data = [] 
excpt = [] 
with open('./data/angel_de.txt') as f:
    for line in f:
        try: 
            out = line.split(',')
            row = out[0:4]
            data.append(row)
        except:
            excpt.append(line)


# -- 
# Reduce columns to eliminate text data

wbDat = pd.DataFrame(data)
wbDat.columns = ['unID', 'lon', 'lat', 'timestamp']
wbDat.reset_index(inplace=True)

'''Convert string lat lons to float'''
wbDat['lon'] = wbDat.apply(lambda row: np.float(row['lon']), axis=1)
wbDat['lat'] = wbDat.apply(lambda row: np.float(row['lat']), axis=1)

# -- 
# Reduce points to polygons 

'''Load geojson file'''

with open("./data/beijing.geojson") as json_file:
    json_data = geojson.load(json_file)


'''Define functions to reduce data'''

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


'''Run function and reduce points to polygons: 171,507'''

inpolys = [] 
i = 0 
for f in json_data['features']:
    print(i)
    i += 1
    poly = shape(f['geometry']) 
    polydf = getInPolyPoints(poly, wbDat)
    inpolys.append(polydf)

weibo_subset = pd.concat(inpolys)
# wbDat.to_csv('./data/inPolyPoints.csv')


# -- 
# Limit points to region with labels via udit DB's

'''Load sqlite db'''
con = sqlite3.connect('./data/google.db')
cursor = con.cursor()

cursor.execute("SELECT * FROM google_result;")
dat = cursor.fetchall() 
dfg = pd.DataFrame(dat)
dfpoints = dfg[[1, 2]]
df = dfpoints.sample(frac=0.4, replace=False)
df.columns = ['lon','lat']

'''Write out labels for future ground truth expr'''
# df.to_csv('./inPolyLabels.csv', encoding = 'utf-8')

'''Get bounds of region with annotations: 164,639'''
maxLon = np.max(df['lon'])
minLon = np.min(df['lon'])
maxLat, minLat = np.max(df['lat']), np.min(df['lat'])

wbSub = weibo_subset.loc[(weibo_subset['lon'] >= minLon) & (weibo_subset['lon'] <= maxLon)]
wbSub = wbSub.loc[(wbSub['lat'] >= minLat) & (wbSub['lat'] <= maxLat)]

'''Plot subset of weibo points'''
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

'''Plot all labels: Sanity check labeled region'''
xd, yd = wbSub[['lon']], wbSub[['lat']]
ax.scatter(xd, yd, color='red', s=0.1)
plt.show() 


'''Plot labels from google db'''
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

'''Plot all labels: Sanity check labeled region'''
xd, yd = df[['lon']], df[['lat']]
ax.scatter(xd, yd, color='red', s=0.1)
plt.show() 


# -- 
# Make plot to show both regions and explain script

'''Plot polygon boundaries'''
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
xd, yd = df[['lon']], df[['lat']]
ax.scatter(xd, yd, color='blue', s=0.009)

'''Show plot of annotations, weibo and boundary'''
plt.show()


# -- 
# Save out reduced data for segmentation and clustering

'''Write out in-label region points to csv'''
wbSub.to_csv('./data/inLabelRegionPoints.csv')
