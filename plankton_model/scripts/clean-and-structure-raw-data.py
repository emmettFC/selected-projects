''' 
    Math Final Project: 
        I: Load and structure plankton data from WARP
        II: Load and structure tidal data from sheerness 
        III: Merge data and prepare for regression analysis of chl concentation
'''

# --  
# dependancies 

import pandas as pd
import re
import datetime
from datetime import timedelta

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
from math import log
from math import sin, cos 

from astral import Astral

import seaborn as sns 

# -- 
# io 

folder_path = '/Users/culhane/Desktop/Math_Papers/'
df_plank = pd.read_csv(folder_path + 'SmartBuoy-Downloaded-Data-2018-11-20T22_45_34/warp-(th1)-nmmp-smartbuoy.csv')
df_tide = pd.read_csv(folder_path + 'Sheerness_19861024_20180430.csv')


# -- 
# clean tidal data 

''' functions to clean tidal data '''

def fix_date(row): 
    date_format = re.compile(r'(\d{4}/\d{2}/\d{2})')
    d = re.findall(date_format, row['date'])
    return d[0]


''' fix dates for tide data & convert to datetime object '''

df_tide.columns = ['date', 'time', 'tide_height']
df_tide['date'] = df_tide.apply(lambda row: fix_date(row), axis=1)
df_tide['date_time'] = df_tide.apply(lambda row: row['date'] + ' ' + row['time'], axis=1)
df_tide['date_time'] = df_tide.apply(lambda row: datetime.datetime.strptime(row['date_time'], '%Y/%m/%d %H:%M:%S'), axis=1)
df_tide['date_time'] = df_tide.apply(lambda row: pd.to_datetime(row['date_time']), axis=1)


# -- 
# clean plankton data 

''' fix column names and time dislocation of 2 minutes from hour '''

c = df_plank.columns

new_columns = [u'time', 
       u'salinity_1m', 
       u'tempC_1m',
       u'turbidity_sp_1m', 
       u'chl_fl_SP_1m',
       u'PAR_0m',
       u'PAR_1m',
       u'PAR_2m',
       u'chl_fl_ts_1m', 
       u'nitrate_1m',
       u'oxygen_sat_percent_1m',
       u'turbidity_ts_1_m']

df_plank.columns = new_columns
df_plank = df_plank[new_columns]
s = df_plank.iloc[0]['time']
s[:-2]+'00'

