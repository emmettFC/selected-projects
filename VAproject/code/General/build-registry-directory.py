'''
    Build index sets for scraping utilities: 
        I:    States
        II:   Territories
        III:  Tribes
'''


# -- 
# Dependancies

import urllib2
from urllib2 import urlopen
import requests
import csv
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from pprint import pprint


# -- 
# Scrape link index 
url = urlopen('https://www.nsopw.gov/en-US/Registry/allregistries/')
soup     = BeautifulSoup(url)
posts    = soup.findAll("div", {'class' : 'clfx'})


# -- 
# Get states
states = soup.find("section", {'class' : 'states'})
states = states.findAll('li')
stateLinks = []
for line in states: 
    out = {
        'region' : 'state',
        'name' : line.find('a').get_text(),
        'link' : line.find('a')['href']
    }
    stateLinks.append(out)


# -- 
# Get territories
territories = soup.find("section", {'class' : 'territories'})
territories = territories.findAll('li')
territoryLinks = []
for line in territories: 
    out = {
        'region' : 'territory',
        'name' : line.find('a').get_text(),
        'link' : line.find('a')['href']
    }
    territoryLinks.append(out)


# -- 
# Get Indian tribes (some tribes work with the associated state authority)
tribes = soup.find("section", {'class' : 'tribes'})
tribes = tribes.findAll('li')
tribeLinks = []
missingTribeLinks = []
for line in tribes: 
    try: 
        out = {
            'region' : 'tribe',
            'name' : line.find('a').get_text(),
            'link' : line.find('a')['href']
        }
        tribeLinks.append(out)
    except: 
        missingTribeLinks.append(line)

# -- 
# Format scraped indices and begin to build process

allRegistries = territoryLinks + stateLinks + tribeLinks
df = pd.DataFrame(allRegistries)
df.to_csv('/Users/culhane/VAproject/data/registry_index.csv')





