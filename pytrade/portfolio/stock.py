class Stock:
    def __init__(self, ticker, num_shares, avg_cost):
        self.ticker = ticker
        self.num_shares = num_shares
        self.avg_cost = avg_cost

    def __str__(self):
        return f"{self.ticker}: {self.num_shares} @ {self.avg_cost}"