'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: SOM clustering & find centroids 
        II: Voronoi polygon tesselation
'''

# -- 
# Dependancies 

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
# IO 

with open("./data/beijing.geojson") as json_file:
    json_data = geojson.load(json_file)

dfWB = pd.read_csv('./data/inLabelRegionPoints.csv')

# -- 
# Make corner frame
maxLon, minLon = np.max(dfWB['lon']), np.min(dfWB['lon'])
maxLat, minLat = np.max(dfWB['lat']), np.min(dfWB['lat'])
corners = [(minLon, maxLat), (maxLon, maxLat), (maxLon, minLat), (minLon, minLat)]
dfCorners = pd.DataFrame(corners)
dfCorners.columns = ['lon', 'lat']


# -- 
# Run SOM for optimal initialization given [p,q] [9,11] 

'''Calculated using standard deviation for DBI'''
'''Hardcode [p,q]'''
GRID_HEIGHT = 9
GRID_WIDTH = 11

'''Sample only 50 percent of dataframe for speed'''
wbDat = dfWB.sample(frac=0.50, replace=False)
wbArray = np.array(wbDat[['lon', 'lat']])
sofm = algorithms.SOFM(
    n_inputs=2,
    features_grid=(GRID_HEIGHT, GRID_WIDTH),
    verbose=True,
    shuffle_data=True,
    distance='euclid',
    learning_radius=2,
    reduce_radius_after=20,
    std=2,
    reduce_std_after=50,
    step=0.3,
    reduce_step_after=50,
)

'''this takes 5 minutes'''
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
    # - 

'''Make dataframe of centroids to join'''
dfcnt = pd.DataFrame(coords)


# -- 
# Use centroids to do voronoi tesselation

subset = dfcnt[['lon', 'lat']]
points = [tuple(x) for x in subset.values]
vPolys = pytess.voronoi(points)


# -- 
# Plot Voronoi polygons to evaluate result

plt.figure()
for i in range(len(vPolys)): 
    print(i)
    verts = vPolys[i][1]
    pList = [Point(i) for i in verts]
    poly = geometry.Polygon([[p.x, p.y] for p in pList])
    x,y = poly.exterior.xy
    plt.plot(x, y, color='#6699cc', alpha=0.7,
        linewidth=.8, solid_capstyle='round', zorder=2)

plt.show() 


# -- 
# Plot tesselation polygons over beijing polygons

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
        print('failed to add polygon with index ' + str(i))


for i in range(len(vPolys)): 
    print(i)
    verts = vPolys[i][1]
    pList = [Point(i) for i in verts]
    poly = geometry.Polygon([[p.x, p.y] for p in pList])
    x,y = poly.exterior.xy
    ax.plot(x, y, color='black', alpha=0.7,# color='#6699cc', alpha=0.7,
        linewidth=1.25, solid_capstyle='round', zorder=2)


'''include boundary points via labeled data'''
ax.scatter(dfCorners['lon'], dfCorners['lat'], color='red', s=10)

'''include scatter of weibo points'''
ax.scatter(*wbArray.T, color='blue', s=0.01)

'''include plot of centroids'''
ax.scatter(dfcnt['lon'], dfcnt['lat'], color='red', s=10)

'''Limit axis to focus region'''
ax.set_xlim(maxLon, minLon)
ax.set_ylim(maxLat, minLat)

'''reveal plot'''
plt.show() 

'''Save polygons'''
dfPoly = pd.DataFrame(vPolys) 
# dfPoly.to_csv('./data/voronoi-polygons-9-11-npDefaults.csv')


# -- 
# Limit polygons to finite polygons 

'''Include only polygons with verticies inside rectangular region'''
'''http://zderadicka.eu/voronoi-diagrams/'''

region = dfCorners[['lon', 'lat']]
bounds = [tuple(x) for x in region.values]
ps = [Point(i) for i in bounds]
boundary = geometry.Polygon([[p.x, p.y] for p in ps])

'''Get finite polygons using boundary rectangle'''
finite_polygons = []
for i in range(len(vPolys)): 
    print(i)
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
        print('found finite voronoi polygon')
        poly = geometry.Polygon([[p.x, p.y] for p in pList])
        finite_polygons.append((cent, poly))
    elif val == 'out': 
        print('found infinite polygon: excluding from spatial domain')


'''Save polygons'''
def getCoords(r): 
    crds = mapping(r[1])
    crds = crds['coordinates']
    return (r[0], list(crds[0]))


polygons = [getCoords(i) for i in finite_polygons]
dfPolygon = pd.DataFrame(polygons) 
dfPolygon.to_csv('./data/voronoi-polygons-9-11-npd-finite-only.csv')


# -- 
# Label the polygons and assign cluster ID to weibo data 

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


'''Prepare frames'''
dfPolygon.columns = ['center', 'polygon']
dfPolygon.reset_index(inplace=True)
dfPolygon.columns = ['polygonID', 'center', 'polygon']

'''Label polygons'''
dfTemp = dfWB
inpolys = []
for p in range(len(dfPolygon)):
    print(p)
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


'''Concatenate and write out weibo data with polygon labels'''
inPoly = pd.concat(inpolys)
inPoly.to_csv('./data/weibo-dat-with-polygon-labels.csv')


# -- 
# Plot trial tesselation for Nuepy Defaults (9, 11) == [p, q]

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
        print('failed to add polygon with index ' + str(i))

'''List finite polygon IDs'''
ids = inPoly.label.unique()

for i in range(len(vPolys)): 
    print(i)
    if i in ids: 
        verts = vPolys[i][1]
        pList = [Point(i) for i in verts]
        poly = geometry.Polygon([[p.x, p.y] for p in pList])
        x,y = poly.exterior.xy
        ax.plot(x, y, color='black', alpha=0.7,# color='#6699cc', alpha=0.7,
            linewidth=1.25, solid_capstyle='round', zorder=2)
    else: 
        print('incomplete polygon: excluding from plot')

'''include boundary points via labeled data'''
ax.scatter(dfCorners['lon'], dfCorners['lat'], color='red', s=10)

'''include scatter of weibo points'''
ax.scatter(*wbArray.T, color='blue', s=0.01)

'''include plot of centroids'''
ax.scatter(dfcnt['lon'], dfcnt['lat'], color='red', s=10)

'''Limit axis to focus region'''
ax.set_xlim(maxLon, minLon)
ax.set_ylim(maxLat, minLat)

'''reveal plot'''
plt.show() 






