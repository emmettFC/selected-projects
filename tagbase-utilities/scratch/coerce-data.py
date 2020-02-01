'''
    Clean timeseries files by: 
        I: removing argos and writing to new clean file
        II: coercing argos to numeric and writing to new clean file
        III: logging metadata (A --> 0) for files to loading logfile
'''

# -- 
# dependancies 

import pandas as pd
import os 
from pprint import pprint
import re
import datetime
import numpy as np

# -- 
# get sample file 

ts_files = os.listdir('./data/raw/timeseries/')
file_name = ts_files[0]


# -- 
# load file and stucture as dataframe 

file_path = './data/raw/timeseries/' + file_name
file_ = open(file_path, mode='r')
file_ = file_.read() 

sp = file_.split('data:')
data = sp[1][4:]
data = data.split('\n')
data = [i.split(',') for i in data]
cols = data[0]
dat = data[1:]
df = pd.DataFrame(dat)
df.columns = cols


# -- 
# make metadata file if it doesnt esits or else load it 

d = datetime.datetime.today() 
id_ = 0

log_info = {
    'file_id'  : 0,
    'file_name' : file_name, 
    'date' : d, 
    'n_records' : len(df), 
    'type' : 'time_series'
}

log_input = pd.DataFrame([log_info])

if not os.path.exists('./data/ingest-log.csv'): 


# -- 
# clean file by removing argos LC lines without replacing them 

def is_numeric(row): 
    d = row['VariableValue']
    try: 
        o = np.float(d)
        out = 'valid'
    except: 
        out = 'invalid'
    return out

df['is_numeric'] = df.apply(lambda row: is_numeric(row), axis=1)
invalid_variables = df.loc[df['is_numeric'] == 'invalid'].VariableName.unique() 

dfc1 = df.loc[~df['VariableName'].isin(invalid_variables)]
dflc = df.loc[df['VariableName'] == 'argosLC']


# -- 
# clean file by coercing argos values to numeric 

new_values = dflc.VariableValue.unique()

meta = {
    'indices' : range(len(new_values)), 
    'codes' : new_values
    }

dfmeta = pd.DataFrame(meta)


def coerce_LC(row): 
    key = row['VariableValue']
    val = dfmeta.loc[dfmeta['codes'] == key].indices.values[0]
    return str(val)

dflc['VariableValue'] = dflc.apply(lambda row: coerce_LC(row), axis=1)


dfc1 = dfc1.drop(['is_numeric'], axis=1)

dfc1_out = []
for i in range(len(dfc1)): 
    x = get_row_string(i, dfc1)
    dfc1_out.append(x)

a = '\r\n// '
b = ",".join(c for c in cols) + '\n'
line_1 = a + b
line_2 = "".join(i for i in dfc1_out)

data_c1 = sp[0] + 'data:' + line_1 + line_2


# -- 
# clean file by changing argos values to numeric values and build a metadata reference file for that 

df_clean_2 = pd.concat([dfc1, dflc], axis=0)
dfc2 = df_clean_2.drop(['is_numeric'], axis=1)


# --
# rebiuld the data into the etuff file format

dfc2_out = []
for i in range(len(dfc2)): 
    x = get_row_string(i, dfc2)
    dfc2_out.append(x)


def get_row_string(i, df): 
    row = df.iloc[i]
    s = ",".join(row[c] for c in cols)
    if i == len(df) -1:
        out = s.replace('\r', '')
    else: 
        out = s + '\n'
    return out



dfc2_out[0]
cols
a = '\r\n// '
b = ",".join(c for c in cols) + '\n'
line_1 = a + b
line_2 = "".join(i for i in dfc2_out)

data_c2 = sp[0] + 'data:' + line_1 + line_2

# -- 
# write out both kinds of cleaned up file

cleanfile = open('./data/clean_no_argos/' + file_name, "w+")
cleanfile.write(data_c1)
cleanfile.close()

cleanfile = open('./data/clean_numeric_argos/' + file_name, "w+")
cleanfile.write(data_c2)
cleanfile.close()


