import pandas as pd
import yfinance as yf


def get_data(period="2y", reload=True):
    """
    """
    df_close = None
    if reload:
        f = open("./ticker.csv", "r")
        tickers = f.read().split(",")
        df = yf.download(" ".join(tickers), period=period)
        df_close = df["Adj Close"]
    else:
        df_close = pd.read_pickle("./latest.pkl")

    df_close.to_pickle("./latest.pkl")
    return df_close

def calculate_ratio(df, index="^GSPC",):
    """
    """
    latest_index = df[index].iloc[-1]
    ratios = df.iloc[:].div(df[index], axis=0) * latest_index # Better way to do this?
    return ratios
