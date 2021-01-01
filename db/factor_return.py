from db.db import Session
from db.market_type import MarketType
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_repr import RepresentableBase

Base = declarative_base(cls=RepresentableBase)
class FactorReturn(Base):
    __tablename__ = 'factor_returns'

    id = Column(Integer, primary_key=True)
    market_type_id = Column(Integer, ForeignKey(MarketType.id), nullable=False)
    occurred_at = Column(Date, nullable=False)
    risk_free = Column(Numeric, nullable=False)
    market_minus_risk_free = Column(Numeric, nullable=False)
    small_minus_big = Column(Numeric, nullable=False)
    high_minus_low = Column(Numeric, nullable=False)
    robust_minus_weak = Column(Numeric)
    conservative_minus_aggressive = Column(Numeric)
    winners_minus_losers = Column(Numeric)

    market_type = relationship(MarketType, foreign_keys=[market_type_id])

    @staticmethod
    def query_by_market_type_name(market_type_name):
        return Session() \
            .query(FactorReturn) \
            .join(FactorReturn.market_type) \
            .filter(MarketType.name == market_type_name)
