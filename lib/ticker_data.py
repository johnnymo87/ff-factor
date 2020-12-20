from db.db import Session
from db.ticker_price import TickerPrice
# Pandas to read sql into a dataframe
import pandas as pd
# Datareader to download price data from the Yahoo API
import pandas_datareader as web

class TickerData:
    @staticmethod
    def get_yahoo_data(ticker_symbol, start, end):
        """
        @param [string] ticker_symbol Ticker symbol of the stock
        @param [Date] start Start date of the range (inclusive) of desired data
        @param [Date] end End date of the range (inclusive) of desired data
        @raise [pandas_datareader._utils.RemoteDataError] If Yahoo API response is not 200
        @return [pandas.core.frame.DataFrame]
        """
        data = web.get_data_yahoo(ticker_symbol, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

        # Keep only the adjusted close column
        data = data['Adj Close']

        # Keep only prices at the last day of each month
        data = data.resample('M').last()

        # Calculate the percent change
        data = data.pct_change()[1:]

        # Convert from Series to DataFrame
        data = pd.DataFrame(data)

        # Rename the columns
        data.columns = ['percentage_change']
        data['symbol'] = ticker_symbol
        data['occurred_at'] = data.index
        data['occurred_at'] = data.occurred_at.dt.date
        return data

    @staticmethod
    def fetch(ticker_symbol, start, end):
        """
        @param [string] ticker_symbol Ticker symbol of the stock
        @param [Date] start Start date of the range (inclusive) of desired data
        @param [Date] end End date of the range (inclusive) of desired data
        @raise [pandas_datareader._utils.RemoteDataError] If Yahoo API response is not 200
        @return [pandas.core.frame.DataFrame]
        """
        session = Session()
        query = session.query(TickerPrice).\
            filter(TickerPrice.symbol == ticker_symbol).\
            filter(TickerPrice.occurred_at >= start).\
            filter(TickerPrice.occurred_at <= end)
        if not session.query(query.exists()).scalar():
            print(f'Ticker price data for ({ticker_symbol}, {start}, {end}) not found in the DB, backfilling it from the Yahoo API')
            yahoo_data = TickerData.get_yahoo_data(ticker_symbol, start, end)
            session.add_all([TickerPrice(**row) for _, row in yahoo_data.iterrows()])
            session.commit()
        return pd.read_sql(query.statement, query.session.bind)
