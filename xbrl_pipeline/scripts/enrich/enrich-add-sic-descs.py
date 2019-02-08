import re
import csv
import sys
import json
import pickle 
import argparse

from datetime import datetime, date, timedelta
from dateutil.parser import parse as dateparse

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, streaming_bulk

# --
# cli 

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
parser.add_argument("--lookup-path", type=str, action='store', default='../reference/sic_ref.p')
parser.add_argument("--index", type=str, action='store', required=True)
args=parser.parse_args()

config = json.load(open(args.config_path))
lookup = pickle.load(open(args.lookup_path))
client = Elasticsearch([{
    'host' : config['es']['host'], 
    'port' : config['es']['port']
}], timeout=60000)


# -- 
# define query
def gen():
    query = {
        "_source" : "sic",
        "query" : {
            "filtered" : {
                "filter" : {
                    "and" : [
                        {
                            "missing" : {
                                "field" : "__meta__.sic_lab"
                            }
                        },
                        {
                            "exists" : {
                                "field" : "sic"
                            }
                        }
                    ] 
                }
            }
        }
    }
    
    total_count = client.count(index=config[args.index]['index'], body=query)['count']
    
    counter = 0
    for doc in scan(client, index=config[args.index]['index'], query=query): 
        try:
            yield {
                "_index"    : doc['_index'], 
                "_type"     : doc['_type'], 
                "_id"       : doc['_id'],
                "_op_type"  : "update",
                "doc"       : {
                    "__meta__" : {
                        "sic_lab" : lookup.get(doc['_source']['sic'], None)
                    }
                }
            }
            counter += 1
            sys.stdout.write('\r Completed \t %d \t out of \t %d' % (counter, total_count))
            sys.stdout.flush()
        except:
            print doc
            pass


for a,b in streaming_bulk(client, gen(), chunk_size=2500):
    pass

print