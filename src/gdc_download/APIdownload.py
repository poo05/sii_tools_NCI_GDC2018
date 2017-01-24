import getopt
import json
import os
import re
import subprocess
import urllib

import requests

#import json requests
with open('queries.json') as f:
    JSON_QUERIES = json.load(f)

#import cancer names to be used in json requests
with open('cancers.txt') as f:
    CANCERS = [cancer for cancer in f]

#import the metadata fields normally seen
mapping = requests.get('https://gdc-api.nci.nih.gov/files/_mapping')
json_field_map = mapping.json()
expand_fields = json_field_map["expand"]
expand_string = expand_fields.join(',')
expand_req_string = '?expand=' + expand_string

def download_manifest(cancer, path):
    """ Downloads the manifest from NCI-GDC via API using
        the cancer (i.e. project name) and path for a set of queries.
    """
    manifest_query = JSON_QUERIES.copy()
    manifest_query['main_request']['content'].extend(JSON_QUERIES['requests'])

    #Replace the cancer filter placeholder with the cancer name
    cancer_dict = manifest_query['main_request']['content'][0]
    cancer_dict['value'] = [cancer]
    manifest_query['main_request']['content'][0] = cancer_dict

    #Create the http get url
    query = urllib.parse.urlencode(json.dumps(manifest_query['main_request']))
    query_url = 'https://gdc-api.nci.nih.gov/files?filters='+query+'&size=30000&return_type=manifest'

    #Execute the http get url
    name = re.match('.+-(.+)', cancer)
    file_name = path + '/' + name.group(1) + '.tsv'
    api_response = requests.get(query_url)

    #Write manifest to file
    with open(file_name, 'w') as f:
        f.write(api_response.text)
    
    return file_name

def download_other_manifests(cancer, path):
    """ DocString goes here
    """
    #initiate manifest list
    manifests = []

    #Find cancer name
    name = re.match('.+-(.+)', cancer).group(1)

    #Use main query
    manifest_query = JSON_QUERIES.copy()
    cancer_dict = manifest_query['main_request']['content'][0]
    cancer_dict['value'] = [cancer]
    manifest_query['main_request']['content'][0] = cancer_dict
    manifest_query = manifest_query['main_request']

    #Instantiate requests for each type of manifest
    for i in JSON_QUERIES["requests"]:
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

    #Store filenames
    file_names = []

    #Ask for requests in sequence
    manifests = ['https://gdc-api.nci.nih.gov/files?filters='+
                 query+'&size=30000&return_type=manifest' 
                 for query in manifests]

    for prefix, query in zip(prefixes, manifests):
        file_name = path + prefix + '_' + name + '.tsv'

        response = requests.get(query)
        json_response = response.json()

        #Write the response to a file
        with open(file_name, 'w') as f:
            json.dump(json_response, f, indent='\t')

        file_names.append(file_name)

    return file_names

def write_metadata(manifest_path, path=None):
    """ DocString Goes Here
    """
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
    
    if path != None:
        manifest_path = path + manifest_path[manifest_path.rfind('/'):]

    #Make pretty json file with metadata    
    with open(manifest_path[:-4] + '.json') as f:
        json.dump(meta_list, f, indent='\t')

    os.remove(manifest_path)


def write_files(manifest_path, gdc_path, path):
    """ DocString Goes Here
    """
    #Download Files using the gdc-client
    subprocess.call([gdc_path+'/gdc-client', 'download', '-d', path,
                     '--no-segment-md5sums', '--no-related-files', '--no-annotations',
                     '-m', manifest_path])

    os.remove(manifest_path)

def main():
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hgd",["help","c_dir=","dest=","g_path=","m_path=", "d_dir="])
    except getopt.GetoptError:
        print( 'downloadManifests.py -g --c_dir <directory of cancer list> '
              +'--dest <directory to save the files>'+
              ' --g_path <path of the gdc-client> --m_path <path of lastest mozilla browser>')
        sys.exit(2)
    for o,a in opts:
        if o in ("-h","--help"):
            print( 'downloadManifests.py -g --c_dir <directory of cancer list> ' + 
                    '--dest <directory to save the files>'+
                    ' --g_path <path of the gdc-client>')
        elif o == "-d":
            break
        elif o == "--c_dir":
            cancer_dir = a
        elif o == "--dest":
            dest = a
        elif o == "--g_path":
            gdc_path = a
        elif o == "--down_dir":
            download_dir = a    
        else:
            assert False, "unhandled option"
    '''
    path = '//sii-nas3/Data/NCI_GDC'
    for cancer in CANCERS:
        name = re.match('.+-(.+)', cancer).group(1)
        raw_manifests = download_other_manifests(cancer, path +'/'+ name)
        for manifest in raw_manifests:
            write_metadata(manifest)
        all_manifest_path = download_manifest(cancer, path)
        write_files(all_manifest_path, 'C:/Users/localadmin/Downloads', path +'/'+ name +'/'+ name)

if __name__ == "__main__":
    main()
