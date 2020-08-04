from ..portfolio import Portfolio
import pandas as pd
import datetime

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


class TSLA_Strategy(Strategy):
    def __init__(self, name):
        Strategy.__init__(self, name)

    def initialize(self, portfolio, start_date):
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
    
class Utkarsh_v1_short(Strategy):
    def __init__(self, name):
        Strategy.__init__(self, name)

    def initialize(self, portfolio):
        start_date = portfolio.context.index.date[-1]
        metric = self.analysis(portfolio.context["Adj Close"], start_date)
        metric.sort_values(by="metric",ascending=False,inplace=True)
        
        return [(metric.index[0], 13/32), (metric.index[1], 8/32), (metric.index[2], 5/32), (metric.index[3], 3/32), \
            (metric.index[4], 2/32), (metric.index[5], 1/32)]
    
    def to_buy(self, portfolio):
        # Look at result of analysis to determine what to buy
        start_date = portfolio.context.index.date[-1]
        metric = self.analysis(portfolio.context["Adj Close"], start_date)
        metric.sort_values(by="metric",ascending=False,inplace=True)
        if portfolio.buy_power > portfolio.max_holding():
            return [(metric.index[0], 2/3), (metric.index[1], 1/3)]
        else:
            return [(metric.index[0], 1)]

    def to_sell(self, portfolio):
        # Look at result of analysis to determine what to sell
        current_date = portfolio.context.index.date[-1]
        metric = self.analysis(portfolio.context["Adj Close"], current_date)
        sell_list = []
        for stock in portfolio.stocks:
            if round(metric["metric"][stock.ticker], 3) <= 0:
                sell_list.append((stock.ticker, 1))
        return sell_list

    def analysis(self, adj_close_df, analysis_date):
        # Put data manipulation here that build triggers/metrics.
        ratios = self.calculate_ratio(adj_close_df)

        three_wk_mask = analysis_date-ratios.index.date <= datetime.timedelta(days=21)
        one_yr_mask = analysis_date-ratios.index.date <= datetime.timedelta(days=365)
        #st_multiplier = 2

        # Format Analysis
        analysis = pd.DataFrame(ratios.iloc[-1])
        analysis.rename({analysis.columns[0]:"latest"}, axis = 1, inplace = True) # Better way to do this?
        analysis["three_wk_high"] = pd.DataFrame(ratios[three_wk_mask].max())
        analysis["three_wk_low"] = pd.DataFrame(ratios[three_wk_mask].min())
        analysis["one_yr_high"] = pd.DataFrame(ratios[one_yr_mask].max())
        analysis["one_yr_low"] = pd.DataFrame(ratios[one_yr_mask].min())

        analysis["three_wk_range"] = (analysis["latest"] - analysis["three_wk_low"]) / ((analysis["three_wk_high"] - analysis["three_wk_low"]))
        analysis["one_yr_range"] = (analysis["latest"] - analysis["one_yr_low"]) / ((analysis["one_yr_high"] - analysis["one_yr_low"]))
        analysis["stochastic_difference"] = analysis["one_yr_range"] - analysis["three_wk_range"]

        equilibrium = (analysis["three_wk_low"] * analysis["one_yr_high"] - analysis["one_yr_low"] * analysis["three_wk_high"]) / \
            (analysis["one_yr_high"] - analysis["three_wk_high"] + analysis["three_wk_low"] - analysis["one_yr_low"])
        analysis["potential"] = equilibrium / analysis["latest"] - 1

        st_multiplier = abs((1 - analysis["stochastic_difference"]) / analysis["potential"]).min()
        analysis["metric"] = analysis["stochastic_difference"] + analysis["potential"] * st_multiplier

        # Return output
        return analysis

    def calculate_ratio(self, df, index="^GSPC",):
        """
        """
        latest_index = df[index][-1]
        ratios = df.iloc[:].div(df[index], axis=0) * latest_index # Better way to do this?
        return ratios