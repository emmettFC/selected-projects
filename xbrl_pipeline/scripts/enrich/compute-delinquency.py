import json
import time
import argparse
import holidays
import dateutil.parser as parser

import datetime
from datetime import timedelta, date

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, streaming_bulk

# --
# deadlines lookup

deadlines = {
    "10-K" : {
        "Large Accelerated Filer"   : {
            'preDec1506' : 75,
            'postDec1506': 60
        }
        "Accelerated Filer"         : {
            'preDec1503' : 90,
            'postDec1503': 75
        }
        "Non-accelerated Filer"     : 90,
        "Smaller Reporting Company" : 90
    },
    "10-Q" : {
        "Large Accelerated Filer"   : 40,
        "Accelerated Filer"         : {
            "preDec1504" : 45,
            "postDec1504": 40
        }
        "Non-accelerated Filer"     : 45,
        "Smaller Reporting Company" : 45
    }
}

# -- 
# CLI

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type = str, action = 'store', default='../config.json')
args = parser.parse_args()

# -- 
# config

config = json.load(open(args.config_path))


# --
# es connection

client = Elasticsearch([{
  'host' : config['es']['host'], 
  'port' : config['es']['port']
  }], timeout = 60000)


# --
# Define query

query = { 
    "query" : { 
        "bool" : { 
            "must" : [
                {
                    "terms" : { 
                        "_enrich.status.cat" : ["Large Accelerated Filer", "Accelerated Filer", "Smaller Reporting Company", "Non-accelerated Filer"]
                    }
                },
                {
                    "query" : { 
                        "filtered": {
                            "filter": {
                                "exists": {
                                    "field": "_enrich.period"
                                  }
                              }
                          }
                      }
                  },
                {
                    "query" : { 
                        "filtered": {
                            "filter": {
                                "missing": {
                                    "field": "_enrich.deadline"
                                }
                            }
                        }
                    }
                }
            ]
        } 
    }
}


# --
# Functions

def get_days(src): 
    if src['_enrich']['status'] == "Large Accelerated Filer": 
        if src['form'] == "10-K": 
            if src['_enrich']['period'] < '2006-12-15': 
                ndays = deadlines[src['form']][src['_enrich']['status']]['preDec1506']
            else: 
                ndays = deadlines[src['form']][src['_enrich']['status']]['postDec1506']
        elif src['form'] == "10-Q":
            ndays = deadlines[src['form']][src['_enrich']['status']]
    elif src['_enrich']['status'] == "Accelerated Filer": 
        if src['form'] == "10-K": 
            if src['_enrich']['period'] < '2003-12-15': 
                ndays = deadlines[src['form']][src['_enrich']['status']]['preDec1503']
            else: 
                ndays = deadlines[src['form']][src['_enrich']['status']]['postDec1503']        
        elif src['form'] == "10-Q":
            if src['_enrich']['period'] < '2004-12-15': 
                ndays = deadlines[src['form']][src['_enrich']['status']]['preDec1504'] 
            else: 
                ndays = deadlines[src['form']][src['_enrich']['status']]['postDec1504']        
    else: 
        ndays = deadlines[src['form']][src['_enrich']['status']]
    
    return ndays


def add_delinquency(src, us_holidays=holidays.US()): 
    r     = map(int, src['_enrich']['period'].split('-'))
    d     = datetime.date(r[0], r[1], r[2])  
    ndays = get_days(src)
    dl = d + timedelta(days=ndays)
    while (dl in us_holidays) or (dl.weekday() >= 5):
        dl += timedelta(days=1)
       
    filed = map(int, src['date'].split('-'))
    filed = datetime.date(filed[0], filed[1], filed[2])  
    src['_enrich']['deadline']         = dl.strftime("%Y-%m-%d")    
    src['_enrich']['days_to_deadline'] = (dl - filed).days
    src['_enrich']['is_late']          = src['_enrich']['days_to_deadline'] < 0
    
    return src

# --
# Run

for doc in scan(client, index = config['delinquency']['index'], query = query): 
    client.index(
        index    = config['delinquency']['index'], 
        doc_type = config['delinquency']['_type'], 
        id       = doc["_id"],
        body     = add_delinquency(doc['_source']), 
    )