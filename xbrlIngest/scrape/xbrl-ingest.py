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

parser = argparse.ArgumentParser(description='ingest-xbrl-rss-docs')
parser.add_argument("--year",  type=str, action='store')
parser.add_argument("--month",  type=str, action='store')
parser.add_argument("--config-path", type=str, action='store', default='/home/ubuntu/ernest/config.json')
args = parser.parse_args()

# -- 
# define tags

tags = ['us-gaap_Assets',
'us-gaap_Liabilities',
'us-gaap_LiabilitiesCurrent',
'us-gaap_AssetsCurrent',
'us-gaap_OtherLiabilitiesCurrent',
'us-gaap_OtherAssetsCurrent',
'us-gaap_OtherAssets',
'us-gaap_OtherLiabilities',
'us-gaap_OtherLiabilitiesNoncurrent',
'us-gaap_OtherAssetsNoncurrent',
'us-gaap_LiabilitiesAndStockholdersEquity',
'us-gaap_StockholdersEquity',
'us-gaap_EarningsPerShareDiluted',
'us-gaap_CommonStockValue',
'us-gaap_CommonStockSharesOutstanding',
'us-gaap_PreferredStockValue',
'us-gaap_CommonStockSharesIssued',
'us-gaap_WeightedAverageNumberOfShareOutstandingBasicAndDiluted',
'us-gaap_NetIncome',
'us-gaap_NetIncomeLoss',
'us-gaap_OperatingIncomeLoss',
'us-gaap_OperatingIncome',
'us-gaap_ComprehensiveIncomeNetOfTax',
'us-gaap_Revenues',
'us-gaap_SalesRevenueNet',
'us-gaap_OtherSalesRevenueNet',
'us-gaap_AccountsPayableCurrent',
'us-gaap_AccountsReceivableCurrent'
'us-gaap_AccountsReceivableNetCurrent',
'us-gaap_AccountsPayableNetCurrent',
'us-gaap_CashAndCashEquivalentsAtCarryingValue',
'us-gaap_Cash',
'us-gaap_InterestExpense',
'us-gaap_OtherNonoperatingIncomeExpense',
'us-gaap_OperatingExpenses',
'us-gaap_OperatingExpense',
'us-gaap_OtherNonoperatingExpense',
'us-gaap_InterestAndDebtExpense',
'us-gaap_InterestIncomeExpenseNet',
'us-gaap_CostsAndExpenses',
'us-gaap_ResearchAndDevelopmentExpense',
'us-gaap_GeneralAndAdministrativeExpense',
'us-gaap_DepreciationExpense',
'us-gaap_LegalFees'
'us-gaap_LongTermDebt',
'us-gaap_ShortTermDebt',
'us-gaap_LongTermDebtNoncurrent',
'us-gaap_DebtCurrent',
'us-gaap_LongTermDebtCurrent',
'us-gaap_ShortTermDebtCurrent',
'us-gaap_InventoryNet',
'us-gaap_PropertyPlantAndEquipmentNet',
'us-gaap_DepreciationAndAmortization',
'us-gaap_DepreciationDepletionAndAmortization',
'us-gaap_PropertyPlantAndEquipmentGross',
'us-gaap_Depreciation',
'us-gaap_Amortization',
'us-gaap_AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment',
'us-gaap_RetainedEarningsAccumulatedDeficit',
'us-gaap_RetainedEarnings',
'us-gaap_Goodwill',
'us-gaap_Profit',
'us-gaap_ProfitLoss',
'us-gaap_GrossProfit']

dei_tags = ["dei_AmendmentDescription",
"dei_AmendmentFlag",
"dei_ApproximateDateOfCommencementOfProposedSaleToThePublic",
"dei_CurrentFiscalYearEndDate",
"dei_DocumentEffectiveDate",
"dei_DocumentFiscalPeriodFocus",
"dei_DocumentFiscalYearFocus",
"dei_DocumentPeriodEndDate",
"dei_DocumentPeriodStartDate",
"dei_DocumentType",
"dei_EntityAddressAddressLine1",
"dei_EntityAddressCityOrTown",
"dei_EntityAddressPostalZipCode",
"dei_EntityAddressStateOrProvince",
"dei_EntityCentralIndexKey",
"dei_EntityCommonStockSharesOutstanding",
"dei_EntityCurrentReportingStatus",
"dei_EntityFilerCategory",
"dei_EntityIncorporationDateOfIncorporation",
"dei_EntityIncorporationStateCountryName",
"dei_EntityInformationDateToChangeFormerLegalOrRegisteredName",
"dei_EntityInformationFormerLegalOrRegisteredName",
"dei_EntityLegalForm",
"dei_EntityListingDepositoryReceiptRatio",
"dei_EntityListingDescription",
"dei_EntityListingParValuePerShare",
"dei_EntityNumberOfEmployees",
"dei_EntityPublicFloat",
"dei_EntityRegistrantName",
"dei_EntityTaxIdentificationNumber",
"dei_EntityVoluntaryFilers",
"dei_EntityWellKnownSeasonedIssuer",
"dei_FormerFiscalYearEndDate",
"dei_ParentEntityLegalName",
"dei_TradingSymbol"]

