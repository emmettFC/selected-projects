import json, csv, pickle, re
import funcy as _
import numpy as np
import argparse

from pprint import pprint

from datetime import datetime, date, timedelta
from dateutil.parser import parse as dateparse

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

from sklearn import metrics, svm
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, chi2


# --
# cli

parser = argparse.ArgumentParser()
parser.add_argument("--back-fill", action = 'store_true') 
parser.add_argument("--start-date",   type = str, action = 'store')
parser.add_argument("--end-date",   type = str, action = 'store')  
parser.add_argument("--config-path",   type = str, action = 'store', default='../config.json')
parser.add_argument("--model-path",   type = str, action = 'store', default='../models/triclass_model_20150826_1200.pickle') 
args = parser.parse_args()


# --
# config

config_path = args.config_path
config      = json.load(open(config_path))


# --
# import model

model_path = args.model_path
model      = pickle.load(open(model_path, 'rb'))


# --
# define query

if not args.end_date: 
    args.end_date = date.today() + timedelta(days = 1)


if args.start_date: 
    params = {
        'back_fill'    : args.back_fill,
        'start_date'   : dateparse(str(args.start_date)).strftime('%Y-%m-%d %H:%M:%S'),
        'end_date'     : dateparse(str(args.end_date)).strftime('%Y-%m-%d %H:%M:%S'),
    }
elif not args.start_date: 
    params = {
        'back_fill'    : args.back_fill,
        'end_date'     : dateparse(str(args.end_date)).strftime('%Y-%m-%d %H:%M:%S'),
    }


must = []
if args.start_date: 
    must.append({ "range" : {"time" : {"gte" : params['start_date'], "lte" : params['end_date']}}})
elif not args.start_date: 
    print('--no date range applied--')

if params['back_fill']:
    must.append({ 
        "filtered": {
            "filter": {
                "missing": {
                    "field": "__meta__.tri_pred" 
                }
            }
        }
    }) 

query = {"query" : {"bool" : {"must" : must}}}
print query


# --
# functions

def apply_model_stream(docs):
    global model
    
    ids  = _.pluck('id', docs)
    msgs = map(lambda x: _.flatten([x])[0], _.pluck('msg', docs))
    
    z    = model['vect'].transform(msgs)
    z    = model['ch2'].transform(z)
    z    = model['tfidf'].transform(z)
    pred = model['clf'].predict_proba(z)
    
    for i in range(0, len(ids)):
        yield {
            "_id"      : ids[i],
            "_type"    : config['elasticsearch']['_type'],
            "_index"   : config['elasticsearch']['_to_index'],
            "_op_type" : "update",
            "doc" : {
                '__meta__' : {
                    'tri_pred' : {
                        'neg'  : float(pred[i][0]),
                        'neut' : float(pred[i][1]),
                        'pos'  : float(pred[i][2])
                    }
                }
            }
        }


def run(query):
    buff = []
    for a in scan(client, index = config['elasticsearch']['_to_index'], doc_type = config['elasticsearch']['_type'], query = query):
        buff.append({'id' : a['_id'], 'msg' : a['_source']['msg']})     
        
        if len(buff) >= 5000:
            for d in apply_model_stream(buff):
                yield d
            
            buff = []
    
    for d in apply_model_stream(buff):
        yield d


# --
# run 

client = Elasticsearch([{
    'host' : config['elasticsearch']['hostname'], 
    'port' : config['elasticsearch']['hostport']
}], timeout = 60000)

for a,b in streaming_bulk(client, run(query), chunk_size = 10000):
    print a, b
