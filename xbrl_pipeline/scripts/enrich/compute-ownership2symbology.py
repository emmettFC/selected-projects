'''
    Create symbology index from forms index
'''

import re
import json
import argparse
from hashlib import sha1
from datetime import date, timedelta
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

from pyspark import SparkContext
sc = SparkContext(appName='ownership2symbology')

# -- 
# CLI

parser = argparse.ArgumentParser(description='ownership2symbology')
parser.add_argument('--from-scratch', dest='from_scratch', action="store_true")
parser.add_argument('--last-week', dest='last_week', action="store_true")
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
parser.add_argument("--testing", action='store_true')
args = parser.parse_args()

config = json.load(open(args.config_path))
# config = json.load(open('../config.json'))

es_resource_out_expr = '%s/%s' if not args.testing else '%s_test/%s'

# --
# Defining queries

query = {
    "_source" : [
        "ownershipDocument.issuer", 
        "ownershipDocument.periodOfReport", 
        "header.ACCESSION-NUMBER", 
        "header.ISSUER.COMPANY-DATA.ASSIGNED-SIC"
    ],
    "query": {
        "bool" : { 
            "must" : [
                {
                    "filtered" : {
                        "filter" : {
                            "exists" : {
                                "field" : "ownershipDocument.issuer.issuerCik"
                            }
                        }
                    }
                }
            ]
        } 
    }
}

if args.last_week: 
    query['query']['bool']['must'].append({
        "range" : {
            "ownershipDocument.periodOfReport" : {
                "gte" : str(date.today() - timedelta(days=9))
            }
        }
    })
elif not args.from_scratch: 
    print 'must chose one option [--from-scratch; --last-week]'


# --
# Connections

client = Elasticsearch([{
    'host' : config["es"]["host"], 
    'port' : config["es"]["port"]
}], timeout = 60000)

rdd = sc.newAPIHadoopRDD(
    inputFormatClass="org.elasticsearch.hadoop.mr.EsInputFormat",
    keyClass="org.apache.hadoop.io.NullWritable",
    valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
    conf={
        "es.nodes"    : config['es']['host'],
        "es.port"     : str(config['es']['port']),
        "es.resource" : "%s/%s" % (config['forms']['index'], config['forms']['_type']),
        "es.query"    : json.dumps(query)
   }
)

# --
# Function definitions
def get_id(x): 
    return sha1('__'.join(map(str, x[0]))).hexdigest()

def merge_dates(x, min_dates):
    id_ = get_id(x)
    if min_dates.get(id_, False):
        x[1]['min_date'] = min_dates[id_]
    
    return x

def get_properties(x): 
    try: 
        sic = x[1]['header']['ISSUER'][0]['COMPANY-DATA'][0]['ASSIGNED-SIC'][0]
    except (KeyError, IndexError): 
        sic = None
    
    tmp = {
        "cik"    : str(x[1]['ownershipDocument']['issuer']['issuerCik']).zfill(10),
        "name"   : str(x[1]['ownershipDocument']['issuer']['issuerName']).upper(),
        "ticker" : str(x[1]['ownershipDocument']['issuer']['issuerTradingSymbol']).upper(), 
        "sic"    : sic,
        "period" : str(x[1]['ownershipDocument']['periodOfReport']),
    }
    
    return (
        (tmp['cik'], tmp['name'], tmp['ticker'], tmp['sic']), 
        (tmp['period'], tmp['period'])
    )

def coerce_out(x):
    return ('-', {
        "id"       : get_id(x),
        "cik"      : x[0][0],
        "name"     : x[0][1],
        "ticker"   : x[0][2],
        "sic"      : x[0][3],
        "min_date" : x[1]['min_date'],
        "max_date" : x[1]['max_date'],
        "__meta__" : {
            "source" : "ownership"
        }
    })


# --
# Apply pipeline

df_range = rdd.map(get_properties)\
    .reduceByKey(lambda a,b: (min(a[0], b[0]), max(a[1], b[1])))\
    .mapValues(lambda x: {
        "min_date" : x[0],
        "max_date" : x[1]
    })

if args.last_week:
    ids = df_range.map(get_id).collect()
    min_dates = {}
    for i in ids: 
        try:
            mtc          = client.get(index=config['symbology']['index'], doc_type=config['symbology']['_type'], id=i)
            min_dates[i] = mtc['_source']['min_date']
        except:
            print 'missing \t %s' % i
    
    df_out = df_range.map(lambda x: merge_dates(x, min_dates))
    
elif args.from_scratch: 
    df_out = df_range

# --
# Write to ES

df_out.map(coerce_out).saveAsNewAPIHadoopFile(
    path='-',
    outputFormatClass='org.elasticsearch.hadoop.mr.EsOutputFormat',
    keyClass='org.apache.hadoop.io.NullWritable', 
    valueClass='org.elasticsearch.hadoop.mr.LinkedMapWritable', 
    conf={
        'es.input.json'      : 'false',
        'es.nodes'           : config['es']['host'],
        'es.port'            : str(config['es']['port']),
        'es.resource'        : es_resource_out_expr % (config['symbology']['index'], config['symbology']['_type']),
        'es.mapping.id'      : 'id',
        'es.write.operation' : 'upsert'
    }
)
