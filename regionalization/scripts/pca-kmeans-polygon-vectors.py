
'''
    Data Driven Yale: Analytical regionalization & Social media data
        I: Trial 2D PCA & Kmeans clustering of polygon vectors
        II: Make signature graphs for each cluster (re FM)
'''

# -- 
# Dependancies

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


# -- 
# IO 

def fixLstring(row): 
    v = row['combined']
    s = v[1:-1].split(', ')
    s = [np.float(i) for i in s]
    return s

dhv = pd.read_csv('./data/day-hour-vectors.csv')
dhv['combined_list'] = dhv.apply(lambda row: fixLstring(row), axis=1)
len(dhv.iloc[0].combined_list) # 168 dim, correct
# [ 0.11674758  0.0951933 ]

dsv = pd.read_csv('./data/day-segment-vectors.csv')
dsv['combined_list'] = dsv.apply(lambda row: fixLstring(row), axis=1)
len(dsv.iloc[0].combined_list) # 504 dim, correct
# [ 0.06345558  0.04879742]

whv = pd.read_csv('./data/week-hour-vectors.csv')
whv['combined_list'] = whv.apply(lambda row: fixLstring(row), axis=1)
len(whv.iloc[0].combined_list) # 48 dim, correct
# [ 0.22319044  0.16556947]

wsv = pd.read_csv('./data/week-segment-vectors.csv')
wsv['combined_list'] = wsv.apply(lambda row: fixLstring(row), axis=1)
len(wsv.iloc[0].combined_list) # 144 dim, correct
# [ 0.12599064  0.09439987]

# -- 
# Run PCA and kmeans clustering on aggregate vectors

'''Process can be repeated for each of the four frames above'''

def normVec(row): 
    v = row['combined']
    d = np.sum(v)
    norm = [np.float(i)/np.float(d) for i in v]
    return norm

'''Change this line to point to correct frame'''
# cluster_frame = wsv[['label', 'combined_list']]
cluster_frame = whv[['label', 'combined_list']]
# cluster_frame = dhv[['label', 'combined_list']]
# cluster_frame = dsv[['label', 'combined_list']]

'''Generic process'''
cluster_frame.columns = ['label', 'combined']
cluster_frame['normalized_vector'] = cluster_frame.apply(lambda row: normVec(row), axis=1)

'''Cluster normalized vectors'''
cluster_frame.set_index('label', inplace=True)
cluster_frame2 = pd.DataFrame(cluster_frame['normalized_vector'].values.tolist())
cluster_frame2.index.names = ['polygon']
cluster_frame2.columns.names = ['time_slot']

pca = PCA(n_components=2)

pca.fit(cluster_frame2)
pca_cluster_2d = pca.transform(cluster_frame2)
pca_cluster_df_2d = pd.DataFrame(pca_cluster_2d)
pca_cluster_df_2d.index = cluster_frame2.index
pca_cluster_df_2d.columns = ['PC1','PC2']
pca_cluster_df_2d.head()

'''Look at clustering performance'''
print(pca.explained_variance_ratio_) 
# ax = pca_cluster_df_2d.plot(kind='scatter', x='PC2', y='PC1', figsize=(16,8))
# kmeans = KMeans(n_clusters=5)
kmeans = KMeans(n_clusters=3)
clusters = kmeans.fit(cluster_frame2)
pca_cluster_df_2d['cluster'] = pd.Series(clusters.labels_, index=pca_cluster_df_2d.index)

'''Add color dictionary to centroids: 5 cluster'''
colors = ['red', 'blue', 'orange', 'yellow', 'green'] 
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
df_2d_pca_48 = pd.merge(pca_cluster_df_2d, df_color, on='cluster', how='left')

'''Look at plot of clusters: (Not great but move on / compare to denormalized plot'''
# df_2d_pca_48.plot(kind='scatter', x='PC2', y='PC1', c=df_2d_pca_48.color, figsize=(16,8))


'''Join cluster id back to dataframe on polygon label: this is a unique id for vectors'''
df_2d_pca_48.reset_index(inplace=True)
df_2d_pca_48.columns = ['label', 'PC1', 'PC2', 'cluster', 'color']
df_plot = pd.merge(df_2d_pca_48, cluster_frame, on='label', how='left')
df_plot_grouped = df_plot.groupby('cluster').agg({'normalized_vector':(lambda x: list(x))})
df_plot_grouped.reset_index(inplace=True)

