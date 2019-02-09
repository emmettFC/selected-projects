import feedparser
import os.path
import sys, getopt, time, socket, os, csv, re, json
import requests
import xml.etree.ElementTree as ET
import zipfile, zlib
import argparse
import subprocess
import itertools
import shutil
import calendar

import urllib2 
from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import HTTPError

from os import listdir
from os.path import isfile, join
from collections import Counter
from bs4 import BeautifulSoup

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan

import datetime
from datetime import datetime
from datetime import date, timedelta

# --
# CLI

parser = argparse.ArgumentParser(description='download-xbrl-rss-docs')
parser.add_argument("--year",  type=str, action='store')
parser.add_argument("--month",  type=str, action='store')
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()


# -- 
# config 

config = json.load(open(args.config_path))

# config = json.load(open('/home/ubuntu/ernest/config.json'))

# -- 
# es connection

client = Elasticsearch([{"host" : config['es']['host'], "port" : config['es']['port']}])


# -- 
# functions

def downloadfile( sourceurl, targetfname ):
    mem_file = ""
    good_read = False
    xbrlfile = None
    if os.path.isfile( targetfname ):
        print( "Local copy already exists" )
        return True
    else:
        print( "Downloading:", sourceurl )
        try:
            xbrlfile = urlopen( sourceurl )
            try:
                mem_file = xbrlfile.read()
                good_read = True
            finally:
                xbrlfile.close()
        except HTTPError as e:
            print( "HTTP Error:", e.code )
        except URLError as e:
            print( "URL Error:", e.reason )
        except socket.timeout:
            print( "Socket Timeout Error" )
        except: 
            print('TimeoutError')
        if good_read:
            output = open( targetfname, 'wb' )
            output.write( mem_file )
            output.close()
        return good_read


def SECdownload( year, month ):
    root = None
    feedFile = None
    feedData = None
    good_read = False
    itemIndex = 0
    edgarFilingsFeed = 'http://www.sec.gov/Archives/edgar/monthly/xbrlrss-' + str(year) + '-' + str(month).zfill(2) + '.xml'
    print( edgarFilingsFeed )
    if not os.path.exists("/home/ubuntu/sec/filings__" + str(year) + "__" + str(month)):
        os.makedirs( "/home/ubuntu/sec/filings__" + str(year) + "__" + str(month))
    target_dir = "/home/ubuntu/sec/filings__" + str(year) + "__" + str(month) + "/"
    try:
        feedFile = urlopen( edgarFilingsFeed )
        try:
            feedData = feedFile.read()
            good_read = True
        finally:
            feedFile.close()
    except HTTPError as e:
        print( "HTTP Error:", e.code )
    except URLError as e:
        print( "URL Error:", e.reason )
    # except TimeoutError as e:
    #     print( "Timeout Error:", e.reason )
    except socket.timeout:
        print( "Socket Timeout Error" )
    except: 
        print('TimeoutError')
    if not good_read:
        print( "Unable to download RSS feed document for the month:", year, month )
        return
    # we have to unfortunately use both feedparser (for normal cases) and ET for old-style RSS feeds,
    # because feedparser cannot handle the case where multiple xbrlFiles are referenced without enclosure
    try:
        root = ET.fromstring(feedData)
    except ET.ParseError as perr:
        print( "XML Parser Error:", perr )
    feed = feedparser.parse( feedData )
    try:
        print( feed[ "channel" ][ "title" ] )
    except KeyError as e:
        print( "Key Error:", e )
    # Process RSS feed and walk through all items contained
    for item in feed.entries:
        print( item[ "summary" ], item[ "title" ], item[ "published" ] )
        try:
            # Identify ZIP file enclosure, if available
            enclosures = [ l for l in item[ "links" ] if l[ "rel" ] == "enclosure" ]
            if ( len( enclosures ) > 0 ):
                # ZIP file enclosure exists, so we can just download the ZIP file
                enclosure = enclosures[0]
                sourceurl = enclosure[ "href" ]
                cik = item[ "edgar_ciknumber" ]
                targetfname = target_dir+cik+'-'+sourceurl.split('/')[-1]
                retry_counter = 3
                while retry_counter > 0:
                    good_read = downloadfile( sourceurl, targetfname ) ## first f(x) call
                    if good_read:
                        break
                    else:
                        print( "Retrying:", retry_counter )
                        retry_counter -= 1
            else:
                # We need to manually download all XBRL files here and ZIP them ourselves...
                linkname = item[ "link" ].split('/')[-1]
                linkbase = os.path.splitext(linkname)[0]
                cik = item[ "edgar_ciknumber" ]
                zipfname = target_dir+cik+'-'+linkbase+"-xbrl.zip"
                if os.path.isfile( zipfname ):
                    print( "Local copy already exists" )
                else:
                    edgarNamespace = {'edgar': 'http://www.sec.gov/Archives/edgar'}
                    currentItem = list(root.iter( "item" ))[itemIndex]
                    xbrlFiling = currentItem.find( "edgar:xbrlFiling", edgarNamespace )
                    xbrlFilesItem = xbrlFiling.find( "edgar:xbrlFiles", edgarNamespace )
                    xbrlFiles = xbrlFilesItem.findall( "edgar:xbrlFile", edgarNamespace )
                    if not os.path.exists(  target_dir+"temp" ):
                        os.makedirs( target_dir+"temp" )
                    zf = zipfile.ZipFile( zipfname, "w" )
                    try:
                        for xf in xbrlFiles:
                            xfurl = xf.get( "{http://www.sec.gov/Archives/edgar}url" )
                            if xfurl.endswith( (".xml",".xsd") ):
                                targetfname = target_dir+"temp/"+xfurl.split('/')[-1]
                                retry_counter = 3
                                while retry_counter > 0:
                                    good_read = downloadfile( xfurl, targetfname ) ## second f(x) call
                                    if good_read:
                                        break
                                    else:
                                        print( "Retrying:", retry_counter )
                                        retry_counter -= 1
                                zf.write( targetfname, xfurl.split('/')[-1], zipfile.ZIP_DEFLATED )
                                os.remove( targetfname )
                    finally:
                        zf.close()
                        os.rmdir( target_dir+"temp" )
        except KeyError, KeyboardInterrupt:
            print( 'Error' )
        finally:
            print( "----------" )
        itemIndex += 1


year = str(args.year)
month = str(args.month).zfill(2)
SECdownload(args.year, args.month)

