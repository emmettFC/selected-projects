'''
    Replicate Stumpf Implementation from Ehes & Rooney (2015)
        I: WV2 Multispectral images of Carie Bow Marine Quay
        II: Passive depth soundings over subset of ROI
'''

# -- 
# Dependancies 

import pandas as pd
from math import log
import numpy as np
import statsmodels.api as sm

import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns 

from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


# -- 
# IO (costal blue & yellow bands)

cyRel = pd.read_csv('/Users/culhane/Desktop/cy-relbath/cy-relbath-intersect.csv')
cySlim = cyRel[['Depth', 'relBathCYp']]
dataIn = cySlim.loc[cySlim['Depth'] >0]


# -- 
# Udfs

def getError(y_pred, y_test): 
    errors = [] 
    for i in range(len(y_pred)): 
        error = list(y_test)[i] - y_pred[i]
        error = abs(error)
        errors.append(error)
    return np.mean(error)


# -- 
# Build baseline model for 30 meters 

# I: 30 meter limit
data = dataIn.loc[dataIn['Depth'] <= 30]
X_train, X_test, y_train, y_test = train_test_split(data['relBathCYp'], data['Depth'], test_size=0.25, random_state=42)
# X_train = X_train.reshape(-1, 1)
X_train = X_train.values.reshape(-1, 1)
X_test = X_test.values.reshape(-1, 1)
lm = linear_model.LinearRegression()
lm.fit(X_train, y_train)
y_pred = lm.predict(X_test)

metrics30 = {
    'mse' : mean_squared_error(y_test, y_pred),
    'r2' : r2_score(y_test, y_pred), 
    'rmse' : np.sqrt(mean_squared_error(y_test, y_pred)),
    'error' : getError(y_pred, y_test)
}

# plt.scatter(X_test, y_test,  color='black')
# plt.plot(X_test, y_pred, color='blue', linewidth=3)

# ymin, ymax = plt.ylim() 
# xmin, xmax = plt.xlim() 
# plt.xlim(xmin, 1.18)
# plt.ylim(0, 30)


# II: 15 meter limit
data2 = dataIn.loc[dataIn['Depth'] <= 15]
X_train2, X_test2, y_train2, y_test2 = train_test_split(data2['relBathCYp'], data2['Depth'], test_size=0.25, random_state=42)
X_train2 = X_train2.values.reshape(-1, 1)
X_test2 = X_test2.values.reshape(-1, 1)
lm = linear_model.LinearRegression()
lm.fit(X_train2, y_train2)
y_pred2 = lm.predict(X_test2)

metrics15 = {
    'mse' : mean_squared_error(y_test2, y_pred2),
    'r2' : r2_score(y_test2, y_pred2),
    'rmse' : np.sqrt(mean_squared_error(y_test2, y_pred2)),
    'error' : getError(y_pred2, y_test2)
}



sns.set_style('white')

dfPlot = pd.DataFrame(X_test, y_test) 
dfPlot.reset_index(inplace=True)
dfPlot.columns = ['Depth', 'Relative Bathymetry']
sns.pairplot(dfPlot, x_vars=['Relative Bathymetry'], y_vars='Depth')
plt.plot(X_test, y_pred, color='red', label='30 Meters: ' + str(round(metrics30['rmse'],3)) + ' RMSE', linewidth=1)
plt.plot(X_test2, y_pred2, color='blue', label='15 Meters: ' + str(round(metrics15['rmse'],3)) + ' RMSE', linewidth=1)
# plt.plot(x, y)
ymin, ymax = plt.ylim() 
plt.ylim(0, ymax)
plt.legend()
plt.show()


# III: Run regression with squared term included 


data2 = dataIn.loc[dataIn['Depth'] <= 15]
data2['rb2'] = data2.apply(lambda row: row['relBathCYp']**2, axis=1)



# X_train2, X_test2, y_train2, y_test2 = train_test_split([data2['relBathCYp'], data2['relBathCYp']], data2['Depth'], test_size=0.25, random_state=42)


import pandas

import random

df = pandas.DataFrame(np.random.randn(100, 4), columns=list('ABCD'))

rows = random.sample(data2.index, 550)

df_10 = data2.ix[rows]

df_90 = data2.drop(rows)



# X_train2 = X_train2.values.reshape(-1, 1)
# X_test2 = X_test2.values.reshape(-1, 1)


dat = df_90.as_matrix()

Yt = np.array(df_90['Depth'])
Xt = np.array(df_90['relBathCYp'])


# x_array = np.array(X_train)
x_terms = [] 
for i in range(3): 
    x_terms.append(Xt**i)



mat = np.dstack(tuple(x_terms))
m = np.asmatrix(mat)
mT = m.transpose() 
mTm = np.matmul(mT, m)
pInv = np.matmul(mTm.I, mT)
w = np.matmul(pInv, Yt)


x = np.linspace(0, 2, 100)

y = get_line(w)

plt.scatter(df_90['relBathCYp'], df_90['Depth'])
plt.plot(x, y)
plt.axis([0, 2, 0, 20])


def get_line(mat): 
    dims = mat.shape
    n_vars = dims[1]
    x = np.linspace(-1, 3, 100)
    x_vecs = []
    for i in x: 
        xv = []
        for n in range(n_vars): 
            xv.append(i**n)
        x_vecs.append(xv)
    coefs = np.array(mat[[0]])[0]
    y_pred = []
    for r in x_vecs: 
        y_pred.append(np.dot(coefs, r))
    return y_pred



mat = np.dstack(tuple(x_terms))


lm = linear_model.LinearRegression()
lm.fit(X_train2, y_train2)
y_pred2 = lm.predict(X_test2)




X = data['x_vector']
Y = data['y_w_noise']
x_terms = [] 
for i in range(degree + 1): 
    x_terms.append(X**i)
mat = np.dstack(tuple(x_terms))
m = np.asmatrix(mat)
mT = m.transpose() 
mTm = np.matmul(mT, m)
pInv = np.matmul(mTm.I, mT)
w = np.matmul(pInv, Y)
















# plt.scatter(X_test2, y_test2,  color='black')
# plt.plot(X_test2, y_pred2, color='red', linewidth=3)

''' 
    metrics30: 
        {'mse': 13.36012027375482, 'error': 4.155762816621339, 'r2': 0.5411737029668209, 'rmse': 3.6551498291800324}
    metrics15 
        {'mse': 3.6734519801584, 'error': 0.9822712072743904, 'r2': 0.5859740412678888, 'rmse': 1.9166251537946588}
'''


# -- 
# Use seaborn to plot: I) Scatter of testing vectors; II) Line of best fit given predictions 

sns.set_style('darkgrid')

dfPlot = pd.DataFrame(X_test, y_test) 
dfPlot.reset_index(inplace=True)
dfPlot.columns = ['Depth', 'Relative Bathymetry']
sns.pairplot(dfPlot, x_vars=['Absolute Bathymetry'], y_vars='Depth')
plt.plot(X_test, y_pred, color='red', label='30 Meters: ' + str(round(metrics30['rmse'],3)) + ' RMSE', linewidth=1)
plt.plot(X_test2, y_pred2, color='blue', label='15 Meters: ' + str(round(metrics15['rmse'],3)) + ' RMSE', linewidth=1)
ymin, ymax = plt.ylim() 
plt.ylim(0, ymax)
plt.legend()
plt.show()


# -- 
# Significance testing metrics (rmse, abs mean difference, coeficients, intercept)

# I: Plot distribution of error 

# -- 
# Apply transformation for non-linear regression 








