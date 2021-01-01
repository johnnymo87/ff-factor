from lib.factor_returns import FactorReturns
from lib.investment_returns import InvestmentReturns
# To round off a long float
import math
# To draw plots
import matplotlib.pyplot as plt
# To make a directory if it does not exist
import os
# Pandas to read csv file and other things
import pandas as pd
# To prepare design matrices using R-like formulas
from patsy import dmatrices
# Statsmodels to run our multiple regression model
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
# To sleep in between requests to yahoo finance
import time

FORMULA = """
port_excess ~ market_minus_risk_free + small_minus_big + high_minus_low + robust_minus_weak + conservative_minus_aggressive + winners_minus_losers
"""

def run_reg_model(market_type, ticker, minimum_months=12):
    # Get FF data
    ff_data = FactorReturns.fetch(market_type)
    ff_first = ff_data.occurred_at[0]
    ff_last = ff_data.occurred_at[len(ff_data.occurred_at) - 1]

    ticker_data = InvestmentReturns.fetch(ticker, ff_first, ff_last)
    if len(ticker_data) < minimum_months:
        print(f'Less than {minimum_months} months of data, skipping!')
        return

    # Join the FF and ticker data
    all_data = pd.merge(ticker_data, ff_data, on='occurred_at')
    all_data['port_excess'] = all_data.percentage_change - all_data.risk_free

    # Prepare endogenous and exogenous data sets
    endogenous, exogenous = dmatrices(FORMULA, data=all_data, return_type='dataframe')

    # Draw rolling OLS plot
    rolling_ols_plot(endogenous, exogenous, minimum_months)

    # Run non-rolling OLS regression
    non_rolling_ols_regression(endogenous, exogenous)

def rolling_ols_plot(endogenous, exogenous, minimum_months):
    rolling_ols_results = RollingOLS(endogenous, exogenous, window=minimum_months).fit()
    variables = [c for c in exogenous.columns if c != 'Intercept']
    fig, _ = plt.subplots(figsize=(18, 10))
    rolling_ols_results.plot_recursive_coefficient(fig=fig, variables=variables)
    head, *tail = fig.axes
    fill_percentages = []
    for ax in tail:
        ax.set_ylim(0, 1)
        middle_line, lower_line, _ = ax.get_lines()
        lower_line.remove()
        xs, ys = middle_line.get_data()
        normalized_ys = [max(min(y, 1), 0) for y in ys]
        alpha = sum(normalized_ys) / len(normalized_ys)
        middle_line.set_alpha(alpha)
        ax.fill_between(xs, ys, alpha=alpha)
        fill_percentage = math.ceil(alpha * 100)
        ax.set_title(f'{ax.get_title()} {fill_percentage}%')
        fill_percentages.append(fill_percentage)
    fill_percentage = math.ceil(sum(fill_percentages) / len(fill_percentages))
    head.text(0.99, 1.01, f'{fill_percentage}%')
    plt.savefig(f'plots/{market_type}/{fill_percentage}_{ticker}.png')
    plt.close(fig)

def non_rolling_ols_regression(endogenous, exogenous):
    ols_results = sm.OLS(endogenous, exogenous).fit()
    print(ols_results.summary())

if __name__ == '__main__':
    market_type = 'Emerging_5_Factors'
    if not os.path.exists(f'plots/{market_type}'):
        os.makedirs(f'plots/{market_type}')
    tickers = ['EEMD']
    for ticker in tickers:
        print()
        print(ticker)
        run_reg_model(market_type, ticker)
        time.sleep(1)
        try:
            run_reg_model(market_type, ticker)
        except KeyError as e:
            print(f'Skipping {ticker} due to lack of Yahoo API response')
