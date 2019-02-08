'''
    Florida SOF Registry Scrape: 
        I: Uses the sequential indices of individual offenders to loop through offender urls
        II: Deals with several formats for the offender flyers
        III: All errors are caught explicitly to ensure no data is lost
'''

# -- 
# Dependancies

import urllib2
import requests
import csv
import re
import time
import pandas as pd

from bs4 import BeautifulSoup
from pprint import pprint
from urllib2 import urlopen


# --
# Manually generated list of offenders (seems to stop at 102220)

ids = range(1, 102220)
ids = [str(i) for i in ids]

urls = [] 
for i in ids: 
    url = 'http://offender.fdle.state.fl.us/offender/flyer.do?personId=' + i 
    urls.append(url)


# -- 
# User defined functions for page evaluation

def removeWS(s): 
    return s.replace('\r', '').replace('\n','').replace('\t', '')

def evalPage(soup): 
    image = soup.findAll('table')[1].find('img')['src']
    tab = soup.findAll('table', {'class' : 'FlyerInfo'})
    rows = tab[0].findAll('tr')
    rowtext = [removeWS(i.get_text()) for i in rows]
    keys = [i.split(':')[0].replace(' ', '_').replace('_#', '') for i in rowtext[1:]]
    vals = [i.split(':')[1] for i in rowtext[1:]]
    d = dict(zip(keys, vals))
    d['Department_of_Corrections'] = re.sub("\D", '', d['Department_of_Corrections']) 
    rows2 = tab[1].findAll('tr')
    aliases = removeWS(rows2[1].get_text())
    if 'Absconded' in d['Status']: 
        d['addType'] = 'Absconded, no known address'
        d['image'] = image
        d['aliases'] = aliases
    else: 
        try: 
            d = evalNormal(rows2, d, aliases, image)
        except: 
            try: 
                d = evalOdd(rows2, d, aliases, image)
            except: 
                try: 
                    d = evalMarked(rows2, d, aliases, image)
                except:
                    d = 'irregularURl'
        # - 
    return d

def evalNormal(rows2, d, aliases, image): 
    aI = rows2[7].findAll('td') 
    s = str(aI[2].find('u')) 
    info = s[s.find("(")+1:s.find(")")].split(',')
    info = [removeWS(i).replace("'", '').rstrip().lstrip() for i in info]
    # -- address information
    d['addType'] = removeWS(aI[1].get_text()).lstrip().rstrip().split(':')[3]
    d['addLoc'] = info[4] 
    d['city'] = info[6] 
    d['state'] = info[7] 
    d['zip'] = info[8]
    d['county'] = info[9]
    d['lat'] = info[10]
    d['lon'] = info[11]
    d['image'] = image
    d['aliases'] = aliases
    return d

def evalOdd(rows2, d, aliases, image): 
    aI = rows2[7].findAll('tr')[1].findAll('td')
    s = str(aI[2].find('u')) 
    info = s[s.find("(")+1:s.find(")")].split(',')
    info = [removeWS(i).replace("'", '').rstrip().lstrip() for i in info]
    # -- address information
    d['addType'] = info[4] 
    d['addLoc'] = info[5] 
    d['city'] = info[6] 
    d['state'] = info[7] 
    d['zip'] = info[8]
    d['county'] = info[9]
    d['lat'] = info[10]
    d['lon'] = info[11]
    d['image'] = image
    d['aliases'] = aliases
    return d

def evalMarked(rows2, d, aliases, image):
    try: 
        aI = rows2[8].findAll('tr')[1].findAll('td')
        if 'Show Map' in aI[2].get_text(): 
            s = str(aI[2].find('u')) 
            info = s[s.find("(")+1:s.find(")")].split(',')
            info = [removeWS(i).replace("'", '').rstrip().lstrip() for i in info]
            d = {}
            # -- address information
            d['addType'] = info[4] 
            d['addLoc'] = info[5] 
            d['city'] = info[6] 
            d['state'] = info[7] 
            d['zip'] = info[8]
            d['county'] = info[9]
            d['lat'] = info[10]
            d['lon'] = info[11]
        elif 'not mappable' in aI[2].get_text(): 
            info = aI[0] 
            info[info.find("br/>")+1:info.find("<br/")]
            add1, add2 = info.split('>')[2], info.split('>')[3]
            d['city'] = add1.split(',')[0] 
            comp = re.compile('[^a-zA-z]+<br')
            d['zip'] = re.sub('[^0-9]', '', re.findall(comp, add1)[0]) 
            d['county'] = add2.replace('</td', '')
            d['state'] = re.sub('[^A-Z]', '', add1.split(',')[1]) 
    except: 
        aI = rows2[7].findAll('td')
        if 'Show Map' in aI[2].get_text(): 
            s = str(aI[2].find('u')) 
            info = s[s.find("(")+1:s.find(")")].split(',')
            info = [removeWS(i).replace("'", '').rstrip().lstrip() for i in info]
            d = {}
            # -- address information
            d['addType'] = info[4] 
            d['addLoc'] = info[5] 
            d['city'] = info[6] 
            d['state'] = info[7] 
            d['zip'] = info[8]
            d['county'] = info[9]
            d['lat'] = info[10]
            d['lon'] = info[11]
        elif 'not mappable' in aI[2].get_text(): 
            info = str(aI[0]) 
            info[info.find("br/>")+1:info.find("<br/")]
            add1, add2 = info.split('>')[2], info.split('>')[3]
            d['city'] = add1.split(',')[0] 
            comp = re.compile('[^a-zA-z]+<br')
            d['zip'] = re.sub('[^0-9]', '', re.findall(comp, add1)[0]) 
            d['county'] = add2.replace('</td', '')
            d['state'] = re.sub('[^A-Z]', '', add1.split(',')[1])      
    return d



