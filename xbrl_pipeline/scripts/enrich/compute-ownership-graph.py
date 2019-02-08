import re
import json
import argparse

from collections import OrderedDict
from datetime import date, timedelta
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

from pyspark import SparkContext
sc = SparkContext()

# --
# Define CLI
parser = argparse.ArgumentParser(description='grab_new_filings')
parser.add_argument('--from-scratch', dest='from_scratch', action="store_true")
parser.add_argument('--last-week', dest='last_week', action="store_true")
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()

config = json.load(open(args.config_path))

# --
# Defining queries

query = {
    "_source" : [
        "ownershipDocument.periodOfReport", 
        "ownershipDocument.reportingOwner", 
        "ownershipDocument.issuer",
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
                                "field" : "ownershipDocument"
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
                "gte" : str(date.today() - timedelta(days = 9))
            }
        }
    })
elif not args.from_scratch: 
    raise Exception('must chose one option [--from-scratch; --last-week]')


# --
# Connections

client = Elasticsearch([{
    'host' : config["es"]["host"], 
    'port' : config["es"]["port"]
}], timeout = 60000)

rdd = sc.newAPIHadoopRDD(
    inputFormatClass = "org.elasticsearch.hadoop.mr.EsInputFormat",
    keyClass = "org.apache.hadoop.io.NullWritable",
    valueClass = "org.elasticsearch.hadoop.mr.LinkedMapWritable",
    conf = {
        "es.nodes"    : config['es']['host'],
        "es.port"     : str(config['es']['port']),
        "es.resource" : "%s/%s" % (config['forms']['index'], config['forms']['_type']),
        "es.query"    : json.dumps(query)
   }
)

# --
# Function definition

def cln(x):
    return re.sub(' ', '_', str(x))

def get_id(x): 
    return '__'.join(map(cln, x[0]))

def merge_dates(x, min_dates): 
    id_ = get_id(x)
    if min_dates.get(id_, False):
        x[1]['min_date'] = min_dates[id_]
    
    return x

def clean_logical(x):
    tmp = str(x).lower()
    if tmp == 'true':
        return 1
    elif tmp == 'false':
        return 0
    else: 
        return x

def _get_owners(r):
    return {
        "isOfficer"         : clean_logical(r.get('reportingOwnerRelationship', {}).get('isOfficer', 0)),
        "isTenPercentOwner" : clean_logical(r.get('reportingOwnerRelationship', {}).get('isTenPercentOwner', 0)),
        "isDirector"        : clean_logical(r.get('reportingOwnerRelationship', {}).get('isDirector', 0)),
        "isOther"           : clean_logical(r.get('reportingOwnerRelationship', {}).get('isOther', 0)),
        "ownerName"         : clean_logical(r.get('reportingOwnerId', {}).get('rptOwnerName', 0)), 
        "ownerCik"          : clean_logical(r.get('reportingOwnerId',{}).get('rptOwnerCik', 0))
    }

def get_owners(val):
    try: 
        sic = val['header']['ISSUER'][0]['COMPANY-DATA'][0]['ASSIGNED-SIC'][0]
    except (KeyError, IndexError): 
        sic = None
    top_level_fields = {
        "issuerCik"             : val['ownershipDocument']['issuer']['issuerCik'],
        "issuerName"            : val['ownershipDocument']['issuer']['issuerName'],
        "issuerTradingSymbol"   : val['ownershipDocument']['issuer']['issuerTradingSymbol'],
        "periodOfFiling"        : val['ownershipDocument']['periodOfReport'],
        "sic"                   : sic
    }
    ro = val['ownershipDocument']['reportingOwner'] 
    ro = [ro] if type(ro) == type({}) else ro
    ros = map(_get_owners, ro)
    for r in ros:
        r.update(top_level_fields)
    return ros


def get_properties(x): 
    tmp = {
        "issuerCik"             : str(x[1]['issuerCik']).zfill(10), 
        "issuerName"            : str(x[1]['issuerName']).upper(),
        "issuerTradingSymbol"   : str(x[1]['issuerTradingSymbol']).upper(),
        "ownerName"             : str(x[1]['ownerName']).upper(),
        "ownerCik"              : str(x[1]['ownerCik']).zfill(10),
        "isDirector"            : int(x[1]['isDirector']),
        "isOfficer"             : int(x[1]['isOfficer']),
        "isOther"               : int(x[1]['isOther']),
        "isTenPercentOwner"     : int(x[1]['isTenPercentOwner']),
        "periodOfFiling"        : str(x[1]['periodOfFiling']),
        "sic"                   : x[1]['sic']
    }
    return (
        (tmp['issuerCik'], tmp['issuerName'], tmp['issuerTradingSymbol'], tmp['ownerName'], tmp['ownerCik'], tmp['isDirector'], tmp['isOfficer'], tmp['isOther'], tmp['isTenPercentOwner'], tmp['sic']), 
        tmp['periodOfFiling']
    )


def coerce_out(x): 
    tmp = {
        "issuerCik"             : str(x[0][0]), 
        "issuerName"            : str(x[0][1]),
        "issuerTradingSymbol"   : str(x[0][2]),
        "ownerName"             : str(x[0][3]),
        "ownerCik"              : str(x[0][4]),
        "isDirector"            : int(x[0][5]),
        "isOfficer"             : int(x[0][6]),
        "isOther"               : int(x[0][7]),
        "isTenPercentOwner"     : int(x[0][8]),
        "sic"                   : x[0][9],
        "min_date"              : str(x[1]['min_date']),
        "max_date"              : str(x[1]['max_date'])
    }
    tmp['id'] = str(tmp['issuerCik']) + '__' + str(re.sub(' ', '_', tmp['ownerName'])) + '__' + str(tmp['ownerCik']) + '__' + \
                str(tmp['isDirector']) + '__' + str(tmp['isOfficer']) + '__' + str(tmp['isOther']) + '__' + \
                str(tmp['isTenPercentOwner']) + '__' + str(tmp['sic'])
    return ('-', tmp)


# --
# Apply pipeline

df_range = rdd.flatMapValues(get_owners)\
    .map(get_properties)\
    .groupByKey()\
    .mapValues(lambda x: {
        "min_date" : min(x), 
        "max_date" : max(x)
    })


if args.last_week: 
    ids = df_range.map(get_id).collect()
    min_dates = {}
    for i in ids: 
        try:
            mtc          = client.get(index=config['ownership']['index'], doc_type=config['ownership']['_type'], id=i)
            min_dates[i] = mtc['_source']['min_date']
        except:
            print 'missing \t %s' % i
    
    df_out = df_range.map(lambda x: merge_dates(x, min_dates))
    
elif args.from_scratch: 
    df_out = df_range


# --
# Write to ES

df_out.map(coerce_out).saveAsNewAPIHadoopFile(
    path = '-',
    outputFormatClass = "org.elasticsearch.hadoop.mr.EsOutputFormat",
    keyClass = "org.apache.hadoop.io.NullWritable", 
    valueClass = "org.elasticsearch.hadoop.mr.LinkedMapWritable", 
    conf = {
        "es.nodes"           : config['es']['host'],
        "es.port"            : str(config['es']['port']),
        "es.resource"        : '%s/%s' % (config['ownership']['index'], config['ownership']['_type']),
        "es.mapping.id"      : 'id',
        "es.write.operation" : "upsert"
    }
)
