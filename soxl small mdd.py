from os import curdir
import yfinance as yf
import backtrader as bt
from datetime import datetime
import matplotlib.pyplot as plt
import strategy as strat

#start_time_str = '2016-01-01'
#end_time_str = '2021-06-20'
start_time_str = '2016-01-01'
end_time_str = '2021-08-30'
ticker = "SOXL"
tickerHedge = "UVXY"
#tickerHedge = "SOXS"
ticker2 = "SOXX"

#response = requests.get(HISTORY_DATA_URL)
response = yf.download(ticker, start=start_time_str, end=end_time_str)
response2 = yf.download(ticker2, start=start_time_str, end=end_time_str)
openPrices = response['Open']
closePrices = response['Close']
closePrices2 = response2['Close']

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

splitStrategyCount = 5
splitIncreaseStep = 0.5
splitMiddle = 26.745
initialSplitCount = splitMiddle - (splitStrategyCount - 1)/2 * splitIncreaseStep


buyOnRiseRatioStrategyCount = 5
buyOnRiseRatioIncreaseStep = 0.01
buyOnRiseRatioMiddle = 0.4
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
rebalance = True

mainAssetInvestmentRatios = []
rebalanceHedge =  True
mainAssetBalances = []
hedgeAssetBalances = []

hedgeAssetRatio = hedgeRatio
balanceTotal = initialMoney
flow_h2m = []


reservedBudgetForRebalance_H2M = 0
reservedBudgetForRebalance_M2H = 0
for dayIdx in range (0, openPrices.size):

	if(hedgeRatio > destHedgeRatio ):
		hedgeRatio -= hedgeDecreaseStep

	if(reservedBudgetForRebalance_H2M > 0):

		rebalancePerStrategy = reservedBudgetForRebalance_H2M / hedgeStrategyCount
		amountTotal = 0
		for hhh in range(0, hedgeStrategyCount):
			amount = hedgeStrategies[hhh].reserve_budget_at_open(dayIdx, rebalancePerStrategy) # todo
			amountTotal += hedgeStrategies[hhh].transfer_budget(amount) # todo
			hedgeStrategies[hhh].lock_trade() # todo

		print('++ hedge to main')
		flow_h2m.append(initialHedgeMoney - amountTotal)
		for sss in range(0, strategyCount):
			strategies[sss].fill_budget(amountTotal / strategyCount)  # todo

		reservedBudgetForRebalance_H2M = 0
	
	elif(reservedBudgetForRebalance_M2H > 0):
		flow_h2m.append(initialHedgeMoney + reservedBudgetForRebalance_M2H)
		for hhh in range(0, hedgeStrategyCount):
			hedgeStrategies[hhh].fill_budget(reservedBudgetForRebalance_M2H / hedgeStrategyCount)
		reservedBudgetForRebalance_M2H = 0
	else:
		if(len(flow_h2m) == 0):
			flow_h2m.append(initialHedgeMoney)
		else:
			flow_h2m.append(flow_h2m[-1])

	if rebalanceHedge == True  :
		amount = 0
		if( hedgeAssetRatio < hedgeRatio * 0.9 ): #현재 헷지가 기준치 미달이라면
			if(dayIdx % mainAssetToHedgeInterval) == (mainAssetToHedgeInterval - 1):
				insufficientAmount = (hedgeRatio - hedgeAssetRatio) * balanceTotal * mainAssetToHedgeRebalanceRateAtOnce
				amount = 0
				for sss in range(0, strategyCount):
					transfered = strategies[sss].transfer_budget(insufficientAmount / strategyCount) # todo
					reservedBudgetForRebalance_M2H += transfered
				
				print('-- main to hedge')

		elif( hedgeAssetRatio > hedgeRatio * 1.2): #현재 헷지가 기준치 초과라면
			if(dayIdx % hedgetToMainAssetInterval) == (hedgetToMainAssetInterval - 1):
				exceededRatio = hedgeAssetRatio - hedgeRatio 
				insufficientAmount = balanceTotal * exceededRatio * hedgeToMainAssetRebalanceRateAtOnce
				reservedBudgetForRebalance_H2M = insufficientAmount

	balanceTotal = 0
	mainAssetTotalBudgets = 0
	mainAssetBalanceTotal = 0
	hedgeAssetBalanceTotal = 0
	if(dayIdx % 100 == 99 ):
		print('.day..'+ str(dayIdx))

	for si in range (0, strategyCount):
		strategies[si].sell_all_when_done(dayIdx)
		strategies[si].buy(dayIdx)
		strategies[si].post_trade(dayIdx)
		mainAssetTotalBudgets += strategies[si].budget
		mainAssetBalanceTotal += strategies[si].calc_balance(dayIdx)

	balanceTotal = mainAssetBalanceTotal
	for hi in range (0, hedgeStrategyCount):
		if(hedgeStrategies[hi].is_trade_locked() == False):
			hedgeStrategies[hi].sell_all_when_done(dayIdx)
			hedgeStrategies[hi].buy(dayIdx)
		else:
			hedgeStrategies[hi].unlock_trade()

		hedgeStrategies[hi].post_trade(dayIdx)
		hedgeAssetBalanceTotal += hedgeStrategies[hi].calc_balance(dayIdx)

	balanceTotal = hedgeAssetBalanceTotal + mainAssetBalanceTotal
	balances.append(balanceTotal)

	ratio = mainAssetTotalBudgets/balanceTotal
	assert(ratio >= -0.1)
	mainAssetInvestmentRatios.append(1 - ratio)
	mainAssetBalances.append(mainAssetBalanceTotal)
	hedgeAssetBalances.append(hedgeAssetBalanceTotal)

	hedgeAssetRatio = hedgeAssetBalanceTotal / balanceTotal


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

for i in range (0, len(flow_h2m)):
	flow_h2m[i] *= 10



#################################################################################






	#sell_trade_list[index].
	#buy_trade_list = [None]*len(closePrices)
	#hedge_sell_trade_list = [None]*len(closePrices)
	#hedge_buy_trade_list = [None]*len(closePrices
        #self.signal_add(bt.SIGNAL_LONG, crossover)



class SmaCross(bt.SignalStrategy):
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
cerebro.adddata(data0)
cerebro.adddata(data1)

cerebro.addstrategy(SmaCross)
cerebro.broker.setcash(initialMoney)
cerebro.broker.setcommission(0.0025)
cerebro.run()
cerebro.plot()
#################################################################################










plt.plot(strategies[0].stockData.index, flow_h2m)
plt.plot(strategies[0].stockData.index, mainAssetInvestmentRatios, color='lightskyblue')
plt.plot(strategies[0].stockData.index, hedgeAssetBalances, label = str(i), color='purple')
plt.plot(strategies[0].stockData.index, mainAssetBalances, label = str(i), color='green')

mul = initialMoney/closePrices2[0]
#mul = balances[-1]/closePrices2[-1]
plt.plot(strategies[0].stockData.index, closePrices2 * mul, color='grey')
plt.plot(strategies[0].stockData.index, balances, color='red')
plt.tight_layout(pad=1.08, h_pad=None, w_pad=None, rect=None)
plt.grid(True)


#plt.subplot(211)
#plt.plot(strategies[i].stockData.index, hedgeAssetBalances, label = str(i))





#plt.yscale("log",basey=2)

#plt.legend()
plt.grid(True)
plt.show()