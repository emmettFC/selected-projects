'''
    Mathematical Models Final Project Code: 
        I: continuous one dimensional diffusion single source
        II: discrete one dimensional diffusion single source
        III: continuous one dimensional diffusion punctuated source
        IV: discrete one dimensional diffusion punctuated source
        V: discrete one dimensional diffusion punctuated source and sedimentation
        VI: discrete one dimensional diffusion punctuated source, sedimentation and periodic diffusion
'''

# -- 
# dependancies 

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import  colors

from math import sqrt
from math import pi 
from math import exp 
import random

from math import sin, cos 
import pandas as pd

from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn import linear_model

import statsmodels.api as sm
import matplotlib.patches as mpatches


# ---------------------------------------------------------------------------------------------- 
# PART I: continuous one dimensional diffusion ficks law 
# ---------------------------------------------------------------------------------------------- 

''' function for contiuous diffusion '''

def concentrate(D,x,t, p0):
    cxt = (p0/(sqrt(4*pi*D*t))) * exp((-x**2)/(4*D*t))
    return cxt


def init_vectors(xMin, xMax, pindex, p0):
    l1 = range(xMin, xMax)
    l = [0]*len(l1)
    l[pindex] = p0
    return l1, l

''' initial conditions '''

params = {
        'dx' : 1, 
        'dt' : 1, 
        'p0' : 500
}

D = float(0.5) * float(params['dx']**2/params['dt'])

l1, l = init_vectors(-40, 40, 40, params['p0'])

''' run for specified time steps ''' 

vectors = [] 
for t in [1, 5, 10, 15, 20, 25, 30, 35]: 
    out = [] 
    for i in range(0, len(l1)):
        x = l1[i]
        out.append(concentrate(D,x,t,params['p0']))
    vectors.append(out)


''' plot time distributions of concentration '''

for v in vectors: 
    plt.plot(l1, v, 'Gray',label='numerical')

plt.show()



# ---------------------------------------------------------------------------------------------- 
# PART II: discrete one dimensional diffusion ficks law 
# ---------------------------------------------------------------------------------------------- 

''' functions for discrete time diffusion '''

def discreteC(D, dt, dx, vect, x):
    ct0 = vect[x]
    cx1 = vect[x+1]
    cxm1 = vect[x-1]
    cxt1 = (1 - ((2*D*dt)/(dt**2))) * ct0 + (((D*dt)/(dx**2)) * (cx1 + cxm1))
    return cxt1

def buildNextVector(vector_in): 
    vector_out = [] 
    for i in range(len(vector_in)): 
        if i == 0: 
            out = 0
        elif i == len(vector_in) - 1: 
            out = 0 
        else: 
            out = discreteC(D, dt, dx, vector_in, i)
        vector_out.append(out)
    return vector_out


''' initial conditions '''

params['Dd'] = 0.25

l1, l = init_vectors(-40, 40, 40, params['p0'])

t_vectors = [] 
t_vectors.append(l)


''' run for indices 0-300 '''

t = 1
while t <= 300: 
    index = t - 1
    inVec = t_vectors[index]
    out = buildNextVector(inVec)
    t_vectors.append(out)
    t += 1

for v in t_vectors: 
    plt.plot(l1, v, 'Gray',label='numerical')

plt.show()


# ---------------------------------------------------------------------------------------------- 
# PART III: continuous punctuated / dependant diffusion 
# ---------------------------------------------------------------------------------------------- 

''' define functions for cont puntuated diffusion '''

def convolution_mutiple(D, x, t, punct_points):
    cxt = sum([get_term(i, D, t, x) for i in punct_points])
    return cxt

def build_x_vector(positions, value, length): 
    l = [0] * length
    for p in positions: 
        l[p] = value
    return l 

def get_term(E, D, t, x):
    return ((E)/(sqrt(4*pi*D*t)))*exp(-1*(((x-E)**2)/(4*D*t)))


''' initial conditions '''

params['p0'] = 600
D = float(0.25) * float(params['dx']**2/params['dt'])

positions = random.sample(range(0, 80), 3)
value = 200
ranIn = build_x_vector(positions, value, 81)
punct_points = len(positions) * [value]


''' run for specified time steps ''' 

