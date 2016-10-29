#Constantly Searchs stocktracker.stocksowned
#For each stock in the database, track the amount of days
#For each stock in the database, track the current price
#Compare current price to price bought, and track percentage
#Track total amount made in week increments for 5 weeks.

import squelch
import Storage
import urllib
import mysql.connector as mysql

start = True

while True:    
    
    if start == True:
        
        Storage.storage.connect()
        Storage.storage.populateStockList()
        start == False
        
    else:

        Storage.storage.retrieveCurrentPrice()



    
    
    
