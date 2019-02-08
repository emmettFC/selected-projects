'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: Aggregate weibo data for polygons 
        II: Do aggregations by an hourly and 20 minute basis
'''

# -- 
# Dependancies 

from datetime import timedelta
import numpy as np 
import pandas as pd 
from dateutil import parser

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

import matplotlib
import matplotlib.pyplot as plt

# -- 
# IO 

'''WHERE IS THIS DATAFRAME COMING FROM: WHAT PRODUCES THIS SCRIPT'''
weibo_frame = pd.read_csv('./data/weibo-dat-with-polygon-labels.csv')
# weibo_frame = weibo_frame.sample(frac=0.10, replace=False)

'''This takes a very long time'''
weibo_frame['time'] = weibo_frame.apply(lambda row: parser.parse(row['timestamp'].replace('"','')), axis =1)
wbf = weibo_frame[[u'unID', u'lon', u'lat', u'timestamp', u'inRange', u'labelInPoly',
       u'label', u'center', u'polygon', u'time']]


# -- 
# Get 60 minute bucket assignment for each record (full process for 87p by 48hr vectors)

wbf.reset_index(inplace=True)
tvect = wbf[['time', 'index']]
buckets = tvect.set_index('time')
buckets = buckets.resample('60T', how='count')
buckets.reset_index(inplace=True)
buckets['end_time'] = buckets.apply(lambda row: row['time'] + timedelta(minutes=59, seconds=59), axis=1)
buckets.reset_index(inplace=True)
buckets.columns = ['bucket', 'start_time', 'count', 'end_time']

'''Logic to make complete set of buckets to join to: otherwise vectors dont preserve time slot'''
buckets['day'] = buckets.apply(lambda row: row['bucket'] / 24, axis=1)
buckets['day_start'] = buckets.apply(lambda row: row['start_time'].replace(hour=0, minute=0, second=0), axis=1)

def getCompId(row): 
    dif = (row['start_time'] - row['day_start']).total_seconds() / 60
    return int(dif / 60) 

def getBucket(row): 
    r = row['time']
    b = buckets.loc[(buckets['end_time'] >= r) & (buckets['start_time'] <= r)]
    return int(b['bucket'])


buckets['comp_id'] = buckets.apply(lambda row: getCompId(row), axis=1)
wbf = wbf.drop(['center', 'polygon', 'unID'], axis=1)
wbf['bucket'] = wbf.apply(lambda row: getBucket(row), axis=1)

weibo = pd.merge(wbf, buckets, on='bucket', how='left')
weibo_60_minutes = weibo[[u'bucket', u'index', u'lon', u'lat', u'timestamp',
       u'label', u'time', u'start_time', u'count',
       u'day', u'comp_id']]


'''Have to build frame for vectors given absence of some data points'''

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

'''Function to initialize and splice in data for 24 dim day vectors'''

def buildXsn(row):
    xsn = [0] * 24 #parameter must change for 20 minute segments
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

'''make reference frame'''
agg1 = weibo.groupby(['label', 'day', 'comp_id']).agg({'index' : 'count'})
agg1.reset_index(inplace=True)

Xsn = pd.DataFrame(frame)
Xsn['xsn'] = Xsn.apply(lambda row: buildXsn(row), axis=1)

'''Agregate by weekend /weekday: 87p by 48hour matrix'''

days = buckets[['day', 'day_start']].drop_duplicates() 
xsn = pd.merge(Xsn, days, on='day', how='left')

'''Label weekend/weekday'''
def isWeekday(row): 
    d = row['day_start']
    if d.weekday() in [5,6]: 
        out = 'weekend'
    else: 
        out = 'weekday'
    return out

xsn['weekday'] = xsn.apply(lambda row: isWeekday(row), axis=1)
Xswkn = xsn.loc[xsn['weekday'] == 'weekend']
Xswkd = xsn.loc[xsn['weekday'] == 'weekday']
Xswkn = Xswkn.groupby('label').agg({'xsn':(lambda x: list(x))})
Xswkd = Xswkd.groupby('label').agg({'xsn':(lambda x: list(x))})

def getAvgVec(row): 
    vecs = np.array(row['xsn'])
    comb = np.mean(vecs, axis=0)
    return comb

Xswkn['avg_vec'] = Xswkn.apply(lambda row: getAvgVec(row), axis=1)
Xswkd['avg_vec'] = Xswkd.apply(lambda row: getAvgVec(row), axis=1)

'''Join average vectors for weekday and weekend'''
Xswkd.reset_index(inplace=True)
Xswkn.reset_index(inplace=True)

Xswkn.columns = ['label', 'xsnWknd', 'avg_vec_wkn']
df_vector = pd.merge(Xswkd, Xswkn, on='label', how='left')
df_vector['combined'] = df_vector.apply(lambda row: list(row['avg_vec']) + list(row['avg_vec_wkn']), axis=1)
df_spect = df_vector[['label', 'combined']]

polys = weibo_frame[['label', 'center', 'polygon']].drop_duplicates()
week_hour_vectors = pd.merge(df_spect, polys, on='label', how='left')
week_hour_vectors.to_csv('./data/week-hour-vectors.csv')


'''Agregate by day-hour: 87p by 168hour matrix'''

def dayOfweek(row): 
    d = row['day_start']
    return d.weekday()

def getAvgVec(row): 
    vecs = np.array(row['xsn'])
    comb = np.mean(vecs, axis=0)
    return comb

def getConcatVec(row): 
    items = row['avg_vec']
    l = list(items[0])
    for i in range(len(items)): 
        if i > 0: 
            l.extend(list(items[i]))
    return l

xsn['day_lab'] = xsn.apply(lambda row: dayOfweek(row), axis=1)
Xsall = xsn.groupby(['label', 'day_lab']).agg({'xsn':(lambda x: list(x))})
Xsall['avg_vec'] = Xsall.apply(lambda row: getAvgVec(row), axis=1)
Xsall = Xsall.groupby('label').agg({'avg_vec':(lambda x: list(x))})
Xsall['combined'] = Xsall.apply(lambda row: getConcatVec(row), axis=1)
day_hour_vectors = pd.merge(Xsall, polys, on='label', how='left')
day_hour_vectors = day_hour_vectors[['label', 'combined', 'center', 'polygon']]
day_hour_vectors.to_csv('./data/day-hour-vectors.csv')


# -- 
# Get 20 minute bucket assignment for each record

wbf = weibo_frame[[u'unID', u'lon', u'lat', u'timestamp', u'inRange', u'labelInPoly',
       u'label', u'center', u'polygon', u'time']]

wbf.reset_index(inplace=True)
tvect = wbf[['time', 'index']]
buckets = tvect.set_index('time')
buckets = buckets.resample('20T', how='count')
buckets.reset_index(inplace=True)
buckets['end_time'] = buckets.apply(lambda row: row['time'] + timedelta(minutes=19, seconds=59), axis=1)
buckets.reset_index(inplace=True)
buckets.columns = ['bucket', 'start_time', 'count', 'end_time']

'''Logic to make complete set of buckets to join to: otherwise vectors dont preserve time slot'''

buckets['day'] = buckets.apply(lambda row: row['bucket'] / 72, axis=1)
buckets['day_start'] = buckets.apply(lambda row: row['start_time'].replace(hour=0, minute=0, second=0), axis=1)

def getCompId(row): 
    dif = (row['start_time'] - row['day_start']).total_seconds() / 60
    return int(dif / 20) 

def getBucket(row): 
    r = row['time']
    b = buckets.loc[(buckets['end_time'] >= r) & (buckets['start_time'] <= r)]
    return int(b['bucket'])


buckets['comp_id'] = buckets.apply(lambda row: getCompId(row), axis=1)
wbf = wbf.drop(['center', 'polygon', 'unID'], axis=1)
wbf['bucket'] = wbf.apply(lambda row: getBucket(row), axis=1)

weibo = pd.merge(wbf, buckets, on='bucket', how='left')
weibo_20_minutes = weibo[[u'bucket', u'index', u'lon', u'lat', u'timestamp',
       u'label', u'time', u'start_time', u'count',
       u'day', u'comp_id']]

'''Have to build frame for vectors given absence of some data points'''

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

'''Function to initialize and splice in data for 24 dim day vectors'''

def buildXsn(row):
    xsn = [0] * 72 #parameter must change for 20 minute segments
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

'''make reference frame'''
agg1 = weibo.groupby(['label', 'day', 'comp_id']).agg({'index' : 'count'})
agg1.reset_index(inplace=True)

Xsn = pd.DataFrame(frame)
Xsn['xsn'] = Xsn.apply(lambda row: buildXsn(row), axis=1)

'''Agregate by weekend /weekday: 87p by 144hour matrix'''

days = buckets[['day', 'day_start']].drop_duplicates() 
xsn = pd.merge(Xsn, days, on='day', how='left')

'''Label weekend/weekday'''
def isWeekday(row): 
    d = row['day_start']
    if d.weekday() in [5,6]: 
        out = 'weekend'
    else: 
        out = 'weekday'
    return out

xsn['weekday'] = xsn.apply(lambda row: isWeekday(row), axis=1)
Xswkn = xsn.loc[xsn['weekday'] == 'weekend']
Xswkd = xsn.loc[xsn['weekday'] == 'weekday']
Xswkn = Xswkn.groupby('label').agg({'xsn':(lambda x: list(x))})
Xswkd = Xswkd.groupby('label').agg({'xsn':(lambda x: list(x))})

def getAvgVec(row): 
    vecs = np.array(row['xsn'])
    comb = np.mean(vecs, axis=0)
    return comb

Xswkn['avg_vec'] = Xswkn.apply(lambda row: getAvgVec(row), axis=1)
Xswkd['avg_vec'] = Xswkd.apply(lambda row: getAvgVec(row), axis=1)

'''Join average vectors for weekday and weekend'''
Xswkd.reset_index(inplace=True)
Xswkn.reset_index(inplace=True)

Xswkn.columns = ['label', 'xsnWknd', 'avg_vec_wkn']
df_vector = pd.merge(Xswkd, Xswkn, on='label', how='left')
df_vector['combined'] = df_vector.apply(lambda row: list(row['avg_vec']) + list(row['avg_vec_wkn']), axis=1)
df_spect = df_vector[['label', 'combined']]

polys = weibo_frame[['label', 'center', 'polygon']].drop_duplicates()
week_segment_vectors = pd.merge(df_spect, polys, on='label', how='left')
week_segment_vectors.to_csv('./data/week-segment-vectors.csv')

'''Agregate by day-hour: 87p by 504 segment matrix'''

def dayOfweek(row): 
    d = row['day_start']
    return d.weekday()

def getAvgVec(row): 
    vecs = np.array(row['xsn'])
    comb = np.mean(vecs, axis=0)
    return comb

def getConcatVec(row): 
    items = row['avg_vec']
    l = list(items[0])
    for i in range(len(items)): 
        if i > 0: 
            l.extend(list(items[i]))
    return l

xsn['day_lab'] = xsn.apply(lambda row: dayOfweek(row), axis=1)
Xsall = xsn.groupby(['label', 'day_lab']).agg({'xsn':(lambda x: list(x))})
Xsall['avg_vec'] = Xsall.apply(lambda row: getAvgVec(row), axis=1)
Xsall = Xsall.groupby('label').agg({'avg_vec':(lambda x: list(x))})
Xsall['combined'] = Xsall.apply(lambda row: getConcatVec(row), axis=1)
day_segment_vectors = pd.merge(Xsall, polys, on='label', how='left')
day_segment_vectors = day_segment_vectors[['label', 'combined', 'center', 'polygon']]
day_segment_vectors.to_csv('./data/day-segment-vectors.csv')

