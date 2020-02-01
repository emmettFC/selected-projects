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
import argparse 
import shutil


# -- 
# user defined functions 

def is_numeric(row): 
    d = row['VariableValue']
    try: 
        o = np.float(d)
        out = 'valid'
    except: 
        out = 'invalid'
    return out

def coerce_LC(row, dfmeta): 
    key = row['VariableValue']
    val = dfmeta.loc[dfmeta['codes'] == key].indices.values[0]
    return str(val)

def get_row_string(i, df): 
    row = df.iloc[i]
    s = ",".join(row[c] for c in cols)
    if i == len(df) -1:
        out = s.replace('\r', '')
    else: 
        out = s + '\n'
    return out

def make_log_input(id_, file_name, df):
    log_info = {
        'file_id'  : id_,
        'file_name' : file_name, 
        'date' : datetime.datetime.today(), 
        'n_records' : len(df), 
        'type' : 'time_series'
    }
    log_input = pd.DataFrame([log_info])
    return log_input

def log_file_info(file_name, df):
    if os.path.exists('./data/ingest-log.csv'): 
        meta_file = pd.read_csv('./data/ingest-log.csv')
        id_ = max(meta_file.file_id) + 1
        log_input = make_log_input(id_, file_name, df)
        meta = pd.concat([meta_file, log_input])
        meta.to_csv('./data/ingest-log.csv', index=False)
    else: 
        id_ = 0
        meta = make_log_input(id_, file_name, df)
        meta.to_csv('./data/ingest-log.csv', index=False)

def log_argos_values(dflc):
    if os.path.exists('./data/lc_log_info.csv'): 
        lc_file = pd.read_csv('./data/lc_log_info.csv')
        new_values = dflc.loc[~dflc['VariableValue'].isin(lc_file.codes.values.tolist())].VariableValue.unique()
        meta = {
            'indices' : range(max(lc_file.indices) + 1, max(dfmeta.indices) + 1 + len(new_values)), 
            'codes' : new_values
            }
        lc_out = pd.concat([lc_file, pd.DataFrame(meta)], axis=0)
        lc_out.to_csv('./data/lc_log_info.csv', index=False)
    else: 
        new_values = dflc.VariableValue.unique()
        meta = {
            'indices' : range(len(new_values)), 
            'codes' : new_values
            }
        lc_out = pd.DataFrame(meta)
        lc_out.to_csv('./data/lc_log_info.csv', index=False)
    return lc_out

def clean_rebuild(dfc1, dflc, sp, cols):
    df_clean_2 = pd.concat([dfc1, dflc], axis=0)
    dfc2 = df_clean_2.drop(['is_numeric'], axis=1)
    dfc2_out = []
    for i in range(len(dfc2)): 
        x = get_row_string(i, dfc2)
        dfc2_out.append(x)
        # - 
    dfc2_out[0]
    cols
    a = '\r\n// '
    b = ",".join(c for c in cols) + '\n'
    line_1 = a + b
    line_2 = "".join(i for i in dfc2_out)
    data_c2 = sp[0] + 'data:' + line_1 + line_2
    return data_c2

def split_format(file_name):
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
    return sp, df, cols

def write_file(file_name, data_c2): 
    if not os.path.exists('./data/clean_timeseries'): 
        os.mkdir('./data/clean_timeseries/')
    cleanfile = open('./data/clean_timeseries/' + file_name, "w+")
    cleanfile.write(data_c2)
    cleanfile.close()


# -- 
# get file directory

ts_files = os.listdir('./data/raw/timeseries/')


# -- 
# run program

for file_name in ts_files: 
    ' split text '
    sp, df, cols = split_format(file_name)
    ' log file ingest '
    log_file_info(file_name, df)
    df['is_numeric'] = df.apply(lambda row: is_numeric(row), axis=1)
    invalid_variables = df.loc[df['is_numeric'] == 'invalid'].VariableName.unique() 
    dfc1 = df.loc[~df['VariableName'].isin(invalid_variables)]
    dflc = df.loc[df['VariableName'] == 'argosLC']
    ' log argos LC values '
    dfmeta = log_argos_values(dflc)
    ' transform to numeric '
    dflc['VariableValue'] = dflc.apply(lambda row: coerce_LC(row, dfmeta), axis=1)
    dfc1 = dfc1.drop(['is_numeric'], axis=1)
    ' rebuild the eTUFF file '
    data_c2 = clean_rebuild(dfc1, dflc, sp, cols)
    ' write eTUFF to file directory '
    write_file(file_name, data_c2)
    ' move imgested file to post-cleaning storage '
    os.rename('./data/raw/timeseries/' + file_name, './data/ingested/timeseries/' + file_name)




