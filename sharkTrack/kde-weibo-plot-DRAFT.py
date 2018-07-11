'''
    Make bivariate KDE plot with havershine: 
        I: hopefully this provides some sanity check on 
'''

# -- 
# Dependancies

import matplotlib
import matplotlib.pyplot as plt 
import seaborn as sns
from mpl_toolkits.basemap import Basemap

import pandas as pd
import json, re, math
import numpy as np
from pprint import pprint
from datetime import datetime
from dateutil import parser as dp
from datetime import date, timedelta
import time
import datetime
from math import ceil
import csv
import pickle

from scipy.cluster.vq import kmeans2, whiten

from sklearn.datasets import fetch_species_distributions
from sklearn.datasets.species_distributions import construct_grids
from sklearn.neighbors import KernelDensity

import geojson
import copy
from collections import OrderedDict
import warnings
warnings.filterwarnings('ignore')
import geojson
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from geopy.distance import vincenty #
import matplotlib.cm as cm
from scipy.spatial.distance import cdist, pdist
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# -- 
# IO

wbDat = pd.read_csv('/Users/culhane/Desktop/DDYale-NASA/dataOth/weibo-inRange.csv')

with open("./dataDDY/beijing.geojson") as json_file:
    json_data = geojson.load(json_file)


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


# -- 
# Determine parameters for creation of grid

'''Longitude moves from 115 to 118'''
'''Latitude moves from 39 to 41.5'''

xllc = 115
yllc = 39
Nx = (118 - 115) / 0.005
Ny = (41.5 - 39) /0.005


prm = dict(x_left_lower_corner=xllc,
                    Nx=Nx,
                    y_left_lower_corner=yllc,
                    Ny=Ny,
                    grid_size=0.005)


# - 
# Build KDE 

x_train = wbDat[['lat', 'lon']].values
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


# -- 
# Build Beijing plot as base for contour 

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



# -- 
# Get cluster centers from K-Means impl (to do after initial KDE)

cntLons, cntLats = cntrds['lon'], cntrds['lat']    
ax.scatter(cntLons, cntLats, marker = 'x', color='red', edgecolor='gray', zorder=5, alpha=1.0, s=30)


# -- 
# Build contour and add to polgons 

levels = np.linspace(0, Z.max(), 25)
plt.contourf(X, Y, Z, levels=levels, cmap=plt.get_cmap('Blues'))


# -- 
# Show KDE 
'''This is hilariously wrong; check what bivariate kde plot looks like'''
'''This is because the grid is way too small'''
plt.scatter(wbDat['lon'], wbDat['lat'], marker = 'x', color='red', edgecolor='gray', zorder=5, alpha=1.0, s=1)
plt.show() 


# -- 
# Make basic bivariate kde plot

x, y = wbDat['lon'], wbDat['lat']
ax = sns.regplot(x=x, y=y, fit_reg=False)
sns.kdeplot(x, y, bw=.005, shade=False)
'''This takes a while; which suggests that above error is due to granularity'''
'''Should also plot the scatter beneath the KDE'''

# -- 
# Can also make a hexagonal bin heatmap to see if the coords are correct
# Baically what this means is that there are like a billion points right there in the middle


X = wbDat[['lat', 'lon']].values
Ks = range(1, 25)
kmean = [KMeans(n_clusters=i).fit(X) for i in Ks]
k = [20]
nClusters = k[0]
est = kmean[nClusters-1]

centers = np.array(est.cluster_centers_)
cntrds = pd.DataFrame(centers)
cntrds.columns = ['lat', 'lon']

x, y = wbDat['lon'], wbDat['lat']
ax = sns.regplot(x=x, y=y, fit_reg=False)
sns.regplot(x=cntrds['lon'], y=cntrds['lat'], fit_reg=False)


# -- 
# Combine two methods of plotting and build kde for each clutser: 


x, y = wbDat['lon'], wbDat['lat']
ax = sns.regplot(x=x, y=y, fit_reg=False, scatter_kws={'s':1})
# ax = plt.scatter(x, y, color='red', s=0.1)

for i in range(0, len(feats)): 
    try: 
        test = feats[i]
        poly = test['geometry']
        coords = poly['coordinates']
        x = [i for i,j in coords[0]]
        y = [j for i,j in coords[0]]
        # ax = fig.gca() 
        # ax.plot(x,y)
        ax.plot(x, y, color='black')
        ax.axis('scaled')
    except: 
        print('failed to add polygon with index ' + str(i))



for i in range(K):
    df = wbDat.loc[wbDat['cluster'] == clist[i]]        
    x1, y1 = df['lon'], df['lat']
    sns.kdeplot(x1, y1, bw=.15, shade=False) 


sns.regplot(x=cntrds['lon'], y=cntrds['lat'], fit_reg=False)

# ax = sns.kdeplot(setosa.sepal_width, setosa.sepal_length, 
#     cmap="Reds", shade=True, shade_lowest=False)
# ax = sns.kdeplot(virginica.sepal_width, virginica.sepal_length, 
#     cmap="Blues", shade=True, shade_lowest=False)











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







