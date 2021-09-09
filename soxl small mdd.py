from os import curdir
import yfinance as yf
import backtrader as bt
from datetime import datetime
import matplotlib.pyplot as plt
import strategy as strat
import math

start_time_str = '2016-01-01'
end_time_str = '2021-08-31'
#start_time_str = '2010-03-17'
#end_time_str = '2013-09-30'
ticker = "SOXL"
tickerHedge = "SOXL"
tickerHedge2 = "SOXL"
ticker2 = "SOXX"

#response = requests.get(HISTORY_DATA_URL)
response = yf.download(ticker, start=start_time_str, end=end_time_str)
response2 = yf.download(ticker2, start=start_time_str, end=end_time_str)
openPrices = response['Open']
closePrices = response['Close']
closePrices2 = response2['Close']

responseHedge = yf.download(tickerHedge, start=start_time_str, end=end_time_str)
responseHedge2 = yf.download(tickerHedge2, start=start_time_str, end=end_time_str)

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
losscutMiddle = 0.93
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep
rebalanceRateAtOnce = 0.1
rebalanceInterval = 40
mainAssetToHedgeInterval = 1
hedgetToMainAssetInterval = 1

rebalanceRateAtOnce = 0.1
mainAssetToHedgeRebalanceRateAtOnce = 0.05
hedgeToMainAssetRebalanceRateAtOnce = 1
'''

initialMoney = 100000000
sellRateMiddle = 1.11
sellRateStrategyCount = 7
sellRateIncreaseStep = 0.5 * (1/100)
initialSellRate = sellRateMiddle - (sellRateStrategyCount - 1)/2 * sellRateIncreaseStep

splitStrategyCount = 1
splitIncreaseStep = 0.5
splitMiddle = 26.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep

buyOnRiseRatioStrategyCount = 5
buyOnRiseRatioIncreaseStep = 0.001
buyOnRiseRatioMiddle = 0.412
initialbuyOnRiseRatio = buyOnRiseRatioMiddle - (buyOnRiseRatioStrategyCount - 1)/2 * buyOnRiseRatioIncreaseStep


delayTradeStrategyCount = 10
delayTradeStep = 15
buyMoreUnderLossRatio = 0.00

initialHedgeRatio = 0.05
destHedgeRatio = 0.05
hedgeRatioDecreaseTerm = 120
hedgeDecreaseStep = (initialHedgeRatio - destHedgeRatio)/hedgeRatioDecreaseTerm
hedgeRatio = initialHedgeRatio


losscutStrategyCount = 1
losscutIncreaseStep = 0.5 * (1/100)
losscutMiddle = 1.0
#losscutMiddle = 1.03
initialLosscut = losscutMiddle - (losscutStrategyCount - 1)/2 * losscutIncreaseStep

rebalanceInterval = 40
mainAssetToHedgeInterval = 1
hedgetToMainAssetInterval = 1
rebalanceRateAtOnce = 0.1
mainAssetToHedgeRebalanceRateAtOnce = 0.1
hedgeToMainAssetRebalanceRateAtOnce = 0.05


hedge = hedgeRatio * initialMoney
totalStrategyCount = splitStrategyCount * sellRateStrategyCount * delayTradeStrategyCount * losscutStrategyCount * buyOnRiseRatioStrategyCount 
budget = initialMoney * (1.0-hedgeRatio) / totalStrategyCount 

rebalance = True
rebalanceHedge =  True


sell_trade_list = [None]*len(closePrices)
buy_trade_list = [None]*len(closePrices)
hedge_sell_trade_list = [None]*len(closePrices)
hedge_buy_trade_list = [None]*len(closePrices)

def store_trade_data(dest, index, price, count):
	price = int(price * 100)
	price=price/100

	if dest[index] is None:
		dictItem = {price: count}
		dest[index] = dictItem
	else:
		price_and_count = dest[index]
		if price in price_and_count:
			price_and_count[price] += count
		else:
			price_and_count[price] = count
	

def on_hedge_buy(index, price, count):
	store_trade_data(hedge_buy_trade_list, index, price, count)

def on_hedge_sell(index, price, count):
	store_trade_data(hedge_sell_trade_list, index, price, count)

def on_buy(index, price, count):
	store_trade_data(buy_trade_list, index, price, count)

def on_sell(index, price, count):
	store_trade_data(sell_trade_list, index, price, count)


##########################################################################################
# hedgeStrategy
initialHedgeMoney = initialMoney * (hedgeRatio)
hedgeStrategyCount = int(initialHedgeMoney / budget)
hedgeStrategies = []

for i in range (0, hedgeStrategyCount ):
	s = strat.Strategy(stockData=responseHedge, 
				budget=budget, 
				splitCount=10+10/hedgeStrategyCount * i, 
				profitRate=5+5/hedgeStrategyCount * i, 
				buyOnRiseRatio=0.2,
				delayTrade=0, 
				buyMoreUnderLossRatio =0,
				minimumLosscutRate=0.85,
				logTrade=False, name='hedge')
	s.set_on_buy_fn(on_hedge_buy)
	s.set_on_sell_fn(on_hedge_sell)
	hedgeStrategies.append(s)


def calc_moving_average(sampling_count, index, data_list):
	assert(sampling_count > 0)

	count = len(data_list)
	if( count >= sampling_count + index):
		count = sampling_count

	sumVal = 0
	for i in range(0, count):
		sumVal += data_list[index - i]

	return sumVal / count

	


buyWeigt = 1
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
					s = strat.Strategy(response, 
							budget, 
							splitCount, 
							profitRate, 
							buyOnRiseRatio,
							delayTrade, 
							0.0, 
							logTrade, minimumLosscutRate)
					s.set_on_buy_fn(on_buy)
					s.set_on_sell_fn(on_sell)
					strategies.append(s)

strategyCount = len(strategies)
balances = []

mainAssetInvestmentRatios = []
mainAssetBalances = []
hedgeAssetBalances = []

scores = []
scoresDiff = []

recentHedgeAssetRatio = hedgeRatio
balanceTotal = initialMoney
h2mFlowHistory = []

for dayIdx in range (0, openPrices.size):

	if(hedgeRatio > destHedgeRatio ):
		hedgeRatio -= hedgeDecreaseStep

#----------------------------------------------------------------------------------------------------------------------
#	calc amount to rebalance between h and m
#----------------------------------------------------------------------------------------------------------------------
	toBeReserved_H2M = 0
	toBeReserved_M2H = 0
	if rebalanceHedge == True  :
		amount = 0
		if( recentHedgeAssetRatio < hedgeRatio * 0.9 ): #현재 헷지가 기준치 미달이라면
			if(dayIdx % mainAssetToHedgeInterval) == (mainAssetToHedgeInterval - 1):
				insufficientAmount = (hedgeRatio - recentHedgeAssetRatio) * balanceTotal * mainAssetToHedgeRebalanceRateAtOnce
				toBeReserved_M2H = insufficientAmount

		elif( recentHedgeAssetRatio > hedgeRatio * 1.2): #현재 헷지가 기준치 초과라면
			if(dayIdx % hedgetToMainAssetInterval) == (hedgetToMainAssetInterval - 1):
				exceededRatio = recentHedgeAssetRatio - hedgeRatio 
				insufficientAmount = balanceTotal * exceededRatio * hedgeToMainAssetRebalanceRateAtOnce
				toBeReserved_H2M = insufficientAmount
#----------------------------------------------------------------------------------------------------------------------
#	start trading
#----------------------------------------------------------------------------------------------------------------------
	balanceTotal = 0
	mainAssetTotalBudgets = 0
	mainAssetBalanceTotal = 0
	hedgeAssetBalanceTotal = 0
	if(dayIdx % 100 == 99 ):
		print('.day..'+ str(dayIdx))

	reservedBudgetForRebalance_M2H = 0

	for si in range (0, strategyCount):
		if toBeReserved_M2H > 0:
			reservedBudgetForRebalance_M2H += strategies[si].transfer_budget(toBeReserved_M2H / strategyCount) # todo

		strategies[si].sell_all_when_done(dayIdx)
		strategies[si].buy_weight(dayIdx, buyWeigt)
		strategies[si].post_trade(dayIdx)


		mainAssetTotalBudgets += strategies[si].budget
		mainAssetBalanceTotal += strategies[si].calc_balance(dayIdx)

	balanceTotal = mainAssetBalanceTotal
	reservedBudgetForRebalance_H2M = 0
	for hi in range (0, hedgeStrategyCount):
		if( toBeReserved_H2M > 0 ):
			rebalancePerStrategy = toBeReserved_H2M / hedgeStrategyCount
			amount = hedgeStrategies[hi].reserve_budget_at_close(dayIdx, rebalancePerStrategy) # todo
			reservedBudgetForRebalance_H2M += hedgeStrategies[hi].transfer_budget(amount) # todo
		else:
			hedgeStrategies[hi].sell_all_when_done(dayIdx)
			hedgeStrategies[hi].buy(dayIdx)

		hedgeStrategies[hi].post_trade(dayIdx)
		hedgeAssetBalanceTotal += hedgeStrategies[hi].calc_balance(dayIdx)
#----------------------------------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------------------------------
	score = 0
	lastSm = 0
	minDuration = 10
	#maxDuration = int(splitMiddle) * 2
	weight = 1
	maxDuration = 30
	lastSamplingDays = 0
	for i in range(minDuration, maxDuration):
		ri = maxDuration + minDuration - i
		days = int(math.pow(1.1, ri))
		if(lastSamplingDays == days):
			continue

		lastSamplingDays = days
		sm = calc_moving_average( days, dayIdx-2, closePrices2)

		if(lastSm == 0): 
			lastSm = sm

		score += (lastSm - sm) * weight

	sign = score / math.fabs(score)
	score = math.log(math.fabs(score)) * sign
	
	if(dayIdx == 0) :
		scoresDiff.append(0)
	else:
		scoreDiff = score - scores[-1]
		if math.fabs(scoreDiff) > 20:
			scoresDiff.append(0)
		else:
			scoresDiff.append(scoreDiff)


	if(dayIdx > 200):
		buyWeigt = 1 - score / 49

	if(math.fabs(score) > 200):
		score = 0

	scores.append(score)
	print(score)

#	if(score < -53.663):
#		scores.append(mainAssetBalanceTotal)
#	else:
#		scores.append(0)


	balanceTotal = hedgeAssetBalanceTotal + mainAssetBalanceTotal
	balances.append(balanceTotal)

	mainAssetRatio = mainAssetTotalBudgets/balanceTotal
	assert(mainAssetRatio >= -0.1)
	mainAssetInvestmentRatios.append(1 - mainAssetRatio)

	mainAssetBalances.append(mainAssetBalanceTotal)
	hedgeAssetBalances.append(hedgeAssetBalanceTotal)

	recentHedgeAssetRatio = hedgeAssetBalanceTotal / balanceTotal

#----------------------------------------------------------------------------------------------------------------------
#	rebalancing after marget
#----------------------------------------------------------------------------------------------------------------------
	if(rebalance == True ):
		if((dayIdx % rebalanceInterval == (rebalanceInterval-1))):
			rebalanceBase = balanceTotal / strategyCount
			sortedStrategies = sorted(strategies, key=lambda x : x.lastBalance) 	

			for strategyIdx in range (0, strategyCount):
				desire = rebalanceBase - sortedStrategies[strategyIdx].lastBalance
				if(desire < 0):
					break

				taker = sortedStrategies[strategyIdx]
				giver = sortedStrategies[strategyCount - strategyIdx - 1]
				amount = giver.transfer_budget( desire * rebalanceRateAtOnce)
				taker.fill_budget(amount)


#----------------------------------------------------------------------------------------------------------------------
#	deferred trans budget between h and m
#----------------------------------------------------------------------------------------------------------------------
	if(len(h2mFlowHistory) == 0):
		h2mFlow = initialHedgeMoney
	else:
		h2mFlow = h2mFlowHistory[-1]

	if(reservedBudgetForRebalance_H2M > 0):
		h2mFlow = initialHedgeMoney - reservedBudgetForRebalance_H2M
		for sss in range(0, strategyCount):
			strategies[sss].fill_budget(reservedBudgetForRebalance_H2M / strategyCount)  # todo
		reservedBudgetForRebalance_H2M = 0
	
	elif(reservedBudgetForRebalance_M2H > 0):
		h2mFlow = initialHedgeMoney + reservedBudgetForRebalance_M2H
		for hhh in range(0, hedgeStrategyCount):
			hedgeStrategies[hhh].fill_budget(reservedBudgetForRebalance_M2H / hedgeStrategyCount)
		reservedBudgetForRebalance_M2H = 0

	h2mFlowHistory.append(h2mFlow)
		#print('---------------after rebalance-----------------------[' + str(dayIdx))
		#for strategyIdx in range (0, strategyCount):
		#	print(sortedStrategies[strategyIdx].lastBalance)










#- end of trade routine -----------------------------------------------------------------------------------------------------------------------

profitRatio = balances[-1]/initialMoney

#plt.subplot(211)

for i in range (0, len(mainAssetInvestmentRatios)):
	mainAssetInvestmentRatios[i] *= balances[-1]

for i in range (0, len(h2mFlowHistory)):
	h2mFlowHistory[i] *= 20



#################################################################################






	#sell_trade_list[index].
	#buy_trade_list = [None]*len(closePrices)
	#hedge_sell_trade_list = [None]*len(closePrices)
	#hedge_buy_trade_list = [None]*len(closePrices
        #self.signal_add(bt.SIGNAL_LONG, crossover)



class SimpleBTStrat(bt.SignalStrategy):
	def __init__(self):
		self.index = 0

	def next(self):
		if sell_trade_list[self.index] is not None:
			for price, count in sell_trade_list[self.index].items():
				self.sell(data = self.datas[0], size = int(count), price=price)


		if buy_trade_list[self.index] is not None:
			for price, count in buy_trade_list[self.index].items():
				self.buy(data = self.datas[0], size = int(count), price=price)

		if hedge_sell_trade_list[self.index] is not None:
			for price, count in hedge_sell_trade_list[self.index].items():
				self.sell(data = self.datas[1], size = int(count), price=price)

		if hedge_buy_trade_list[self.index] is not None:
			for price, count in hedge_buy_trade_list[self.index].items():
				self.buy(data = self.datas[1], size = int(count), price=price)
		self.index += 1

cerebro = bt.Cerebro()

data0 = bt.feeds.PandasData(dataname=yf.download(ticker, start_time_str, end_time_str))
data1 = bt.feeds.PandasData(dataname=yf.download(tickerHedge, start_time_str, end_time_str))
data0.plotinfo.plot = False
data1.plotinfo.plot = False
cerebro.adddata(data0)
cerebro.adddata(data1)

cerebro.addstrategy(SimpleBTStrat)
cerebro.broker.setcash(initialMoney)
cerebro.broker.setcommission(0.0025)
cerebro.addobserver(bt.observers.Broker)
cerebro.run(stdstats=False)
cerebro.plot()
#################################################################################








yticks = []
for i in range(0, 50):
	yticks.append(initialMoney*i)
plt.yticks(yticks)

plt.plot(strategies[0].stockData.index, h2mFlowHistory)
plt.plot(strategies[0].stockData.index, mainAssetInvestmentRatios, color='lightskyblue')
plt.plot(strategies[0].stockData.index, hedgeAssetBalances, label = str(i), color='purple')
plt.plot(strategies[0].stockData.index, mainAssetBalances, label = str(i), color='green')

mul = initialMoney/closePrices2[0]

for i in range(0, len(scores)):
	scores[i] *= initialMoney / 20
	scoresDiff[i]*= initialMoney / 20


#mul = balances[-1]/closePrices2[-1]
plt.plot(strategies[0].stockData.index, closePrices2 * mul, color='grey')
plt.plot(strategies[0].stockData.index, balances, color='red')
plt.plot(strategies[0].stockData.index, scores, color='purple')
plt.plot(strategies[0].stockData.index, scoresDiff, color='red')
plt.tight_layout(pad=1.08, h_pad=None, w_pad=None, rect=None)
plt.grid(True)


#plt.subplot(211)
#plt.plot(strategies[i].stockData.index, hedgeAssetBalances, label = str(i))





#plt.yscale("log",basey=2)

#plt.legend()
plt.grid(True)
plt.show()