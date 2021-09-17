import math
from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt

EPSILON = 0.000000001
class Strategy:

	def __init__(self, stockData, budget, splitCount, profitRate, buyOnRiseRatio, delayTrade = 0, buyMoreUnderLossRatio = 0.00, logTrade = True, minimumLosscutRate = 1.0, name = '', seq = 0):
		self.days_buy_lock = 0
		self.name = name
		self.budget = budget
		self.lastBalance = budget 
		self.snapshotBalance = budget
		self.splitCount = splitCount
		self.initialProfitRate = self.profitRate = profitRate
		self.buyOnRiseRatio = buyOnRiseRatio
		self.stockData = stockData
		self.openPrices = stockData['Open']
		self.closePrices = stockData['Close']
		self.highPrices = stockData['High']
		self.lowPrices = stockData['Low']
		self.stockData['Date'] = stockData.index
		self.logTrade = logTrade
		self.minimumLosscutRate = minimumLosscutRate
		self.profitSellAmountRateAtOnce = 1
		self.lossSellAmountRateAtOnce = 1
		#self.buyOrderCalcWeight = 0.9804
		self.buyOrderPriceFactor = 1.06
		self.seq = seq

		self.stockCount = 0
		self.breakEvenPrice = 0
		self.balanceHistory = []
		self.assetValueHistory = []
		self.delayTrade = delayTrade
		self.sellFee = 0.25/100
		self.buyFee = 0.25/100
		self.buyMoreUnderLossRatio = buyMoreUnderLossRatio
		self.score = 0
		self.recentScoreWeight = 1.0
		self.lastScore = 0
		self.scoreHistory = []
		self.trade_locked = False
		self.curBuyProgress = 0
		self.buyAmountUnit = self.budget / self.splitCount
		self.on_buy = 0 # fn(dayIndex, price, count)
		self.on_sell = 0 # fn(dayIndex, price, count)

	def set_on_buy_fn(self, func):
		self.on_buy = func # fn(dayIndex, price, count)

	def set_on_sell_fn(self, func):
		self.on_sell = func # fn(dayIndex, price, count)
	

	def _buy_close(self, dayIndex, money) :
		#print(money)
		
		if(self.budget <= -EPSILON):
			return False

		if(self.budget - money < -EPSILON):
			money = self.budget
			
		if(money <= 0):
			return False

		#recentPrice = self.closePrices[dayIndex-1]
		recentPrice = self.openPrices[dayIndex]
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

		if(budget <= 0.):
			return False

		if( count > 0):
			self.on_buy(dayIndex, closePrice, count)


		self.breakEvenPrice = breakEvenPrice
		self.stockCount = stockCount
		self.budget = budget 

		if(math.fabs(self.budget) < EPSILON):
			self.budget = 0

		#print("[BUY ] self.budget(%d) Count(%d) Mean(%f) BUY(%f)" % (self.budget, self.stockCount, self.breakEvenPrice, close_value))

		return True
	
	def is_tradable(self, dayIndex):
		if(dayIndex < self.delayTrade):
			return False

		size = self.closePrices.size
		if dayIndex >= size:
			return False
		
		return True

	
	def is_take_profit_condition(self, dayIndex, profitRate):
		return self.breakEvenPrice * profitRate < float(self.highPrices[dayIndex])

	def calc_balance(self, dayIndex):
		return self.closePrices[dayIndex] * self.stockCount + self.budget

	def sell_all_when_done(self, dayIndex, sellAllAtClose = False ):
		price_and_count = (0, 0)
		sold = 0
		soldCount = 0
		if self.is_tradable(dayIndex) == False: return price_and_count

		if( self.stockCount == 0 ):
			return price_and_count

		if(math.fabs(self.splitCount - self.curBuyProgress) <= EPSILON):
			self.curBuyProgress = self.splitCount

		assert(self.splitCount - self.curBuyProgress >= 0 )

		progressRatio = self.curBuyProgress / self.splitCount
		#progressRatio = 1
		sellAmountRate = 0

		if(self.budget - self.buyAmountUnit <= 0 or sellAllAtClose == True):
			#if self.is_take_profit_condition(dayIndex, self.minimumLosscutRate) : # losscut
				price = self.closePrices[dayIndex] 
				sellAmountRate = self.lossSellAmountRateAtOnce
				soldCount = self.stockCount * sellAmountRate
				sold = (soldCount * price)
				price_and_count = (price, soldCount)

		elif self.is_take_profit_condition(dayIndex, self.profitRate) : # take profit
			price = self.breakEvenPrice * self.profitRate
			if(price < self.lowPrices[dayIndex]):
				price = self.lowPrices[dayIndex]

			#sellAmountRate = self.profitSellAmountRateAtOnce * (0.5 + (progressRatio * progressRatio)*0.5)
			sellAmountRate = self.profitSellAmountRateAtOnce
			soldCount = self.stockCount * sellAmountRate 
			sold = soldCount * price
			price_and_count = (price, soldCount)

		if sold > 0:
			self.budget += sold  * (1.0 - self.sellFee)
			self.curBuyProgress *= (1.0 - sellAmountRate)
			self.stockCount -= soldCount
			if(self.stockCount <= EPSILON):
				self.breakEvenPrice = 0

			self.lastBalance = self.calc_balance(dayIndex)
			self.buyAmountUnit = self.lastBalance / self.splitCount
			
			self.on_sell(dayIndex, price_and_count[0], price_and_count[1])
		

		return price_and_count
	
	
	
	def lock_trade(self):
		self.trade_locked = True

	def is_trade_locked(self):
		return self.trade_locked

	def unlock_trade(self):
		self.trade_locked = False 

	def fill_budget(self, money):
		assetValue = self.lastBalance - self.budget
		self.budget += money
		self.lastBalance += money
		self.curBuyProgress = self.splitCount * assetValue / self.lastBalance
		if(self.splitCount - self.curBuyProgress < 0 ):
			self.curBuyProgress = self.splitCount
		self.buyAmountUnit = self.lastBalance / self.splitCount

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

		assert(self.splitCount - self.curBuyProgress >= 0 )
		return transfered

	def reserve_budget_at_close(self, dayIndex, desiredReserve):

		if(dayIndex == 0):
			return 0

		if(desiredReserve <= self.budget): # already reserved
			return desiredReserve

