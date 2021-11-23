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
        #TODO: fix this so that it rounds properly
        await message.channel.send(msg)
    #TODO: make this be more universal (!price {symbol}), where symbol is either a crypto converted or a stock
    # also make the message be "BTC: $56,900".
    if message.content.startswith('!priceBTC'):
        await message.channel.send(getPrice('BTC-USD'))
    if message.content.startswith('!priceETH'):
        await message.channel.send(getPrice('ETH-USD'))
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

    btc_price = getPrice('BTC-USD')
    eth_price = getPrice('ETH-USD')

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
    #print("test", listOfBtcEntries)
    for x in listOfBtcEntries:
        if str(x[0]) ==  "nan":
            continue
        new_x = x[0]
        new_x = new_x[1:].replace(",", "")
        #print(new_x, btc_price, x[1])
        if float(new_x) >= float(btc_price) and x[1] == "NO":
            channel = client.get_channel(911349581667790889)
            format_str = "BTC is currently at " + str(btc_price) + ", which is below one of the table entry's price ceiling of " + str(x[0])
            await channel.send(format_str)

    for x in listOfEthEntries:
        if str(x[0]) ==  "nan":
            continue
        new_x = x[0]
        new_x = new_x[1:].replace(",", "")
        if float(new_x) >= float(eth_price) and x[1] == "NO":
            channel = client.get_channel(911349581667790889)
            format_str = "ETH is currently at " + str(eth_price) + ", which is below one of the table entry's price ceiling of " + str(x[0])
            await channel.send(format_str)
    global lastRefresh
    lastRefresh = dt.datetime.now()

#TODO ASAP: make a sell table version which should b super simple
#we should make dummy data first though if we dont have the actual table made lol


# works for BTC-USD and VOO
def getPrice(asset_name):
    start = dt.datetime.now() - timedelta(days = 1)
    #print(start)
    end = dt.datetime.now()
    asset = web.DataReader(asset_name, 'yahoo', start, end)

    #print(asset) # the price we want is today's "close".
    price = asset.iloc[len(asset)-1][3]
    #print(price)

    return price

@client.event 
async def on_ready():
    print(f'Successful Launch!!! {client.user}') 
    check_crypto_buy_tables.start()

client.run(AUTH_TOKEN) # Pull Auth Token from above