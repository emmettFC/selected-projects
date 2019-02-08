'''
    Matches names to CIK numbers via Elasticsearch query
'''

import sys
import json
import argparse
from datetime import datetime, date
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

# --
# cli 

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
parser.add_argument("--index", type=str, action='store', required=True)
parser.add_argument("--field-name", type=str, action='store', required=True)
parser.add_argument("--threshold", type=float, action='store', default=7)
args = parser.parse_args()

config = json.load(open(args.config_path))
client = Elasticsearch([{
    'host' : config['es']['host'], 
    'port' : config['es']['port']
}], timeout = 60000)

# --
# Run

def run():
    query = {
        "_source" : args.field_name,
        "query" : {
            "filtered" : {
                "filter" : {
                    "and" : [
                        {
                            "missing" : {
                                "field" : "__meta__.sym.match_attempted"
                            }
                        },
                        {
                            "exists" : {
                                "field" : args.field_name
                            }
                        }
                    ]
                }
            }
        }
    }
    total_count = client.count(index=config[args.index]['index'], body=query)['count']
    
    counter = 0
    for a in scan(client, index=config[args.index]['index'], query=query):
        sym = {"match_attempted" : True}
        
        res = client.search(index=config['symbology']['index'], body={
            "size"    : 1,
            "_source" : "cik",
            "query"   : {
                "match_phrase" : {
                    "name" : a['_source'][args.field_name]
                }
            }    
        })['hits']['hits']
        
        if res:
            if res[0]['_score'] > args.threshold:
                sym.update(res[0]['_source'])
            
        yield {
            "_index"   : a['_index'],
            "_type"    : a['_type'],
            "_id"      : a['_id'],
            "_op_type" : "update",
            "doc" : {
                "__meta__" : {
                    "sym" : sym     
                }
            }            
        }
        counter += 1
        sys.stdout.write('\r Completed \t %d \t out of \t %d' % (counter, total_count))
        sys.stdout.flush()


if __name__ == "__main__":
    for a,b in streaming_bulk(client, run(), chunk_size=100, raise_on_error=False):
        pass
    print '\ndone\n'