vectors = [] 
for t in ((40 * i) for i in range(1,100)): 
    out = [] 
    for i in range(0, len(ranIn)):
        x = ranIn[i]
        out.append(convolution_mutiple(D, x, t, punct_points))
    vectors.append(out)


''' plot time distributions of concentration '''

for v in vectors: 
    plt.plot(l1, v, 'Gray',label='numerical')

for i in positions: 
    plt.axvline(l1[i], color='r')

plt.show()



# ---------------------------------------------------------------------------------------------- 
# PART IV: discrete punctuated / independant diffusion 
# ---------------------------------------------------------------------------------------------- 

''' functions for punctuated & dependant diffusion '''

def discreteC(D, dt, dx, vect, x):
    ct0 = vect[x]
    cx1 = vect[x+1]
    cxm1 = vect[x-1]
    cxt1 = (1 - ((2*D*dt)/(dt**2))) * ct0 + (((D*dt)/(dx**2)) * (cx1 + cxm1))
    return cxt1

def buildNextVector(vector_in): 
    vector_out = [] 
    for i in range(len(vector_in)): 
        if i == 0: 
            out = 0
        elif i == len(vector_in) - 1: 
            out = 0 
        else: 
            out = discreteC(D, dt, dx, vector_in, i)
        vector_out.append(out)
    return vector_out

def init_vectors(xMin, xMax, pindex, p0):
    l1 = range(xMin, xMax)
    l = [0]*len(l1)
    l[pindex] = p0
    return l1, l

def iterate_timesteps(niter, tinit, initvec):
    matrix = [] 
    matrix.append(initvec)
    t = tinit
    while t <= niter: 
        index = t - 1
        inVec = matrix[index]
        out = buildNextVector(inVec)
        matrix.append(out)
        t += 1
    return matrix

def combine_vectors(vecA, vecB):
    combined_vectors = [] 
    for i in range(len(vecA)):
        cvec = []
        for n in range(len(vecA[i])):
            cvec.append(vecA[i][n] + vecB[i][n])
        combined_vectors.append(cvec)
    return combined_vectors


''' init params and run functions to build matrix out '''

dt = params['dt']
dx = params['dx']
D = params['Dd']

l1, la = init_vectors(-40, 40, 60, 500)
l1, lb = init_vectors(-40, 40, 20, 500)

t_vec_a = iterate_timesteps(1000, 1, la)
t_vec_b = iterate_timesteps(1000, 1, lb)

combined = combine_vectors(t_vec_a, t_vec_b)


''' plot specific curves for t steps '''

plt.plot(l1, combined[100], 'blue',label='numerical')
plt.plot(l1, combined[250], 'black',label='numerical')
plt.plot(l1, combined[500], 'yellow',label='numerical')
plt.plot(l1, combined[750], 'green',label='numerical')
plt.plot(l1, combined[1000], 'red',label='numerical')


bl_patch = mpatches.Patch(color='blue', label='t=100')
b_patch = mpatches.Patch(color='black', label='t=250')
y_patch = mpatches.Patch(color='yellow', label='t=500')
g_patch = mpatches.Patch(color='green', label='t=750')
r_patch = mpatches.Patch(color='red', label='t=1000')
plt.legend(handles=[bl_patch, b_patch, y_patch, g_patch, r_patch])

plt.show()


# ---------------------------------------------------------------------------------------------- 
# PART V: discrete punctuated diffusion with sedimentation 
# ---------------------------------------------------------------------------------------------- 

''' redefine function to include sedimentation '''

def discreteCSed(D, dt, dx, vect, x, Ws):
    c0 = vect[x]
    c1 = vect[x+1]
    c3 = vect[x-1]
    B1 = (dt * D)/(dx**2)
    B2 = (Ws * dt)/(2*dx)
    cxt1 = ((B1 + B2) * c1) + ((B1 - B2) * c3) + (1 - (2*B1)) * c0
    # cxt1 = (1 - ((2*D*dt)/(dt**2))) * ct0 + (((D*dt)/(dx**2)) * (cx1 + cxm1))
    return cxt1

