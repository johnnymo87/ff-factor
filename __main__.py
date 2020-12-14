from lib.factor_data import FactorData
from lib.ticker_data import TickerData
# To draw plots
import matplotlib.pyplot as plt
# Pandas to read csv file and other things
import pandas as pd
# To prepare design matrices using R-like formulas
from patsy import dmatrices
# Statsmodels to run our multiple regression model
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
# To sleep in between requests to yahoo finance
import time

def run_reg_model(ticker, minimum_months=12):
    # Get FF data
    ff_data = FactorData.fetch('Emerging_5_Factors.csv')
    ff_first = ff_data.occurred_at[0]
    ff_last = ff_data.occurred_at[len(ff_data.occurred_at) - 1]

    ticker_data = TickerData.fetch(ticker, ff_first, ff_last)
    if len(ticker_data) < minimum_months:
        print(f'Less than {minimum_months} months of data, skipping!')
        return

    # Join the FF and ticker data
    all_data = pd.merge(ticker_data, ff_data, on='occurred_at')
    all_data['port_excess'] = all_data.percentage_change - all_data.rf

    # Prepare endogenous and exogenous data sets
    y, X = dmatrices('port_excess ~ mkt_rf + smb + hml + rmw + cma', data=all_data, return_type='dataframe')

    # Draw rolling OLS plot
    rolling_ols_results = RollingOLS(y, X, window=minimum_months).fit()
    variables = [c for c in X.columns if c != 'Intercept']
    fig, _ = plt.subplots(figsize=(10, 20))
    rolling_ols_results.plot_recursive_coefficient(fig=fig, variables=variables)
    for ax in fig.axes[1:]:
        ax.axhline(y=1, linewidth=2, color='g')
        ax.axhline(y=0, linewidth=2, color='y')
        ax.axhline(y=-1, linewidth=2, color='r')
    plt.savefig(f'plots/{ticker}.png')

    # Run non-rolling OLS regression
    ols_results = sm.OLS(y, X).fit()
    print(ols_results.summary())

if __name__ == '__main__':
    tickers = ['EEMD']
    for ticker in tickers:
        print()
        print(ticker)
        run_reg_model(ticker)
        time.sleep(1)
