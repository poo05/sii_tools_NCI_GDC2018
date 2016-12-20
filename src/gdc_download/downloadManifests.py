# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 16:23:18 2016

@author: localadmin
"""

# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import shutil2




binary = FirefoxBinary('C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe')

driver = webdriver.Firefox(firefox_binary=binary)
driver.implicitly_wait(30)
base_url = "https://gdc-portal.nci.nih.gov/"

with open('cancers.txt','r') as f:
    cancers = []
    for line in f:
        splLine = line.split(' ')[0]
        if splLine != '': 
            cancers.append()

queries = []             
            
for cancer in cancers:
    driver.get(base_url + "/query/s?query=cases.project.project_id%20in%20%5B"+
               cancer + "%5D%20and%20files.access%20in%20%5B%22open%22%5D%20and%20%0A"+
               "(%0A%0A(files.data_category%20in%20%5B%22Simple%20Nucleotide%20Variation%22%5D%20and%20files.analysis.workflow_type%20in%20%5B%22MuTect2%20Variant%20Aggregation%20and%20Masking%22%5D)"+
               "%20%0Aor%0A%0A"+"(files.data_category%20in%20%5B%22Copy%20Number%20Variation%22%5D%20and%20files.data_type%20in%20%5B%22Copy%20Number%20Segment%22%5D)"+
               "%0Aor%0A%0A"+"(files.data_type%20in%20%5B%22Gene%20Expression%20Quantification%22%5D%20and%20files.analysis.workflow_type%20in%20%5B%22HTSeq%20-%20FPKM%22%5D%20and%20files.access%20in%20%5B%22open%22%5D)"+
               "%0Aor%0A%0A"+"(files.data_type%20in%20%5B%22miRNA%20Expression%20Quantification%22%5D%20and%20files.experimental_strategy%20in%20%5B%22miRNA-Seq%22%5D)"+
               "%0Aor%0A%0A"+"(files.data_category%20in%20%5B%22DNA%20Methylation%22%5D)%0A%0A)&filters=%7B%22op%22:%22and%22,%22content%22:%5B%7B%22op%22:%22and%22,%22content%22:%5B%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22cases.project.project_id%22,%22value%22:%5B%22TCGA-BRCA%22%5D%7D%7D,%7B%22op%22:%22and%22,%22content%22:%5B%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.access%22,%22value%22:%5B%22open%22%5D%7D%7D,%7B%22op%22:%22or%22,%22content%22:%5B%7B%22op%22:%22and%22,%22content%22:%5B%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.data_category%22,%22value%22:%5B%22Simple%20Nucleotide%20Variation%22%5D%7D%7D,%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.analysis.workflow_type%22,%22value%22:%5B%22MuTect2%20Variant%20Aggregation%20and%20Masking%22%5D%7D%7D%5D%7D,%7B%22op%22:%22or%22,%22content%22:%5B%7B%22op%22:%22and%22,%22content%22:%5B%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.data_category%22,%22value%22:%5B%22Copy%20Number%20Variation%22%5D%7D%7D,%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.data_type%22,%22value%22:%5B%22Copy%20Number%20Segment%22%5D%7D%7D%5D%7D,%7B%22op%22:%22or%22,%22content%22:%5B%7B%22op%22:%22and%22,%22content%22:%5B%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.data_type%22,%22value%22:%5B%22Gene%20Expression%20Quantification%22%5D%7D%7D,%7B%22op%22:%22and%22,%22content%22:%5B%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.analysis.workflow_type%22,%22value%22:%5B%22HTSeq%20-%20FPKM%22%5D%7D%7D,%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.access%22,%22value%22:%5B%22open%22%5D%7D%7D%5D%7D%5D%7D,%7B%22op%22:%22or%22,%22content%22:%5B%7B%22op%22:%22and%22,%22content%22:%5B%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.data_type%22,%22value%22:%5B%22miRNA%20Expression%20Quantification%22%5D%7D%7D,%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.experimental_strategy%22,%22value%22:%5B%22miRNA-Seq%22%5D%7D%7D%5D%7D,%7B%22op%22:%22in%22,%22content%22:%7B%22field%22:%22files.data_category%22,%22value%22:%5B%22DNA%20Methylation%22%5D%7D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D")
    driver.find_element_by_css_selector("span.ng-binding.ng-scope").click()
    for ftype in type: 
        driver.find_element_by_id("add-to-cart-button").click()
        driver.find_element_by_css_selector("i.fa.fa-shopping-cart").click()
        driver.find_element_by_xpath("//div[@id='skip']/div/section[2]/div/div/button").click()
        driver.find_element_by_css_selector("#split-control-1482191843912 > span > span.ng-binding.ng-scope").click()
        driver.find_element_by_id("clear-button").click()




