from .stock import Stock
import pickle

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
        self.stocks = [] # List of stocks
        self.context = data # Data
        self.autosave = False
        self.logging = True

    @autosave
    def deposit(self, value):
        self.buy_power += value
        self.log("DEP.", f"{value}")

    @autosave
    def buy(self, ticker, num_shares, cost_per_share):
        stock_in_portfolio = next((s for s in self.stocks if s.ticker == ticker), None)
        total_cost = num_shares * cost_per_share

        if stock_in_portfolio is None:
            stock = Stock(ticker, num_shares, cost_per_share)
            self.stocks.append(stock)
        else:
            stock = stock_in_portfolio
            stock.avg_cost = ( stock.avg_cost * stock.num_shares + total_cost ) / (stock.num_shares + num_shares)
            stock.num_shares = stock.num_shares + num_shares

        if self.buy_power - total_cost >= 0 :
            self.buy_power = self.buy_power - total_cost
        else:
            raise ValueError("Cannot buy stocks. Not enough buy power")
        self.log("BUY ", f"{ticker} {num_shares} @ {cost_per_share}")
       
    @autosave
    def sell(self, ticker, num_shares, price):
        stock_to_sell = next((s for s in self.stocks if s.ticker == ticker), None)
        if stock_to_sell is not None:
            if stock_to_sell.num_shares - num_shares >= 0:
                stock_to_sell.num_shares = stock_to_sell.num_shares - num_shares
            else:
                raise ValueError("Cannot sell more stock than you own")
            if stock_to_sell.num_shares == 0:
                self.stocks.remove(stock_to_sell)
            self.buy_power = self.buy_power + num_shares * price
        else:
            raise ValueError("Cannot sell stock that you don't own")
        self.log("SELL", f"{ticker} {num_shares} @ {price}")

    def current_value(self):
        stock_value = 0
        for s in self.stocks:
            price = self.context[s.ticker].iloc[-1]
            stock_value = stock_value + price * s.num_shares
        return stock_value + self.buy_power

    def report(self):
        for s in self.stocks:
            print(s)

    def save(self):
        filename = f"{self.name}.pkl"
        with open(filename, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def log(self, log_type, message):
        if self.logging:
            filename = f"{self.name}.log"
            with open(filename, 'a') as logfile:
                nl = '\n'
                logfile.write(f"{log_type}: {message}{nl}")

    @staticmethod
    def load(name, context = None):
        filename = f"{name}.pkl"
        with open(filename, 'rb') as objfile:
            portfolio =  pickle.load(objfile)
            if context is not None:
                portfolio.context = context
            return portfolio