# --  
# Run & evaluate method

offenderDat = []
invalidUrls = [] 
for i in range(0, len(urls)): 
    print(urls[i])
    print('found ' + str(len(offenderDat)) + ' valid offenders and ' + str(len(invalidUrls)) + ' invalid links')
    print('evaluating ' + str(i + 1) + ' of ' + str(len(urls)) + ' offenders') 
    try: 
        url = urlopen(urls[i])
        soup = BeautifulSoup(url)
        out = evalPage(soup)
        if out == 'irregularUrl': 
            invalidUrls.append([urls[i], 'data error'])
        elif type(out) == dict: 
            offenderDat.append(out)
    except urllib2.HTTPError as err:
        if err.code == 404:
            continue
        else:
            invalidUrls.append([urls[i], 'url error'])
    except KeyboardInterrupt: 
        raise


for i in range(1682, len(urls)): 
    print(urls[i])
    print('found ' + str(len(offenderDat)) + ' valid offenders and ' + str(len(invalidUrls)) + ' invalid links')
    print('evaluating ' + str(i + 1) + ' of ' + str(len(urls)) + ' offenders') 
    try: 
        url = urlopen(urls[i])
        soup = BeautifulSoup(url)
        out = evalPage(soup)
        if out == 'irregularUrl': 
            invalidUrls.append([urls[i], 'data error'])
        elif type(out) == dict: 
            offenderDat.append(out)
    except urllib2.HTTPError as err:
        if err.code == 404:
            continue
        else:
            invalidUrls.append([urls[i], 'url error'])
    except KeyboardInterrupt: 
        raise

emptyUrls = [] 
for i in range(10947, len(urls)): 
    print(urls[i])
    print('found ' + str(len(offenderDat)) + ' valid offenders and ' + str(len(invalidUrls)) + ' invalid links')
    print('evaluating ' + str(i + 1) + ' of ' + str(len(urls)) + ' offenders') 
    try: 
        url = urlopen(urls[i])
        soup = BeautifulSoup(url)
        out = evalPage(soup)
        if out == 'irregularUrl': 
            invalidUrls.append([urls[i], 'data error'])
        elif type(out) == dict: 
            offenderDat.append(out)
    except urllib2.HTTPError as err:
        if err.code == 404:
            emptyUrls.append(urls[i])
        else:
            invalidUrls.append([urls[i], 'url error'])
    except KeyboardInterrupt: 
        raise


import pickle
with open('/Users/culhane/VAproject/code/FL/FL-Data-Raw.pickle', 'wb') as _file:
    pickle.dump(offenderDat, _file, protocol=pickle.HIGHEST_PROTOCOL)


for i in range(39864, len(urls)): 
    print(urls[i])
    print('found ' + str(len(offenderDat)) + ' valid offenders and ' + str(len(invalidUrls)) + ' invalid links')
    print('evaluating ' + str(i + 1) + ' of ' + str(len(urls)) + ' offenders') 
    try: 
        url = urlopen(urls[i])
        soup = BeautifulSoup(url)
        out = evalPage(soup)
        if out == 'irregularUrl': 
            invalidUrls.append([urls[i], 'data error'])
        elif type(out) == dict: 
            offenderDat.append(out)
    except urllib2.HTTPError as err:
        if err.code == 404:
            continue
        else:
            invalidUrls.append([urls[i], 'url error'])
    except KeyboardInterrupt: 
        raise


import pickle
with open('/Users/culhane/VAproject/code/FL/FL-Data-Raw.pickle', 'wb') as _file:
    pickle.dump(offenderDat, _file, protocol=pickle.HIGHEST_PROTOCOL)





for i in range(88862, len(urls)): 
    print(urls[i])
    print('found ' + str(len(offenderDat)) + ' valid offenders and ' + str(len(invalidUrls)) + ' invalid links')
    print('evaluating ' + str(i + 1) + ' of ' + str(len(urls)) + ' offenders') 
    try: 
        url = urlopen(urls[i])
        soup = BeautifulSoup(url)
        out = evalPage(soup)
        if out == 'irregularUrl': 
            invalidUrls.append([urls[i], 'data error'])
        elif type(out) == dict: 
            offenderDat.append(out)
    except urllib2.HTTPError as err:
        if err.code == 404:
            emptyUrls.append(urls[i])
        else:
            invalidUrls.append([urls[i], 'url error'])
    except KeyboardInterrupt: 
        raise


import pickle
with open('/Users/culhane/VAproject/code/FL/FL-Data-Raw-Final.pickle', 'wb') as _file:
    pickle.dump(offenderDat, _file, protocol=pickle.HIGHEST_PROTOCOL)



# -- 
# You should have definitely included data logging in this, the urls cant be traced back 
# to the individual offender results dictionaries...




pprint(urls[60546]) 
{u'Date_of_Birth': u'01/17/1972',
 u'Department_of_Corrections': u'17676',
 u'Designation': u'Sexual Predator',
 u'Eyes': u'Brown',
 u'Hair': u'Brown',
 u'Height': u'5\'08"',
 u'Name': u'RICARDO DIZON DANIEL',
 u'Race_': u'White',
 u'Sex': u'Male',
 u'Status': u'Confinement',
 u'Weight': u'191 lbs'}

url

http://offender.fdle.state.fl.us/offender/flyer.do?personId=60546