'''Agregate average vectors from aggregates based on cluster-label assignment'''
def getAvgVec(row): 
    vecs = np.array(row['normalized_vector'])
    comb = np.mean(vecs, axis=0)
    return comb

df_plot_grouped['avg_vec'] = df_plot_grouped.apply(lambda row: getAvgVec(row), axis=1)
df_plot_grouped = df_plot_grouped[['cluster', 'avg_vec']]


# -- 
# Plot spectral signature graphs

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


'''PLotting for five clusters'''
# x1 = np.array(df_plot_grouped.iloc[1]['avg_vec'])
# x2 = np.array(df_plot_grouped.iloc[2]['avg_vec'])
# x3 = np.array(df_plot_grouped.iloc[3]['avg_vec'])
# x4 = np.array(df_plot_grouped.iloc[4]['avg_vec'])

'''Plotting for five clusters'''
# plt.subplot(2, 3, 1)
# plt.plot(y, x)
# plt.axvline(x=line, color='blue')
# plt.title('Spectral Graphs: Naive Kmeans')
# plt.ylabel('Cluster 0')

# plt.subplot(2, 3, 2)
# plt.plot(y, x1)
# plt.axvline(x=line, color='blue')
# plt.ylabel('Cluster 1')

# plt.subplot(2, 3, 3)
# plt.plot(y, x2)
# plt.axvline(x=line, color='blue')
# plt.ylabel('Cluster 2')

# plt.subplot(2, 3, 4)
# plt.plot(y, x3)
# plt.axvline(x=line, color='blue')
# plt.ylabel('Cluster 3')

# plt.subplot(2, 3, 5)
# plt.plot(y, x4)
# plt.axvline(x=line, color='blue')
# plt.ylabel('Cluster 4')

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
# Plot polygons with cluster color (going to be hard, string shit)

# df_2d_pca_48.head() 
# len(df_2d_pca_48)

polys = whv.groupby('label').agg({'polygon' : 'max'})
polys.reset_index(inplace=True)

'''Check type of the variable'''
# rec = polys.iloc[0]['polygon']
# type(rec)

'''Coerce variable back to polygon'''
# rec = rec.replace('POLYGON ((', ''). replace('))', '')
# rec = rec.split(', ')
# rec = [i.split(' ') for i in rec]
# verts = []
# for i in rec: 
#     vert = [np.float(v) for v in i]
#     vert = tuple(vert)
#     verts.append(vert)


'''Make into function and coerce all polygons'''

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

polys['pgon'] = polys.apply(lambda row: coercePolygon(row), axis=1)


'''Join back to frame with cluster labels'''

df_plot_poly = pd.merge(df_2d_pca_48, polys, on='label', how='left')
df_plot_poly.reset_index(inplace=True)

'''Load geojson polygons to plot underneath'''

with open("./data/beijing.geojson") as json_file:
    json_data = geojson.load(json_file)

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
        print('failed to add polygon with index ' + str(i))

'''Plot Voronoi polygons'''
# for i in range(len(polys)): 
#     print(i)
#     verts = polys.iloc[i]['pgon']
#     pList = [Point(i) for i in verts]
#     poly = geometry.Polygon([[p.x, p.y] for p in pList])
#     x,y = poly.exterior.xy
#     ax.plot(x, y, color='black', alpha=0.7,# color='#6699cc', alpha=0.7,
#         linewidth=1.25, solid_capstyle='round', zorder=2)

'''Demo plot polygon with color fill'''
# from matplotlib import pyplot as plt
# from shapely.geometry.polygon import Polygon
# from descartes import PolygonPatch

for i in range(len(polys)): 
    print(i)
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
dfWB = pd.read_csv('./data/inLabelRegionPoints.csv')
maxLon, minLon = np.max(dfWB['lon']), np.min(dfWB['lon'])
maxLat, minLat = np.max(dfWB['lat']), np.min(dfWB['lat'])
ax.set_xlim(maxLon, minLon)
ax.set_ylim(maxLat, minLat)

'''Reveal plot'''
plt.show()




