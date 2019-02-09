import json
import math
import argparse
import urllib2
import re

from datetime import datetime, date, timedelta
from dateutil.parser import parse as dateparse

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan, bulk

# -- 
# cli

parser = argparse.ArgumentParser(description='ingest_finra_docs')
parser.add_argument("--directory", type=str, action='store')
parser.add_argument("--update-halts", action='store_true')
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()

# --
# global vars

config = json.load(open(args.config_path))
client = Elasticsearch([{'host' : config['es']['host'], 'port' : config['es']['port']}])

urls = {
    "directory"   : 'http://otce.finra.org/Directories/DirectoriesJson?pgnum=',
    "halts"       : 'http://otce.finra.org/TradeHaltsHistorical/TradeHaltsHistoricalJson?pgnum=',
    "delinquency" : 'http://otce.finra.org/DCList/DCListJson?pgnum='
}


INDEX = config['otc_%s' % args.directory]['index']
TYPE  = config['otc_%s' % args.directory]['_type']
url   = urls[args.directory]


# --
# functions

def to_ref_date(date): 
    d = int(re.sub('\D', '', date)) 
    out_date = datetime.utcfromtimestamp(d / 1000).strftime('%Y-%m-%d')
    return out_date

def get_max_date(INDEX):
    global config 
    query = {
        "size" : 0,
        "aggs" : { "max" : { "max" : { "field" : "_enrich.halt_short_date" } } }
    }
    d = client.search(index = INDEX, body = query)
    x = int(d['aggregations']['max']['value'])
    max_date = datetime.utcfromtimestamp(x / 1000).strftime('%Y-%m-%d')
    return max_date

def build_directory(url, INDEX, TYPE):    
    x = json.load(urllib2.urlopen(url + str(1)))
    r = x['iTotalRecords']
    n = int(math.ceil(float(r) / 25))
    for i in range(0, n + 1): 
        x   = json.load(urllib2.urlopen(url + str(i)))
        out = x['aaData']
        for i in out:
            if args.directory == 'halts':
                _id = str(i['HaltResumeID']) + '_' + str(i['SecurityID'])        
            elif args.directory == 'directory':       
                _id = str(i['SecurityID']) + '_' + str(i['IssuerId'])
            elif args.directory == 'delinquency':       
                _id = str(i['SecurityID']) + '_' + str(i['DCList_ID'])
            try: 
                client.index(index=INDEX, doc_type=TYPE, body=i, id=_id) 
            except: 
                print('document already exists')

def update_directory(url, INDEX, TYPE):    
    x = json.load(urllib2.urlopen(url + str(1)))
    r = x['iTotalRecords']
    n = int(math.ceil(float(r) / 25))
    for i in range(0, n + 1): 
        x   = json.load(urllib2.urlopen(url + str(i)))
        out = x['aaData']
        if to_ref_date(out[0]['DateHalted']) >= get_max_date(INDEX): 
            for i in out:
                _id = str(i['HaltResumeID']) + '_' + str(i['SecurityID'])   
                try:      
                    client.create(index=INDEX, doc_type=TYPE, body=i, id=_id) 
                except: 
                    print('document already exists')
        elif to_ref_date(out[0]['DateHalted']) < get_max_date(INDEX):
            break

# --
# run

if not args.update_halts:
    build_directory(
        url, 
        INDEX, 
        TYPE
    )
elif args.update_halts: 
    update_directory(
        url, 
        INDEX, 
        TYPE
    )