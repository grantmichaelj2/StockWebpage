import ystockquote as quote
import Scraper
import time
import urllib

#Calculates the M.A and PEG

class Analysis():

    #Stock being Analyzed
    stock = ''
    
    #List to iterate through days of the year
    daysInMonth = [[1, 31],
                   [2, 28],
                   [3, 31],
                   [4, 30],
                   [5, 31],
                   [6, 30],
                   [7, 31],
                   [8, 31],
                   [9, 30],
                   [10, 31],
                   [11, 30],
                   [12, 31]]
    
    currentDay = [time.localtime()[0], time.localtime()[1], time.localtime()[2]]
    
    #Dates that we will be retrieving values from
    dates = []
    
    #Store 35 day moving average in this variable
    MA35 = 0

    #Store 350 day moving average in this variable
    MA350 = 0

    #Store PEG ratio in this variable
    PEG = 0

    #Price to buy at
    price = 0

    #Variable to help us keep track of number of dates iterated through in our different
    #Moving average values
    count = 0

    #List to do math for our Moving Averages
    total = [0, 0]
    
    def __init__(self):
        
        self.stock = Scraper.scraper.stock
            
    def createDates(self, length):
        
        while self.count < length:
            self.count += 1
            
            #Subtract one day
            self.currentDay[2] = int(self.currentDay[2])
            self.currentDay[2] -= 1
            
            #If days go to 0, go to the previous month
            if self.currentDay[2] == 0:
                self.currentDay[1] = int(self.currentDay[1])
                self.currentDay[1] -= 1
                
                #If it is January, and months go to 0, start at the previous year
                if self.currentDay[1] == 0:
                    self.currentDay =[self.currentDay[0] - 1, self.daysInMonth[11][0], self.daysInMonth[11][1]]
                else:
                    #If not January, find the month it is, and populate the proper list
                    for i in range(len(self.daysInMonth)):
                        if self.currentDay[1] == self.daysInMonth[i][0]:
                            self.currentDay[2] = self.daysInMonth[i][1]
                            
            #Need 2 digit string values to instert for ystockquote
            if self.currentDay[2] in (1,2,3,4,5,6,7,8,9):
                self.currentDay[2] = '0' + str(self.currentDay[2])
            if self.currentDay[1] in (1,2,3,4,5,6,7,8,9):
                self.currentDay[1] = '0' + str(self.currentDay[1])
                
            #Add the updated string to the list of dates (Nested List)
            toAddToDates = [str(self.currentDay[0]), str(self.currentDay[1]), str(self.currentDay[2])]
            self.dates.append(toAddToDates)
            
    def movingAverage(self, stock, start, end, MA):

        #Convert range from list form to string
        start = str('-'.join(start))
        end = str('-'.join(end))

        #ystockquote function to retrieve historical data from a certain period
        data = quote.get_historical_prices(stock, start, end)

        #Retrieve the Closing Price of stocks for a given date in our list of dates
        for i in range(len(self.dates)):
            dateCalculated = '-'.join(self.dates[i])
            if str(dateCalculated) in data:
                add = float(data.get(dateCalculated).get("Close"))
                #Keeps track of total price and our data points
                self.total[0] += round(add, 2)
                self.total[1] += 1

        #Store Moving Averages IOT save to database
        if MA == 35:
            self.MA35 = round(self.total[0]/self.total[1], 2)
        elif MA == 350:
            self.MA350 = round(self.total[0]/self.total[1], 2)

    def testMovingAverage(self, stock):
        
        if self.MA35 > self.MA350 and self.MA35 > float(quote.get_price(stock)):
            return 1
        else:
            return 0

    def priceEarningsGrowth(self, stock):
        self.PEG = float(quote.get_price_earnings_growth_ratio(stock))

        if self.PEG > 0 and self.PEG <= 1:
            return 1
        else:
            return 0

    def priceBought(self, stock):
        self.price = float(quote.get_price(stock))
        return self.price
            
analysis = Analysis()
