from calendar import monthrange
from datetime import date
from datetime import timedelta
from db.db import Session
from db.investment_return import InvestmentReturn
# Pandas to read sql into a dataframe
import pandas as pd
# Datareader to download price data from the Yahoo API
import pandas_datareader as web
from sqlalchemy.sql import func
import time

class InvestmentReturns:
    @staticmethod
    def get_percentage_change_data(ticker_symbol, start, end):
        """
        @param [string] ticker_symbol Ticker symbol of the stock
        @param [Date] start Start date of the range (inclusive) of desired data
        @param [Date] end End date of the range (inclusive) of desired data, can be `None`
        @raise [pandas_datareader._utils.RemoteDataError] If Yahoo API response is not 200
        @return [pandas.core.frame.DataFrame]
        """
        data = web.get_data_yahoo(ticker_symbol, start, end)

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
        data['ticker_symbol'] = ticker_symbol
        data['occurred_at'] = data.index
        data['occurred_at'] = data.occurred_at.dt.date
        return data

    @staticmethod
    def backfill_returns(ticker_symbol, start, end):
        """
        Looks for investment returns for the ticker between the given start and
        end date. If some are present, checks the last time it was backfilled
        to see if there is a gap. If so, backfills either of these gaps. If none
        are present, backfills starting with the given start date.
        @param [string] ticker_symbol Ticker symbol of the stock
        @param [Date] start Start date of the range (inclusive) of desired data
        @param [Date] end End date of the range (inclusive) of desired data
        @raise [pandas_datareader._utils.RemoteDataError] If Yahoo API response is not 200
        @raise [requests.exceptions.ConnectionError] If unable to connect to the Yahoo API
        """
        session = Session()
        query = session.query(InvestmentReturn).\
            filter(InvestmentReturn.ticker_symbol == ticker_symbol).\
            filter(InvestmentReturn.occurred_at >= start).\
            filter(InvestmentReturn.occurred_at <= end)
        if session.query(query.exists()).scalar():
            max_occurred_at = session.query(func.max(InvestmentReturn.occurred_at)).filter(InvestmentReturn.ticker_symbol == ticker_symbol).scalar()
            if max_occurred_at < end:
                print(f'Ticker price data for ({ticker_symbol}, {max_occurred_at}, {end}) not found in the DB, backfilling it from the Yahoo API')
                percentage_change_data = InvestmentReturns.get_percentage_change_data(ticker_symbol, max_occurred_at, end)
                if percentage_change_data.empty:
                    print(f'WARNING: No new ticker price data found for ({ticker_symbol}, {max_occurred_at}, {end}) in the Yahoo API')
                session.add_all([InvestmentReturn(**row) for _, row in percentage_change_data.iterrows()])
                session.commit()
        else:
            print(f'Ticker price data for ({ticker_symbol}, {start}, {end}) not found in the DB, backfilling it from the Yahoo API')
            this_year, last_month = date.today().year, date.today().month - 1
            _, last_day = monthrange(this_year, last_month)
            end = date(this_year, last_month, last_day)
            percentage_change_data = InvestmentReturns.get_percentage_change_data(ticker_symbol, start, end)
            session.add_all([InvestmentReturn(**row) for _, row in percentage_change_data.iterrows()])
            session.commit()

    @staticmethod
    def fetch(ticker_symbol, start, end):
        """
        @param [string] ticker_symbol Ticker symbol of the stock
        @param [Date] start Start date of the range (inclusive) of desired data
        @param [Date] end End date of the range (inclusive) of desired data
        @raise [pandas_datareader._utils.RemoteDataError] If Yahoo API response is not 200
        @raise [requests.exceptions.ConnectionError] If unable to connect to the Yahoo API
        @return [pandas.core.frame.DataFrame]
        """
        session = Session()
        query = session.query(InvestmentReturn).\
            filter(InvestmentReturn.ticker_symbol == ticker_symbol).\
            filter(InvestmentReturn.occurred_at >= start).\
            filter(InvestmentReturn.occurred_at <= end)
        return pd.read_sql(query.statement, query.session.bind)
