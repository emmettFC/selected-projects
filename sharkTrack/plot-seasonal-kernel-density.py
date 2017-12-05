'''
Make preliminary vizualization of seasonal density
'''


import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt 
import seaborn as sns
from mpl_toolkits.basemap import Basemap

import pandas as pd
import json, re, math
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, streaming_bulk
import numpy as np
from pprint import pprint
from datetime import datetime
from dateutil import parser as dp
from datetime import date, timedelta
import time
import datetime
from math import ceil
import plotly.plotly as py
import plotly.graph_objs as go
from __future__ import division

import csv
import pandas as pd
import numpy as np

from scipy.cluster.vq import kmeans2, whiten


from netCDF4 import Dataset as NetCDFFile

from sklearn.datasets import fetch_species_distributions
from sklearn.datasets.species_distributions import construct_grids
from sklearn.neighbors import KernelDensity

import pickle

# -- 
# Load sharks data from pickle 

with open('shark_tracker_data.pickle', 'rb') as handle:
    sharks = pickle.load(handle)

_type = 'White Shark (Carcharodon carcharias)'
whiteSharks = [s for s in sharks if s['species'] == _type]

allPings = []
for ws in whiteSharks: 
    pings = ws['pings']
    for ping in pings: 
        ping['shark'] = ws['name']
        ping['active'] = ws['active']
        ping['gender'] = ws['gender']
        ping['isMobile'] = ws['isMobile']
        ping['is_alive'] = ws['is_alive']
        ping['length'] = ws['length']
        ping['cnt_inactive_pings'] = ws['cnt_inactive_pings']
        ping['stageOfLife'] = ws['stageOfLife']
        ping['tagDate'] = ws['tagDate']
        ping['tagLocation'] = ws['tagLocation']
        ping['weight'] = ws['weight']
    allPings.extend(pings)

pgs = pd.DataFrame(allPings)

pgs['lat'] = pgs.latitude.apply(lambda x: float(x))
pgs['lon'] = pgs.longitude.apply(lambda x: float(x))


# -- 
# Build out KDE data struc (adapted from scikitlearn docs sample kde)

def construct_grid(prm):
    xmin = prm['x_left_lower_corner'] + prm['grid_size']
    xmax = xmin + (prm['Nx'] * prm['grid_size'])
    ymin = prm['y_left_lower_corner'] + prm['grid_size']
    ymax = ymin + (prm['Ny'] * prm['grid_size'])
    xgrid = np.arange(xmin, xmax, prm['grid_size'])
    ygrid = np.arange(ymin, ymax, prm['grid_size'])
    return (xgrid, ygrid)

prm = dict(x_left_lower_corner=-90,
                    Nx=1212,
                    y_left_lower_corner=0,
                    Ny=1592,
                    grid_size=0.05)

# - 
# Seasonal subplots (Loops above process for seasonal telemetry)

pgs['time'] = pgs.datetime.apply(lambda x: dp.parse(x))
pgs['month']  = pgs['time'].map(lambda x: x.strftime('%m'))

spring = pgs.loc[pgs['month'].isin(['04', '05', '06'])]
winter = pgs.loc[pgs['month'].isin(['01', '02', '03'])]
fall = pgs.loc[pgs['month'].isin(['10', '11', '12'])]
summer = pgs.loc[pgs['month'].isin(['07', '08', '09'])]

# seasons = {
#     1: ('spring', 'Greens'),
#     2: ('summer', 'Reds'),
#     3: ('fall', 'Oranges'),
#     4: ('winter', 'Blues')
# }

seasons = {
    1: ('spring', 'Reds'),
    2: ('summer', 'Reds'),
    3: ('fall', 'Blues'),
    4: ('winter', 'Blues')
}


fig = plt.figure()
counter = 1
for season in (spring, summer, fall, winter): 
    # - fit
    x_train = season[['lat', 'lon']].values
    y_train = np.ones(len(x_train))
    x_train *= np.pi / 180.  # Convert lat/long to radians
    xgrid, ygrid = construct_grid(prm)
    X, Y = np.meshgrid(xgrid[::5], ygrid[::5][::-1]) 
    xy = np.vstack([Y.ravel(), X.ravel()]).T
    xy *= np.pi / 180.
    kde = KernelDensity(bandwidth=0.04, metric='haversine',
                        kernel='gaussian', algorithm='ball_tree')
    kde.fit(x_train[y_train == 1])
    Z = np.exp(kde.score_samples(xy))
    Z = Z.reshape(X.shape)
    # - plot
    number = '22' + str(counter)
    number = int(number)
    ax = fig.add_subplot(number)
    ax.set_title(seasons[counter][0])
    levels = np.linspace(0, Z.max(), 25)
    plt.contourf(X, Y, Z, levels=levels, cmap=plt.get_cmap(seasons[counter][1]))
    m = Basemap(projection='cyl', llcrnrlat=Y.min(),
                urcrnrlat=Y.max(), llcrnrlon=X.min(),
                urcrnrlon=X.max(), resolution='c')
    m.drawcoastlines()
    m.drawcountries()
    counter += 1

plt.show()







