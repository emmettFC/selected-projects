import re, json
import argparse
import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

from ftplib import FTP
from sec_header_ftp_download import *

# --
# cli 

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type = str, action = 'store', default='../config.json')
parser.add_argument("--from-scratch", action='store_true')
parser.add_argument("--update", action='store_true')
parser.add_argument("--status", action='store_true')
parser.add_argument("--period", action='store_true')
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
# ftp connection 

ftpcon = SECFTP(FTP('ftp.sec.gov', 'anonymous'))


# -- 
# define query

if args.status: 
    if args.from_scratch: 
        query = {
          "query" : { 
            "terms" : { 
              "form.cat" : ["10-K", "10-Q"]
            }
          }
        }
    elif args.update: 
        query = {
          "query" : { 
            "bool" : { 
              "must" : [
                {
                  "query" : { 
                      "filtered": {
                          "filter": {
                              "missing": {
                                  "field": "download_try"
                                  }
                              }
                          }
                      }
                  },
                {
                  "terms" : { 
                    "form.cat" : ["10-K", "10-Q"]
                  }
                }
                ]
            }
          }
        }
elif args.period: 
    query = {
        "query" : { 
            "filtered" : { 
                "filter" : { 
                    "missing" : { 
                        "field" : "_enrich.period"
                    }
                }
            }
        }
    }


# -- 
# define global reference

afs_ref = {
    'LAF' : 'Large Accelerated Filer',
    'ACC' : 'Accelerated Filer',
    'SRA' : 'Accelerated Filer',   
    'NON' : 'Non-accelerated Filer',
    'SML' : 'Smaller Reporting Company'
}


# --
# functions

def parse_adsh ( body ): 
    acc = re.compile("\d{5,}-\d{2}-\d{3,}")
    val = re.findall(acc, body['url'])[0]
    return val


def get_status ( sub ):
  if len(sub['afs']) == 0: 
    status = None
  else: 
    regex  = re.compile('[^a-zA-Z]')
    key    = regex.sub('', sub['afs'])
    status = afs_ref[key]
  return status


def get_period ( x ): 
    p    = [int(x[:4]), int(x[4:6]), int(x[6:8])]
    date = datetime.date(p[0], p[1], p[2])  
    return date


def enrich_status( body ): 
    body['_enrich'] = {}
    acc             = parse_adsh( body )
    query           = {"query" :{"match" :{"_id" : acc}}}
    acc_match       = []
    for doc in scan(client, index = "xbrl_submissions_cat", query = query): 
        acc_match.append(doc)
        # --
    if len(acc_match) == 1: 
        sub = acc_match[0]['_source']
        body['_enrich']['status'] = get_status( sub )
        body['_enrich']['meta']   = 'matched_acc'
        # --
    elif len(acc_match) == 0: 
        cik       = body['cik'].zfill(10)
        r         = map(int, body['date'].split('-'))
        date      = datetime.date(r[0], r[1], r[2])  
        query     = {"query" :{"match" :{"cik" : cik}}}
        cik_match = []
        for doc in scan(client, index = "xbrl_submissions_cat", query = query): 
            m             = doc['_source']
            s_date        = get_period(m['filed'])
            m['date_dif'] = abs((s_date - date).days)
            cik_match.append(m)
            # --
        if len(cik_match) == 0: 
          body['_enrich']['meta']   = 'no_available_match'
          body['_enrich']['status'] = None
        elif len(cik_match) > 0: 
            out = sorted(cik_match, key=lambda k: k['date_dif']) 
            body['_enrich']['status'] = get_status( out[0] )
            body['_enrich']['meta']   = 'matched_cik'
    else: 
        print('-- query not functioning properly --')
        # -- 
    return body


def enrich_deadline( body ): 
    path   = ftpcon.url_to_path(body['url'])
    try: 
        x      = ftpcon.download_parsed(path)['PERIOD'][0]
        prd    = x[:4] + '-' + x[4:6] + '-' + x[6:8]
        body['_enrich']['period'] = prd
        try: 
            body['_enrich']['doc_count'] = int(ftpcon.download_parsed(path)['PUBLIC-DOCUMENT-COUNT'][0]) 
        except: 
            body['_enrich']['doc_count'] = None
    except: 
        body['_enrich']['period'] = None
    return body


def add_meta( body ): 
    body['download_try'] = True
    return body


# --
# run

if args.status: 
    for doc in scan(client, index = config['edgar_index']['index'], query = query): 
        client.index(
            index    = config['aq_forms_enrich']['index'], 
            doc_type = config['aq_forms_enrich']['_type'], 
            id       = doc["_id"],
            body     = enrich_status( doc['_source'] )
        )
        client.index(
            index    = config['edgar_index']['index'], 
            doc_type = config['edgar_index']['_type'], 
            id       = doc["_id"],
            body     = add_meta( doc['_source'] )
        )
        print(doc['_id'])
elif args.period: 
    for doc in scan(client, index = config['aq_forms_enrich']['index'], query = query): 
        client.index(
            index    = config['aq_forms_enrich']['index'], 
            doc_type = config['aq_forms_enrich']['_type'], 
            id       = doc["_id"],
            body     = enrich_deadline( doc['_source'] )
        )
        print(doc['_id'])