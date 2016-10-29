#Controller for running the Webscraper
#Run threads of the scraper
#If the threads start moving slower than 5 seconds, close, and then reopen

import subprocess
import time
class Monitor():
    
    run = False

def runMonitor():
    subprocess.call(['python.exe', "C:\\Users\\Grant\\Desktop\\Programs\\StockWebpage\\TwitterMoney.pyw"])

monitor = Monitor()

while True:
    runMonitor()
