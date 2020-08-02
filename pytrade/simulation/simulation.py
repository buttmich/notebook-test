from datetime import date, datetime
from ..strategy import Strategy
from ..portfolio import Portfolio

class Simulation:
    def __init__(self, context, buy_power, strategy, start_date, name="", end_date = date.today()):
        """Simulation initialization

        Args:
            name ([type]): [description]
            start_date ([type]): [description]
            end_date ([type], optional): [description]. Defaults to date.today().
            strategy (Strategy): Strategy to run the simulation.
        """
        self.name = name
        self.buy_power = buy_power
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        # Enable passing in portfolio as initial starting point
        self._portfolio = Portfolio(name, context)
    
    def run(self):
        # Initialize Portfolio
        self.initialize(self.buy_power)
        
        current_date = self.start_date

        # Run Simulation
        while(current_date <= self.end_date):
            print(current_date)
            # Apply strategy actions / transactions

                #Check to see if stocks need to be sold
                    
                    # Sell off stocks based on strategy
                
                # Update buy power (dividends/new deposit)
                
                # Buy new stocks
            current_date += datetime.timedelta(days=1)

        return self._portfolio
        # Do something with results.
    
    def initialize(self, buy_power):
        # Buy stocks and put into Portfolio in accordance with strategy
        pass