'''
    NY State SOF Registry Scrape: 
        I:   Use selenium driver to manually get past captcha 
        II:  Get all valid offender ID numbers through zip code
        III: Iterate over all offender links and get page info
'''

# -- 
# Dependancies

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display

import urllib2
from urllib2 import urlopen
import requests
import csv
import re
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pprint import pprint
import xmltodict
import pickle


# -- 
# Get zipcodes from file

allCodes = pd.read_csv('/Users/culhane/VAproject/data/zip_code_database.csv')
nyCodes = allCodes.loc[allCodes['state'] == 'NY']
nyCodes = nyCodes[['zip']].values.tolist() 
nyCodes = [str(i[0]) for i in nyCodes]


# -- 
# Driver and display 

display = Display(visible=0, size=(800, 600))
display.start()
url = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp'
driver = webdriver.Chrome('/Users/culhane/Desktop/chromedriver') 
time.sleep(1)

driver.get(url)


# -- 
# Manually enter captcha and obtain valid extension 
# I: January 22 attempt 1
# ext = '&recaptcha_challenge_field=03AA7ASh2VYLDK6ZrOZ9hH27SZvHxdd5hvCN18vtW_fd3lvRtPgVYUsh_PBprukX9A3Ghtiwl6SzZE41Dsuqm-fmePeyKpwFXOYU7hn9Q39Syza-PFwQy18gb4hqJp2shi7mmUwlkfL8CLICmz3oF3ygcR7ibFvQaw7hVQVCSwlzc4NYDXkIKTjDmzceNLswLKu8nQuDtoioupd5F5yxrOCJcOYz85_qpECw&recaptcha_response_field=ford+stay&Submit=EN'
ext = '&recaptcha_challenge_field=03AA7ASh1Ri6yY-MC9vqwaW2COM6F1aOYkNHw2YxwGw4Ch_TskUO6jyQuCYJNeItFu9LoiSEH38Hce-OCNKx7t1IBScNo8eo-td3YABAllr_bHRsI5l_VIDoBM_fSjcfUs3BO66CtA35StI-WovRP8bCslaSBctRFUsAKazkVdmq0nsvmCmj1xdTqxgu4xcuV5km_A-K_rlNf8n8d6-ltevvvZGhVj-EoQjQ&recaptcha_response_field=salim+asisa&Submit=EN'


# -- 
# Get page links 

def buildUrl(link): 
    url = 'http://www.criminaljustice.ny.gov' + link
    return url

def getLinks(_zip, ext): 
    base = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp?offenderSubmit=true&LastName=&County=&Zip='
    url = base + _zip + ext
    print(url)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html)
    emptyString = 'There are no offenders with the following'
    if emptyString in soup.find('table').get_text(): 
        links = False
    else: 
        content = soup.find('div', {'id' : 'mainContent'})
        tab = content.findAll('table')[1]
        rows = tab.findAll('tr')
        links = [] 
        for r in range(1, len(rows)):
            link = rows[r].find('a')['href']
            links.append([buildUrl(link), url])
        # - 
    return links


# -- 
# Get offneder links and write to file as checkpoint

allLinks = [] 
emptyZips = []
for i in range(0, len(nyCodes)): 
    _zip = nyCodes(i)
    print('evaluating ' + str(i) + ' of ' + len(nyCodes) + ' zips')
    if len(_zip) == 5: 
        links = getLinks(_zip, ext)
        if links == False: 
            emptyZips.append(_zip)
            print('no offenders for given zip')
        else: 
            allLinks.append(links)
    else: 
        continue

ls = []
for l in allLinks: 
    ls.extend(l)


links = [i[0] for i in ls]
links = list(set(links))
dfLink = pd.DataFrame(links)
dfLink.to_csv('/Users/culhane/VAProject/code/NY/offender-links.csv')


# -- 
# Loop through offender flyers and extract relevant data points

def evalPage(url): 
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html)
    top = soup.find('div', {'id' : 'mainContent'})
    data = top.findAll('li')
    keys = ['offId', 
            'lastName', 
            'firstName', 
            'middleName', 
            'dateOfBirth', 
            'sex', 
            'riskLevel', 
            'designation', 
            'race', 
            'ethnicity', 
            'height', 
            'weight', 
            'hair', 
            'eyes', 
            'contacts', 
            'photoDate', 
            'addType', 
            'county', 
            'address']
    pageData = [] 
    for i in range(0, 19): 
        info = data[i].findAll('span')[1].get_text()
        pageData.append(info)
        # - 
    d = dict(zip(keys, pageData))
    return d


# -- 
# Load offender flyer urls from checkpoint csv

df = pd.read_csv('/Users/culhane/VAProject/code/NY/offender-links.csv')
urls = df.values.tolist()
urls = [i[1] for i in urls]


# -- 
# Loop through offender urls and get offender data: 

urlSummary = [] 
offenderDat = [] 

for i in range(0, len(urls)): 
    print('evaluating ' + str(i) + ' of ' + str(len(urls)) + 'offenders')
    print(urls[i])
    print('found ' + str(len(offenderDat)) + ' offenders')
    try: 
        url = urls[i]
        try: 
            out = evalPage(url)
            offenderDat.append(out)
            urlSummary.append([url, 'valid'])
        except: 
            urlSummary.append([url, invalid])
    except KeyboardInterrupt: 
        raise


for i in range(2991, len(urls)): 
    print('evaluating ' + str(i) + ' of ' + str(len(urls)) + 'offenders')
    print(urls[i])
    print('found ' + str(len(offenderDat)) + ' offenders')
    try: 
        url = urls[i]
        try: 
            out = evalPage(url)
            offenderDat.append(out)
            urlSummary.append([url, 'valid'])
        except: 
            urlSummary.append([url, invalid])
    except KeyboardInterrupt: 
        raise


