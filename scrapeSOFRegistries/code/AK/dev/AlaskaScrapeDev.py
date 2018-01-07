'''
    Alaska Scrape Draft: 
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
# Get all available zipcode values from search homepage

url   = urlopen('http://www.dps.alaska.gov/Sorweb/Search.aspx')
soup  = BeautifulSoup(url)
posts = soup.findAll("select", {'id' : 'ctl00_ctl00_Content_Content_SearchForm_ZipCodes'})
zips  = posts[0].findAll('option')
codes = [i.get_text() for i in zips]
codes = list(set(codes)) 

valid_codes = [i for i in codes if len(i) == 5]

# -- 
# Build set of urls

def evalZip(code): 
    # - params 
    base1 = "http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum="
    base2 = "&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes="
    suffix = "&city=All%20Cities&ExecuteQuery=Submit%20Query"
    pgNum = 1
    # - build first page url
    urlStr = base1 + str(pgNum) + base2 + code + suffix
    url   = urlopen(urlStr)
    soup  = BeautifulSoup(url)
    table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
    table = table[0].findAll('table')
    tableDat = table[0].findAll('tr')
    y = tableDat[2].get_text().encode('ascii', 'ignore') 
    y = removeWS(y.encode('ascii', 'ignore')) 
    # - identify no results instance
    urls = []
    if 'SORCR Found 0 registered sex offenders' in tableDat[1].get_text(): 
        print('no results found')
    # - identify single page instance
    elif 'Index:' not in y: 
        print('single page results')
        urls.append((urlStr, 'single'))
    # - identify multiple page instance
    elif 'Index:' in y: 
        print('multiple results on page')
        n_index = len(tableDat[2].findAll('a')) 
        pages = [] 
        for i in range(1,n_index+1): 
            url = base1 + str(i) + base2 + code + suffix
            pages.append((url, 'multiple'))
        urls.extend(pages) 
    return urls


urls = []
for i in valid_codes: 
    urls.extend(evalZip(i)) 


# -- 
# Save urls

df = pd.DataFrame(urls)
df.to_csv('/Users/culhane/VAproject/data/alaska_urls.csv')

# -- 
# Load urls

df = pd.read_csv('/Users/culhane/VAproject/data/alaska_urls.csv')
df.columns = ('index', 'url', 'class')
urls = df[['url', 'class']].values.tolist() 

# -- 
# Get and structure SOF data for each results page


# Revise the code below: 


# --
# Get SOFF data for each page 

url = urls[0] 
soup  = BeautifulSoup(urlopen(url[0]))
table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
table = table[0].findAll('table')
tableDat = table[0].findAll('tr')

if url[1] == 'single': 
    offenders = tableDat[2:len(tableDat)-1]
elif url[1] == 'multiple': 
    offenders = tableDat[3:len(tableDat)-1]


# -- 
# Trial data ingest for individual offender 

import xmltodict


def removeWS(s): 
    return s.replace('\r', '').replace('\n','')


def getTables(o): 
    link = o.findAll('td')[1].find('a')['href']
    offUrl = 'http://www.dps.alaska.gov' + link
    page = urlopen(offUrl)
    time.sleep(1)
    soup  = BeautifulSoup(page) 
    tables = soup.findAll("table")
    return tables

def getHeader(table): 
    aliases = table.findAll('table')[0]
    aliases = aliases.findAll('tr')
    header = [removeWS(i.get_text()) for i in aliases]    

def getImageUrl(table):
    image = table.findAll('table')[2].findAll('img')[0]['src']
    imageUrl = 'http://www.dps.alaska.gov' + image
    return imageUrl

# def getOffenseData(table): 
#     offs = table.findAll('tr')
#     offsTable = [] 
#     counter = 1
#     out = {}
#     conv = 'conviction1'
#     out['Convictions'] = {}
#     out['Convictions'][conv] = {}
#     for i in offs: 
#         if len(i.findAll('i')) == 1: 
#             section = removeWS(i.get_text().replace(' ', ''))
#             if len(re.findall('Conviction', section)) == 0: 
#                 out[section] = {}
#         elif len(i.findAll('i')) == 0: 
#             # if section.replace(' ', '') != 'Convictions': 
#             if len(re.findall('Conviction', section)) == 0: 
#                 # print(section)
#                 tds = i.findAll('td')
#                 # print(tds)
#                 # print(len(tds))
#                 for t in tds: 
#                     # print(t)
#                     try: 
#                         feild = removeWS(t.find('b').get_text())
#                         value = removeWS(t.get_text().replace(feild, ''))
#                         out[section][feild] = value
#                     except: 
#                         x = 1
#             elif len(re.findall('Conviction', section)) > 0: 
#             # elif out[section] == 'Convictions': 
#                 # print(section)
#                 tds = i.findAll('td')
#                 # print(len(tds))
#                 if len(i.findAll('b')) == 0: 
#                     counter +=1
#                     conv = 'conviction' + str(counter)
#                     out[section][conv] = {}
#                 elif len(i.findAll('b')) != 0: 
#                     for t in tds: 
#                         feild = removeWS(t.find('b').get_text())
#                         value = removeWS(t.get_text().replace(feild, ''))
#                         out[section][conv][feild] = value 
#     return out


def getOffenseData(table): 
    offs = table.findAll('tr')
    offsTable = [] 
    counter = 1
    out = {}
    conv = 'conviction1'
    out['Convictions'] = {}
    out['Convictions'][conv] = {}
    out['ConvictionsOutOfState'] = {}
    out['ConvictionsOutOfState'][conv] = {}
    for i in offs: 
        if len(i.findAll('i')) == 1: 
            section = removeWS(i.get_text().replace(' ', ''))
            if len(re.findall('Conviction', section)) == 0: 
                out[section] = {}
        elif len(i.findAll('i')) == 0: 
            # if section.replace(' ', '') != 'Convictions': 
            if len(re.findall('Conviction', section)) == 0: 
                # print(section)
                tds = i.findAll('td')
                # print(tds)
                # print(len(tds))
                for t in tds: 
                    # print(t)
                    try: 
                        feild = removeWS(t.find('b').get_text())
                        value = removeWS(t.get_text().replace(feild, ''))
                        out[section][feild] = value
                    except: 
                        x = 1
            elif len(re.findall('ConvictionOut', section)) > 0: 
            # elif out[section] == 'Convictions': 
                # print(section)
                tds = i.findAll('td')
                # print(len(tds))
                if len(i.findAll('b')) == 0: 
                    counter +=1
                    conv = 'conviction' + str(counter)
                    out[section][conv] = {}
                elif len(i.findAll('b')) != 0: 
                    for t in tds: 
                        feild = removeWS(t.find('b').get_text())
                        value = removeWS(t.get_text().replace(feild, ''))
                        out[section][conv][feild] = value 
            elif len(re.findall('Conviction', section)) > 0: 
            # elif out[section] == 'Convictions': 
                # print(section)
                tds = i.findAll('td')
                # print(len(tds))
                if len(i.findAll('b')) == 0: 
                    counter +=1
                    conv = 'conviction' + str(counter)
                    out[section][conv] = {}
                elif len(i.findAll('b')) != 0: 
                    for t in tds: 
                        feild = removeWS(t.find('b').get_text())
                        value = removeWS(t.get_text().replace(feild, ''))
                        out[section][conv][feild] = value 
    return out



def getPageOffenders(offenders): 
    offenderData = []
    for o in offenders: 
        name = removeWS(o.findAll('td')[1].get_text())
        _zip = removeWS(o.findAll('td')[2].get_text())
        compliant = removeWS(o.findAll('td')[3].get_text())
        try: 
            tables = getTables(o) 
        except: 
            time.sleep(5)
            tables = getTables(o)
        header = getHeader(tables[1])
        image = getImageUrl(tables[1])
        oData = getOffenseData(tables[6])
        out = {
            'name' : name, 
            'zip' : _zip, 
            'compliant' : compliant, 
            'header' : header, 
            'image' : image, 
            'data' : oData
        }
        offenderData.append(out)
    return offenderData





allData = [] 
brokeUrls = []
for u in urls: 
    try: 
        soup  = BeautifulSoup(urlopen(u[0]))
        table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
        table = table[0].findAll('table')
        tableDat = table[0].findAll('tr')
        if u[1] == 'single': 
            offenders = tableDat[2:len(tableDat)-1]
        elif u[1] == 'multiple': 
            offenders = tableDat[3:len(tableDat)-1]
        # - 
        pageData = getPageOffenders(offenders)
        allData.extend(pageData)
    except: 
        print(u)
        brokeUrls.append(u)



# -- 
# Debug not working proceedure

allData = []
brokeUrls = []
pageCounts = []
for i in range(0, len(urls)):
    time.sleep(2)
    print('evaluating url index ' + str(i) + ' for offenders')
    try: 
        url = urls[i] 
        soup  = BeautifulSoup(urlopen(url[0]))
        table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
        table = table[0].findAll('table')
        tableDat = table[0].findAll('tr')
        # - 
        if url[1] == 'single': 
            offenders = tableDat[2:len(tableDat)-1]
        elif url[1] == 'multiple': 
            offenders = tableDat[3:len(tableDat)-1]
        # - 
        offenderData = []
        url[2] = 'evaluated'
        url[3] = len(offenders)
        pageCounts.append(urls[i] + ['evaluated', len(offenders)])
        for o in offenders: 
            name = removeWS(o.findAll('td')[1].get_text())
            _zip = removeWS(o.findAll('td')[2].get_text())
            compliant = removeWS(o.findAll('td')[3].get_text())
            try: 
                tables = getTables(o) 
            except: 
                time.sleep(60)
                tables = getTables(o)
            header = getHeader(tables[1])
            image = getImageUrl(tables[1])
            oData = getOffenseData(tables[6])
            out = {
                'name' : name, 
                'zip' : _zip, 
                'compliant' : compliant, 
                'header' : header, 
                'image' : image, 
                'data' : oData
            }
            offenderData.append(out)
            # print(len(offenderData))
            # - 
        allData.extend(offenderData)
        print(len(allData))
    except: 
        print(url)
        brokeUrls.append(url)      




# -- 
# Now the fucking issue begins again

allData = []
brokeUrls = []
pageCounts = []

url = urls[0] 
soup  = BeautifulSoup(urlopen(url[0]))
table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
table = table[0].findAll('table')
tableDat = table[0].findAll('tr')
# - 
if url[1] == 'single': 
    offenders = tableDat[2:len(tableDat)-1]
elif url[1] == 'multiple': 
    offenders = tableDat[3:len(tableDat)-1]
# - 
offenderData = []
pageCounts.append(urls[i] + ['evaluated', len(offenders)])
# pageCounts.append((url[0], len(offenders)))
for o in offenders: 
    name = removeWS(o.findAll('td')[1].get_text())
    _zip = removeWS(o.findAll('td')[2].get_text())
    compliant = removeWS(o.findAll('td')[3].get_text())
    try: 
        tables = getTables(o) 
    except: 
        time.sleep(5)
        tables = getTables(o)
    header = getHeader(tables[1])
    image = getImageUrl(tables[1])
    oData = getOffenseData(tables[6])
    out = {
        'name' : name, 
        'zip' : _zip, 
        'compliant' : compliant, 
        'header' : header, 
        'image' : image, 
        'data' : oData
    }
    offenderData.append(out)
    # print(len(offenderData))
    # - 
allData.extend(offenderData)




['http://www.dps.alaska.gov/SORWeb/List.aspx?PgNum=1&Preview=FALSE&SEARCH_TYPE=search&firstname=&lastname=&addresstype=&streetname=&zipcodes=99586&city=All%20Cities&ExecuteQuery=Submit%20Query', 'single']






# allData = [] 
# brokeUrls = []
# workUrls = []
# for url in urls: 
#     print('worked: ' + str(len(allworkUrls)) + '||' + ' failed: ' + str(len(allworkUrls)))
#     try: 
#         soup  = BeautifulSoup(urlopen(url[0]))
#         table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
#         table = table[0].findAll('table')
#         tableDat = table[0].findAll('tr')
#         if url[1] == 'single': 
#             offenders = tableDat[2:len(tableDat)-1]
#         elif url[1] == 'multiple': 
#             offenders = tableDat[3:len(tableDat)-1]
#         # - 
#         pageData = getPageOffenders(offenders)
#         allData.extend(pageData)
#         # print(len(allData))
#         workUrls.append(url)
#         # print(len(workUrls))
#     except: 
#         # print(url)
#         brokeUrls.append(url)

allData = [] 
brokeUrls = []
workUrls = []
for url in urls: 
    print('worked: ' + str(len(allworkUrls)) + '||' + ' failed: ' + str(len(allworkUrls)))
    try: 
        soup  = BeautifulSoup(urlopen(url[0]))
        table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table1'})
        table = table[0].findAll('table')
        tableDat = table[0].findAll('tr')
        if url[1] == 'single': 
            offenders = tableDat[2:len(tableDat)-1]
        elif url[1] == 'multiple': 
            offenders = tableDat[3:len(tableDat)-1]
        # - 
        pageData = getPageOffenders(offenders)
        allData.extend(pageData)
        # print(len(allData))
        workUrls.append(url)
        # print(len(workUrls))
    except: 
        # print(url)
        brokeUrls.append(url)











def getOffenseData(table): 
    offs = table.findAll('tr')
    offsTable = [] 
    counter = 1
    out = {}
    conv = 'conviction1'
    out['Convictions'] = {}
    out['Convictions'][conv] = {}
    for i in offs: 
        if len(i.findAll('i')) == 1: 
            section = removeWS(i.get_text().replace(' ', ''))
            if len(re.findall('Conviction', section)) == 0: 
                out[section] = {}
        elif len(i.findAll('i')) == 0: 
            # if section.replace(' ', '') != 'Convictions': 
            if len(re.findall('Conviction', section)) == 0: 
                print(section)
                tds = i.findAll('td')
                # print(tds)
                # print(len(tds))
                for t in tds: 
                    print(t)
                    try: 
                        feild = removeWS(t.find('b').get_text())
                        value = removeWS(t.get_text().replace(feild, ''))
                        out[section][feild] = value
                    except: 
                        x = 1
            elif len(re.findall('Conviction', section)) > 0: 
            # elif out[section] == 'Convictions': 
                print(section)
                tds = i.findAll('td')
                print(len(tds))
                if len(i.findAll('b')) == 0: 
                    counter +=1
                    conv = 'conviction' + str(counter)
                    out[section][conv] = {}
                elif len(i.findAll('b')) != 0: 
                    for t in tds: 
                        feild = removeWS(t.find('b').get_text())
                        value = removeWS(t.get_text().replace(feild, ''))
                        out[section][conv][feild] = value 
    return out

# -- 
# Compliance Header

# table = soup.findAll("table", {'id' : 'ctl00_ctl00_Content_Content_Table4'})
# _data = table[0].find('span', {'class' : 'headcompliant'}).get_text()


# -- 
# Offense level data
# this list of tables generated by this should be the way to do all of the things, much easier can just use index like so: 

table = soup.findAll("table")



offs = table[6].findAll('tr')


# import urllib2
# import xmltodict

# # def homepage(request):

# _file = urllib2.urlopen(offUrl)
# data = _file.read()
# _file.close()

# data = data.encode('utf-8', 'ignore')
# def _removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

# data = _removeNonAscii(data)

# data = xmltodict.parse(data)
# return render_to_response('my_template.html', {'data': data})

# _try = xmltodict.parse(BeautifulSoup(urlopen(offUrl)))


offsTable = [] 
counter = 1
out = {}
conv = 'conviction1'
out[u'\n\nConvictions\n\n'] = {}
out[u'\n\nConvictions\n\n'][conv] = {}
for i in offs: 
    if len(i.findAll('i')) == 1: 
        section = i.get_text().replace(' ', '')
        if len(re.findall('Conviction', section)) == 0: 
            out[section] = {}
    elif len(i.findAll('i')) == 0: 
        # if section.replace(' ', '') != 'Convictions': 
        if len(re.findall('Conviction', section)) == 0: 
            print(section)
            tds = i.findAll('td')
            print(len(tds))
            for t in tds: 
                feild = t.find('b').get_text() 
                value = t.get_text().replace(feild, '')
                out[section][feild] = value
        elif len(re.findall('Conviction', section)) > 0: 
        # elif out[section] == 'Convictions': 
            print(section)
            tds = i.findAll('td')
            print(len(tds))
            if len(i.findAll('b')) == 0: 
                counter +=1
                conv = 'conviction' + str(counter)
                out[section][conv] = {}
            elif len(i.findAll('b')) != 0: 
                for t in tds: 
                    feild = t.find('b').get_text() 
                    value = t.get_text().replace(feild, '')
                    out[section][conv][feild] = value 







