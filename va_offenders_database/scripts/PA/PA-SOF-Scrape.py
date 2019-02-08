'''
    PA Scrape Draft: 
        I: Uses selenium to get past acceptance criteria on homepage
        II: Handles single page results and multiple page results
        III: 
'''

# -- 
# Dependancies

import urllib2
import requests
import csv
import re
import time
import pandas as pd

from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display


# -- 
# Define functions 

def buildUrl(code): 
    base = 'https://www.pameganslaw.state.pa.us/Search/ZipSearchResults?enteredzip='
    ext = '&chkZipIncarcerated=true'
    url = base + code + ext
    return url

def getLinks(check): 
    base = 'https://www.pameganslaw.state.pa.us'
    val = "/Search/ZipSearchResults?page="
    links = [] 
    for i in range(len(check)): 
        try: 
            link = check[i]['href']
            if val in link:
                try: 
                    num = int(check[i].get_text()) 
                    links.append(base + link)
                except: 
                    x = 0
        except: 
            x = 0 
    return links

def evalRow(row, code, url, _class): 
    name = row.find('p', {'class' : 'searchResultName'}).get_text()
    img = row.find('img', {'class' : 'searchResultImg'})['src']
    info1 = row.findAll('span') 
    level = info1[1].get_text()
    bYear = info1[3].get_text()
    addrs = row.findAll('div', {'class' : 'searchResultAddress'})
    addrs = [i.get_text().replace(' ', '') for i in addrs]
    data = {
        'name' : name, 
        'img' : img, 
        'zip' : code, 
        'level' : level, 
        'bYear' : bYear, 
        'addrs' : addrs, 
        'url' : url, 
        'class' : _class
        }
    return data

def getZipOffenders(url): 
    try: 
        driver.find_element_by_name("button")
        driver.find_element_by_name("button").click()
    except: 
        print('driver still valid')
        # - 
    u = url[0]
    code = url[1]
    driver.get(u)
    html = driver.page_source
    soup = BeautifulSoup(html)
    _class = sortUrl(soup)
    out = []
    if _class == 'single': 
        out.extend(getResults(soup, code, u, _class))
    elif _class == 'multiple': 
        out.extend(getResults(soup, code, u, _class))
        check = soup.find('ul' , {'class' : 'pagination'}).findAll('a')
        links = getLinks(check)
        for link in links: 
            driver.get(link)
            html = driver.page_source
            soup = BeautifulSoup(html)
            out.extend(getResults(soup, code, link, _class))
    return out

def getResults(soup, code, url, _class): 
    results = soup.findAll('div', {'class' : 'searchResultRow'})
    pageData = [] 
    for row in results: 
        pageData.append(evalRow(row, code, url, _class))
    return pageData

def sortUrl(soup): 
    noResults = soup.find('p' , {'class' : 'noSearchResults'})
    if noResults != None: 
        _class = 'noResults'
    elif len(soup.find('ul' , {'class' : 'pagination'}).findAll('a')) ==2: 
        _class = 'single'
    elif len(soup.find('ul' , {'class' : 'pagination'}).findAll('a')) > 2: 
        _class = 'multiple'
    return _class


# -- 
# Get zipcodes from file

allCodes = pd.read_csv('/Users/culhane/VAproject/data/zip_code_database.csv')
paCodes = allCodes.loc[allCodes['state'] == 'PA']
paCodes = paCodes[['zip']].values.tolist() 
paCodes = [str(i[0]) for i in paCodes]


# -- 
# Instantiate display

display = Display(visible=0, size=(800, 600))
display.start()


# --
# Instantiate driver

driver = webdriver.Chrome('/Users/culhane/Desktop/chromedriver') 
time.sleep(1)


# -- 
# Get homepage url and submit accept button

driver.get('http://www.pameganslaw.state.pa.us/SearchZip.aspx')
driver.find_element_by_name("button").click() 

# -- 
# Get zip codes from file

allCodes = pd.read_csv('/Users/culhane/VAproject/data/zip_code_database.csv')
paCodes = allCodes.loc[allCodes['state'] == 'PA']
paCodes = paCodes[['zip']].values.tolist() 
paCodes = [str(i[0]) for i in paCodes]

urls = []
for code in paCodes: 
    url = buildUrl(code)
    urls.append((url, code))


# -- 
# Run

allData = []
for i in range(308, 500): 
    url = urls[i]
    try: 
        allData.extend(getZipOffenders(url))
        print('evaluating index ' + str(i) + ' of ' + str(len(urls))) 
        print('found data for ' + str(len(allData)) + ' offenders') 
    except: 
        time.sleep(3)
        allData.extend(getZipOffenders(url))
        print('evaluating index ' + str(i) + ' of ' + str(len(urls))) 
        print('found data for ' + str(len(allData)) + ' offenders') 


# -- 
# Write out raw data

with open('/Users/culhane/VAproject/PA-Data-Raw.pickle', 'wb') as _file:
    pickle.dump(allData, _file, protocol=pickle.HIGHEST_PROTOCOL)








