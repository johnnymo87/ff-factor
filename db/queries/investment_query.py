import datetime
from dateutil.relativedelta import relativedelta
from db.investment import Investment
from db.market_type import MarketType
import pandas as pd
from sqlalchemy import or_
from sqlalchemy.orm import Query
from sqlalchemy.sql.expression import bindparam

# https://stackoverflow.com/a/23312811/2197402
# Inherit from query to define custom query methods
class InvestmentQuery(Query):
    def for_analysis(self, market_type_name, analysis_ends_at):
        return self.\
            by_market_type_name(market_type_name).\
            with_at_least_twelve_full_months_of_history(analysis_ends_at).\
            order_by(Investment.ticker_symbol)

    def with_at_least_twelve_full_months_of_history(self, analysis_ends_at):
        twelve_months_before_first_day_of_this_month =\
            analysis_ends_at.\
            replace(day=1) + relativedelta(months=-12)
        return self.\
            filter(Investment.inception_date <=\
                twelve_months_before_first_day_of_this_month)

    def by_market_type_name(self, market_type_name):
        return self.\
            join(Investment.market_type).\
            filter(MarketType.name == market_type_name)

    def missing_facts(self):
        """
        Filters for records that are missing their expense ratio, their
        dividend yield, AND their inception date
        """
        return self.\
            filter(
                (Investment.dividend_yield == None) | \
                (Investment.expense_ratio == None) | \
                (Investment.inception_date == None)
            )

    def update_by_ticker_symbol(self, ticker_symbol, values):
        """
        NB: This forces a commit, because I want to avoid having to requery
        Yahoo because I crashed before I committed.
        @param [string] ticker_symbol
        @param [dict] values
        @returns [int] the count of rows updated
        """
        count = self.\
            filter(Investment.ticker_symbol == ticker_symbol).\
            update(values, synchronize_session=False)
        self.session.commit()
        return count

    def to_data_frame(self):
        df = pd.read_sql(
            self.statement,
            self.session.bind
        )[['ticker_symbol', 'dividend_yield', 'expense_ratio', 'inception_date']]
        df = df.rename(columns={ 'ticker_symbol': 'ticker' })
        return df
