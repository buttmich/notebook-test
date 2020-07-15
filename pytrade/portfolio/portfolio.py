from .stock import Stock
from .transaction import *
import pickle
from datetime import date

def autosave(func):
    def save_wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if(self.autosave):
            self.save()
            print(f"Saved portfolio: {self.name}")
        return res
    return save_wrapper

class Portfolio:
    def __init__(self, name, data):
        self.name = name   # P
        self.buy_power = 0
        self.stocks = [] # List of Stocks
        self.context = data # Data
        self.autosave = False
        self.logging = True
        self.history = [] # List of Transactions

    @autosave
    def deposit(self, value, trans_date = date.today()):
        self.buy_power += value
        transaction = DepositTransaction(trans_date, TransactionType.DEPOSIT, value)
        self.history.append(transaction)
        self.log(transaction)

    @autosave
    def buy(self, ticker, num_shares, total_cost, trans_date = date.today()):
        stock_in_portfolio = next((s for s in self.stocks if s.ticker == ticker), None)

        if round(self.buy_power - total_cost, 3) >= 0 :
            self.buy_power = self.buy_power - total_cost
        else:
            raise ValueError("Cannot buy stocks. Not enough buy power")

        if stock_in_portfolio is None:
            stock = Stock(ticker, num_shares, total_cost)
            self.stocks.append(stock)
        else:
            stock = stock_in_portfolio
            stock.avg_cost = (stock.avg_cost * stock.num_shares + total_cost) / (stock.num_shares + num_shares)
            stock.num_shares = stock.num_shares + num_shares

        new_stock = Stock(ticker, num_shares, total_cost)
        transaction = StockTransaction(trans_date, TransactionType.BUY, new_stock)
        self.history.append(transaction)
        self.log(transaction)
        # self.log("BUY ", f"{trans_date} {ticker} {num_shares} for {round(total_cost, 3)}")
       
    @autosave
    def sell(self, ticker, num_shares, total_price, trans_date = date.today()):
        stock_to_sell = next((s for s in self.stocks if s.ticker == ticker), None)
        if stock_to_sell is not None:
            if stock_to_sell.num_shares - num_shares >= 0:
                stock_to_sell.num_shares = stock_to_sell.num_shares - num_shares
            else:
                raise ValueError("Cannot sell more stock than you own")
            if stock_to_sell.num_shares == 0:
                self.stocks.remove(stock_to_sell)
            self.buy_power = self.buy_power + total_price
        else:
            raise ValueError("Cannot sell stock that you don't own")

        sold_stock = Stock(ticker, num_shares, total_price)
        transaction = StockTransaction(trans_date, TransactionType.SELL, sold_stock)
        self.history.append(transaction)
        self.log(transaction)

    def current_value(self):
        stock_value = 0
        for s in self.stocks:
            price = self.context[s.ticker].iloc[-1]
            stock_value = stock_value + price * s.num_shares
        return round(stock_value + self.buy_power, 3)

    def report(self):
        print(f"Current Value = {self.current_value()}")
        print("-" * 30)
        self.stocks.sort(key = lambda x : x.num_shares * self.context[x.ticker].iloc[-1], reverse = True)
        for s in self.stocks:
            print(f"{s} {round(self.context[s.ticker].iloc[-1], 3)}")

    def save(self):
        filename = f"{self.name}.pkl"
        with open(filename, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def log(self, transaction):
        if self.logging:
            filename = f"{self.name}.log"
            with open(filename, 'a') as logfile:
                nl = '\n'
                logfile.write(f"{transaction}{nl}")

    @staticmethod
    def load(name, context = None):
        filename = f"{name}.pkl"
        with open(filename, 'rb') as objfile:
            portfolio =  pickle.load(objfile)
            if context is not None:
                portfolio.context = context
            return portfolio