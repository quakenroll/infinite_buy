from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt


class Strategy:
	def __init__(self, stockData, budget, splitCount, sellRate, buyOnDropRatio, delayTrade = 0, buyMoreUnderLossRatio = 0.00, logTrade = True, losscutRate = 1.0):
		self.budget = budget
		self.lastBalance = budget 
		self.snapshotBalance = budget
		self.splitCount = splitCount
		self.sellRate = sellRate
		self.buyAmountUnit = self.budget / splitCount
		self.buyOnDropRatio = buyOnDropRatio
		self.stockData = stockData
		self.openPrices = stockData['Open']
		self.closePrices = stockData['Close']
		self.highPrices = stockData['High']
		self.lowPrices = stockData['Low']
		self.stockData['Date'] = stockData.index
		self.logTrade = logTrade
		self.losscutRate = losscutRate

		self.stockCount = 0
		self.stockMeanValue = 0
		self.balanceHistory = []
		self.curBuyProgress = 0
		self.delayTrade = delayTrade
		self.tradeFee = 0.0025
		self.buyMoreUnderLossRatio = buyMoreUnderLossRatio
		self.score = 0
		self.recentScoreWeight = 1.0
		self.lastScore = 0
		self.scoreHistory = []

	def _buy_close(self, close_value, money) :
		#print(money)
		if(money > self.budget):
			money = self.budget

		c = (money / close_value)
		if c == 0:
			return False


		self.stockMeanValue = ( ( self.stockCount * self.stockMeanValue ) + (c * close_value ) ) / (self.stockCount + c)
		self.stockCount += c

		self.budget -= (close_value * c) * (1.0 + self.tradeFee)

		#print("[BUY ] self.budget(%d) Count(%d) Mean(%f) BUY(%f)" % (self.budget, self.stockCount, self.stockMeanValue, close_value))

		return True

	def is_tradable(self, dayIndex):
		if(dayIndex < self.delayTrade):
			self.balanceHistory.append( self.budget )
			return False

		size = self.closePrices.size
		if dayIndex >= size:
			assert(0)
			return False
		
		return True

	def calcScore(self, currentBalance, prevBalance):
		if(prevBalance == 0):
			self.score = -10000000000000000000000;

		increase = 0
		if(currentBalance > prevBalance):
			increase = (currentBalance - prevBalance) / prevBalance
		else:
			increase = (currentBalance - prevBalance) / currentBalance
		self.score = self.score + increase * self.recentScoreWeight

	def is_losscut_condition(self, dayIndex):
		return self.budget - self.buyAmountUnit < 0 and self.is_take_profit_condition(dayIndex, self.losscutRate)
	
	def is_take_profit_condition(self, dayIndex, sellRate):
		return self.stockMeanValue * sellRate < float(self.highPrices[dayIndex])

	def calc_balance(self):
		return self.stockMeanValue * self.stockCount + self.budget

	def calc_score2(self, dayIndex):
		currentBalance = self.calc_balance()
		increase = (currentBalance - self.snapshotBalance) / currentBalance
		self.snapshotBalance = currentBalance
		self.lastScore = increase

		return self.lastScore

	def sell_all_when_done(self, dayIndex ):
		if self.is_tradable(dayIndex) == False: return

		prevBalance = self.lastBalance
		profitTakingMoney = 0
		lossCutMoney = 0

		liquidation = 0
		if self.is_losscut_condition(dayIndex) : # lossCut
			liquidation = (self.stockCount * float(self.closePrices[dayIndex]))

		elif self.is_take_profit_condition(dayIndex, self.sellRate) : # take profit
			liquidation = self.stockCount * self.stockMeanValue * self.sellRate

		if liquidation > 0:
			self.budget += liquidation  * (1.0 - self.tradeFee)
			self.buyAmountUnit = self.budget / self.splitCount
			self.curBuyProgress = 0
			buyProgress = self.curBuyProgress
			self.stockCount = 0
			self.stockMeanValue = 0
			self.lastBalance = self.budget
			self.calcScore(self.lastBalance, prevBalance)



	def fillBudget(self, amount):
		self.budget += amount
		self.lastBalance += amount
		self.balanceHistory[-1] = self.lastBalance

	def takeBudget(self, desiredAmount):
		took = 0
		if(self.budget > desiredAmount):
			took = desiredAmount
		else:
			took = self.budget

		self.budget -= took
		self.lastBalance -= took
		self.balanceHistory[-1] = self.lastBalance 
		return took


	def buy(self, dayIndex):
		if(self.curBuyProgress >= self.splitCount or self.budget <= 0):
			self.lastBalance = ( self.closePrices[dayIndex] * self.stockCount + self.budget )
			self.balanceHistory.append( self.lastBalance )
			self.scoreHistory.append(self.calc_score2(dayIndex))
			return

		buyRatio = self.buyOnDropRatio
		if self.stockMeanValue < float(self.closePrices[dayIndex]) * (1.0 - self.buyMoreUnderLossRatio) :
			sucess = self._buy_close(float(self.closePrices[dayIndex]), self.buyAmountUnit * buyRatio)
			if sucess == True:
				self.curBuyProgress += buyRatio

		buyRatio = 1.0 - self.buyOnDropRatio

		sucess = self._buy_close(float(self.closePrices[dayIndex]), self.buyAmountUnit  * buyRatio)
		if sucess == True:
			self.curBuyProgress += (buyRatio)


		self.lastBalance = ( self.closePrices[dayIndex] * self.stockCount + self.budget )
		self.balanceHistory.append( self.lastBalance )
		self.scoreHistory.append(self.calc_score2(dayIndex))
