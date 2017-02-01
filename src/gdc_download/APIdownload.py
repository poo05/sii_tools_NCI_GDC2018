import getopt
import json
import os
import re
import urllib

import requests

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

# import json requests
with open(SRC_PATH + '/' + 'queries.json') as f:
    JSON_QUERIES = json.load(f)

# import cancer names to be used in json requests
with open(SRC_PATH + '/' + 'cancers.txt') as f:
    CANCERS = [cancer for cancer in f]


def meta():
    """Fetch the expand fields from the NCI-GDC files/_mappping endpoint"""
    mapping = requests.get('https://gdc-api.nci.nih.gov/files/_mapping')
    json_field_map = mapping.json()
    expand_fields = json_field_map["expand"]
    expand_string = ','.join(expand_fields)
    ret = expand_string
    return ret

# import the metadata fields normally seen
expand_req_string = meta()


def download_manifest(cancer_project, dest):
    """ Downloads the manifest of relevant files from NCI-GDC via API for a particular cancer project

    Keywords arguments:
    cancer_project -- the NCI-GDC project for the particular cancer (i.e. TCGA-BRCA)
    dest -- the destination to which the files are downloaded
    """
    # Create a copy of the constant that stores all required queries
    manifest_query = dict(JSON_QUERIES)

    # Replace the cancer filter placeholder with the cancer name
    manifest_query['main_request']['content'][0]["content"]['value'] = [cancer_project]

    print( manifest_query['main_request']['content'][0])
    
    manifest_query['main_request']['content'].append({"op":"or", "content":[]})
    
    manifest_query['main_request']['content'][-1]["content"].extend(JSON_QUERIES['requests'])

    # Create the http get url
    query = urllib.parse.quote(json.dumps(manifest_query['main_request']))

    #print(manifest_query['main_request'])
    query_url = 'https://gdc-api.nci.nih.gov/files?filters=' + \
        query + '&size=30000&return_type=manifest'

    # Execute the http get url
    name = re.match('.+-(.+)', cancer_project)
    file_name = dest + '/' + name.group(1) + '/' +name.group(1) + '.tsv'
    api_response = requests.get(query_url)

    # Write manifest to file
    with open(file_name, 'w') as f:
        f.write(api_response.text)

    return file_name


def download_other_manifests(cancer_project, dest, create_dir=False):
    """ Returns the manifests given the NCI_GDC project name of the cancer and the path

    Keyword arguments:
    cancer_project -- the NCI-GDC project for the particular cancer (i.e. TCGA-BRCA)
    dest -- the destination string to which the files are downloaded. Ends without a slash
    creat_dir -- a boolean that determines whether the pat should be created
    """
    if create_dir:
        os.mkdir(dest)
    # initiate manifest list
    manifests = []

    # Find cancer name
    name = re.match('.+-(.+)', cancer_project).group(1)

    # Use main query
    manifest_query = dict(JSON_QUERIES)
    manifest_query['main_request']['content'][0]['content']['value'] = [cancer_project]
    manifest_query = manifest_query['main_request']

    # Instantiate requests for each type of manifest
    for i in JSON_QUERIES["requests"]:
        temp_query = dict(manifest_query)
        temp_query['content'].append(i)
        
        #dealing with weird object inheritance!!!
        temp_query['content'].pop(2)
        
        # Save json request as a quoted string
        json_string = json.dumps(temp_query)
        request_string = urllib.parse.quote(json_string)
        manifests.append(request_string)
    
    # import file prefixes
    with open(SRC_PATH + '/' + 'file_prefixes.txt') as f:
        prefixes = []
        for prefix in f:
            if prefix[-1] == '\n':
                prefixes.append(prefix[:-1])
            else:
                prefixes.append(prefix)

    # Store filenames
    file_names = []

    # Ask for requests in sequence
    manifests = ['https://gdc-api.nci.nih.gov/files?filters=' +
                 query + '&size=30000&return_type=manifest'
                 for query in manifests]

    print(prefixes)
    for prefix, query in zip(prefixes, manifests):
        file_name = dest + '/' + prefix + '_metadata.' + name + '.tsv'
        print(file_name)
        response = requests.get(query)
        #json_response = response.json()
        #print("fubar")
        # Write the response to a file
        with open(file_name, 'w') as f:
            f.write(response.text)

        file_names.append(file_name)

    return file_names


def write_metadata(manifest_path, dels=True, path=None):
    """ Replaces the manifest file with a JSON metadata file

    Keyword Arguments
    manifest_path -- string of the path where the manifest is stored
    path -- an alternative path to which to save the json metadata
    """
    # Get the file uuids from manifest
    with open(manifest_path) as f:
        file_ids = [i[0:i.find('\t')] for i in f]
        file_ids.pop()

    # Metadata list
    meta_list = []

    payload_json = {"filters":{"op":"in", "content": {
    "field": "files.file_id", "value": file_ids}},"fields":expand_req_string,"size":"30000"}

    # Use NCI-GDC API to search for metadata
    response = requests.post(
        'https://gdc-api.nci.nih.gov/files', json=payload_json)
    json_response = response.json()
    meta_list.append(json_response)

    if path != None:
        manifest_path = path + '/' + manifest_path[manifest_path.rfind('/'):]

    # Make pretty json file with metadata
    with open(manifest_path[:-4] + '.json', 'w') as f:
        json.dump(meta_list, f, indent=2)

    # delete the manifest
    if dels:
        os.remove(manifest_path)


def write_files(manifest_path, path=False, dels=True):
    """ Writes files from manifest
    """

    print(manifest_path)
    # Download Files using the gdc-API post method
    with open(manifest_path) as f:
        id_list = []
        for line in f:
            if line[-1] == '\n':
                id_list.append(line[:-1])
            else:
                id_list.append(line)
    print(id_list[0])
    json_post = {"ids": id_list}

    post = requests.post("https://gdc-api.nci.nih.gov/data", json=json_post)
    
    with open('data','w') as f:
        f.write(post)
        
    # Delete the manifest
    if dels:
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
        print(cancer)
        if cancer[-1] == '\n':
            cancer = cancer[:-1]
        name = re.match('.+-(.+)', cancer).group(1)
        raw_manifests = download_other_manifests(cancer, path + '/' + name)
        for manifest in raw_manifests:
            write_metadata(manifest)
        all_manifest_path = download_manifest(cancer, path)
        write_files(all_manifest_path, path + '/' + name + '/' + name, dels=False)

if __name__ == "__main__":
    main()
