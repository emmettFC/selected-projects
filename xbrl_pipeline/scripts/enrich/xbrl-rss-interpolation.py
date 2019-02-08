import itertools
import argparse
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan
from elasticsearch.helpers import reindex


# --
# CLI

parser = argparse.ArgumentParser(description='ingest-xbrl-rss-docs')
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()


# -- 
# config 

config = json.load(open(args.config_path))


# -- 
# es connection

client = Elasticsearch([{"host" : config['es']['host'], "port" : config['es']['port']}])

# --
# query

query = { 
  "query" : { 
    "bool" : { 
      "must" : [
        {
          "filtered" : { 
            "filter" : { 
              "exists" : { 
                "field" : "__meta__.financials"
              } 
            } 
          } 
        },
        {
          "filtered" : { 
            "filter" : { 
              "missing" : { 
                "field" : "__meta__.financials.interpolated"
              } 
            } 
          } 
        }
      ]
    }
  }
}

# -- 
# functions

def _assets( doc ): 
    val =((doc['liabilitiesAndStockholdersEquity']['value'] if doc['liabilitiesAndStockholdersEquity']!= None else \
          (doc['liabilities']['value'] if doc['liabilities'] != None else 0)) +
          (doc['stockholdersEquity']['value'] if doc['stockholdersEquity'] != None else 0))
    return val


def _liabilities( doc ): 
    val =((doc['liabilitiesAndStockholdersEquity']['value'] if doc['liabilitiesAndStockholdersEquity'] != None else \
          (doc['assets']['value'] if doc['assets']['value'] != None else 0)) -
          (doc['stockholdersEquity']['value'] if doc['stockholdersEquity'] != None else 0))
    return val

def _stockholdersEquity( doc ): 
    val =((doc['liabilitiesAndStockholdersEquity']['value'] if doc['liabilitiesAndStockholdersEquity'] != None else \
          (doc['assets']['value'] if doc['assets'] != None else 0)) -
          (doc['liabilities']['value'] if doc['liabilities'] != None else 0))
    return val

def _liabilitiesAndStockholdersEquity( doc ): 
    val =(doc['assets']['value'] if doc['assets'] != None else \
         (doc['liabilities']['value'] if doc['liabilities'] != None else 0) + \
         (doc['stockholdersEquity']['value'] if doc['stockholdersEquity'] != None else 0))
    return val


def interpolate( a ): 
    doc = a['_source']['__meta__']['financials']
    for k, v in doc.iteritems(): 
        if v == None and k == 'assets': 
            doc['assets'] = {}
            doc['assets']['value'] = _assets( doc )
        elif v == None and k == 'liabilities': 
            doc['liabilities'] = {}
            doc['liabilities']['value'] = _liabilities( doc )
        elif v == None and k == 'stockholdersEquity': 
            doc['stockholdersEquity'] = {}
            doc['stockholdersEquity']['value'] = _stockholdersEquity( doc )
        elif v == None and k == 'liabilitiesAndStockholdersEquity': 
            doc['liabilitiesAndStockholdersEquity'] = {}
            doc['liabilitiesAndStockholdersEquity']['value'] = _liabilitiesAndStockholdersEquity( doc )        
        else: 
            pass
    doc['interpolated'] = True
    return a



# -- 
# run 

for a in scan(client, index = config['aq_forms_enrich']['index'], query = query): 
    s = interpolate( a )
    client.index(index = config['aq_forms_enrich']['index'], doc_type = config['aq_forms_enrich']['_type'], body = s['_source'], id = s['_id'])