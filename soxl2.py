from os import curdir
import yfinance as yf
import time
import datetime
import math
import matplotlib.pyplot as plt
import strategy as strat


#start_time_str = '2016-01-01'
#end_time_str = '2021-06-20'
start_time_str = '2016-01-01'
end_time_str = '2021-08-30'
ticker = "SOXL"
tickerHedge = "TLT"

#response = requests.get(HISTORY_DATA_URL)
response = yf.download(ticker, start=start_time_str, end=end_time_str)
openPrices = response['Open']
closePrices = response['Close']

responseHedge = yf.download(tickerHedge, start=start_time_str, end=end_time_str)

strategies = []

'''
#mdd = 0.407, x 19.5
start_time_str = '2016-01-01'
end_time_str = '2021-08-30'
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
hedgeRatio = 0.


losscutStrategyCount = 41
losscutIncreaseStep = 0.5 * (1/100)
losscutMiddle = 1.03
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceRateAtOnce = 0.1
rebalanceInterval = 40
mainAssetToHedgeInterval = 1
hedgetToMainAssetInterval = 1

rebalanceRateAtOnce = 0.1
mainAssetToHedgeRebalanceRateAtOnce = 0.05
hedgeToMainAssetRebalanceRateAtOnce = 1
'''

initialMoney = 10000000
sellRateMiddle = 1.11
sellRateStrategyCount = 35
sellRateIncreaseStep = 0.1 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
#splitMiddle = 25.745
splitMiddle = 26.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnRiseRatioStrategyCount = 1
buyOnRiseRatioIncreaseStep = 0.01
buyOnRiseRatioMiddle = 0.41
initialbuyOnRiseRatio = buyOnRiseRatioMiddle - (buyOnRiseRatioStrategyCount - 1)/2 * buyOnRiseRatioIncreaseStep


delayTradeStrategyCount = 1
delayTradeStep = 1
buyMoreUnderLossRatio = 0.00
hedgeRatio = 0.0


losscutStrategyCount = 41
losscutIncreaseStep = 0.5 * (1/100)
losscutMiddle = 1.03
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceInterval = 40
mainAssetToHedgeInterval = 1
hedgetToMainAssetInterval = 1

rebalanceRateAtOnce = 0.1
mainAssetToHedgeRebalanceRateAtOnce = 0.05
hedgeToMainAssetRebalanceRateAtOnce = 1


hedge = hedgeRatio * initialMoney
totalStrategyCount = splitStrategyCount * sellRateStrategyCount * delayTradeStrategyCount * losscutStrategyCount * buyOnRiseRatioStrategyCount 
budget = initialMoney * (1.0-hedgeRatio) / totalStrategyCount 

##########################################################################################
# hedgeStrategy
initialHedgeMoney = initialMoney * (hedgeRatio)
hedgeStrategyCount = int(initialHedgeMoney / budget)
hedgeStrategies = []
for i in range (0, hedgeStrategyCount ):
	s = strat.Strategy(stockData=responseHedge, 
				budget=budget, 
				splitCount=10, 
				profitRate=1000, 
				buyOnRiseRatio=0,
				delayTrade=0, 
				buyMoreUnderLossRatio =0,
				logTrade=False, name='hedge')
	hedgeStrategies.append(s)



##########################################################################################

for delayTradeStrategyIndex in range (0, delayTradeStrategyCount ):
	for sellRateStrategyIndex in range (0, sellRateStrategyCount ):
		for splitStrategyIndex in range (0, splitStrategyCount ):
			for losscutStrategyIndex in range (0, losscutStrategyCount ):
				for buyOnRiseRatioIndex in range (0, buyOnRiseRatioStrategyCount ):
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

