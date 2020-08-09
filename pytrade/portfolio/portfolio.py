from .stock import Stock
from .transaction import DepositTransaction, StockTransaction, DividendTransaction, TransactionType
import pickle
from datetime import date
import scipy.optimize as opt
import pandas as pd

def autosave(func):
    """Decorator that saves a portfolio after an operation if the autosave property is True.

    Args:
        func (function): function to wrap with autosave decorator. Function is invoked before save check.
    """
    def save_wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if(self.autosave):
            self.save()
            print(f"Saved portfolio: {self.name}")
        return res
    return save_wrapper

class Portfolio:
    def __init__(self, name, data):
        """Portfolio initializer.

        Args:
            name (str): Portfolio name. Used to name save and log files.
            data (DataFram): Current stock dataframe to use as context.
        """
        self.name = name   # P
        self.buy_power = 0
        self.stocks = [] # List of Stocks
        self.context = data # DataFrame
        self.autosave = False
        self.logging = True
        self.history = [] # List of Transactions

    @autosave
    def deposit(self, value, trans_date=date.today()):
        """Deopsit new cash into a portfolio. Increases the buy power of a portfolio.

        Args:
            value (number): Amount added to portfolio.
            trans_date (datetime, optional): Date of deposit. Defaults to date.today().
        """
        self.buy_power += value
        transaction = DepositTransaction(trans_date, TransactionType.DEPOSIT, value)
        self.history.append(transaction)
        self.log(transaction)

    @autosave
    def buy(self, ticker, num_shares, total_cost, trans_date=date.today()):
        """Buy a new stock using a portfolio's buy power.

        Args:
            ticker (str): Stock identifier
            num_shares (number): Number of shares of stock "ticker" to buy
            total_cost (number): Cost of buying "num_shares" of stock "ticker"
            trans_date (datetime, optional): Date that the stock purchase occurred. Defaults to date.today().

        Raises:
            ValueError: When a portfolio doesn't have enough buy power to buy the desired stocks.
        """
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
        """Sell shares of a stock from a portfolio's stock list.

        Args:
            ticker (str): Stock Identifier 
            num_shares (number): Number of shares of stock "ticker" to be sold.
            total_price (number): Total value added to buy power after selling "num_shares" of stock "ticker".
            trans_date (datetime, optional): Date that the stock sell occurred. Defaults to date.today().

        Raises:
            ValueError: Cannot sell stocks that a portfolio doesn't own.
        """
        stock_to_sell = next((s for s in self.stocks if s.ticker == ticker), None)
        if stock_to_sell is not None:
            if round(stock_to_sell.num_shares - num_shares, 3) >= 0:
                stock_to_sell.num_shares = stock_to_sell.num_shares - num_shares
            else:
                raise ValueError("Cannot sell more stock than you own")
            if round(stock_to_sell.num_shares, 3) == 0:
                self.stocks.remove(stock_to_sell)
            self.buy_power = self.buy_power + total_price
        else:
            raise ValueError("Cannot sell stock that you don't own")

        sold_stock = Stock(ticker, num_shares, total_price)
        transaction = StockTransaction(trans_date, TransactionType.SELL, sold_stock)
        self.history.append(transaction)
        self.log(transaction)

    @autosave
    def sell_all(self, ticker, total_price, trans_date=date.today()):
        """[summary]

        Args:
            ticker ([type]): [description]
            total_price ([type]): [description]
            trans_date ([type], optional): [description]. Defaults to date.today().

        Raises:
            ValueError: [description]
        """
        num_shares = self.get_numshares(ticker)
        stock_to_sell = next((s for s in self.stocks if s.ticker == ticker), None)
        if stock_to_sell is not None:
            stock_to_sell.num_shares = 0
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
        """Apply a stock dividend to a portfolio.

        Args:
            ticker (str): Stock Identifier
            amount (number): Total dividend returned for owning a stock.
            ex_dividend_date (datetime): [description]
            trans_date (datetime, optional): [description]. Defaults to date.today().

        Raises:
            ValueError: Must own a stock to get a dividend.
        """
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

    def get_numshares(self, ticker):
        """[summary]

        Returns:
            [type]: [description]
        """
        stock = next((s for s in self.stocks if s.ticker == ticker), None)
        return stock.num_shares

    def max_holding(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        max_holding = 0
        for stock in self.stocks:
            holding = stock.num_shares * self.context["Adj Close"][stock.ticker].iloc[-1]
            if holding > max_holding:
                max_holding = holding
        return max_holding

    def current_value(self):
        """Calculates the current value of a portfolio by looking up lastes prices for the stocks in the stock list.

        Returns:
            number: Current value of a portfolio
        """
        stock_value = 0
        for s in self.stocks:
            price = self.context["Adj Close"][s.ticker].iloc[-1]
            stock_value = stock_value + price * s.num_shares
        return round(stock_value + self.buy_power, 3)

    def market_current_value(self, index="^GSPC"):
        """Calculates the current value of a portfolio if all deposists were invested in the index. 
           Assumes all deposits were immediately invested in the index (using partial shares).

        Args:
            index (str, optional): Index to compare against. Defaults to "^GSPC".

        Returns:
            number: 
        """
        market_shares = 0
        for trans in self.history:
            market_shares = market_shares + trans.get_deposit() / self.context["Adj Close"][index][trans.date]
        return round(market_shares * self.context["Adj Close"][index].iloc[-1], 3)

    def calc_rate_of_return(self):
        """Calculates rate of return using an optimization package.

        Returns:
            number: Rate of return of the portfolio.
        """
        return round(opt.fsolve(lambda rate: self.value_diff(rate), 1)[0], 3)
    
    def calc_market_rate_of_return(self, index="^GSPC"):
        """Cacluates a rate of return for a naive market strategy.

        Args:
            index (str, optional): [description]. Defaults to "^GSPC".

        Returns:
            number: Rate of return for a portfolio using a naive strategy.
        """
        return round(opt.fsolve(lambda rate: self.value_diff(rate, index), 1)[0], 3)

    def value_diff(self, rate, index=None):
        """Helper method to produce the rate of return equations.

        Args:
            rate (number): guess made by solving method.
            index (str, optional): Index to buid rate of return for. Defaults to None.

        Returns:
            number: difference between value generated using guessed rate and a portfolios current value.
        """
        value = 0
        for trans in self.history:
            value = value + trans.get_deposit() * (rate ** ((date.today() - trans.date).days / 365))
        return value - (self.current_value() if index is None else self.market_current_value(index))
    
    def report(self):
        """Prints a report of a portfiolo.
        """
        print(f"Current Value = {self.current_value()}")
        print(f"Buy Power = {round(self.buy_power, 3)}")
        print("-" * 30)
        self.stocks.sort(key = lambda x : x.num_shares * self.context["Adj Close"][x.ticker].iloc[-1], reverse = True)
        for s in self.stocks:
            current_value = round(self.context["Adj Close"][s.ticker].iloc[-1], 3)
            print(f"{s} {current_value}")

    def save(self):
        """Saves a portfolio by dumping the object to a pickle file.
        """
        filename = f"{self.name}.pkl"
        with open(filename, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def log(self, transaction):
        """Writes a message to a log file indicating a transaction that occurred.

        Args:
            transaction (Transaction): Transaction that occurred on a portfolio.
        """
        if self.logging:
            filename = f"{self.name}.log"
            with open(filename, 'a') as logfile:
                nl = '\n'
                logfile.write(f"{transaction}{nl}")

    @staticmethod
    def load(name, context=None):
        """Loads a given portfolio by reading it from a pickle file.

        Args:
            name (str): Name of portfolio to open.
            context (Dataframe, optional): Curret stock prices to load into the portfolio. Defaults to None.

        Returns:
            Portfolio: Portfolio object loaded from "name".pkl.
        """
        filename = f"{name}.pkl"
        with open(filename, 'rb') as objfile:
            portfolio =  pickle.load(objfile)
            if context is not None:
                portfolio.context = context
            return portfolio
