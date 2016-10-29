#Manipulate Database
import squelch
import mysql.connector as mysql
import Scraper
import Analysis
import sys
import urllib
#If it is the first time the program is started after reset, connect to database

class Storage():

    connected = False
    user = ''
    password = ''
    host = ''
    name = ''
    database = ''
    cursor = ''
    newUpdate = True
    stockList = []
    start = False
    
    def __init__(self):
        pass
        
    #If it is the first time the program is started after reset, connect to database
    
    def connect(self):
        
        if self.connected == False:

            self.database = mysql.connect(user = squelch.squelch.db_user,
                          password = squelch.squelch.db_pass,
                          host = squelch.squelch.db_host,
                          database = squelch.squelch.db_name)

            self.connected = True

        else:
            pass
        
        self.cursor = self.database.cursor(buffered=True)
        
    def checkStart(self):

        #Redundancy for hardcoding SPY
        if self.start == False:
            self.cursor.execute("SELECT stock FROM stockAnalysis "
                                "WHERE stock='SPY'")
            check = self.cursor.fetchone()
                
            if check == None:
                    
                self.cursor.execute("INSERT INTO stockAnalysis(stock, views, searched, mapass, pegpass) "
                               "VALUES(%s, %s, %s, %s, %s)", ("SPY", 0, 0, 0, 0))
                self.database.commit()

                self.start = True
            
            else:
                
                pass
        
        
    def updateSearched(self):
        #Update stock being searched to true for searched
        
        self.cursor.execute("UPDATE stockAnalysis "
                           "SET searched=%s "
                           "WHERE stock=%s",  (1, Scraper.scraper.stock))
        
        self.database.commit()
        
    def addNewStocks(self, newStocks):
        
        #Test to see if any parsed stocks are not in the database already
        for i in range(len(newStocks)):
            
            self.cursor.execute("INSERT INTO stockAnalysis"
                            "(stock, views, searched, mapass, pegpass) "
                            "VALUES(%s, %s, %s, %s, %s) "
                            "ON DUPLICATE KEY UPDATE stock=stock", (str(newStocks[i]), 0, 0, 0, 0))
            
            self.database.commit()

            
    def populateViews(self):
        
        #Update total number of views              
        for i in range(len(Scraper.scraper.countTickerSymbols)):
            
            count = Scraper.scraper.ticker_symbols_found.count(Scraper.scraper.countTickerSymbols[i])
            self.cursor.execute("SELECT views FROM stockAnalysis "
                           "WHERE stock=%s", (str(Scraper.scraper.countTickerSymbols[i]),))
            
            update = self.cursor.fetchone()[0]
            count += update
            
            #Update number of views, and if the other data points are true or false
            self.cursor.execute("UPDATE stockAnalysis "
                           "SET views=%s "
                           "WHERE stock=%s", (count, str(Scraper.scraper.countTickerSymbols[i])))
            
        self.database.commit()


    #Find a new stock to search
        
    def updateStockToSearch(self):
            
        self.cursor.execute("SELECT stock FROM stockAnalysis "
                           "WHERE searched=0")
        
        allStocks = self.cursor.fetchone()
        
        if allStocks == None:
            return "DONE"
        
        else:
            Scraper.scraper.stock = allStocks[0]

        self.database.commit()

    #After all stocks are parsed, run an analysis on the top 50 stocks
    def populateAnalysis(self):
        
        self.cursor.execute("SELECT stock FROM stockAnalysis "
                             "ORDER BY views DESC limit 50")
        topStocks = self.cursor.fetchall()
        
        for i in range(len(topStocks)):
            
            stock = str(topStocks[i][0])
            
            try:
                Analysis.analysis.createDates(35)
                Analysis.analysis.movingAverage(stock, Analysis.analysis.dates[-1], Analysis.analysis.dates[0], 35)
                Analysis.analysis.createDates(350)
                Analysis.analysis.movingAverage(stock, Analysis.analysis.dates[-1], Analysis.analysis.dates[0], 350)
                movingAverage = Analysis.analysis.testMovingAverage(stock)
                PEG = Analysis.analysis.priceEarningsGrowth(stock)
                priceBought = Analysis.analysis.priceBought(stock)
                
            except (ValueError, urllib.error.HTTPError):
                print('ERROR IN GETTING MA AND PEG')
                continue
            
            print(stock + ': Price= ' + str(priceBought) + ' MA=' + str(movingAverage) +' PEG=' + str(PEG))
            
            #Update Moving Average and PEG in the database for the searched stock
            
            self.cursor.execute("UPDATE stockAnalysis "
                               "SET mapass=%s, pegpass=%s, price_bought=%s, date_bought=CURDATE() "
                               "WHERE stock=%s", (movingAverage, PEG, priceBought, stock))
            
        self.newUpdate = True
        self.database.commit()
        
            
    def exportAndRestart(self):
        
        run = True
        
        while run == True:
            
            try:
                
                self.cursor.execute("INSERT INTO stocksOwned(stock, price_bought, date_bought)"
                                     "SELECT stock, price_bought, date_bought FROM stockAnalysis "
                                     "WHERE mapass=1 and pegpass=1 "
                                     "ON DUPLICATE KEY UPDATE stock=stockAnalysis.stock")

                run = False
                
            except mysql.Error as e:
                print(e)
                

        self.cursor.execute("DELETE FROM stockAnalysis")
        Scraper.scraper.stock = "SPY"

        self.database.commit()

########################################################################################################
#Database Manipulation for Director        
########################################################################################################

    def populateStockList(self):
        
        if self.newUpdate == True:
            
            self.stockList = []
            self.cursor.execute("SELECT stock FROM stocksOwned")
            toAddToList = self.cursor.fetchall()
            
            if len(toAddToList) == None:
                   pass

            else:
                
                for i in range(len(toAddToList)):
                    self.stockList.append(toAddToList[i][0])

            print(self.stockList)
                    
            self.newUpdate = False
            
        else:
            
            pass
            
    
    def retrieveCurrentPrice(self):
        
        if len(self.stockList) == None:
               pass
        else:
            
            for i in range(len(self.stockList)):
                stock = self.stockList[i]
                
                newPrice = Analysis.analysis.priceBought(stock)
                
                self.cursor.execute("UPDATE stocksOwned "
                                    "SET current_price=%s "
                                    "WHERE stock=%s", (newPrice, stock))

                self.database.commit()

    def trackPercentChange(self):
        #Tack percent change in stock price
        pass

    def trackDaysOwned(self):
        #Track each week's gain/loss
        pass

    def eraseAndExport():
        #Save to a history database
        pass

        
storage = Storage()
        
        

    
