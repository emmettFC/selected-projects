#################################
##scraping yahoo finance data##
################################

##THIS WILL SCRAPE ALL OF THE DATA ON THE SPY


##SECTION 1: IMPORTING LIBRARIES
import re
import pandas as pd
import requests

main='http://finance.yahoo.com/q/hp?s='

#SECTION 2: SETTING UP FUNCTION TO SCRAPE TEXT
def get( URL): #getting text from the web
    ses = requests.session()
    return ses.get(URL).text 

#SECTION 3: looping through each page and each set of prices
ticker='SPY'
dates='&a=00&b=29&c=1993&d=04&e=30&f=2015'
pageInfo='&g=d&z=66&y='

mergedPrices=[]
for p in range(0,5610,66):  #GOING TO LOOP BACK THROUGH THE 5,000 PRICES 
    print p
    page=str(p)
    
    url=main+ticker+dates+pageInfo+page
    
    x=get(url)
    
    regex = 'yfnc_tabledata1"(.+?)/td>' #this is the locator on all prices on that page
    pattern = re.compile(regex)
    prices = re.findall(pattern,x)
    
    
    pattern=re.compile('right">(.+?)<')
    deletion=False
    for i in range((len(prices)-1),-1,-1): #need to get rid of entire row where they repeat the date - so look for dividend
        print(i)
        if('Dividend' in prices[i]):
            del prices[i] #deleting the dividend
            deletion=True
        elif(deletion==True): 
            del prices[i] #deleting the date right after dividend
            deletion=False
        else:
            prices[i]=tuple(re.findall(pattern,prices[i].encode('ascii')))[0] #removing encoding and html crud
    mergedPrices=mergedPrices+prices #putting it all into one list

        
#SECTOIN 4: ASSIGNING EVERYTHING TO A DATAFRAME
columns=('date','open','high','low','close','volumn','adjClose')
df=pd.DataFrame(columns=columns)
for i in range(0,len(mergedPrices)/7): #pulling it all into a dataframe, i need to grab 7 at a time and create new rows with those
    #print i
    if(i>0):
        j=i*7
    else:
        j=0
    
   # print j    
    k=j+7
    df.loc[i]=mergedPrices[j:k] #putting into dataframe
    

import csv
df.to_csv('C:/Users/eculhane/Box Sync/Personal (Private) - eculhane/XPrize/data/test.csv')

    
