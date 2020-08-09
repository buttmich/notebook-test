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

    def analysis(self, portfolio, analysis_date):
        pass
    