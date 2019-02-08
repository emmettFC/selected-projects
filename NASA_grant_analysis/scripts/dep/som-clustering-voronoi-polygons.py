'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: SOM clustering & find centroids 
        II: Voronoi polygon tesselation
        III: Going forward must edit source code module to allow haversine function
            - 2 arcsin(sqrt(sin^2(0.5*dx) + cos(x1)cos(x2)sin^2(0.5*dy)))
'''

# -- 
# dependancies 

import pandas as pd
import numpy as np
import json 
import geojson
import matplotlib.pyplot as plt 
plt.style.use('ggplot')

from pprint import pprint 
from dateutil import parser

import pytess
from shapely.geometry import shape, Point
from descartes import PolygonPatch

from shapely import geometry
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry import Polygon, mapping
from scipy.spatial import Voronoi, voronoi_plot_2d

from neupy import algorithms, environment
from utils import plot_2d_grid

environment.reproducible()


# --
# io 

with open("../data/beijing.geojson") as json_file:
    json_data = geojson.load(json_file)

df_weibo = pd.read_csv('../data/inLabelRegionPoints.csv')


# -- 
# user defined functions

def getCoords(r): 
    crds = mapping(r[1])
    crds = crds['coordinates']
    return (r[0], list(crds[0]))

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
# make corner frame

maxLon, minLon = np.max(dfWB['lon']), np.min(dfWB['lon'])
maxLat, minLat = np.max(dfWB['lat']), np.min(dfWB['lat'])
corners = [(minLon, maxLat), (maxLon, maxLat), (maxLon, minLat), (minLon, minLat)]
dfCorners = pd.DataFrame(corners)
dfCorners.columns = ['lon', 'lat']


# -- 
# run SOM for optimal initialization given [p,q] [9,11] 

GRID_HEIGHT = 9
GRID_WIDTH = 11

# -- 
# initialize som and create input array

wbArray = np.array(df_weibo[['lon', 'lat']])
sofm = algorithms.SOFM(
    n_inputs=2,
    features_grid=(GRID_HEIGHT, GRID_WIDTH),
    verbose=True,
    shuffle_data=True,
    distance='euclid',
    # distance='haversine',
    learning_radius=2,
    reduce_radius_after=20,
    std=2,
    reduce_std_after=50,
    step=0.3,
    reduce_step_after=50,
)

# -- 
# train model and build dataframe of centroids

sofm.train(wbArray, epochs=20)
preds = sofm.predict(wbArray)
dfp = pd.DataFrame(preds)
dfp['label'] = dfp.idxmax(axis=1)
dfp.reset_index(inplace=True)
npd34 = sofm.weight
npd34Lats, npd34Lons = npd34[1], npd34[0]

coords = [] 
for i in range(len(npd34Lats)): 
    lat, lon = npd34Lats[i], npd34Lons[i]
    out = {
        'lat' : lat, 
        'lon' : lon
    }
    coords.append(out)

dfcnt = pd.DataFrame(coords)


# -- 
# use centroids to do voronoi tesselation

subset = dfcnt[['lon', 'lat']]
points = [tuple(x) for x in subset.values]
vPolys = pytess.voronoi(points)


# -- 
# limit polygons to finite polygons within ROI rectangle (must improve method)

region = dfCorners[['lon', 'lat']]
bounds = [tuple(x) for x in region.values]
ps = [Point(i) for i in bounds]
boundary = geometry.Polygon([[p.x, p.y] for p in ps])

finite_polygons = []
for i in range(len(vPolys)): 
    verts = vPolys[i][1]
    cent = vPolys[i][0]
    pList = [Point(i) for i in verts]
    val = 'in'
    for v in pList: 
        if boundary.contains(v): 
            continue
        else: 
            val = 'out'
    if val == 'in': 
        poly = geometry.Polygon([[p.x, p.y] for p in pList])
        finite_polygons.append((cent, poly))
    elif val == 'out': 
        continue 



# -- 
# join centroids to polygon verticies & save to file

polygons = [getCoords(i) for i in finite_polygons]
dfPolygon = pd.DataFrame(polygons) 

dfPolygon.columns = ['center', 'polygon']
dfPolygon.reset_index(inplace=True)
dfPolygon.columns = ['polygonID', 'center', 'polygon']

dfTemp = dfWB
inpolys = []
for p in range(len(dfPolygon)):
    polyRow = dfPolygon.iloc[p]
    poly = polyRow['polygon']
    label = polyRow['polygonID']
    center = polyRow['center']
    poly = geometry.Polygon(poly)
    polypoints = getInPolyPoints(poly, dfTemp)
    polypoints['label'] = polypoints.apply(lambda row: label, axis=1)
    polypoints['center'] = polypoints.apply(lambda row: center, axis=1)
    polypoints['polygon'] = polypoints.apply(lambda row: poly, axis=1)
    dfTemp = dfTemp.iloc[~dfTemp.index.isin(polypoints.index.tolist())]
    inpolys.append(polypoints)

inPoly = pd.concat(inpolys)
inPoly.to_csv('../data/vtess-finite-npdefaults-9-11.csv')


# -- 
# plot trial tesselation for Nuepy Defaults (9, 11) == [p, q] for finite polygons

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
        ax.plot(x, y, color='black')
        ax.axis('scaled')
    except: 
        continue

'''list finite polygon IDs'''
ids = inPoly.label.unique()

for i in range(len(vPolys)): 
    if i in ids: 
        verts = vPolys[i][1]
        pList = [Point(i) for i in verts]
        poly = geometry.Polygon([[p.x, p.y] for p in pList])
        x,y = poly.exterior.xy
        ax.plot(x, y, color='black', alpha=0.7,# color='#6699cc', alpha=0.7,
            linewidth=1.25, solid_capstyle='round', zorder=2)
    else: 
        continue

'''include boundary points via labeled data'''
ax.scatter(dfCorners['lon'], dfCorners['lat'], color='red', s=10)

'''include scatter of weibo points'''
ax.scatter(*wbArray.T, color='blue', s=0.01)

'''include plot of centroids'''
ax.scatter(dfcnt['lon'], dfcnt['lat'], color='red', s=10)

'''limit axis to focus region'''
ax.set_xlim(maxLon, minLon)
ax.set_ylim(maxLat, minLat)

'''save plot'''
plt.savefig('../assets/vtess-finite-npdefaults-9-11.png')

'''reveal plot'''
plt.show() 

