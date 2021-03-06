import datetime
from ..strategy import Strategy
from ..portfolio import Portfolio
import pandas as pd

class Simulation:
    def __init__(self, context, buy_power, strategy, start_date, end_date = datetime.date.today(), name=""):
        """Simulation initialization

        Args:
            name ([type]): [description]
            start_date ([type]): [description]
            end_date ([type], optional): [description]. Defaults to date.today().
            strategy (Strategy): Strategy to run the simulation.
            context: (Dataframe): Full data set for simulation
        """
        self.name = name
        # rename simulation buy power
        self.buy_power = buy_power
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.context = context
        # Enable passing in portfolio as initial starting point
        self._portfolio = Portfolio(name, None)
    
    def run(self):
        # Initialize Portfolio
        self.initialize()

        current_date = self.start_date

        # Run Simulation
        while(current_date <= self.end_date):
            # print(current_date)
            # Update portfolio context with new date's data
            current_date_mask = current_date >= self.context.index.date
            self._portfolio.context = pd.DataFrame(self.context[current_date_mask])
            to_sell = self.strategy.to_sell(self._portfolio)
            for stock in to_sell:
                name = stock[0]
                percentage = stock[1]
                num_shares = self._portfolio.get_numshares(name) * percentage
                total_price = self._portfolio.context["Adj Close"][name].iloc[-1] * num_shares
                self._portfolio.sell(name, num_shares, total_price, current_date)

            # Add dividend logic

            if round(self._portfolio.buy_power, 3) != 0:
                to_buy = self.strategy.to_buy(self._portfolio)
                amount_buy = self._portfolio.buy_power
                for stock in to_buy:
                    name = stock[0]
                    percentage = stock[1]
                    price = self._portfolio.context["Adj Close"][name].iloc[-1]
                    num_shares = (amount_buy / price) * percentage
                    self._portfolio.buy(name, num_shares, amount_buy * percentage, current_date)

            if len(self.context.index) <= (self.context.index.get_loc(current_date) + 1):
                break
            current_date = self.context.index[self.context.index.get_loc(current_date) + 1]

        print("Finished Simulation")
        print(self._portfolio.report())
        return self._portfolio
        # Do something with results.
    
    def initialize(self):
        self._portfolio.deposit(self.buy_power, self.start_date)

        start_date_mask = self.start_date >= self.context.index.date
        self._portfolio.context = pd.DataFrame(self.context[start_date_mask])

        # Buy stocks and put into Portfolio in accordance with strategy
        to_buy = self.strategy.initialize(self._portfolio)
        for stock in to_buy:
            name = stock[0]
            percentage = stock[1]
            price = self._portfolio.context["Adj Close"][name].iloc[-1]
            num_shares = (self.buy_power / price) * percentage
            self._portfolio.buy(name, num_shares, self.buy_power * percentage, self.start_date)

        print("Finished Initialization")
        print(self._portfolio.report())