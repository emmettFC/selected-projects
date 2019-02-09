'''
Plot White Shark Telemetry: 
    I:   Seasonal scatter of pings 
    II:  Include ETOPO1 bathymetric layer
    III: Include CoRTAD SST tiles only
'''

# - 
# Dependancies

from __future__ import division

import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt 
from mpl_toolkits.basemap import Basemap, shiftgrid
import seaborn as sns

import netCDF4
from netCDF4 import Dataset

import numpy.ma as ma
import pandas as pd
import numpy as np

import json, re, math
import csv
from math import ceil
from pprint import pprint
import pickle

from datetime import datetime
from dateutil import parser as dp
from datetime import date, timedelta
import time
import datetime

from matplotlib.collections import PatchCollection
import urllib3
import os, sys, string
from pylab import *
import pylab as pl
import argparse 

import laplaceFilter

# -- 
# Parse args: Command Line Interface

parser = argparse.ArgumentParser(description='Plot White Shark Telemetry')
parser.add_argument('--bathymetry', dest='bathymetry', action="store_true")
parser.add_argument('--season', type=str, dest='season', action="store")
args = parser.parse_args()

# --
# Funtcions to ingest and structure SST tiles from CoRTAD NetCDF4 files

def loadNCDF4(fileNames, params): 
    cdfs = {} 
    for i in range(0, len(fileNames)): 
        filename = params['base'] + fileNames[i]
        cdfs['cdf' + str(i +1)] = Dataset(filename)

    return cdfs

def getLonLat(cdfs, latIndices, lonIndices): 
    lons = [] 
    lats = []
    files = cdfs.keys()
    for latIndex in latIndices: 
        lats.append(np.squeeze(cdfs['cdf' + str(latIndex)].variables["Latitude"][:]))

    for lonIndex in lonIndices: 
        lons.append(np.squeeze(cdfs['cdf' + str(lonIndex)].variables["Longitude"][:]))

    latitude = concatenate(tuple(lats))
    longitude = concatenate(tuple(lons))
    return latitude, longitude

def getIndex(date): 
    closeDates = {}
    for t in range(len(time)):
        currentTime=params['refDate'] + datetime.timedelta(days=time[t])
        if abs((date-currentTime).days) <= 7: 
            closeDates[t] = abs((date-currentTime).days)

    return min(closeDates, key=closeDates.get)

def buildIndices(): 
    smr = getIndex(datetime.datetime(2009,8,15))
    spg = getIndex(datetime.datetime(2009,5,15))
    fll = getIndex(datetime.datetime(2009,11,15))
    wtr = getIndex(datetime.datetime(2009,2,15))
    return smr, spg, fll, wtr

def makeSST(t): 
    SSTs = {}
    for i in range(0, len(cdfs)): 
        index = str(i + 1)
        fst = cdfs['cdf' + index].variables["FilledSST"][:,:,t]
        offset =cdfs['cdf' + index].variables["FilledSST"].__getattribute__('add_offset')
        fst=fst + abs(offset)
        fst=np.rot90(fst,3) 
        SSTs['filledSST' + index] = np.fliplr(fst) 

    return SSTs

def buildTileMatrix(nCols, t): 
    SSTs = makeSST(t)
    rows = []
    nRows = int(len(SSTs)/nCols)
    endPts = [i + 1 for i in range(len(SSTs)) if (i + 1) % nCols == 0]
    for i in range(nRows): 
        end = endPts[i]
        SSTrow = []
        for n in range(nCols): 
            index = str(end - (n)) 
            SSTrow.append(SSTs['filledSST' + index])

        rows.append(concatenate(tuple(list(reversed(SSTrow))), axis=1))

    filledSST = concatenate(tuple(rows), axis=0)
    return filledSST

