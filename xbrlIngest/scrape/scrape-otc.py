import os
import re
import csv
import json
import zlib
import zipfile
import argparse
import itertools

import urllib2 
from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import HTTPError

from bs4 import BeautifulSoup

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

from datetime import datetime, date, timedelta

# --
# CLI 

parser = argparse.ArgumentParser(description='ingest_otc')
parser.add_argument("--from-scratch", action = 'store_true') 
parser.add_argument("--most-recent", action = 'store_true') 
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()

config = json.load(open(args.config_path))
client = Elasticsearch([{"host" : config['es']['host'], "port" : config['es']['port']}])

# -- 
# Functions

def text_date(string):
    try: 
        front     = re.findall('\d{1,}-\D{1,}-\d{4}', string)[0]
        back      = re.findall('\d{2}:\d{2}:\d{2}', string)[0]
        monthDict = {'JAN' : 1, 'FEB' : 2, 'MAR' : 3, 'APR' : 4, 'MAY' : 5, 'JUN' : 6, 'JUL' : 7, 'AUG' : 8, 'SEP' : 9, 'OCT' : 10, 'NOV' : 11, 'DEC' : 12}
        parts     = front.split('-')
        parts[1]  = monthDict[parts[1]]
        date      = '%s-%s-%s %s' % (parts[2], str(parts[1]).zfill(2), str(parts[0].zfill(2)), back)
        return date
    except: 
        pass


def zip_date(string): 
    try: 
        front = re.findall('\d{1,}/\d{1,}/\d{4}', string)[0]
        parts = front.split('/')
        date  = parts[2] + '-' + str(parts[0].zfill(2)) + '-' + str(parts[1]).zfill(2)
        try: 
            back = re.findall('\d{1,}:\d{2}:\d{2}', string)[0]
            date = date + ' ' + back
        except: 
            date = date
    except: 
        date = None
    return date


def ingest_raw(start_year):
    url   = 'http://otce.finra.org/DailyList/Archives'
    soup  = BeautifulSoup(urllib2.urlopen(url)) 
    links = soup.find("ul", {"class" : ['rawlist']}).findAll("li")
    
    for link in links: 
        x     = link.find('a')
        _file = x['href']
        _text = x.get_text()
        base  = 'http://otce.finra.org'
        
        if 'txt' in str(_text): 
            
            o     = re.sub('\D', '', _text)
            month = int(o[:2])
            year  = int(o[4:])
            
            if year >= start_year:
                response  = urllib2.urlopen(base + _file)
                body      = [line.split('|') for line in response] 
                keys      = body[0]
                for p in range(1, len(body)):
                    vals            = body[p]
                    d               = dict(zip(keys, vals))
                    out = { 
                        'raw_source'   : 'txt_archive',
                        'source_doc'   : _text,
                        'enrichDate'   : text_date(d['Daily List Date']),
                        'IssuerSymbol' : d['New Symbol'].upper(),
                        'CompanyName'  : d['New Company Name'].upper(),
                        'Type'         : d['Type'].upper()
                    }
                    
                    client.index(
                        index    = config['otc_raw']['index'], 
                        doc_type = config['otc_raw']['_type'], \
                        body    = out, \
                        id      = out['source_doc'].decode('utf-8') + '_' + out['IssuerSymbol'].decode('utf-8') + \
                                '_' + str(out['enrichDate']).decode('utf-8') + '_' + out['CompanyName'].decode('utf-8') \
                                + '_' + out['Type'].decode('utf-8'))
            else: 
                pass
        elif 'zip' in str(_file): 
            year      = int(_text) 
            if year >= start_year: 
                response  = urllib2.urlopen(base + _file)       
                read      = response.read()
                with open('/home/ubuntu/data/otc_archives/' + _text + '.zip', 'w') as inf:
                    inf.write(read)
                    inf.close()
                    # ---
                with zipfile.ZipFile('/home/ubuntu/data/otc_archives/' + _text + '.zip', 'r') as z:
                    z.extractall('/home/ubuntu/data/otc_archives/')
                    # ---
                for i in os.listdir('/home/ubuntu/data/otc_archives/Daily_List_' + _text + '/'):
                    name      = str(i)
                    f         = open('/home/ubuntu/data/otc_archives/Daily_List_' + _text + '/'+ i, 'r')
                    x         = f.readlines()
                    body      = [line.split('|') for line  in x] 
                    body      = [[body[i][k].replace('\r\n', '') for k in range(len(body[i]))] for i in range(len(body))]
                    for m in range(1, len(body)): 
                        keys            = body[0]
                        vals            = body[m]
                        d               = dict(zip(keys, vals))
                        if name[:2] == 'BB':
                            out = { 
                                'raw_source'   : 'zip_archive',
                                'source_doc'   : name,
                                'enrichDate'   : zip_date(d['DailyListDate']),
                                'IssuerSymbol' : d['NewSymbol'].upper(),
                                'CompanyName'  : d['NewName'].upper(),
                                'Type'         : d['Type'].upper()
                            }
                            # ---
                            client.index(index = config['otc_raw']['index'], doc_type = config['otc_raw']['_type'], \
                                        body = out, \
                                        id = out['source_doc'].decode('utf-8') + '_' + out['IssuerSymbol'].decode('utf-8') + \
                                        '_' + str(out['enrichDate']).decode('utf-8') + '_' + out['CompanyName'].decode('utf-8') \
                                        + '_' + out['Type'].decode('utf-8'))
                        elif name[:2] == 'di':
                            out = { 
                                'raw_source'   : 'zip_archive',
                                'source_doc'   : name,
                                'enrichDate'   : zip_date(d['Daily List Date']),
                                'IssuerSymbol' : d['Issue Symbol'].upper(),
                                'CompanyName'  : d['Company Name'].upper(),
                                'Type'         : 'DIVIDEND'
                            }
                            # ---
                            client.index(index = config['otc_raw']['index'], doc_type = config['otc_raw']['_type'], \
                                        body = out, \
                                        id = out['source_doc'].decode('utf-8') + '_' + out['IssuerSymbol'].decode('utf-8') + \
                                        '_' + str(out['enrichDate']).decode('utf-8') + '_' + out['CompanyName'].decode('utf-8') \
                                        + '_' + out['Type'].decode('utf-8'))
            else: 
                pass


# -- 
# Run

if args.from_scratch: 
    start_year = 2010
elif args.most_recent: 
    start_year = int(date.today().year)

ingest_raw(start_year)
