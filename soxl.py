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

initialMoney = 1000000
splitStrategyCount = 5
sellRateStrategyCount = 1
defaultSplitCount = 25
barrierStrategyCount = 50
for barrierStrategyIndex in range (0, barrierStrategyCount ):
	for sellRateStrategyIndex in range (0, sellRateStrategyCount ):
		for splitStrategyIndex in range (0, splitStrategyCount ):
			strategy.append(
				strat.Strategy(response, 
					initMoney=float(initialMoney)/(splitStrategyCount * sellRateStrategyCount * barrierStrategyCount), 
					splitCount=defaultSplitCount + splitStrategyIndex, 
					sellRate=1.12 + sellRateStrategyIndex * 0.01, 
					buyRatioOnBearMarket=0.5,
					barrier=barrierStrategyIndex * 1))

strategyCount = len(strategy)
for strategyIdx in range (0, strategyCount):
	for dayIdx in range (0, openPrices.size):
		strategy[strategyIdx].trade(dayIdx)

balances = []
for dayIdx in range (0, openPrices.size):
	balanceTotal = 0
	for strategyIdx in range (0, strategyCount):
		balanceTotal += strategy[strategyIdx].balanceHistory[dayIdx]
	balances.append(balanceTotal)

mul = initialMoney/closePrices[0]


plt.plot(strategy[0].stockData.index, balances, closePrices * mul)
#plt.plot(strategy[0].stockData.index, balances)
plt.grid(True)
plt.show()