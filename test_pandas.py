from numpy.core.numeric import NaN
import pandas_datareader as web
import datetime as dt
from datetime import timedelta


# We call this function every 5 minutes
# for now, it is just for crypto buy tables. I will eventually expand it to US markets (VTI and VOO), plus crypto sell tables 
def check_crypto_buy_tables():

    start = dt.datetime.now() - timedelta(days = 1)
    #print(start)
    end = dt.datetime.now()

    btc = web.DataReader('BTC-USD', 'yahoo', start, end)
    #print(btc) # the price we want is today's "close". 
    btc_price = btc.iloc[1][3]


    eth = web.DataReader('ETH-USD', 'yahoo', start, end)
    eth_price = eth.iloc[1][3]

    # We will do the same for VTI and VOO in the future. For now, however, we will focus on Crypto.

    import pandas as pd
    sheet_id = "private" #removed for privacy purposes
    sheet_name = "Buy_Tables"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    buyCSV = pd.read_csv(url)

    #print(pd.read_csv(url))

    # TODO: we will need to create a function that transforms this data into readable/usable data.

    def createBuyEntries(csv):
        listOfBuyEntriesBtc = []
        # step 1: find out how to get all BTC prices
        btc_prices = csv.iloc[:, 0]
        # step 2: find out how to get all BTC fulfillments
        btc_fulfillments = csv.iloc[:, 3]
        # step 3: combine into one list
        for i in range(len(btc_prices)):
            listOfBuyEntriesBtc.append([btc_prices[i], btc_fulfillments[i]])
        # step 4: repeat for ETH
        listOfBuyEntriesEth = []
        
        eth_prices = csv.iloc[:, 5]
        
        eth_fulfillments = csv.iloc[:, 8]
        
        for i in range(len(eth_prices)):
            listOfBuyEntriesEth.append([eth_prices[i], eth_fulfillments[i]])

        return listOfBuyEntriesBtc, listOfBuyEntriesEth

    listOfBtcEntries, listOfEthEntries = createBuyEntries(buyCSV)

    # now, we iterate through each list and check the following things:
    # (1): is price greater than or equal to current price? 
    # (2): is fulfilled NO

    for x in listOfBtcEntries:
        if str(x[0]) ==  "nan":
            break
        new_x = x[0]
        new_x = new_x[1:].replace(",", "")
        if float(new_x) >= float(btc_price) and x[1] == "NO":
            print("SEND PRICE ALERT")

    for x in listOfEthEntries:
        if str(x[0]) ==  "nan":
            break
        new_x = x[0]
        new_x = new_x[1:].replace(",", "")
        if float(new_x) >= float(eth_price) and x[1] == "NO":
            print("SEND PRICE ALERT")