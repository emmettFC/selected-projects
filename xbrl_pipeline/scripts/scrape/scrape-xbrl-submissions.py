import json
import argparse
import urllib2
import zipfile

from pprint import pprint
from datetime import date, timedelta
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, streaming_bulk

# --
# cli

parser = argparse.ArgumentParser(description='ingest_new_forms')
parser.add_argument("--from-scratch", action = 'store_true') 
parser.add_argument("--most-recent", action = 'store_true') 
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()

# -- 
# config
config_path = args.config_path
config      = json.load(open(config_path))


# -- 
# es connections
client = Elasticsearch([{'host' : config['es']['host'], \
                         'port' : config['es']['port']}])


# -- 
# function

def __ingest(period):
    try: 
        response = urllib2.urlopen('https://www.sec.gov/data/financial-statements/' + period + '.zip')
    except urllib2.HTTPError: 
        print('--quarterly document has not yet been released--')
        raise
    aqfs     = response.read()
    
    with open('/home/ubuntu/data/xbrl_aqfs/' + period + '.zip', 'w') as inf:
        inf.write(aqfs)
        inf.close()
        
    with zipfile.ZipFile('/home/ubuntu/data/xbrl_aqfs/' + period + '.zip', 'r') as z:
        z.extractall('/home/ubuntu/data/xbrl_aqfs/' + period + '/')
        
    f = open('/home/ubuntu/data/xbrl_aqfs/' + period + '/sub.txt', 'r')
    x = f.readlines()
    
    lst = [] 
    for line in x: 
        row     = line.split('\t')
        row[35] = row[35].replace('\n', '')
        lst.append(row)
        
    for i in range(1, len(lst)): 
        x = lst[0]
        y = lst[i]
        dictionary = dict(zip(x, y))
        dictionary['file_period'] = period
        
        client.index(index = "xbrl_submissions", doc_type = 'filing', \
            body = dictionary, id = dictionary['adsh'])


# -- 
# run 

periods = [] 

if args.from_scratch: 
    for yr in range(2009, int(date.today().year) + 1): 
        if yr < date.today().year: 
            for qtr in range(1, 5): 
                periods.append(str(yr) + 'q' + str(qtr))
                #
        elif yr == date.today().year: 
            for qtr in range(1, (int(date.today().month) / 3) + 1): 
                periods.append(str(yr) + 'q' + str(qtr))
        
elif args.most_recent: 
    yr  = str(int(date.today().year)) 
    qtr = str(int(date.today().month) / 3) 
    periods.append(yr + 'q' + qtr)


for period in periods: 
    print('___ ingesting ___' + period)
    __ingest(period)

