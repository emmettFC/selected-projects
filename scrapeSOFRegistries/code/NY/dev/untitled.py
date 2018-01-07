'''
    Attempt to gig up a 
'''


url   = urlopen(url)
soup  = BeautifulSoup(url)

url = 'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp?offenderSubmit=true&LastName=&County=&Zip=10003&recaptcha_challenge_field=03AMPJSYVvCMRfxHD41CvwzreaEOKWWV0SRh1kQsbDaMQn_IV7xyWETAu2m0Qvb4-OexUv9Yh0c7nl5Q6jfxlhNacJLBNhX8P_M7IzZrAaJu8q1a6RWenm2BNqsl1lw60oEp-PGo8nDh208TU_omHdKDGL_pJWBvWC0OeGsil3C1QopJVJDPcRYhhHMrC1LRXjjtILhvkfKOE_OhAQmI74_vy3GeR-zt1aCw&recaptcha_response_field=como+fermata&Submit=EN'


tables = soup.findAll('table')




'http://www.criminaljustice.ny.gov/SomsSUBDirectory/search_index.jsp?offenderSubmit=true&LastName=&County=&Zip=10003&recaptcha_challenge_field=03AMPJSYVvCMRfxHD41CvwzreaEOKWWV0SRh1kQsbDaMQn_IV7xyWETAu2m0Qvb4-OexUv9Yh0c7nl5Q6jfxlhNacJLBNhX8P_M7IzZrAaJu8q1a6RWenm2BNqsl1lw60oEp-PGo8nDh208TU_omHdKDGL_pJWBvWC0OeGsil3C1QopJVJDPcRYhhHMrC1LRXjjtILhvkfKOE_OhAQmI74_vy3GeR-zt1aCw&recaptcha_response_field=como+fermata&Submit=EN'




from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from pyvirtualdisplay import Display



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