#--------------------------------------------------------------------------------
#	calc count by recentPrice
#--------------------------------------------------------------------------------
		recentPrice = self.closePrices[dayIndex-1]
		#recentPrice = self.closePrices[dayIndex]
		count = desiredReserve / recentPrice
		if(self.stockCount < count):
			count = self.stockCount
#--------------------------------------------------------------------------------

		if( count > 0):
			self.on_sell(dayIndex, self.closePrices[dayIndex], count)

		self.stockCount -= count
		self.budget += count * self.closePrices[dayIndex] * (1.0 - self.sellFee);

		assert(self.splitCount - self.curBuyProgress >= 0 )
		if(desiredReserve <= self.budget): # finally reserved
			return desiredReserve

		return self.budget


	def post_trade(self, dayIndex):
		self.assetValueHistory.append(self.stockCount * self.closePrices[dayIndex])
		self.balanceHistory.append(self.calc_balance(dayIndex))

	def buy(self, dayIndex):
		if self.is_tradable(dayIndex) == False: 
			self.lastBalance = self.calc_balance(dayIndex)
			return

		if(dayIndex == 0):
			self.lastBalance = self.calc_balance(dayIndex)
			return
		if( self.budget <= 0):
			self.lastBalance = self.calc_balance(dayIndex)
			return

		buyRatio = 1

		if((self.curBuyProgress + buyRatio) > self.splitCount):
			self.lastBalance = self.calc_balance(dayIndex)
			return

		success = self._buy_close(dayIndex, self.buyAmountUnit  * buyRatio)
		if success == True:
			self.curBuyProgress += buyRatio


		self.lastBalance = self.calc_balance(dayIndex)

	def buy_old(self, dayIndex):
		if self.is_tradable(dayIndex) == False: 
			self.lastBalance = self.calc_balance(dayIndex)
			return
		if(dayIndex == 0):
			self.lastBalance = self.calc_balance(dayIndex)
			return
		if( self.budget <= 0):
			self.lastBalance = self.calc_balance(dayIndex)
			return

		buyRatio = self.buyOnRiseRatio

		openPrice = float(self.closePrices[dayIndex-1])
		if self.breakEvenPrice < openPrice:
			if((self.curBuyProgress + buyRatio) >= self.splitCount):
				self.lastBalance = self.calc_balance(dayIndex)
				return

			success = self._buy_close(dayIndex, self.buyAmountUnit * buyRatio)
			if success == True:
				self.curBuyProgress += buyRatio

		buyRatio = 1.0 - self.buyOnRiseRatio
		if((self.curBuyProgress + buyRatio) >= self.splitCount):
			self.lastBalance = self.calc_balance(dayIndex)
			return

		success = self._buy_close(dayIndex, self.buyAmountUnit  * buyRatio)
		if success == True:
			self.curBuyProgress += buyRatio


		self.lastBalance = self.calc_balance(dayIndex)

	def buy_weight(self, dayIndex, weight):
		if self.is_tradable(dayIndex) == False: 
			self.lastBalance = self.calc_balance(dayIndex)
			return
		if(dayIndex == 0):
			self.lastBalance = self.calc_balance(dayIndex)
			return
		if( self.budget <= 0):
			self.lastBalance = self.calc_balance(dayIndex)
			return

		buyRatio = self.buyOnRiseRatio * weight

		openPrice = float(self.closePrices[dayIndex-1])
		if self.breakEvenPrice < openPrice * 0.98 :
			if((self.curBuyProgress + buyRatio) >= self.splitCount):
				self.lastBalance = self.calc_balance(dayIndex)
				return

			success = self._buy_close(dayIndex, self.buyAmountUnit * buyRatio)
			if success == True:
				self.curBuyProgress += buyRatio

		buyRatio = (1.0 - self.buyOnRiseRatio) * weight
		if((self.curBuyProgress + buyRatio) >= self.splitCount):
			self.lastBalance = self.calc_balance(dayIndex)
			return

		success = self._buy_close(dayIndex, self.buyAmountUnit  * buyRatio)
		if success == True:
			self.curBuyProgress += buyRatio


		self.lastBalance = self.calc_balance(dayIndex)
		assert(self.splitCount - self.curBuyProgress >= 0 )