df_plank['time'] = df_plank.apply(lambda row: row['time'][:-2]+'00', axis=1)
df_plank['date_time'] = df_plank.apply(lambda row: datetime.datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S'), axis=1)
df_plank['date_time'] = df_plank.apply(lambda row: pd.to_datetime(row['date_time']), axis=1)


# -- 
# create subset of data frames for time period of interest

''' restrict datasets to the range of overlap '''

pmax, pmin = max(df_plank['date_time'].values), min(df_plank['date_time'].values)
tmax, tmin = max(df_tide['date_time'].values), min(df_tide['date_time'].values)

df_tide_sub = df_tide.loc[df_tide['date_time'] >= pd.to_datetime(pmin) - timedelta(days=1)]
df_plank_sub = df_plank.loc[df_plank['date_time'] <= tmax]
df_plank_sub = df_plank_sub[['date_time', 'chl_fl_SP_1m', 'PAR_0m', 'PAR_1m', 'PAR_2m', 'chl_fl_ts_1m', 'tempC_1m']]


# -- 
# tidal data is not complete for all years; the years with best coverage are [2003, 2004, 2005]


''' functions to evaluate get all values and join points for time steps'''

def make_tide_float(row): 
    try: 
        t = float(row['tide_height'])
    except: 
        t = 'NA'
    return t

def get_year(row): 
    d = row['date_time']
    try: 
        year = d.year
    except: 
        year = 'NA'
    return year

def is_int(row): 
    if type(row['date_time']) == int: 
        out = 1
    else: 
        out = 0
    return out

def get_month(row): 
    return row['date_time'].month


def get_tide_val(row, ind):
    if ind == 0: 
        t =  row['date_time'] - timedelta(hours=2)
    elif t == 1: 
        t = row['date_time']
    try:
        tide = df_tide_sub.loc[df_tide_sub['date_time'] == t]['tide_height'].values.tolist()[0]
    except: 
        tide = 'NA'
    return tide

def get_chl_val(row): 
    if row['index'] ==0: 
        chl = 0
    else: 
        chl = chl_col_ref.loc[chl_col_ref['inx'] == row['index']]['chl_fl_SP_1m'].values.tolist()[0]
    return chl

def eval_sunset_sunrise(row, _type): 
    try: 
        city_name = 'London'
        a = Astral()
        a.solar_depression = 'civil'
        city = a[city_name]
        d = row['date_time']
        sun = city.sun(date=d, local=True)
        # sr, ss = sun['sunrise'], sun['sunset']
        out = sun[_type]
    except: 
        # sr, ss = 'NA', 'NA'
        out = 'NA'
    return out

def is_light(row): 
    d = row['date_time']
    if (pd.to_datetime(row['sunrise']) < d < pd.to_datetime(row['sunset'])): 
        light = True
    else: 
        light = False
    return light



def remove_timezone(row, _type): 
    # ss, sr = row['sunset'], row['sunrise']
    out = row[_type]
    return out.tz_localize(None) #ss.tz_localize(None), sr.tz_localize(None)

def is_light(row): 
    d = row['date_time']
    if (pd.to_datetime(row['sunrise']) < d < pd.to_datetime(row['sunset'])): 
        light = True
    else: 
        light = False
    return light



''' apply functions to raw plankton dataset ''' 

df_plank_sub['tide_height'] = df_plank_sub.apply(lambda row: get_tide_val(row, 1), axis=1)
df_plank_sub['tide_height_prev'] = df_plank_sub.apply(lambda row: get_tide_val(row, 0), axis=1)
chl_col_ref = df_plank_sub['chl_fl_SP_1m']
chl_col_ref = chl_col_ref.reset_index()
chl_col_ref['inx'] = chl_col_ref.apply(lambda row: int(row['index'] + 1), axis=1)
df_plank_sub.reset_index(inplace=True)
df_plank_sub['chl_fl_SP_1m_prev'] = df_plank_sub.apply(lambda row: get_chl_val(row), axis=1)

tides = df_tide_sub.loc[df_tide_sub['year'].isin([2003,2004,2005])]
df_plank_sub['date_time'] = df_plank_sub.apply(lambda row: pd.to_datetime(row['date_time']), axis=1)
df_plank_sub['year'] = df_plank_sub.apply(lambda row: get_year(row), axis=1)
chl = df_plank_sub.loc[df_plank_sub['year'].isin([2003, 2004, 2005])]

chl['lnCHLfl'] = chl.apply(lambda row: log(row['chl_fl_SP_1m']), axis=1)
chl['lnCHLfl_prev']= chl.apply(lambda row: log(row['chl_fl_SP_1m_prev']), axis=1)
chl['date_time'] = chl.apply(lambda row: pd.to_datetime(row['date_time']), axis=1)

chl['sunrise'] = chl.apply(lambda row: eval_sunset_sunrise(row, 'sunrise'), axis=1)
chl['sunset'] = chl.apply(lambda row: eval_sunset_sunrise(row, 'sunset'), axis=1)

chl['ss_no_tz'] = chl.apply(lambda row: remove_timezone(row, 'sunset'), axis=1)
chl['sr_no_tz'] = chl.apply(lambda row: remove_timezone(row, 'sunrise'), axis=1)

chl['is_light'] = chl.apply(lambda row: is_light(row), axis=1)


# based on coverage and availability of data in either dataset; restrict analysis to 2003 


''' restrict to second half 2003; remove 22 entries from november 16th '''

data_2003 = chl.loc[chl['year'] == 2003]
data_2003['month'] = data_2003.apply(lambda row: get_month(row), axis=1)
data_2003_sub = data_2003.loc[data_2003['month'].isin([6,7,8,9,10,11,12])]
data_2003_sub = data_2003_sub.loc[~data_2003_sub['tide_height'].isna()]
data_2003_sub['is_light'] = data_2003_sub.apply(lambda row: is_light(row), axis=1)


''' get current speed for each increment ''' 

def get_current_speed(row): 
    diff = float(row['tide_height']) - float(row['tide_height_prev'])
    curr = abs(diff)
    return curr


data = data_2003_sub.loc[(data_2003_sub['tide_height'] != '-99.000N') & (data_2003_sub['tide_height_prev'] != '-99.000N')]
data['current'] = data.apply(lambda row: get_current_speed(row), axis=1) 


# -- 
# generate plot of tidal current speed and tide height for discrete 2 hour segments and continuous tidal data


''' plot discrete tidal height and current (week 1 June 2003)''' 

data['tide_height'] = data.apply(lambda row: float(row['tide_height']), axis=1) 
data['tide_height_prev'] = data.apply(lambda row: float(row['tide_height_prev']), axis=1) 

tides = data.loc[data['month'] == 6]
tides = tides.iloc[0:7*12]
domain = range(0,len(tides))
plt.plot(domain, tides['tide_height'], 'blue')
plt.plot(domain, tides['current'], 'red')


''' plot continuous tidal height and current change data '''

def remove_invalid(row): 
    try: 
        f = float(row['tide_height'])
        o = True
    except: 
        o = False
    return o 

def get_prev_tide(row): 
    try: 
        prev = tide_2003.loc[tide_2003['index'] == row['index'] - 1]['tide_height'].values.tolist()[0] 
    except: 
        prev = 'NA'
    return prev


df_tide['year'] = df_tide.apply(lambda row: get_year(row), axis=1)
df_tide_2003 = df_tide.loc[df_tide['year'] == 2003]
df_tide_2003 = df_tide_2003.loc[df_tide_2003['tide_height'] != '-99.000N']
df_tide_2003['month'] = df_tide_2003.apply(lambda row: get_month(row), axis=1)
tide_2003 = df_tide_2003.loc[df_tide_2003['month'].isin([6, 7, 8, 9, 10, 11, 12])]
tide_2003['invalid'] = tide_2003.apply(lambda row: remove_invalid(row), axis=1) 
tide_2003 = tide_2003.loc[tide_2003['invalid'] == True]
tide_2003['tide_height'] = tide_2003.apply(lambda row: float(row['tide_height']), axis=1) 

''' have to get previous tide values for this subset ''' 

tide_2003.reset_index(inplace=True)
tide_2003['tide_height_prev'] = tide_2003.apply(lambda row: get_prev_tide(row), axis=1)
# tide_2003.to_csv('/Users/culhane/Desktop/Math_Papers/tide-2003-clean-analysis-range.csv')
tide_plot = tide_2003.loc[tide_2003['tide_height_prev'] != 'NA']
tide_plot['current'] = tide_plot.apply(lambda row: get_current_speed(row), axis=1)


''' plot continuous difference for week 1 June 2003 '''

tides = tide_plot.loc[tide_plot['month'] == 6]
df_t_sample = tides.iloc[0:(24*7)*4]
domain = range(0,(24*7)*4)
plt.plot(domain, df_t_sample['tide_height'], 'blue')
plt.plot(domain, df_t_sample['current'], 'red')
plt.show() 


# -- 
# add relative rate of change of chlorophyl to the plankton dataset  according to paper 

''' natural log chain rule function result '''

def get_relative_ROC(row): 
    diff = float(row['chl_fl_SP_1m']) - float(row['chl_fl_SP_1m_prev'])
    rRoc = diff / float(row['chl_fl_SP_1m'])
    return rRoc


''' apply function to data and build plot again (week 1 June 2003)'''

data['chl_rRoc'] = data.apply(lambda row: get_relative_ROC(row), axis=1)

tides = data.loc[data['month'] == 6]
tides_plot = tides.iloc[0:(12*7)]
domain = range(0,(12*7))
plt.plot(domain, tides['tide_height'], 'blue')
plt.plot(domain, tides['current'], 'red')
plt.plot(domain, tides['chl_rRoc'], 'black')

r_patch = mpatches.Patch(color='red', label='current')
b_patch = mpatches.Patch(color='blue', label='tide height')
bl_patch = mpatches.Patch(color='black', label='chlorophyll fl at 1m')
plt.legend(handles=[bl_patch, r_patch, b_patch])

plt.show()

plt.show()


# -- 
# clean out NA values to prepare for regression analysis 

''' functions for cleaning and relative current calculation '''

def get_prev_current(row): 
    try: 
        csp = reg_data.loc[reg_data['index'] == row['index'] - 1]['current'].values.tolist()[0]
    except: 
        csp = None
    return csp

def get_relative_current(row): 
    cs = row['current']
    csp = row['csp']
    rcs = float(cs) - float(csp)
    out = rcs / float(cs)
    return out


''' apply functions to make clean dataset '''

reg_data = data.loc[~data['chl_rRoc'].isna()]

reg_data = reg_data[[u'date_time', u'chl_fl_SP_1m',
       u'PAR_1m', u'chl_fl_ts_1m', u'tempC_1m',
       u'tide_height', u'tide_height_prev', u'chl_fl_SP_1m_prev', u'year',
       u'lnCHLfl', u'lnCHLfl_prev', u'sr_no_tz',
       u'ss_no_tz', u'month', u'is_light', u'current', u'chl_rRoc']]

reg_data.reset_index(inplace=True)
reg_data['csp'] = reg_data.apply(lambda row: get_prev_current(row), axis=1)
# len(reg_data.loc[reg_data['csp'].isna()])
reg_data = reg_data.loc[~reg_data['csp'].isna()]
reg_data['current_rRoc'] = reg_data.apply(lambda row: get_relative_current(row), axis=1) 
reg_data['ln_diff_chl'] = reg_data.apply(lambda row: row['lnCHLfl'] - row['lnCHLfl_prev'], axis=1)


# -- 
# write out final structured datasets for tide and plankton 

reg_data.to_csv('/Users/culhane/Desktop/Math_Papers/chl-tide-analysis-data-clean.csv')
tide_2003.to_csv('/Users/culhane/Desktop/Math_Papers/tide-2003-clean-analysis-range.csv')












