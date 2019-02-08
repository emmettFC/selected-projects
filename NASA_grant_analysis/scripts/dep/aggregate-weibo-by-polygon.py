'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: Aggregate weibo data for polygons 
        II: Do aggregations by an hourly and 20 minute basis
'''

# -- 
# dependancies 

from datetime import timedelta
import numpy as np 
import pandas as pd 
from dateutil import parser

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

import matplotlib
import matplotlib.pyplot as plt


# -- 
# io

weibo_frame = pd.read_csv('../data/vtess-finite-npdefaults-9-11.csv')


# -- 
# user defined functions

def getCompId(row, bucket_minutes): 
    dif = (row['start_time'] - row['day_start']).total_seconds() / bucket_minutes
    return int(dif / bucket_minutes) 

def getBucket(row): 
    r = row['time']
    b = buckets.loc[(buckets['end_time'] >= r) & (buckets['start_time'] <= r)]
    return int(b['bucket'])

def buildXsn(row, n_day_buckets):
    xsn = [0] * n_day_buckets 
    s = row['label']
    n = row['day']
    records = agg1.loc[(agg1['label'] == s) & (agg1['day'] == n)]
    to_modify = xsn
    indexes = list(records['comp_id'])
    replacements = list(records['index'])
    for i in range(len(indexes)):
        # print(i)
        to_modify[indexes[i]] = replacements[i]
    return to_modify

def isWeekday(row): 
    d = row['day_start']
    if d.weekday() in [5,6]: 
        out = 'weekend'
    else: 
        out = 'weekday'
    return out

def getAvgVec(row): 
    vecs = np.array(row['xsn'])
    comb = np.mean(vecs, axis=0)
    return comb

def dayOfweek(row): 
    d = row['day_start']
    return d.weekday()

def getConcatVec(row): 
    items = row['avg_vec']
    l = list(items[0])
    for i in range(len(items)): 
        if i > 0: 
            l.extend(list(items[i]))
    return l


# -- 
# convert time feild and reduce columns

weibo_frame['time'] = weibo_frame.apply(lambda row: parser.parse(row['timestamp'].replace('"','')), axis =1)
wbf = weibo_frame[[u'unID', u'lon', u'lat', u'timestamp', u'labelInPoly',
       u'label', u'center', u'polygon', u'time']]


# -- 
# build and export vectors for n_polygon by 48 hour aggregation

wbf.reset_index(inplace=True)
tvect = wbf[['time', 'index']]
buckets = tvect.set_index('time')
buckets = buckets.resample('60T', how='count')
buckets.reset_index(inplace=True)
buckets['end_time'] = buckets.apply(lambda row: row['time'] + timedelta(minutes=59, seconds=59), axis=1)
buckets.reset_index(inplace=True)
buckets.columns = ['bucket', 'start_time', 'count', 'end_time']

buckets['day'] = buckets.apply(lambda row: row['bucket'] / 24, axis=1)
buckets['day_start'] = buckets.apply(lambda row: row['start_time'].replace(hour=0, minute=0, second=0), axis=1)


# -- 
# apply functions to bucket frame to join to weibo data

buckets['comp_id'] = buckets.apply(lambda row: getCompId(row, 60), axis=1)
wbf['bucket'] = wbf.apply(lambda row: getBucket(row), axis=1)

weibo = pd.merge(wbf, buckets, on='bucket', how='left')
weibo_60_minutes = weibo[[u'bucket', u'index', u'lon', u'lat', u'timestamp',
       u'label', u'time', u'start_time', u'count',
       u'day', u'comp_id', u'polygon',u'center']]


# -- 
# have to build frame of polygon-day given limit of data coverage

days = list(buckets['day']) 
days = list(set(days))
polygons = list(weibo['label'])
polygons = list(set(polygons))

frame = []
for p in polygons: 
    for d in days: 
        out = {
            'label' : p, 
            'day' : d
        }
        frame.append(out)


# -- 
# aggregate data by polygon-day-hours 

agg1 = weibo.groupby(['label', 'day', 'comp_id']).agg({'index' : 'count'})
agg1.reset_index(inplace=True)

# -- 
# create vectors with function 

Xsn = pd.DataFrame(frame)
Xsn['xsn'] = Xsn.apply(lambda row: buildXsn(row, 24), axis=1)


# -- 
# join to dates and label by weekennd and weekday

days = buckets[['day', 'day_start']].drop_duplicates() 
xsn = pd.merge(Xsn, days, on='day', how='left')
xsn['weekday'] = xsn.apply(lambda row: isWeekday(row), axis=1)
Xswkn = xsn.loc[xsn['weekday'] == 'weekend']
Xswkd = xsn.loc[xsn['weekday'] == 'weekday']

# -- 
# aggregate by weekend weekday

Xswkn = Xswkn.groupby('label').agg({'xsn':(lambda x: list(x))})
Xswkd = Xswkd.groupby('label').agg({'xsn':(lambda x: list(x))})


# -- 
# build average activity vectors for wknd/wkdy

Xswkn['avg_vec'] = Xswkn.apply(lambda row: getAvgVec(row), axis=1)
Xswkd['avg_vec'] = Xswkd.apply(lambda row: getAvgVec(row), axis=1)

Xswkd.reset_index(inplace=True)
Xswkn.reset_index(inplace=True)

# -- 
# join average vectors for each polygon to build one 48 hour dim vector of average activity

Xswkn.columns = ['label', 'xsnWknd', 'avg_vec_wkn']
df_vector = pd.merge(Xswkd, Xswkn, on='label', how='left')
df_vector['combined'] = df_vector.apply(lambda row: list(row['avg_vec']) + list(row['avg_vec_wkn']), axis=1)
df_spect = df_vector[['label', 'combined']]


# -- 
# Join to polygons and activity vectors and write to csv

polys = weibo_frame[['label', 'center', 'polygon']].drop_duplicates()
week_hour_vectors = pd.merge(df_spect, polys, on='label', how='left')
week_hour_vectors.to_csv('../data/weekday-weekend-hour-vectors.csv')

# -- 
# repeat process for day-hour level (0-6) activity vectors 

xsn['day_lab'] = xsn.apply(lambda row: dayOfweek(row), axis=1)
Xsall = xsn.groupby(['label', 'day_lab']).agg({'xsn':(lambda x: list(x))})
Xsall['avg_vec'] = Xsall.apply(lambda row: getAvgVec(row), axis=1)
Xsall = Xsall.groupby('label').agg({'avg_vec':(lambda x: list(x))})
Xsall['combined'] = Xsall.apply(lambda row: getConcatVec(row), axis=1)

# -- 
# join to polygons and write to csv

day_hour_vectors = pd.merge(Xsall, polys, on='label', how='left')
day_hour_vectors = day_hour_vectors[['label', 'combined', 'center', 'polygon']]
day_hour_vectors.to_csv('../data/day-hour-vectors.csv')

