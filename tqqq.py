from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt
import strategy as strat


#start_time_str = '2010-01-01'
#end_time_str = '2021-06-20'
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


'''
initialMoney = 10000000
initialSellRate = 1.15
sellRateStrategyCount = 1
sellRateIncreaseStep = -0.005

#0.59
initialSplitCount = 25.745
splitStrategyCount = 1
splitIncreaseStep = 1.745

delayTradeStrategyCount = 1
delayTradeStep = 1
buyOnDropRatio = 0.41
buyMoreUnderLossRatio = 0.00
losscutRate = 0.98
cashRatio = 0.0
rebalanceInterval = 5
'''
'''
# x 13.5
initialMoney = 10000000
sellRateMiddle = 1.13
sellRateStrategyCount = 41
sellRateIncreaseStep = 0.001
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 3
splitIncreaseStep = 0.05
splitMiddle = 25.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep

delayTradeStrategyCount = 1
delayTradeStep = 1
buyOnDropRatio = 0.41
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0
losscutRate = 1.05
rebalanceInterval = 5
'''


'''
x 12.84
initialMoney = 10000000
sellRateMiddle = 1.13
sellRateStrategyCount = 41
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 3
splitIncreaseStep = 0.05
splitMiddle = 25.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep

delayTradeStrategyCount = 1
delayTradeStep = 1
buyOnDropRatio = 0.41
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 10
losscutIncreaseStep = 0.15 * (1/100)
#losscutMiddle = 1.09
losscutMiddle = 1.05
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 5
'''
'''
# x 11
initialMoney = 10000000
sellRateMiddle = 1.13
sellRateStrategyCount = 41
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 3
splitIncreaseStep = 0.05
splitMiddle = 25.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep

delayTradeStrategyCount = 1
delayTradeStep = 1
buyOnDropRatio = 0.41
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 10
losscutIncreaseStep = 0.3 * (1/100)
#losscutMiddle = 1.09
losscutMiddle = 1.04
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 5
'''
'''
# x 11, mdd 50
initialMoney = 10000000
sellRateMiddle = 1.13
sellRateStrategyCount = 41
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 3
splitIncreaseStep = 0.05
splitMiddle = 25.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep

delayTradeStrategyCount = 1
delayTradeStep = 1
buyOnDropRatio = 0.41
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 10
losscutIncreaseStep = 0.5 * (1/100)
losscutMiddle = 1.04
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 15
'''
'''
mdd 40.3, x 10.27
initialMoney = 10000000
sellRateMiddle = 1.13
sellRateStrategyCount = 35
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
#splitMiddle = 25.745
splitMiddle = 25.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnDropRatioStrategyCount = 1
buyOnDropRatioIncreaseStep = 0.01
buyOnDropRatioMiddle = 0.41
initialbuyOnDropRatio = buyOnDropRatioMiddle - (buyOnDropRatioStrategyCount - 1)/2 * buyOnDropRatioIncreaseStep


delayTradeStrategyCount = 1
delayTradeStep = 1
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 41
losscutIncreaseStep = 0.1 * (1/100)
losscutMiddle = 1.01
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 20
'''
'''
mdd 40.6, x 10.5
initialMoney = 10000000
sellRateMiddle = 1.13
sellRateStrategyCount = 35
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
#splitMiddle = 25.745
splitMiddle = 25.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnDropRatioStrategyCount = 1
buyOnDropRatioIncreaseStep = 0.01
buyOnDropRatioMiddle = 0.41
initialbuyOnDropRatio = buyOnDropRatioMiddle - (buyOnDropRatioStrategyCount - 1)/2 * buyOnDropRatioIncreaseStep


delayTradeStrategyCount = 1
delayTradeStep = 1
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 51
losscutIncreaseStep = 0.8 * (1/100)
losscutMiddle = 1.01
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 30
rebalanceRateAtOnce = 0.13
cash = cashRatio * initialMoney
'''

'''
mdd 39.5 , x 10.35
initialMoney = 10000000
sellRateMiddle = 1.13
sellRateStrategyCount = 35
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
#splitMiddle = 25.745
splitMiddle = 25.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnDropRatioStrategyCount = 1
buyOnDropRatioIncreaseStep = 0.01
buyOnDropRatioMiddle = 0.41
initialbuyOnDropRatio = buyOnDropRatioMiddle - (buyOnDropRatioStrategyCount - 1)/2 * buyOnDropRatioIncreaseStep


delayTradeStrategyCount = 1
delayTradeStep = 1
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 51
losscutIncreaseStep = 0.8 * (1/100)
losscutMiddle = 1.01
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 20
rebalanceRateAtOnce = 0.13
cash = cashRatio * initialMoney
'''

