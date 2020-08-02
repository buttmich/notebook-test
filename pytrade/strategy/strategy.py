class Strategy:
    def __init__(self, name):
        self.name = name
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

    def to_buy(self, portfolio):
        # Look at result of analysis to determine what to buy
        return ["TSLA"]

    def to_sell(self, portfolio):
        # Look at result of analysis to determine what to sell
        return []

    def analysis(self, portfolio):
        # Put data manipulation here that build triggers/metrics.
        pass
    
class Utkarsh_v1(Strategy):
    pass