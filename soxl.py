from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt
import strategy as strat

#start_time_str = '2020-03-01'
#end_time_str = '2021-08-20'

start_time_str = '2018-01-01'
end_time_str = '2021-08-20'


ticker = "SOXL"
tickerRev1 = "SOXX"

#response = requests.get(HISTORY_DATA_URL)
response = yf.download(ticker, start=start_time_str, end=end_time_str)
openPrices = response['Open']
closePrices = response['Close']
highPrices = response['High']
response['Date'] = response.index
dates = response['Date']

strategy = []


initialMoney = 2000000
initialSellRate = 1.12
sellRateStrategyCount = 1
sellRateIncreaseStep = 0.01

initialSplitCount = 25
splitStrategyCount = 5
splitIncreaseStep = 1.745

barrierStrategyCount = 1
barrierStep = 1
buyRatioOnBearMarket = 0.5
buyMoreUnderLossPercentage = 0.00


for barrierStrategyIndex in range (0, barrierStrategyCount ):
	for sellRateStrategyIndex in range (0, sellRateStrategyCount ):
		for splitStrategyIndex in range (0, splitStrategyCount ):
			strategy.append(
				strat.Strategy(response, 
					budget=float(initialMoney)/(splitStrategyCount * sellRateStrategyCount * barrierStrategyCount), 
					splitCount=initialSplitCount + splitStrategyIndex * splitIncreaseStep, 
					sellRate=initialSellRate+ sellRateStrategyIndex * sellRateIncreaseStep, 
					buyRatioOnBearMarket=buyRatioOnBearMarket,
					barrier=barrierStrategyIndex * barrierStep, 
					buyMoreUnderLossPercentage = buyMoreUnderLossPercentage,
					logTrade=False))

strategyCount = len(strategy)
balances = []
for dayIdx in range (0, openPrices.size):
	balanceTotal = 0
	for strategyIdx in range (0, strategyCount):
		strategy[strategyIdx].sell_all_when_done(dayIdx)
		strategy[strategyIdx].buy(dayIdx)
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