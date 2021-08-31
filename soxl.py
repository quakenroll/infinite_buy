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
initialSellRate = 1.12
sellRateStrategyCount = 1
sellRateIncreaseStep = 0.01

initialSplitCount = 25
splitStrategyCount = 5
splitIncreaseStep = 1.745

delayTradeStrategyCount = 1
delayTradeStep = 1
buyOnDropRatio = 0.5
buyMoreUnderLossRatio = 0.00


for delayTradeStrategyIndex in range (0, delayTradeStrategyCount ):
	for sellRateStrategyIndex in range (0, sellRateStrategyCount ):
		for splitStrategyIndex in range (0, splitStrategyCount ):
			strategy.append(
				strat.Strategy(response, 
					budget=float(initialMoney)/(splitStrategyCount * sellRateStrategyCount * delayTradeStrategyCount), 
					splitCount=initialSplitCount + splitStrategyIndex * splitIncreaseStep, 
					sellRate=initialSellRate+ sellRateStrategyIndex * sellRateIncreaseStep, 
					buyOnDropRatio=buyOnDropRatio,
					delayTrade=delayTradeStrategyIndex * delayTradeStep, 
					buyMoreUnderLossRatio=buyMoreUnderLossRatio, 
					logTrade=False))

strategyCount = len(strategy)
balances = []
rebalance = True
winnerTakesItAll = True

for dayIdx in range (0, openPrices.size):
	balanceTotal = 0
	for strategyIdx in range (0, strategyCount):

		strategy[strategyIdx].sell_all_when_done(dayIdx)
		strategy[strategyIdx].buy(dayIdx)


		balanceTotal += strategy[strategyIdx].lastBalance

	balances.append(balanceTotal)

	if rebalance == False:
		continue


	if(dayIdx % 300 == 299):
		if(winnerTakesItAll == True):
			rebalanceBase = balanceTotal/strategyCount
			sortedStrategies = sorted(strategy, key=lambda x : x.score * -1) 	

			print('---------------prev  rebalance-----------------------[' + str(dayIdx), 'rebalance', str(rebalanceBase))
			for strategyIdx in range (0, strategyCount):
				print(sortedStrategies[strategyIdx].lastBalance, sortedStrategies[strategyIdx].score)

			for strategyIdx in range (0, strategyCount):
				winner = sortedStrategies[strategyIdx]

				for i in range(strategyIdx + 1, strategyCount - strategyIdx - 1):
					amount = sortedStrategies[i].takeBudget(rebalanceBase * 0.005)
					winner.fillBudget(amount)

			print('---------------after rebalance-----------------------[' + str(dayIdx))
			for strategyIdx in range (0, strategyCount):
				print(sortedStrategies[strategyIdx].lastBalance, sortedStrategies[strategyIdx].score)

		else:
			rebalanceBase = balanceTotal/strategyCount
			sortedStrategies = sorted(strategy, key=lambda x : x.lastBalance) 	

			print('---------------prev  rebalance-----------------------[' + str(dayIdx), 'rebalance', str(rebalanceBase))
			for strategyIdx in range (0, strategyCount):
				print(sortedStrategies[strategyIdx].lastBalance)

			for strategyIdx in range (0, strategyCount):
				desire = rebalanceBase - sortedStrategies[strategyIdx].lastBalance
				if(desire < 0):
					break

				counterStrategey = sortedStrategies[strategyCount - strategyIdx - 1]
				amount = counterStrategey.takeBudget( desire * 0.05)
				sortedStrategies[strategyIdx].fillBudget(amount)


			print('---------------after rebalance-----------------------[' + str(dayIdx))
			for strategyIdx in range (0, strategyCount):
				print(sortedStrategies[strategyIdx].lastBalance)


print('---------------finally -----------------------')

for strategyIdx in range (0, strategyCount):
	print(strategy[strategyIdx].lastBalance)
mul = initialMoney/closePrices[0]

#plt.plot(strategy[0].stockData.index, balances, closePrices * mul)
#plt.plot(strategy[0].stockData.index, balances)


for i in range (0, strategyCount):
	plt.plot(strategy[i].stockData.index, strategy[i].balanceHistory, label = str(i))
#plt.yscale("log",basey=2)

plt.legend()
plt.grid(True)
plt.show()