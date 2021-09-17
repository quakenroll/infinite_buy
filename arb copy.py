from os import curdir
from time import strftime
import yfinance as yf
import backtrader as bt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import strategy as strat
import strategyArb as stratArb
import math

tickerMainAssets = [("FNGU", 0.2), ("TQQQ", 0.3), ("TECL", 0.3), ("SOXL", 0.2)]
#tickerHedges = [("UUP", 0.5), ("TMF", 0.5)]

tickerHedges = [("UUP", 0.25), ("TMF", 0.2), ("TIP", 0.25), ("UVXY", 0.15), ("GLD", 0.15)]
#tickerHedge = "UUP"
#tickerHedge2 = "TMF"
#tickerHedge2 = "QYLD"
#tickerHedge2 = "TLT"
#tickerHedge3 = "TIP"
#tickerHedge4 = "TMF"
#tickerHedge5 = "UUP"

ticker2 = "QQQ"
initialMoney = 1000000
budget = initialMoney
outperform_rates_outperform_chart = []
outperform_orig_outperform_chart = []
outperform_model_outperform_chart = []
hedgeRatio = 0.6
rebalanceProfitTarget = 0.015
rebalanceRate = 0.08

beginDate = None
endDate = datetime(2010, 3, 8)
#endDate = datetime(2012, 2, 31)
endDate = datetime(2018, 12, 3)
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

	allTickers = []
	mainAssetDataList = []
	mainAssetTickerCount = len(tickerMainAssets)
	days = 0
	dates = None
	for tm in range(mainAssetTickerCount):
		tickerName = tickerMainAssets[tm][0]
		ratio = tickerMainAssets[tm][1] * (1-hedgeRatio)
		responseMain = yf.download(tickerName, start=strDateBegin, end=strDateEnd)
		dates = responseMain.index
		closePrices = responseMain['Close']
		days = closePrices.size
		mainAssetDataList.append((responseMain, tickerName, ratio))
		allTickers.append(tickerName)

	response2 = yf.download(ticker2, start=strDateBegin, end=strDateEnd)
	closePrices2 = response2['Close']

	originalAssetPrices = []
	mul = initialMoney/closePrices2[0]


	hedgeAssetDataList = []
	hedgeTickerCount = len(tickerHedges)
	for th in range(hedgeTickerCount):
		tickerName = tickerHedges[th][0]
		ratio = tickerHedges[th][1] * hedgeRatio
		responseHedge = yf.download(tickerName, start=strDateBegin, end=strDateEnd)
		hedgeAssetDataList.append((responseHedge, tickerName, ratio))
		allTickers.append(tickerName)

	strategies = []

	sell_trade_data_dict = {}
	buy_trade_data_dict = {}
	
	mainAssetTickerCount = 1

	for i in range(len(allTickers)):
		tickerId = allTickers[i]
		sell_trade_list = [None]*(days)
		buy_trade_list = [None]*(days)
		sell_trade_data_dict[tickerId] = sell_trade_list
		buy_trade_data_dict[tickerId] = buy_trade_list

	def store_trade_data(trade_data_dict, tickerId, dayIdx, price, count):
		price = int(price * 100)
		price=price/100

		dest = trade_data_dict[tickerId]

		if dest[dayIdx] is None:
			dictItem = {price: count}
			dest[dayIdx] = dictItem
		else:
			price_and_count = dest[dayIdx]
			if price in price_and_count:
				price_and_count[price] += count
			else:
				price_and_count[price] = count
		

	def on_buy(ticker_id, dayIdx, price, count):
		price = int(price * 100) + 1
		price=price/100
		store_trade_data(buy_trade_data_dict, ticker_id, dayIdx, price, count)

	def on_sell(ticker_id, dayIdx, price, count):
		store_trade_data(sell_trade_data_dict, ticker_id, dayIdx, price, count)


	##########################################################################################
	# hedgeStrategy
	hedgeStrategies = []
	hedgeStrategyCount = len(hedgeAssetDataList)
	for i in range ( hedgeStrategyCount ):
		data = hedgeAssetDataList[i]
		financeData = data[0]
		tickerName = data[1]
		desiredAllocationRatio = data[2]

		hs = stratArb.StrategyArb(stockData=financeData, 
					budget=initialMoney * desiredAllocationRatio, 
					desiredAllocationRatio = desiredAllocationRatio,
					delayTrade=0, 
					logTrade=False, name=tickerName)

		hs.set_on_buy_fn(on_buy)
		hs.set_on_sell_fn(on_sell)
		hedgeStrategies.append(hs)

	##########################################################################################

	initialMainAssetMoney = initialMoney * (1-hedgeRatio)
	mainAssetStrategyCount = len(mainAssetDataList)
	for i in range (0, mainAssetStrategyCount ):
		data = mainAssetDataList[i]
		financeData = data[0]
		tickerName = data[1]
		desiredAllocationRatio = data[2]
		s = stratArb.StrategyArb(stockData=financeData, 
				desiredAllocationRatio = desiredAllocationRatio,
				budget=initialMoney * desiredAllocationRatio, 
				name=tickerName)

		s.set_on_buy_fn(on_buy)
		s.set_on_sell_fn(on_sell)
		strategies.append(s)

	strategyCount = len(strategies)

	balances = []

	mainAssetInvestmentRatios = []
	mainAssetBalances = []
	hedgeAssetBalances = []


	recentHedgeAssetRatio = hedgeRatio

	lastBalanceTotalAtRebalance = initialMoney
	balanceTotal = 0
	for dayIdx in range (days):

		boughtToday = False 
		strToday = dates[dayIdx]
		for mi in range(mainAssetStrategyCount):
			if(True == strategies[mi].buy_all(dayIdx)):
				boughtToday = True
	
		for hi in range(hedgeStrategyCount):
			hedgeStrategies[hi].buy_all(dayIdx)
			if(True == strategies[mi].buy_all(dayIdx)):
				boughtToday = True
	

		balanceTotal = 0
		budgetTotal = 0
		for mi in range(mainAssetStrategyCount):
			balanceTotal += strategies[mi].calc_balance(dayIdx)
			budgetTotal += strategies[mi].budget
	
		for hi in range(hedgeStrategyCount):
			balanceTotal += hedgeStrategies[hi].calc_balance(dayIdx)
			budgetTotal += hedgeStrategies[hi].budget
		
		##################################################################################################################
		curProfit = (balanceTotal - lastBalanceTotalAtRebalance) / lastBalanceTotalAtRebalance

		if(curProfit > rebalanceProfitTarget):
			if(boughtToday == True):
				print('boughtToday and (curProfit > rebalanceProfitTarget)')
			else:
				print('+++++++++++++', strToday, ': ', int(balanceTotal), int(curProfit * 1000) / 1000)

				surplus = 0
				mainAssetBalanceTotal = 0
				hedgeAssetBalanceTotal = 0
				reservedMoneyTotal = 0
				takers = []
				for mi in range(mainAssetStrategyCount):
					surplus = strategies[mi].calc_allocation_surplus_amount(totalBalance =balanceTotal, dayIndex = dayIdx) * rebalanceRate
					if(surplus > 0):
						reservedMoney = strategies[mi].reserve_budget_at_close(dayIndex= dayIdx, desiredReserve=surplus)
						reservedMoneyTotal += strategies[mi].transfer_budget(desiredMoney=reservedMoney)
					else:
						takers.append(strategies[mi])

			
				for hi in range(hedgeStrategyCount):
					surplus = hedgeStrategies[hi].calc_allocation_surplus_amount(totalBalance =balanceTotal, dayIndex = dayIdx) * rebalanceRate
					if(surplus > 0):
						reservedMoney = hedgeStrategies[hi].reserve_budget_at_close(dayIndex= dayIdx, desiredReserve=surplus)
						reservedMoneyTotal += hedgeStrategies[hi].transfer_budget(desiredMoney=reservedMoney)
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
			if(curProfit < -0.15):
				print('             ', strToday, ': ', int(balanceTotal), '          ', int(curProfit*1000)/1000, '-------------------------------------')


	print('   ', 'Finally:', balanceTotal, int(curProfit*100)/100, '----')

	class SimpleBTStrat(bt.SignalStrategy):
		def __init__(self):
			self.index = 0
			self.mainAssetLongPositions = 0
			self.keyToDataIdx = None
			self.mycash = self.broker.getcash()

			cerebroDataIdx = 0
			for key, value in buy_trade_data_dict.items():
				tickerName = key
				if(self.keyToDataIdx == None):
					self.keyToDataIdx = {tickerName : cerebroDataIdx}
				else:
					self.keyToDataIdx[tickerName] = cerebroDataIdx
				cerebroDataIdx += 1


		def notify_order(self, order):
			if order.status not in [order.Completed]:
				return

			if order.isbuy():
				action = 'Buy'
			elif order.issell():
				action = 'Sell'

			cash = self.broker.getcash()
			value = self.broker.getvalue()

			
			#print(action, order.size, cash, value)

		def next(self):
			cash = self.broker.getcash()
			for ticker, value in sell_trade_data_dict.items():
				sell_trade_data = value
				dataIndex = self.keyToDataIdx[ticker]
				if sell_trade_data[self.index] is not None:
					for price, count in sell_trade_data[self.index].items():
						pos = self.getposition(data = self.datas[dataIndex])
						if( pos.size < count ):
							count = pos.size
						self.sell(data = self.datas[dataIndex], size = int(count), price=price)
						self.mycash += int(count) * price * (1-0.0025)

			for ticker, value in buy_trade_data_dict.items():
				buy_trade_data = value
				dataIndex = self.keyToDataIdx[ticker]
				if buy_trade_data[self.index] is not None:
					for price, count in buy_trade_data[self.index].items():
						cash = self.broker.getcash()
						order_size = int(count)
						if(cash < price * order_size):
							order_size = int(cash / price)

						self.buy(data = self.datas[dataIndex], size = order_size, price=price)
						self.mycash -= order_size * price * (1+0.0025)
						if(self.index == 0):
							value = self.datas[dataIndex].close[0]
							print(ticker, ': ', value, price)
							print(self.mycash)
			self.index += 1

	cerebro = bt.Cerebro()

	cerebroStrat = SimpleBTStrat

	for key, value in buy_trade_data_dict.items():
		tickerName = key
		data = bt.feeds.PandasData(dataname=yf.download(tickerName, strDateBegin, strDateEnd))
		data.plotinfo.plot = False
		cerebro.adddata(data)


	'''data2 = bt.feeds.PandasData(dataname=yf.download(tickerHedge2, strDateBegin, strDateEnd))
	data3 = bt.feeds.PandasData(dataname=yf.download(tickerHedge3, strDateBegin, strDateEnd))
	data4 = bt.feeds.PandasData(dataname=yf.download(tickerHedge4, strDateBegin, strDateEnd))
	data5 = bt.feeds.PandasData(dataname=yf.download(tickerHedge5, strDateBegin, strDateEnd))'''

	'''cerebro.adddata(data2)
	cerebro.adddata(data3)
	cerebro.adddata(data4)
	cerebro.adddata(data5)'''

	cerebro.addstrategy(cerebroStrat)
	cerebro.broker.setcash(initialMoney)
	cerebro.broker.setcommission(0.0025)
	cerebro.addobserver(bt.observers.Broker)
	cerebro.run(stdstats=False)
	cerebro.plot()

print(balanceTotal)	