def buildNextVectorSed(vector_in): 
    vector_out = [] 
    for i in range(len(vector_in)): 
        if i == 0: 
            out = 0
        elif i == len(vector_in) - 1: 
            out = 0 
        else: 
            out = discreteCSed(D, dt, dx, vector_in, i, Ws)
        vector_out.append(out)
    return vector_out

def iterate_timestepsSed(niter, tinit, initvec):
    matrix = [] 
    matrix.append(initvec)
    t = tinit
    while t <= niter: 
        index = t - 1
        inVec = matrix[index]
        out = buildNextVectorSed(inVec)
        matrix.append(out)
        t += 1
    return matrix

''' initial conditions '''

params['Ws'] = 0.025
# params['Ws'] = 0.5
dt = params['dt']
dx = params['dx']
D = params['Dd']
Ws = params['Ws']

l1, la = init_vectors(-40, 40, 60, 500)
l1, lb = init_vectors(-40, 40, 20, 500)

t_vec_a = iterate_timestepsSed(10000, 1, la)
t_vec_b = iterate_timestepsSed(10000, 1, lb)

combined = combine_vectors(t_vec_a, t_vec_b)


''' plot specific curves for t steps '''

plt.plot(l1, combined[100], 'blue',label='numerical')
plt.plot(l1, combined[250], 'black',label='numerical')
plt.plot(l1, combined[500], 'yellow',label='numerical')
plt.plot(l1, combined[750], 'green',label='numerical')
plt.plot(l1, combined[1000], 'red',label='numerical')

bl_patch = mpatches.Patch(color='blue', label='t=100')
b_patch = mpatches.Patch(color='black', label='t=250')
y_patch = mpatches.Patch(color='yellow', label='t=500')
g_patch = mpatches.Patch(color='green', label='t=750')
r_patch = mpatches.Patch(color='red', label='t=1000')
plt.legend(handles=[bl_patch, b_patch, y_patch, g_patch, r_patch])

plt.show()


''' plot loss of density of particles over the period t '''

n_particles = [sum(i) for i in combined]
steps = range(0,1001)
plt.plot(steps, n_particles, 'red',label='numerical')


# ----------------------------------------------------------------------------------------------------
# PART V: comparison of model with and without sedimentation for 6 hour period with params from paper
# ----------------------------------------------------------------------------------------------------

# params['Ws'] = 10**-1
params['Ws'] = 0.025
params['Dd'] = 10**-1


''' initial conditions '''

dt = params['dt']
dx = params['dx']
D = params['Dd']
Ws = params['Ws']


''' WITHOUT SEDIMENTATION '''

l1, la = init_vectors(-8, 8, -4, 500)
l1, lb = init_vectors(-8, 8, 4, 500)

t_vec_a = iterate_timesteps(3600, 1, la)
t_vec_b = iterate_timesteps(3600, 1, lb)

combined_noSed = combine_vectors(t_vec_a, t_vec_b)


''' WITH SEDIMENTATION '''

l1, la = init_vectors(-8, 8, -4, 500)
l1, lb = init_vectors(-8, 8, 4, 500)

t_vec_a = iterate_timestepsSed(3600, 1, la)
t_vec_b = iterate_timestepsSed(3600, 1, lb)

combined_wSed = combine_vectors(t_vec_a, t_vec_b)


''' visualize and explore results '''

fig = plt.figure()
indices = [(100, 'black'), (600, 'blue'), (1200, 'green'), (1800, 'yellow'), (3400, 'red')]
# indicesa = [(100, 'blue')]
# indicesb = [(100, 'red')]
plt.subplot(2, 1, 1)
for i in indices: 
    plt.plot(l1, combined_noSed[i[0]], i[1],label='numerical')


plt.subplot(2, 1, 2)
for i in indices: 
    plt.plot(l1, combined_wSed[i[0]], i[1],label='numerical')

# bl_patch = mpatches.Patch(color='blue', label='without sedimentation')
# b_patch = mpatches.Patch(color='black', label='with sedimentation Ws=0.02')

# plt.legend(handles=[bl_patch, b_patch])

plt.show()



''' very flat behavior of sedimentation function, seems there are negatives or rapid loss of overall matter '''
''' there is both rapid loss of particles and rapid sedimentation to the bottom with Ws = Dd '''

