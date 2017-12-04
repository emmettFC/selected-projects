import re
import time
import json
import xmltodict
import argparse

import urllib2
from urllib2 import urlopen

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, streaming_bulk

from copy import copy
from threading import Timer, activeCount
from pprint import pprint
from ftplib import FTP
from datetime import datetime
from datetime import date, timedelta
from sec_header_ftp_download import *

# --
# Global vars
T = time.time()

# --
# Helpers
def validate(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

# --
# CLI
parser = argparse.ArgumentParser(description='scrape-edgar-forms')
parser.add_argument("--back-fill",   action='store_true') 
parser.add_argument("--start-date",  type=str, action='store', required=True)
parser.add_argument("--end-date",    type=str, action='store', default=date.today().strftime('%Y-%m-%d'))  
parser.add_argument("--form-types",  type=str, action='store', required=True)
parser.add_argument("--section",     type=str, action='store', default='both')
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()

# -- 
# Config
config = json.load(open(args.config_path))

HOSTNAME = config['es']['host']
HOSTPORT = config['es']['port']

FORMS_INDEX = config['forms']['index']
INDEX_INDEX = config['edgar_index']['index']

# -- 
# IO
client = Elasticsearch([{'host' : HOSTNAME, 'port' : HOSTPORT}])

# --
# define query
params = {
    'back_fill'  : args.back_fill,
    'start_date' : datetime.strptime(args.start_date, '%Y-%m-%d'),
    'end_date'   : datetime.strptime(args.end_date, '%Y-%m-%d'),
    'form_types' : map(int, args.form_types.split(',')),
    'section'    : args.section
}


docs   = params['section'] in ['body', 'both']
header = params['section'] in ['header', 'both']
if (not docs) and (not header):
    raise Exception('section must be in [body, header, both]')

# Must be the right form type and between the dates
must = [
    {
        "terms" : { "form.cat" : params['form_types'] }
    },
    {
        "range" : {
            "date" : {
                "gte" : params['start_date'], 
                "lte" : params['end_date']
            }
        }
    }
]

# If not back filling, only load forms that haven't been tried
if not params['back_fill']:
    must.append({
        "filtered" : {
            "filter" : { 
                "or" : [
                    {"missing" : { "field" : "download_try2"    }},
                    {"missing" : { "field" : "download_try_hdr" }},
                ]
            }
        }
    })
# Otherwise, try forms that haven't been tried or have failed
else:
    must.append({
        "bool" : {
            "should" : [
                {"match" : {"download_success2"    : False } },
                {"match" : {"download_success_hdr" : False } }, 
                {
                    "filtered" : {
                        "filter" : { 
                            "or" : [
                                {"missing" : { "field" : "download_try2" }},
                                {"missing" : { "field" : "download_try_hdr" }}
                            ]
                            
                        }
                    }
                }
            ],
            "minimum_should_match" : 1
        }    
    })

query = {
    "_source" : False, 
    "query" : {
        "bool" : {
            "must" : must
        }
    }
}

pprint(query)

# --
# Function definitions

def get_headers(a, ftpcon, forms_index=FORMS_INDEX):
    path = ftpcon.url_to_path(a['_id'])
    
    out = {
        "_id"           : a['_id'],
        "_type"         : a['_type'],
        "_index"        : forms_index,
        "_op_type"      : 'update',
        "doc_as_upsert" : True
    }
    out_log = {
        "_id"      : a['_id'],
        "_type"    : a['_type'], 
        "_index"   : a['_index'], 
        "_op_type" : "update"
    }
    try:
        out['doc']     = {"header" : ftpcon.download_parsed(path)}
        out_log['doc'] = {"download_try_hdr" : True, "download_success_hdr" : True}
        
        return out, out_log  
    except (KeyboardInterrupt, SystemExit):
        raise      
    except:
        try: 
            x = a['_source']['try_count_hdr']
        except: 
            x = 0

        out_log['doc'] = {"download_try_hdr" : True, \
                          "download_success_hdr" : False, \
                          "try_count_hdr" : x + 1}            
        print 'failed @ %s' % path
        return None, out_log


def get_docs(a, ftpcon, forms_index=FORMS_INDEX):
    out = {
        "_id"           : a['_id'],
        "_type"         : a['_type'],
        "_index"        : forms_index,
        "_op_type"      : "update",
        "doc_as_upsert" : True
    }
    
    out_log = {
        "_id"      : a['_id'],
        "_type"    : a['_type'], 
        "_index"   : a['_index'], 
        "_op_type" : "update"
    }
    
    try:
        page         = ftpcon.download(a['_id'])
        split_string = 'ownershipDocument>'
        page         = '<' + split_string + page.split(split_string)[1] + split_string
        page         = re.sub('\n', '', page)
        page         = re.sub('>([0-9]{4}-[0-9]{2}-[0-9]{2})-[0-9]{2}:[0-9]{2}<', '>\\1<', page)
        page         = re.sub('([0-9]{2})(- -)([0-9]{2})', '\\1-\\3', page) 
        parsed_page  = xmltodict.parse(page)
        out['doc']   = parsed_page
        
        out_log['doc'] = {"download_try2" : True, "download_success2" : True}
        
        return out, out_log
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        try: 
            x = a['_source']['try_count_body']
        except: 
            x = 0
            
        out_log['doc'] = {"download_try2" : True, \
                          "download_success2" : False, \
                          "try_count_body" : x + 1}
        print(out_log)
        print 'failed @ ' + a['_id']
        return None, out_log


def process_chunk(chunk, docs, header):
    ftpcon = SECFTP(FTP('ftp.sec.gov', 'anonymous'))
    for a in chunk:
        if docs:
            out, out_log = get_docs(a, ftpcon)    
            if out:
                yield out
            
            yield out_log
        
        if header:
            out, out_log = get_headers(a, ftpcon)
            if out: 
                yield out
            
            yield out_log


def load_chunk(chunk, docs, header):
    for a,b in streaming_bulk(client, process_chunk(chunk, docs, header), chunk_size=250):
        pass
    

def run(query, docs, header, chunk_size=1000, max_threads=5, counter=0):
    chunk = []
    for a in scan(client, index=INDEX_INDEX, query=query):
        chunk.append(a)
        
        if len(chunk) >= chunk_size:
            while activeCount() > max_threads:
                time.sleep(1)
            
            Timer(0, load_chunk, args=(copy(chunk), docs, header)).start()
            counter += len(chunk)
            print 'indexed %d in %f' % (counter, time.time() - T)
            chunk = []
    
    Timer(0, load_chunk, args=(copy(chunk), docs, header)).start()
    print 'done : %d' % counter


if __name__ == "__main__":
    run(query, docs, header)
