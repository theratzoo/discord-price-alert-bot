import discord
from numpy.core.numeric import NaN
import pandas_datareader as web
import datetime as dt
from datetime import timedelta
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

client = discord.Client() # starts the discord client.

AUTH_TOKEN = os.getenv('AUTH_TOKEN')
SHEET_ID_CRYPTO_BUY = os.getenv('SHEET_ID_CRYPTO_BUY')

mins = 5 #how many minutes between refreshes

lastRefresh = dt.datetime.now()

@client.event
async def on_message(message):
    global lastRefresh
    if message.content.startswith('!status'):
        timeDelta = dt.datetime.now() - lastRefresh
        msg = "Online! Last price check was " + str(timeDelta.seconds / 60) + " minutes ago"
        await message.channel.send(msg)
    # Ideas for more commands:
    # help commander to list commands
    # timing to tell us how often it fetches new data
    # history, which shows history of price alerts
    # we can also make this bot give us real-time data on BTC, ETH, etc pricing if we want.

    #TODO: make it so it can ONLY send messages if used in the right channel!

# We call this function every 5 minutes
# for now, it is just for crypto buy tables. I will eventually expand it to US markets (VTI and VOO), plus crypto sell tables 
from discord.ext import commands, tasks
@tasks.loop(seconds=60*mins)
async def check_crypto_buy_tables():

    start = dt.datetime.now() - timedelta(days = 1)
    #print(start)
    end = dt.datetime.now()

    btc = web.DataReader('BTC-USD', 'yahoo', start, end)

    #print(btc) # the price we want is today's "close".
    btc_price = btc.iloc[len(btc)-1][3]

    eth = web.DataReader('ETH-USD', 'yahoo', start, end)
    eth_price = eth.iloc[len(eth)-1][3]

    # We will do the same for VTI and VOO in the future. For now, however, we will focus on Crypto.
    
    sheet_id = SHEET_ID_CRYPTO_BUY
    sheet_name = "Buy_Tables"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    buyCSV = pd.read_csv(url)

    #print(pd.read_csv(url))
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
            channel = client.get_channel(911349581667790889)
            format_str = "BTC is currently at " + btc_price + ", which is below one of the table entry's price ceiling of " + x[0]
            await channel.send(format_str)

    for x in listOfEthEntries:
        if str(x[0]) ==  "nan":
            break
        new_x = x[0]
        new_x = new_x[1:].replace(",", "")
        if float(new_x) >= float(eth_price) and x[1] == "NO":
            channel = client.get_channel(911349581667790889)
            format_str = "ETH is currently at " + eth_price + ", which is below one of the table entry's price ceiling of " + x[0]
            await channel.send(format_str)
    global lastRefresh
    lastRefresh = dt.datetime.now()

#TODO ASAP: make a sell table version which should b super simple
#we should make dummy data first though if we dont have the actual table made lol

@client.event 
async def on_ready():
    print(f'Successful Launch!!! {client.user}') 
    check_crypto_buy_tables.start()

client.run(AUTH_TOKEN) # Pull Auth Token from above