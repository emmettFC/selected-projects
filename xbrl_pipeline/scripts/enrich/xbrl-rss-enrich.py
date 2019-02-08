from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk, scan
from elasticsearch.helpers import reindex

import json
import argparse
import calendar

# --
# CLI

parser = argparse.ArgumentParser(description='enrich-xbrl-rss-docs')
parser.add_argument("--year",  type=str, action='store')
parser.add_argument("--month",  type=str, action='store')
parser.add_argument("--config-path", type=str, action='store', default='../config.json')
args = parser.parse_args()

# -- 
# config 

config = json.load(open(args.config_path))

# -- 
# es connection

client = Elasticsearch([{"host" : config['es']['host'], "port" : config['es']['port']}])


# -- 
# global vars 


if not args.month:
    from_date = str(args.year) + '-01-01'
    to_date   = str(args.year) + '-12-31'
elif args.month: 
    days      = calendar.monthrange(int(args.year), int(args.month))
    from_date = str(args.year) + '-' + str(args.month).zfill(2) + '-01'
    to_date   = str(args.year) + '-' + str(args.month).zfill(2) + '-' + str(days[1]).zfill(2)

query = { 
  "query" : { 
    "range" : { 
      "date" : { 
        "gte" : from_date,
        "lte" : to_date
      }
    }
  }
}

print(query)


INDEX     = config['aq_forms_enrich']['index']
REF_INDEX = config['xbrl_rss']['index']
TYPE      = config['aq_forms_enrich']['_type']


print(INDEX)

def run(query): 
    for a in scan(client, index = INDEX, query = query): 
        res = client.search(index = REF_INDEX, body = {
            "query" : {
                "bool"  : { 
                    "must" : [
                    {
                        "match" : { 
                            "entity_info.dei_EntityCentralIndexKey.fact" : a["_source"]["cik"].zfill(10)
                        }
                    },
                    {
                        "match" : { 
                            "entity_info.dei_DocumentType.to_date" : a["_source"]["_enrich"]["period"]
                                }
                            }
                        ] 
                    }
                }
            })
        if res['hits']['total'] > 0:
            body = res['hits']['hits'][0]['_source']['facts']
            doc  = {
                    "__meta__" : { 
                        "financials" : get_financials( body )
                }
            }
        else: 
            doc = {
                "__meta__" : { 
                    "financials" : None
                }
            }
        yield {
            "_id"      : a['_id'],
            "_type"    : TYPE,
            "_index"   : INDEX,
            "_op_type" : "update",
            "doc"      : doc
        }



def to_numeric(val): 
    if val != None: 
        if val['value'] == 'NA': 
            val['value'] = 0 
        val['value'] = float(val['value'])

    return fix_dates(val)


def fix_dates(val): 
    if val != None: 
        if val['to'] == 'NA': 
            val['to'] = None
        if val['from'] == 'NA':
            val['from'] = None
    return val


def get_financials( body ):
    out = { 
        'assets'                           : to_numeric(body.get("us-gaap_Assets", None)),
        'liabilities'                      : to_numeric(body.get("us-gaap_Liabilities", None)),
        'stockholdersEquity'               : to_numeric(body.get("us-gaap_StockholdersEquity", None)),
        'netIncome'                        : to_numeric(body.get("us-gaap_NetIncomeLoss", None)),
        'liabilitiesAndStockholdersEquity' : to_numeric(body.get("us-gaap_LiabilitiesAndStockholdersEquity", None)),
        'liabilitiesCurrent'               : to_numeric(body.get("us-gaap_LiabilitiesCurrent", None)),
        'assetsCurrent'                    : to_numeric(body.get("us-gaap_AssetsCurrent", None)),
        'revenues'                         : to_numeric(body.get("us-gaap_Revenues", None)), 
        'commonStockValue'                 : to_numeric(body.get("us-gaap_CommonStockValue", None)), 
        'commonStockSharesOutstanding'     : to_numeric(body.get("us-gaap_CommonStockSharesOutstanding", None)),
        'commonStockSharesIssued'          : to_numeric(body.get("us-gaap_CommonStockSharesIssued", None)),
        'operatingIncome'                  : to_numeric(body.get("us-gaap_OperatingIncomeLoss", None)),
        'accountsPayable'                  : to_numeric(body.get("us-gaap_AccountsPayableCurrent", None)),
        'cash'                             : to_numeric(body.get("us-gaap_CashAndCashEquivalentsAtCarryingValue", body.get('us-gaap_Cash', None))),
        'interestExpense'                  : to_numeric(body.get("us-gaap_InterestExpense", None)),
        'operatingExpense'                 : to_numeric(body.get("us-gaap_OperatingExpenses", None)),
        'earnings'                         : to_numeric(body.get("us-gaap_RetainedEarningsAccumulatedDeficit", None)),
        'profit'                           : to_numeric(body.get("us-gaap_ProfitLoss", body.get('us-gaap_GrossProfit', None)))
        # 'depreciationAndAmortization'      : to_numeric(body.get("us-gaap_DepreciationAndAmortization", body.get('us-gaap_DepreciationDepletionAndAmortization', body.get('us-gaap_AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment', None))))
    }
    return out


# --
# run

for a,b in streaming_bulk(client, run(query), chunk_size = 1000, raise_on_error = False):
    print a, b