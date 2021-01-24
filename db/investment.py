from db.market_type import MarketType
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_repr import RepresentableBase

Base = declarative_base(cls=RepresentableBase)
class Investment(Base):
    __tablename__ = 'investments'

    id = Column(Integer, primary_key=True)
    market_type_id = Column(Integer, ForeignKey(MarketType.id), nullable=False)
    ticker_symbol = Column(String, nullable=False)
    expense_ratio = Column(Numeric)
    dividend_yield = Column(Numeric)
    inception_date = Column(Date)

    market_type = relationship(MarketType, foreign_keys=[market_type_id])
