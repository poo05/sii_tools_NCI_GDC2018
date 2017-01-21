import requests
import urllib
import re
import os
import json

cancer = 'TCGA-SARC'
try:
    if gdc_path == True:
        gdc_path == downloadDir 
    
    base_url = "https://gdc-portal.nci.nih.gov"
    print(cancer)
    cancer_search = re.match('.+-(.+)',cancer)
    cancer_name = cancer_search.group(1)
except:
    print("Something's wrong")
queryS =  ['(cases.project.project_id in [', '] and files.access in [open])']
queries = ['(files.data_category in ["Simple Nucleotide Variation"] and files.analysis.workflow_type in ["MuTect2 Variant Aggregation and Masking"])',
                 '(files.data_category in ["Copy Number Variation"] and files.data_type in ["Copy Number Segment"])',
                 '(files.data_type in ["Gene Expression Quantification"] and files.analysis.workflow_type in ["HTSeq - FPKM"]',
                 '(files.data_type in ["miRNA Expression Quantification"] and files.experimental_strategy in ["miRNA-Seq"])',
                 '(files.data_category in ["DNA Methylation"])'
                ]             
qName = ['snv','cnv','gene_expr','mirna','meth']

queries_json = [
    '{"op":"and", "content":[{"op":in, content:{"field:files.data_category", "value": ["Simple Nucleotide Variation"]}  files.analysis.workflow_type in ["MuTect2 Variant Aggregation and Masking"]}']

json_string = '{'
for query in queries:
    fields = re.match('\((.+) in (.+) and (.+) in (.+)\)',query)
    fields.group(1)

if os.path.exists(dest+'/'+cancer_name) != True:
            #Create a folder in the destination to store the results
            os.mkdir(dest+'/'+cancer_name)

qString = queryS[0]+ cancer +queryS[1]

urlsite = base_url + '/files?filters=' + urllib.parse.quote(qString + ' and (' + queries[0] + ' or ' + queries[1]+' or '+queries[2]+' or ' + queries[3] + ' or ' + queries[4] +')') + '&size=30000&return_type=manifest'


r = requests.get(urlsite)