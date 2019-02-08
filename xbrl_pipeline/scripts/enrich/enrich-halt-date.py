import re
import csv
import json
import pickle 
import argparse

from datetime import datetime, date, timedelta
from dateutil.parser import parse as dateparse

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

# --
# cli 

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type = str, action = 'store', default='../config.json')
args = parser.parse_args()


# --
# config 

config_path = args.config_path
config      = json.load(open(config_path))

# --
# es connection

client = Elasticsearch([{
    'host' : config['es']['host'], 
    'port' : config['es']['port']
}], timeout = 60000)


# -- 
# global vars 

INDEX = config['otc_halts']['index']
TYPE  = config['otc_halts']['_type']

# -- 
# define query

query = {
  "query" : {
      "filtered" : {
          "filter" : {
              "missing" : {
                 "field" : "_enrich.halt_short_date"
              }
          }
      }
  }
}


# -- 
# function

def enrich_dates(body):
    body['_enrich'] = {} 
    body['_enrich']['halt_short_date'] = to_ref_date(body['DateHalted'])
    body['_enrich']['halt_long_date']  = to_long_date(body['DateHalted'])
    body['_enrich']['load_short_date'] = to_ref_date(body['LoadDate'])
    body['_enrich']['load_long_date']  = to_long_date(body['LoadDate'])
    return body

def to_ref_date(date): 
    d = int(re.sub('\D', '', date)) 
    out_date = datetime.utcfromtimestamp(d / 1000).strftime('%Y-%m-%d')
    return out_date

def to_long_date(date): 
    d = int(re.sub('\D', '', date)) 
    out_date = datetime.utcfromtimestamp(d / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return out_date


# --
# run

for doc in scan(client, index = INDEX, query = query): 
    client.index(
        index    = INDEX, 
        doc_type = TYPE, 
        id       = doc["_id"],
        body     = enrich_dates( doc['_source'] )
    )
    print(doc['_id'])