'''
    Alaska Scrape Part I:  
        I: Get full list of individual urls 
'''

# -- 
# Dependancies

import urllib2
from urllib2 import urlopen
import requests
import csv
import re
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pprint import pprint
import xmltodict

import pickle

# -- 
# Define functional utilities

def removeWS(s): 
    return s.replace('\r', '').replace('\n','')

def evalZip(code): 
    # - params 
    base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
    base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
    suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"
    pgNum = 1
    # - build first page url
    urlStr = base1 + str(pgNum) + base2 + code + suffix
    url   = urlopen(urlStr)
    soup  = BeautifulSoup(url)
    table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
    table = table[0].findAll('table')
    tableDat = table[0].findAll('tr')
    y = tableDat[2].get_text().encode('ascii', 'ignore') 
    y = removeWS(y.encode('ascii', 'ignore')) 
    # - identify no results instance
    urls = []
    if 'SORCR Found 0 registered sex offenders' in tableDat[1].get_text(): 
        print('no results found')
    # - identify single page instance
    elif 'Index:' not in y: 
        print('single page results')
        urls.append((urlStr, 'single'))
    # - identify multiple page instance
    elif 'Index:' in y: 
        print('multiple results on page')
        n_index = len(tableDat[2].findAll('a')) 
        pages = [] 
        for i in range(1,n_index+1): 
            url = base1 + str(i) + base2 + code + suffix
            pages.append((url, 'multiple'))
        urls.extend(pages) 
    return urls


# -- 
# Get zipcodes from file

allCodes = pd.read_csv('/Users/culhane/VAproject/data/zip_code_database.csv')
alaskaCodes = allCodes.loc[allCodes['state'] == 'AK']
alaskaCodes = alaskaCodes[['zip']].values.tolist() 
alaskaCodes = [str(i[0]) for i in alaskaCodes]


# -- 
# Get page urls

urls = []
for i in alaskaCodes: 
    urls.extend(evalZip(i)) 

# -- 
# Save urls

df = pd.DataFrame(urls)
df.to_csv('/Users/culhane/VAproject/code/Alaska/data/zipCodes.csv')

# -- 
# Load urls

df = pd.read_csv('/Users/culhane/VAproject/data/alaska_urls.csv')
df.columns = ('index', 'url', 'class')
urls = df[['url', 'class']].values.tolist() 

# -- 
# Get all offender links & high-level info

def getInfo(row): 
    link = row.findAll('td')[1].find('a')['href']
    offUrl = 'http://www.dps.alaska.gov' + link
    name = removeWS(row.findAll('td')[1].get_text())
    _zip = removeWS(row.findAll('td')[2].get_text())
    compliant = removeWS(row.findAll('td')[3].get_text())
    out = {
        'name' : name, 
        'zip' : _zip, 
        'compliant' : compliant,
        'offUrl' : offUrl
    }
    return out


def getPageData(url): 
    soup  = BeautifulSoup(urlopen(url[0]))
    table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
    table = table[0].findAll('table')
    tableDat = table[0].findAll('tr')
    # - 
    if url[1] == 'single': 
        offenders = tableDat[2:len(tableDat)-1]
    elif url[1] == 'multiple': 
        offenders = tableDat[3:len(tableDat)-1]
    # - 
    offenderDat = [] 
    for row in offenders: 
        data = getInfo(row)
        data['url'] = url
        data['control'] = len(offenders)
        offenderDat.append(data)
    return offenderDat


# -- 
# Run for all urls

workPage = [] 
errorPage = []
SORDat = []
for url in urls: 
    try: 
        SORDat.append(getPageData(url))
        workPage.append(url)
    except: 
        errorPage.append(url)

# -- 
# Retrive missed data

SORDatII = [] 
SORDatII.append(getPageData(errorPage[0])) 
SORDatII.append(getPageData(errorPage[1])) 


# -- 
# Combine and check data 

allData = SORDat + SORDatII
unlisted = [] 
for i in allData: 
    unlisted.extend(i)

dfO = pd.DataFrame(unlisted)
grouped = dfO.groupby('url').agg({'name' : pd.Series.nunique, 
                                  'offUrl' : pd.Series.nunique, 
                                  'control' : np.max})

grouped.reset_index(inplace=True)
grouped['check_urls'] = grouped.apply(lambda row: row['control'] - row['offUrl'], axis=1) 


# --
# Structure and write out data

dfO.to_csv('/Users/culhane/VAproject/code/Alaska/data/SOFRIndex.csv')

# -- 
# Quickly check the cardinality (Confirmed that there offenders can be listed in multiple zipcode regions)

# I: names
names = dfO[['name']].values.tolist() 
names = [i[0] for i in names]
len(names) 3049
len(list(set(names))) # 2559 

# II: urls
urls = dfO[['offUrl']].values.tolist() 
urls = [i[0] for i in urls]
len(list(set(urls))) # 2561

# III: combos

### a) names with two urls (seems to be one)
ncounts = dfO.groupby('name').agg({'offUrl' : pd.Series.nunique})

ncounts.index.names = ['name']

ncounts.reset_index(inplace=True)
check = ncounts.loc[ncounts['offUrl'] > 1]

#       index                    offUrl
# 337   BROWN, ROBERT LEE        2
# 2374  USUGAN, JONATHAN         2


# IV: Examine duplicates

dups = check.name.values
sub = dfO.loc[dfO['name'].isin(dups)]
sub = sub.sort_values('name', 0)

#### a) Check for Robert Lee Brown (two dudes)

rlb = sub.iloc[0]['name']
urls = sub[['offUrl']].loc[sub['name'] == rlb]
urls = urls.values
'http://www.dps.alaska.gov/sorweb/offender.aspx?LOOKUP_KEY=427596436714858925&FORM_TYPE=search'
'http://www.dps.alaska.gov/sorweb/offender.aspx?LOOKUP_KEY=104630702386205197&FORM_TYPE=search'


#### b) Check for USUGAN, JONATHAN (two dudes)

JU = sub.iloc[2]['name']
urls = sub[['offUrl']].loc[sub['name'] == JU]
urls = urls.values
'http://www.dps.alaska.gov/sorweb/offender.aspx?LOOKUP_KEY=104656709086335192&FORM_TYPE=search'
'http://www.dps.alaska.gov/sorweb/offender.aspx?LOOKUP_KEY=104656709986145191&FORM_TYPE=search'




