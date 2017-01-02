#Tracks Commodities compared to the US Dollar

from bs4 import BeautifulSoup as soup
import requests
import mysql.connector as mysql
import squelch

########################################################################################
#Retrieve Price of Commodities and Dollar
########################################################################################

class priceParser():

    #List of the Commodities I am tracking
    commodityList = [["https://www.bloomberg.com/quote/DXY:CUR", "US Dollar Index"],
                     ["https://www.bloomberg.com/quote/GC1:COM", "Gold"],
                     ["https://www.bloomberg.com/quote/SI1:COM", "Silver"],
                     ["https://www.bloomberg.com/quote/HG1:COM", "Copper"],
                     ["https://www.bloomberg.com/quote/XPTUSD:CUR", "Platinum"],
                     ["https://www.bloomberg.com/quote/XPDUSD:CUR", "Palladium"],
                     ["https://www.bloomberg.com/quote/CL1:COM", "Crude Oil"],
                     ["https://www.bloomberg.com/quote/HO1:COM", "Heating Oil"],
                     ["https://www.bloomberg.com/quote/XB1:COM", "Gas"],
                     ["https://www.bloomberg.com/quote/W%201:COM", "Wheat"],
                     ["https://www.bloomberg.com/quote/C%201:COM", "Corn"],
                     ["https://www.bloomberg.com/quote/S%201:COM", "Soybeans"],
                     ["https://www.bloomberg.com/quote/LC1:COM", "Live Cattle"]]

    #Place holder for the price
    price = ""
    
    #Place holder for our cursor object for db manipulation
    cursor = ""
    database = ""

    #Gets HTML needed from websites
    def requestData(self, website):
    
        connected = False
        
        while connected == False:
            
            try:
                
                data = requests.get(website)
                parse = soup(data.content, "html5lib")
                connected = True
                return parse
            except (TimeoutError, requests.exceptions.ConnectionError, TypeError):
                
                print("Attemping to establish a connection")

    def commaHandler(self):
        #Handle any commas in our strings to prevent ValueError
        self.price = list(self.price)
        
        if "," in self.price:
            self.price.remove(",")
            
        self.price = "".join(self.price)
    
    def connectToDatabase(self, user, password, host, name):

        #Saves our database information to be used for manipulation
        self.database = mysql.connect(user = user,
                                 password = password,
                                 host = host,
                                 database = name)

        self.cursor = self.database.cursor(buffered=True)

    def dollarChange(self):
    
        #Gets the previous closing price of the dollar to compare with
        self.cursor.execute("SELECT closing_price FROM main "
                            "WHERE commodity='US Dollar Index' ")

        update = self.cursor.fetchone()[0]
        
        #Gets a bit sloppy here because I need to compare the dollar before anything else so I get the data again
        data = self.requestData(self.commodityList[0][0])
        dollar = data.find("div", class_ = "price")
        dollar = dollar.get_text()
        
        self.commaHandler()

        if float(dollar) >= update:
            return(True)
        else:
            return(False)

    def compareToDollar(self, number):
        
        self.commaHandler()
        
        #Run the same comparison as we did with the dollar for each stock in the list

        #Grabs the closing price of the dollar
        self.cursor.execute("SELECT closing_price FROM main "
                            "WHERE commodity=%s", (str(self.commodityList[number][1]),))

        update = self.cursor.fetchone()[0]

        #Fetch days increased so we can increment it in the program if necessary
        self.cursor.execute("SELECT days_increased FROM main "
                            "WHERE commodity=%s", (str(self.commodityList[number][1]),))

        days_increased = self.cursor.fetchone()[0]
        days_increased += 1
        
        #fetch total_days so we can increment it in the program
        self.cursor.execute("SELECT total_days FROM main "
                            "WHERE commodity=%s", (str(self.commodityList[number][1]),))

        total_days = self.cursor.fetchone()[0]
        total_days += 1

        #If the price went up we will compare it to how the dollar did
        if float(self.price) >= update and self.dollarChange() == True:
            self.cursor.execute("UPDATE main "
                                "SET days_increased=%s, total_days=%s "
                                "WHERE commodity=%s ", (days_increased, total_days, str(self.commodityList[number][1])))
            
        elif float(self.price) >= update and self.dollarChange() == False:
            self.cursor.execute("UPDATE main "
                                "SET total_days=%s "
                                "WHERE commodity=%s ", (total_days, str(self.commodityList[number][1])))
            
        #If the price went down we will compare it to how the dollar did
        elif float(self.price) < update and self.dollarChange() == False:
            self.cursor.execute("UPDATE main "
                                "SET total_days=%s "
                                "WHERE commodity=%s ", (total_days, str(self.commodityList[number][1])))
            
        elif float(self.price) < update and self.dollarChange() == True:
            self.cursor.execute("UPDATE main "
                                "SET days_increased=%s, total_days=%s "
                                "WHERE commodity=%s ", (days_increased, total_days, str(self.commodityList[number][1])))

        self.database.commit()

    def updateProportion(self, number):

        #Fetch the days increased
        self.cursor.execute("SELECT days_increased FROM main "
                            "WHERE commodity=%s ", (str(self.commodityList[number][1]),))

        daysIncreased = self.cursor.fetchone()[0]

        #Fetch the total days
        self.cursor.execute("SELECT total_days FROM main "
                            "WHERE commodity=%s ", (str(self.commodityList[number][1]),))

        totalDays = self.cursor.fetchone()[0]

        #Finds our current proportion with the new numbers
        proportion = daysIncreased/totalDays

        #Adds it to the database
        self.cursor.execute("UPDATE main "
                            "SET proportion=%s "
                            "WHERE commodity=%s ", (proportion, self.commodityList[number][1]))

        self.database.commit()        
            
    def updateClosingPrice(self, number):

        #Update our table with the new price
        self.commaHandler()
        self.cursor.execute("UPDATE main "
                            "SET closing_price=%s "
                            "WHERE commodity=%s", (float(self.price), self.commodityList[number][1]))

        self.database.commit()

    #Basically our main function call for the update
    def mainFunction(self):
        
        #Connect to database
        self.connectToDatabase(squelch.squelch.db_user,
                              squelch.squelch.db_pass,
                              squelch.squelch.db_host,
                              squelch.squelch.db_name)
        
        for i in range(len(self.commodityList)):
            
            #Calls the HTML request and parses the data
            data = self.requestData(self.commodityList[i][0])
            self.price = data.find("div", class_ = "price")
            self.price = self.price.get_text()
            
            #Updates Database
            self.compareToDollar(i)
            self.updateProportion(i)
            self.updateClosingPrice(i)

        print("Table updated")
        
priceParser = priceParser()

priceParser.mainFunction()




        
        

    

