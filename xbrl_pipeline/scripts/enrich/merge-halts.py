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
parser.add_argument("--config-path", type = str, action = 'store', default='../config.json')
parser.add_argument("--most-recent", action='store_true')
parser.add_argument("--from-scratch", action='store_true')
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

TARGET_INDEX  = config['suspension']['index']
TARGET_TYPE   = config['suspension']['_type']

REF_INDEX     = config['otc_halts']['index']
REF_TYPE      = config['otc_halts']['_type']



# -- 
# functions

def get_max_date():
    global config 
    query = {
        "size" : 0,
        "aggs" : { "max" : { "max" : { "field" : "date" } } }
    }
    d = client.search(index = TARGET_INDEX, body = query)
    x = int(d['aggregations']['max']['value'])
    max_date = datetime.utcfromtimestamp(x / 1000).strftime('%Y-%m-%d')
    return max_date


def build_out(ratio, score, hits, body, a, hit):
    if ratio >= 65 and score >= 1 and hits > 0: 
        out = {
                "_id"      : body["_id"],
                "_type"    : TARGET_TYPE,
                "_index"   : TARGET_INDEX,
                "_op_type" : "update",
                "doc"      : { 
                    "__meta__" : { 
                        'finra' : { 
                            'ticker'         : hit['SymbolName'],
                            'company'        : hit['CompanyName'],
                            'haltResumeID'   : hit['HaltResumeID'],
                            'haltID'         : hit['TradeHaltID'],
                            'haltReasonCode' : hit['HaltReasonCode'],
                            'marketCat'      : hit['MarketCategoryLookup'],
                            'dateHalted'     : hit['_enrich']['halt_long_date'],
                            'dateLoaded'     : hit['_enrich']['load_long_date'],
                            'score'          : body['_score'],
                            'ratio'          : ratio,
                            'secHalt'        : True,
                            'matched'        : True
                            }
                        }
                    }
            }
    else: 
        out = {
            "_id"      : a['_id'],
            "_type"    : TARGET_TYPE,
            "_index"   : TARGET_INDEX,
            "_op_type" : "index",
            "_source"      : { 
                "date"           : hit['_enrich']['halt_short_date'],
                "company"        : hit['SymbolName'],
                "link"           : None,
                "release_number" : None,
                "__meta__" : { 
                    'finra' : { 
                        'ticker'         : hit['SymbolName'],
                        'company'        : hit['CompanyName'],
                        'haltResumeID'   : hit['HaltResumeID'],
                        'haltID'         : hit['TradeHaltID'],
                        'haltReasonCode' : hit['HaltReasonCode'],
                        'marketCat'      : hit['MarketCategoryLookup'],
                        'dateHalted'     : hit['_enrich']['halt_long_date'],
                        'dateLoaded'     : hit['_enrich']['load_long_date'],
                        'score'          : 0,
                        'ratio'          : ratio, 
                        'secHalt'        : True,
                        'matched'        : False
                    }
                }
            }
        }   
    return out


def run(query): 
    for a in scan(client, index = REF_INDEX, query = query):
        hit = a['_source'] 
        if hit['IsSECRelatedHalt'] == "Yes" and hit['ActionDescription'] == 'Halt': 
            res = client.search(index = TARGET_INDEX, body = {
                "sort" : [
                    {
                        "_score" : {
                            "order" : "desc"
                            }
                        }],
                "query" : {
                    "bool" : { 
                        "must" : [
                            {
                                "match" : {
                                    "company" : hit['CompanyName']
                                    }
                                },
                            {
                                "match" : { 
                                    "date" : hit['_enrich']['halt_short_date']
                                        }
                                    }
                                ]
                            }
                        }
                    })
            if res['hits']['total'] > 0:
                mtc          = res['hits']['hits'][0]['_source']
                sym_name     = hit['CompanyName'].lower().replace('common stock', '').replace('ordinary shares', '')
                halt_name    = mtc['company'].lower() 
                x            = fuzz.token_sort_ratio(sym_name, halt_name)
                y            = fuzz.ratio(sym_name, halt_name)
                body         = res['hits']['hits'][0]
                out          = build_out(x, body['_score'], 1, body, a, hit)
                out_log = {
                    "_id"      : a['_id'],
                    "_type"    : REF_TYPE,
                    "_index"   : REF_INDEX,
                    "_op_type" : "update",
                    "doc"      : { 
                        "__meta__" : { 
                            "match_attempted" : True,
                            "match_success"   : True
                        }
                    }
                }
            elif res['hits']['total'] == 0: 
                out = build_out(0, 0, 0, 0, a, hit)
                out_log = {
                    "_id"      : a['_id'],
                    "_type"    : REF_TYPE,
                    "_index"   : REF_INDEX,
                    "_op_type" : "update",
                    "doc"      : { 
                        "__meta__" : { 
                            "match_attempted" : True,
                            "match_success"   : False
                        }
                    }
                }
            
            if out: 
                yield out
            yield out_log
        
        else: 
            pass



def run2(query): 
    for a in scan(client, index = REF_INDEX, query = query):
        hit = a['_source'] 
        if hit['IsSECRelatedHalt'] == "No" and hit['ActionDescription'] == 'Halt': 
            _id = a['_id']
            out = {
                "_id"      : _id,
                "_type"    : TARGET_TYPE,
                "_index"   : TARGET_INDEX,
                "_op_type" : "index",
                "_source"      : { 
                        "date"           : hit['_enrich']['halt_short_date'],
                        "company"        : hit['SymbolName'],
                        "link"           : None,
                        "release_number" : None,
                        "__meta__" : { 
                            'finra' : { 
                                'ticker'         : hit['SymbolName'],
                                'company'        : hit['CompanyName'],
                                'haltResumeID'   : hit['HaltResumeID'],
                                'haltID'         : hit['TradeHaltID'],
                                'haltReasonCode' : hit['HaltReasonCode'],
                                'marketCat'      : hit['MarketCategoryLookup'],
                                'dateHalted'     : hit['_enrich']['halt_long_date'],
                                'dateLoaded'     : hit['_enrich']['load_long_date'],
                                'score'          : 0,
                                'ratio'          : 0,
                                'secHalt'        : False,
                                'matched'        : False
                            }
                        }
                    }
            }
            out_log = {
                "_id"      : a['_id'],
                "_type"    : REF_TYPE,
                "_index"   : REF_INDEX,
                "_op_type" : "update",
                "doc"      : { 
                    "__meta__" : { 
                        "match_attempted" : True,
                        "match_success"   : True
                    }
                }
            }
            if out: 
                yield out
            yield out_log
        
        else: 
            pass


# --
# run 

if args.from_scratch: 
    query = {
        "query" : { 
            "range" : { 
                "_enrich.halt_short_date" : { 
                    "lte" : get_max_date()
                }
            }
        }
    }
elif args.most_recent: 
    query = {
        "query" : { 
            "bool" : { 
                "must" : [
                    {
                        "range" : { 
                            "_enrich.halt_short_date" : { 
                                "lte" : get_max_date()
                            }
                        }
                    },
                    {
                        "filtered" : { 
                            "filter" : { 
                                "missing" : { 
                                    "field" : "__meta__.match_attempted"
                                }
                            }
                        }
                    }
                ]
            }
        }
    }


for a,b in streaming_bulk(client, run(query), chunk_size = 1000, raise_on_error = False):
    print a, b


for a,b in streaming_bulk(client, run2(query), chunk_size = 1000, raise_on_error = False):
    print a, b