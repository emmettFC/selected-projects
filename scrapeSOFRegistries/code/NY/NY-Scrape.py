'''
    New York State SOR Scrape:
'''


# -- 
# Dependancies

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display

import urllib2
from urllib2 import urlopen
import requests
import csv
import re
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pprint import pprint
import xmltodict
import pickle


# -- 
# Get zipcodes from file

allCodes = pd.read_csv('/Users/culhane/VAproject/data/zip_code_database.csv')
nyCodes = allCodes.loc[allCodes['state'] == 'NY']
nyCodes = nyCodes[['zip']].values.tolist() 
nyCodes = [str(i[0]) for i in nyCodes]

# -- 
# Instantiate display to get past captcha manually

display = Display(visible=0, size=(800, 600))
display.start()
url = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp'
driver = webdriver.Chrome('/Users/culhane/Desktop/chromedriver') 
time.sleep(1)

driver.get(url)

base = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp?offenderSubmit=true&LastName=&County=&Zip='
lhs = '&recaptcha_challenge_field='
captcha = '03AMPJSYUeBk4iSBuGFyQvEVWwYyxc1nkQmOwg-dqZ0g1QHsCjk07oBGdUFPAGYhDx_yVGuhS_IdkmqtYdevED48NWkdnJsXAZFqFUr1PSzxOKT-bi9y_nveUoeVKyV7P3bdeUzg3a0Nmvc8O1Xzng8_tUgSTwdXXQN8dQU6hyEp_8f64dRLWdvUXXCRfTrnqhp-eSFCawqoAvoFI-XR5oHD09Qs-Mx9WWwg&recaptcha_response_field=eccetto+rybroo'
rhs = '&Submit=EN'

# -- 
# Copy and paste url after captcha / identify captcha string 

def getCaptcha(url): 
    base = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp?offenderSubmit=true&LastName=&County=&Zip='
    code = nyCodes[0]
    lhs = '&recaptcha_challenge_field='
    rhs = '&Submit=EN'
    left = base + code + lhs
    captcha = url.replace(left, '')
    return captcha.replace(rhs, '')


http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp

# - 

code = 10003 
url = base + str(code) + ext
driver.get(url)


# - 

html     = driver.page_source
soup     = BeautifulSoup(html)
tables   = soup.findAll('table')  


# -- 
# Get all offender links

url   = urlopen(url)
soup  = BeautifulSoup(url)



base = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp?offenderSubmit=true&LastName=&County=&Zip='
code = '10003'
lhs = '&recaptcha_challenge_field'
captcha = '=03AMPJSYVvCMRfxHD41CvwzreaEOKWWV0SRh1kQsbDaMQn_IV7xyWETAu2m0Qvb4-OexUv9Yh0c7nl5Q6jfxlhNacJLBNhX8P_M7IzZrAaJu8q1a6RWenm2BNqsl1lw60oEp-PGo8nDh208TU_omHdKDGL_pJWBvWC0OeGsil3C1QopJVJDPcRYhhHMrC1LRXjjtILhvkfKOE_OhAQmI74_vy3GeR-zt1aCw&recaptcha_response_field=como+fermata'
rhs = '&Submit=EN'


tables = soup.findAll('table')




'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp?offenderSubmit=true&LastName=&County=&Zip=10003&recaptcha_challenge_field=03AMPJSYVvCMRfxHD41CvwzreaEOKWWV0SRh1kQsbDaMQn_IV7xyWETAu2m0Qvb4-OexUv9Yh0c7nl5Q6jfxlhNacJLBNhX8P_M7IzZrAaJu8q1a6RWenm2BNqsl1lw60oEp-PGo8nDh208TU_omHdKDGL_pJWBvWC0OeGsil3C1QopJVJDPcRYhhHMrC1LRXjjtILhvkfKOE_OhAQmI74_vy3GeR-zt1aCw&recaptcha_response_field=como+fermata&Submit=EN'




8426
8487



# -

display = Display(visible=0, size=(800, 600))
display.start()


# - 

url = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp'
driver = webdriver.Chrome('/Users/culhane/Desktop/chromedriver') 
time.sleep(1)

# - 

driver.get(url)

base = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp?offenderSubmit=true&LastName=&County=&Zip='
ext = '&recaptcha_challenge_field=03AMPJSYUeBk4iSBuGFyQvEVWwYyxc1nkQmOwg-dqZ0g1QHsCjk07oBGdUFPAGYhDx_yVGuhS_IdkmqtYdevED48NWkdnJsXAZFqFUr1PSzxOKT-bi9y_nveUoeVKyV7P3bdeUzg3a0Nmvc8O1Xzng8_tUgSTwdXXQN8dQU6hyEp_8f64dRLWdvUXXCRfTrnqhp-eSFCawqoAvoFI-XR5oHD09Qs-Mx9WWwg&recaptcha_response_field=eccetto+rybroo&Submit=EN'

# - 

code = 10003 
url = base + str(code) + ext
driver.get(url)


# - 

html     = driver.page_source
soup     = BeautifulSoup(html)
tables   = soup.findAll('table')   

# this is actually the table; very cool I guess. 
tables[1]  