'''
    Mathematical Models Final Proejct: 
        I: Evaluate relationship between chl relative ROC and tidal current
        II: Segment by light availability
        III: Experiment with relative ROC current 
'''



# -- 
# dependancies 

import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import linear_model

import statsmodels.api as sm
import numpy as np 
import pandas as pd


# -- 
# io  

reg_data = pd.read_csv('/Users/culhane/Desktop/Math_Papers/chl-tide-analysis-data-clean.csv')
tide_2003 = pd.read_csv('/Users/culhane/Desktop/Math_Papers/tide-2003-clean-analysis-range.csv')


# -- 
# prepare data for regression

y = pd.DataFrame(reg_data['chl_rRoc'], columns = ['chl_rRoc'])
x = pd.DataFrame(reg_data['current'], columns = ['current'])
X = x['current']
Y = y['chl_rRoc']
Xa = np.array(X)
Xa = Xa.reshape(-1, 1)
Y = np.array(Y)
xtrain = Xa[:-500]
xtest = Xa[-500:]
ytrain = Y[:-500]
ytest = Y[-500:]


# -- 
# run linear OLS regression for chl and tidal current velocity 

''' initialize and run model '''

regr = linear_model.LinearRegression()
regr.fit(xtrain, ytrain)
ypred = regr.predict(xtest)

''' plot results ''' 

plt.scatter(xtest, ytest,  color='black')
plt.plot(xtest, ypred, color='blue', linewidth=3)
plt.xticks(())
plt.yticks(())
plt.show() 

''' generate model summary: {coef = 0.07; mse = 0.03; r2 = 0.21} '''

print('Coefficients: \n', regr.coef_)
print("Mean squared error: %.2f"
      % mean_squared_error(ytest, ypred))
print('Variance score: %.2f' % r2_score(ytest, ypred))


# -- 
# run OLS least squares regression for dark measuments only

''' structure input vectors '''

reg_data_dark = reg_data.loc[reg_data['is_light'] == False]
y = pd.DataFrame(reg_data_dark['chl_rRoc'], columns = ['chl_rRoc'])
x = pd.DataFrame(reg_data_dark['current'], columns = ['current'])
X = x['current']
Y = y['chl_rRoc']
Xa = np.array(X)
Xa = Xa.reshape(-1, 1)
Y = np.array(Y)
xtrain = Xa[:-500]
xtest = Xa[-500:]
ytrain = Y[:-500]
ytest = Y[-500:]


''' instantiate and run model '''

regr = linear_model.LinearRegression()
regr.fit(xtrain, ytrain)
ypred = regr.predict(xtest)

''' plot model output '''

plt.scatter(xtest, ytest,  color='black')
plt.plot(xtest, ypred, color='blue', linewidth=3)
plt.xticks(())
plt.yticks(())
plt.show() 

''' generate model summary: {rcoef = 0.053; mse = 0.04; r2 = 0.18} '''

print('Coefficients: \n', regr.coef_)
print("Mean squared error: %.2f"
      % mean_squared_error(ytest, ypred))
print('Variance score: %.2f' % r2_score(ytest, ypred))


# --
# run OLS least squares for model with relative rate of change for current instead of raw 

''' structure input vectors '''

y = pd.DataFrame(reg_data_dark['chl_rRoc'], columns = ['chl_rRoc'])
x = pd.DataFrame(reg_data_dark['current_rRoc'], columns = ['current_rRoc'])
X = x['current_rRoc']
Y = y['chl_rRoc']
Xa = np.array(X)
Xa = Xa.reshape(-1, 1)
Y = np.array(Y)
xtrain = Xa[:-500]
xtest = Xa[-500:]
ytrain = Y[:-500]
ytest = Y[-500:]


''' instantiate and run model '''

regr = linear_model.LinearRegression()
regr.fit(xtrain, ytrain)
ypred = regr.predict(xtest)

''' plot model output '''

plt.scatter(xtest, ytest,  color='black')
plt.plot(xtest, ypred, color='blue', linewidth=3)
plt.xticks(())
plt.yticks(())
plt.show() 

''' generate model summary: {model is not performant} '''

print('Coefficients: \n', regr.coef_)
print("Mean squared error: %.2f"
      % mean_squared_error(ytest, ypred))
print('Variance score: %.2f' % r2_score(ytest, ypred))


