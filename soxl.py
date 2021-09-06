from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt
import strategy as strat


#start_time_str = '2010-01-01'
#end_time_str = '2021-06-20'
start_time_str = '2016-01-01'
end_time_str = '2021-08-28'
ticker = "SOXL"

#response = requests.get(HISTORY_DATA_URL)
response = yf.download(ticker, start=start_time_str, end=end_time_str)
openPrices = response['Open']
closePrices = response['Close']
highPrices = response['High']
response['Date'] = response.index
dates = response['Date']

strategies = []


initialMoney = 10000000
sellRateMiddle = 1.11
sellRateStrategyCount = 35
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
splitMiddle = 26.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnRiseRatioStrategyCount = 1
buyOnRiseRatioIncreaseStep = 0.01
buyOnRiseRatioMiddle = 0.41
initialbuyOnRiseRatio = buyOnRiseRatioMiddle - (buyOnRiseRatioStrategyCount - 1)/2 * buyOnRiseRatioIncreaseStep


delayTradeStrategyCount = 1
delayTradeStep = 1
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 41
losscutIncreaseStep = 0.5 * (1/100)
losscutMiddle = 1.03
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 40
rebalanceRateAtOnce = 0.1
cash = cashRatio * initialMoney
'''
mdd = 0.407, x 19
initialMoney = 10000000
sellRateMiddle = 1.11
sellRateStrategyCount = 35
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
splitMiddle = 26.745
#splitMiddle = 16.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnRiseRatioStrategyCount = 1
buyOnRiseRatioIncreaseStep = 0.01
buyOnRiseRatioMiddle = 0.41
initialbuyOnRiseRatio = buyOnRiseRatioMiddle - (buyOnRiseRatioStrategyCount - 1)/2 * buyOnRiseRatioIncreaseStep


delayTradeStrategyCount = 1
delayTradeStep = 1
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 41
losscutIncreaseStep = 0.5 * (1/100)
losscutMiddle = 1.03
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 22
rebalanceRateAtOnce = 0.1
cash = cashRatio * initialMoney
'''

initialMoney = 10000000
#sellRateMiddle = 1.13
sellRateMiddle = 1.11
sellRateStrategyCount = 35
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
splitMiddle = 26.745
#splitMiddle = 16.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnRiseRatioStrategyCount = 1
buyOnRiseRatioIncreaseStep = 0.01
buyOnRiseRatioMiddle = 0.41
initialbuyOnRiseRatio = buyOnRiseRatioMiddle - (buyOnRiseRatioStrategyCount - 1)/2 * buyOnRiseRatioIncreaseStep


delayTradeStrategyCount = 1
delayTradeStep = 1
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 41
losscutIncreaseStep = 0.5 * (1/100)
losscutMiddle = 1.03
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 22
rebalanceRateAtOnce = 0.1
cash = cashRatio * initialMoney

for delayTradeStrategyIndex in range (0, delayTradeStrategyCount ):
	for sellRateStrategyIndex in range (0, sellRateStrategyCount ):
		for splitStrategyIndex in range (0, splitStrategyCount ):
			for losscutStrategyIndex in range (0, losscutStrategyCount ):
				for buyOnRiseRatioIndex in range (0, buyOnRiseRatioStrategyCount ):
					totalStrategyCount = splitStrategyCount * sellRateStrategyCount * delayTradeStrategyCount * losscutStrategyCount * buyOnRiseRatioStrategyCount 
					budget = initialMoney * (1.0-cashRatio) / totalStrategyCount 
					splitCount = initialSplitCount + splitStrategyIndex * splitIncreaseStep
					profitRate = initialSellRate + sellRateStrategyIndex * sellRateIncreaseStep 
					buyOnRiseRatio = initialbuyOnRiseRatio +buyOnRiseRatioIndex * buyOnRiseRatioIncreaseStep
					delayTrade = delayTradeStrategyIndex * delayTradeStep
					logTrade = False
					minimumLosscutRate = initialLosscut + losscutStrategyIndex * losscutIncreaseStep
					strategies.append(
						strat.Strategy(response, 
							budget, 
							splitCount, 
							profitRate, 
							buyOnRiseRatio,
							delayTrade, 
							0.0, 
							logTrade, minimumLosscutRate))

strategyCount = len(strategies)
balances = []
rebalance = True
winnerTakesItAll = False

investmentRatios = []
investmentAmount = 0
highestBalance = 0
for dayIdx in range (0, openPrices.size):
	balanceTotal = 0
	dailyTotalBudgets = 0
	for strategyIdx in range (0, strategyCount):

		strategies[strategyIdx].sell_all_when_done(dayIdx)
		strategies[strategyIdx].buy(dayIdx)
		dailyTotalBudgets += strategies[strategyIdx].budget
		balanceTotal += strategies[strategyIdx].lastBalance

	balances.append(balanceTotal + cash)

	ratio = (dailyTotalBudgets)/(balanceTotal + cash)
	assert(ratio >= -0.1)
	investmentRatios.append(1 - ratio)


	if(highestBalance < balanceTotal + cash):
		highestBalance = balanceTotal + cash



	if rebalance == False:
		continue


	if(dayIdx % rebalanceInterval == (rebalanceInterval-1)):
		rebalanceBase = balanceTotal/strategyCount
		sortedStrategies = sorted(strategies, key=lambda x : x.lastBalance) 	

		#for strategyIdx in range (0, strategyCount):
		#	print(sortedStrategies[strategyIdx].lastBalance)

		for strategyIdx in range (0, strategyCount):
			desire = rebalanceBase - sortedStrategies[strategyIdx].lastBalance
			if(desire < 0):
				break

			counterStrategey = sortedStrategies[strategyCount - strategyIdx - 1]
			amount = counterStrategey.transfer_budget( desire * rebalanceRateAtOnce)
			sortedStrategies[strategyIdx].fill_budget(amount)


		#print('---------------after rebalance-----------------------[' + str(dayIdx))
		#for strategyIdx in range (0, strategyCount):
		#	print(sortedStrategies[strategyIdx].lastBalance)

print('---------------finally -----------------------')

for strategyIdx in range (0, strategyCount):
	print(strategies[strategyIdx].lastBalance)
mul = initialMoney/closePrices[0]

#plt.plot(strategies[0].stockData.index, balances, closePrices * mul)

profitRatio = balances[-1]/initialMoney


#plt.subplot(211)

yticks = []
for i in range(0, 50):
	yticks.append(initialMoney*i)
plt.yticks(yticks)

'''
for i in range (0, strategyCount):
	if( i < strategyCount / 2):
		linestyle = '--'
	else:
		linestyle = 'dotted'

	plt.plot(strategies[i].stockData.index, strategies[i].scoreHistory, linestyle=linestyle, label = 'split: '+str(strategies[i].splitCount) +', sell rate: '+ str(strategies[i].profitRate))
'''
for i in range (0, len(investmentRatios)):
	investmentRatios[i] *= balances[-1]

plt.plot(strategies[0].stockData.index, investmentRatios, color='lightskyblue')
plt.plot(strategies[0].stockData.index, balances)
plt.grid(True)


'''
plt.subplot(212)
for i in range (0, strategyCount):
	if(i % 10 == 9):
		for j in range(0, len(strategies[i].balanceHistory)):
			strategies[i].balanceHistory[j] *= strategyCount / 2
		plt.plot(strategies[i].stockData.index, strategies[i].balanceHistory, label = str(i))
'''
#plt.yscale("log",basey=2)

#plt.legend()
plt.grid(True)
plt.show()