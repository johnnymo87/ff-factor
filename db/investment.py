from db.db import Session
from db.market_type import MarketType
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_repr import RepresentableBase

Base = declarative_base(cls=RepresentableBase)
class Investment(Base):
    __tablename__ = 'investments'

    id = Column(Integer, primary_key=True)
    market_type_id = Column(Integer, ForeignKey(MarketType.id), nullable=False)
    ticker_symbol = Column(String, nullable=False)

    market_type = relationship(MarketType, foreign_keys=[market_type_id])

    @staticmethod
    def query_by_market_type_name(market_type_name):
        return Session() \
            .query(Investment) \
            .join(Investment.market_type) \
            .filter(MarketType.name == market_type_name)
