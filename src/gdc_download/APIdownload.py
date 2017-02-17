"""APIDownload

This module uses the NCI-GDC API to download various
important files and information from the NCI-GDC Data Repository.
This is as specified in the mission objectives.
"""
import getopt
import json
import os
import re
import subprocess
import urllib

import requests

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

# import json requests
with open(SRC_PATH + '/' + 'queries.json') as query_f:
    JSON_QUERIES = json.load(query_f)

# import cancer names to be used in json requests
with open(SRC_PATH + '/' + 'cancers.txt') as cancer_f:
    CANCERS = [cancer for cancer in cancer_f]

# import the metadata fields normally seen
with open(SRC_PATH + '/' + 'metadataFilters.json') as filter_f:
    meta_f = json.load(filter_f)
    FIELDS = ",".join(meta_f["fields"])
    EXPAND = ",".join(meta_f["expand"])

def download_manifest(cancer_project, dest):
    """ Downloads the manifest of relevant files from NCI-GDC
        via API for a particular cancer project

    Keywords arguments:
    cancer_project -- the NCI-GDC project for the particular cancer (i.e. TCGA-BRCA)
    dest -- the destination to which the files are downloaded
    """
    # Create a copy of the constant that stores all required queries
    manifest_query = dict(JSON_QUERIES)

    # Replace the cancer filter placeholder with the cancer name
    manifest_query['main_request']['content'][0]["content"]['value'] = [cancer_project]

    print(manifest_query['main_request']['content'][0])

    manifest_query['main_request']['content'].append({"op":"or", "content":[]})

    manifest_query['main_request']['content'][-1]["content"].extend(JSON_QUERIES['requests'])

    # Create the http get url
    query = urllib.parse.quote(json.dumps(manifest_query['main_request']))

    #print(manifest_query['main_request'])
    query_url = 'https://gdc-api.nci.nih.gov/files?filters=' + \
        query + '&size=30000&return_type=manifest'

    # Execute the http get url
    name = re.match('.+-(.+)', cancer_project)
    file_name = dest + '/' + name.group(1) + '/' +name.group(1) + 'manifest.tsv'
    api_response = requests.get(query_url)

    # Write manifest to file
    with open(file_name, 'w') as whole_manifest:
        whole_manifest.write(api_response.text)

    with open(file_name) as whole_manifest:
        print(len(whole_manifest.readlines())-1)

    return file_name

def assemble_manifest(manifest_list, cancer_project, dest):
    # Assemble a complete manifest from all the smaller manifests
    name = re.match('.+-(.+)', cancer_project)
    file_name = dest + '/' + name.group(1) + '/' +name.group(1) + 'manifest.tsv'
    for manifest in manifest_list:
        with open(manifest) as read_file:
            with open(file_name, 'a+') as write_file:
                write_file.write(read_file.read())

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
        if len(temp_query['content'])>3:
            popped = temp_query['content'].pop(2)
            #print(popped)
        assert len(temp_query['content']) == 3

        # Save json request as a quoted string
        json_string = json.dumps(temp_query)
        request_string = urllib.parse.quote(json_string)
        manifests.append(request_string)

    # import file prefixes
    with open(SRC_PATH + '/' + 'file_prefixes.txt') as prefix_file:
        prefixes = []
        for prefix in prefix_file:
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
        response = requests.get(query)
        #json_response = response.json()
        #print("fubar")
        # Write the response to a file
        with open(file_name, 'w') as manifest:
            manifest.write(response.text)
            
        print(file_name+'\t'+str(os.path.getsize(file_name)))

    return file_names


def write_metadata(manifest_path, dels=True, path=None):
    """ Replaces the manifest file with a JSON metadata file

    Keyword Arguments
    manifest_path -- string of the path where the manifest is stored
    path -- an alternative path to which to save the json metadata
    """

    print(manifest_path[:-4] + '.json')

    # Get the file uuids from manifest
    with open(manifest_path) as f:
        file_ids = [i[0:i.find('\t')] for i in f]
        print(file_ids.pop(0))

    payload_json = {
        "filters": {
            "op":"in",
            "content": {
                "field": "files.file_id",
                "value": file_ids}
        },
        "fields":FIELDS,
        "expand":EXPAND,
        "size":"30000"
    }

    # Use NCI-GDC API to search for metadata
    request = requests.post(
        'https://gdc-api.nci.nih.gov/files', stream=True, json=payload_json)
    with open(manifest_path[:-4] + '.json', 'wb') as f:
        for content in request.iter_content():
            f.write(content)

    with open(manifest_path[:-4] + '.json', 'w') as f:
        a = json.load(f)
        b = a["data"]["hits"]
        json.dump(b, f, indent=2)
    if path != None:
        manifest_path = path + '/' + manifest_path[manifest_path.rfind('/'):]

    # delete the manifest
    if dels:
        os.remove(manifest_path)


def write_files(manifest_path, client_path=False, dels=True, use_API=True):
    """ Use GDC Client instead of API b/c connection reset
    """

    print(manifest_path)
    if use_API:
        #Download Files using the gdc-API post method
        with open(manifest_path) as f:
            id_list = []
            for line in f:
                id_list.append(line.split('\t')[0])
            id_list.pop(0)
        print(id_list[0])
        json_post = {"ids": id_list}

        post = requests.post("https://gdc-api.nci.nih.gov/data", stream=True, json=json_post)
        print("Current File:" + manifest_path[:-12] + '_data.tar.gz')
        print(post.headers)
        with open(manifest_path[:-12] + '_data.tar.gz', 'wb') as f:
            for content in post.iter_content():
                f.write(content)
    else:
        #Download via GDC-client
        complete_object = subprocess.run(
            [
                client_path, "download", "-d",
                str(manifest_path[:manifest_path.rfind('/')]), "--no-segment-md5sums",
                "--no-file-md5sum", "--no-related-files",
                "--no-annotations", "-m", manifest_path])
        print(complete_object)

    # Delete the manifest
    if dels:
        os.remove(manifest_path)

def write_files_from_list(manifest_list, client_path=False, use_API=True):
    """ Use GDC Client instead of API b/c connection reset
    """

    if use_API:
        for manifest_path in manifest_list:
            #Download Files using the gdc-API post method
            with open(manifest_path) as f:
                id_list = []
                for line in f:
                    id_list.append(line.split('\t')[0])
                id_list.pop(0)
            print(id_list[0])
            json_post = {"ids": id_list}

            post = requests.post("https://gdc-api.nci.nih.gov/data", stream=True, json=json_post)
            print("Current File:" + manifest_path[:-12] + '_data.tar.gz')
            print(post.headers)
            with open(manifest_path[:-12] + '_data.tar.gz', 'wb') as zip_file:
                for content in post.iter_content():
                    zip_file.write(content)
    else:
        for manifest_path in manifest_list:
            #Download via GDC-client
            complete_object = subprocess.run(
                [
                    client_path, "download", "-d",
                    str(manifest_path[:manifest_path.rfind('/')]), "--no-segment-md5sums",
                    "--no-file-md5sum", "--no-related-files",
                    "--no-annotations", "-m", manifest_path])
            print(complete_object)

def main():
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hgd",["help","c_dir=","dest=",
                                   "g_path=","m_path=", "d_dir="])
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
        names = re.match('(.+)-(.+)', cancer)
        project = names.group(1)
        if project == "TARGET":
            continue
        
        name = names.group(2)
        raw_manifests = download_other_manifests(cancer, path + '/' + name)
        write_files_from_list(raw_manifests)
        
        for manifest in raw_manifests:
            write_metadata(manifest)

if __name__ == "__main__":
    main()
