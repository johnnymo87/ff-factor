import datetime
from db.db import Engine, sessionmaker
from db.investment import Investment
from db.queries.investment_query import InvestmentQuery
from os import environ
import requests
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
        Looks for investments that are missing facts -- either their dividend
        yield, expense ratio, or inception date are null -- and attempts to
        backfill this data by collecting it from various APIs.
        @param [string] market_type_name The market type by which to query
            investments
        @raise [urllib.error.HTTPError] If API response is not 200
        """
        self.backfill_facts_from_yahoo(market_type_name)
        self.backfill_facts_from_seeking_alpha(market_type_name)

    def backfill_facts_from_yahoo(self, market_type_name):
        """
        Looks for investments that are missing facts -- either their dividend
        yield, expense ratio, or inception date are null -- and attempts to
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
            print(f'Either expense ratio, dividend yield, or inception date is null for ({ticker_symbol}), backfilling this data from Yahoo')
            info = yf.Ticker(ticker_symbol).info
            dividend_yield = info.get('yield')
            expense_ratio = info.get('annualReportExpenseRatio')
            inception_date = info.get('fundInceptionDate')
            payload = {}
            if dividend_yield is not None and investment.dividend_yield is None:
                payload['dividend_yield'] = dividend_yield
            if expense_ratio is not None and investment.expense_ratio is None:
                payload['expense_ratio'] = expense_ratio
            if inception_date is not None and investment.inception_date is None:
                payload['inception_date'] = datetime.datetime.fromtimestamp(inception_date)
            if payload.keys():
                self.query.update_by_ticker_symbol(ticker_symbol, payload)

    def backfill_facts_from_seeking_alpha(self, market_type_name):
        """
        Looks for investments that are missing facts -- either their dividend
        yield, expense ratio, or inception date are null -- and attempts to
        backfill this data by querying the Seeking Alpha API.
        @param [string] market_type_name The market type by which to query
            investments
        @raise [urllib.error.HTTPError] If the HTTP response is not 200
        """
        investments_missing_facts = self.query.\
            by_market_type_name(market_type_name).\
            missing_facts()

        # https://stackoverflow.com/a/8290508/2197402
        def batch(iterable, batch_size):
            total_size = len(iterable)
            for ndx in range(0, total_size, batch_size):
                yield iterable[ndx:min(ndx + batch_size, total_size)]

        root_url = 'https://seeking-alpha.p.rapidapi.com/symbols'
        headers = {
            'x-rapidapi-host': 'seeking-alpha.p.rapidapi.com',
            'x-rapidapi-key': environ['SEEKING_ALPHA_RAPIDAPI_KEY']
        }
        seeking_alpha_batch_size = 4 # Apparent hard cap?
        for investments in batch(list(investments_missing_facts), seeking_alpha_batch_size):
            ticker_symbols = [investment.ticker_symbol for investment in investments]
            ticker_symbols_joined = ','.join(ticker_symbols)
            print(f'Either expense ratio, dividend yield, or inception date is null for ({ticker_symbols_joined}), backfilling this data from the Seeking Alpha API')

            querystring = {'symbols': ticker_symbols_joined}
            profile_payloads = requests.\
                request('GET', f'{root_url}/get-profile', headers=headers, params=querystring).\
                json().\
                get('data', [])
            summary_payloads = requests.\
                request('GET', f'{root_url}/get-summary', headers=headers, params=querystring).\
                json().\
                get('data', [])
            profile_payloads = {profile_payload['id']: profile_payload['attributes'] for profile_payload in profile_payloads}
            summary_payloads = {summary_payload['id']: summary_payload['attributes'] for summary_payload in summary_payloads}

            for investment in investments:
                dividend_yield = summary_payloads.get(investment.ticker_symbol, {}).get('divYield')
                expense_ratio = profile_payloads.get(investment.ticker_symbol, {}).get('expenseRatio')
                inception_date = profile_payloads.get(investment.ticker_symbol, {}).get('inceptionDate')
                payload = {}
                if dividend_yield is not None and investment.dividend_yield is None:
                    payload['dividend_yield'] = dividend_yield
                if expense_ratio is not None and investment.expense_ratio is None:
                    payload['expense_ratio'] = expense_ratio
                if inception_date is not None and investment.inception_date is None:
                    payload['inception_date'] = datetime.datetime.strptime(inception_date, '%m/%d/%Y')
                if payload.keys():
                    self.query.update_by_ticker_symbol(investment.ticker_symbol, payload)
