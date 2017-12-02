'''
Ingest OCEARCH Global Shark Tracker Telemetric Data
'''

# - 
# Dependencies

from bs4 import BeautifulSoup
from urllib import request, parse
from urllib.request import urlopen

import json
import pickle
from datetime import datetime
from datetime import date, timedelta
import datetime
import time
from dateutil import parser as dp
import pandas as pd
import numpy as np
from collections import Counter
import ast
import base64


# - 
# Functions 

def parseSharks(_list): 
    parsed = [] 
    for s in range(1, len(_list)): 
        shark = {
        'shark_id' : _list[s].get('value'),
        'shark_name' : _list[s].getText()
        }
        parsed.append(shark)
    return parsed

def getSharkInfo(shark):
    params = {
        'Accept' : 'Accept: application/json, text/javascript, */*; q=0.01', 
        'Accept-Encoding' : 'gzip, deflate', 
        'Accept-Language' : 'en-US,en;q=0.8', 
        'Connection'      : 'keep-alive', 
        'Cookie'          : 'Cookie: viewed=yes; shark_profile_data=%5Bobject%20Object%5D; wpfilebase=1; __qca=P0-1274151182-1500835576537; 29068ca6ca7778cbe7e71f51dc32c904=MjkwNjhjYTZjYTc3NzhjYmU3ZTcxZjUxZGMzMmM5MDQ%3D; PHPSESSID=6g4du55kab3osgndima274rcr5; __atuvc=3%7C30; __atuvs=59762a048a032557001; __atssc=google%3B3; _ga=GA1.2.791958373.1500835576; _gid=GA1.2.1664358293.1500835576',
        'Host'            : 'www.ocearch.org',
        'Referer'         : 'http://www.ocearch.org/tracker/',
        'X-Requested-With': 'XMLHttpRequest' 
    }
    urlSecs = ('http://www.ocearch.org/tracker/ajax/filter-sharks/?sharks%5B%5D=', \
              '&tracking-activity=+&fromDate=&toDate=&species=&gender=+&stage-of-life=+&location=0') 
    shark_id = shark['shark_id']
    shark_name = shark['shark_name']
    params = parse.urlencode(params).encode()
    url = urlSecs[0] + str(shark_id) + urlSecs[1]
    req =  request.Request(url, data=params)
    resp = request.urlopen(req)
    sharkDat = resp.read() 
    sH = json.loads(sharkDat.decode("utf-8"))
    out = sH[0]
    return out

# - 
# Get data & save to file

url = urlopen('http://www.ocearch.org/tracker/')
soup = BeautifulSoup(url) 
_list = soup.find('select', attrs={'class':'sharks-select'}).findAll('option')
sharkInfo = [getSharkInfo(shark) for shark in parseSharks(_list)]

with open('./shark_tracker_data.pickle', 'wb') as _file:
    pickle.dump(sharkInfo, _file, protocol=pickle.HIGHEST_PROTOCOL)

