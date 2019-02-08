'''
    Try California: 
'''

# -- 
# Dependancies

import urllib2
import requests
import csv
import re
import time
import pandas as pd

from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display


# -- 
# Instantiate display

display = Display(visible=0, size=(800, 600))
display.start()


# --
# Instantiate driver

driver = webdriver.Chrome('/Users/culhane/Desktop/chromedriver') 
time.sleep(1)


# -- 
# Get past recaptcha 

driver.get('https://www.meganslaw.ca.gov/Search.aspx#')


# -- 
# Include transient offenders

includePath = '//*[@id="IncludeTransient"]' 
driver.find_element_by_xpath(includePath).click()


# -- 
# Input first zipcode search

driver.find_element_by_xpath('//*[@id="ui-id-12"]').click() 
driver.find_element_by_id('OZipCode').send_keys(90210)
# driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90210)
driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click() 
driver.find_element_by_xpath('//*[@id="ShowListButton"]/a').click() 


# -- Try to iterate: 

driver.find_element_by_xpath('//*[@id="OZipCode"]').clear() 
driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90001)
driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click()

driver.find_element_by_xpath('//*[@id="OZipCode"]').clear() 
driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90002)
driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click()

driver.find_element_by_xpath('//*[@id="OZipCode"]').clear() 
driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90003)
driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click()

driver.find_element_by_xpath('//*[@id="OZipCode"]').clear() 
driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90004)
driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click()


# -- 
# Figure how to loop though individual offender flyers


path = '//*[@id="SearchResults"]/div[5]/div/div[1]/div[2]/div/a'
driver.find_element_by_xpath(path).click()
closePath = '/html/body/div[3]/div[1]/button/span[1]'
driver.find_element_by_xpath(closePath).click()



path = '//*[@id="SearchResults"]/div[5]/div/div[2]/div[2]/div/a'
driver.find_element_by_xpath(path).click()
closePath = '/html/body/div[3]/div[1]/button/span[1]'
driver.find_element_by_xpath(closePath).click()


path = '//*[@id="SearchResults"]/div[5]/div/div[3]/div[2]/div/a'
driver.find_element_by_xpath(path).click()
closePath = '/html/body/div[3]/div[1]/button/span[1]'
driver.find_element_by_xpath(closePath).click()


# -- 
# Identify the indices for the loop process to accomplish above 

html = driver.page_source
soup = BeautifulSoup(html)
nRecords = soup.find('span', {'id' : 'SearchCount'}).get_text()
nRecords = int(re.sub('[^0-9]', '', nRecords)) 

path = '//*[@id="SearchResults"]/div[5]/div/div[12]/div[2]/div/a'
driver.find_element_by_xpath(path).click()
closePath = '/html/body/div[3]/div[1]/button/span[1]'
driver.find_element_by_xpath(closePath).click()


# -- 
# Continue with Oakland Example

driver.find_element_by_xpath('//*[@id="OZipCode"]').clear() 
driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(94577)
driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click()

path = '//*[@id="SearchResults"]/div[5]/div/div[13]/div[2]/div/a'
driver.find_element_by_xpath(path).click()
closePath = '/html/body/div[3]/div[1]/button/span[1]'
driver.find_element_by_xpath(closePath).click()


# -- 
# Seems possible that we could use the names from the page to build this out: 

html = driver.page_source
soup = BeautifulSoup(html)

tab = soup.find('div', {'class' : 'grid-canvas'})
rows = tab.findAll('div', {'class' : 'ui-widget-content'})



driver.execute_script("window.scrollTo(0, 572)") 
driver.execute_script("window.scrollTo(572, 1000)") 

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

//*[@id="SearchResults"]/div[5]/div/div[13]/div[2]/div/a














# -- 
# Need to select the include transient offenders button

driver.get('https://www.meganslaw.ca.gov/Search.aspx#')
driver.find_element_by_xpath('//*[@id="ui-id-12"]').click() 
driver.find_element_by_id('OZipCode').send_keys(90210)
# driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90210)
driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click() 
driver.find_element_by_xpath('//*[@id="ShowListButton"]/a').click() 

includePath = '//*[@id="IncludeTransient"]' 
driver.find_element_by_xpath(path).click()




SCROLL_PAUSE_TIME = 0.5
# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height









//*[@id="SearchResults"]/div[5]/div/div[8]/div[2]/div/a


//*[@id="SearchResults"]/div[5]/div/div[12]/div[2]/div/a




zipUrls()






94577










# -- 
# Input second zipcode to begin loop process

driver.get('https://www.meganslaw.ca.gov/Search.aspx#')

driver.find_element_by_xpath('//*[@id="ui-id-12"]').click() 

driver.find_element_by_id('OZipCode').send_keys(90001)

driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click() 

driver.find_element_by_xpath('//*[@id="ShowListButton"]/a').click() 



# -- Try to iterate: 

driver.find_element_by_xpath('//*[@id="OZipCode"]').clear() 
driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90210)
driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click()



driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click() 

.send_keys(90210)




# driver.find_element_by_id('AcceptDisclaimer').click() 

# Manually enter captcha variables
<input type="text" id="OZipCode" maxlength="5" style="width: 65px">



driver.find_element_by_xpath('//*[@id="ui-id-12"]').click() 

driver.find_element_by_id('OZipCode').send_keys(90001)

driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click() 

driver.find_element_by_xpath('//*[@id="ShowListButton"]/a').click() 



# driver.find_element_by_id('OZipCode').send_keys(90002)

driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90001)

driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click() 


driver.find_element_by_xpath('//*[@id="OZipCode"]')

driver.find_element_by_xpath('//*[@id="OZipCode"]').send_keys(90210)

driver.find_element_by_xpath('//*[@id="ui-id-13"]/input[2]').click() 

.send_keys(90210)




'//*[@id="ShowListButton"]/a'


driver.find_element_by_name("button").click() 


driver.find_element_by_id('scrollMarker').click()


driver.find_element_by_id('recaptcha-anchor')

driver.find_element_by_id("recaptcha-anchor").click()



from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By

wait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element_by_xpath('//iframe[contains(@src, "google.com/recaptcha")]')))

wait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'recaptcha-anchor'))).click()

wait(driver, 10).until(EC.element_to_be_clickable((driver.find_element_by_id('recaptcha-anchor')))).click()


id - 'AcceptDisclaimer'
input

class = recaptcha-checkbox-checkmark
class = recaptcha-checkbox

driver.get('https://www.meganslaw.ca.gov/Search.aspx#')
driver.find_element_by_name("button").click() 

# -- 
# Get zip codes from file

allCodes = pd.read_csv('/Users/culhane/VAproject/data/zip_code_database.csv')
paCodes = allCodes.loc[allCodes['state'] == 'PA']
paCodes = paCodes[['zip']].values.tolist() 
paCodes = [str(i[0]) for i in paCodes]

urls = []
for code in paCodes: 
    url = buildUrl(code)
    urls.append((url, code))
