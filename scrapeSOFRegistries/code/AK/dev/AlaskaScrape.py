'''
    Scrape the Alaska Sex Offender Registry: 
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
from bs4 import BeautifulSoup
from pprint import pprint


# -- 
# Get all available zipcode values from search homepage

url   = urlopen('http://www.dps.alaska.gov/Sorweb/Search.aspx')
soup  = BeautifulSoup(url)
posts = soup.findAll("select", {'id' : 'ctl00_ctl00_Content_Content_SearchForm_ZipCodes'})
zips  = posts[0].findAll('option')
codes = [i.get_text() for i in zips]
codes = list(set(codes)) 

valid_codes = [i for i in codes if len(i) == 5]

# -- 
# Use zipcode list to build urls and scrape data
test_code = '99502'

base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
pgNum = 1
base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"

url = base1 + pgNum + base2 + test_code + suffix
url   = urlopen(url)
soup  = BeautifulSoup(url)

table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
table = table[0].findAll('table')
tableDat = table[0].findAll('tr')


# --
# Find how many pages there are to be looped throgh and build urls

n_index = len(tableDat[2].findAll('a')) 

urls = [] 
for i in range(1,n_index+1): 
    url = base1 + str(i) + base2 + test_code + suffix
    urls.append(url)


# --
# Find all links

base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"
urls = []
for zc in valid_codes: 
    pgNum = 1
    url = base1 + str(pgNum) + base2 + zc + suffix
    url   = urlopen(url)
    soup  = BeautifulSoup(url)
    table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
    table = table[0].findAll('table')
    tableDat = table[0].findAll('tr')
    n_index = len(tableDat[2].findAll('a')) 
    pages = [] 
    for i in range(1,n_index+1): 
        url = base1 + str(i) + base2 + zc + suffix
        pages.append(url)
    urls.extend(pages)


# -- 
# Debug the spurious index thing: 



test_code = '99502'

base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
pgNum = 1
base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"

url = base1 + str(pgNum) + base2 + test_code + suffix
url   = urlopen(url)
soup  = BeautifulSoup(url)

# soup = BeautifulSoup(url,from_encoding="utf-8")

table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
table = table[0].findAll('table')
tableDat = table[0].findAll('tr')

n_index = len(tableDat[2].findAll('a')) 

y = tableDat[2].get_text() 

# def _removeNonAscii(s): return "".join(i for i in s if ord(i)<128)
# y = _removeNonAscii(y)

y = y.encode('ascii', 'ignore') 

def removeWS(s): 
    return s.replace('\r', '').replace('\n','')

y = removeWS(y)



# -- 
# Have to handle two conditions: 
    #1: single page of results
    #2: no available results

url = 'http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum=1&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes=995011179&city=All%20Cities&ExecuteQuery=Submit%20Query'

url   = urlopen(url)
soup  = BeautifulSoup(url)

# soup = BeautifulSoup(url,from_encoding="utf-8")

table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
table = table[0].findAll('table')
tableDat = table[0].findAll('tr')

n_index = len(tableDat[2].findAll('a')) 

y = tableDat[2].get_text() 


# -- 
# No results criteria

# test process on the zips: 

base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"

pgNum = 1
url = base1 + str(pgNum) + base2 + zc + suffix
url   = urlopen(url)
soup  = BeautifulSoup(url)
table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
table = table[0].findAll('table')
tableDat = table[0].findAll('tr')
n_index = len(tableDat[2].findAll('a')) 
    pages = [] 
    for i in range(1,n_index+1): 
        url = base1 + str(i) + base2 + zc + suffix
        pages.append(url)
    urls.extend(pages)

z1 = '995011179'
z2 = '99502'
z3 = '99790'

def evalZip(code): 
    # - params 
    base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
    base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
    suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"
    pgNum = 1
    # - build first page url
    url = base1 + str(pgNum) + base2 + code + suffix
    url   = urlopen(url)
    soup  = BeautifulSoup(url)
    table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
    table = table[0].findAll('table')
    tableDat = table[0].findAll('tr')
    y = tableDat[2].get_text().encode('ascii', 'ignore') 
    y = removeWS(y.encode('ascii', 'ignore')) 
    # - identify no results instance
    if 'SORCR Found 0 registered sex offenders' in tableDat[1].get_text(): 
        print('no results found')
    # - identify single page instance
    elif 'Index:' not in y: 
        print('single page results')
    # - identify multiple page instance
    elif 'Index:' in y: 
        print('multiple reults on page')


evalZip(z1)
evalZip(z2)
evalZip(z3)


# -- 
# This function works; now make it into the url generating function: 

urls = []
def evalZip(code): 
    # - params 
    base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
    base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
    suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"
    pgNum = 1
    # - build first page url
    url = base1 + str(pgNum) + base2 + code + suffix
    url   = urlopen(url)
    soup  = BeautifulSoup(url)
    table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
    table = table[0].findAll('table')
    tableDat = table[0].findAll('tr')
    y = tableDat[2].get_text().encode('ascii', 'ignore') 
    y = removeWS(y.encode('ascii', 'ignore')) 
    # - identify no results instance
    if 'SORCR Found 0 registered sex offenders' in tableDat[1].get_text(): 
        print('no results found')
    # - identify single page instance
    elif 'Index:' not in y: 
        print('single page results')
        urls.append(url)
    # - identify multiple page instance
    elif 'Index:' in y: 
        print('multiple reults on page')
        n_index = len(tableDat[2].findAll('a')) 
        pages = [] 
        for i in range(1,n_index+1): 
            url = base1 + str(i) + base2 + code + suffix
            pages.append(url)
        urls.extend(pages)





y = tableDat[2].get_text().encode('ascii', 'ignore') 
y = removeWS(y.encode('ascii', 'ignore')) 

def removeWS(s): 
    return s.replace('\r', '').replace('\n','')

y = removeWS(y)

# --
# Single page criteria


test_code = '99790'

base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
pgNum = 1
base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"

url = base1 + str(pgNum) + base2 + test_code + suffix
url   = urlopen(url)
soup  = BeautifulSoup(url)

# soup = BeautifulSoup(url,from_encoding="utf-8")

table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
table = table[0].findAll('table')
tableDat = table[0].findAll('tr')

n_index = len(tableDat[2].findAll('a')) 





y = y.encode('utf-8', 'ignore')

y = y.encode('ascii', 'ignore') 
y.decode() 
    , 'ignore').decode('ascii')

y = y.encode('utf-8')

.replace(' ', '')

print(y.encode('utf-8'))

print(y.decode('unicode_escape'))
    .encode('ascii','ignore'))

# --
# Get SOFF data for each page 

url = urls[0] 
url   = urlopen(url)
soup  = BeautifulSoup(url)
table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
table = table[0].findAll('table')
tableDat = table[0].findAll('tr')
offenders = tableDat[3:len(tableDat)-1]


# -- 
# Trial data ingest for individual offender 

entry = offenders[0] 
link = entry.findAll('td')[1].find('a')['href']
base3 = 'http://www.dps.alaska.gov'
offUrl = base3 + link
offUrl = urlopen(offUrl)
soup  = BeautifulSoup(offUrl)

# -- 
# Get Aliases 

table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table3'})
secs = table[0].findAll('table')
aliases = secs[0]
aliases = aliases.findAll('tr')
header = [i.get_text() for i in aliases]

# -- 
# Image url

image = secs[2].findAll('img')[0]['src']
imageUrl = base3 + image

# -- 
# Compliance Header

table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table4'})
_data = table[0].find('span', {'class' : 'headcompliant'}).get_text()


# -- 
# Offense level data
# this list of tables generated by this should be the way to do all of the things, much easier can just use index like so: 

table = soup.findAll("table")

offs = table[6].findAll('tr')

offsTable = [] 
counter = 1
out = {}
conv = 'conviction1'
out[u'\n\nConvictions\n\n'] = {}
out[u'\n\nConvictions\n\n'][conv] = {}
for i in offs: 
    if len(i.findAll('i')) == 1: 
        section = i.get_text().replace(' ', '')
        if len(re.findall('Conviction', section)) == 0: 
            out[section] = {}
    elif len(i.findAll('i')) == 0: 
        # if section.replace(' ', '') != 'Convictions': 
        if len(re.findall('Conviction', section)) == 0: 
            print(section)
            tds = i.findAll('td')
            print(len(tds))
            for t in tds: 
                feild = t.find('b').get_text() 
                value = t.get_text().replace(feild, '')
                out[section][feild] = value
        elif len(re.findall('Conviction', section)) > 0: 
        # elif out[section] == 'Convictions': 
            print(section)
            tds = i.findAll('td')
            print(len(tds))
            if len(i.findAll('b')) == 0: 
                counter +=1
                conv = 'conviction' + str(counter)
                out[section][conv] = {}
            elif len(i.findAll('b')) != 0: 
                for t in tds: 
                    feild = t.find('b').get_text() 
                    value = t.get_text().replace(feild, '')
                    out[section][conv][feild] = value 