mainAssetInvestmentRatios = []
investmentAmount = 0
highestBalance = 0
reservedRebalance = 0
rebalanceHedge =  True
hedgeRebalancingWaitUntil = 1
reservedBudgetForRebalance = 0
mainAssetBalances = []
hedgeAssetBalances = []
hedgeRebalanceCount = 0
consecutiveHedgeToMainRevCount = 0
hedgeRebalanceHistory = []
for dayIdx in range (0, openPrices.size):
	balanceTotal = 0
	mainAssetTotalBudgets = 0
	mainAssetBalanceTotal = 0
	hedgeAssetBalanceTotal = 0

	if(reservedBudgetForRebalance > 0):
		for sss in range(0, strategyCount):
			strategies[sss].fill_budget(reservedBudgetForRebalance / strategyCount)
		reservedBudgetForRebalance = 0

	for si in range (0, strategyCount):
		strategies[si].sell_all_when_done(dayIdx)
		strategies[si].buy(dayIdx)
		strategies[si].post_trade(dayIdx)
		mainAssetTotalBudgets += strategies[si].budget
		mainAssetBalanceTotal += strategies[si].lastBalance

	balanceTotal = mainAssetBalanceTotal
	for hi in range (0, hedgeStrategyCount):
		hedgeStrategies[hi].sell_all_when_done(dayIdx)
		hedgeStrategies[hi].buy(dayIdx)
		hedgeStrategies[hi].resetBuyProgress()
		hedgeStrategies[hi].post_trade(dayIdx)
		hedgeAssetBalanceTotal += hedgeStrategies[hi].lastBalance

	balanceTotal = hedgeAssetBalanceTotal + mainAssetBalanceTotal
	balances.append(balanceTotal)

	ratio = mainAssetTotalBudgets/balanceTotal
	assert(ratio >= -0.1)
	mainAssetInvestmentRatios.append(1 - ratio)
	mainAssetBalances.append(mainAssetBalanceTotal)
	hedgeAssetBalances.append(hedgeAssetBalanceTotal)

	hedgeAssetRatio = hedgeAssetBalanceTotal / balanceTotal

	if rebalanceHedge == True  :
		amount = 0
		if( hedgeAssetRatio < hedgeRatio * 1.25 ): #현재 헷지가 기준치 미달이라면
			if(dayIdx % mainAssetToHedgeInterval) == (mainAssetToHedgeInterval - 1):
					#if(hedgeRebalancingWaitUntil < 1.0):
					#	hedgeRebalancingWaitUntil *= 1.02
					#else:
						insufficientAmount = (hedgeRatio - hedgeAssetRatio) * balanceTotal * mainAssetToHedgeRebalanceRateAtOnce
						amount = 0
						for sss in range(0, strategyCount):
							amount += strategies[sss].transfer_budget(insufficientAmount / strategyCount)
						
						for hhh in range(0, hedgeStrategyCount):
							hedgeStrategies[hhh].fill_budget(amount / hedgeStrategyCount)


						if( consecutiveHedgeToMainRevCount  > 0):
							print('enter main to hedge: consecutiveHedgeRevCount(' + str(consecutiveHedgeToMainRevCount))
						
						consecutiveHedgeToMainRevCount = 0

		elif( hedgeAssetRatio > hedgeRatio * 0.75 ): #현재 헷지가 기준치 초과라면
			if(dayIdx % hedgetToMainAssetInterval) == (hedgetToMainAssetInterval - 1):
				desireTotal = hedgeAssetBalanceTotal*(math.pow(1.1, consecutiveHedgeToMainRevCount) *0.03)
				amount = desireTotal / hedgeStrategyCount
				for hhh in range(0, hedgeStrategyCount):
					hedgeStrategies[hhh].reserve_budget_at_close(dayIdx, amount)

				for hhh in range(0, hedgeStrategyCount):
					reservedBudgetForRebalance += hedgeStrategies[hhh].transfer_budget(amount)

				consecutiveHedgeToMainRevCount += 1
				newHedgeRatio = (hedgeAssetBalanceTotal - reservedBudgetForRebalance) / balanceTotal
				hedgeRebalancingWaitUntil *= 0.9
				print('enter hedge to main, revAmount: ', str(math.pow(1.1, consecutiveHedgeToMainRevCount) *0.03))

		

	if(highestBalance < balanceTotal):
		highestBalance = balanceTotal

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

			taker = sortedStrategies[strategyIdx]
			giver = sortedStrategies[strategyCount - strategyIdx - 1]
			amount = giver.transfer_budget( desire * rebalanceRateAtOnce)
			taker.fill_budget(amount)


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
for i in range (0, len(mainAssetInvestmentRatios)):
	mainAssetInvestmentRatios[i] *= balances[-1]

plt.plot(strategies[0].stockData.index, mainAssetInvestmentRatios, color='lightskyblue')
plt.plot(strategies[0].stockData.index, balances)
plt.grid(True)





plt.plot(strategies[i].stockData.index, mainAssetBalances, label = str(i))
plt.plot(strategies[i].stockData.index, hedgeAssetBalances, label = str(i))


#plt.yscale("log",basey=2)

#plt.legend()
plt.grid(True)
plt.show()