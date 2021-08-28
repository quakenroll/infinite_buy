from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt

start_time_str = '2016-06-01'
end_time_str = '2021-06-01'
ticker = "TQQQ"

initMoney = 100000
splitCount = 40
sellRate = 1.10
oneMoney = initMoney / splitCount
buyRatioOnBearMarket = 0.5

#response = requests.get(HISTORY_DATA_URL)
response = yf.download(ticker, start=start_time_str, end=end_time_str)
openPrices = response['Open']
closePrices = response['Close']
highPrices = response['High']
response['Date'] = response.index
dates = response['Date']

stockCount = 0
stockMeanValue = 0

def buy_close(close_value, money) :
    global stockCount, stockMeanValue, initMoney

    #print(money)
    c = int(money / close_value)
    stockMeanValue = ( ( stockCount * stockMeanValue ) + (c * close_value ) ) / (stockCount + c)
    stockCount += c

    initMoney -= (close_value * c)

    #print("[BUY ] initMoney(%d) Count(%d) Mean(%f) BUY(%f)" % (initMoney, stockCount, stockMeanValue, close_value))

    if initMoney <= 0:
        return False

    return True

size = closePrices.size

balance = []
isFirst = True
buyIndex = 0
for row in range (0, size):
    if initMoney - oneMoney < 0 :
        initMoney += (stockCount * float(closePrices[row]) )
        oneMoney = initMoney / splitCount
        print("buyIndex(%s) [매도청산] row(%s, %d), initMoney(%d) Count(%d) Mean(%f) SELL(%f)" % (int(buyIndex), dates[row], row, initMoney, stockCount, stockMeanValue, float(closePrices[row])))
        buyIndex = 0
        stockCount = 0
        stockMeanValue = 0
    elif stockMeanValue * sellRate < float(highPrices[row]) :
        initMoney += (stockCount * stockMeanValue * sellRate )
        oneMoney = initMoney / splitCount
        if isFirst == False:
            print("buyIndex(%s) [수익청산] row(%s, %d), initMoney(%d) Count(%d) Mean(%f) SELL(%f)" % (int(buyIndex), dates[row], row, initMoney, stockCount, stockMeanValue, stockMeanValue * sellRate))
        buyIndex = 0
        stockCount = 0
        stockMeanValue = 0
        isFirst = False
        

    buyRatio = buyRatioOnBearMarket
    #buyRatio = buyRatioOnBearMarket - ((splitCount-buyIndex)/10.0/splitCount)
    if stockMeanValue < float(closePrices[row]) :
        sucess = buy_close(float(closePrices[row]), oneMoney * buyRatio)
        if sucess == True:
            buyIndex += buyRatio

    buyRatio = 1.0 - buyRatioOnBearMarket
    #buyRatio = 1.0 - buyRatioOnBearMarket - ((splitCount-buyIndex)/10.0/splitCount)

    sucess = buy_close(float(closePrices[row]), oneMoney  * buyRatio )
    if sucess == True:
        buyIndex += buyRatio

    curBalance = ( closePrices[row] * stockCount + initMoney )
    balance.append( curBalance )

print (curBalance)
plt.plot(response.index, balance)

plt.show()