plt.plot(l1, combined_wSed[1], 'red', label='numerical')
plt.plot(l1, combined_wSed[10], 'red', label='numerical')
plt.plot(l1, combined_wSed[30], 'red', label='numerical')
plt.plot(l1, combined_wSed[100], 'red', label='numerical')
plt.plot(l1, combined_wSed[200], 'red', label='numerical')
plt.plot(l1, combined_wSed[200], 'red', label='numerical')
plt.plot(l1, combined_wSed[400], 'red', label='numerical')
plt.show() 

plt.plot(l1, combined_wSed[600], 'red', label='numerical')
plt.show() 


# ---------------------------------------------------------------------------------------------- 
# PART VI: discrete punctuated diffusion with sedimentation & periodic excitation
# ---------------------------------------------------------------------------------------------- 

''' functions for diffusion with sedimentation and periodic excitation '''

def norm_x_val(x, xmean): 
    x, xmean = float(x), float(xmean)
    nx = (xmean - abs(xmean - x)) / xmean
    return float(nx)

def Dxt(nx, t, alpha, Dparam):
    t = float(t) 
    Dparam = float(Dparam)
    alpha = float(alpha)
    dxt = nx*Dparam + nx*alpha*abs(sin((pi*t/21600)))
    return float(dxt)

def discreteCSed(dt, dx, vectC, vectD, x, Ws):
    dt = float(dt) 
    dx = float(dx) 
    Ws = float(Ws)
    C1 = dt/(2*dx)
    C2 = (vectD[x]*dt)/(dx**2)
    C3 = (Ws*dt)/(2*dx)
    B1 = vectD[x+1] - vectD[x-1]
    B2 = vectC[x+1] - vectC[x-1]
    B3 = vectC[x+1] - (2*vectC[x]) + vectC[x-1]
    B4 = vectC[x]
    cxt1 = C1 * (B1*B2) + C2*(B3) + C3 * B2 + B4
    return float(cxt1)

def buildNextVectorSed(vector_inC, vector_inD, t): 
    vector_out_c = [] 
    vector_out_d = []
    for i in range(len(vector_inC)): 
        if i == 0: 
            outC  = 0 
            outD  = 0
        elif i == len(vector_inC) - 1: 
            outC = 0 
            outD = 0
        else: 
            outC = discreteCSed(dt, dx, vector_inC, vector_inD, i, Ws)
            outD = Dxt(norm_x_val(i, xmean), t+1, alpha, Dparam)
        vector_out_c.append(outC)
        vector_out_d.append(outD)
    return vector_out_c, vector_out_d

def iterate_timestepsSed(niter, tinit, initvecC, initvecD):
    matrixC = [] 
    matrixC.append(initvecC)
    matrixD = [] 
    matrixD.append(initvecD)
    t = tinit
    while t <= niter: 
        index = t - 1
        inVecC = matrixC[index]
        inVecD = matrixD[index]
        outC, outD = buildNextVectorSed(inVecC, inVecD, index)
        lossC = 100 - sum(outC)
        outC[1] = outC[1] + lossC
        matrixC.append(outC)
        matrixD.append(outD)
        t += 1
    return matrixC, matrixD


''' paramaters and initial vectors for D and (p1, p1) ''' 

alpha = 0.25
Dparam = 0.25
x_domain = range(0, 21)
xmean = 10
Ws = 0.025
dx = float(1)
dt = float(1)

d_initial = [Dxt(norm_x_val(x, xmean), 0, alpha, Dparam) for x in x_domain]
x_initial_p1 = [0] * 21
x_initial_p1[5] = 100
x_initial_p2 = [0] * 21
x_initial_p2[15] = 100


''' run functions for initial conditions for 10 tidal cycles '''

t_vec_ac, t_vec_ad = iterate_timestepsSed(21600*10, 1, x_initial_p1, d_initial)
t_vec_bc, t_vec_bd = iterate_timestepsSed(21600*10, 1, x_initial_p2, d_initial)

combined = combine_vectors(t_vec_ac, t_vec_bc)


''' plot macro level curves for timesteps at  '''

plt.plot(x_domain, combined[1], 'red', label='numerical')
# plt.plot(x_domain, combined[5400], 'red', label='numerical')
plt.plot(x_domain, combined[10800], 'black', label='numerical')
plt.plot(x_domain, combined[21600], 'blue', label='numerical')
plt.plot(x_domain, combined[32400], 'green', label='numerical')
plt.plot(x_domain, combined[43200], 'yellow', label='numerical')

