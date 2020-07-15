class Stock:
    def __init__(self, ticker, num_shares, total_cost):
        self.ticker = ticker
        self.num_shares = num_shares
        self.avg_cost = total_cost / num_shares

    def __str__(self):
        return f"{self.ticker}: {self.num_shares} @ {round(self.avg_cost, 3)}"