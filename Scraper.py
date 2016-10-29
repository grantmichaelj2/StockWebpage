#Parses all the ticker symbols acquired from a twitter page

import subprocess
import time
from bs4 import BeautifulSoup as soup
import requests

class Scraper():

    stock = ''
    searched = 0
    ticker_symbols_found = []
    countTickerSymbols = []
    end = ''
    
    def __init__(self):

        self.stock = 'SPY'
        self.ticker_symbols_found = []

    #Ensure the Program Doesn't Break if No Internet Connection Exists
    def testConnection(self):
        
        connection = subprocess.call("ping twitter.com", shell=True)
        if connection == 0:
            return True
        else:
            print("Trying to Establish a Connection")
            time.sleep(5)
            return False

    #Parse Information from data
    def requestData(self, stock):

        data = requests.get("https://twitter.com/search?q=%" + "24%s&src=ctag" % stock)
        parse = soup(data.content, "html.parser")
        hashtags_found = parse.find_all('b')
        for i in range(len(hashtags_found)):
            self.ticker_symbols_found += hashtags_found[i]
            
        
    # Pull only the Ticker Symbols
    def seperateTickerSymbols(self):
        
        def removeStock():
            self.ticker_symbols_found.remove(self.ticker_symbols_found[start])
            self.end -= 1

        self.end = len(self.ticker_symbols_found) - 1
        start = 0
        
        while start <= self.end:
            try:
                if self.ticker_symbols_found[start].isupper():
                    if len(self.ticker_symbols_found[start]) <= 4:
                        start += 1
                    else:
                        removeStock()
                
                else:
                    removeStock()
                    
            except TypeError as e:
                removeStock()
                    
        for i in range(len(self.ticker_symbols_found)):
            return self.ticker_symbols_found

    def countTotalOccurances(self):
        for i in range(len(self.ticker_symbols_found)):
            if self.ticker_symbols_found[i] not in self.countTickerSymbols:
                self.countTickerSymbols.append(self.ticker_symbols_found[i])
            else:
                pass
        return(self.countTickerSymbols)
    
                        

scraper = Scraper()      
