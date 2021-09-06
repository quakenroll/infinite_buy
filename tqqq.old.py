from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt
import strategy as strat

start_time_str = '2018-08-28'
end_time_str = '2020-05-21'
ticker = "TQQQ"

#response = requests.get(HISTORY_DATA_URL)
response = yf.download(ticker, start=start_time_str, end=end_time_str)
openPrices = response['Open']
closePrices = response['Close']
highPrices = response['High']
response['Date'] = response.index
dates = response['Date']

strategies = []

initialMoney = 1000000
splitStrategyCount = 5
sellRateStrategyCount = 1
defaultSplitCount = 20
delayTradeStrategyCount = 80
for delayTradeStrategyIndex in range (0, delayTradeStrategyCount ):
	for sellRateStrategyIndex in range (0, sellRateStrategyCount ):
		for splitStrategyIndex in range (0, splitStrategyCount ):
			strategies.append(
				strat.Strategy(response, 
					initMoney=float(initialMoney)/(splitStrategyCount * sellRateStrategyCount * delayTradeStrategyCount), 
					splitCount=defaultSplitCount + splitStrategyIndex, 
					profitRate=1.10 + sellRateStrategyIndex * 0.015, 
					bearMarketbuyRatio=0.5, 
					delayTrade=delayTradeStrategyIndex * 1))

for strategyIdx in range (0, len(strategies)):
	for dayIdx in range (0, openPrices.size):
		strategies[strategyIdx].trade(dayIdx)

balances = []
for dayIdx in range (0, openPrices.size):
	balanceTotal = 0
	for strategyIdx in range (0, len(strategies)):
		balanceTotal += strategies[strategyIdx].lastBalance
	balances.append(balanceTotal)

mul = initialMoney/closePrices[0]

plt.plot(strategies[0].stockData.index, balances, closePrices * mul)
#plt.plot(strategies[0].stockData.index, balances)
plt.grid(True)
plt.show()