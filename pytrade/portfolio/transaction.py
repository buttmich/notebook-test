from enum import Enum

class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    DEPOSIT = "DEPOSIT"
    # Dividens are hard.

class Transaction:
    def __init__(self, date, transaction_type):
        self.date = date
        self.type = transaction_type # Transaction Type

    def __str__(self):
        raise NotImplementedError("Not implemented in base class") # defined in child class


class StockTransaction(Transaction):
    def __init__(self, date, transaction_type, stock):
        if transaction_type != TransactionType.BUY and transaction_type != transaction_type.SELL:
            raise ValueError("Bad Transaction type")
        Transaction.__init__(self, date, transaction_type)
        self.stock = stock

    def __str__(self):
        return f"{self.type.name} {self.date} {self.stock.ticker} {self.stock.num_shares} for {round(self.stock.num_shares * self.stock.avg_cost, 3)}"

class DepositTransaction(Transaction):
    def __init__(self, date, transaction_type, value):
        if transaction_type != TransactionType.DEPOSIT:
            raise ValueError("Bad Transaction type")
        Transaction.__init__(self, date, transaction_type)
        self.value = value

    def __str__(self):
        return f"{self.type.name} {self.date} {self.value}"
    

# class DividendTransaction(Transaction):
#     def __init__(self, fname, lname):
#         Transaction.__init__(self, fname, lname)
#         self.stock
#         self.value

print(object)