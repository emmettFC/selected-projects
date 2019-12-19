import re
import sys
import json
import funcy as _
import argparse
from yahoo_finance import Share
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan
from datetime import datetime, date, timedelta

# --
# cli 

parser = argparse.ArgumentParser()
parser.add_argument("--config-path",   type = str, action = 'store', default='../config.json')
parser.add_argument("--start-date",   type = str, action = 'store')
parser.add_argument("--end-date",   type = str, action = 'store')
parser.add_argument("--grab-new", action = 'store_true')
args = parser.parse_args()

config = json.load(open(args.config_path))
# config = json.load(open('../config.json'))

client = Elasticsearch([{
    'host' : config['elasticsearch']['hostname'],
    'port' : config['elasticsearch']['hostport']
}])

# --
# vars

INDEX    = config['elasticsearch']['_to_index']
TYPE     = config['elasticsearch']['_type']
PV_INDEX = config['pv']['pv_index']
PV_TYPE  = config['pv']['pv_type']



# -- 
# functions

def get_all_tickers():
    query = {
        "size" : 0,
        "aggs" : {
            "ticker" : {
                "terms" : {
                    "field" : "ticker",
                    "size"  : 0
                }
            }
        }
    }
    res = client.search(index = INDEX, doc_type = TYPE, body = query)
    return _.pluck('key', res['aggregations']['ticker']['buckets'])


def clean(x):
    tmp = {}
    for k in x:
        tmp[k.lower()] = x[k]
    
    x = tmp
    
    num = ['volume', 'adj_close', 'high', 'low', 'close', 'open']
    for n in num:
        if n in x:
            x[n] = float(x[n])
    
    return x


def run(tickers, start_date, end_date):
    for t in tickers:
        try:
            print 'downloading %s' % t
            hist = Share(t).get_historical(start_date, end_date)
            hist = map(clean, hist)
            print 'downloaded %s %d' % (t, len(hist))
                 
            if len(hist) > 0:
                for h in hist:
                    yield {
                        "_index"   : PV_INDEX,
                        "_type"    : PV_TYPE,
                        "_id"      : t + '__' + re.sub('-', '_', h['date']),
                        "_op_type" : 'index',
                        "_source"  : h
                    }
        
        except KeyboardInterrupt:
            raise
        except:
            print >> sys.stderr, 'error @ %s' % t


# --
# run

if not args.grab_new: 
    start_date = args.start_date
    end_date   = args.end_date
elif args.grab_new: 
    start_date = (date.today() - timedelta(days=20)).strftime('%Y-%m-%d')
    end_date   = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')

tickers = get_all_tickers()
tickers.sort()
for a, b in streaming_bulk(client, run(tickers, start_date, end_date), chunk_size=100):
    print a,b
