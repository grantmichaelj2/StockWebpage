#Classes I created and am importing
import Scraper
from squelch import *
import Storage
import Analysis
import time
import sys
import urllib
import requests

Storage.storage.connect()
Storage.storage.populateStockList()

while True:
    #Check to see if we are commencing, or picking up
    if Storage.storage.start == False:
        Storage.storage.checkStart()
    else:
        pass
    
    #Scrape data from Twitter
    try:
        start = time.localtime()[5]
        Scraper.scraper.requestData(Scraper.scraper.stock)
    except (TimeoutError, requests.exceptions.ConnectionError, TypeError):
        print('ERROR IN TWITTER REQUEST')
        continue
    
    try:
        Scraper.scraper.seperateTickerSymbols()
    except (TimeoutError, requests.exceptions.ConnectionError):
        print('ERROR IN SEPERATING TICKERS')
        continue
    try:
        Scraper.scraper.countTotalOccurances()
    except (TimeoutError, requests.exceptions.ConnectionError):
        print('ERROR IN COUNTING TOTAL OCCURANCES')
        continue

    #Manipulate database
    Storage.storage.updateSearched()
    Storage.storage.addNewStocks(Scraper.scraper.countTickerSymbols)
    Storage.storage.populateViews()
    if Storage.storage.updateStockToSearch() == "DONE":
        try:
            Storage.storage.populateAnalysis()
            Storage.storage.populateStockList()
            Storage.storage.exportAndRestart()
        except (ValueError, urllib.error.HTTPError):
            print('ERROR IN GETTING MA AND PEG RETURNS')
            
    else:
        pass
    
    finish = time.localtime()[5] - start
    if finish > 3:
        sys.exit()

# *6* Save data fr om the newly parsed data, populate tables with new views, new tickers, change searched to true
# *9* Update tables to reflect the new data.
# *10* When all ticker symbols have been searched, organize stock_analysis into most viewed stocks
# *11* If the stock is in the top 25 most viewed stocks, and the M.A. and PEG values are True
# Add the ticker symbol, price at next day open current price, days left to sell (2 weeks), and percent change

    

