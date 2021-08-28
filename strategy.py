from os import curdir
import yfinance as yf
import time
import datetime
import matplotlib.pyplot as plt


class Strategy:
	def __init__(self, stockData, initMoney, splitCount, sellRate, buyRatioOnBearMarket, barrier = 0, logTrade = True):
		self.moneyInPool = initMoney
		self.splitCount = splitCount
		self.sellRate = sellRate
		self.buyAmountUnit = self.moneyInPool / splitCount
		self.buyRatioOnBearMarket = buyRatioOnBearMarket
		self.stockData = stockData
		self.openPrices = stockData['Open']
		self.closePrices = stockData['Close']
		self.highPrices = stockData['High']
		self.stockData['Date'] = stockData.index
		self.logTrade = logTrade

		self.stockCount = 0
		self.stockMeanValue = 0
		self.balanceHistory = []
		self.curBuyProgress = 0
		self.barrier = barrier
		self.tradeFee = 0.0025

	def buy_close(self, close_value, money) :
		#print(money)
		c = int(money / close_value)
		if c == 0:
			return False

		self.stockMeanValue = ( ( self.stockCount * self.stockMeanValue ) + (c * close_value ) ) / (self.stockCount + c)
		self.stockCount += c

		self.moneyInPool -= (close_value * c) * (1.0 + self.tradeFee)

		#print("[BUY ] self.moneyInPool(%d) Count(%d) Mean(%f) BUY(%f)" % (self.moneyInPool, self.stockCount, self.stockMeanValue, close_value))

		return True

	def trade(self, dayIndex ):
		if(dayIndex < self.barrier):
			self.balanceHistory.append( self.moneyInPool )
			return

		size = self.closePrices.size
		if dayIndex >= size:
			assert(0)
			return
		
		if self.moneyInPool - self.buyAmountUnit < 0 :
			self.moneyInPool += (self.stockCount * float(self.closePrices[dayIndex]) ) * (1.0 - self.tradeFee)
			self.buyAmountUnit = self.moneyInPool / self.splitCount

			if(True == self.logTrade):
				print("curBuyProgress(%s) [매도청산] day(%s, %d), moneyInPool(%d) Count(%d) Mean(%f) SELL(%f)" % (int(self.curBuyProgress), self.stockData['Date'][dayIndex], dayIndex, self.moneyInPool, self.stockCount, self.stockMeanValue, float(self.closePrices[dayIndex])))

			self.curBuyProgress = 0
			self.stockCount = 0
			self.stockMeanValue = 0

		elif self.stockMeanValue * self.sellRate < float(self.highPrices[dayIndex]) :
			self.moneyInPool += (self.stockCount * self.stockMeanValue * self.sellRate ) * (1.0 - self.tradeFee)
			self.buyAmountUnit = self.moneyInPool / self.splitCount
			if(True == self.logTrade):
				if dayIndex > 0:
					print("curBuyProgress(%s) [수익청산] day(%s, %d), moneyInPool(%d) Count(%d) Mean(%f) SELL(%f)" % (int(self.curBuyProgress), self.stockData['Date'][dayIndex], dayIndex, self.moneyInPool, self.stockCount, self.stockMeanValue, self.stockMeanValue * self.sellRate))

			self.curBuyProgress = 0
			self.stockCount = 0
			self.stockMeanValue = 0
			

		buyRatio = self.buyRatioOnBearMarket
		if self.stockMeanValue < float(self.closePrices[dayIndex]) :
			sucess = self.buy_close(float(self.closePrices[dayIndex]), self.buyAmountUnit * buyRatio)
			if sucess == True:
				self.curBuyProgress += buyRatio

		buyRatio = 1.0 - self.buyRatioOnBearMarket

		sucess = self.buy_close(float(self.closePrices[dayIndex]), self.buyAmountUnit  * buyRatio )
		if sucess == True:
			self.curBuyProgress += buyRatio

		curBalance = ( self.closePrices[dayIndex] * self.stockCount + self.moneyInPool )
		self.balanceHistory.append( curBalance )
