from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt
import strategy as strat

start_time_str = '2016-01-01'
end_time_str = '2021-06-20'
ticker = "TQQQ"

#response = requests.get(HISTORY_DATA_URL)
response = yf.download(ticker, start=start_time_str, end=end_time_str)
openPrices = response['Open']
closePrices = response['Close']
highPrices = response['High']
response['Date'] = response.index
dates = response['Date']

strategy = []

initialMoney = 2000000
initialSellRate = 1.15
sellRateStrategyCount = 2
sellRateIncreaseStep = 0.025


#0.59
initialSplitCount = 24
splitStrategyCount = 4
splitIncreaseStep = 1.745

barrierStrategyCount = 1
buyRatioOnBearMarket = 0.41
for barrierStrategyIndex in range (0, barrierStrategyCount ):
	for sellRateStrategyIndex in range (0, sellRateStrategyCount ):
		for splitStrategyIndex in range (0, splitStrategyCount ):
			strategy.append(
				strat.Strategy(response, 
					initMoney=float(initialMoney)/(splitStrategyCount * sellRateStrategyCount * barrierStrategyCount), 
					splitCount=initialSplitCount + splitStrategyIndex * splitIncreaseStep, 
					sellRate=initialSellRate+ sellRateStrategyIndex * sellRateIncreaseStep, 
					buyRatioOnBearMarket=buyRatioOnBearMarket,
					barrier=barrierStrategyIndex * 1, logTrade=False))

strategyCount = len(strategy)
balances = []
for dayIdx in range (0, openPrices.size):
	balanceTotal = 0
	for strategyIdx in range (0, strategyCount):
		strategy[strategyIdx].trade(dayIdx)
		balanceTotal += strategy[strategyIdx].balanceHistory[dayIdx]

	balances.append(balanceTotal)

	#if(dayIdx % 200):
	#	rebalance = balanceTotal/strategyCount
	#	for strategyIdx in range (0, strategyCount):
	#		curBalance = strategy[strategyIdx].balanceHistory[dayIdx]


mul = initialMoney/closePrices[0]

#plt.plot(strategy[0].stockData.index, balances, closePrices * mul)
plt.plot(strategy[0].stockData.index, balances)
plt.grid(True)
plt.show()