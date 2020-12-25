from db.db import Session
from db.factor_return import FactorReturn
from db.market_type import MarketType
from lib.factor_data_downloader import FactorDataDownloader
# Pandas to read and write sql
import pandas as pd

class FactorData:
    @staticmethod
    def download_and_write_data():
        for market_type, data_frame in FactorDataDownloader.download_all().items():
            FactorData.write(market_type, data_frame)

    @staticmethod
    def write(market_type_name, data_frame):
        session = Session()
        market_type = session.query(MarketType).filter(MarketType.name == market_type_name).one_or_none()
        if market_type is None:
            market_type = MarketType(name=market_type_name)
            session.add(market_type)
            session.flush()
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
        market_type = session.query(MarketType).filter(MarketType.name == market_type_name).one_or_none()
        if market_type is None:
            FactorData.download_and_write_data()
            market_type = session.query(MarketType).filter(MarketType.name == market_type_name).one()
        query = session.query(FactorReturn).filter(FactorReturn.market_type_id == market_type.id)
        return pd.read_sql(query.statement, query.session.bind)
