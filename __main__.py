from lib.factor_data import FactorData
# To draw plots
import matplotlib.pyplot as plt
# Pandas to read csv file and other things
import pandas as pd
# Datareader to download price data from Yahoo Finance
import pandas_datareader as web
# To prepare design matrices using R-like formulas
from patsy import dmatrices
# Statsmodels to run our multiple regression model
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
# To sleep in between requests to yahoo finance
import time

# Build the get_price function
# We need 3 arguments, ticker, start and end date
def get_price_data(ticker, start, end):
    try:
        price = web.get_data_yahoo(ticker, start, end)
    except pandas_datareader._utils.RemoteDataError as e:
        print(e)
        return
    price = price['Adj Close'] # keep only the Adj Price col
    return price

def get_return_data(price_data, period = "M"):
    # Resample the data to monthly price
    price = price_data.resample(period).last()

    # Calculate the percent change
    ret_data = price.pct_change()[1:]

    # convert from series to DataFrame
    ret_data = pd.DataFrame(ret_data)

    # Rename the columns
    ret_data.columns = ['portfolio']
    ret_data['occurred_at'] = ret_data.index
    ret_data['occurred_at'] = ret_data.occurred_at.dt.date
    return ret_data

def run_reg_model(ticker, minimum_months=12):
    # Get FF data
    ff_data = FactorData.fetch('Emerging_5_Factors.csv')
    ff_first = ff_data.occurred_at[0]
    ff_last = ff_data.occurred_at[len(ff_data.occurred_at) - 1]

    # Get the fund price data
    price_data = get_price_data(ticker, ff_first.strftime("%Y-%m-%d"), ff_last.strftime("%Y-%m-%d"))
    if price_data is None:
        return
    price_data = price_data.loc[:ff_last]
    ret_data = get_return_data(price_data, "M")
    if len(ret_data) < minimum_months:
        print(f'Less than {minimum_months} months of data, skipping!')
        return

    # Join the FF and fund data
    all_data = pd.merge(ret_data, ff_data, on='occurred_at')
    all_data['port_excess'] = all_data.portfolio - all_data.rf

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
