from enum import Enum

class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    DEPOSIT = "DEPOSIT"
    DIVIDEND = "DIVIDEND"

class Transaction:
    def __init__(self, date, transaction_type):
        self.date = date
        self.type = transaction_type # Transaction Type

    def get_deposit(self):
        raise NotImplementedError("Not implemented in base class") # defined in child class

    def __str__(self):
        raise NotImplementedError("Not implemented in base class") # defined in child class


class StockTransaction(Transaction):
    def __init__(self, date, transaction_type, stock):
        if transaction_type != TransactionType.BUY and transaction_type != transaction_type.SELL:
            raise ValueError("Bad Transaction type")
        Transaction.__init__(self, date, transaction_type)
        self.stock = stock

    def get_deposit(self):
        return 0

    def __str__(self):
        return f"{self.type.name} {self.date} {self.stock.ticker} {self.stock.num_shares} for {round(self.stock.num_shares * self.stock.avg_cost, 3)}"

class DepositTransaction(Transaction):
    def __init__(self, date, transaction_type, value):
        if transaction_type != TransactionType.DEPOSIT:
            raise ValueError("Bad Transaction type")
        Transaction.__init__(self, date, transaction_type)
        self.value = value

    def get_deposit(self):
        return self.value

    def __str__(self):
        return f"{self.type.name} {self.date} {self.value}"
    

class DividendTransaction(Transaction):
    def __init__(self, date, transaction_type, amount, ticker):
        if transaction_type != TransactionType.DIVIDEND:
            raise ValueError("Bad Transaction type")
        Transaction.__init__(self, date, transaction_type)
        self.dividend = amount
        self.ticker = ticker

    def get_deposit(self):
        return 0

    def __str__(self):
        return f"{self.type.name} {self.date} {self.ticker} {self.dividend}"