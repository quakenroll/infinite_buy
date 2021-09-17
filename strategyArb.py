import math
from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt

EPSILON = 0.000000001
class StrategyArb:

	def __init__(self, stockData, budget, desiredAllocationRatio, delayTrade = 0, logTrade = True, name = ''):
		self.days_buy_lock = 0
		self.name = name
		self.budget = budget
		self.lastBalance = budget 
		self.stockData = stockData
		self.openPrices = stockData['Open']
		self.closePrices = stockData['Close']
		self.highPrices = stockData['High']
		self.lowPrices = stockData['Low']
		self.stockData['Date'] = stockData.index
		self.logTrade = logTrade
		self.buyOrderPriceFactor = 1
		self.desiredAllocationRatio = desiredAllocationRatio

		self.stockCount = 0
		self.breakEvenPrice = 0
		self.balanceHistory = []
		self.assetValueHistory = []
		self.delayTrade = delayTrade
		#self.sellFee = 0.25/100
		#self.buyFee = 0.25/100
		self.sellFee = 0.25/100
		self.buyFee = 0.25/100
		self.on_buy = 0 # fn(dayIndex, price, count)
		self.on_sell = 0 # fn(dayIndex, price, count)

	def set_on_buy_fn(self, func):
		self.on_buy = func # fn(dayIndex, price, count)

	def set_on_sell_fn(self, func):
		self.on_sell = func # fn(dayIndex, price, count)
	

	def calc_asset_alloc_ratio(self, totalBalance, dayIndex):
		val = self.calc_balance(dayIndex) / totalBalance
		return val

	def calc_allocation_surplus_ratio(self, totalBalance, dayIndex):
		curAssetAllocRatio = self.calc_asset_alloc_ratio(totalBalance, dayIndex)
		return curAssetAllocRatio - self.desiredAllocationRatio

	def calc_allocation_surplus_amount(self, totalBalance, dayIndex):
		desiredBudget = totalBalance * self.desiredAllocationRatio
		surplusAmount = self.calc_balance(dayIndex=dayIndex) - desiredBudget
		return surplusAmount
	
	
	def _buy_close(self, dayIndex, money) :
		#print(money)
		
		if(self.budget <= -EPSILON):
			return False

		if(self.budget - money < -EPSILON):
			money = self.budget
			
		if(money <= 0):
			return False

		recentPrice = self.closePrices[dayIndex]
		orderPrice = recentPrice * (self.buyOrderPriceFactor)
		costPerStock = orderPrice * (1.0 + self.buyFee)
		count = (money / costPerStock) * 1.0
		if count <= -EPSILON:
			return False

		if(orderPrice < self.closePrices[dayIndex]):
			return False

		closePrice = self.closePrices[dayIndex]
		breakEvenPrice = ( ( self.stockCount * self.breakEvenPrice ) + (count * closePrice * (1.0 + self.buyFee)) ) / (self.stockCount + count)
		stockCount = self.stockCount + count
		budget = self.budget - (closePrice * count) * (1.0 + self.buyFee)

		if(budget <= -1*EPSILON):
			return False

		if( count > 0):
			self.on_buy(self.name, dayIndex, closePrice, count)


		self.breakEvenPrice = breakEvenPrice
		self.stockCount = stockCount
		self.budget = budget 

		if(math.fabs(self.budget) < EPSILON):
			self.budget = 0

		assert(self.budget >= 0)
		#print("[BUY ] self.budget(%d) Count(%d) Mean(%f) BUY(%f)" % (self.budget, self.stockCount, self.breakEvenPrice, close_value))

		return True
	
	def is_tradable(self, dayIndex):
		if(dayIndex < self.delayTrade):
			return False

		size = self.closePrices.size
		if dayIndex >= size:
			return False
		
		return True

	
	def calc_balance(self, dayIndex):
		val = self.closePrices[dayIndex] * self.stockCount + self.budget
		return val
	
	def fill_budget(self, money):
		assetValue = self.lastBalance - self.budget
		self.budget += money
		self.lastBalance += money

	def fill_budget_and_buy_all(self, money, dayIndex):
		self.fill_budget(money)

	def buy_all(self, dayIndex):
		self._buy_close(dayIndex=dayIndex, money=self.budget)
		

	def transfer_budget(self, desiredMoney):
		transfered = 0
		if(self.budget > desiredMoney):
			transfered = desiredMoney
		else:
			transfered = self.budget

		self.budget -= transfered
		self.lastBalance -= transfered
		if(self.budget < 0):
			assert(0)

		return transfered

	def reserve_budget_at_close(self, dayIndex, desiredReserve):

		if(dayIndex == 0):
			return 0

		if(desiredReserve <= self.budget): # already reserved
			return desiredReserve

#--------------------------------------------------------------------------------
#	calc count by recentPrice
#--------------------------------------------------------------------------------
		recentPrice = self.closePrices[dayIndex]
		#recentPrice = self.closePrices[dayIndex]
		count = desiredReserve / (recentPrice * (1.0 - self.sellFee))
		if(self.stockCount < count):
			count = self.stockCount
#--------------------------------------------------------------------------------

		if( count > 0):
			self.on_sell(self.name, dayIndex, self.closePrices[dayIndex], count)

		self.stockCount -= count
		assert(self.stockCount >= 0)
		self.budget += count * self.closePrices[dayIndex] * (1.0 - self.sellFee);

		if(desiredReserve <= self.budget): # finally reserved
			return desiredReserve

		return self.budget


	def post_trade(self, dayIndex):
		self.assetValueHistory.append(self.stockCount * self.closePrices[dayIndex])
		self.balanceHistory.append(self.calc_balance(dayIndex))