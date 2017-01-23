import urllib
import json
import re
import requests

#import json requests
with open('queries.json') as f:
    json_queries = json.load(f)

#import cancer names to be used in json requests
with open('cancers.txt') as f:
    cancers = [cancer for cancer in f]

#import the metadata fields normally seen
with requests.get('https://gdc-api.nci.nih.gov/files/_mapping') as f:
    json_field_map = json.load(f)
    expand_fields = json_field_map["expand"]
    expand_string = expand_fields.join(',')
    expand_req_string = 'expand?=' + expand_string

def download_manifest(cancer,path):
    manifest_query = json_queries
    manifest_query['main_request']['content'].extend(json_queries['requests'])
    
    #Replace the cancer filter placeholder with the cancer name
    cancer_dict = manifest_query['main_request']['content'][0]
    cancer_dict['value'] = [cancer]
    manifest_query['main_request']['content'][0] = cancer_dict
    
    #Create the http get url
    query = urllib.urlencode(json.dumps(a))
    query_url = 'https://gdc-api.nci.nih.gov/files?filters='+query+'&size=30000&return_type=manifest'
    
    #Execute the http get url
    name = re.match('.+-(.+)',cancer)
    file_name = path+'/'+name.group(1)+'.tsv'
    api_response = requests.get(query_url)
    
    #Write manifest to file
    with open(file_name,'w') as f:
        for line in api_response.iter_lines():
            f.write(line+'\n')
    return f.exists()


def write_metadata(manifest_path):
    with open(manifest_path) as f:
        file_ids = [i[0:i.find('\t')] for i in f]
