# Pandas to read csv file and other things
import pandas as pd
# Datareader to download price data from Yahoo Finance
import pandas_datareader as web
# Statsmodels to run our multiple regression model
import statsmodels.api as sm
# To download the Fama French data from the web
import urllib.request
# To unzip the ZipFile
import zipfile
# To sleep in between requests to yahoo finance
import time

def get_fama_french():
    # Web url
    # ff_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"

    # Download the file and save it
    # We will name it fama_french.zip file

    urllib.request.urlretrieve(ff_url, 'fama_french.zip')
    with zipfile.ZipFile('fama_french.zip', 'r') as z:
        # Next we extact the file data
        z.extractall()
        # Look up filename so we can read it
        filename = z.namelist()[0]

    # Now open the CSV file
    ff_factors = pd.read_csv(filename, skiprows = 3, index_col = 0)

    # We want to find out the row with NULL value
    # We will skip these rows
    ff_row = ff_factors.isnull().any(1).to_numpy().nonzero()[0][0]

    # Read the csv file again with skipped rows
    ff_factors = pd.read_csv(filename, skiprows = 3, nrows = ff_row, index_col = 0)

    # Format the date index
    ff_factors.index = pd.to_datetime(ff_factors.index, format='%Y%m')

    # Format dates to end of month
    ff_factors.index = ff_factors.index + pd.offsets.MonthEnd()

    # Convert from percent to decimal
    ff_factors = ff_factors.apply(lambda x: x/ 100)
    return ff_factors

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

    # Rename the Column
    ret_data.columns = ['portfolio']
    return ret_data

def run_reg_model(ticker):
    # Get FF data
    ff_data = get_fama_french()
    ff_first = ff_data.index[0].date()
    ff_last = ff_data.index[ff_data.shape[0] - 1].date()
    #Get the fund price data
    price_data = get_price_data(ticker, ff_first.strftime("%Y-%m-%d"), ff_last.strftime("%Y-%m-%d"))
    if price_data is None:
        return
    price_data = price_data.loc[:ff_last]
    ret_data = get_return_data(price_data, "M")
    if len(ret_data) < 12:
        print('Less than 12 months of data, skipping!')
        return
    all_data = pd.merge(pd.DataFrame(ret_data), ff_data, how = 'inner', left_index= True, right_index= True)
    all_data.rename(columns={"Mkt-RF":"mkt_excess"}, inplace=True)
    all_data['port_excess'] = all_data['portfolio'] - all_data['RF']
    # Run the model
    model = sm.formula.ols(formula = "port_excess ~ mkt_excess + SMB + HML + RMW + CMA", data = all_data).fit()
    return model.summary()

if __name__ == '__main__':
    tickers = ['EEMD']
    for ticker in tickers:
        print()
        print(ticker)
        results = run_reg_model(ticker)
        if results:
            print(results)
        time.sleep(1)
