# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 16:23:18 2016
@author: Eric Ye
"""

import collections
import getopt
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib
from datetime import datetime

import queue
from selenium import webdriver
from selenium.common.exceptions import (NoAlertPresentException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions


def download_cancer(q,cancer,downloadDir,dest='//sii-nas3/Data/NCI_GDC',
    gdc_path=True,
    mozillaPath = 'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'):
    try:
        if gdc_path == True:
            gdc_path == downloadDir 
        binary = FirefoxBinary(mozillaPath)
        
        driver = webdriver.Firefox(firefox_binary=binary)
        base_url = "https://gdc-portal.nci.nih.gov"
        print(cancer)
        cancer_search = re.match('.+-(.+)',cancer)
        cancer_name = cancer_search.group(1)
        
        
        queryS = ['(cases.project.project_id in [','] and files.access in ["open"])']
        queries = ['(files.data_category in ["Simple Nucleotide Variation"] and files.analysis.workflow_type in ["MuTect2 Variant Aggregation and Masking"])',
                 '(files.data_category in ["Copy Number Variation"] and files.data_type in ["Copy Number Segment"])',
                 '(files.data_type in ["Gene Expression Quantification"] and files.analysis.workflow_type in ["HTSeq - FPKM"] and files.access in ["open"])',
                 '(files.data_type in ["miRNA Expression Quantification"] and files.experimental_strategy in ["miRNA-Seq"])',
                 '(files.data_category in ["DNA Methylation"])'
                ]             
        qName = ['snv','cnv','gene_expr','mirna','meth']
            
        if os.path.exists(dest+'/'+cancer_name) != True:
            #Create a folder in the destination to store the results
            os.mkdir(dest+'/'+cancer_name)

        #Base of the search string with the project name integrated
        qString = queryS[0]+ cancer +queryS[1]
        driver.maximize_window()
        website = base_url + '/query/s?query=' + urllib.parse.quote(qString + ' and (' + queries[0] + ' or ' + queries[1]+' or '+queries[2]+' or ' + queries[3] + ' or ' + queries[4] +')')        #Go to website
        driver.get(website)
        driver.implicitly_wait(60)

        #Click on the banner that says that the site is a gov't website
        try:
            driver.find_element_by_css_selector("button.btn.btn-primary").click()
        except NoSuchElementException:
            driver.implicitly_wait(700)
            print("Yes?")
            try:
                driver.find_element_by_css_selector("button.btn.btn-primary").click()
            except NoSuchElementException:
                print("No gov't notice")
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
            driver.get(base_url + '/query/s?query=' + urllib.parse.quote(qString + ' and (' + ftype +')'))
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
            #Wait 5s for button to appear
            driver.implicitly_wait(5)
            #Click clear cart
            driver.find_element_by_css_selector("#split-control-1482191843912 > span > span.ng-binding.ng-scope").click()
            #Wait 5s for button to appear
            driver.implicitly_wait(5)
            #Click clear all items in cart
            driver.find_element_by_id("clear-button").click()
        # get the manifest file
        manifest = getManifest(downloadDir)
        # Run the gdc-client with the manifest
        subprocess.call([gdc_path+'/gdc-client', 'download','-d', dest+'/'+cancer_name,
            '--no-segment-md5sums','--no-related-files','--no-annotations', '-m', manifest])
        os.remove(manifest)
        fileSort = comp_time(downloadDir)
        for meta,prefix in zip(fileSort,qName):
            shutil.move(downloadDir+'/'+meta, dest+'/'+ prefix+'_'+cancer_name+'.json')
    except:
        print("Error!")
    finally:
        print(cancer_name)
        driver.quit()
        q.task_done()

    

    
def comp_time(downDir):
    while True:
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
        assert (len(sortVals) <=5)
        if len(sortVals) == 5:
            return sortVals
            
        

def getManifest(downDir):
    while True:
        flist = os.listdir(downDir)
        check = False
        for i in flist:
            if i[-4:] == '.tsv':
                os.remove(i)
                return i
            if i[:12] == 'gdc_manifest':
                check = True
        assert (check)
        time.sleep(10)


def multithread(cancers_dir = 'C:\\Users\\localadmin\\Downloads\\cancers.txt',
                download_dir = 'C:\\Users\\localadmin\\Downloads',
                dest='//sii-nas3/Data/NCI_GDC', gdc_path='C:\\Users\\localadmin\\Downloads', 
                mozillaPath = 'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'):
    with open(cancers_dir,'r') as f:
            cancers = []
            for line in f:
                cancers.append(line)
    thread_q = queue.Queue(1)                
    for cancer in cancers:
        t = threading.Thread(target=download_cancer, args=(thread_q,cancer,download_dir))
        thread_q.put(t)
        t.start()
        thread_q.join()
        thread_q.get(t)

        


def main():        
    cancer_dir = 'C:\\Users\\localadmin\\Downloads\\cancers.txt'
    download_dir = 'C:\\Users\\localadmin\\Downloads'
    dest='//sii-nas3/Data/NCI_GDC'
    gdc_path='C:\\Users\\localadmin\\Downloads'
    mozillaPath = 'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hgd",["help","c_dir=","dest=","g_path=","m_path=", "d_dir="])
    except getopt.GetoptError:
        print( 'downloadManifests.py -g --c_dir <directory of cancer list> '
              +'--dest <directory to save the files>'+
              ' --g_path <path of the gdc-client> --m_path <path of lastest mozilla browser>')
        sys.exit(2)
    for o,a in opts:
        if o in ("-h","--help"):
            print( 'downloadManifests.py -g --c_dir <directory of cancer list> '
              +'--dest <directory to save the files>'+
              ' --g_path <path of the gdc-client> --m_path <path of lastest mozilla browser>')
        elif o == "-d":
            break
        elif o == "--c_dir":
            cancer_dir = a
        elif o == "--dest":
            dest = a
        elif o == "--g_path":
            gdc_path = a
        elif o == "--m_path":
            mozillaPath = a
        elif o == "--d_dir":
            download_dir = a    
        else:
            assert False, "unhandled option"
    multithread(cancer_dir, download_dir,dest, gdc_path, mozillaPath)


if __name__== "__main__":
    main()
