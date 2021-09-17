from os import curdir
from time import strftime
import yfinance as yf
import backtrader as bt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import strategy as strat
import strategyArb as stratArb
import math

ticker = "TQQQ"
tickerHedge = "UUP"
tickerHedge2 = "TMF"
#tickerHedge2 = "QYLD"
#tickerHedge2 = "TLT"
tickerHedge3 = "TIP"
tickerHedge4 = "TMF"
tickerHedge5 = "UUP"

ticker2 = "QQQ"
initialMoney = 1000000
budget = initialMoney
outperform_rates_outperform_chart = []
outperform_orig_outperform_chart = []
outperform_model_outperform_chart = []
hedgeRatio = 0.8
rebalanceProfitTarget = 0.08
rebalanceRate = 0.1

beginDate = None
#endDate = datetime(2010, 3, 8)
endDate = datetime(2010, 1, 15)
toggle = 0
#for yy in range(0, 20):
for yy in range(0, 1):
	beginDate = endDate
	#endDate = beginDate + timedelta(days=182)
	endDate = beginDate + timedelta(days=365*11+240)

	strDateBegin = beginDate.strftime('%Y-%m-%d')
	strDateEnd = endDate.strftime('%Y-%m-%d')


	print(strDateBegin)
	print(strDateEnd)

	response = yf.download(ticker, start=strDateBegin, end=strDateEnd)
	response2 = yf.download(ticker2, start=strDateBegin, end=strDateEnd)
	openPrices = response['Open']
	closePrices = response['Close']
	closePrices2 = response2['Close']

	originalAssetPrices = []
	mul = initialMoney/closePrices2[0]
	for c2 in range(0, closePrices.size):
		originalAssetPrices.append(closePrices2[c2] * mul)

	responseHedge = yf.download(tickerHedge, start=strDateBegin, end=strDateEnd)
	responseHedge2 = yf.download(tickerHedge2, start=strDateBegin, end=strDateEnd)
	responseHedge3 = yf.download(tickerHedge3, start=strDateBegin, end=strDateEnd)
	responseHedge4 = yf.download(tickerHedge4, start=strDateBegin, end=strDateEnd)
	responseHedge5 = yf.download(tickerHedge5, start=strDateBegin, end=strDateEnd)

	strategies = []


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
	hedgeStrategies = []
	hedgeStrategyCount = 1
	for i in range (0, hedgeStrategyCount ):
		data = responseHedge
		#if(i % 3 == 0):
		#	data = responseHedge2
		#if(i % 3 == 1):
		#	data = responseHedge3

		desiredAllocationRatio = hedgeRatio / hedgeStrategyCount
		hs = stratArb.StrategyArb(stockData=data, 
					budget=initialHedgeMoney/hedgeStrategyCount, 
					desiredAllocationRatio = desiredAllocationRatio,
					delayTrade=0, 
					logTrade=False, name='hedge')

		hs.set_on_buy_fn(on_hedge_buy)
		hs.set_on_sell_fn(on_hedge_sell)
		hedgeStrategies.append(hs)

	##########################################################################################

	initialMainAssetMoney = initialMoney * (1-hedgeRatio)
	mainAssetStrategyCount = 1
	for i in range (0, mainAssetStrategyCount ):
		desiredAllocationRatio = (1-hedgeRatio) / mainAssetStrategyCount
		s = stratArb.StrategyArb(stockData=response, 
				desiredAllocationRatio = desiredAllocationRatio,
				budget=initialMainAssetMoney / mainAssetStrategyCount)

		s.set_on_buy_fn(on_buy)
		s.set_on_sell_fn(on_sell)
		strategies.append(s)

	strategyCount = len(strategies)

	balances = []

	mainAssetInvestmentRatios = []
	mainAssetBalances = []
	hedgeAssetBalances = []


	recentHedgeAssetRatio = hedgeRatio
	days = openPrices.size - 1

	lastBalanceTotalAtRebalance = initialMoney
	balanceTotal = 0
	for dayIdx in range (days):

		strToday = response.index[dayIdx]
		for mi in range(mainAssetStrategyCount):
			strategies[mi].buy_all(dayIdx)
	
		for hi in range(hedgeStrategyCount):
			hedgeStrategies[hi].buy_all(dayIdx)
	

		balanceTotal = 0
		for mi in range(mainAssetStrategyCount):
			balanceTotal += strategies[mi].calc_balance(dayIdx)
	
		for hi in range(hedgeStrategyCount):
			balanceTotal += hedgeStrategies[hi].calc_balance(dayIdx)
		
		##################################################################################################################
		curProfit = (balanceTotal - lastBalanceTotalAtRebalance) / lastBalanceTotalAtRebalance

		if(curProfit > rebalanceProfitTarget):
			print('+++', strToday, ': ', balanceTotal, int(curProfit * 100) / 100)
			surplus = 0
			mainAssetBalanceTotal = 0
			hedgeAssetBalanceTotal = 0
			reservedMoneyTotal = 0
			takers = []
			for mi in range(mainAssetStrategyCount):
				surplus = strategies[mi].calc_allocation_surplus_amount(totalBalance =balanceTotal, dayIndex = dayIdx) * rebalanceRate
				if(surplus > 0):
					reservedMoney = strategies[mi].reserve_budget_at_close(dayIndex= dayIdx, desiredReserve=surplus)
					reservedMoneyTotal = strategies[mi].transfer_budget(desiredMoney=reservedMoney)
				else:
					takers.append(strategies[mi])

		
			for hi in range(hedgeStrategyCount):
				surplus = hedgeStrategies[hi].calc_allocation_surplus_amount(totalBalance =balanceTotal, dayIndex = dayIdx) * rebalanceRate
				if(surplus > 0):
					reservedMoney = hedgeStrategies[hi].reserve_budget_at_close(dayIndex= dayIdx, desiredReserve=surplus)
					reservedMoneyTotal = hedgeStrategies[hi].transfer_budget(desiredMoney=reservedMoney)
				else:
					takers.append(hedgeStrategies[hi])

			takersCount = len(takers)
			for ti in range(takersCount):
				insuff = -1 * takers[ti].calc_allocation_surplus_amount(totalBalance =balanceTotal, dayIndex = dayIdx) * rebalanceRate
				if( insuff > reservedMoneyTotal ):
					insuff = reservedMoneyTotal
				takers[ti].fill_budget(insuff)
				reservedMoneyTotal -= insuff

			lastBalanceTotalAtRebalance = balanceTotal
		else:
			if(curProfit < -0.1):
				print('   ', strToday, ': ', balanceTotal, int(curProfit*100)/100, '----')



	class SimpleBTStrat(bt.SignalStrategy):
		def __init__(self):
			self.index = 0
			self.mainAssetLongPositions = 0

		def next(self):
			if sell_trade_list[self.index] is not None:
				for price, count in sell_trade_list[self.index].items():
					pos = self.getposition(data = self.datas[0])
					if( pos.size < count ):
						count = pos.size
					self.sell(data = self.datas[0], size = int(count), price=price)


			if buy_trade_list[self.index] is not None:
				for price, count in buy_trade_list[self.index].items():
					cash = self.broker.getcash()
					order_size = int(count)
					if(cash < price * order_size):
						order_size = int(cash / price)

					self.buy(data = self.datas[0], size = order_size, price=price)

			if hedge_sell_trade_list[self.index] is not None:
				for price, count in hedge_sell_trade_list[self.index].items():
					pos = self.getposition(data = self.datas[1])
					if( pos.size < count ):
						count = pos.size
					self.sell(data = self.datas[1], size = int(count), price=price)

			if hedge_buy_trade_list[self.index] is not None:
				for price, count in hedge_buy_trade_list[self.index].items():
					cash = self.broker.getcash()
					order_size = int(count)
					if(cash < price * order_size):
						order_size = int(cash / price)
					self.buy(data = self.datas[1], size = int(order_size), price=price)
					cash = self.broker.getcash()
			self.index += 1

	cerebro = bt.Cerebro()

	data0 = bt.feeds.PandasData(dataname=yf.download(ticker, strDateBegin, strDateEnd))
	data1 = bt.feeds.PandasData(dataname=yf.download(tickerHedge, strDateBegin, strDateEnd))
	'''data2 = bt.feeds.PandasData(dataname=yf.download(tickerHedge2, strDateBegin, strDateEnd))
	data3 = bt.feeds.PandasData(dataname=yf.download(tickerHedge3, strDateBegin, strDateEnd))
	data4 = bt.feeds.PandasData(dataname=yf.download(tickerHedge4, strDateBegin, strDateEnd))
	data5 = bt.feeds.PandasData(dataname=yf.download(tickerHedge5, strDateBegin, strDateEnd))'''

	data0.plotinfo.plot = False
	data1.plotinfo.plot = False
	cerebro.adddata(data0)
	cerebro.adddata(data1)
	'''cerebro.adddata(data2)
	cerebro.adddata(data3)
	cerebro.adddata(data4)
	cerebro.adddata(data5)'''

	cerebro.addstrategy(SimpleBTStrat)
	cerebro.broker.setcash(initialMoney)
	cerebro.broker.setcommission(0.0025)
	cerebro.addobserver(bt.observers.Broker)
	cerebro.run(stdstats=False)
	cerebro.plot()

print(balanceTotal)	