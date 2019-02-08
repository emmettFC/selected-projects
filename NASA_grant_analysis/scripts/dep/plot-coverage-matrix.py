
'''
    Plot sparse vectors: 
        I: Evaluating distribution of vector components
        II: Making a matrix to show coverage
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
import seaborn as sns
pd.set_option('display.expand_frame_repr', False)


# -- 
# user defined functions

def fixLstring(row): 
    v = row['combined']
    s = v[1:-1].split(', ')
    s = [np.float(i) for i in s]
    return s


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
# plot binary matrix for day hour 

dhv_vectors = dhv.combined_list.values.tolist()
dhv_binary = []
for i in dhv_vectors: 
    out = []
    for r in i: 
        if r == 0: 
            out.append(0)
        else: 
            out.append(1)
    dhv_binary.append(out)


dhv_binary_array = np.array(dhv_binary)
G = np.zeros((86,48,3))
G[dhv_binary_array>0] = [1,1,1]
G[dhv_binary_array<1] = [0,0,0]

plt.imshow(G,interpolation='nearest')
plt.show()


# -- 
# plot sums for day hour

'''Pure python and matplotlib'''
df_binary = pd.DataFrame(dhv_binary_array)
y = [] 
for i in range(168): 
    n = df_binary[i].sum()
    y.append(n)

plt.bar(range(168), y)
plt.show()

'''seaborn'''
sns.set()
sns.heatmap(df_binary)
plt.show()


# -- 
# plot binary matrix for week hour

whv_vectors = whv.combined_list.values.tolist()
whv_binary = []
for i in whv_vectors: 
    out = []
    for r in i: 
        if r == 0: 
            out.append(0)
        else: 
            out.append(1)
    whv_binary.append(out)

whv_binary_array = np.array(whv_binary)
G = np.zeros((86,48,3))
G[whv_binary_array>0] = [1,1,1]
G[whv_binary_array<1] = [0,0,0]

plt.imshow(G,interpolation='nearest')
plt.show()


# -- 
# plot sums for week hour

'''Pure python and matplotlib'''
df_binary = pd.DataFrame(whv_binary_array)
y = [] 
for i in range(168): 
    n = df_binary[i].sum()
    y.append(n)

plt.bar(x, y)
plt.show() 

'''seaborn'''
sns.set()
sns.heatmap(df_binary)
plt.show()

