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
import subprocess
import os
import re
import time
from datetime import datetime
import shutil2
import collections

    
def script(downloadDir,dest='\\\\sii-nas3/Data/NCI-GDC', gdc_path='', 
           mozillaPath = 'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe',
           ):
    
    
    
    binary = FirefoxBinary(mozillaPath)
    
    driver = webdriver.Firefox(firefox_binary=binary)
    driver.implicitly_wait(30)
    base_url = "https://gdc-portal.nci.nih.gov"
    
    with open('cancers.txt','r') as f:
        cancers = []
        for line in f:
            splLine = line.split(' ')[0]
            if splLine != '': 
                cancers.append()
    
    queryS = ['(cases.project.project_id in [','] and files.access in ["open"])']
    queries = ['(files.data_category in ["Simple Nucleotide Variation"] and files.analysis.workflow_type in ["MuTect2 Variant Aggregation and Masking"])',
             '(files.data_category in ["Copy Number Variation"] and files.data_type in ["Copy Number Segment"])',
             '(files.data_type in ["Gene Expression Quantification"] and files.analysis.workflow_type in ["HTSeq - FPKM"] and files.access in ["open"])',
             '(files.data_type in ["miRNA Expression Quantification"] and files.experimental_strategy in ["miRNA-Seq"])',
             '(files.data_category in ["DNA Methylation"])'
            ]             
    qName = ['snv','cnv','gene_expr','mirna','meth']
    for cancer in cancers:
        #Create a folder in the destination to store the results
        os.mkdir(dest+'/'+cancer)
        #Base of the search string with the project name integrated
        qString = queryS[0]+ cancer +queryS[1]
        
        #Go to website
        driver.get(base_url + '/query/s?query=' + 
                   urllib.quote(
                                    qString + ' and (' + queries[0] + ' or ' + 
                                    queries[1]+' or '+queries[2]+' or ' + 
                                    queries[3] + ' or ' + queries[4] +')'
                                    )
                    )
        #Click on the banner that says that the site is a gov't website
        driver.find_element_by_css_selector("button.btn.btn-primary").click()
        #wait 10s for page to load
        driver.implicitly_wait(10)
        #Click search query
        driver.find_element_by_xpath("//div[@id='skip']/div/div/div/search-bar/div/div/div/div[2]/button").click()
        #wait 10s for page to load
        driver.implicitly_wait(10)
        #Click on download manifest
        driver.find_element_by_css_selector("span.ng-binding.ng-scope").click()
        for ftype in queries:
            #Go to website
            driver.get(base_url + '/query/s?query=' + urllib.quote(qString + ' and (' + ftype +')'))
            #wait 10s for page to load
            driver.implicitly_wait(10)
            #Click search query
            driver.find_element_by_xpath("//div[@id='skip']/div/div/div/search-bar/div/div/div/div[2]/button").click()
            #wait 10s for page to load
            driver.implicitly_wait(10)
            #Click on add all to cart
            driver.find_element_by_id("add-to-cart-button").click()
            #Click view cart
            driver.find_element_by_css_selector("i.fa.fa-shopping-cart").click()
            #wait 60s for page to load
            driver.implicitly_wait(60)
            #Click on Download Metadata
            driver.find_element_by_xpath("//div[@id='skip']/div/section[2]/div/div/button").click()
            #Click clear cart
            driver.find_element_by_css_selector("#split-control-1482191843912 > span > span.ng-binding.ng-scope").click()
            #Wait 1s for button to appear
            driver.implicitly_wait(1)
            #Click clear all items in cart
            driver.find_element_by_id("clear-button").click()
        
        manifest = getManifest(downloadDir)
        subprocess.call([gdc_path+'/gdc-client', 'download','-d', dest+'/'+cancer,'--no-segment-md5sums','--no-related-files','--no-annotations', '-m', manifest])   
        
        fileSort = comp_time(downloadDir)
        for meta,prefix in zip(fileSort,qName):
            shutil2.move(downloadDir+'/'+meta, dest+'/'+ prefix+'_'+cancer+'.json')
    

    
def comp_time(downDir):
    flist = os.listdir(downDir)
    pattern = re.compile("(?P<Year>[0-9]{4})\-(?P<Month>[0-9]{2})\-(?P<Date>[0-9]{2})T(?P<Hour>[0-9]{2})\_(?P<Minute>[0-9]{2})\_(?P<Second>[0-9]{2})\.(?P<Precision>[0-9]{6})\.json")
    tdic = {}
    for i in flist:
        pattmatch = pattern.match(i)
        if pattmatch != None:
            a = datetime(pattmatch.group('Year'),pattmatch.group('Month'),
                         pattmatch.group('Date'),pattmatch.group('Hour'),
                         pattmatch.group('Minute'),pattmatch.group('Second'),
                         pattmatch.group('Precision')
                         )
            tdic[a] = i
    fdic = collections.OrderedDict(sorted(tdic.items()))
    sortVals = fdic.values()
    assert len(sortVals) <=5
    if len(sortVals)!= 5:
        comp_time(downDir)
        

def getManifest(downDir):
    flist = os.listdir(downDir)
    for i in flist:
        if i[-4:] == '.tsv':
            return i
    
    return manifest(downDir)
    
