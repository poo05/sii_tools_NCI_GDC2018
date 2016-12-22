# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 16:23:18 2016

@author: Eric Ye
"""

# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import urllib
import shutil2
import subprocess
import os




binary = FirefoxBinary('C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe')

driver = webdriver.Firefox(firefox_binary=binary)
driver.implicitly_wait(30)
base_url = "https://gdc-portal.nci.nih.gov"

with open('cancers.txt','r') as f:
    cancers = []
    for line in f:
        splLine = line.split(' ')[0]
        if splLine != '': 
            cancers.append()

queries = ['(cases.project.project_id in [#CANCER] and files.access in ["open"])',
           '(files.data_category in ["Simple Nucleotide Variation"] and files.analysis.workflow_type in ["MuTect2 Variant Aggregation and Masking"])',
           '(files.data_category in ["Copy Number Variation"] and files.data_type in ["Copy Number Segment"])',
           '(files.data_type in ["Gene Expression Quantification"] and files.analysis.workflow_type in ["HTSeq - FPKM"] and files.access in ["open"])',
           '(files.data_type in ["miRNA Expression Quantification"] and files.experimental_strategy in ["miRNA-Seq"])',
           '(files.data_category in ["DNA Methylation"])'
           ]             
            
for cancer in cancers:
    driver.get(base_url + '/query/s?query=' + 
               urllib.quote(
                                queries[0] + ' and (' + queries[1] + ' or ' + 
                                queries[2]+' or '+queries[3]+' or ' + 
                                queries[4] + ' or ' + queries[5] +')'
                                )
                )
    driver.find_element_by_css_selector("span.ng-binding.ng-scope").click()
    for ftype in queries[1:]:
        driver.get(base_url + '/query/s?query=' + urllib.quote(queries[0] + ' and (' + ftype +')'))
        driver.find_element_by_id("add-to-cart-button").click()
        driver.find_element_by_css_selector("i.fa.fa-shopping-cart").click()
        driver.find_element_by_xpath("//div[@id='skip']/div/section[2]/div/div/button").click()
        driver.find_element_by_css_selector("#split-control-1482191843912 > span > span.ng-binding.ng-scope").click()
        driver.find_element_by_id("clear-button").click()
        
    file_names = [filenames for (a, b, filenames) in os.walk(downloadDir)]
    
    subprocess.call()   



