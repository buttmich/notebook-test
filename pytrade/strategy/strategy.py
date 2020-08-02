from ..portfolio import Portfolio
import pandas as pd

class Strategy:
    def __init__(self, name):
        self.name = name
        pass

    def initialize(self, portfolio):
        pass

    def to_buy(self, portfolio):
        pass

    def to_sell(self, portfolio):
        pass

    def analysis(self, portfolio):
        pass


class TSLA_Strategy(Strategy):
    def __init__(self, name):
        Strategy.__init__(self, name)

    def initialize(self, portfolio):
        return [("TSLA", 0.5)]
    
    def to_buy(self, portfolio):
        # Look at result of analysis to determine what to buy
        if "TSLA" in portfolio.stocks and portfolio.context["Close"]["TSLA"].iloc[-1] < 1500:
            return []
        return [("TSLA", 1)]

    def to_sell(self, portfolio):
        # Look at result of analysis to determine what to sell
        if "TSLA" in portfolio.stocks and portfolio.context["Close"]["TSLA"].iloc[-1] > 1500:
            return [("TSLA", 1)]
        return []

    def analysis(self, portfolio):
        # Put data manipulation here that build triggers/metrics.
        self.results = pd.DataFrame()
    
class Utkarsh_v1(Strategy):
    pass