initialMoney = 10000000
sellRateMiddle = 1.13
sellRateStrategyCount = 35
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
#splitMiddle = 25.745
splitMiddle = 25.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnDropRatioStrategyCount = 1
buyOnDropRatioIncreaseStep = 0.01
buyOnDropRatioMiddle = 0.41
initialbuyOnDropRatio = buyOnDropRatioMiddle - (buyOnDropRatioStrategyCount - 1)/2 * buyOnDropRatioIncreaseStep


delayTradeStrategyCount = 1
delayTradeStep = 1
buyMoreUnderLossRatio = 0.00
cashRatio = 0.0


losscutStrategyCount = 51
losscutIncreaseStep = 0.8 * (1/100)
losscutMiddle = 1.01
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 20
rebalanceRateAtOnce = 0.13
cash = cashRatio * initialMoney

for delayTradeStrategyIndex in range (0, delayTradeStrategyCount ):
	for sellRateStrategyIndex in range (0, sellRateStrategyCount ):
		for splitStrategyIndex in range (0, splitStrategyCount ):
			for losscutStrategyIndex in range (0, losscutStrategyCount ):
				for buyOnDropRatioIndex in range (0, buyOnDropRatioStrategyCount ):
					totalStrategyCount = splitStrategyCount * sellRateStrategyCount * delayTradeStrategyCount * losscutStrategyCount * buyOnDropRatioStrategyCount 
					budget = initialMoney * (1.0-cashRatio) / totalStrategyCount 
					splitCount = initialSplitCount + splitStrategyIndex * splitIncreaseStep
					sellRate = initialSellRate + sellRateStrategyIndex * sellRateIncreaseStep 
					buyOnDropRatio = initialbuyOnDropRatio +buyOnDropRatioIndex * buyOnDropRatioIncreaseStep
					delayTrade = delayTradeStrategyIndex * delayTradeStep
					logTrade = False
					losscutRate = initialLosscut + losscutStrategyIndex * losscutIncreaseStep
					strategy.append(
						strat.Strategy(response, 
							budget, 
							splitCount, 
							sellRate, 
							buyOnDropRatio,
							delayTrade, 
							0.0, 
							logTrade, losscutRate))

strategyCount = len(strategy)
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

		strategy[strategyIdx].sell_all_when_done(dayIdx)
		strategy[strategyIdx].buy(dayIdx)
		dailyTotalBudgets += strategy[strategyIdx].budget
		balanceTotal += strategy[strategyIdx].lastBalance

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
		sortedStrategies = sorted(strategy, key=lambda x : x.lastBalance) 	

		#for strategyIdx in range (0, strategyCount):
		#	print(sortedStrategies[strategyIdx].lastBalance)

		for strategyIdx in range (0, strategyCount):
			desire = rebalanceBase - sortedStrategies[strategyIdx].lastBalance
			if(desire < 0):
				break

			counterStrategey = sortedStrategies[strategyCount - strategyIdx - 1]
			amount = counterStrategey.takeBudget( desire * rebalanceRateAtOnce)
			sortedStrategies[strategyIdx].fillBudget(amount)


		#print('---------------after rebalance-----------------------[' + str(dayIdx))
		#for strategyIdx in range (0, strategyCount):
		#	print(sortedStrategies[strategyIdx].lastBalance)

print('---------------finally -----------------------')

for strategyIdx in range (0, strategyCount):
	print(strategy[strategyIdx].lastBalance)
mul = initialMoney/closePrices[0]

#plt.plot(strategy[0].stockData.index, balances, closePrices * mul)

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

	plt.plot(strategy[i].stockData.index, strategy[i].scoreHistory, linestyle=linestyle, label = 'split: '+str(strategy[i].splitCount) +', sell rate: '+ str(strategy[i].sellRate))
'''
for i in range (0, len(investmentRatios)):
	investmentRatios[i] *= balances[-1]

plt.plot(strategy[0].stockData.index, investmentRatios, color='lightskyblue')
plt.plot(strategy[0].stockData.index, balances)
plt.grid(True)


'''
plt.subplot(212)
for i in range (0, strategyCount):
	if(i % 10 == 9):
		for j in range(0, len(strategy[i].balanceHistory)):
			strategy[i].balanceHistory[j] *= strategyCount / 2
		plt.plot(strategy[i].stockData.index, strategy[i].balanceHistory, label = str(i))
'''
#plt.yscale("log",basey=2)

#plt.legend()
plt.grid(True)
plt.show()