# plt.show() 


bl_patch = mpatches.Patch(color='red', label='t=1')
b_patch = mpatches.Patch(color='black', label='t=10800')
y_patch = mpatches.Patch(color='blue', label='t=21600')
g_patch = mpatches.Patch(color='green', label='t=32400')
r_patch = mpatches.Patch(color='yellow', label='t=43200')
plt.legend(handles=[bl_patch, b_patch, y_patch, g_patch, r_patch])

plt.show()


''' plot macro curves first in subplot matrix '''

hc = 10800
indices = []
for i in range(18): 
    indices.append(hc*(i+1))



fig, ((ax1,ax2,ax3), (ax4, ax5, ax6), (ax7,ax8,ax9)) = plt.subplots(nrows=3, ncols=3, figsize=(20,20))

ax1.plot(x_domain, combined[1], 'black', label='numerical')
ax1.plot(x_domain, combined[indices[0]], 'red', label='numerical')
ax1.plot(x_domain, combined[indices[1]], 'blue', label='numerical')

ax2.plot(x_domain, combined[indices[2]], 'red', label='numerical')
ax2.plot(x_domain, combined[indices[3]], 'blue', label='numerical')

ax3.plot(x_domain, combined[indices[4]], 'red', label='numerical')
ax3.plot(x_domain, combined[indices[5]], 'blue', label='numerical')

ax4.plot(x_domain, combined[indices[6]], 'red', label='numerical')
ax4.plot(x_domain, combined[indices[7]], 'blue', label='numerical')

ax5.plot(x_domain, combined[indices[8]], 'red', label='numerical')
ax5.plot(x_domain, combined[indices[9]], 'blue', label='numerical')

ax6.plot(x_domain, combined[indices[10]], 'red', label='numerical')
ax6.plot(x_domain, combined[indices[11]], 'blue', label='numerical')

ax7.plot(x_domain, combined[indices[12]], 'red', label='numerical')
ax7.plot(x_domain, combined[indices[13]], 'blue', label='numerical')

ax7.plot(x_domain, combined[indices[14]], 'red', label='numerical')
ax7.plot(x_domain, combined[indices[15]], 'blue', label='numerical')

ax8.plot(x_domain, combined[indices[16]], 'red', label='numerical')
ax8.plot(x_domain, combined[indices[17]], 'blue', label='numerical')

ax9.plot(x_domain, combined[indices[16]], 'red', label='numerical')
ax9.plot(x_domain, combined[indices[17]], 'blue', label='numerical')

plt.subplots_adjust(top=0.92, bottom=0.08, left=0.20, right=0.95, hspace=0.35,
                wspace=0.60)

fig.suptitle('Plot of 1m density at t+3 and t+6 for simulation', fontsize=16)

plt.savefig('/Users/culhane/Desktop/_plank_20.tiff')

plt.show()



''' work to make better plot of particles / then transition to DL pset '''


# fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(20,20))

N = 1000

# for t + 3
t = combined[10800]
z_vec = []
for i in t: 
    try: 
        p = i/200
        n = 1000 * p 
        z_vec.append(int(round(n)))
    except: 
        z_vec.append(0)

coords = []
for i in range(len(z_vec)): 
    for n in range(z_vec[i]): 
        z = random.uniform(i, i+1)
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        coords.append((x, y, z))

zdata = [i[2] for i in coords]
xdata = [i[0] for i in coords]
ydata = [i[1] for i in coords]

# for t + 6
t = combined[21600]
z_vec = []
for i in t: 
    try: 
        p = i/200
        n = 1000 * p 
        z_vec.append(int(round(n)))
    except: 
        z_vec.append(0)

coords = []
for i in range(len(z_vec)): 
    for n in range(z_vec[i]): 
        z = random.uniform(i, i+1)
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        coords.append((x, y, z))

zdata1 = [i[2] for i in coords]
xdata1 = [i[0] for i in coords]
ydata1 = [i[1] for i in coords]

