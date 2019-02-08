import json
import argparse
from elasticsearch import Elasticsearch


# --
# cli

parser = argparse.ArgumentParser()
parser.add_argument("--config-path",   type = str, action = 'store')
args = parser.parse_args()


# --
# config

config_path = args.config_path
config      = json.load(open(config_path))

# --
# es connection

client = Elasticsearch([{'host' : config['elasticsearch']['hostname'], 'port' : config['elasticsearch']['hostport']}])


# -- 
# functions

def add_cat_mapping(raw_index, form_types):
    for form_type in form_types:
        mapping = {}
        mapping[form_type] = {
            "dynamic_templates": [
               {
                  "string_cat": {
                     "mapping": {
                        "type": "multi_field",
                        "fields": {
                           "{name}": {
                              "type": "string"
                           },
                           "cat": {
                              "type": "string",
                              "index": "not_analyzed"
                           }
                        }
                     },
                     "match": "*",
                     "match_mapping_type": "string"
                  }
               }
			],
            "properties": {
               "msg": {
	       		"type": "string"
               },
               "time" : {
               		"type" : "date",
               		"format" : "yyyy-MM-dd HH:mm:ss"
               }
            }
        }
        client.indices.put_mapping(index     = raw_index, 
                                    doc_type = form_type,
                                    body     = mapping)


# --
# create index

try:
	client.indices.create(index = config['elasticsearch']['_to_index'])
except:
	print 'error creating index'


# --
# add mapping

add_cat_mapping(config['elasticsearch']['_to_index'], [config['elasticsearch']['_type']])