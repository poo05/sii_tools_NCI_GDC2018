import urllib
import json
import re
import requests
import subprocess

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
    expand_req_string = '?expand=' + expand_string

def download_manifest(cancer, path):
    """ Downloads the manifest from NCI-GDC via API using
        the cancer (i.e. project name) and path for a set of queries.
    """
    manifest_query = json_queries.copy()
    manifest_query['main_request']['content'].extend(json_queries['requests'])

    #Replace the cancer filter placeholder with the cancer name
    cancer_dict = manifest_query['main_request']['content'][0]
    cancer_dict['value'] = [cancer]
    manifest_query['main_request']['content'][0] = cancer_dict

    #Create the http get url
    query = urllib.parse.urlencode(json.dumps(manifest_query['main_request']))
    query_url = 'https://gdc-api.nci.nih.gov/files?filters='+query+'&size=30000&return_type=manifest'

    #Execute the http get url
    name = re.match('.+-(.+)', cancer)
    file_name = path+'/'+name.group(1)+'.tsv'
    api_response = requests.get(query_url)

    #Write manifest to file
    with open(file_name,'w') as f:
        for line in api_response.iter_lines():
            f.write(line+'\n')
    return f.exists()

def download_other_manifests(cancer,path):
    """ DocString goes here
    """
    #initiate manifest list
    manifests = []

    #Find cancer name
    name = re.match('.+-(.+)', cancer).group(1)

    #Use main query
    manifest_query = json_queries.copy()
    cancer_dict = manifest_query['main_request']['content'][0]
    cancer_dict['value'] = [cancer]
    manifest_query['main_request']['content'][0] = cancer_dict
    manifest_query = manifest_query['main_request']

    #Instantiate requests for each type of manifest
    for i in json_queries["requests"]:
        temp_query = manifest_query.copy()
        temp_dic = temp_query['content']
        temp_dic.append(i)
        temp_query['content'] = temp_dic

        #Save json request as a urlencoded string
        json_string = json.dumps(temp_query)
        request_string = urllib.parse.urlencode(json_string)
        manifests.append(request_string)

    #import file prefixes
    with open('file_prefixes.txt') as f:
        prefixes = [prefix for prefix in f]

    #Ask for requests in sequence
    manifests = ['https://gdc-api.nci.nih.gov/files?filters='+query+'&size=30000&return_type=manifest' for query in manifests]

    for prefix,query in zip(prefixes, manifests):
        
        file_name = prefix + '_' + name + '.tsv'
        
        response = requests.get(query)
        json_response = response.json()
        
        #Write the response to a file
        with open(file_name, 'w') as f:
            json.dump(json_response,f)

def write_metadata(manifest_path, dest):
    
    #Get the file uuids from manifest
    with open(manifest_path) as f:
        file_ids = [i[0:i.find('\t')] for i in f]
        file_ids.pop()
    
    #Metadata list
    meta_list = []

    #Use NCI-GDC API to search for metadata
    for i in file_ids:
        response = requests.get('https://gdc-api.nci.nih.gov/files/'+ i + expand_req_string)
        json_response = response.json()
        meta_list.append(json_response)

    #Make pretty json file with metadata    
    with open(manifest_path[:-4] + '.json') as f:
        json.dump(meta_list, f)


def write_files(manifest, dest):
    
    #Download Files
    subprocess.call([gdc_path+'/gdc-client', 'download','-d', dest+'/'+cancer_name,
            '--no-segment-md5sums','--no-related-files','--no-annotations', '-m', manifest_path])

    