# for t == 0 
t = combined[1]
z_vec = []
for i in t: 
    try: 
        p = i/200
        n = 1000 * p 
        z_vec.append(int(round(n)))
    except: 
        z_vec.append(0)

coords = []
for i in range(len(z_vec)): 
    for n in range(z_vec[i]): 
        z = random.uniform(i, i+1)
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        coords.append((x, y, z))

zdata0 = [i[2] for i in coords]
xdata0 = [i[0] for i in coords]
ydata0 = [i[1] for i in coords]


# debugging plot 
fig = plt.figure()
ax1 = fig.add_subplot(111, projection='3d')
# ax2 = fig.add_subplot(211, projection='3d')
# ax3 = fig.add_subplot(311, projection='3d')
# ax1 = plt.axes(projection='3d')
# ax1.scatter3D(xdata0, ydata0, zdata0, depthshade=0, cmap='Blues')
ax1.scatter(xdata0, ydata0, zdata0, c='black')
ax1.set_xlabel('X - random gaussian')
ax1.set_ylabel('Y - random gaussian')
ax1.set_zlabel('Z - model density P(zn, t)')
ax1.set_title('Plankton density at t=0')

fig = plt.figure()
ax1 = fig.add_subplot(111, projection='3d')
# ax2 = fig.add_subplot(211, projection='3d')
# ax3 = fig.add_subplot(311, projection='3d')
# ax1 = plt.axes(projection='3d')
# ax1.scatter3D(xdata0, ydata0, zdata0, depthshade=0, cmap='Blues')
ax1.scatter(xdata, ydata, zdata, c='blue')
ax1.set_xlabel('X - random gaussian')
ax1.set_ylabel('Y - random gaussian')
ax1.set_zlabel('Z - model density P(zn, t)')
ax1.set_title('Plankton density at t=3')

fig = plt.figure()
ax1 = fig.add_subplot(111, projection='3d')
# ax2 = fig.add_subplot(211, projection='3d')
# ax3 = fig.add_subplot(311, projection='3d')
# ax1 = plt.axes(projection='3d')
# ax1.scatter3D(xdata0, ydata0, zdata0, depthshade=0, cmap='Blues')
ax1.scatter(xdata1, ydata1, zdata1, c='red')
ax1.set_xlabel('X - random gaussian')
ax1.set_ylabel('Y - random gaussian')
ax1.set_zlabel('Z - model density P(zn, t)')
ax1.set_title('Plankton density at t=6')

# ax2 = plt.axes(projection='3d')
ax2 = plt.axes(projection='3d')
ax2.scatter3D(xdata, ydata, zdata, depthshade=0, cmap='Blues')
ax2.set_xlabel('X - random gaussian')
ax2.set_ylabel('Y - random gaussian')
ax2.set_zlabel('Z - model density P(zn, t)')
ax2.set_title('Plankton density at t=3hours')

# ax3 = plt.axes(projection='3d')
ax3 = plt.axes(projection='3d')
ax3.scatter3D(xdata1, ydata1, zdata1, depthshade=0, cmap='Blues')
ax3.set_xlabel('X - random gaussian')
ax3.set_ylabel('Y - random gaussian')
ax3.set_zlabel('Z - model density P(zn, t)')
ax3.set_title('Plankton density at t=6hours')


# fig = plt.figure()
# ax1 = fig.add_subplot(111, projection='3d')
# ax2 = fig.add_subplot(211, projection='3d')
# ax3 = fig.add_subplot(311, projection='3d')
# ax1.scatter(xdata0, ydata0, zdata0, c='black')
# ax1.set_xlabel('X - random gaussian')
# ax1.set_ylabel('Y - random gaussian')
# ax1.set_zlabel('Z - model density P(zn, t)')
# ax1.set_title('Plankton density at t=0')

# ax2.scatter(xdata, ydata, zdata, c='b')
# ax2.set_xlabel('X - random gaussian')
# ax2.set_ylabel('Y - random gaussian')
# ax2.set_zlabel('Z - model density P(zn, t)')
# ax2.set_title('Plankton density at t=3hours')

# ax3.scatter(xdata1, ydata1, zdata1, c='r')
# ax3.set_xlabel('X - random gaussian')
# ax3.set_ylabel('Y - random gaussian')
# ax3.set_zlabel('Z - model density P(zn, t)')
# ax3.set_title('Plankton density at t=6hours')

