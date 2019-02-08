
'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: SOM clustering to determine initilizing grid params with DBI index
'''

# -- 
# dependancies 

import pandas as pd
import numpy as np
import json 
import geojson
import matplotlib.pyplot as plt 
from descartes import PolygonPatch
from pprint import pprint 

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import datasets
from neupy import algorithms, environment

import pandas as pd 
from sklearn.cluster import k_means
from scipy.spatial import distance

from utils import plot_2d_grid
plt.style.use('ggplot')
environment.reproducible()

pd.set_option('display.expand_frame_repr', False)

from datetime import timedelta


# -- 
# io 

with open("./data/beijing.geojson") as json_file:
    json_data = geojson.load(json_file)

dfWB = pd.read_csv('./data/inLabelRegionPoints.csv')


# -- 
# user defined functions

def factors(x):
    result = []
    i = 1
    while i*i <= x:
        if x % i == 0:
            result.append(i)
            if x/i != i:
                result.append(x/i)
        i += 1
    return result

def makePQs(fs): 
    pqs = []
    # f = facts[0]
    ind = len(fs)
    if ind % 2 != 0:
        sq = fs[ind - 1]
        pqs.append((sq, sq))
        fs = fs[:-1]
        ind = ind -1
    i = 0
    while i < ind: 
        pair = (fs[i], fs[i+1])
        i += 2
        # print(pair)
        pqs.append(pair)
    return pqs

def validFacts(row): 
    dif = abs(row['f1'] - row['f2'])
    rat = np.max((row['f1'], row['f2'])) / float(dif)
    if rat < 2: 
        out = False 
    else: 
        out = True
    return out

def makePq(row, ind):
    if ind == 'p':  
        out = np.min((row['f1'], row['f2']))
    elif ind == 'q':
        out = np.max((row['f1'], row['f2']))
    return out

def makePq(row, ind):
    if ind == 'p':  
        out = np.min((row['f1'], row['f2']))
    elif ind == 'q':
        out = np.max((row['f1'], row['f2']))
    return out

def getDist(row): 
    p1 = (row['latp'], row['lonp']) 
    p2 = (row['lat'], row['lon']) 
    dst = distance.euclidean(p1, p2)
    return dst

def getDBIstd(grid_size, dfWB):
    GRID_HEIGHT = grid_size['p']
    GRID_WIDTH = grid_size['q']
    wbDat = dfWB.sample(frac=0.10, replace=False)
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
    dfcnt = pd.DataFrame(coords)
    dfcnt.reset_index(inplace=True)
    dfcnt.columns = ['label', 'lat', 'lon']
    dflab = pd.merge(dfp, dfcnt, on='label', how='outer')
    wbdf = pd.DataFrame(wbArray, columns=['lonp', 'latp'])
    wbdf.reset_index(inplace=True)
    dfDB = pd.merge(dflab, wbdf, on='index', how='outer')
    dfDB['euclidean_dist'] = dfDB.apply(lambda row: getDist(row), axis=1)
    average_distance = dfDB.groupby('label').agg({'euclidean_dist' : np.std})
    average_distance.reset_index(inplace=True)
    dbframe = pd.merge(average_distance, dfcnt, on='label', how='outer')
    Ri = []
    for i in range(len(dbframe)): 
        Rij = [] 
        cnt = dbframe.iloc[i]
        p1 = (cnt['lat'], cnt['lon']) 
        mean_dist = cnt['euclidean_dist']
        for j in range(len(dbframe)): 
            if j != i: 
                cnt2 = dbframe.iloc[j]
                p2 = (cnt2['lat'], cnt2['lon'])
                mean_dist2 = cnt2['euclidean_dist']
                r = (mean_dist + mean_dist2) / distance.euclidean(p1, p2)
                Rij.append(r)
                # - 
        Ri.append(max(Rij))
        # - 
    print('found dbi for grid_size')
    dbi = np.mean(Ri)
    return dbi


# -- 
# get hueristic for general shape of intitializing grid

maxLon, minLon = np.max(dfWB['lon']), np.min(dfWB['lon'])
maxLat, minLat = np.max(dfWB['lat']), np.min(dfWB['lat'])

corners = [(minLon, maxLat), (maxLon, maxLat), (maxLon, minLat), (minLon, minLat)]
dfCorners = pd.DataFrame(corners)
dfCorners.columns = ['lon', 'lat']
plt.scatter(dfCorners['lon'], dfCorners['lat'])
plt.show()

width = maxLon - minLon
height = maxLat - minLat
ratio = np.float(height) /np.float(width)


# -- 
# get factors of all desired grid sizes

N = []
for i in range(10, 101): 
    N.append(i)

facts = [factors(i) for i in N]

# --
# make pairs of valid factors based on N

pQs = []
for i in range(len(facts)): 
    print(i)
    pQs.extend(makePQs(facts[i]))


# -- 
# exlude factor pairs where one is less than half of the other

df_factor = pd.DataFrame(pQs)
df_factor.columns = ['f1', 'f2']
df_factor = df_factor.loc[(df_factor['f1'] != 1) & (df_factor['f2'] != 1)]

df_factor['valid'] = df_factor.apply(lambda row: validFacts(row), axis=1)
valid = df_factor.loc[df_factor['valid'] == True]
valid['checkSum'] = valid.apply(lambda row: row['f1'] * row['f2'], axis=1)

valid['p'] = valid.apply(lambda row: makePq(row, 'p'), axis=1)
valid['q'] = valid.apply(lambda row: makePq(row, 'q'), axis=1)
valid['checkAlign'] = valid.apply(lambda row: row['p'] <= row['q'], axis=1)


# -- 
# run SOM and DBI for different valid initializing grid dims

valid.reset_index(inplace=True)

outDicts = []
for i in range(len(valid)): 
    print('evaluating ' + str(i) + ' of ' + str(len(valid)) + 'initializing grids')
    instance = valid.iloc[i][['index','p', 'q']]
    dbi = getDBIstd(instance, dfWB)
    outDicts.append({
            'index' : instance['index'], 
            'p' : instance['p'], 
            'q' : instance['q'],
            'dbi' : dbi
        })

dfDBI = pd.DataFrame(outDicts)


# -- 
# save DBI scores to file for reference

dfDBI.to_csv('./dbi-scores-for-pq-inits-std.csv')


# -- 
# plot DB index over N and save image 

dfDBI.head() 
dfDBI['grid_size'] = dfDBI.apply(lambda row: row['p'] * row['q'], axis=1)

min_score = dfDBI.dbi.min()
min_init = dfDBI.loc[dfDBI['dbi'] == min_score]
x = min_init['grid_size']
y = min_init['dbi']

plt.plot(dfDBI['grid_size'], dfDBI['dbi'], linewidth=2.0)
plt.plot(x, y, marker='o', markersize=3, color="blue")
plt.axvline(x=99, color='black')

plt.savefig('./dbi-std-score-over-N.png')


# -- 
# plot DB index over ratio of p and q 

dfDBI['ratio'] = dfDBI.apply(lambda row: np.float(row['p']) / np.float(row['q']), axis=1)

min_score = dfDBI.dbi.min()
min_init = dfDBI.loc[dfDBI['dbi'] == min_score]
x = min_init['ratio']
y = min_init['dbi']

dfDBI = dfDBI.sort_values('ratio')

plt.plot(dfDBI['ratio'], dfDBI['dbi'], linewidth=2.0)
plt.plot(x, y, marker='o', markersize=3, color="blue")
plt.axvline(x=ratio, color='black')

plt.savefig('./dbi-std-over-pq-ratio.png')