'''

	def sell_on_volatility(self, dayIndex, sampling_duration, profitRate, sellAmountRate):
		sold = 0
		price_and_count = (0, 0)
		if self.is_tradable(dayIndex) == False: return price_and_count

		if self.stockCount == 0:
			return price_and_count


		balanceCount = len(self.assetValueHistory)
		if(balanceCount - 1 < sampling_duration):
			sampling_duration = len(self.assetValueHistory) - 1
			

		if(sampling_duration <= 0):
			return price_and_count 

		avg = 0
		for i in range(0, sampling_duration):
			avg += self.assetValueHistory[balanceCount - 2 - i]

		avg = avg / sampling_duration
		if(avg == 0):
			return price_and_count

		prevBalance = self.lastBalance

		#amount = sellAmountRate * curBalance
		#stockCount = amount / (self.openPrices[dayIndex] * (1.0 - self.sellFee))
		curAssetValue = self.stockCount * self.closePrices[dayIndex]
		stockCount = self.stockCount * sellAmountRate

		if(self.stockCount < stockCount):
			stockCount = self.stockCount

		if (((curAssetValue - avg) / avg + 1) > profitRate ):
			sold = (stockCount * float(self.closePrices[dayIndex])) * (1.0 - self.sellFee)
			price_and_count = (self.closePrices[dayIndex], stockCount)

		elif self.is_take_profit_condition(dayIndex, self.profitRate) : # take profit
			price = self.breakEvenPrice * self.profitRate
			sold = stockCount * price * (1.0 - self.sellFee)
			price_and_count = (price, stockCount)


		if sold > 0:
			self.budget += sold
			self.stockCount -= stockCount
			if(math.fabs(self.stockCount) < EPSILON):
				self.stockCount = 0

			if(self.stockCount == 0):
				self.breakEvenPrice = 0
				
			self.lastBalance = self.budget
			self.on_sell(dayIndex, price_and_count[0], price_and_count[1])
		
		return price_and_count
'''