# # ax.legend()
# plt.show()





x = random.uniform(0, 1) 
y = random.uniform(0, 1)

coords = []
for i in range(len(z_vec)): 
    for n in range(z_vec[i]): 
        z = random.uniform(i, i+1)
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        coords.append((x, y, z))

from mpl_toolkits import mplot3d


ax = plt.axes(projection='3d')

# # Data for a three-dimensional line
# zline = np.linspace(0, 15, 1000)
# xline = np.sin(zline)
# yline = np.cos(zline)
# ax.plot3D(xline, yline, zline, 'gray')
from mpl_toolkits.mplot3d import *
art3d.zalpha = lambda *args:args[0]

fig = plt.figure()
ax = fig.gca(projection='3d')

# Data for three-dimensional scattered points
zdata = [i[2] for i in coords]
xdata = [i[0] for i in coords]
ydata = [i[1] for i in coords]
ax.scatter3D(xdata, ydata, zdata, c=zdata, depthshade=0, cmap='Greens')

ax.scatter3D(xdata, ydata, zdata, depthshade=0, cmap='Greens')



fig = plt.figure()
ax = fig.gca(projection='3d')
s = ax.scatter3D(xdata, ydata, zdata, c=zdata, alpha =1, cmap='Greens')
s.set_edgecolors = s.set_facecolors = lambda *args:None

ax.legend()
ax.set_xlim3d(0, 1)
ax.set_ylim3d(0, 1)
ax.set_zlim3d(0, 1)

plt.show()




ax7.plot(x_domain, combined[indices[14]], 'red', label='numerical')
ax7.plot(x_domain, combined[indices[15]], 'blue', label='numerical')









''' plot density of particles in top 1 meter over mutliple cycles '''

concentration19 = [i[19] for i in combined]
domain = range(0, 21600*10+1)

plt.plot(domain, concentration19, 'blue')

for i in domain: 
    if i % 10800 == 0: 
        plt.axvline(i, color='r')

b_patch = mpatches.Patch(color='blue', label='concentration P(z,t) in the top 1m')
plt.legend(handles=[b_patch])

''' plot coeficient D initial vector ''' 

plt.plot(x_domain, t_vec_ad[0], 'black')

bl_patch = mpatches.Patch(color='black', label='initial vector D at t=0')
plt.legend(handles=[bl_patch])

plt.show()



# ---------------------------------------------------------------------------------------------- 
# PART VII: discrete punctuated diffusion with sedimentation & periodic excitation
# ---------------------------------------------------------------------------------------------- 


''' maybe we can do a regression for change of density per change of diffusion ''' 

def get_prev_c(row): 
    i = row['index']
    try: 
        pc = c_1m.loc[c_1m['index'] == i -1]['c'].values.tolist()[0]
    except: 
        pc = 0
    return pc

c_1m = pd.DataFrame(concentration19)
c_1m.reset_index(inplace = True)
c_1m.columns = ['index', 'c']
c_1m['prev_c'] = c_1m.apply(lambda row: get_prev_c(row), axis=1)
c_1m['c_rRoc'] = c_1m.apply(lambda row: (row['c'] - row['prev_c']) / row['c'], axis=1)
c_1m['currentV'] = c_1m.apply(lambda row: abs(sin((pi*row['index']/21600))), axis=1)
c_1m['raw_D'] = [i[19] for i in t_vec_ad]

''' structure input vectors '''

c_1mr = c_1m[~c_1m['c_rRoc'].isna()]

y = pd.DataFrame(c_1mr['c_rRoc'], columns = ['c_rRoc'])
x = pd.DataFrame(c_1mr['currentV'], columns = ['currentV'])
X = x['currentV']
Y = y['c_rRoc']
Xa = np.array(X)
Xa = Xa.reshape(-1, 1)
Y = np.array(Y)
xtrain = Xa[:-21600]
xtest = Xa[-21600:]
ytrain = Y[:-21600]
ytest = Y[-21600:]


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

print('Coefficients: \n', regr.coef_)
print("Mean squared error: %.2f"
      % mean_squared_error(ytest, ypred))
print('Variance score: %.2f' % r2_score(ytest, ypred))











