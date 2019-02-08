import os
import re
import sys
import time
import json
import pickle
import urllib2
import argparse
import itertools
from urllib2 import urlopen
from bs4 import BeautifulSoup

from datetime import datetime
from dateutil.parser import parse as dateparse

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

# --
# CLI

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
parser.add_argument("--private-config-path", type=str, action='store', default='../private-config.json')
parser.add_argument("--lookup-path", type=str, action='store', default='../board_ticker_lookup.pickle')
args = parser.parse_args()

config  = json.load(open(args.config_path))
pconfig = json.load(open(args.private_config_path))
lookup = pickle.load(open(args.lookup_path)) if os.path.exists(args.lookup_path) else {}

client = Elasticsearch([{
    "host" : config['elasticsearch']['hostname'],
    "port" : config['elasticsearch']['hostport']
}], timeout=60)

# --
# Functions

def parse_post(post):
    try:
        raw_date = post.find('div', {'class' : 'pshead'}).text.split('at')[-1].strip()
        date     = dateparse(raw_date).strftime('%Y-%m-%d %H:%M:%S')  
        board_id = post.find('div', {'class' : 'pshead'}).findAll('a')[1]['href'].split('=')[-1]
         
        source = {
            "time"     : date,

            "msg_id"   : re.sub('ps', '', post['id']),
            "msg"      : post.find('a', {'class' : 'pslink'}).text,
            
            "board"    : post.find('div', {'class' : 'pshead'}).findAll('a')[1].text,
            "board_id" : board_id,
            
            "user"     : post.find('div', {'class' : 'pshead'}).find('a').text,
            "user_id"  : post.find('div', {'class' : 'pshead'}).find('a')['href'].split('=')[-1],
            
            "tbc"      : 'Read Entire Message' in str(post),
            "source"   : 'ihub_psm',
            "ticker"   : get_ticker(board_id),
            
            "schema_version" : 3
        }
        
        return {
            "_index"  : config['elasticsearch']['_to_index'],
            "_type"   : config['elasticsearch']['_type'],
            "_id"     : 'ihub_psm_%s' % str(source['msg_id']),
            "_source" : source
        }
    except:
        return None

def get_ticker(board_id): 
    global lookup
    if not lookup.has_key(board_id):
        base   = 'http://investorshub.advfn.com/boards/board.aspx?board_id='
        soup   = BeautifulSoup(urlopen(base + str(board_id)))
        tag    = soup.find('h1').get_text()
        ticker = re.sub('\W', '', str(re.findall('\([A-Z]{1,6}\)', tag)))
        ticker = re.sub('u', '', ticker)
        print 'got ticker :: %s' % ticker
        lookup[board_id] = ticker
        pickle.dump(lookup, open(lookup_path))
    
    return lookup[board_id]

def load(posts, failover_file='.failover.pkl'):
    if os.path.exists(failover_file):
        posts += pickle.load(open(failover_file))

    try:        
        for a,b in streaming_bulk(client, itertools.chain(posts), chunk_size=100):
            print a, b
     
        if os.path.exists(failover_file):
            os.remove(failover_file)
    except:
         print("Error:", sys.exc_info()[0])
         print >> sys.stderr, 'writing to failover'
         pickle.dump(posts, open(failover_file, 'w'))

def start_session():
    display = Display(visible=0, size=(800, 600))
    display.start()
    
    driver = webdriver.Firefox()
    driver.get('http://investorshub.advfn.com/boards/login.aspx?redirect2=boards%2fpoststream.aspx')
    time.sleep(2)
    
    driver.find_element_by_id('ctl00_CP1_LoginView1_Login1_UserName').send_keys(pconfig['username'])
    driver.find_element_by_id('ctl00_CP1_LoginView1_Login1_Password').send_keys(pconfig['password'])
    driver.find_element_by_id('ctl00_CP1_LoginView1_Login1_LoginButton').click()
    time.sleep(3)
    return driver

def watch_session(driver):
    dirty = False
    
    g = []
    html_orig = None
    while True:
        print 'scraping @ %s' % datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        last_html = html_orig
        ths_html  = html_orig = driver.page_source
        if ths_html != last_html:
            posts = BeautifulSoup(ths_html).findAll("div", {'class' : 'pcont'})
            posts = filter(None, [parse_post(post) for post in posts])
            load(posts)
        
        time.sleep(config['sleep_interval'])

if __name__ == "__main__":
    driver = start_session()
    watch_session(driver)
