#!/usr/bin/env python

'''
    Add period to NT filings documents in ernest_nt_filings 
    
'''

import re
import json
import argparse
import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

import xmltodict

import urllib2
from urllib2 import urlopen

from copy import copy
from pprint import pprint
import datetime
from datetime import date, timedelta

# --
# CLI

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()

config = json.load(open('/home/ubuntu/ernest/config.json'))

client = Elasticsearch([{
    'host' : config['es']['host'], 
    'port' : config['es']['port']
}], timeout = 60000)

ftpcon = SECFTP(FTP('ftp.sec.gov', 'anonymous'))

# -- 
# define query

query = {
    "query" : { 
        "filtered" : { 
            "filter" : { 
                "missing" : { 
                    "field" : "_enrich.period"
                }
            }
        }
    }
}


# --
# functions

# def enrich_deadline(body): 
#     path = ftpcon.url_to_path(body['url'])
#     try: 
#         x = ftpcon.download_parsed(path)['PERIOD'][0]
#         prd = x[:4] + '-' + x[4:6] + '-' + x[6:8]
#         body['_enrich'] = {} 
#         body['_enrich']['period'] = prd
#         try: 
#             body['_enrich']['doc_count'] = int(ftpcon.download_parsed(path)['PUBLIC-DOCUMENT-COUNT'][0]) 
#         except: 
#             body['_enrich']['doc_count'] = None
#     except: 
#         body['_enrich'] = {} 
#         body['_enrich']['period'] = None
#     return body

def enrich_deadline(body): 
    path = url_to_path(body['url'])
    hd   = download_parsed(path)
    try: 
        period    = re.compile('CONFORMED PERIOD OF REPORT')
        period    = [i for i in hd if len(re.findall(period, i)) > 0]
        period    = re.sub('\D', '', period[0])
        prd = period[:4] + '-' + period[4:6] + '-' + period[6:8]
        body['_enrich']['period'] = prd
        try: 
            doc_count = re.compile('PUBLIC DOCUMENT COUNT')
            doc_count = [i for i in hd if len(re.findall(doc_count, i)) > 0]
            doc_count = int(re.sub('\D', '', doc_count[0]))
        except: 
            body['_enrich']['doc_count'] = None
    except: 
        body['_enrich']['period'] = None
    return body

def url_to_path(url):
    url = url.split("/")
    path = 'https://www.sec.gov/Archives/edgar/data/'+ url[2] + "/" + re.sub('\D', '', url[-1]) + "/" + url[-1]
    return path

def run_header(txt):
    txt = __import__('re').sub('\r', '', txt)
    hd  = txt[txt.find('<SEC-HEADER>'):txt.find('<DOCUMENT>')]
    hd  = filter(None, hd.split('\n'))
    return hd

def download(path):
    x    = []
    try: 
        foo  = urllib2.urlopen(path)
        for i in foo:
            x.append(i)
    except: 
        print('malformed url')
    return ''.join(x)

def download_parsed(path):
    x = download(path)
    return run_header(x)

# --
# run

for doc in scan(client, index=config['nt_filings']['index'], query=query): 
    client.index(
        index    = config['nt_filings']['index'], 
        doc_type = config['nt_filings']['_type'], 
        id       = doc["_id"],
        body     = enrich_deadline( doc['_source'] )
    )
    print doc['_id']
