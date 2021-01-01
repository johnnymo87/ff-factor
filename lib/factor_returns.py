from db.db import Session
from db.factor_return import FactorReturn
from db.market_type import MarketType
from lib.factor_returns_downloader import FactorReturnsDownloader
# Pandas to read and write sql
import pandas as pd

class FactorReturns:
    @staticmethod
    def download_and_write_data():
        for market_type_name, data_frame in FactorReturnsDownloader.download_all().items():
            FactorReturns.write(market_type_name, data_frame)

    @staticmethod
    def write(market_type_name, data_frame):
        session = Session()
        factor_returns = FactorReturn.query_by_market_type_name(market_type_name)
        if not session.query(factor_returns.exists()).scalar():
            market_type = session.query(MarketType).filter(MarketType.name == market_type_name).one()
            data_frame['market_type_id'] = market_type.id
            session.add_all([FactorReturn(**row) for _, row in data_frame.iterrows()])
            session.commit()

    @staticmethod
    def fetch(market_type_name):
        """
        @param [string] The market type, e.g. Emerging
        @raise [???] If file can't be found
        @raise [???] If the file isn't a CSV
        @return [pandas.core.frame.DataFrame]
        """
        session = Session()
        factor_returns = FactorReturn.query_by_market_type_name(market_type_name)
        if not session.query(factor_returns.exists()).scalar():
            FactorReturns.download_and_write_data()
        return pd.read_sql(factor_returns.statement, factor_returns.session.bind)
