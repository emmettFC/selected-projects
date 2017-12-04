import json
import urllib2
import argparse
from datetime import datetime, date, timedelta
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk


# -- 
# CLI

parser = argparse.ArgumentParser(description='Scrape EDGAR indices')
parser.add_argument('--from-scratch', dest='from_scratch', action="store_true")
parser.add_argument('--min-year', type=int, dest='min_year', action="store", default=2011)
parser.add_argument('--max-year', type=int, dest='max_year', action="store", default=int(date.today().year))
parser.add_argument('--most-recent', dest='most_recent', action="store_true")
parser.add_argument('--config-path', type=str, action='store', default='../config.json')
args = parser.parse_args()

config = json.load(open(args.config_path))
client = Elasticsearch([
    {"host" : config['es']['host'], 
    "port" : config['es']['port']}
], timeout=6000)

# -- 
# Functions

def get_max_date():
    global config 
    
    query = {
        "size" : 0,
        "aggs" : { "max" : { "max" : { "field" : "date" } } }
    }
    d = client.search(index = config['edgar_index']['index'], body = query)
    return int(d['aggregations']['max']['value'])

def download_index(yr, q, from_date = get_max_date()):
    global config
    parsing = False 
    
    index_url = 'ftp://ftp.sec.gov/edgar/full-index/%d/QTR%d/master.idx' % (yr, q)
    for line in urllib2.urlopen(index_url):
        if parsing:
            cik, name, form, date, url = line.strip().split('|')
            date_int = 1000 * int(datetime.strptime(date, '%Y-%m-%d').strftime("%s"))
            if date_int > from_date: 
                yield {
                    "_id"     : url,
                    "_type"   : config['edgar_index']['_type'],
                    "_index"  : config['edgar_index']['index'],
                    "_source" : {
                        "cik"  : cik,
                        "name" : (name.replace("\\", '')).decode('unicode_escape'),
                        "form" : form,
                        "date" : date,
                        "url"  : url
                    }
                }
            else: 
                pass

        elif line[0] == '-':
            parsing = True


# -- 
# Run

if args.most_recent:
    yr = date.today().year
    q  = ((date.today().month - 1) / 3) + 1
    for a, b in streaming_bulk(client, download_index(yr, q), chunk_size = 1000):
        print a, b

elif args.from_scratch:
    yrs  = range(args.min_year, args.max_year)
    qtrs = [1, 2, 3, 4]
    for yr in yrs:
        for qtr in qtrs:
            for a, b in streaming_bulk(client, download_index(yr, q, from_date = -1), chunk_size = 1000):
                print a, b

else:
    raise Exception('Specificy either `most_recent` or `from_scratch`')
