import re
import csv
import json
import pickle 
import argparse

from datetime import datetime, date, timedelta
from dateutil.parser import parse as dateparse

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# --
# cli 

parser = argparse.ArgumentParser()
parser.add_argument("--config-path",   type = str, action = 'store', default='../config.json')
args = parser.parse_args()

if not args.config_path: 
    print('usage python add_cik_and_ticker.py --config-path=path/to/config')
else: 
    config_path = args.config_path


# --
# config 

config  = json.load(open(config_path))


# --
# es connection

client = Elasticsearch([{
    'host' : config['elasticsearch']['hostname'], 
    'port' : config['elasticsearch']['hostport']
}], timeout = 60000)


# -- 
# define query

query = {
  "query" : {
      "filtered" : {
          "filter" : {
              "missing" : {
                  "field" : "__meta__.sym"
              }
          }
      }
  }
}


# -- 
# functions

def run(query): 
    global config
    for a in scan(client, index = config['elasticsearch']['_to_index'], query = query): 
        res = client.search(index = config['ref_index'], body = {
            "_source" : ['cik', 'sic', 'name', 'max_date', "ticker"],
            "sort" : [
                {"max_date" : {"order" : "desc"}}
            ],
            "query" : {
                "match" : {
                    "ticker" : a['_source']['ticker']
                    }
                }
            })
        
        if res['hits']['total'] > 0:
            mtc   = res['hits']['hits'][0]['_source']
            pname = a['_source']['board'].lower()
            sname = mtc['name'].lower() 
            doc   = {
                '__meta__' : {
                    'sym' : { 
                        "match_attempted"       : True, 
                        "cik"                   : mtc['cik'], 
                        "sic"                   : mtc['sic'],
                        "name"                  : mtc['name'], 
                        "max_date"              : mtc['max_date'],
                        "fuzz_ratio"            : fuzz.ratio(pname, sname),
                        "fuzz_token_sort_ratio" : fuzz.token_sort_ratio(pname, sname), 
                    }
                }
            }
        else: 
            doc = {
                '__meta__' : {
                    'sym' : { 
                        "match_attempted" : True
                    }
                }
            }
        
        yield {
            "_id"      : a['_id'],
            "_type"    : config['elasticsearch']['_type'],
            "_index"   : config['elasticsearch']['_to_index'],
            "_op_type" : "update",
            "doc"      : doc
        }


# --
# run

for a,b in streaming_bulk(client, run(query), chunk_size = 1000, raise_on_error = False):
    print a, b