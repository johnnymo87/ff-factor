from sqlalchemy import Column, Date, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_repr import RepresentableBase

Base = declarative_base(cls=RepresentableBase)
class FactorReturn(Base):
    __tablename__ = 'factor_returns'

    id = Column(Integer, primary_key=True)
    market_type_id = Column(Integer, nullable=False)
    occurred_at = Column(Date, nullable=False)
    risk_free = Column(Numeric, nullable=False)
    market_minus_risk_free = Column(Numeric, nullable=False)
    small_minus_big = Column(Numeric, nullable=False)
    high_minus_low = Column(Numeric, nullable=False)
    robust_minus_weak = Column(Numeric)
    conservative_minus_aggressive = Column(Numeric)
    winners_minus_losers = Column(Numeric)