# -- 
# config 

config = json.load(open(args.config_path))

# config = json.load(open('/home/ubuntu/ernest/config.json'))

# -- 
# es connection

client = Elasticsearch([{"host" : config['es']['host'], "port" : config['es']['port']}])

# --
# functions

# def clean( year, month ):
#     pth1 = '/home/ubuntu/sec/filings'
#     shutil.rmtree(pth1) 
#     pth2 = '/home/ubuntu/sec/parsed_min__' + year + '__' + month
#     shutil.rmtree(pth2)


def dei_tree( dei_frame ): 
    k = dei_frame
    k.sort()
    c = list(k for k,_ in itertools.groupby(k))
    dei_tree = {} 
    for i in c: 
        dei_tree[i[2]] = {
            'fact'      : i[4], 
            'from_date' : find_date( i[9] ),
            'to_date'   : find_date( i[10] )
            }
    return dei_tree


def fact_tree( tag_frame ): 
    z    = tag_frame
    tree = {} 
    for i in z: 
        tree[i[2]] = {
            i[1] : { 
                'fact'     : i[4],
                'unit'     : i[3],
                'decimals' : i[5],
                'scale'    : i[6],
                'sign'     : i[7],
                'factId'   : i[8],
                'from_date': i[9],
                'to_date'  : i[10]
            }
        }
    return tree


def fact_list( tag_frame, entry ): 
    z    = tag_frame
    tree = {} 
    for i in z: 
        if len(i[4]) > 20: 
            pass
        else: 
            if i[10] != entry['entity_info']['dei_DocumentType']['to_date']: 
                pass
            else: 
                try: 
                    x = tree[i[2]]
                except: 
                    tree[i[2]] = {
                        "value"   : i[4],
                        "context" : i[1],
                        "from"    : find_date( i[9] ),
                        "to"      : find_date( i[10] )
                    }
                x = tree[i[2]]
                if toDate(x["from"]) < toDate(i[9]): 
                    pass
                elif toDate(x["from"]) == toDate(i[9]) and len(x['context']) < len(i[1]): 
                    pass
                elif toDate(x["from"]) > toDate(i[9]) or (toDate(x["from"]) == toDate(i[9]) and len(x['context']) > len(i[1])):
                    tree[i[2]] = {
                        "value"   : i[4],
                        "context" : i[1],
                        "from"    : find_date( i[9] ),
                        "to"      : find_date( i[10] )
                    }
                else: 
                    pass
    return tree



def find_date( date ): 
    try: 
        if date == "NA": 
            l = "NA"
        else: 
            o = re.compile("\d{4}-\d{2}-\d{2}")
            l = re.findall(o, date)[0]
    except: 
        l = "NA"
    return l 


def toDate ( date ): 
    if date == "NA": 
        date = datetime.strptime("1900-01-01", "%Y-%m-%d")
    else: 
        date = datetime.strptime(find_date( date ), "%Y-%m-%d")
    return date


def build_object( frame ): 
    out = []
    for c in range(0, len(frame)): 
        x = frame[c]
        if 'TextBlock' in x[2] or 'Axis' in x[1]: 
            pass
        else: 
            try: 
                if int(x[0]): 
                    if len(re.findall('-', x[10])) == 2: 
                        out.append(x)
                    else: 
                        pass
                else: 
                    pass
            except ValueError: 
                pass
                # ---
    return out


def ingest(year, month): 
    path      = '/home/ubuntu/sec/parsed_min__' + year + '__' + month
    for x in os.listdir(path):
        try: 
            doc    = path + '/' + x
            print(doc)
            f      = open(doc, 'rU') 
            reader = csv.reader(f)
            rows   = list(reader)
            entry  = {
                "link"          : x,
                "year"          : year,
                "month"         : str(month).zfill(2),
                "entity_info"   : {}, 
                "facts"         : {}
            }
            # --- define list inputs
            indices   = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 13]
            frame     = []
            for i in range(1, len(rows)): 
                try: 
                    row = [rows[i][k] for k in indices]
                    frame.append(row)
                except: 
                    pass
                    # ---
            dei_frame = build_object([frame[i] for i in range(0, len(frame)) if frame[i][2] in dei_tags])
            tag_frame = build_object([frame[i] for i in range(0, len(frame)) if frame[i][2] in tags]) 
            # --- structure doc entity information
            entry['entity_info'] = dei_tree(dei_frame)
            # --- eliminate non 10-K / 10-Q docs
            try: 
                p = entry['entity_info']['dei_DocumentType']
                if entry['entity_info']['dei_DocumentType']['fact'] in ('10-K', '10-Q'):
                    entry['facts'] = fact_list(tag_frame, entry)
                    try: 
                        client.index(index = 'ernest_xbrl_rss', \
                                     doc_type = 'filing', body = entry, id = x)
                    except: 
                        print(' -- parsing exception -- ')
                else: 
                    print(entry['entity_info']['dei_DocumentType'])
            except KeyError: 
                print('document missing form type value')
        except csv.Error, e: 
            print(e)
        os.remove(path + '/' + x)


# -- 
# run 
year  = str(args.year)
month = str(args.month)

ingest(year, month)
# clean(year, month)
