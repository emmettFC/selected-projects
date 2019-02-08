import json
import argparse
from datetime import datetime, date
from fuzzywuzzy import fuzz, process
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan


# --
# cli 

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()

config = json.load(open(args.config_path))
client = Elasticsearch([{
    'host' : config['es']['host'], 
    'port' : config['es']['port']
}], timeout = 60000)


# -- 
# define query

query = {
  "query" : {
      "filtered" : {
          "filter" : {
              "missing" : {
                 "field" : "__meta__.halts"
              }
          }
      }
  }
}


# -- 
# functions

def run(query): 
    for a in scan(client, index=config['symbology']['index'], query=query): 
        res = client.search(index=config['suspension']['index'], body={
            "_source" : ["company", "date", "link"],
            "query" : {
                "match" : {
                    "company" : a['_source']['name']
                    }
                }
            })
        
        if res['hits']['total'] > 0:
          mtc       = res['hits']['hits'][0]['_source']
          sym_name  = a['_source']['name'].lower()
          halt_name = mtc['company'].lower() 
          x         = fuzz.token_sort_ratio(sym_name, halt_name)
          y         = fuzz.ratio(sym_name, halt_name)
          halts     = {"match_attempted" : True}
          if res['hits']['hits'][0]['_score'] >= 1 and x >= 90):
              halts.update(mtc)
              halts.update({
                  "fuzz_ratio"            : y,
                  "fuzz_token_sort_ratio" : x, 
                  "match_score"           : a['_score']
              })

        yield {
            "_id"      : a['_id'],
            "_type"    : config['symbology']['_type'],
            "_index"   : config['symbology']['index'],
            "_op_type" : "update",
            "doc" : {
                "__meta__" : {
                    "halts" : halts
                }
            }
        }

for a,b in streaming_bulk(client, run(query), chunk_size=1000, raise_on_error=False):
    print a, b