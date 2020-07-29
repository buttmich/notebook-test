from .stock import Stock
from .transaction import DepositTransaction, StockTransaction, DividendTransaction, TransactionType
import pickle
from datetime import date
import scipy.optimize as opt
import pandas as pd

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
        self.context = data # DataFrame
        self.autosave = False
        self.logging = True
        self.history = [] # List of Transactions

    @autosave
    def deposit(self, value, trans_date=date.today()):
        self.buy_power += value
        transaction = DepositTransaction(trans_date, TransactionType.DEPOSIT, value)
        self.history.append(transaction)
        self.log(transaction)

    @autosave
    def buy(self, ticker, num_shares, total_cost, trans_date=date.today()):
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
       
    @autosave
    def sell(self, ticker, num_shares, total_price, trans_date=date.today()):
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

    @autosave
    def dividend(self, ticker, amount, ex_dividend_date, trans_date=date.today()):
        dividend_stock = next((s for s in self.stocks if s.ticker == ticker), None)
        if dividend_stock is not None:
            self.buy_power = self.buy_power + amount
            dividend_per_share = amount / dividend_stock.num_shares
            pre_dividend_close = self.context["Close"][ticker][self.context.index.get_loc(ex_dividend_date)-1]
            adj_factor = 1 - dividend_per_share / pre_dividend_close
            dividend_stock.avg_cost = dividend_stock.avg_cost * adj_factor
        else:
            raise ValueError("Cannot get dividend on stock that you don't own")

        transaction = DividendTransaction(trans_date, TransactionType.DIVIDEND, amount, ticker)
        self.history.append(transaction)
        self.log(transaction)    

    def current_value(self):
        stock_value = 0
        for s in self.stocks:
            price = self.context["Adj Close"][s.ticker].iloc[-1]
            stock_value = stock_value + price * s.num_shares
        return round(stock_value + self.buy_power, 3)

    def market_current_value(self, index="^GSPC"):
        market_shares = 0
        for trans in self.history:
            market_shares = market_shares + trans.get_deposit() / self.context["Adj Close"][index][trans.date]
        return round(market_shares * self.context["Adj Close"][index][date.today()], 3)

    def calc_rate_of_return(self):
        return round(opt.fsolve(lambda rate: self.value_diff(rate), 1)[0], 3)
    
    def calc_market_rate_of_return(self, index="^GSPC"):
        return round(opt.fsolve(lambda rate: self.value_diff(rate, index), 1)[0], 3)

    def value_diff(self, rate, index=None):
        value = 0
        for trans in self.history:
            value = value + trans.get_deposit() * (rate ** ((date.today() - trans.date).days / 365))
        return value - (self.current_value() if index is None else self.market_current_value(index))
    
    def report(self):
        print(f"Current Value = {self.current_value()}")
        print(f"Buy Power = {round(self.buy_power, 3)}")
        print("-" * 30)
        self.stocks.sort(key = lambda x : x.num_shares * self.context["Adj Close"][x.ticker].iloc[-1], reverse = True)
        for s in self.stocks:
            current_value = round(self.context["Adj Close"][s.ticker].iloc[-1], 3)
            print(f"{s} {current_value}")

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
    def load(name, context=None):
        filename = f"{name}.pkl"
        with open(filename, 'rb') as objfile:
            portfolio =  pickle.load(objfile)
            if context is not None:
                portfolio.context = context
            return portfolio
