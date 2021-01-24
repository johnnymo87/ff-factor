import datetime
from db.db import Engine, sessionmaker
from db.investment import Investment
from db.queries.investment_query import InvestmentQuery
import yfinance as yf

class Investments:
    # https://python-patterns.guide/gang-of-four/singleton/
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Investments, cls).__new__(cls)
            session = sessionmaker(bind=Engine, query_cls=InvestmentQuery)
            cls._instance.query = session().query(Investment)
        return cls._instance

    def backfill_facts(self, market_type_name):
        """
        Looks for investments that are missing facts -- their dividend yield,
        expense ratio, and inception date are all null -- and attempts to
        backfill this data by scraping it from Yahoo.
        @param [string] market_type_name The market type by which to query
            investments
        @raise [urllib.error.HTTPError] If Yahoo response is not 200
        """
        investments_missing_facts = self.query.\
            by_market_type_name(market_type_name).\
            missing_facts()

        for investment in investments_missing_facts:
            ticker_symbol = investment.ticker_symbol
            print(f'Expense ratio, dividend yield, and inception date are null for ({ticker_symbol}) not found in the DB, backfilling it from Yahoo')
            info = yf.Ticker(ticker_symbol).info
            inception_date = datetime.datetime.fromtimestamp(
                info.get('fundInceptionDate', 0))
            values = {
                'dividend_yield': info.get('yield'),
                'expense_ratio': info.get('annualReportExpenseRatio'),
                'inception_date': inception_date
            }
            self.query.update_by_ticker_symbol(ticker_symbol, values)
