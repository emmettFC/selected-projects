#################################
## TO QUICKLY ACCESS CNTRL+F ANY OF THE SECTIONS
##SECTIONS:
##1. IMPORT DEPENDENCIES
##2. SET UP FUNCTIONS
##3. QUERY THE WEB
##4. PARSE THE DATA FROM WEB QUERY
##5. PUT DATA INTO DATABASE
##6. GRAPH DATA
##################################

##1. IMPORT DEPENDENCIES##
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import matplotlib.pyplot as plt


##2. SET UP FUNCTIONS##
class SessionGoogle:
    def __init__(self, url_login, url_auth, login, pwd): #LOGGING INTO GOOGLE
        self.ses = requests.session()
        login_html = self.ses.get(url_login)
        soup_login = BeautifulSoup(login_html.content).find('form').find_all('input')
        dico = {}
        for u in soup_login:
            if u.has_attr('value'):
                dico[u['name']] = u['value']
        
        dico['Email'] = login
        dico['Passwd'] = pwd
        self.ses.post(url_auth, data=dico)

    def get(self, URL): #getting text from the web
        return self.ses.get(URL).text 


##3. QUERY THE WEB
url_login = "https://accounts.google.com/ServiceLogin"
url_auth = "https://accounts.google.com/ServiceLoginAuth"
session = SessionGoogle(url_login, url_auth, "UN", "PW") #logging in-input your own UN & PW

main='http://www.google.com/trends/fetchComponent?q='

searchString='homeaway%2C%20home%20away%2C%20vrbo' #between any searches you require %2C%20. spaces between words need %20

queryString=main+searchString+'&cid=TIMESERIES_GRAPH_0&export=3' #this pulls just the data. you can view the graphs by visiting 
#https://www.google.com/trends/explore#q=homeaway%2C%20vrbo%2C%20home%20away&cmpt=q&tz=

x= session.get(queryString) #qeurying the web to get the text

print x #let's view the output 

#the data will be rendered in order so here it will return as homeaway, home away, vrbo


##4. PARSE THE DATA FROM WEB QUERY
regex = 'Date(.+?)new' #this is the locator on all new data for each quarter
pattern = re.compile(regex)
webData = re.findall(pattern,x)

dataPattern=re.compile('f":"(.+?)"') #further parsing the information

searchData=[]
for i in range(1,len(webData)): 
    print(i)
    searchData.append(re.findall(dataPattern,webData[i].encode('ascii'))) #need to transfer the beautiful soup encoding

print searchData[1] #let's look at what we've returned


##5. PUT DATA INTO DATABASE
columns=('date','homeaway','home_away','vrbo')
df=pd.DataFrame(searchData) #using pandas library to set up a data table with column names "columns"
df.columns=columns
df[['homeaway','home_away','vrbo']] = df[['homeaway','home_away','vrbo']].astype(float)

print df[:5] #let's view the data 


##6. GRAPH DATA

plt.plot(df['homeaway'],'r--',df['home_away'],'bs',df['vrbo'],'g^') #red line is homeaway, blue squares home away, green arrows is vrbo