def findSubsetIndices(min_lat,max_lat,min_lon,max_lon,lats,lons):
    ''' Array to store the results returned from the function '''
    res=np.zeros((4),dtype=np.float64)
    minLon=min_lon; maxLon=max_lon
    distances1 = []; distances2 = []
    indices=[]; index=1
    for point in lats:
        s1 = max_lat-point # (vector subtract)
        s2 = min_lat-point # (vector subtract)
        distances1.append((np.dot(s1, s1), point, index))
        distances2.append((np.dot(s2, s2), point, index-1))
        index=index+1

    distances1.sort()
    distances2.sort()
    indices.append(distances1[0])
    indices.append(distances2[0])
    distances1 = []; distances2 = []; index=1
    for point in lons:
        s1 = maxLon-point # (vector subtract)
        s2 = minLon-point # (vector subtract)
        distances1.append((np.dot(s1, s1), point, index))
        distances2.append((np.dot(s2, s2), point, index-1))
        index=index+1

    distances1.sort()
    distances2.sort()
    indices.append(distances1[0])
    indices.append(distances2[0])

    ''' Save final product: max_lat_indices,min_lat_indices,max_lon_indices,min_lon_indices '''
    minJ=indices[1][2]
    maxJ=indices[0][2]
    minI=indices[3][2]
    maxI=indices[2][2]
    res[0]=minI; res[1]=maxI; res[2]=minJ; res[3]=maxJ;
    return res


# --
# Plotting functions

def LevelColormap(levels, cmap=None):
    ''' Make a colormap based on an increasing sequence of levels '''
    if cmap == None:
        cmap = pl.get_cmap()

    nlev = len(levels)
    S = pl.arange(nlev, dtype='float')/(nlev-1)
    A = cmap(S)
    levels = pl.array(levels, dtype='float')
    L = (levels-levels[0])/(levels[-1]-levels[0])
    R = [(L[i], A[i,0], A[i,0]) for i in range(nlev)]
    G = [(L[i], A[i,1], A[i,1]) for i in range(nlev)]
    B = [(L[i], A[i,2], A[i,2]) for i in range(nlev)]
    cdict = dict(red=tuple(R),green=tuple(G),blue=tuple(B))

    return matplotlib.colors.LinearSegmentedColormap(
        '%s_levels' % cmap.name, cdict, 256)


