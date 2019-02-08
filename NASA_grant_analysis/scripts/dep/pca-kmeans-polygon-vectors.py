
'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: Trial 2D PCA & Kmeans clustering of polygon vectors
        II: Make signature graphs for each cluster (re FM)
'''

# -- 
# dependancies

from sklearn.decomposition import PCA
import numpy as np
from sklearn.cluster import KMeans

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geojson
pd.set_option('display.expand_frame_repr', False)

from shapely import geometry
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry import Polygon, mapping
from scipy.spatial import Voronoi, voronoi_plot_2d
from shapely.geometry import shape, Point
from descartes import PolygonPatch


# -- 
# user defined funtions

def fixLstring(row): 
    v = row['combined']
    s = v[1:-1].split(', ')
    s = [np.float(i) for i in s]
    return s

def normVec(row): 
    v = row['combined']
    d = np.sum(v)
    norm = [np.float(i)/np.float(d) for i in v]
    return norm

def getAvgVec(row): 
    vecs = np.array(row['normalized_vector'])
    comb = np.mean(vecs, axis=0)
    return comb

def coercePolygon(row): 
    string = row['polygon'].replace('POLYGON ((', ''). replace('))', '')
    s = string.split(', ')
    s = [i.split(' ') for i in s]
    verts = []
    for i in s: 
        vert = [np.float(v) for v in i]
        vert = tuple(vert)
        verts.append(vert)
    return verts

# -- 
# io 

dhv = pd.read_csv('../data/day-hour-vectors.csv')
dhv['combined_list'] = dhv.apply(lambda row: fixLstring(row), axis=1)
len(dhv.iloc[0].combined_list) # 168 dim, correct
# [ 0.11674758  0.0951933 ]

whv = pd.read_csv('../data/weekday-weekend-hour-vectors.csv')
whv['combined_list'] = whv.apply(lambda row: fixLstring(row), axis=1)
len(whv.iloc[0].combined_list) # 48 dim, correct
# [ 0.22319044  0.16556947]


# -- 
# run PCA and kmeans clustering on aggregate vectors

cluster_frame_whv = whv[['label', 'combined_list']]
cluster_frame_dhv = dhv[['label', 'combined_list']]

cluster_frame_whv.columns = ['label', 'combined']
cluster_frame_dhv.columns = ['label', 'combined']
cluster_frame_whv['normalized_vector'] = cluster_frame_whv.apply(lambda row: normVec(row), axis=1)
cluster_frame_dhv['normalized_vector'] = cluster_frame_dhv.apply(lambda row: normVec(row), axis=1)

# -- 
# cluster normalalized vectors 

cluster_frame_whv.set_index('label', inplace=True)
cluster_frame2w = pd.DataFrame(cluster_frame_whv['normalized_vector'].values.tolist())
cluster_frame2w.index.names = ['polygon']
cluster_frame2w.columns.names = ['time_slot']

cluster_frame_dhv.set_index('label', inplace=True)
cluster_frame2d = pd.DataFrame(cluster_frame_dhv['normalized_vector'].values.tolist())
cluster_frame2d.index.names = ['polygon']
cluster_frame2d.columns.names = ['time_slot']


# -- 
# PCA whv

pca = PCA(n_components=2)
pca.fit(cluster_frame2w)
pca_cluster_2d_w = pca.transform(cluster_frame2w)
pca_cluster_df_2d_w = pd.DataFrame(pca_cluster_2d_w)
pca_cluster_df_2d_w.index = cluster_frame2w.index
pca_cluster_df_2d_w.columns = ['PC1','PC2']

'''Look at clustering performance week hour'''
print(pca.explained_variance_ratio_) 
# [ 0.23911869  0.13230798]


# -- 
# PCA dhv

pca = PCA(n_components=2)
pca.fit(cluster_frame2d)
pca_cluster_2d_d = pca.transform(cluster_frame2d)
pca_cluster_df_2d_d = pd.DataFrame(pca_cluster_2d_d)
pca_cluster_df_2d_d.index = cluster_frame2d.index
pca_cluster_df_2d_d.columns = ['PC1','PC2']

'''Look at clustering performance week hour'''
print(pca.explained_variance_ratio_) 
# [ 0.12612413  0.07584815]


# -- 
# kmeans n = 3 whv

kmeans = KMeans(n_clusters=3)
clusters = kmeans.fit(cluster_frame2w)
pca_cluster_df_2d_w['cluster'] = pd.Series(clusters.labels_, index=pca_cluster_df_2d_w.index)


# -- 
# kmeans n = 3 dhv

kmeans = KMeans(n_clusters=3)
clusters = kmeans.fit(cluster_frame2d)
pca_cluster_df_2d_d['cluster'] = pd.Series(clusters.labels_, index=pca_cluster_df_2d_d.index)


# -- 
# plot result of preliminary clustering / dim reduction

'''Add color dictionary to centroids: 3 cluster'''
colors = ['yellow', 'red', 'orange']
clrs = []
for i in range(len(colors)): 
    out = {
        'color' : colors[i],
        'cluster' : i
    }
    clrs.append(out)

df_color = pd.DataFrame(clrs)
df_2d_pca_48 = pd.merge(pca_cluster_df_2d_w, df_color, on='cluster', how='left')
df_2d_pca_168 = pd.merge(pca_cluster_df_2d_d, df_color, on='cluster', how='left')

'''Look at plot of clusters: (Not great but move on / compare to denormalized plot'''
# df_2d_pca_48.plot(kind='scatter', x='PC2', y='PC1', c=df_2d_pca_48.color, figsize=(16,8))
# df_2d_pca_168.plot(kind='scatter', x='PC2', y='PC1', c=df_2d_pca_168.color, figsize=(16,8))
# week hour looks much better than day hour


# -- 
# Join cluster id back to dataframe on polygon label: this is a unique id for vectors

df_2d_pca_48.reset_index(inplace=True)
df_2d_pca_48.columns = ['label', 'PC1', 'PC2', 'cluster', 'color']
df_plotw = pd.merge(df_2d_pca_48, cluster_frame_whv, on='label', how='left')
df_plot_groupedw = df_plotw.groupby('cluster').agg({'normalized_vector':(lambda x: list(x))})
df_plot_groupedw.reset_index(inplace=True)

df_2d_pca_168.reset_index(inplace=True)
df_2d_pca_168.columns = ['label', 'PC1', 'PC2', 'cluster', 'color']
df_plotd = pd.merge(df_2d_pca_168, cluster_frame_dhv, on='label', how='left')

'''write out polygons with cluster assignment for validation against baidu labels'''
df_plotd.to_csv('../data/polygons-cluster-assignment.csv')

df_plot_groupedd = df_plotd.groupby('cluster').agg({'normalized_vector':(lambda x: list(x))})
df_plot_groupedd.reset_index(inplace=True)


# -- 
# Agregate average vectors from aggregates based on cluster-label assignment

df_plot_groupedw['avg_vec'] = df_plot_groupedw.apply(lambda row: getAvgVec(row), axis=1)
df_plot_groupedw = df_plot_groupedw[['cluster', 'avg_vec']]

df_plot_groupedd['avg_vec'] = df_plot_groupedd.apply(lambda row: getAvgVec(row), axis=1)
df_plot_groupedd = df_plot_groupedd[['cluster', 'avg_vec']]


# -- 
# Plot spectral signature graphs day hours 

# df_plot_grouped = df_plot_groupedd
# df_plot_grouped = df_plot_groupedw
'''Plot all clusters (replicate Frias-Martinez signature graphs)'''
x = np.array(df_plot_grouped.iloc[0]['avg_vec'])
ind = len(df_plot_grouped.iloc[0].avg_vec)
y = range(ind)

fig, ax = plt.subplots()
line = ind / 2

'''PLotting for three clusters'''
x1 = np.array(df_plot_grouped.iloc[1]['avg_vec'])
x2 = np.array(df_plot_grouped.iloc[2]['avg_vec'])

'''Plotting for three clusters'''
plt.subplot(1, 3, 1)
plt.plot(y, x)
plt.axvline(x=line, color='blue')
plt.title('Spectral Graphs: Naive Kmeans')
plt.ylabel('Cluster 0')

plt.subplot(1, 3, 2)
plt.plot(y, x1)
plt.axvline(x=line, color='blue')
plt.ylabel('Cluster 1')

plt.subplot(1, 3, 3)
plt.plot(y, x2)
plt.axvline(x=line, color='blue')
plt.ylabel('Cluster 2')

if ind in (48, 168):
    unit = 'hour' 
elif ind in (144, 504): 
    unit = 'segment'

plt.xlabel(str(ind) + ' Component Period (' + unit + ')')

plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)

path = './plots/cluster-all-test-' + str(ind) + '-' + unit + '-split-line.png'
# plt.savefig(path)
plt.show()


# -- 
# make polygon frame to prepare for geoplot

polys = whv.groupby('label').agg({'polygon' : 'max'})
polys.reset_index(inplace=True)
polys['pgon'] = polys.apply(lambda row: coercePolygon(row), axis=1)


# -- 
# join to whv and dhv frames

df_plot_polyw = pd.merge(df_2d_pca_48, polys, on='label', how='left')
df_plot_polyw.reset_index(inplace=True)

df_plot_polyd = pd.merge(df_2d_pca_168, polys, on='label', how='left')
df_plot_polyd.reset_index(inplace=True)


# -- 
# load base geojson file to plot polygon cluster assignment

with open("../data/beijing.geojson") as json_file:
    json_data = geojson.load(json_file)


# -- 
# plot polygons with cluster assignment

'''Plot geojson polygons'''
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
        continue


'''Demo plot polygon with color fill'''
# df_plot_poly = df_plot_polyw
df_plot_poly = df_plot_polyd

for i in range(len(polys)): 
    verts = df_plot_poly.iloc[i]['pgon']
    color = df_plot_poly.iloc[i]['color']
    pList = [Point(i) for i in verts]
    poly = geometry.Polygon([[p.x, p.y] for p in pList])
    x,y = poly.exterior.xy
    ax.plot(x, y, color='black', alpha=0.7,# color='#6699cc', alpha=0.7,
        linewidth=1.25, solid_capstyle='round', zorder=2)
    ring_mixed = Polygon(verts)
    ring_patch = PolygonPatch(ring_mixed, fc=color)
    ax.add_patch(ring_patch)

'''Limit axis to focus region'''
dfWB = pd.read_csv('../data/inLabelRegionPoints.csv')
maxLon, minLon = np.max(dfWB['lon']), np.min(dfWB['lon'])
maxLat, minLat = np.max(dfWB['lat']), np.min(dfWB['lat'])
ax.set_xlim(maxLon, minLon)
ax.set_ylim(maxLat, minLat)

'''Reveal plot'''
plt.show()
