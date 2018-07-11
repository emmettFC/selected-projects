
'''
    Plot sparse vectors: 
        I: Evaluating distribution of vector components
        II: Making a matrix to show coverage
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
pd.set_option('display.expand_frame_repr', False)


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

whv = pd.read_csv('./data/week-hour-vectors.csv')
whv['combined_list'] = whv.apply(lambda row: fixLstring(row), axis=1)
len(whv.iloc[0].combined_list) # 48 dim, correct
# [ 0.22319044  0.16556947]

wsv = pd.read_csv('./data/week-segment-vectors.csv')
wsv['combined_list'] = wsv.apply(lambda row: fixLstring(row), axis=1)
len(wsv.iloc[0].combined_list) # 144 dim, correct
# [ 0.12599064  0.09439987]


# -- 
# Plot binary matrix 

dhv.head() 
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
# Plot sum to see if you can verify this 

'''seaborn'''

sns.set()
sns.heatmap(df_binary)
plt.show()



'''Pure python and matplotlib'''

# x = range(168)
# x = range(48)

df_binary = pd.DataFrame(dhv_binary_array)

y = [] 
# for i in range(168): 
for i in range(48): 
    n = df_binary[i].sum()
    y.append(n)

plt.bar(x, y)








