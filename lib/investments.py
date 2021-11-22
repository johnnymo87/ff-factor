import datetime
from db.db import Engine, sessionmaker
from db.investment import Investment
from db.queries.investment_query import InvestmentQuery
from os import environ
import requests

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

            updates = {ticker_symbol: {} for ticker_symbol in ticker_symbols}
            for summary_payload in summary_payloads:
                dividend_yield = summary_payload['attributes']['divYield']
                if dividend_yield is not None:
                    updates[summary_payload['id']]['dividend_yield'] = dividend_yield
            for profile_payload in profile_payloads:
                expense_ratio = profile_payload['attributes']['expenseRatio']
                if expense_ratio is not None:
                    updates[profile_payload['id']]['expense_ratio'] = expense_ratio
                inception_date = profile_payload['attributes']['inceptionDate']
                if inception_date is not None:
                    updates[profile_payload['id']]['inception_date'] = datetime.datetime.strptime(inception_date, '%m/%d/%Y')

            for ticker_symbol in ticker_symbols:
                payload = updates[ticker_symbol]
                if len(payload.values()) != 3:
                    found_keys = ','.join(payload.keys())
                    print(f'Only found ({found_keys}) for ({ticker_symbol})')
                if len(payload.values()) != 0:
                    self.query.update_by_ticker_symbol(ticker_symbol, payload)