def plotSeason(season, nCols, params, bathy=True): 
    filledSST = buildTileMatrix(nCols, season[1])
    plt.figure(figsize=(24,20),frameon=False)

    ''' Adjust lon_0 value based on geographic orientation '''
    if params['lonStart']< 0 and params['lonEnd'] < 0:
        lon_0= - (abs(params['lonEnd'])+abs(params['lonStart']))/2.0
    elif params['lonStart'] > 0 and params['lonEnd'] > 0:
        lon_0=(abs(params['lonEnd'])+abs(params['lonStart']))/2.0
    else:
        lon_0=((params['lonEnd'])+(params['lonStart']))/2.0

    ''' Make Basemap Projection of Atlantic window '''
    map = Basemap(llcrnrlat=params['latStart'],urcrnrlat=params['latEnd'],\
            llcrnrlon=params['lonStart'],urcrnrlon=params['lonEnd'],\
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',area_thresh=1000.,projection='lcc',\
            lat_1=params['latStart'],lon_0=lon_0)
    lon,lat=meshgrid(longitude,latitude)
    x, y = map(lon,lat)
    map.drawcoastlines()
    map.fillcontinents(color='grey')
    map.drawcountries()

    ''' Make SST assimilation with CoRTAD tiles '''
    levels = np.arange(0,40,0.65)
    CS1 = map.contourf(x,y,filledSST,levels,
                        cmap = LevelColormap(levels,cmap=cm.RdYlBu_r),
                        extend='both',
                        alpha=0.7,
                        origin='lower',
                        rasterized=True)
    
    ''' Add white shark pings '''
    lats = season[2]['latitude'].values
    lons = season[2]['longitude'].values
    x2, y2 = map(lons, lats)
    map.scatter(x2, y2, marker='D',color='black', s=5)
    CS1.axis='tight'
    map.drawmeridians(np.arange(lon.min(),lon.max(),10),labels=[0,0,0,1])
    map.drawparallels(np.arange(lat.min(),lat.max(),4),labels=[1,0,0,0])
    plt.colorbar(CS1,orientation='vertical',extend='both', shrink=0.5)

    ''' Add ocean Bathymetry layer to plot from Etopo Grid '''
    if bathy: 
        etopo1name='./ETOPO1_Ice_g_gmt4.grd'
        etopo1 = Dataset(etopo1name,'r')
        lons = etopo1.variables["x"][:]
        lats = etopo1.variables["y"][:]
        res = findSubsetIndices(params['latStart']-5,params['latEnd']+5,params['lonStart']-40,params['lonEnd']+10,lats,lons)
        loni,lati=np.meshgrid(lons[int(res[0]):int(res[1])],lats[int(res[2]):int(res[3])])
        bathy = etopo1.variables["z"][int(res[2]):int(res[3]),int(res[0]):int(res[1])]
        bathySmoothed = laplaceFilter.laplace_filter(bathy,M=None)
        levelsi=[-6000,-5000,-3000, -2000, -1500, -1000,-500, -400, -300, -250, -200, -150, -100, -75, -65, -50, -35, -25, -15, -10, -5, 0]
        xi, yi = map(loni,lati)
        CS2 = map.contour(xi,yi,bathySmoothed,levelsi,
                           linewidth = .001,
                           colors = 'Grey',
                           extend='upper',
                           alpha=0.4,
                           origin='lower')
        CS2.axis='tight'

    plt.title(season[0] + ' white shark telemetry against mid-season CoRTAD SST layer')
    if bathy: 
        plotfile= season[0] + '_telemetry_cortadSST_bathymetry.png'
    else: 
        plotfile= season[0] + '_telemetry_cortadSST.png'
    
    ''' Save plot to directory '''
    plt.savefig(plotfile)



# --
# Define parameters 

params = {
    'lonStart' : -85,
    'lonEnd' : -20,
    'latStart' : 14, 
    'latEnd' : 49,
    'name' : 'Atlantic Ocean',
    'base' : "http://data.nodc.noaa.gov/opendap/cortad/Version3/",
    'refDate' : datetime.datetime(1982,1,1,0,0,0)
}

fileNames = ["cortadv3_row01_col04.h5",
            "cortadv3_row01_col05.h5",
            "cortadv3_row01_col06.h5",
            "cortadv3_row02_col04.h5",
            "cortadv3_row02_col05.h5",
            "cortadv3_row02_col06.h5",
            "cortadv3_row03_col04.h5",
            "cortadv3_row03_col05.h5",
            "cortadv3_row03_col06.h5"]

# --
# Load white shark telemetry

with open('./shark_tracker_data.pickle', 'rb') as handle:
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

pgs['time'] = pgs.datetime.apply(lambda x: dp.parse(x))
pgs['month']  = pgs['time'].map(lambda x: x.strftime('%m'))


# --
# Run

cdfs = loadNCDF4(fileNames, params)
time=np.squeeze(cdfs['cdf1'].variables["Time"][:])
latitude, longitude = getLonLat(cdfs, latIndices = [1, 4, 7], lonIndices = [1, 2, 3])

seasons = {
    'spring' : ('Spring', getIndex(datetime.datetime(2009,5,15)), pgs.loc[pgs['month'].isin(['04', '05', '06'])]),
    'summer' : ('Summer', getIndex(datetime.datetime(2009,8,15)), pgs.loc[pgs['month'].isin(['07', '08', '09'])]),
    'fall' : ('Fall', getIndex(datetime.datetime(2009,11,15)), pgs.loc[pgs['month'].isin(['10', '11', '12'])]),
    'winter' : ('Winter', getIndex(datetime.datetime(2009,2,15)), pgs.loc[pgs['month'].isin(['01', '02', '03'])])
}


if not args.season: 
    print('No season argument provided: Please select [spring, summer, fall, winter]')
if args.bathymetry: 
    plotSeason(seasons[args.season], 3, params, bathy=True)
else: 
    plotSeason(seasons[args.season], 3, params, bathy=False)


