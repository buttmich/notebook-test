import pandas as pd
import datetime
import numpy as np

def run(ratios):
    three_wk_mask = datetime.date.today()-ratios.index.date <= datetime.timedelta(days=21)
    three_m_mask = datetime.date.today()-ratios.index.date <= datetime.timedelta(days=91)
    one_yr_mask = datetime.date.today()-ratios.index.date <= datetime.timedelta(days=365)
    #st_multiplier = 2

    # Format Analysis
    analysis = pd.DataFrame(ratios.iloc[-1])
    analysis.rename({analysis.columns[0]:"latest"}, axis = 1, inplace = True) # Better way to do this?
    analysis["three_wk_high"] = pd.DataFrame(ratios[three_wk_mask].max())
    analysis["three_wk_low"] = pd.DataFrame(ratios[three_wk_mask].min())
    analysis["three_m_high"] = pd.DataFrame(ratios[three_m_mask].max())
    analysis["three_m_low"] = pd.DataFrame(ratios[three_m_mask].min())
    analysis["one_yr_high"] = pd.DataFrame(ratios[one_yr_mask].max())
    analysis["one_yr_low"] = pd.DataFrame(ratios[one_yr_mask].min())

    # Better way to do this?
    analysis["three_wk_range"] = (analysis["latest"] - analysis["three_wk_low"]) / ((analysis["three_wk_high"] - analysis["three_wk_low"]))
    analysis["three_m_range"] = (analysis["latest"] - analysis["three_m_low"]) / ((analysis["three_m_high"] - analysis["three_m_low"]))
    analysis["one_yr_range"] = (analysis["latest"] - analysis["one_yr_low"]) / ((analysis["one_yr_high"] - analysis["one_yr_low"]))
    analysis["short_term_stochastic"] = analysis["one_yr_range"] - analysis["three_wk_range"]
    analysis["long_term_stochastic"] = analysis["one_yr_range"] - analysis["three_m_range"]

    #analysis["short_term_potential"] = 1-analysis["latest"] / analysis["three_wk_high"]
    #analysis["long_term_potential"] = 1-analysis["latest"] / analysis["three_m_high"]
    st_equilibrium = (analysis["three_wk_low"] * analysis["one_yr_high"] - analysis["one_yr_low"] * analysis["three_wk_high"]) / \
        (analysis["one_yr_high"] - analysis["three_wk_high"] + analysis["three_wk_low"] - analysis["one_yr_low"])
    real_st_potential = st_equilibrium / analysis["latest"] - 1
    analysis["st_potential"] = real_st_potential
    lt_equilibrium = (analysis["three_m_low"] * analysis["one_yr_high"] - analysis["one_yr_low"] * analysis["three_m_high"]) / \
        (analysis["one_yr_high"] - analysis["three_m_high"] + analysis["three_m_low"] - analysis["one_yr_low"])
    real_lt_potential = lt_equilibrium / analysis["latest"] - 1
    analysis["lt_potential"] = real_lt_potential
    st_multiplier = abs((1 - analysis["short_term_stochastic"]) / real_st_potential).min()
    analysis["short_term_metric"] = analysis["short_term_stochastic"] + st_multiplier * real_st_potential
    lt_multiplier = abs((1 - analysis["long_term_stochastic"]) / real_lt_potential).min()
    analysis["long_term_metric"] = analysis["long_term_stochastic"] + lt_multiplier * real_lt_potential
    # Save file

    # Return output
    return analysis
