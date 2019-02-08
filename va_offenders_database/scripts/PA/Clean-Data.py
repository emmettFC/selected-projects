
'''
    Structure PA Data & Write to Database
'''

# - 
# Dependancies

import pandas as pd
import numpy as np
import pickle
import re
from pprint import pprint 

# -- 
# Load raw data

with open('./data/PA-Data-Raw.pickle', 'rb') as handle:
    data = pickle.load(handle)


# - 
# Cleaning utilities

def cleanAddress(address):
    a = address.replace('\n', ' ').lstrip().rstrip()
    a = re.sub( r'([A-Z])([0-9])', r'\1 \2', a)
    a = re.sub( r'([0-9])([A-Z])', r'\1 \2', a)
    a = re.sub( r'([,])([A-Z])', r'\1 \2', a)
    return a


def expandAddress(entry): 
    ads = entry['addrs']
    for i in range(len(ads)): 
        entry['Address' + str(i+1)] = cleanAddress(ads[i])
        # - 
    del entry['addrs']
    return entry


# - 
# Build raw dataframe for PA 

clean = [expandAddress(i) for i in data]
dfo = pd.DataFrame(clean)

dfo.to_csv('./data/PA-Data-Clean.csv')

