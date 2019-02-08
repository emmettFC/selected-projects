'''

    Add CIKs by joining on tickers

    python enrich-ticker2cik.py --index omx --field-name tickers.symbol.cat

'''
import sys
import json
import argparse

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

# --
# cli 

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
parser.add_argument("--index", type=str, action='store', required=True)
parser.add_argument("--field-name", type=str, action='store', required=True)
args = parser.parse_args()

config = json.load(open(args.config_path))
# config = json.load(open('../config.json'))

client = Elasticsearch([{
    'host' : config['es']['host'], 
    'port' : config['es']['port']
}], timeout = 60000)


# --
# Run

def get_lookup():
    query = {
        "_source" : ["max_date", "sic", "cik", "ticker", "name"],
        "query" : {
            "filtered" : {
                "filter" : {
                    "exists" : {
                        "field" : "ticker"
                    }
                }
            }
        }
    }
    
    out = {}
    for a in scan(client, index=config['symbology']['index'], query=query):
        out[a['_source']['ticker']] = a['_source']
    
    return out

def run(lookup): 
    query = {
        "fields" : args.field_name,
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
        mtc = lookup.get(a['fields'][args.field_name][0], {})
        sym.update(mtc)
        yield {
            "_id"      : a['_id'],
            "_type"    : a['_type'],
            "_index"   : a['_index'],
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
    counter = 0
    for a,b in streaming_bulk(client, run(get_lookup()), chunk_size=1000, raise_on_error=False):
        pass
    print '\ndone\n'
